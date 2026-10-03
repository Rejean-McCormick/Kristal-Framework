#!/usr/bin/env python3
"""Non-normative semantic-atom AI context compiler for Kristal v8.0.0.

Uses bytes as the portable hard budget. Optional token budgeting is explicitly heuristic unless a
real tokenizer implementation is supplied by a production engine. Whole semantic atoms are selected
or omitted; bucket fragments are not sliced silently.
"""
from __future__ import annotations
import argparse, json, uuid
from pathlib import Path


def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def encoded_bytes(obj): return len(json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf-8'))
def estimate_tokens(obj): return max(1,(encoded_bytes(obj)+3)//4)

def refs_from_payload(payload):
    out=[]; seen=set()
    def walk(x):
        if isinstance(x,dict):
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
        elif isinstance(x,str) and x.startswith(('KQ','KP','KA','KS')) and x[2:].isdigit():
            if x not in seen:
                seen.add(x); out.append({'identity_space':'kristall','id':x})
    walk(payload); return out

def provenance(source_fingerprints, reason):
    if not source_fingerprints: return [{'source_ref':'unknown','retrieval_reason':reason}]
    return [{'source_ref':source_fingerprints[0]['ref'],'retrieval_reason':reason}]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('query_result')
    ap.add_argument('--max-bytes',type=int,default=131072)
    ap.add_argument('--max-tokens',type=int)
    ap.add_argument('--tokenizer-id',default='heuristic-chars-per-token/4')
    ap.add_argument('--encoding',choices=('expanded_json','symbol_table_v1'),default='expanded_json')
    ap.add_argument('--output',required=True)
    a=ap.parse_args(); q=load(a.query_result)
    fps=q.get('source_fingerprints',[]); roots={r.get('id') for r in q.get('resolved_roots',[])}

    candidates=[]
    def add(kind,payload,priority,idx):
        atom={
          'atom_id':f'atom:{kind}:{idx}','kind':kind,'semantic_refs':refs_from_payload(payload),'payload':payload,
          'provenance':provenance(fps,'ai_context_compilation'),'trust_class':'derived','priority':priority
        }
        candidates.append(atom)
    for i,x in enumerate(q.get('result',{}).get('assertions',[])): add('assertion',x,110,i)
    for i,x in enumerate(q.get('result',{}).get('evidence',[])): add('evidence_ref',x,105,i)
    for i,x in enumerate(q.get('result',{}).get('edges',[])): add('edge',x,95,i)
    for i,x in enumerate(q.get('result',{}).get('nodes',[])):
        nid=x.get('id'); add('entity' if x.get('kind')=='entity' else ('property' if x.get('kind')=='property' else 'source'),x,120 if nid in roots else 70,i)
    for i,x in enumerate(q.get('conflicts',[])): add('conflict',x,100,i)
    for i,x in enumerate(q.get('unresolved',[])): add('unresolved',x,90,i)
    candidates.sort(key=lambda x:(-x['priority'],x['atom_id']))

    chosen=[]; used_b=0; used_t=0; dropped=[]
    for atom in candidates:
        cb=encoded_bytes(atom); ct=estimate_tokens(atom)
        fits_bytes=used_b+cb<=a.max_bytes
        fits_tokens=a.max_tokens is None or used_t+ct<=a.max_tokens
        if fits_bytes and fits_tokens:
            chosen.append(atom); used_b+=cb; used_t+=ct
        else:
            dropped.append(atom)

    base_comp=q.get('completeness',{
      'semantic_closure':'unknown','evidence_closure':'unknown','source_coverage':'unknown','truncated':False,'reasons':[]})
    comp=dict(base_comp); reasons=list(comp.get('reasons',[]))
    omissions=list(q.get('omissions',[]))
    if dropped:
        comp['truncated']=True
        if comp.get('semantic_closure')=='complete': comp['semantic_closure']='partial'
        reasons.append('ai_context_budget')
        omissions.append({'kind':'ai_context_budget','count':len(dropped),'atom_ids':[x['atom_id'] for x in dropped]})
    comp['reasons']=sorted(set(reasons))

    context={'atoms':chosen}
    if a.encoding=='symbol_table_v1':
        ids=[]
        for atom in chosen:
            for r in atom.get('semantic_refs',[]):
                if r['id'] not in ids: ids.append(r['id'])
        context['symbol_table']={str(i):sid for i,sid in enumerate(ids)}

    budget={'max_bytes':a.max_bytes,'used_bytes':used_b}
    if a.max_tokens is not None:
        budget.update({'max_tokens':a.max_tokens,'estimated_tokens':used_t,'tokenizer_id':a.tokenizer_id,'token_estimate_kind':'heuristic'})

    doc={
      'schema_version':'8.0','artifact_type':'kristall_ai_context_bundle','bundle_id':'AICB-'+uuid.uuid4().hex[:12],
      'query_id':q['query_id'],'source_fingerprints':fps,'roots':q.get('resolved_roots',[]),'encoding':a.encoding,
      'budget':budget,'selection':{'policy':'semantic_atom_priority','intent':q.get('query_plan',{}).get('intent','semantic_slice'),'atom_ordering':'priority_then_stable_id'},
      'completeness':comp,'context':context,'unresolved':q.get('unresolved',[]),'omissions':omissions
    }
    Path(a.output).write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"AI context: {len(chosen)}/{len(candidates)} atoms, {used_b}/{a.max_bytes} bytes -> {a.output}")
if __name__=='__main__': main()
