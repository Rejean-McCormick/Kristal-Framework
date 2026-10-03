#!/usr/bin/env python3
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
CFG=yaml.safe_load((ROOT/'mkdocs.yml').read_text(encoding='utf-8'))
DOCS=ROOT/CFG.get('docs_dir','docs')

def walk(node):
    if isinstance(node,str): yield node
    elif isinstance(node,list):
        for x in node: yield from walk(x)
    elif isinstance(node,dict):
        for x in node.values(): yield from walk(x)

def main():
    missing=[]
    for rel in walk(CFG.get('nav',[])):
        if rel.startswith(('http://','https://')): continue
        if not (DOCS/rel).is_file(): missing.append(rel)
    if missing:
        print('missing mkdocs targets:',*missing,sep='\n'); return 1
    print('mkdocs navigation targets: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
