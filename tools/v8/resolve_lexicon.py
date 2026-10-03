#!/usr/bin/env python3
"""Resolve one semantic reference through a v8 lexicon stack. Non-normative reference helper."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('semantic_id'); ap.add_argument('--identity-space',default='kristall')
    ap.add_argument('--layer',action='append',required=True,help='PRECEDENCE:path/to/lexicon.json')
    a=ap.parse_args(); candidates=[]
    for item in a.layer:
        prec_s,path=item.split(':',1); prec=int(prec_s); doc=load(path)
        for e in doc.get('entries',[]):
            r=e.get('semantic_ref',{})
            if r.get('identity_space')==a.identity_space and r.get('id')==a.semantic_id and e.get('lexical_status')=='resolved':
                candidates.append((prec,doc.get('lexicon_id'),e.get('preferred_term')))
    if not candidates:
        print(json.dumps({'semantic_ref':a.semantic_id,'lexical_status':'missing','render':a.semantic_id},ensure_ascii=False)); return
    top=max(x[0] for x in candidates); best=[x for x in candidates if x[0]==top]
    terms={x[2] for x in best}
    if len(terms)>1:
        print(json.dumps({'semantic_ref':a.semantic_id,'lexical_status':'conflicted','candidates':best},ensure_ascii=False)); return
    print(json.dumps({'semantic_ref':a.semantic_id,'lexical_status':'resolved','term':best[0][2],'lexicon':best[0][1],'precedence':top},ensure_ascii=False))
if __name__=='__main__': main()
