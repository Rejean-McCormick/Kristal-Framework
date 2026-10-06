#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    contract=json.loads((ROOT/'contracts/contract-set.json').read_text())
    for section in contract['normative'].values():
        for rel in section:
            p=ROOT/rel.rstrip('/')
            if not p.exists(): raise SystemExit(f'missing contract surface: {rel}')
    bundle_path=ROOT/'contracts/knowledge-model-contract.v5.json'
    bundle=json.loads(bundle_path.read_text())
    core=dict(bundle); declared=core.pop('bundle_sha256')
    actual='sha256:'+hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if actual!=declared: raise SystemExit('knowledge-model-contract.v5 bundle hash mismatch')
    for e in bundle['files']:
        p=ROOT/e['path']; b=p.read_bytes(); h='sha256:'+hashlib.sha256(b).hexdigest()
        if h!=e['sha256'] or len(b)!=e['bytes']: raise SystemExit(f'contract file drift: {e["path"]}')
    print('contract set: PASS')
if __name__=='__main__': main()
