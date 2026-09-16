#!/usr/bin/env python3
"""Build a deterministic source release ZIP from Git-tracked files only."""
from __future__ import annotations

import argparse
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DIST = ROOT / "dist"
ARCHIVE = DIST / f"kristal-framework-v{VERSION}.zip"

# These are local/export artifacts even if someone accidentally tracks them.
HARD_EXCLUDED = {
    "CODE_SNAPSHOT_MANIFEST.md",
}
EXCLUDED_PARTS = {".git", ".venv", ".levelupdiag", "__pycache__", "site", "dist"}
TEXT_SUFFIXES = {".md", ".json", ".txt", ".yml", ".yaml", ".py", ".mjs", ".toml"}
TEXT_NAMES = {"VERSION", ".gitattributes", ".gitignore"}


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def ensure_git_worktree() -> None:
    rc = git("rev-parse", "--is-inside-work-tree", check=False)
    if rc.returncode != 0 or rc.stdout.strip() != b"true":
        raise RuntimeError("release archive must be built from a Git work tree")


def ensure_clean_worktree() -> None:
    status = git("status", "--porcelain").stdout
    if status.strip():
        raise RuntimeError("working tree is not clean; commit/stash changes or use --allow-dirty for local diagnostics")


def tracked_paths() -> list[Path]:
    raw = git("ls-files", "-z").stdout
    rels = [part.decode("utf-8") for part in raw.split(b"\0") if part]
    paths: list[Path] = []
    for rel_text in rels:
        rel = Path(rel_text)
        if rel.as_posix() in HARD_EXCLUDED:
            continue
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        path = ROOT / rel
        if path.is_file() and path.suffix != ".pyc":
            paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(ROOT).as_posix())


def archive_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES:
        text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        return text.encode("utf-8")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="local diagnostics only: archive tracked working-tree bytes even when modified",
    )
    args = parser.parse_args()

    ensure_git_worktree()
    if not args.allow_dirty:
        ensure_clean_worktree()

    DIST.mkdir(exist_ok=True)
    files = tracked_paths()
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            zf.writestr(
                info,
                archive_bytes(path),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    print(ARCHIVE)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
