from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from .core import BootstrapError

RUN_URL_RE = re.compile(r"/actions/runs/(\d+)(?:\b|/|$)")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

LogFn = Callable[[str], None]


def _noop(_: str) -> None:
    pass


def _run(
    argv: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        kwargs: dict[str, Any] = {}
        if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        p = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            text=True,
            input=input_text,
            capture_output=True,
            **kwargs,
        )
    except FileNotFoundError as exc:
        raise BootstrapError(f"Required executable not found: {argv[0]}") from exc
    if check and p.returncode:
        diagnostic = (p.stderr or p.stdout or "").strip()
        raise BootstrapError(
            f"Command failed ({p.returncode}): {' '.join(argv)}"
            + (f"\n{diagnostic}" if diagnostic else "")
        )
    return p


def _json_command(argv: list[str], *, cwd: Path | None = None) -> Any:
    p = _run(argv, cwd=cwd)
    raw = (p.stdout or "").strip()
    if not raw:
        raise BootstrapError(f"Command returned no JSON: {' '.join(argv)}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"Command returned invalid JSON: {' '.join(argv)}\n{raw}") from exc


def require_tools() -> dict[str, str]:
    paths: dict[str, str] = {}
    for name in ("gh", "git", "node"):
        found = shutil.which(name)
        if not found:
            raise BootstrapError(f"Required executable is not available on PATH: {name}")
        paths[name] = found
    return paths


def extract_run_id(text: str) -> str | None:
    matches = RUN_URL_RE.findall(text or "")
    return matches[-1] if matches else None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_genesis_state(state_ref: str, collection: str = "public", created_at: str | None = None) -> dict[str, Any]:
    if not state_ref.strip():
        raise BootstrapError("state_ref is required")
    return {
        "schema_version": "9.0",
        "artifact_type": "kristal_state_snapshot",
        "state_ref": state_ref.strip(),
        "logical_commitment": {
            "profile": "kristal.state-commitment/jcs-sha256-v1",
            "digest": "sha256:" + ("0" * 64),
        },
        "members": [],
        "references": [],
        "parents": [],
        "scope": {"collection": collection, "purpose": "genesis"},
        "created_at": created_at or utc_now(),
    }


def local_paths(workspace: Path, framework_repository: str, collection_repository: str) -> dict[str, Path]:
    framework_name = framework_repository.split("/", 1)[-1]
    return {
        "workspace": workspace,
        "framework": workspace / framework_name,
        "collection": workspace / collection_repository,
    }



MANAGER_FORMAT = "kristal-local-registry/2.0"
LOCAL_STATE_CANDIDATES = (
    "build/v9/state-snapshot.json",
    "state/state-snapshot.json",
    ".kristal/v9/state-snapshot.json",
    "state-snapshot.json",
)


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", (value or "").strip()).strip(".-_").lower()
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        raise BootstrapError("Kristal slug is empty after normalization")
    return slug[:96]


def load_manager_catalog(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise BootstrapError(f"Kristal Manager catalog not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise BootstrapError(f"Unable to read Kristal Manager catalog: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BootstrapError("Kristal Manager catalog must be a JSON object")
    fmt = str(data.get("format") or "")
    if fmt != MANAGER_FORMAT:
        raise BootstrapError(f"Unsupported Kristal Manager catalog format: {fmt or 'missing'}")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise BootstrapError("Kristal Manager catalog entries must be an array")
    return data


def manager_entries(path: Path, *, existing_only: bool = True) -> list[dict[str, Any]]:
    data = load_manager_catalog(path)
    rows: list[dict[str, Any]] = []
    for raw in data.get("entries", []):
        if not isinstance(raw, dict) or not raw.get("path"):
            continue
        local = Path(str(raw["path"])).expanduser()
        if existing_only and not local.is_dir():
            continue
        row = dict(raw)
        row["path"] = str(local.resolve()) if local.exists() else str(local)
        row["title"] = str(row.get("title") or local.name)
        row["slug"] = slugify(str(row.get("slug") or local.name))
        target = str(row.get("publication_target") or "none").lower()
        row["publication_target"] = target if target in {"public", "private", "none"} else "none"
        rows.append(row)
    return sorted(rows, key=lambda r: (str(r.get("title") or "").casefold(), str(r.get("path") or "").casefold()))


def discover_local_state(local_path: Path) -> Path:
    root = local_path.expanduser().resolve()
    if not root.is_dir():
        raise BootstrapError(f"Local Kristal folder not found: {root}")
    for rel in LOCAL_STATE_CANDIDATES:
        candidate = root / rel
        if candidate.is_file():
            return candidate
    release_dir = root / "release" / "v9" / "states"
    if release_dir.is_dir():
        candidates = sorted(
            (p for p in release_dir.glob("*.json") if p.is_file()),
            key=lambda p: (p.stat().st_mtime_ns, p.name),
            reverse=True,
        )
        if candidates:
            return candidates[0]
    raise BootstrapError(
        f"No v9 State Snapshot found in {root}. Run the Local Kit build-v9 first. "
        f"Expected one of: {', '.join(LOCAL_STATE_CANDIDATES)} or release/v9/states/*.json"
    )


def inspect_local_kristal(local_path: Path, *, manager_entry: dict[str, Any] | None = None) -> dict[str, Any]:
    root = local_path.expanduser().resolve()
    workspace_doc: dict[str, Any] = {}
    workspace_file = root / "kristal.workspace.json"
    if workspace_file.is_file():
        try:
            loaded = json.loads(workspace_file.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                workspace_doc = loaded
        except Exception as exc:
            raise BootstrapError(f"Invalid Local Kristal workspace file: {workspace_file}: {exc}") from exc
    title = str((manager_entry or {}).get("title") or workspace_doc.get("title") or workspace_doc.get("name") or root.name)
    slug = slugify(str((manager_entry or {}).get("slug") or workspace_doc.get("slug") or root.name))
    target = str((manager_entry or {}).get("publication_target") or "none").lower()
    if target not in {"public", "private", "none"}:
        target = "none"
    state_file = discover_local_state(root)
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise BootstrapError(f"Invalid State Snapshot JSON: {state_file}: {exc}") from exc
    if not isinstance(state, dict) or state.get("artifact_type") != "kristal_state_snapshot":
        raise BootstrapError(f"Not a Kristal v9 State Snapshot: {state_file}")
    state_ref = state.get("state_ref")
    commitment = state.get("logical_commitment")
    if not isinstance(state_ref, str) or not state_ref:
        raise BootstrapError(f"State Snapshot has no state_ref: {state_file}")
    if not isinstance(commitment, dict) or not commitment.get("digest"):
        raise BootstrapError(f"State Snapshot has no logical commitment: {state_file}")
    return {
        "path": str(root),
        "title": title,
        "slug": slug,
        "publication_target": target,
        "workspace_format": workspace_doc.get("format"),
        "state_path": str(state_file),
        "state_ref": state_ref,
        "logical_commitment": commitment,
    }


def collection_state_relative(slug: str) -> str:
    return f"kristals/{slugify(slug)}/state/state-snapshot.json"


def default_channel_id(visibility: str, slug: str) -> str:
    vis = visibility.lower().strip()
    if vis not in {"public", "private"}:
        raise BootstrapError("Publication target must be public or private")
    return f"{vis}/{slugify(slug)}/stable"


def stage_local_state(
    collection_path: Path,
    source_state: Path,
    state_relative: str,
    kristal_cli: Path,
    *,
    log: LogFn = _noop,
) -> dict[str, Any]:
    source = source_state.resolve()
    source_verified = _json_command(["node", str(kristal_cli), "verify-state-v9", str(source)])
    if not source_verified.get("ok"):
        raise BootstrapError(f"Local State Snapshot verification failed: {json.dumps(source_verified.get('issues', []), ensure_ascii=False)}")
    state = json.loads(source.read_text(encoding="utf-8"))
    target = (collection_path / state_relative).resolve()
    try:
        target.relative_to(collection_path.resolve())
    except ValueError as exc:
        raise BootstrapError("Collection state path escapes the repository") from exc
    data = source.read_bytes()
    changed = not target.is_file() or target.read_bytes() != data
    if changed:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        log(f"Staged Local Kristal state: {source} -> {target}")
    else:
        log(f"Collection already contains identical state bytes: {target}")
    copied_verified = _json_command(["node", str(kristal_cli), "verify-state-v9", str(target)])
    if not copied_verified.get("ok"):
        raise BootstrapError("Copied State Snapshot failed verification inside collection")
    return {
        "source": str(source),
        "path": str(target),
        "relative": state_relative,
        "state_ref": state["state_ref"],
        "commitment": copied_verified.get("commitment"),
        "changed": changed,
    }

def verify_local_framework(
    workspace: Path,
    framework_repository: str,
    framework_sha: str,
    *,
    log: LogFn = _noop,
) -> dict[str, str]:
    require_tools()
    if not SHA_RE.fullmatch(framework_sha or ""):
        raise BootstrapError("Framework ref must be a full 40-character SHA")
    paths = local_paths(workspace, framework_repository, "unused")
    framework = paths["framework"]
    if not (framework / ".git").exists():
        raise BootstrapError(f"Framework Git repository not found: {framework}")
    cli = framework / "reference" / "js" / "bin" / "kristal-ref.mjs"
    if not cli.exists():
        raise BootstrapError(f"Kristal reference CLI not found: {cli}")
    head = (_run(["git", "-C", str(framework), "rev-parse", "HEAD"]).stdout or "").strip().lower()
    if head != framework_sha.lower():
        raise BootstrapError(f"Local Framework SHA mismatch. Expected {framework_sha}, found {head}")
    log(f"Framework pinned: {head}")
    return {"path": str(framework), "cli": str(cli), "sha": head}


def prepare_local_collection(
    workspace: Path,
    owner: str,
    repo_name: str,
    *,
    branch: str = "main",
    log: LogFn = _noop,
) -> Path:
    require_tools()
    repo = f"{owner}/{repo_name}"
    target = workspace / repo_name
    workspace.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        log(f"Cloning {repo} -> {target}")
        _run(["gh", "repo", "clone", repo, str(target)])
    elif not (target / ".git").exists():
        raise BootstrapError(f"Local path exists but is not a Git repository: {target}")
    _run(["git", "-C", str(target), "fetch", "origin"])
    _run(["git", "-C", str(target), "checkout", branch])
    _run(["git", "-C", str(target), "pull", "--ff-only", "origin", branch])
    dirty = (_run(["git", "-C", str(target), "status", "--porcelain"]).stdout or "").strip()
    if dirty:
        raise BootstrapError(f"Local repository has uncommitted changes: {target}\n{dirty}")
    log(f"Local repository ready: {target}")
    return target


def ensure_genesis_state(
    collection_path: Path,
    kristal_cli: Path,
    state_relative: str,
    state_ref: str,
    *,
    collection: str = "public",
    log: LogFn = _noop,
) -> dict[str, Any]:
    state_file = (collection_path / state_relative).resolve()
    try:
        state_file.relative_to(collection_path.resolve())
    except ValueError as exc:
        raise BootstrapError("State path escapes the collection repository") from exc
    created = not state_file.exists()
    if state_file.exists():
        log(f"State already exists; preserving bytes: {state_file}")
    else:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state = build_genesis_state(state_ref, collection)
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        commitment = _json_command(["node", str(kristal_cli), "state-commitment-v9", str(state_file)])
        state["logical_commitment"] = {
            "profile": commitment["profile"],
            "digest": commitment["digest"],
        }
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        log(f"Genesis commitment: {commitment['digest']}")
    verified = _json_command(["node", str(kristal_cli), "verify-state-v9", str(state_file)])
    if not verified.get("ok"):
        raise BootstrapError(f"State verification failed: {json.dumps(verified.get('issues', []), ensure_ascii=False)}")
    return {
        "path": str(state_file),
        "state_ref": json.loads(state_file.read_text(encoding="utf-8"))["state_ref"],
        "commitment": verified.get("commitment"),
        "created": created,
    }


def commit_and_push_state(
    collection_path: Path,
    state_relative: str,
    *,
    message: str = "Add Kristal public genesis state",
    branch: str = "main",
    log: LogFn = _noop,
) -> dict[str, Any]:
    _run(["git", "-C", str(collection_path), "add", state_relative])
    staged = (_run(["git", "-C", str(collection_path), "diff", "--cached", "--name-only"]).stdout or "").strip()
    committed = False
    if staged:
        _run(["git", "-C", str(collection_path), "commit", "-m", message])
        _run(["git", "-C", str(collection_path), "push", "origin", branch])
        committed = True
        log("State committed and pushed.")
    else:
        log("State already committed; no Git mutation required.")
    sha = (_run(["git", "-C", str(collection_path), "rev-parse", "HEAD"]).stdout or "").strip().lower()
    if not SHA_RE.fullmatch(sha):
        raise BootstrapError(f"Invalid local HEAD SHA: {sha}")
    return {"sha": sha, "committed": committed}


def remote_head(owner: str, repo_name: str, branch: str = "main") -> str:
    p = _run(["gh", "api", f"repos/{owner}/{repo_name}/commits/{branch}", "--jq", ".sha"])
    sha = (p.stdout or "").strip().lower()
    if not SHA_RE.fullmatch(sha):
        raise BootstrapError(f"GitHub returned invalid {branch} SHA for {owner}/{repo_name}: {sha}")
    return sha


def _workflow_run(owner: str, repo_name: str, run_id: str) -> dict[str, Any]:
    return _json_command(["gh", "run", "view", run_id, "--repo", f"{owner}/{repo_name}", "--json", "databaseId,status,conclusion,headSha,url,workflowName"])


def _qualification_receipt(owner: str, repo_name: str, run_id: str, sha: str) -> dict[str, Any]:
    artifacts = _json_command(["gh", "api", f"repos/{owner}/{repo_name}/actions/runs/{run_id}/artifacts"]).get("artifacts", [])
    expected = f"kristal-qualification-{sha}"
    receipt = next((a for a in artifacts if a.get("name") == expected), None)
    if not receipt:
        raise BootstrapError(f"Qualification succeeded but receipt artifact is missing: {expected}")
    return receipt


def qualify_repository(
    owner: str,
    repo_name: str,
    *,
    workflow: str = "kristal-qualify.yml",
    branch: str = "main",
    log: LogFn = _noop,
) -> dict[str, Any]:
    require_tools()
    repo = f"{owner}/{repo_name}"
    sha = remote_head(owner, repo_name, branch)
    log(f"Qualifying {repo}@{sha}")
    dispatched = _run(["gh", "workflow", "run", workflow, "--repo", repo, "--ref", branch])
    run_id = extract_run_id((dispatched.stdout or "") + "\n" + (dispatched.stderr or ""))
    if not run_id:
        # Fallback for older gh output: select newest workflow_dispatch run on exact SHA.
        listing = _json_command([
            "gh", "run", "list", "--repo", repo, "--workflow", workflow, "--event", "workflow_dispatch",
            "--limit", "20", "--json", "databaseId,headSha,createdAt"
        ])
        candidate = next((r for r in listing if r.get("headSha") == sha), None)
        if not candidate:
            raise BootstrapError("Workflow dispatched but run ID could not be resolved")
        run_id = str(candidate["databaseId"])
    log(f"Qualification run: {run_id}")
    watch = _run(["gh", "run", "watch", run_id, "--repo", repo, "--exit-status"], check=False)
    run = _workflow_run(owner, repo_name, run_id)
    if watch.returncode or run.get("conclusion") != "success" or run.get("headSha") != sha:
        failed = _run(["gh", "run", "view", run_id, "--repo", repo, "--log-failed"], check=False)
        raise BootstrapError(f"Qualification failed for {repo}@{sha}\n{(failed.stdout or failed.stderr or '').strip()}")
    receipt = _qualification_receipt(owner, repo_name, run_id, sha)
    log(f"Qualification PASS: {repo}")
    return {
        "repository": repo,
        "sha": sha,
        "run_id": int(run_id),
        "url": run.get("url"),
        "receipt": receipt.get("name"),
        "receipt_digest": receipt.get("digest"),
        "result": "PASS",
    }


def ensure_exact_qualification(
    owner: str,
    repo_name: str,
    sha: str,
    *,
    workflow: str = "kristal-qualify.yml",
    branch: str = "main",
    log: LogFn = _noop,
) -> dict[str, Any]:
    repo = f"{owner}/{repo_name}"
    # Reuse any already successful run for the exact source SHA when the receipt exists.
    listing = _json_command([
        "gh", "run", "list", "--repo", repo, "--workflow", workflow, "--limit", "30",
        "--json", "databaseId,headSha,status,conclusion,url,event"
    ])
    for run in listing:
        if run.get("headSha") == sha and run.get("status") == "completed" and run.get("conclusion") == "success":
            run_id = str(run["databaseId"])
            try:
                receipt = _qualification_receipt(owner, repo_name, run_id, sha)
            except BootstrapError:
                continue
            log(f"Reusing exact-commit qualification run: {run_id}")
            return {
                "repository": repo,
                "sha": sha,
                "run_id": int(run_id),
                "url": run.get("url"),
                "receipt": receipt.get("name"),
                "receipt_digest": receipt.get("digest"),
                "result": "PASS",
                "reused": True,
            }
    # The branch must still point at the exact candidate before dispatch.
    if remote_head(owner, repo_name, branch) != sha:
        raise BootstrapError("Remote main changed before qualification; refusing to qualify a different candidate")
    result = qualify_repository(owner, repo_name, workflow=workflow, branch=branch, log=log)
    if result["sha"] != sha:
        raise BootstrapError("Qualification ran against a different source commit")
    result["reused"] = False
    return result


def _jobs(owner: str, repo_name: str, run_id: str) -> list[dict[str, Any]]:
    return _json_command(["gh", "api", f"repos/{owner}/{repo_name}/actions/runs/{run_id}/jobs"]).get("jobs", [])


def _releases(owner: str, repo_name: str) -> list[dict[str, Any]]:
    out = _json_command(["gh", "api", f"repos/{owner}/{repo_name}/releases?per_page=50"])
    return out if isinstance(out, list) else []


def find_release_for_commit(owner: str, repo_name: str, sha: str) -> dict[str, Any] | None:
    return next((
        r for r in _releases(owner, repo_name)
        if r.get("target_commitish") == sha and str(r.get("tag_name", "")).startswith("kristal-pub-")
    ), None)



def _release_publication_record(owner: str, repo_name: str, tag: str) -> dict[str, Any] | None:
    repo = f"{owner}/{repo_name}"
    with tempfile.TemporaryDirectory(prefix="kristal-publication-probe-") as td:
        p = _run(
            ["gh", "release", "download", tag, "--repo", repo, "--pattern", "publication.json", "--dir", td],
            check=False,
        )
        if p.returncode:
            return None
        publication = Path(td) / "publication.json"
        if not publication.is_file():
            return None
        try:
            value = json.loads(publication.read_text(encoding="utf-8"))
        except Exception:
            return None
        return value if isinstance(value, dict) else None


def find_release_for_state_ref(
    owner: str,
    repo_name: str,
    state_ref: str,
    *,
    target_commit: str | None = None,
) -> dict[str, Any] | None:
    for release in _releases(owner, repo_name):
        tag = str(release.get("tag_name") or "")
        if not tag.startswith("kristal-pub-") or release.get("draft"):
            continue
        if target_commit and release.get("target_commitish") != target_commit:
            continue
        publication = _release_publication_record(owner, repo_name, tag)
        state = publication.get("state") if isinstance(publication, dict) else None
        if isinstance(state, dict) and state.get("state_ref") == state_ref:
            out = dict(release)
            out["_publication_record"] = publication
            return out
    return None


def verified_publication_for_state_ref(
    owner: str,
    repo_name: str,
    state_ref: str,
    kristal_cli: Path,
    *,
    target_commit: str | None = None,
    log: LogFn = _noop,
) -> tuple[dict[str, Any], dict[str, Any]]:
    release = find_release_for_state_ref(owner, repo_name, state_ref, target_commit=target_commit)
    if not release:
        suffix = f" at commit {target_commit}" if target_commit else ""
        raise BootstrapError(f"No Kristal publication found for state_ref {state_ref!r}{suffix} in {owner}/{repo_name}")
    required = {"state-snapshot.json", "bundle-manifest.json", "publication.json"}
    assets = {a.get("name") for a in release.get("assets", [])}
    missing = sorted(required - assets)
    if missing:
        raise BootstrapError(f"Publication Release is missing required assets: {', '.join(missing)}")
    if release.get("immutable") is False:
        raise BootstrapError("Publication Release is not immutable")
    verified = verify_release_bundle(owner, repo_name, str(release["tag_name"]), kristal_cli, log=log)
    state = verified.get("state") if isinstance(verified, dict) else None
    if not isinstance(state, dict) or state.get("state_ref") != state_ref:
        raise BootstrapError("Independently verified Release does not match requested state_ref")
    return release, verified


def verify_release_bundle(
    owner: str,
    repo_name: str,
    tag: str,
    kristal_cli: Path,
    *,
    log: LogFn = _noop,
) -> dict[str, Any]:
    repo = f"{owner}/{repo_name}"
    with tempfile.TemporaryDirectory(prefix="kristal-verify-") as td:
        _run(["gh", "release", "download", tag, "--repo", repo, "--dir", td])
        verified = _json_command(["node", str(kristal_cli), "verify-publication-bundle-v10", td])
        if not verified.get("ok"):
            raise BootstrapError(f"Downloaded publication verification failed: {json.dumps(verified.get('issues', []), ensure_ascii=False)}")
        log(f"Independent bundle verification PASS: {tag}")
        return verified


def publish_exact_state(
    owner: str,
    repo_name: str,
    sha: str,
    state_relative: str,
    kristal_cli: Path,
    *,
    expected_state_ref: str | None = None,
    workflow: str = "kristal-publish.yml",
    branch: str = "main",
    log: LogFn = _noop,
) -> dict[str, Any]:
    repo = f"{owner}/{repo_name}"
    if remote_head(owner, repo_name, branch) != sha:
        raise BootstrapError("Remote main changed after qualification; refusing publication")
    dispatched = _run([
        "gh", "workflow", "run", workflow, "--repo", repo, "--ref", branch,
        "-f", f"state_file={state_relative}"
    ])
    run_id = extract_run_id((dispatched.stdout or "") + "\n" + (dispatched.stderr or ""))
    if not run_id:
        listing = _json_command([
            "gh", "run", "list", "--repo", repo, "--workflow", workflow, "--event", "workflow_dispatch",
            "--limit", "20", "--json", "databaseId,headSha,createdAt"
        ])
        candidate = next((r for r in listing if r.get("headSha") == sha), None)
        if not candidate:
            raise BootstrapError("Publication workflow dispatched but run ID could not be resolved")
        run_id = str(candidate["databaseId"])
    log(f"Publication run: {run_id}")
    watch = _run(["gh", "run", "watch", run_id, "--repo", repo, "--exit-status"], check=False)
    run = _workflow_run(owner, repo_name, run_id)
    if watch.returncode or run.get("conclusion") != "success" or run.get("headSha") != sha:
        failed = _run(["gh", "run", "view", run_id, "--repo", repo, "--log-failed"], check=False)
        raise BootstrapError(f"Publication failed for {repo}@{sha}\n{(failed.stdout or failed.stderr or '').strip()}")
    jobs = _jobs(owner, repo_name, run_id)
    steps = [s for job in jobs for s in job.get("steps", [])]
    attestation = next((s for s in steps if s.get("name") == "Attest publication bundle"), None)
    if expected_state_ref:
        release, verified = verified_publication_for_state_ref(
            owner, repo_name, expected_state_ref, kristal_cli, target_commit=sha, log=log
        )
    else:
        release = find_release_for_commit(owner, repo_name, sha)
        if not release:
            raise BootstrapError("Publication workflow succeeded but no Kristal Release targets the exact source commit")
        if release.get("draft"):
            raise BootstrapError("Publication Release is still a draft")
        if release.get("immutable") is False:
            raise BootstrapError("Publication Release is not immutable")
        required = {"state-snapshot.json", "bundle-manifest.json", "publication.json"}
        assets = {a.get("name") for a in release.get("assets", [])}
        missing = sorted(required - assets)
        if missing:
            raise BootstrapError(f"Publication Release is missing required assets: {', '.join(missing)}")
        verified = verify_release_bundle(owner, repo_name, release["tag_name"], kristal_cli, log=log)
    return {
        "repository": repo,
        "source_commit": sha,
        "run_id": int(run_id),
        "run_url": run.get("url"),
        "attestation": attestation.get("conclusion") if attestation else "not-reported",
        "release": release["tag_name"],
        "release_url": release.get("html_url"),
        "immutable": release.get("immutable"),
        "assets": sorted(assets),
        "verification": verified,
        "result": "PASS",
    }




def _gh_api_json(
    endpoint: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    check: bool = True,
) -> Any:
    argv = ["gh", "api"]
    if method != "GET":
        argv += ["--method", method]
    argv.append(endpoint)
    input_text = None
    if payload is not None:
        argv += ["--input", "-"]
        input_text = json.dumps(payload, ensure_ascii=False)
    p = _run(argv, check=check, input_text=input_text)
    if p.returncode:
        return p
    raw = (p.stdout or "").strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"GitHub API returned invalid JSON for {endpoint}\n{raw}") from exc


def _same_state_ref(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    if not isinstance(a, dict) or not isinstance(b, dict):
        return False
    ac = a.get("logical_commitment") if isinstance(a.get("logical_commitment"), dict) else {}
    bc = b.get("logical_commitment") if isinstance(b.get("logical_commitment"), dict) else {}
    return (
        a.get("state_ref") == b.get("state_ref")
        and ac.get("profile") == bc.get("profile")
        and ac.get("digest") == bc.get("digest")
    )


def activation_ref_name(channel_id: str) -> str:
    channel = channel_id.strip()
    if not channel:
        raise BootstrapError("Activation channel is required")
    if len(channel) > 128:
        raise BootstrapError("Activation channel is too long")
    slug = re.sub(r"[^a-z0-9._-]+", "-", channel.lower()).strip(".-")
    if not slug:
        slug = "channel"
    slug = slug[:48].rstrip(".-") or "channel"
    suffix = hashlib.sha256(channel.encode("utf-8")).hexdigest()[:10]
    return f"kristal-activation/{slug}-{suffix}"


def _activation_pointer_path() -> str:
    return ".kristal/activation.json"


def _get_git_ref(owner: str, repo_name: str, branch: str) -> dict[str, Any] | None:
    endpoint = f"repos/{owner}/{repo_name}/git/ref/heads/{quote(branch, safe='/')}"
    out = _gh_api_json(endpoint, check=False)
    if isinstance(out, subprocess.CompletedProcess):
        diagnostic = ((out.stderr or "") + "\n" + (out.stdout or "")).lower()
        if "404" in diagnostic or "not found" in diagnostic:
            return None
        raise BootstrapError(f"Unable to read activation ref {branch}: {(out.stderr or out.stdout or '').strip()}")
    return out if isinstance(out, dict) else None


def _read_repo_file(owner: str, repo_name: str, path: str, ref: str) -> tuple[dict[str, Any], bytes] | None:
    endpoint = f"repos/{owner}/{repo_name}/contents/{quote(path, safe='/')}?ref={quote(ref, safe='')}"
    out = _gh_api_json(endpoint, check=False)
    if isinstance(out, subprocess.CompletedProcess):
        diagnostic = ((out.stderr or "") + "\n" + (out.stdout or "")).lower()
        if "404" in diagnostic or "not found" in diagnostic:
            return None
        raise BootstrapError(f"Unable to read {path}@{ref}: {(out.stderr or out.stdout or '').strip()}")
    if not isinstance(out, dict) or out.get("type") != "file" or not isinstance(out.get("content"), str):
        raise BootstrapError(f"Unexpected GitHub content response for {path}@{ref}")
    try:
        raw = base64.b64decode(out["content"].replace("\n", ""), validate=False)
    except Exception as exc:
        raise BootstrapError(f"Unable to decode GitHub content for {path}@{ref}") from exc
    return out, raw


def _verify_activation_document(kristal_cli: Path, activation: dict[str, Any]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="kristal-activation-verify-") as td:
        p = Path(td) / "activation.json"
        p.write_text(json.dumps(activation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result = _json_command(["node", str(kristal_cli), "verify-activation-v9", str(p)])
        if not result.get("ok"):
            raise BootstrapError(f"Activation verification failed: {json.dumps(result.get('issues', []), ensure_ascii=False)}")
        return result


def _simulate_activation_transition(
    kristal_cli: Path,
    activation: dict[str, Any],
    current: dict[str, Any] | None,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="kristal-activation-cas-") as td:
        root = Path(td)
        candidate = root / "candidate.json"
        pointer = root / "active.json"
        candidate.write_text(json.dumps(activation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if current is not None:
            pointer.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result = _json_command(["node", str(kristal_cli), "activate-state-v9", str(candidate), str(pointer)])
        stored = json.loads(pointer.read_text(encoding="utf-8"))
        if stored != activation:
            raise BootstrapError("Reference activation transition did not preserve the candidate activation record")
        return result


def _activation_branch_state(
    owner: str,
    repo_name: str,
    channel_id: str,
) -> dict[str, Any]:
    branch = activation_ref_name(channel_id)
    ref = _get_git_ref(owner, repo_name, branch)
    if ref is None:
        return {"branch": branch, "ref": None, "commit_sha": None, "activation": None}
    commit_sha = str(((ref.get("object") or {}).get("sha") or "")).lower()
    if not SHA_RE.fullmatch(commit_sha):
        raise BootstrapError(f"Activation ref {branch} resolved to an invalid commit SHA: {commit_sha}")
    found = _read_repo_file(owner, repo_name, _activation_pointer_path(), branch)
    if found is None:
        raise BootstrapError(f"Activation branch exists but {_activation_pointer_path()} is missing: {branch}")
    _, raw = found
    try:
        activation = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise BootstrapError(f"Activation pointer is not valid UTF-8 JSON on {branch}") from exc
    return {"branch": branch, "ref": ref, "commit_sha": commit_sha, "activation": activation}


def _write_activation_branch_cas(
    owner: str,
    repo_name: str,
    *,
    branch: str,
    current_commit_sha: str | None,
    source_commit: str,
    activation: dict[str, Any],
) -> str:
    if not SHA_RE.fullmatch(source_commit or ""):
        raise BootstrapError(f"Invalid publication source commit for activation: {source_commit}")
    # Confirm the immutable publication target still names a real Git commit, but
    # keep the activation ref as a tiny operational tree containing only the pointer.
    # That prevents activation metadata from mutating the source branch or carrying
    # the repository workflows onto the activation ref.
    _gh_api_json(f"repos/{owner}/{repo_name}/git/commits/{source_commit}")
    content = json.dumps(activation, indent=2, ensure_ascii=False) + "\n"
    tree = _gh_api_json(
        f"repos/{owner}/{repo_name}/git/trees",
        method="POST",
        payload={
            "tree": [
                {
                    "path": _activation_pointer_path(),
                    "mode": "100644",
                    "type": "blob",
                    "content": content,
                }
            ],
        },
    )
    tree_sha = str((tree or {}).get("sha") or "")
    if not SHA_RE.fullmatch(tree_sha):
        raise BootstrapError("GitHub did not return a valid activation tree SHA")
    parent = current_commit_sha or source_commit
    commit = _gh_api_json(
        f"repos/{owner}/{repo_name}/git/commits",
        method="POST",
        payload={
            "message": f"Activate Kristal channel {activation['channel_id']} sequence {activation['sequence']}",
            "tree": tree_sha,
            "parents": [parent],
        },
    )
    commit_sha = str((commit or {}).get("sha") or "").lower()
    if not SHA_RE.fullmatch(commit_sha):
        raise BootstrapError("GitHub did not return a valid activation commit SHA")
    if current_commit_sha is None:
        _gh_api_json(
            f"repos/{owner}/{repo_name}/git/refs",
            method="POST",
            payload={"ref": f"refs/heads/{branch}", "sha": commit_sha},
        )
    else:
        # force=false + parent=current ref gives remote compare-and-swap semantics:
        # a concurrent sibling update becomes non-fast-forward and is rejected.
        _gh_api_json(
            f"repos/{owner}/{repo_name}/git/refs/heads/{quote(branch, safe='/')}",
            method="PATCH",
            payload={"sha": commit_sha, "force": False},
        )
    after = _get_git_ref(owner, repo_name, branch)
    resolved = str((((after or {}).get("object") or {}).get("sha") or "")).lower()
    if resolved != commit_sha:
        raise BootstrapError(f"Activation ref did not resolve to the committed activation: {resolved} != {commit_sha}")
    return commit_sha


def _best_effort_deployment(
    owner: str,
    repo_name: str,
    *,
    source_commit: str,
    release_url: str | None,
    activation: dict[str, Any],
    activation_ref: str,
    log: LogFn = _noop,
) -> dict[str, Any]:
    repo = f"{owner}/{repo_name}"
    payload = {
        "ref": source_commit,
        "environment": "production",
        "auto_merge": False,
        "required_contexts": [],
        "description": f"Kristal {activation['channel_id']} sequence {activation['sequence']}",
        "payload": {
            "kristal_channel": activation["channel_id"],
            "kristal_sequence": activation["sequence"],
            "activation_ref": activation_ref,
        },
        "transient_environment": False,
        "production_environment": True,
    }
    try:
        deployment = _gh_api_json(f"repos/{owner}/{repo_name}/deployments", method="POST", payload=payload)
        deployment_id = int((deployment or {}).get("id"))
        status_payload: dict[str, Any] = {
            "state": "success",
            "environment": "production",
            "description": f"Kristal activation sequence {activation['sequence']}",
            "auto_inactive": True,
        }
        if release_url:
            status_payload["environment_url"] = release_url
        status = _gh_api_json(
            f"repos/{owner}/{repo_name}/deployments/{deployment_id}/statuses",
            method="POST",
            payload=status_payload,
        )
        log(f"GitHub production deployment recorded: {deployment_id}")
        return {
            "repository": repo,
            "deployment_id": deployment_id,
            "deployment_url": (deployment or {}).get("url"),
            "status": (status or {}).get("state", "success"),
            "result": "PASS",
        }
    except Exception as exc:
        log(f"WARNING: GitHub Environment deployment unavailable (best_effort): {exc}")
        return {"repository": repo, "result": "UNAVAILABLE", "reason": str(exc)}


def latest_publication(
    *,
    workspace: Path,
    owner: str,
    framework_repository: str,
    framework_sha: str,
    public_repo: str,
    log: LogFn = _noop,
) -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    fw = verify_local_framework(workspace, framework_repository, framework_sha, log=log)
    releases = [r for r in _releases(owner, public_repo) if str(r.get("tag_name", "")).startswith("kristal-pub-") and not r.get("draft")]
    if not releases:
        raise BootstrapError(f"No published Kristal Release found in {owner}/{public_repo}")
    release = releases[0]
    required = {"state-snapshot.json", "bundle-manifest.json", "publication.json"}
    assets = {a.get("name") for a in release.get("assets", [])}
    missing = sorted(required - assets)
    if missing:
        raise BootstrapError(f"Latest Release is missing required assets: {', '.join(missing)}")
    verified = verify_release_bundle(owner, public_repo, release["tag_name"], Path(fw["cli"]), log=log)
    if not isinstance(verified.get("state"), dict):
        raise BootstrapError("Verified publication bundle did not expose a state reference")
    return fw, release, verified


def activate_latest_publication(
    *,
    workspace: Path,
    owner: str,
    framework_repository: str,
    framework_sha: str,
    public_repo: str,
    channel_id: str = "public/stable",
    environments_mode: str = "best_effort",
    immutable_releases_mode: str = "best_effort",
    log: LogFn = _noop,
) -> dict[str, Any]:
    if environments_mode == "required":
        raise BootstrapError(
            "Lifecycle activation with environments=required needs a workflow-mediated approval gate; "
            "alpha.10 refuses to bypass that governance. Use best_effort/off or add the required activation workflow profile."
        )
    fw, release, verified = latest_publication(
        workspace=workspace,
        owner=owner,
        framework_repository=framework_repository,
        framework_sha=framework_sha,
        public_repo=public_repo,
        log=log,
    )
    if immutable_releases_mode == "required" and release.get("immutable") is not True:
        raise BootstrapError("Activation requires an immutable GitHub Release, but the selected Release is not immutable")
    active_state = verified["state"]
    branch_state = _activation_branch_state(owner, public_repo, channel_id)
    branch = branch_state["branch"]
    current = branch_state["activation"]
    if current is not None:
        _verify_activation_document(Path(fw["cli"]), current)
        if current.get("channel_id") != channel_id:
            raise BootstrapError(f"Activation channel mismatch: {current.get('channel_id')} != {channel_id}")
        if _same_state_ref(current.get("active_state"), active_state):
            log(f"Channel already active at sequence {current.get('sequence')}; no activation mutation required.")
            checked = verify_active_channel(
                workspace=workspace,
                owner=owner,
                framework_repository=framework_repository,
                framework_sha=framework_sha,
                public_repo=public_repo,
                channel_id=channel_id,
                log=log,
            )
            checked["reused"] = True
            return checked
        sequence = int(current.get("sequence", -1)) + 1
        if sequence <= 0:
            raise BootstrapError("Existing activation has an invalid sequence")
    else:
        sequence = 1
    activation: dict[str, Any] = {
        "schema_version": "9.0",
        "artifact_type": "kristal_activation",
        "channel_id": channel_id,
        "active_state": active_state,
        "sequence": sequence,
        "updated_at": utc_now(),
        "signatures": [],
        "extensions": {
            "kristal.host/github/1.0": {
                "publication_id": verified.get("publication_id"),
                "release_tag": release.get("tag_name"),
                "source_commit": release.get("target_commitish"),
            }
        },
    }
    if current is not None:
        activation["previous_state"] = current["active_state"]
        activation["expected_previous"] = current["active_state"]
    _verify_activation_document(Path(fw["cli"]), activation)
    transition = _simulate_activation_transition(Path(fw["cli"]), activation, current)
    log(f"Activation candidate verified: {channel_id} sequence {sequence}")
    activation_commit = _write_activation_branch_cas(
        owner,
        public_repo,
        branch=branch,
        current_commit_sha=branch_state["commit_sha"],
        source_commit=str(release.get("target_commitish") or ""),
        activation=activation,
    )
    log(f"Activation CAS committed: {branch}@{activation_commit}")
    deployment: dict[str, Any] | None = None
    if environments_mode == "best_effort":
        deployment = _best_effort_deployment(
            owner,
            public_repo,
            source_commit=str(release.get("target_commitish") or ""),
            release_url=release.get("html_url"),
            activation=activation,
            activation_ref=branch,
            log=log,
        )
    checked = verify_active_channel(
        workspace=workspace,
        owner=owner,
        framework_repository=framework_repository,
        framework_sha=framework_sha,
        public_repo=public_repo,
        channel_id=channel_id,
        log=log,
    )
    checked.update({
        "transition": transition,
        "deployment": deployment,
        "reused": False,
        "result": "KRISTAL ACTIVATION VERIFIED END-TO-END",
    })
    return checked


def verify_active_channel(
    *,
    workspace: Path,
    owner: str,
    framework_repository: str,
    framework_sha: str,
    public_repo: str,
    channel_id: str = "public/stable",
    log: LogFn = _noop,
) -> dict[str, Any]:
    fw = verify_local_framework(workspace, framework_repository, framework_sha, log=log)
    state = _activation_branch_state(owner, public_repo, channel_id)
    activation = state.get("activation")
    if not isinstance(activation, dict):
        raise BootstrapError(f"No active Kristal channel found for {channel_id}")
    schema_check = _verify_activation_document(Path(fw["cli"]), activation)
    if activation.get("channel_id") != channel_id:
        raise BootstrapError(f"Activation channel mismatch: {activation.get('channel_id')} != {channel_id}")
    host_ext = ((activation.get("extensions") or {}).get("kristal.host/github/1.0") or {})
    tag = host_ext.get("release_tag")
    source_commit = host_ext.get("source_commit")
    if not isinstance(tag, str) or not tag.startswith("kristal-pub-"):
        raise BootstrapError("Activation record does not identify its GitHub publication Release")
    release = _gh_api_json(f"repos/{owner}/{public_repo}/releases/tags/{quote(tag, safe='')}")
    if not isinstance(release, dict) or release.get("draft"):
        raise BootstrapError(f"Activation Release is unavailable or still a draft: {tag}")
    if source_commit and release.get("target_commitish") != source_commit:
        raise BootstrapError("Activation source commit does not match the Release target")
    verified = verify_release_bundle(owner, public_repo, tag, Path(fw["cli"]), log=log)
    if not _same_state_ref(activation.get("active_state"), verified.get("state")):
        raise BootstrapError("Active channel state does not match the independently verified publication bundle")
    log(f"Active channel verification PASS: {channel_id} sequence {activation.get('sequence')}")
    return {
        "repository": f"{owner}/{public_repo}",
        "channel_id": channel_id,
        "activation_ref": state["branch"],
        "activation_commit": state["commit_sha"],
        "pointer_path": _activation_pointer_path(),
        "activation": activation,
        "activation_schema": schema_check,
        "release": tag,
        "release_url": release.get("html_url"),
        "immutable": release.get("immutable"),
        "publication_verification": verified,
        "result": "PASS",
    }

def publish_public_genesis(
    *,
    workspace: Path,
    owner: str,
    framework_repository: str,
    framework_sha: str,
    public_repo: str,
    state_relative: str,
    state_ref: str,
    branch: str = "main",
    log: LogFn = _noop,
) -> dict[str, Any]:
    fw = verify_local_framework(workspace, framework_repository, framework_sha, log=log)
    collection = prepare_local_collection(workspace, owner, public_repo, branch=branch, log=log)
    state = ensure_genesis_state(collection, Path(fw["cli"]), state_relative, state_ref, collection="public", log=log)
    git_result = commit_and_push_state(collection, state_relative, branch=branch, log=log)
    sha = git_result["sha"]
    remote = remote_head(owner, public_repo, branch)
    if remote != sha:
        raise BootstrapError(f"Remote {branch} does not match local publication candidate: {remote} != {sha}")
    qualification = ensure_exact_qualification(owner, public_repo, sha, branch=branch, log=log)
    publication = publish_exact_state(owner, public_repo, sha, state_relative, Path(fw["cli"]), branch=branch, log=log)
    return {
        "framework": fw,
        "state": state,
        "git": git_result,
        "qualification": qualification,
        "publication": publication,
        "result": "KRISTAL PUBLICATION VERIFIED END-TO-END",
    }


def verify_latest_publication(
    *,
    workspace: Path,
    owner: str,
    framework_repository: str,
    framework_sha: str,
    public_repo: str,
    log: LogFn = _noop,
) -> dict[str, Any]:
    fw = verify_local_framework(workspace, framework_repository, framework_sha, log=log)
    releases = [r for r in _releases(owner, public_repo) if str(r.get("tag_name", "")).startswith("kristal-pub-") and not r.get("draft")]
    if not releases:
        raise BootstrapError(f"No published Kristal Release found in {owner}/{public_repo}")
    release = releases[0]
    required = {"state-snapshot.json", "bundle-manifest.json", "publication.json"}
    assets = {a.get("name") for a in release.get("assets", [])}
    missing = sorted(required - assets)
    if missing:
        raise BootstrapError(f"Latest Release is missing required assets: {', '.join(missing)}")
    verified = verify_release_bundle(owner, public_repo, release["tag_name"], Path(fw["cli"]), log=log)
    return {
        "repository": f"{owner}/{public_repo}",
        "release": release["tag_name"],
        "release_url": release.get("html_url"),
        "target_commitish": release.get("target_commitish"),
        "immutable": release.get("immutable"),
        "assets": sorted(assets),
        "verification": verified,
        "result": "PASS",
    }

# ---------------------------------------------------------------------------
# alpha.10 multi-Kristal lifecycle surface
# ---------------------------------------------------------------------------

def publication_for_state_ref(
    *,
    workspace: Path,
    owner: str,
    framework_repository: str,
    framework_sha: str,
    collection_repo: str,
    state_ref: str,
    log: LogFn = _noop,
) -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    """Resolve a publication by semantic state identity, never by repo-global 'latest'."""
    fw = verify_local_framework(workspace, framework_repository, framework_sha, log=log)
    release, verified = verified_publication_for_state_ref(
        owner, collection_repo, state_ref, Path(fw["cli"]), log=log
    )
    return fw, release, verified


def verify_publication_for_state(
    *,
    workspace: Path,
    owner: str,
    framework_repository: str,
    framework_sha: str,
    collection_repo: str,
    state_ref: str,
    log: LogFn = _noop,
) -> dict[str, Any]:
    fw, release, verified = publication_for_state_ref(
        workspace=workspace,
        owner=owner,
        framework_repository=framework_repository,
        framework_sha=framework_sha,
        collection_repo=collection_repo,
        state_ref=state_ref,
        log=log,
    )
    return {
        "repository": f"{owner}/{collection_repo}",
        "state_ref": state_ref,
        "release": release["tag_name"],
        "release_url": release.get("html_url"),
        "target_commitish": release.get("target_commitish"),
        "immutable": release.get("immutable"),
        "verification": verified,
        "framework": fw,
        "result": "PASS",
    }


def publish_local_kristal(
    *,
    workspace: Path,
    owner: str,
    framework_repository: str,
    framework_sha: str,
    collection_repo: str,
    local_path: Path,
    target_visibility: str,
    manager_entry: dict[str, Any] | None = None,
    branch: str = "main",
    log: LogFn = _noop,
) -> dict[str, Any]:
    """Publish one Local Kristal into a public/private collection repository.

    The local folder remains the authoring source. Formal publication stages only the
    exact verified v9 State Snapshot under kristals/<slug>/state/. The optimized
    GitHub/AI read surface is synchronized separately by Kristal Manager.
    """
    target = target_visibility.lower().strip()
    if target not in {"public", "private"}:
        raise BootstrapError("Publication target must be public or private")
    fw = verify_local_framework(workspace, framework_repository, framework_sha, log=log)
    local = inspect_local_kristal(local_path, manager_entry=manager_entry)
    configured_target = str(local.get("publication_target") or "none")
    if configured_target in {"public", "private"} and configured_target != target:
        raise BootstrapError(
            f"Kristal Manager publication_target is {configured_target!r}, but Setup was asked to publish to {target!r}. "
            "Change the Manager configuration or the selected target explicitly."
        )
    collection = prepare_local_collection(workspace, owner, collection_repo, branch=branch, log=log)
    state_relative = collection_state_relative(str(local["slug"]))
    staged = stage_local_state(
        collection,
        Path(str(local["state_path"])),
        state_relative,
        Path(fw["cli"]),
        log=log,
    )
    git_result = commit_and_push_state(
        collection,
        state_relative,
        message=f"Publish Kristal {local['slug']} state",
        branch=branch,
        log=log,
    )
    sha = git_result["sha"]
    remote = remote_head(owner, collection_repo, branch)
    if remote != sha:
        raise BootstrapError(f"Remote {branch} does not match local publication candidate: {remote} != {sha}")
    qualification = ensure_exact_qualification(owner, collection_repo, sha, branch=branch, log=log)
    publication = publish_exact_state(
        owner,
        collection_repo,
        sha,
        state_relative,
        Path(fw["cli"]),
        expected_state_ref=str(local["state_ref"]),
        branch=branch,
        log=log,
    )
    return {
        "framework": fw,
        "local": local,
        "target_visibility": target,
        "collection_repository": f"{owner}/{collection_repo}",
        "collection_state": staged,
        "git": git_result,
        "qualification": qualification,
        "publication": publication,
        "activation_channel_default": default_channel_id(target, str(local["slug"])),
        "result": "KRISTAL LOCAL PUBLICATION VERIFIED END-TO-END",
    }


def activate_publication_for_state(
    *,
    workspace: Path,
    owner: str,
    framework_repository: str,
    framework_sha: str,
    collection_repo: str,
    state_ref: str,
    channel_id: str,
    environments_mode: str = "best_effort",
    immutable_releases_mode: str = "best_effort",
    log: LogFn = _noop,
) -> dict[str, Any]:
    if environments_mode == "required":
        raise BootstrapError(
            "Lifecycle activation with environments=required needs a workflow-mediated approval gate; "
            "alpha.10 refuses to bypass that governance. Use best_effort/off or add the required activation workflow profile."
        )
    fw, release, verified = publication_for_state_ref(
        workspace=workspace,
        owner=owner,
        framework_repository=framework_repository,
        framework_sha=framework_sha,
        collection_repo=collection_repo,
        state_ref=state_ref,
        log=log,
    )
    if immutable_releases_mode == "required" and release.get("immutable") is not True:
        raise BootstrapError("Activation requires an immutable GitHub Release, but the selected Release is not immutable")
    active_state = verified["state"]
    branch_state = _activation_branch_state(owner, collection_repo, channel_id)
    branch = branch_state["branch"]
    current = branch_state["activation"]
    if current is not None:
        _verify_activation_document(Path(fw["cli"]), current)
        if current.get("channel_id") != channel_id:
            raise BootstrapError(f"Activation channel mismatch: {current.get('channel_id')} != {channel_id}")
        if _same_state_ref(current.get("active_state"), active_state):
            log(f"Channel already active at sequence {current.get('sequence')}; no activation mutation required.")
            checked = verify_active_channel(
                workspace=workspace,
                owner=owner,
                framework_repository=framework_repository,
                framework_sha=framework_sha,
                public_repo=collection_repo,
                channel_id=channel_id,
                log=log,
            )
            if not _same_state_ref(checked.get("activation", {}).get("active_state"), active_state):
                raise BootstrapError("Active channel resolved to a different state")
            checked["reused"] = True
            checked["state_ref"] = state_ref
            return checked
        sequence = int(current.get("sequence", -1)) + 1
        if sequence <= 0:
            raise BootstrapError("Existing activation has an invalid sequence")
    else:
        sequence = 1

    activation: dict[str, Any] = {
        "schema_version": "9.0",
        "artifact_type": "kristal_activation",
        "channel_id": channel_id,
        "active_state": active_state,
        "sequence": sequence,
        "updated_at": utc_now(),
        "signatures": [],
        "extensions": {
            "kristal.host/github/1.0": {
                "publication_id": verified.get("publication_id"),
                "release_tag": release.get("tag_name"),
                "source_commit": release.get("target_commitish"),
                "state_ref": state_ref,
            }
        },
    }
    if current is not None:
        activation["previous_state"] = current["active_state"]
        activation["expected_previous"] = current["active_state"]
    _verify_activation_document(Path(fw["cli"]), activation)
    transition = _simulate_activation_transition(Path(fw["cli"]), activation, current)
    log(f"Activation candidate verified: {channel_id} sequence {sequence}")
    activation_commit = _write_activation_branch_cas(
        owner,
        collection_repo,
        branch=branch,
        current_commit_sha=branch_state["commit_sha"],
        source_commit=str(release.get("target_commitish") or ""),
        activation=activation,
    )
    log(f"Activation CAS committed: {branch}@{activation_commit}")
    deployment: dict[str, Any] | None = None
    if environments_mode == "best_effort":
        deployment = _best_effort_deployment(
            owner,
            collection_repo,
            source_commit=str(release.get("target_commitish") or ""),
            release_url=release.get("html_url"),
            activation=activation,
            activation_ref=branch,
            log=log,
        )
    checked = verify_active_channel(
        workspace=workspace,
        owner=owner,
        framework_repository=framework_repository,
        framework_sha=framework_sha,
        public_repo=collection_repo,
        channel_id=channel_id,
        log=log,
    )
    if not _same_state_ref(checked.get("activation", {}).get("active_state"), active_state):
        raise BootstrapError("Post-activation verification resolved to a different state")
    checked.update({
        "state_ref": state_ref,
        "transition": transition,
        "deployment": deployment,
        "reused": False,
        "result": "KRISTAL ACTIVATION VERIFIED END-TO-END",
    })
    return checked
