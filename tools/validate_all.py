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
    run('v11 canonical semantics',[sys.executable,str(ROOT/'tools/v11/validate_v11.py')])
    run('v11 dictionary catalog',[sys.executable,str(ROOT/'tools/v11/dictionaries.py'),'audit','--catalog',str(ROOT/'examples/v11/dictionaries/catalog.json'),'--crosswalk',str(ROOT/'examples/v11/external-crosswalk.example.json'),'--registry',str(ROOT/'examples/v11/identity-registry.example.json')])
    run('v11 diK coverage',[sys.executable,str(ROOT/'tools/v11/dik_coverage.py'),'--graph',str(ROOT/'examples/v11/semantic-graph.example.json'),'--registry',str(ROOT/'examples/v11/identity-registry.example.json'),'--crosswalk',str(ROOT/'examples/v11/external-crosswalk.example.json'),'--catalog',str(ROOT/'examples/v11/dictionaries/catalog.json'),'--locales','fr,en,fr-CA'])
    run('v11 diK plan check',[sys.executable,str(ROOT/'tools/v11/dik_conversion_plan.py'),'--plan',str(ROOT/'examples/v11/dik-conversion-plan.example.json'),'--registry',str(ROOT/'examples/v11/identity-registry.example.json'),'--source',str(ROOT/'examples/v11/dik-legacy-sample.json')])
    run('v11 diK/Kit preflight',[sys.executable,str(ROOT/'tools/v11/interop_preflight.py'),'--catalog',str(ROOT/'examples/v11/dictionaries/catalog.json'),'--registry',str(ROOT/'examples/v11/identity-registry.example.json'),'--crosswalk',str(ROOT/'examples/v11/external-crosswalk.example.json'),'--graph',str(ROOT/'examples/v11/semantic-graph.example.json'),'--locales','fr,en,fr-CA'])
    run('v11 negative tests',[sys.executable,'-m','unittest','discover','-s','tools/tests','-p','test_v11_*.py','-v'])
    run('reader discovery profile',[sys.executable,str(ROOT/'tools/check_reader_discovery_profile.py')])
    run('contract set',[sys.executable,str(ROOT/'tools/check_contract_set.py')])
    run('v10 local alignment',[sys.executable,str(ROOT/'tools/check_v10_ecosystem_alignment.py')])
    run('v10 alignment negative tests',[sys.executable,'-m','unittest','discover','-s','tools/tests','-p','test_v10_ecosystem_alignment.py','-v'])
    run('documentation links',[sys.executable,str(ROOT/'tools/check_links.py')])
    run('mkdocs navigation',[sys.executable,str(ROOT/'tools/check_mkdocs.py')])
    run('reference implementation',['npm','test'],ROOT/'reference/js')
    run('github bootstrap',[sys.executable,'-m','unittest','discover','-s','tests','-v'],ROOT/'tools/github-bootstrap')
    print('\nKristal monorepo validation: PASS')
if __name__=='__main__': main()
