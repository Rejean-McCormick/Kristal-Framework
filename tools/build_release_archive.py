#!/usr/bin/env python3
"""Build a deterministic source release ZIP and SHA-256 sidecar."""
from __future__ import annotations
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DIST = ROOT / "dist"
ARCHIVE = DIST / f"kristal-framework-v{VERSION}.zip"
SIDECAR = DIST / f"kristal-framework-v{VERSION}.zip.sha256"
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", "site", "dist"}


def included(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if path.suffix == ".pyc":
        return False
    return path.is_file()


def main() -> int:
    DIST.mkdir(exist_ok=True)
    files = sorted((p for p in ROOT.rglob("*") if included(p)), key=lambda p: p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    SIDECAR.write_text(f"{digest}  {ARCHIVE.name}\n", encoding="utf-8")
    print(ARCHIVE)
    print(f"sha256:{digest}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
