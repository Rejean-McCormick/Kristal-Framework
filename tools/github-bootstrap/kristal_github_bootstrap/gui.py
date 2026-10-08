from __future__ import annotations

import json
import os
import queue
import re
import subprocess
import sys
import threading
import traceback
from pathlib import Path
from typing import Any, Callable

from .core import (
    BootstrapError,
    GhClient,
    apply_account,
    apply_single_repo,
    load_config,
    plan_account,
)
from .lifecycle import (
    activate_publication_for_state,
    default_channel_id,
    inspect_local_kristal,
    manager_entries,
    publish_local_kristal,
    qualify_repository,
    verify_active_channel,
    verify_publication_for_state,
)

SHA_RE = re.compile(r"^[0-9a-f]{40}$")

# Ready-to-use defaults for the current Kristal v10 GitHub host.
# They remain editable in the GUI and do not participate in logical commitments.
DEFAULT_OWNER = "Rejean-McCormick"
DEFAULT_KIND = "user"
DEFAULT_NETWORK_ID = "urn:kristal:network:rejean-mccormick"
DEFAULT_FRAMEWORK_REPO = "Rejean-McCormick/KristalV10"
DEFAULT_FRAMEWORK_SHA = "27c0c7db3d79a4597c1c964fe8281fa35b5f858a"
DEFAULT_WINDOWS_CONFIG = r"C:\mycode\Kristal\network.toml"
DEFAULT_WINDOWS_WORKSPACE = r"C:\mycode\Kristal"


def _q(value: str) -> str:
    """Render a safe TOML basic string using JSON-compatible escapes."""
    return json.dumps(value, ensure_ascii=False)


def render_config(values: dict[str, str]) -> str:
    """Render the minimal supported network.toml used by the GUI."""
    owner = values["owner"].strip()
    kind = values.get("kind", "organization").strip()
    network_id = values.get("network_id", "").strip() or f"urn:kristal:network:{owner}"
    framework_repo = values.get("framework_repo", "").strip() or f"{owner}/KristalV10"
    framework_ref = values.get("framework_ref", "").strip()
    hub = values.get("hub_repo", "kristal-hub").strip() or "kristal-hub"
    public_repo = values.get("public_repo", "kristal-public").strip() or "kristal-public"
    private_repo = values.get("private_repo", "kristal-private").strip() or "kristal-private"
    immutable = values.get("immutable_releases", "best_effort")
    environments = values.get("environments", "best_effort")
    custom_properties = values.get("custom_properties", "best_effort")
    attestations = values.get("attestations", "best_effort")
    # Global GitHub profile repositories are useful for organizations, but are
    # intentionally off for personal accounts: the bootstrap must not create or
    # take over the user's profile repository or an otherwise unnecessary .github repo.
    if kind == "organization":
        create_dotgithub = True
        private_profile = values.get("create_private_profile", "true").lower() == "true"
    else:
        create_dotgithub = False
        private_profile = False
    create_profile_repository = False

    return f'''[account]
owner = {_q(owner)}
kind = {_q(kind)}

[network]
id = {_q(network_id)}

[framework]
repository = {_q(framework_repo)}
ref = {_q(framework_ref)}

[global]
create_dotgithub = {str(create_dotgithub).lower()}
create_private_profile = {str(private_profile).lower()}
create_profile_repository = {str(create_profile_repository).lower()}

[hub]
repository = {_q(hub)}
visibility = "private"
identity_key = "root-directory"

[policy]
default_branch = "main"

[features]
immutable_releases = {_q(immutable)}
environments = {_q(environments)}
custom_properties = {_q(custom_properties)}
attestations = {_q(attestations)}

[[collections]]
name = {_q(public_repo)}
identity_key = "public-primary"
visibility = "public"
role = "collection"
collection = "public"
description = "Public Kristal collection"

[[collections]]
name = {_q(private_repo)}
identity_key = "private-primary"
visibility = "private"
role = "collection"
collection = "private"
description = "Private Kristal collection"
'''


def validate_gui_values(values: dict[str, str]) -> None:
    owner = values.get("owner", "").strip()
    if not owner:
        raise BootstrapError("GitHub owner is required")
    if values.get("kind") not in {"user", "organization"}:
        raise BootstrapError("Account kind must be user or organization")
    ref = values.get("framework_ref", "").strip()
    if not SHA_RE.fullmatch(ref):
        raise BootstrapError("Framework ref must be an immutable full 40-character commit SHA")
    names = [values.get(k, "").strip() for k in ("hub_repo", "public_repo", "private_repo")]
    if any(not n for n in names):
        raise BootstrapError("Hub/public/private repository names are required")
    if len(set(names)) != len(names):
        raise BootstrapError("Hub/public/private repository names must be distinct")


def resolve_framework_head(repository: str, ref: str = "main") -> str:
    p = subprocess.run(
        ["gh", "api", f"/repos/{repository}/commits/{ref}", "--jq", ".sha"],
        text=True,
        capture_output=True,
    )
    if p.returncode:
        raise BootstrapError(f"Unable to resolve {repository}@{ref}: {(p.stderr or '').strip() or 'no diagnostic text'}")
    sha = (p.stdout or '').strip().lower()
    if not SHA_RE.fullmatch(sha):
        raise BootstrapError(f"GitHub returned an invalid commit SHA: {sha!r}")
    return sha


def main() -> None:
    # Import Tk lazily so core/config helpers remain usable on headless systems.
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter.scrolledtext import ScrolledText

    root = tk.Tk()
    root.title("Kristal GitHub Setup")
    root.geometry("920x760")
    root.minsize(820, 650)

    workq: queue.Queue[tuple[str, Any]] = queue.Queue()
    running = {"value": False}

    vars_: dict[str, tk.StringVar] = {
        "owner": tk.StringVar(value=DEFAULT_OWNER),
        "kind": tk.StringVar(value=DEFAULT_KIND),
        "network_id": tk.StringVar(value=DEFAULT_NETWORK_ID),
        "framework_repo": tk.StringVar(value=DEFAULT_FRAMEWORK_REPO),
        "framework_ref": tk.StringVar(value=DEFAULT_FRAMEWORK_SHA),
        "hub_repo": tk.StringVar(value="kristal-hub"),
        "public_repo": tk.StringVar(value="kristal-public"),
        "private_repo": tk.StringVar(value="kristal-private"),
        "immutable_releases": tk.StringVar(value="best_effort"),
        "environments": tk.StringVar(value="best_effort"),
        "custom_properties": tk.StringVar(value="off"),
        "attestations": tk.StringVar(value="best_effort"),
        "create_private_profile": tk.StringVar(value="true"),
    }
    # Keep the operator-owned network declaration stable across bootstrap upgrades.
    launch_dir = Path(sys.argv[0]).resolve().parent
    default_config = Path(DEFAULT_WINDOWS_CONFIG) if os.name == "nt" else (launch_dir / "network.toml")
    config_path = tk.StringVar(value=str(default_config))
    plan_path = tk.StringVar(value=str(default_config.with_name("kristal-plan.json")))

    mainf = ttk.Frame(root, padding=12)
    mainf.pack(fill="both", expand=True)
    notebook = ttk.Notebook(mainf)
    notebook.pack(fill="both", expand=True)

    setup = ttk.Frame(notebook, padding=12)
    repos = ttk.Frame(notebook, padding=12)
    lifecycle = ttk.Frame(notebook, padding=12)
    notebook.add(setup, text="Initial setup")
    notebook.add(repos, text="Add repository")
    notebook.add(lifecycle, text="Lifecycle")

    row = 0
    def field(label: str, key: str, width: int = 58) -> None:
        nonlocal row
        ttk.Label(setup, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(setup, textvariable=vars_[key], width=width).grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

    field("GitHub owner / organization", "owner")
    ttk.Label(setup, text="Account type").grid(row=row, column=0, sticky="w", pady=3)
    ttk.Combobox(setup, textvariable=vars_["kind"], values=["organization", "user"], state="readonly", width=20).grid(row=row, column=1, sticky="w", pady=3)
    row += 1
    field("Stable network ID", "network_id")
    field("Framework repository (OWNER/REPO)", "framework_repo")
    ttk.Label(setup, text="Push C:\\mycode\\Kristal\\KristalV10 first, then detect the immutable main SHA.").grid(row=row, column=1, sticky="w", pady=(0,3))
    row += 1

    ttk.Label(setup, text="Framework commit SHA").grid(row=row, column=0, sticky="w", pady=3)
    sha_frame = ttk.Frame(setup)
    sha_frame.grid(row=row, column=1, sticky="ew", pady=3)
    ttk.Entry(sha_frame, textvariable=vars_["framework_ref"]).pack(side="left", fill="x", expand=True)
    def detect_sha() -> None:
        repo = vars_["framework_repo"].get().strip()
        if not repo:
            owner = vars_["owner"].get().strip()
            repo = f"{owner}/KristalV10" if owner else ""
            vars_["framework_repo"].set(repo)
        run_task("Resolve framework SHA", lambda: {"sha": resolve_framework_head(repo)}, on_result=lambda r: vars_["framework_ref"].set(r["sha"]))
    ttk.Button(sha_frame, text="Detect main SHA", command=detect_sha).pack(side="left", padx=(6,0))
    row += 1

    field("Private hub repository", "hub_repo")
    field("Public collection repository", "public_repo")
    field("Private collection repository", "private_repo")

    modes = ["off", "best_effort", "required"]
    for label, key in [
        ("Immutable releases", "immutable_releases"),
        ("Environments", "environments"),
        ("Custom properties", "custom_properties"),
        ("Attestations", "attestations"),
    ]:
        ttk.Label(setup, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Combobox(setup, textvariable=vars_[key], values=modes, state="readonly", width=20).grid(row=row, column=1, sticky="w", pady=3)
        row += 1

    ttk.Label(setup, text="Config file").grid(row=row, column=0, sticky="w", pady=3)
    pframe = ttk.Frame(setup); pframe.grid(row=row, column=1, sticky="ew", pady=3)
    ttk.Entry(pframe, textvariable=config_path).pack(side="left", fill="x", expand=True)
    def browse_cfg() -> None:
        p = filedialog.asksaveasfilename(title="Save Kristal network config", defaultextension=".toml", filetypes=[("TOML", "*.toml"), ("All files", "*")])
        if p: config_path.set(p)
    ttk.Button(pframe, text="Browse", command=browse_cfg).pack(side="left", padx=(6,0))

    def load_existing_config() -> None:
        selected = filedialog.askopenfilename(title="Open Kristal network config", filetypes=[("TOML", "*.toml"), ("All files", "*")])
        if not selected:
            return
        try:
            cfg = load_config(Path(selected))
            config_path.set(selected)
            account = cfg.get("account", {}); network = cfg.get("network", {}); fw = cfg.get("framework", {}); hub = cfg.get("hub", {}); features = cfg.get("features", {})
            vars_["owner"].set(account.get("owner", "")); vars_["kind"].set(account.get("kind", "organization"))
            vars_["network_id"].set(network.get("id", "")); vars_["framework_repo"].set(fw.get("repository", "")); vars_["framework_ref"].set(fw.get("ref", ""))
            vars_["hub_repo"].set(hub.get("repository", "kristal-hub"))
            cols = cfg.get("collections", [])
            pub = next((c for c in cols if c.get("visibility") == "public"), None)
            priv = next((c for c in cols if c.get("visibility") == "private"), None)
            if pub: vars_["public_repo"].set(pub.get("name", "kristal-public"))
            if priv: vars_["private_repo"].set(priv.get("name", "kristal-private"))
            for key in ("immutable_releases", "environments", "custom_properties", "attestations"):
                vars_[key].set(features.get(key, "best_effort"))
            append_log(f"Loaded: {selected}")
            try:
                lifecycle_workspace.set(str(Path(selected).resolve().parent))
            except Exception:
                pass
        except Exception as exc:
            append_log(f"ERROR: {exc}")
            messagebox.showerror("Kristal GitHub Setup", str(exc))

    ttk.Button(pframe, text="Load", command=load_existing_config).pack(side="left", padx=(6,0))

    def auto_load_default_config() -> None:
        p = Path(config_path.get()).expanduser()
        if not p.exists():
            return
        try:
            cfg = load_config(p)
            account = cfg.get("account", {})
            network = cfg.get("network", {})
            fw = cfg.get("framework", {})
            hub = cfg.get("hub", {})
            features = cfg.get("features", {})
            vars_["owner"].set(account.get("owner", DEFAULT_OWNER))
            vars_["kind"].set(account.get("kind", DEFAULT_KIND))
            vars_["network_id"].set(network.get("id", DEFAULT_NETWORK_ID))
            vars_["framework_repo"].set(fw.get("repository", DEFAULT_FRAMEWORK_REPO))
            vars_["framework_ref"].set(fw.get("ref", DEFAULT_FRAMEWORK_SHA))
            vars_["hub_repo"].set(hub.get("repository", "kristal-hub"))
            cols = cfg.get("collections", [])
            pub = next((c for c in cols if c.get("visibility") == "public"), None)
            priv = next((c for c in cols if c.get("visibility") == "private"), None)
            if pub:
                vars_["public_repo"].set(pub.get("name", "kristal-public"))
            if priv:
                vars_["private_repo"].set(priv.get("name", "kristal-private"))
            for key in ("immutable_releases", "environments", "custom_properties", "attestations"):
                vars_[key].set(features.get(key, vars_[key].get()))
            append_log(f"Auto-loaded: {p}")
            try:
                lifecycle_workspace.set(str(p.resolve().parent))
            except Exception:
                pass
        except Exception as exc:
            append_log(f"Default config exists but could not be auto-loaded: {exc}")

    root.after(100, auto_load_default_config)
    row += 1

    setup.columnconfigure(1, weight=1)

    log = ScrolledText(mainf, height=14, wrap="word")
    log.pack(fill="both", expand=False, pady=(10,0))
    log.configure(state="disabled")

    def append_log(text: str) -> None:
        log.configure(state="normal")
        log.insert("end", text.rstrip() + "\n")
        log.see("end")
        log.configure(state="disabled")

    def values() -> dict[str, str]:
        return {k: v.get() for k, v in vars_.items()}

    def save_config() -> Path:
        vals = values()
        validate_gui_values(vals)
        p = Path(config_path.get()).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(render_config(vals), encoding="utf-8")
        # Load through the real parser/validator before any remote action.
        load_config(p)
        return p

    def run_task(label: str, fn: Callable[[], Any], on_result: Callable[[Any], None] | None = None) -> None:
        if running["value"]:
            messagebox.showinfo("Kristal", "An operation is already running.")
            return
        running["value"] = True
        append_log(f"\n== {label} ==")
        def worker() -> None:
            try:
                workq.put(("ok", (fn(), on_result)))
            except Exception as exc:
                try:
                    setattr(exc, "_kristal_traceback", traceback.format_exc())
                except Exception:
                    pass
                workq.put(("error", exc))
        threading.Thread(target=worker, daemon=True).start()

    def poll() -> None:
        try:
            while True:
                kind, payload = workq.get_nowait()
                if kind == "log":
                    append_log(str(payload))
                    continue
                running["value"] = False
                if kind == "error":
                    append_log(f"ERROR: {payload}")
                    tb = getattr(payload, "_kristal_traceback", None)
                    if tb:
                        append_log("--- diagnostic traceback ---\n" + tb)
                    messagebox.showerror("Kristal GitHub Setup", str(payload))
                else:
                    result, callback = payload
                    if callback:
                        callback(result)
                    append_log(json.dumps(result, indent=2, ensure_ascii=False) if not isinstance(result, str) else result)
        except queue.Empty:
            pass
        root.after(150, poll)

    buttons = ttk.Frame(setup)
    buttons.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(12,4))

    def prepare_config() -> Path | None:
        try:
            p = save_config()
            append_log(f"Saved and validated: {p}")
            return p
        except Exception as exc:
            append_log(f"ERROR: {exc}")
            messagebox.showerror("Kristal GitHub Setup", str(exc))
            return None

    def do_doctor() -> None:
        p = prepare_config()
        if not p: return
        def task() -> Any:
            client = GhClient()
            return {"doctor": client.doctor(), "plan": plan_account(client, load_config(p))}
        run_task("Doctor + preflight", task)

    def do_plan() -> None:
        p = prepare_config()
        if not p: return
        def task() -> Any:
            client = GhClient(); result = plan_account(client, load_config(p))
            out = Path(plan_path.get()).expanduser().resolve(); out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            result = dict(result); result["saved_plan"] = str(out); return result
        run_task("Plan", task)

    def do_apply() -> None:
        p = prepare_config()
        if not p: return
        if not messagebox.askyesno("Apply Kristal configuration", "This will create/configure GitHub repositories and managed files. Continue?"):
            return
        def task() -> Any:
            cfg = load_config(p); client = GhClient(); plan = plan_account(client, cfg)
            return apply_account(client, cfg, expected_observed_fingerprint=plan["observed_fingerprint"])
        run_task("Apply", task)

    def do_status() -> None:
        p = prepare_config()
        if not p: return
        def task() -> Any:
            return plan_account(GhClient(), load_config(p))
        run_task("Status", task)

    def do_save() -> None:
        prepare_config()

    ttk.Button(buttons, text="1. Doctor", command=do_doctor).pack(side="left", padx=3)
    ttk.Button(buttons, text="2. Plan", command=do_plan).pack(side="left", padx=3)
    ttk.Button(buttons, text="3. Apply", command=do_apply).pack(side="left", padx=3)
    ttk.Button(buttons, text="Status", command=do_status).pack(side="left", padx=3)
    ttk.Button(buttons, text="Save config", command=do_save).pack(side="left", padx=3)

    # Lifecycle tab: multi-Kristal operational lifecycle from the .pyw itself.
    lifecycle_workspace = tk.StringVar(value=DEFAULT_WINDOWS_WORKSPACE if os.name == "nt" else str(default_config.parent))
    lifecycle_catalog = tk.StringVar(value=str(Path(lifecycle_workspace.get()) / "kristal-manager.json"))
    lifecycle_local_path = tk.StringVar(value="")
    lifecycle_local_choice = tk.StringVar(value="")
    lifecycle_target = tk.StringVar(value="")
    lifecycle_state_ref = tk.StringVar(value="")
    lifecycle_channel = tk.StringVar(value="")
    lifecycle_status = tk.StringVar(value="Ready")
    lifecycle_rows: dict[str, dict[str, Any]] = {}

    lr = 0
    ttk.Label(lifecycle, text="Kristal lifecycle", font=("TkDefaultFont", 11, "bold")).grid(row=lr, column=0, columnspan=3, sticky="w", pady=(0,8)); lr += 1
    ttk.Label(
        lifecycle,
        text="Select one Local Kristal. Setup copies only its verified v9 State Snapshot into the chosen public/private collection, qualifies the exact collection commit, publishes the matching v10 Release, and activates a per-Kristal channel.",
        wraplength=820,
    ).grid(row=lr, column=0, columnspan=3, sticky="w", pady=(0,10)); lr += 1

    ttk.Label(lifecycle, text="Workspace root").grid(row=lr, column=0, sticky="w", pady=4)
    ttk.Entry(lifecycle, textvariable=lifecycle_workspace, width=66).grid(row=lr, column=1, sticky="ew", pady=4)
    def browse_workspace() -> None:
        selected = filedialog.askdirectory(title="Select Kristal workspace")
        if selected:
            old_root = lifecycle_workspace.get()
            lifecycle_workspace.set(selected)
            if lifecycle_catalog.get() in {str(Path(old_root) / "kristal-manager.json"), ""}:
                lifecycle_catalog.set(str(Path(selected) / "kristal-manager.json"))
    ttk.Button(lifecycle, text="Browse", command=browse_workspace).grid(row=lr, column=2, padx=(6,0), pady=4); lr += 1

    ttk.Label(lifecycle, text="Kristal Manager catalog").grid(row=lr, column=0, sticky="w", pady=4)
    ttk.Entry(lifecycle, textvariable=lifecycle_catalog).grid(row=lr, column=1, sticky="ew", pady=4)
    def browse_catalog() -> None:
        selected = filedialog.askopenfilename(title="Select kristal-manager.json", filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if selected:
            lifecycle_catalog.set(selected)
            refresh_manager_catalog()
    ttk.Button(lifecycle, text="Browse", command=browse_catalog).grid(row=lr, column=2, padx=(6,0), pady=4); lr += 1

    ttk.Label(lifecycle, text="Manager Local Kristal").grid(row=lr, column=0, sticky="w", pady=4)
    local_combo = ttk.Combobox(lifecycle, textvariable=lifecycle_local_choice, state="readonly")
    local_combo.grid(row=lr, column=1, sticky="ew", pady=4)
    local_controls = ttk.Frame(lifecycle); local_controls.grid(row=lr, column=2, sticky="e")
    ttk.Button(local_controls, text="Refresh", command=lambda: refresh_manager_catalog()).pack(side="left", padx=(6,2))
    def browse_local() -> None:
        selected = filedialog.askdirectory(title="Select Local Kristal")
        if selected:
            lifecycle_local_choice.set("")
            lifecycle_local_path.set(selected)
            apply_local_inspection(None)
    ttk.Button(local_controls, text="Folder", command=browse_local).pack(side="left", padx=2); lr += 1

    ttk.Label(lifecycle, text="Local path").grid(row=lr, column=0, sticky="w", pady=4)
    ttk.Entry(lifecycle, textvariable=lifecycle_local_path).grid(row=lr, column=1, columnspan=2, sticky="ew", pady=4); lr += 1

    ttk.Label(lifecycle, text="Publication target").grid(row=lr, column=0, sticky="w", pady=4)
    target_combo = ttk.Combobox(lifecycle, textvariable=lifecycle_target, values=["public", "private"], state="readonly")
    target_combo.grid(row=lr, column=1, sticky="w", pady=4)
    ttk.Label(lifecycle, text="GitHub hosting/sync visibility is independent; this target controls formal publication in the Kristal collection only.", wraplength=410).grid(row=lr, column=2, sticky="w", padx=(6,0)); lr += 1

    ttk.Label(lifecycle, text="State ref").grid(row=lr, column=0, sticky="w", pady=4)
    ttk.Entry(lifecycle, textvariable=lifecycle_state_ref, state="readonly").grid(row=lr, column=1, columnspan=2, sticky="ew", pady=4); lr += 1
    ttk.Label(lifecycle, text="Activation channel").grid(row=lr, column=0, sticky="w", pady=4)
    ttk.Entry(lifecycle, textvariable=lifecycle_channel).grid(row=lr, column=1, columnspan=2, sticky="ew", pady=4); lr += 1

    ttk.Label(lifecycle, text="Status").grid(row=lr, column=0, sticky="w", pady=4)
    ttk.Label(lifecycle, textvariable=lifecycle_status).grid(row=lr, column=1, columnspan=2, sticky="w", pady=4); lr += 1

    def lifecycle_logger(text: str) -> None:
        workq.put(("log", text))

    def lifecycle_config() -> tuple[Path, dict[str, Any]] | None:
        p = prepare_config()
        if not p:
            return None
        return p, load_config(p)

    def selected_manager_entry() -> dict[str, Any] | None:
        return lifecycle_rows.get(lifecycle_local_choice.get())

    def apply_local_inspection(entry: dict[str, Any] | None) -> None:
        try:
            local_path = Path(str((entry or {}).get("path") or lifecycle_local_path.get())).expanduser()
            if not str(local_path):
                return
            info = inspect_local_kristal(local_path, manager_entry=entry)
            lifecycle_local_path.set(info["path"])
            lifecycle_state_ref.set(info["state_ref"])
            target = str((entry or {}).get("publication_target") or info.get("publication_target") or "none")
            if target in {"public", "private"}:
                lifecycle_target.set(target)
                lifecycle_channel.set(default_channel_id(target, info["slug"]))
            elif lifecycle_target.get() in {"public", "private"}:
                lifecycle_channel.set(default_channel_id(lifecycle_target.get(), info["slug"]))
            else:
                lifecycle_target.set("")
                lifecycle_channel.set("")
            lifecycle_status.set(f"Selected: {info['title']} ({info['slug']})")
        except Exception as exc:
            lifecycle_state_ref.set("")
            lifecycle_status.set(f"Local inspection failed: {exc}")
            append_log(f"Local inspection: {exc}")

    def refresh_manager_catalog() -> None:
        lifecycle_rows.clear()
        try:
            rows = manager_entries(Path(lifecycle_catalog.get()).expanduser().resolve())
            labels: list[str] = []
            for row in rows:
                target = str(row.get("publication_target") or "none")
                label = f"{row.get('title')}  [{target}]  —  {row.get('path')}"
                # Ensure duplicate titles/paths still map deterministically.
                while label in lifecycle_rows:
                    label += " "
                lifecycle_rows[label] = row
                labels.append(label)
            local_combo["values"] = labels
            if labels:
                current = lifecycle_local_choice.get()
                if current not in lifecycle_rows:
                    lifecycle_local_choice.set(labels[0])
                apply_local_inspection(lifecycle_rows[lifecycle_local_choice.get()])
            else:
                lifecycle_status.set("Manager catalog contains no existing Local Kristals")
        except Exception as exc:
            local_combo["values"] = []
            lifecycle_status.set("Manager catalog unavailable; browse a Local Kristal folder directly")
            append_log(f"Manager catalog: {exc}")

    def on_local_choice(_event: Any = None) -> None:
        entry = selected_manager_entry()
        if entry:
            lifecycle_local_path.set(str(entry["path"]))
            apply_local_inspection(entry)
    local_combo.bind("<<ComboboxSelected>>", on_local_choice)

    def on_target_choice(_event: Any = None) -> None:
        try:
            info = inspect_local_kristal(Path(lifecycle_local_path.get()), manager_entry=selected_manager_entry())
            if lifecycle_target.get() in {"public", "private"}:
                lifecycle_channel.set(default_channel_id(lifecycle_target.get(), info["slug"]))
        except Exception:
            pass
    target_combo.bind("<<ComboboxSelected>>", on_target_choice)

    def lifecycle_context() -> tuple[dict[str, Any], dict[str, Any], str, str]:
        prepared = lifecycle_config()
        if not prepared:
            raise BootstrapError("Configuration is not ready")
        _, cfg = prepared
        local_path = lifecycle_local_path.get().strip()
        if not local_path:
            raise BootstrapError("Select a Local Kristal first")
        entry = selected_manager_entry()
        info = inspect_local_kristal(Path(local_path), manager_entry=entry)
        target = lifecycle_target.get().strip().lower()
        if target not in {"public", "private"}:
            raise BootstrapError("Choose publication target: public or private")
        configured = str((entry or {}).get("publication_target") or "none")
        if configured in {"public", "private"} and configured != target:
            raise BootstrapError(f"Manager says publication_target={configured}; change Manager or choose that target")
        collection = next((c["name"] for c in cfg["collections"] if c.get("visibility") == target), None)
        if not collection:
            raise BootstrapError(f"network.toml has no {target} collection")
        lifecycle_state_ref.set(str(info["state_ref"]))
        if not lifecycle_channel.get().strip():
            lifecycle_channel.set(default_channel_id(target, str(info["slug"])))
        return cfg, info, target, str(collection)

    def do_qualify_both() -> None:
        prepared = lifecycle_config()
        if not prepared:
            return
        _, cfg = prepared
        owner = cfg["account"]["owner"]
        public = next(c["name"] for c in cfg["collections"] if c.get("visibility") == "public")
        private = next(c["name"] for c in cfg["collections"] if c.get("visibility") == "private")
        lifecycle_status.set("Qualifying public + private collections...")
        def task() -> Any:
            return {
                "public": qualify_repository(owner, public, log=lifecycle_logger),
                "private": qualify_repository(owner, private, log=lifecycle_logger),
                "result": "ALL KRISTAL COLLECTIONS QUALIFIED SUCCESSFULLY",
            }
        def done(_: Any) -> None:
            lifecycle_status.set("Public + private qualification PASS")
        run_task("Lifecycle / Qualify collections", task, done)

    def do_publish_local() -> None:
        try:
            cfg, info, target, collection = lifecycle_context()
        except Exception as exc:
            messagebox.showerror("Kristal", str(exc)); return
        owner = cfg["account"]["owner"]
        if not messagebox.askyesno(
            "Publish Local Kristal",
            f"Publish {info['title']!r} to {owner}/{collection} ({target})?\n\n"
            f"Setup publishes the exact verified State Snapshot. The AI/GitHub read surface under kristals/{info['slug']}/ is synchronized separately by Kristal Manager and is not rewritten by publication.",
        ):
            return
        lifecycle_status.set(f"Publishing {info['title']} to {target}...")
        def task() -> Any:
            return publish_local_kristal(
                workspace=Path(lifecycle_workspace.get()).expanduser().resolve(),
                owner=owner,
                framework_repository=cfg["framework"]["repository"],
                framework_sha=cfg["framework"]["ref"],
                collection_repo=collection,
                local_path=Path(info["path"]),
                target_visibility=target,
                manager_entry=selected_manager_entry(),
                log=lifecycle_logger,
            )
        def done(result: Any) -> None:
            pub = result.get("publication", {}) if isinstance(result, dict) else {}
            lifecycle_state_ref.set(str(result.get("local", {}).get("state_ref", info["state_ref"])))
            lifecycle_channel.set(str(result.get("activation_channel_default") or default_channel_id(target, info["slug"])))
            lifecycle_status.set(f"Publication PASS: {pub.get('release', 'PASS')}")
        run_task(f"Lifecycle / Publish {info['title']}", task, done)

    def do_verify_selected_publication() -> None:
        try:
            cfg, info, target, collection = lifecycle_context()
        except Exception as exc:
            messagebox.showerror("Kristal", str(exc)); return
        lifecycle_status.set(f"Verifying publication for {info['title']}...")
        def task() -> Any:
            return verify_publication_for_state(
                workspace=Path(lifecycle_workspace.get()).expanduser().resolve(),
                owner=cfg["account"]["owner"],
                framework_repository=cfg["framework"]["repository"],
                framework_sha=cfg["framework"]["ref"],
                collection_repo=collection,
                state_ref=str(info["state_ref"]),
                log=lifecycle_logger,
            )
        def done(result: Any) -> None:
            lifecycle_status.set(f"Publication verification PASS: {result.get('release', 'PASS')}")
        run_task(f"Lifecycle / Verify {info['title']} publication", task, done)

    def do_activate_selected() -> None:
        try:
            cfg, info, target, collection = lifecycle_context()
        except Exception as exc:
            messagebox.showerror("Kristal", str(exc)); return
        channel = lifecycle_channel.get().strip() or default_channel_id(target, info["slug"])
        if not messagebox.askyesno(
            "Activate Kristal publication",
            f"Activate the verified publication for {info['title']!r} on channel {channel!r}?\n\n"
            "Activation is separate from publication and advances a dedicated Git ref with compare-and-swap semantics.",
        ):
            return
        lifecycle_status.set(f"Activating {channel}...")
        def task() -> Any:
            return activate_publication_for_state(
                workspace=Path(lifecycle_workspace.get()).expanduser().resolve(),
                owner=cfg["account"]["owner"],
                framework_repository=cfg["framework"]["repository"],
                framework_sha=cfg["framework"]["ref"],
                collection_repo=collection,
                state_ref=str(info["state_ref"]),
                channel_id=channel,
                environments_mode=cfg.get("features", {}).get("environments", "off"),
                immutable_releases_mode=cfg.get("features", {}).get("immutable_releases", "off"),
                log=lifecycle_logger,
            )
        def done(result: Any) -> None:
            seq = result.get("activation", {}).get("sequence", "?") if isinstance(result, dict) else "?"
            lifecycle_status.set(f"Activation PASS: {channel} seq {seq}")
        run_task(f"Lifecycle / Activate {info['title']}", task, done)

    def do_verify_active_selected() -> None:
        try:
            cfg, info, target, collection = lifecycle_context()
        except Exception as exc:
            messagebox.showerror("Kristal", str(exc)); return
        channel = lifecycle_channel.get().strip() or default_channel_id(target, info["slug"])
        lifecycle_status.set(f"Verifying active channel {channel}...")
        def task() -> Any:
            result = verify_active_channel(
                workspace=Path(lifecycle_workspace.get()).expanduser().resolve(),
                owner=cfg["account"]["owner"],
                framework_repository=cfg["framework"]["repository"],
                framework_sha=cfg["framework"]["ref"],
                public_repo=collection,
                channel_id=channel,
                log=lifecycle_logger,
            )
            active = result.get("activation", {}).get("active_state", {})
            if active.get("state_ref") != info["state_ref"]:
                raise BootstrapError(
                    f"Channel {channel} is active for {active.get('state_ref')!r}, not selected Local Kristal {info['state_ref']!r}"
                )
            return result
        def done(result: Any) -> None:
            seq = result.get("activation", {}).get("sequence", "?") if isinstance(result, dict) else "?"
            lifecycle_status.set(f"Active channel verification PASS: {channel} seq {seq}")
        run_task(f"Lifecycle / Verify active {info['title']}", task, done)

    lifecycle_buttons = ttk.Frame(lifecycle)
    lifecycle_buttons.grid(row=lr, column=0, columnspan=3, sticky="w", pady=(12,6)); lr += 1
    ttk.Button(lifecycle_buttons, text="1. Qualify collections", command=do_qualify_both).pack(side="left", padx=(0,6))
    ttk.Button(lifecycle_buttons, text="2. Publish selected Local", command=do_publish_local).pack(side="left", padx=6)
    ttk.Button(lifecycle_buttons, text="Verify selected publication", command=do_verify_selected_publication).pack(side="left", padx=6)

    lifecycle_buttons2 = ttk.Frame(lifecycle)
    lifecycle_buttons2.grid(row=lr, column=0, columnspan=3, sticky="w", pady=(2,6)); lr += 1
    ttk.Button(lifecycle_buttons2, text="3. Activate selected", command=do_activate_selected).pack(side="left", padx=(0,6))
    ttk.Button(lifecycle_buttons2, text="Verify active channel", command=do_verify_active_selected).pack(side="left", padx=6)

    ttk.Label(
        lifecycle,
        text="alpha.10 is multi-Kristal aware: publications are resolved by state_ref, collection paths are kristals/<slug>/state/state-snapshot.json, and activation channels default to public|private/<slug>/stable. GitHub synchronization/hosting remains independent from formal publication.",
        wraplength=820,
    ).grid(row=lr, column=0, columnspan=3, sticky="w", pady=(8,0))
    lifecycle.columnconfigure(1, weight=1)

    root.after(250, refresh_manager_catalog)

    # Add-repository tab
    repo_name = tk.StringVar()
    repo_visibility = tk.StringVar(value="private")
    repo_role = tk.StringVar(value="collection")
    repo_collection = tk.StringVar()
    rr = 0
    for label, var in [("Repository name", repo_name), ("Collection/group", repo_collection)]:
        ttk.Label(repos, text=label).grid(row=rr, column=0, sticky="w", pady=5)
        ttk.Entry(repos, textvariable=var, width=48).grid(row=rr, column=1, sticky="ew", pady=5); rr += 1
    ttk.Label(repos, text="Visibility").grid(row=rr, column=0, sticky="w", pady=5)
    ttk.Combobox(repos, textvariable=repo_visibility, values=["public", "private", "internal"], state="readonly").grid(row=rr, column=1, sticky="w", pady=5); rr += 1
    ttk.Label(repos, text="Role").grid(row=rr, column=0, sticky="w", pady=5)
    ttk.Combobox(repos, textvariable=repo_role, values=["collection", "directory", "gateway", "publisher"], state="readonly").grid(row=rr, column=1, sticky="w", pady=5); rr += 1
    repos.columnconfigure(1, weight=1)

    def add_repo() -> None:
        name = repo_name.get().strip()
        if not name:
            messagebox.showerror("Kristal", "Repository name is required")
            return
        p = prepare_config()
        if not p: return
        visibility = repo_visibility.get(); role = repo_role.get(); collection = repo_collection.get().strip() or None
        if not messagebox.askyesno("Add Kristal repository", f"Create/configure {name!r} and register it in the private hub?"):
            return
        def task() -> Any:
            cfg = load_config(p)
            return apply_single_repo(GhClient(), cfg, name, visibility, role, collection, True, False)
        run_task(f"Add repository {name}", task)

    ttk.Button(repos, text="Create + configure + register", command=add_repo).grid(row=rr, column=0, columnspan=2, sticky="w", pady=12)
    ttk.Label(repos, text="The repository receives a persistent Kristal node identity and is registered in the private hub.", wraplength=700).grid(row=rr+1, column=0, columnspan=2, sticky="w")

    # Populate convenient defaults after the owner field is completed.
    def owner_defaults(*_args: Any) -> None:
        owner = vars_["owner"].get().strip()
        if owner and not vars_["framework_repo"].get().strip():
            vars_["framework_repo"].set(f"{owner}/KristalV10")
        if owner and not vars_["network_id"].get().strip():
            vars_["network_id"].set(f"urn:kristal:network:{owner}")
    # Bind all owner entries defensively; currently there is exactly one.
    for child in setup.winfo_children():
        if isinstance(child, ttk.Entry) and str(child.cget("textvariable")) == str(vars_["owner"]):
            child.bind("<FocusOut>", owner_defaults)

    poll()
    root.mainloop()


if __name__ == "__main__":
    main()
