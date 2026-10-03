#!/usr/bin/env python3
"""Build a draft lexical Kristal containing semantic references not covered by existing lexicons.

Non-normative helper for Kristal v8. It never invents translations: missing entries are emitted
with lexical_status="missing".
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

KID = re.compile(r'^(?:KQ|KP|KA|KS)[1-9][0-9]*$')

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def collect(obj, out):
    if isinstance(obj, dict):
        if obj.get('artifact_type') == 'kristal_state':
            for r in obj.get('referents', []):
                if isinstance(r, dict) and isinstance(r.get('ref'), str): out.add(('kristal_v6', r['ref']))
        for v in obj.values(): collect(v, out)
    elif isinstance(obj, list):
        for v in obj: collect(v, out)
    elif isinstance(obj, str) and KID.match(obj): out.add(('kristall', obj))

def covered(lexicons):
    out=set()
    for lp in lexicons:
        doc=load(lp)
        for e in doc.get('entries', []):
            if e.get('lexical_status')=='resolved':
                r=e.get('semantic_ref',{})
                if r.get('identity_space') and r.get('id'): out.add((r['identity_space'],r['id']))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('--language',required=True)
    ap.add_argument('--lexicon-id',required=True)
    ap.add_argument('--existing',action='append',default=[])
    ap.add_argument('--output',required=True)
    a=ap.parse_args()
    refs=set(); collect(load(a.source), refs)
    missing=sorted(refs-covered(a.existing))
    doc={'schema_version':'8.0','artifact_type':'kristall_lexicon','lexicon_id':a.lexicon_id,'language':a.language,
         'scope':{'kind':'project','target_kristals':[str(a.source)]},'dependencies':[],
         'entries':[{'semantic_ref':{'identity_space':space,'id':rid},'lexical_status':'missing'} for space,rid in missing]}
    Path(a.output).write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'{len(missing)} unresolved semantic references -> {a.output}')
if __name__=='__main__': main()
