#!/usr/bin/env python3
"""Run Kristal v6 release, v6 conformance and retained v5 compatibility checks."""
from __future__ import annotations
import argparse, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(label,argv):
    print(f'\n== {label} ==')
    rc=subprocess.run(argv,cwd=ROOT)
    if rc.returncode: raise SystemExit(rc.returncode)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--skip-doc-build',action='store_true'); args=ap.parse_args()
    run('v6 release integrity',[sys.executable,str(ROOT/'tools'/'validate_release.py')])
    run('v6 conformance',[sys.executable,str(ROOT/'tools'/'validate_v6_conformance.py')])
    run('legacy v5 framework vectors',[sys.executable,str(ROOT/'tools'/'validate_conformance.py')])
    if args.skip_doc_build:
        print('\nSKIP: strict documentation build')
    else:
        mkdocs=shutil.which('mkdocs')
        if not mkdocs:
            print('FAIL: mkdocs is required; install requirements-dev.txt or use --skip-doc-build',file=sys.stderr); return 1
        run('strict documentation build',[mkdocs,'build','--strict'])
    print('\nKristal v6 validation suite: PASS')
    return 0
if __name__=='__main__': raise SystemExit(main())
