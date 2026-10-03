#!/usr/bin/env python3
from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(label,argv,cwd=ROOT):
    print(f'\n== {label} ==')
    r=subprocess.run(argv,cwd=cwd)
    if r.returncode: raise SystemExit(r.returncode)

def main():
    run('standard',[sys.executable,str(ROOT/'tools/validate_standard.py')])
    run('contract set',[sys.executable,str(ROOT/'tools/check_contract_set.py')])
    run('documentation links',[sys.executable,str(ROOT/'tools/check_links.py')])
    run('mkdocs navigation',[sys.executable,str(ROOT/'tools/check_mkdocs.py')])
    run('reference implementation',['npm','test'],ROOT/'reference/js')
    print('\nKristal monorepo validation: PASS')
if __name__=='__main__': main()
