#!/usr/bin/env python3
"""Check the optional Local Kit 3.3 discovery companion profile (no external I/O)."""
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'profiles/reader-discovery'
PAIR={
 'kristal.discovery.json':'kristal-discovery.schema.json',
 'derived/reader-inventory.json':'kristal-reader-inventory.schema.json',
 'derived/reader-profile.json':'kristal-reader-profile.schema.json',
}

def main():
    example=BASE/'examples/demo-kristal'
    docs={}
    for rel,schemafile in PAIR.items():
        schema=json.loads((BASE/'schemas'/schemafile).read_text())
        Draft202012Validator.check_schema(schema)
        doc=json.loads((example/rel).read_text())
        errors=list(Draft202012Validator(schema).iter_errors(doc))
        if errors:raise ValueError(f'{rel}: {errors[0].message}')
        docs[rel]=doc
    d,i,p=(docs[x] for x in PAIR)
    assert d['state_ref']==i['state_ref']==p['state_ref']
    assert d['source_fingerprint']==i['source_fingerprint']==p['source_fingerprint']
    assert d['reader']['profile']==p['specialization']
    assert d['size']['tracked_local_bytes']==i['storage']['tracked_local_bytes']
    assert d['size']['class']==i['size_class']
    from hashlib import sha256
    for f in i['files']:
        local=(example/f['path']).resolve()
        local.relative_to(example.resolve())
        data=local.read_bytes()
        assert len(data)==f['size_bytes'] and 'sha256:'+sha256(data).hexdigest()==f['sha256']
    print('reader discovery profile: PASS')
if __name__=='__main__':main()
