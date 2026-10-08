from __future__ import annotations

import json
import queue
import re
import subprocess
import threading
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

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _q(value: str) -> str:
    """Render a safe TOML basic string using JSON-compatible escapes."""
    return json.dumps(value, ensure_ascii=False)


def render_config(values: dict[str, str]) -> str:
    """Render the minimal supported network.toml used by the GUI."""
    owner = values["owner"].strip()
    kind = values.get("kind", "organization").strip()
    network_id = values.get("network_id", "").strip() or f"urn:kristal:network:{owner}"
    framework_repo = values.get("framework_repo", "").strip() or f"{owner}/Kristal-Framework"
    framework_ref = values.get("framework_ref", "").strip()
    hub = values.get("hub_repo", "kristal-hub").strip() or "kristal-hub"
    public_repo = values.get("public_repo", "kristal-public").strip() or "kristal-public"
    private_repo = values.get("private_repo", "kristal-private").strip() or "kristal-private"
    immutable = values.get("immutable_releases", "best_effort")
    environments = values.get("environments", "best_effort")
    custom_properties = values.get("custom_properties", "best_effort")
    attestations = values.get("attestations", "best_effort")
    private_profile = values.get("create_private_profile", "true").lower() == "true"

    return f'''[account]
owner = {_q(owner)}
kind = {_q(kind)}

[network]
id = {_q(network_id)}

[framework]
repository = {_q(framework_repo)}
ref = {_q(framework_ref)}

[global]
create_dotgithub = true
create_private_profile = {str(private_profile).lower()}
create_profile_repository = true

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
        raise BootstrapError(f"Unable to resolve {repository}@{ref}: {p.stderr.strip()}")
    sha = p.stdout.strip().lower()
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
        "owner": tk.StringVar(),
        "kind": tk.StringVar(value="organization"),
        "network_id": tk.StringVar(),
        "framework_repo": tk.StringVar(),
        "framework_ref": tk.StringVar(),
        "hub_repo": tk.StringVar(value="kristal-hub"),
        "public_repo": tk.StringVar(value="kristal-public"),
        "private_repo": tk.StringVar(value="kristal-private"),
        "immutable_releases": tk.StringVar(value="best_effort"),
        "environments": tk.StringVar(value="best_effort"),
        "custom_properties": tk.StringVar(value="best_effort"),
        "attestations": tk.StringVar(value="best_effort"),
        "create_private_profile": tk.StringVar(value="true"),
    }
    config_path = tk.StringVar(value=str(Path.cwd() / "network.toml"))
    plan_path = tk.StringVar(value=str(Path.cwd() / "kristal-plan.json"))

    mainf = ttk.Frame(root, padding=12)
    mainf.pack(fill="both", expand=True)
    notebook = ttk.Notebook(mainf)
    notebook.pack(fill="both", expand=True)

    setup = ttk.Frame(notebook, padding=12)
    repos = ttk.Frame(notebook, padding=12)
    notebook.add(setup, text="Initial setup")
    notebook.add(repos, text="Add repository")

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

    ttk.Label(setup, text="Framework commit SHA").grid(row=row, column=0, sticky="w", pady=3)
    sha_frame = ttk.Frame(setup)
    sha_frame.grid(row=row, column=1, sticky="ew", pady=3)
    ttk.Entry(sha_frame, textvariable=vars_["framework_ref"]).pack(side="left", fill="x", expand=True)
    def detect_sha() -> None:
        repo = vars_["framework_repo"].get().strip()
        if not repo:
            owner = vars_["owner"].get().strip()
            repo = f"{owner}/Kristal-Framework" if owner else ""
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
        except Exception as exc:
            append_log(f"ERROR: {exc}")
            messagebox.showerror("Kristal GitHub Setup", str(exc))

    ttk.Button(pframe, text="Load", command=load_existing_config).pack(side="left", padx=(6,0))
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
                workq.put(("error", exc))
        threading.Thread(target=worker, daemon=True).start()

    def poll() -> None:
        try:
            while True:
                kind, payload = workq.get_nowait()
                running["value"] = False
                if kind == "error":
                    append_log(f"ERROR: {payload}")
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
            vars_["framework_repo"].set(f"{owner}/Kristal-Framework")
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
