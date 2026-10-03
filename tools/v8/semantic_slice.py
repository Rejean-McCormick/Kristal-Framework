#!/usr/bin/env python3
"""Non-normative exact semantic-slice reference helper for Kristal v8.0.0.

Consumes v7 registries/mesh without modifying them and emits a typed v8 KQP result.
The helper demonstrates direction/property constraints and explicit partial-result semantics.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import deque
from pathlib import Path


def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return 'sha256:' + hashlib.sha256(Path(p).read_bytes()).hexdigest()

def endpoint_id(x):
    if isinstance(x, dict): return x.get('id')
    return x if isinstance(x, str) else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--entities', required=True)
    ap.add_argument('--properties', required=True)
    ap.add_argument('--assertions', required=True)
    ap.add_argument('--sources', required=True)
    ap.add_argument('--mesh', required=True)
    ap.add_argument('--root', action='append', required=True)
    ap.add_argument('--query-id', default='Q-semantic-slice')
    ap.add_argument('--max-depth', type=int, default=2)
    ap.add_argument('--max-nodes', type=int, default=128)
    ap.add_argument('--max-edges', type=int, default=512)
    ap.add_argument('--direction', choices=('out','in','both'), default='both')
    ap.add_argument('--property', action='append', default=[])
    ap.add_argument('--output', required=True)
    a=ap.parse_args()

    ent=load(a.entities); props=load(a.properties); ass=load(a.assertions); src=load(a.sources); mesh=load(a.mesh)
    entity_map={x['entity_id']:x for x in ent.get('entities',[])}
    property_map={x['property_id']:x for x in props.get('properties',[])}
    source_map={x['source_id']:x for x in src.get('sources',[])}
    edges=mesh.get('edges',[])
    property_filter=set(a.property)

    adj={}
    def add(k,e,other):
        if k: adj.setdefault(k,[]).append((e,other))
    for e in edges:
        if property_filter and e.get('relation') not in property_filter:
            continue
        f=endpoint_id(e.get('from')); t=endpoint_id(e.get('to'))
        if a.direction in ('out','both'): add(f,e,t)
        if a.direction in ('in','both'): add(t,e,f)

    known=set(entity_map)|set(property_map)|set(source_map)
    seen=set(); q=deque((r,0) for r in a.root if r in known or r in adj)
    chosen_edges=[]; chosen_edge_ids=set(); truncated=False; reasons=[]
    while q:
        if len(seen)>=a.max_nodes:
            truncated=True; reasons.append('max_nodes'); break
        node,depth=q.popleft()
        if node in seen: continue
        seen.add(node)
        if depth>=a.max_depth: continue
        for e,other in adj.get(node,[]):
            if len(chosen_edges)>=a.max_edges:
                truncated=True; reasons.append('max_edges'); q.clear(); break
            eid=e.get('edge_id') or json.dumps(e,sort_keys=True,separators=(',',':'))
            if eid not in chosen_edge_ids:
                chosen_edges.append(e); chosen_edge_ids.add(eid)
            if other and other not in seen and len(seen)+len(q)<a.max_nodes:
                q.append((other,depth+1))

    nodes=[]
    for nid in sorted(seen):
        if nid in entity_map: nodes.append({'id':nid,'kind':'entity','record':entity_map[nid]})
        elif nid in property_map: nodes.append({'id':nid,'kind':'property','record':property_map[nid]})
        elif nid in source_map: nodes.append({'id':nid,'kind':'source','record':source_map[nid]})
        else: nodes.append({'id':nid,'kind':'external_or_source_local'})

    included_source_locals={n['id'] for n in nodes if n['kind'] in ('source','external_or_source_local')}
    selected_assertions=[]
    for x in ass.get('assertions',[]):
        sb=x.get('source_binding',{})
        if sb.get('source_kristal_id') in included_source_locals:
            selected_assertions.append(x)

    fps=[]
    for p in (a.entities,a.properties,a.assertions,a.sources,a.mesh):
        fps.append({'ref':str(p),'byte_sha256':sha(p)})

    unresolved=[{'identity_space':'kristall','id':r,'reason':'root_not_found'} for r in a.root if r not in known and r not in adj]
    if unresolved: reasons.append('unresolved_roots')
    reasons=sorted(set(reasons))
    partial=bool(truncated or unresolved)
    omissions=[]
    if truncated:
        omissions.append({'kind':'query_limit','reasons':[r for r in reasons if r.startswith('max_')]})

    doc={
      'schema_version':'8.0','artifact_type':'kristall_query_result','protocol':'kristal-query/1.0',
      'query_id':a.query_id,'mode':'semantic_slice','status':'partial' if partial else 'complete','source_fingerprints':fps,
      'resolved_roots':[{'identity_space':'kristall','id':r} for r in a.root if r in known or r in adj],
      'resolution_candidates':[],
      'result':{'nodes':nodes,'edges':chosen_edges,'assertions':selected_assertions,'evidence':[]},
      'completeness':{
        'semantic_closure':'partial' if partial else 'complete',
        'evidence_closure':'not_requested','source_coverage':'complete','truncated':truncated,'reasons':reasons
      },
      'continuation':{'has_more':False,'ordering_profile':'kristal.query/stable-id-v1'},
      'unresolved':unresolved,'conflicts':[],'omissions':omissions,
      'query_plan':{
        'discovery':'exact','strategy':'identity_graph','intent':'semantic_slice','traversal_direction':a.direction,
        'max_depth':a.max_depth,'max_nodes':a.max_nodes,'max_edges':a.max_edges,'properties':sorted(property_filter),
        'indexes_used':[],'shards_contacted':[]
      }
    }
    Path(a.output).write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"semantic slice: {len(nodes)} nodes, {len(chosen_edges)} edges, status={doc['status']} -> {a.output}")

if __name__=='__main__': main()
