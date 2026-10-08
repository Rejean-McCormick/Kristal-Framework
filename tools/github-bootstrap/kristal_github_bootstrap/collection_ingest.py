from __future__ import annotations

"""Standalone validator used by the generated GitHub collection-ingest workflow.

This module intentionally depends only on the Python standard library so the exact
same source can be copied into a hosted collection at
``.kristal/tools/validate-read-surface.py``.

It validates the *derived* GitHub/AI read surface produced by Kristal Local Kit
3.2.4+ and transported by Kristal Manager alpha.11+. It does not create or alter
semantic commitments.
"""

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any

VALIDATOR_VERSION = "1.0"
READ_SURFACE_FORMAT = "kristal.github-read-surface/1.0"
SYNC_MANIFEST_FORMAT = "kristal.github-sync-manifest/1.0"
COLLECTION_INDEX_FORMAT = "kristal.github-collection-index/1.0"
SYNC_MANIFEST_REL = PurePosixPath(".kristal/sync-manifest.json")
INDEX_REL = PurePosixPath("kristals/index.json")
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ZERO_SHA = "0" * 40


class ValidationError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError(f"Invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"Expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def _safe_rel(value: str, *, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} is empty")
    if "\\" in value:
        raise ValidationError(f"{label} must use POSIX separators: {value!r}")
    rel = PurePosixPath(value)
    if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
        raise ValidationError(f"Unsafe {label}: {value!r}")
    return rel


def _jcs_key(value: str) -> tuple[int, ...]:
    raw = value.encode("utf-16-be")
    return tuple(int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw), 2))


def _number_to_jcs(value: int | float) -> str:
    if isinstance(value, bool):
        raise TypeError("bool is not a number")
    if isinstance(value, int):
        return str(value)
    if not math.isfinite(value):
        raise ValueError("JCS permits only finite JSON numbers")
    if value == 0.0:
        return "0"
    s = repr(value).lower()
    if s.endswith(".0") and "e" not in s:
        s = s[:-2]
    abs_v = abs(value)
    if 1e-6 <= abs_v < 1e21:
        if "e" in s:
            d = Decimal(s)
            s = format(d, "f")
            if "." in s:
                s = s.rstrip("0").rstrip(".")
        return s
    if "e" not in s:
        d = Decimal(s).normalize()
        s = format(d, "e")
    mantissa, exponent = s.split("e", 1)
    if mantissa.endswith(".0"):
        mantissa = mantissa[:-2]
    exp_i = int(exponent)
    sign = "+" if exp_i >= 0 else "-"
    return f"{mantissa}e{sign}{abs(exp_i)}"


def _canonicalize(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return _number_to_jcs(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(_canonicalize(v) for v in value) + "]"
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise TypeError("JCS object keys must be strings")
        return "{" + ",".join(
            json.dumps(k, ensure_ascii=False, separators=(",", ":")) + ":" + _canonicalize(value[k])
            for k in sorted(value, key=_jcs_key)
        ) + "}"
    raise TypeError(f"Unsupported JSON value for JCS: {type(value).__name__}")


def _run(argv: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(argv, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if p.returncode:
        diagnostic = (p.stderr or p.stdout or "").strip()
        raise ValidationError(f"Command failed ({p.returncode}): {' '.join(argv)}" + (f"\n{diagnostic}" if diagnostic else ""))
    return p


def _manifest_file_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise ValidationError("sync manifest files must be a non-empty array")
    out: dict[str, dict[str, Any]] = {}
    for raw in rows:
        if not isinstance(raw, dict):
            raise ValidationError("sync manifest contains a non-object file entry")
        rel = _safe_rel(str(raw.get("path") or ""), label="read-surface file path").as_posix()
        if rel in out:
            raise ValidationError(f"duplicate read-surface file path: {rel}")
        digest = str(raw.get("sha256") or "")
        if not SHA256_RE.fullmatch(digest):
            raise ValidationError(f"invalid sha256 for {rel}: {digest!r}")
        size = raw.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ValidationError(f"invalid size for {rel}: {size!r}")
        out[rel] = {**raw, "path": rel, "sha256": digest, "size": size}
    return out


def validate_surface(repo_root: Path, root_rel: str, framework_cli: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    root_posix = _safe_rel(root_rel, label="Kristal root")
    if len(root_posix.parts) != 2 or root_posix.parts[0] != "kristals" or root_posix.parts[1] == "index.json":
        raise ValidationError(f"Kristal root must be exactly kristals/<slug>: {root_rel!r}")
    root = (repo_root / Path(root_posix.as_posix())).resolve()
    try:
        root.relative_to(repo_root)
    except ValueError as exc:
        raise ValidationError(f"Kristal root escapes repository: {root_rel}") from exc
    if not root.is_dir():
        raise ValidationError(f"Kristal root is missing: {root_rel}")

    manifest_path = root / Path(SYNC_MANIFEST_REL.as_posix())
    manifest = _load_json(manifest_path)
    if manifest.get("format") != SYNC_MANIFEST_FORMAT:
        raise ValidationError(f"Unsupported sync manifest format at {root_rel}: {manifest.get('format')!r}")
    if manifest.get("read_surface_format") != READ_SURFACE_FORMAT:
        raise ValidationError(f"Unsupported read-surface format at {root_rel}: {manifest.get('read_surface_format')!r}")
    if manifest.get("target_root") != root_posix.as_posix():
        raise ValidationError(f"sync manifest target_root mismatch at {root_rel}")
    slug = str(manifest.get("slug") or "")
    if not slug or slug != root_posix.parts[1]:
        raise ValidationError(f"sync manifest slug mismatch at {root_rel}: {slug!r}")
    surface_digest = str(manifest.get("surface_digest") or "")
    if not SHA256_RE.fullmatch(surface_digest):
        raise ValidationError(f"invalid surface_digest at {root_rel}: {surface_digest!r}")

    files = _manifest_file_map(manifest)
    total = 0
    for rel, item in files.items():
        p = (root / Path(rel)).resolve()
        try:
            p.relative_to(root)
        except ValueError as exc:
            raise ValidationError(f"read-surface path escapes root: {rel}") from exc
        if p.is_symlink():
            raise ValidationError(f"read-surface file must not be a symlink: {root_rel}/{rel}")
        if not p.is_file():
            raise ValidationError(f"read-surface file is missing: {root_rel}/{rel}")
        actual_size = p.stat().st_size
        if actual_size != item["size"]:
            raise ValidationError(f"size mismatch for {root_rel}/{rel}: expected {item['size']}, got {actual_size}")
        actual_digest = _sha256(p)
        if actual_digest != item["sha256"]:
            raise ValidationError(f"digest mismatch for {root_rel}/{rel}: expected {item['sha256']}, got {actual_digest}")
        total += actual_size

    if manifest.get("file_count") != len(files):
        raise ValidationError(f"file_count mismatch at {root_rel}: {manifest.get('file_count')} != {len(files)}")
    if manifest.get("total_bytes") != total:
        raise ValidationError(f"total_bytes mismatch at {root_rel}: {manifest.get('total_bytes')} != {total}")

    entrypoint = _safe_rel(str(manifest.get("entrypoint") or ""), label="AI entrypoint").as_posix()
    if entrypoint not in files or not (root / Path(entrypoint)).is_file():
        raise ValidationError(f"AI entrypoint is not part of the exact read surface: {root_rel}/{entrypoint}")
    for required in ("AI_MANIFEST.json", "ai/INDEX.json"):
        if required not in files:
            raise ValidationError(f"required AI navigation file missing from read surface: {root_rel}/{required}")

    state_rel = next((rel for rel, item in files.items() if item.get("role") == "state_snapshot"), None)
    if state_rel is None and "state/state-snapshot.json" in files:
        state_rel = "state/state-snapshot.json"
    if state_rel is None:
        raise ValidationError(f"read surface has no state_snapshot: {root_rel}")
    state_path = root / Path(state_rel)
    _run(["node", str(framework_cli), "verify-state-v9", str(state_path)], cwd=repo_root)
    state = _load_json(state_path)
    if state.get("state_ref") != manifest.get("state_ref"):
        raise ValidationError(f"state_ref mismatch at {root_rel}")
    if state.get("logical_commitment") != manifest.get("state_logical_commitment"):
        raise ValidationError(f"logical commitment mismatch at {root_rel}")

    ai_manifest = _load_json(root / "AI_MANIFEST.json")
    if ai_manifest.get("state_ref") != manifest.get("state_ref"):
        raise ValidationError(f"AI_MANIFEST state_ref mismatch at {root_rel}")
    if ai_manifest.get("state_logical_commitment") != manifest.get("state_logical_commitment"):
        raise ValidationError(f"AI_MANIFEST commitment mismatch at {root_rel}")

    ai_index = _load_json(root / "ai" / "INDEX.json")
    indexed = ai_index.get("files") or []
    if not isinstance(indexed, list):
        raise ValidationError(f"ai/INDEX.json files must be an array at {root_rel}")
    for item in indexed:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ValidationError(f"invalid ai/INDEX.json file entry at {root_rel}")
        rel = _safe_rel(item["path"], label="AI index file path").as_posix()
        hosted = files.get(rel)
        if hosted is None:
            raise ValidationError(f"AI index references a file outside hosted read surface: {root_rel}/{rel}")
        if item.get("size") is not None and item.get("size") != hosted.get("size"):
            raise ValidationError(f"AI index size drift for {root_rel}/{rel}")
        if item.get("sha256") and item.get("sha256") != hosted.get("sha256"):
            raise ValidationError(f"AI index digest drift for {root_rel}/{rel}")

    materialization_objects = ai_index.get("materialization_blobs") or []
    if not isinstance(materialization_objects, list):
        raise ValidationError(f"ai/INDEX.json materialization_blobs must be an array at {root_rel}")
    if manifest.get("materialization_object_count", 0) != len(materialization_objects):
        raise ValidationError(f"materialization_object_count mismatch at {root_rel}")

    ordered = sorted(files.values(), key=lambda x: str(x["path"]).encode("utf-8"))
    projection = {
        "format": READ_SURFACE_FORMAT,
        "slug": slug,
        "state_ref": manifest.get("state_ref"),
        "state_logical_commitment": manifest.get("state_logical_commitment"),
        "entrypoint": entrypoint,
        "files": [
            {"path": x["path"], "role": x.get("role"), "size": x["size"], "sha256": x["sha256"]}
            for x in ordered
        ],
        "materialization_objects": materialization_objects,
    }
    recomputed_surface = "sha256:" + hashlib.sha256(_canonicalize(projection).encode("utf-8")).hexdigest()
    if recomputed_surface != surface_digest:
        raise ValidationError(f"surface_digest mismatch at {root_rel}: expected {surface_digest}, got {recomputed_surface}")

    allowed = set(files) | {SYNC_MANIFEST_REL.as_posix()}
    actual: set[str] = set()
    for p in root.rglob("*"):
        if p.is_symlink():
            rel = p.relative_to(root).as_posix()
            raise ValidationError(f"symlink is not allowed in hosted read surface: {root_rel}/{rel}")
        if p.is_file():
            actual.add(p.relative_to(root).as_posix())
    extras = sorted(actual - allowed)
    if extras:
        preview = ", ".join(extras[:8]) + (" ..." if len(extras) > 8 else "")
        raise ValidationError(f"unmanaged files are present under exact read surface {root_rel}: {preview}")

    return {
        "root": root_rel,
        "state_ref": manifest.get("state_ref"),
        "surface_digest": surface_digest,
        "file_count": len(files),
        "total_bytes": total,
        "result": "PASS",
    }


def _index_digest(rows: list[dict[str, Any]]) -> str:
    projection = {"format": COLLECTION_INDEX_FORMAT, "kristals": rows}
    raw = json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def validate_index(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    index_path = repo_root / Path(INDEX_REL.as_posix())
    if not index_path.is_file():
        # Empty/legacy collections can exist before the first Manager alpha.11 sync.
        return {"result": "PASS", "count": 0, "status": "not-yet-created"}
    index = _load_json(index_path)
    if index.get("format") != COLLECTION_INDEX_FORMAT:
        raise ValidationError(f"Unsupported collection index format: {index.get('format')!r}")
    rows = index.get("kristals")
    if not isinstance(rows, list):
        raise ValidationError("collection index kristals must be an array")
    if index.get("count") != len(rows):
        raise ValidationError(f"collection index count mismatch: {index.get('count')} != {len(rows)}")
    if index.get("index_digest") != _index_digest(rows):
        raise ValidationError("collection index digest mismatch")

    paths: set[str] = set()
    refs: set[str] = set()
    slugs: set[str] = set()
    expected_order = sorted(rows, key=lambda x: (str(x.get("slug") or "").encode("utf-8"), str(x.get("path") or "").encode("utf-8")))
    if rows != expected_order:
        raise ValidationError("collection index rows are not in deterministic slug/path order")

    for item in rows:
        if not isinstance(item, dict):
            raise ValidationError("collection index contains a non-object entry")
        path = _safe_rel(str(item.get("path") or ""), label="collection index path").as_posix()
        parts = PurePosixPath(path).parts
        if len(parts) != 2 or parts[0] != "kristals" or parts[1] == "index.json":
            raise ValidationError(f"collection index path must be kristals/<slug>: {path!r}")
        slug = str(item.get("slug") or "")
        state_ref = str(item.get("state_ref") or "")
        if slug != parts[1]:
            raise ValidationError(f"collection index slug/path mismatch: {slug!r} vs {path!r}")
        if not state_ref:
            raise ValidationError(f"collection index entry has no state_ref: {path}")
        if path in paths or state_ref in refs or slug in slugs:
            raise ValidationError(f"collection index identity/path collision at {path}")
        paths.add(path); refs.add(state_ref); slugs.add(slug)
        manifest_path = repo_root / Path(path) / Path(SYNC_MANIFEST_REL.as_posix())
        if not manifest_path.is_file():
            raise ValidationError(f"collection index points to missing sync manifest: {path}")
        manifest = _load_json(manifest_path)
        if manifest.get("format") != SYNC_MANIFEST_FORMAT:
            raise ValidationError(f"collection index points to unsupported sync manifest: {path}")
        if manifest.get("state_ref") != state_ref:
            raise ValidationError(f"collection index state_ref drift at {path}")
        if manifest.get("surface_digest") != item.get("surface_digest"):
            raise ValidationError(f"collection index surface_digest drift at {path}")
        expected_entry = f"{path}/{manifest.get('entrypoint') or 'AI_START_HERE.md'}"
        if item.get("entrypoint") != expected_entry:
            raise ValidationError(f"collection index entrypoint drift at {path}")
        if item.get("state_logical_commitment") != manifest.get("state_logical_commitment"):
            raise ValidationError(f"collection index commitment drift at {path}")
        if item.get("file_count") != manifest.get("file_count") or item.get("total_bytes") != manifest.get("total_bytes"):
            raise ValidationError(f"collection index read-surface stats drift at {path}")

    return {"result": "PASS", "count": len(rows), "index_digest": index.get("index_digest")}


def _event_json() -> dict[str, Any]:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        return {}
    p = Path(path)
    if not p.is_file():
        return {}
    try:
        value = json.loads(p.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _git_changed_paths(repo_root: Path) -> list[str]:
    event_name = os.environ.get("GITHUB_EVENT_NAME", "workflow_dispatch")
    event = _event_json()
    head = os.environ.get("GITHUB_SHA") or str(event.get("after") or "")
    base = ""
    if event_name == "push":
        base = str(event.get("before") or "")
    elif event_name == "pull_request":
        pr = event.get("pull_request") if isinstance(event.get("pull_request"), dict) else {}
        base_info = pr.get("base") if isinstance(pr, dict) and isinstance(pr.get("base"), dict) else {}
        base = str(base_info.get("sha") or "")
    if not head:
        p = _run(["git", "rev-parse", "HEAD"], cwd=repo_root)
        head = (p.stdout or "").strip()
    if base and base != ZERO_SHA:
        p = subprocess.run(["git", "diff", "--name-only", base, head], cwd=str(repo_root), text=True, capture_output=True)
        if p.returncode == 0:
            return [x.strip() for x in (p.stdout or "").splitlines() if x.strip()]
    p = _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", head], cwd=repo_root)
    return [x.strip() for x in (p.stdout or "").splitlines() if x.strip()]


def discover_roots(repo_root: Path) -> list[str]:
    repo_root = repo_root.resolve()
    event_name = os.environ.get("GITHUB_EVENT_NAME", "workflow_dispatch")
    roots: set[str] = set()
    if event_name == "workflow_dispatch":
        index_path = repo_root / Path(INDEX_REL.as_posix())
        if index_path.is_file():
            index = _load_json(index_path)
            for item in index.get("kristals") or []:
                if isinstance(item, dict) and item.get("path"):
                    roots.add(str(item["path"]))
        else:
            for manifest in (repo_root / "kristals").glob("*/.kristal/sync-manifest.json") if (repo_root / "kristals").is_dir() else []:
                roots.add(manifest.parent.parent.relative_to(repo_root).as_posix())
    else:
        changed = _git_changed_paths(repo_root)
        operational = {".kristal/tools/validate-read-surface.py", ".github/workflows/kristal-ingest.yml"}
        if any(path in operational for path in changed):
            index_path = repo_root / Path(INDEX_REL.as_posix())
            if index_path.is_file():
                index = _load_json(index_path)
                for item in index.get("kristals") or []:
                    if isinstance(item, dict) and item.get("path"):
                        roots.add(str(item["path"]))
        else:
            for path in changed:
                rel = PurePosixPath(path)
                if len(rel.parts) >= 2 and rel.parts[0] == "kristals" and rel.parts[1] != "index.json":
                    root = PurePosixPath("kristals", rel.parts[1]).as_posix()
                    if (repo_root / Path(root) / Path(SYNC_MANIFEST_REL.as_posix())).is_file():
                        roots.add(root)
    return sorted(roots, key=lambda x: x.encode("utf-8"))


def _cmd_discover(args: argparse.Namespace) -> int:
    root = Path(args.repo).resolve()
    roots = discover_roots(root)
    min_size = max(1, int(args.min_shard_size))
    shard_size = max(min_size, math.ceil(len(roots) / 240)) if roots else min_size
    shards = math.ceil(len(roots) / shard_size) if roots else 0
    matrix = {"include": [{"id": i} for i in range(shards)]}
    print("count=" + str(len(roots)))
    print("shard_size=" + str(shard_size))
    print("matrix=" + json.dumps(matrix, separators=(",", ":")))
    return 0


def _cmd_validate_index(args: argparse.Namespace) -> int:
    result = validate_index(Path(args.repo))
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


def _cmd_validate_shard(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    roots = discover_roots(repo)
    shard_id = int(args.shard_id)
    shard_size = int(args.shard_size)
    start = shard_id * shard_size
    selected = roots[start:start + shard_size]
    if not selected:
        print(json.dumps({"result": "PASS", "validated": 0, "shard": shard_id}))
        return 0
    framework_cli = Path(args.framework_cli).resolve()
    if not framework_cli.is_file():
        raise ValidationError(f"Framework CLI not found: {framework_cli}")
    results = []
    for i, root in enumerate(selected, 1):
        print(f"[{i}/{len(selected)}] validate {root}", file=sys.stderr)
        results.append(validate_surface(repo, root, framework_cli))
    print(json.dumps({"result": "PASS", "validated": len(results), "shard": shard_id, "surfaces": results}, ensure_ascii=False, separators=(",", ":")))
    return 0



def _cmd_validate_root(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    framework_cli = Path(args.framework_cli).resolve()
    if not framework_cli.is_file():
        raise ValidationError(f"Framework CLI not found: {framework_cli}")
    result = validate_surface(repo, args.root, framework_cli)
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate Kristal GitHub collection read surfaces.")
    sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("discover")
    d.add_argument("--repo", default=".")
    d.add_argument("--min-shard-size", type=int, default=50)
    d.set_defaults(func=_cmd_discover)
    i = sub.add_parser("validate-index")
    i.add_argument("--repo", default=".")
    i.set_defaults(func=_cmd_validate_index)
    s = sub.add_parser("validate-shard")
    s.add_argument("--repo", default=".")
    s.add_argument("--shard-id", required=True, type=int)
    s.add_argument("--shard-size", required=True, type=int)
    s.add_argument("--framework-cli", required=True)
    s.set_defaults(func=_cmd_validate_shard)
    r = sub.add_parser("validate-root")
    r.add_argument("--repo", default=".")
    r.add_argument("--root", required=True)
    r.add_argument("--framework-cli", required=True)
    r.set_defaults(func=_cmd_validate_root)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
