#!/usr/bin/env python3
"""Run the complete Kristal framework validation suite."""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, argv: list[str]) -> None:
    print(f"\n== {label} ==")
    rc = subprocess.run(argv, cwd=ROOT)
    if rc.returncode:
        raise SystemExit(rc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-doc-build", action="store_true", help="Skip mkdocs build --strict (local convenience only).")
    args = parser.parse_args()

    run("release integrity", [sys.executable, str(ROOT / "tools" / "validate_release.py")])
    run("framework-vector conformance", [sys.executable, str(ROOT / "tools" / "validate_conformance.py")])

    if args.skip_doc_build:
        print("\nSKIP: strict documentation build (--skip-doc-build)")
    else:
        mkdocs = shutil.which("mkdocs")
        if not mkdocs:
            print("FAIL: mkdocs is required; install requirements-dev.txt or use --skip-doc-build locally", file=sys.stderr)
            return 1
        run("strict documentation build", [mkdocs, "build", "--strict"])

    print("\nKristal framework validation suite: PASS")
    print("Implementation conformance remains a separate claim until a compiler/verifier adapter is tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
