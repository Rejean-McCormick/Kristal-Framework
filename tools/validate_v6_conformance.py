#!/usr/bin/env python3
"""Validate Kristal v6 framework vectors and canonical state semantics."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'docs'/'Technical-Reference'/'kristal-docs-v6'

def fail(msg): raise AssertionError(msg)

def schema_fixture():
    schema=json.loads((BASE/'02-schemas'/'kristal-state.schema.json').read_text(encoding='utf-8'))
    data=json.loads((BASE/'09-test-vectors'/'kristal-state'/'kristal-state.example.json').read_text(encoding='utf-8'))
    errs=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(data),key=lambda e:list(e.path))
    if errs:
        e=errs[0]; fail(f"fixture schema error: {e.message} @ /{'/'.join(map(str,e.path))}")

def executable_tck():
    rc=subprocess.run(['node',str(ROOT/'tools'/'kristal_v6_tck.mjs')],cwd=ROOT)
    if rc.returncode: fail('v6 executable TCK failed')

def main():
    schema_fixture(); print('PASS: v6 schema fixture')
    executable_tck(); print('PASS: v6 executable TCK')
    print('Kristal v6 framework conformance: PASS')
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except AssertionError as exc:
        print(f'FAIL: {exc}',file=sys.stderr); raise SystemExit(1)
