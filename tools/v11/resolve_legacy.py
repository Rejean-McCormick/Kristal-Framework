#!/usr/bin/env python3
"""Propose KQ/KP candidates for explicit legacy identifier paths; never rewrites input.

Even 'resolved' is only a unique candidate, NOT permission to alter canonical state.
"""
from __future__ import annotations
import argparse
import json
import sys
import unicodedata
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from validate_v11 import validate_schema, IntegrityError, read

def normalize(s: str) -> str:
    return ' '.join(unicodedata.normalize('NFC',s).casefold().split())

def resolve_requests(requests:dict, lexicons:list[dict], crosswalk:dict) -> dict:
    validate_schema(requests,'kristal-legacy-resolution-requests.schema.json')
    for lex in lexicons:validate_schema(lex,'kristal-lexical-dictionary.schema.json')
    validate_schema(crosswalk,'kristal-external-crosswalk.schema.json')
    lex_index:dict[tuple[str,str,str],list[tuple[str,str,list[str]]]]={}
    for lex in lexicons:
        ns=lex['namespace_id']
        for entry in lex['entries']:
            if entry['status']!='resolved':continue
            for term in [entry['preferred_term'],*entry.get('alternate_terms',[])]:
                key=(lex['language'].lower(),normalize(term), 'entity' if entry['semantic_id'].startswith('KQ') else 'property')
                lex_index.setdefault(key,[]).append((ns,entry['semantic_id'],entry.get('domain_ids',[])))
    wd_index:dict[str,set[tuple[str,str]]]={}
    for m in crosswalk['mappings']:
        if m['status']=='accepted' and m['relation']=='exactMatch':
            key=m['external_ref']['id']
            wd_index.setdefault(key,set()).add((m['local_ref']['namespace_id'],m['local_ref']['id']))
    results=[]
    ids=set()
    for req in requests['requests']:
        if req['request_id'] in ids:raise IntegrityError('duplicate request_id')
        ids.add(req['request_id'])
        expected_prefix='KQ' if req['expected_kind']=='entity' else 'KP'
        lookup=req['lookup']
        if lookup['type']=='term':
            raw=lex_index.get((lookup['language'].lower(),normalize(lookup['term']),req['expected_kind']),[])
            domain=set(req.get('domain_ids',[]))
            # context can narrow candidates but never proves equality
            candidates={(ns,sid) for ns,sid,domains in raw if not domain or not domains or bool(set(domains)&domain)}
            method='lexical_candidate'
        else:
            candidates={p for p in wd_index.get(lookup['id'],set()) if p[1].startswith(expected_prefix)}
            method='accepted_exact_external_mapping'
        found=[{'namespace_id':ns,'id':sid} for ns,sid in sorted(candidates)]
        status='unresolved' if not found else 'resolved' if len(found)==1 else 'ambiguous'
        results.append({'request_id':req['request_id'],'source_path':req['source_path'],'status':status,
                        'candidate_method':method,'candidates':found,
                        'requires_migration_review':True})
    return {'format':'kristal.legacy-resolution-report/11.0','batch_id':requests['batch_id'],
            'canonical_graph_modified':False,'authoritative_identity_decisions':False,'results':results}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--requests',type=Path,required=True)
    parser.add_argument('--lexicon',type=Path,action='append',required=True)
    parser.add_argument('--crosswalk',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=resolve_requests(read(args.requests),[read(p) for p in args.lexicon],read(args.crosswalk))
    serialized=json.dumps(report,indent=2,ensure_ascii=False)+'\n'
    if args.output:args.output.write_text(serialized,encoding='utf-8')
    else:print(serialized,end='')

if __name__=='__main__':
    try: main()
    except (IntegrityError,OSError,json.JSONDecodeError) as exc:
        raise SystemExit(f'Kristal legacy resolver: FAIL: {exc}')
