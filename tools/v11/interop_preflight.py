#!/usr/bin/env python3
"""Read-only Framework v11 preflight of diK -> Authoring Kit catalog handoffs.

This is a companion *verification report*, not a new canonical schema, Kit
commit, diK reconciliation, Wikidata proof, or authority to activate a catalog.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dictionaries import audit, check_schema, read_json, sha256, DictionaryError
from dik_coverage import make_report, validate_counts

PROFILE = 'kristal.v11-dik-authoring-preflight/1.0-candidate'


def _canonical_json(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n'


def _check_identity(catalog: dict, registry: dict, crosswalk: dict) -> dict:
    check_schema(registry,'kristal-identity-registry.schema.json')
    check_schema(crosswalk,'kristal-external-crosswalk.schema.json')
    if catalog['namespace_id'] != registry['namespace_id']:
        raise DictionaryError('catalog/registry namespace mismatch')
    ids={r['id']:r['kind'] for r in registry['identities']}
    if len(ids)!=len(registry['identities']):
        raise DictionaryError('duplicate registry IDs')
    registered_sources={k for k,v in ids.items() if v=='source'}
    approved_local,approved_external=set(),set()
    for mapping in crosswalk['mappings']:
        local=mapping['local_ref']; ext=mapping['external_ref']
        if local['namespace_id'] != registry['namespace_id']:
            raise DictionaryError('crosswalk namespace mismatch')
        kind='entity' if local['id'].startswith('KQ') else 'property'
        if ids.get(local['id']) != kind:
            raise DictionaryError('unregistered or wrong-kind crosswalk target')
        if mapping['status'] == 'accepted':
            for evidence in mapping['review']['evidence_refs']:
                if evidence not in registered_sources:
                    raise DictionaryError('missing KS evidence in accepted mapping')
        if mapping['status']=='accepted' and mapping['relation']=='exactMatch':
            key_l=(local['namespace_id'],local['id'])
            key_e=(local['namespace_id'],ext['system'],ext['id'])
            if key_l in approved_local or key_e in approved_external:
                raise DictionaryError('duplicate accepted exactMatch mapping')
            approved_local.add(key_l);approved_external.add(key_e)
    return {'registered_identity_count':len(ids),'accepted_exact_matches':len(approved_local)}


def preflight(*, catalog:Path, registry:Path, crosswalk:Path, graph:Path|None=None,
              locales:list[str]|None=None, kit_import_candidate:bool=False) ->dict:
    catalog,registry,crosswalk=[Path(p).resolve() for p in (catalog,registry,crosswalk)]
    content=read_json(catalog)
    check_schema(content,'kristal-dictionary-catalog.schema.json')
    r=read_json(registry); c=read_json(crosswalk)
    identity=_check_identity(content,r,c)
    dictionary_audit=audit(catalog,crosswalk,registry)
    # Published diK import-large catalog is only imported, verified Wikidata
    # layers; reviewed curated/external layers are managed separately by Kit.
    if kit_import_candidate:
        if any(layer['kind']!='wikidata' for language in content['languages'] for layer in language['layers']):
            raise DictionaryError('Kit import candidate cannot contain curated/external layers')
    # Independent derived readout; no import-side decisions or adoption.
    report={'profile':PROFILE,'status':'preflight_pass',
            'framework_baseline':'11.0.0-draft.3-contracts',
            'namespace_id':content['namespace_id'], 'catalog_id':content['catalog_id'],
            'input_sha256':{'catalog':sha256(catalog),'registry':sha256(registry),'crosswalk':sha256(crosswalk)},
            'identity_checks':identity,
            'dictionary':{'locales':dictionary_audit['locales'],
                'records_by_locale':dictionary_audit['records_by_locale'],
                'layer_count':sum(len(lang['layers']) for lang in content['languages'])},
            'kit_import_candidate':kit_import_candidate,
            'canonical_graph_modified':False,'catalog_activated':False,
            'scope':'Local Framework preflight only; not a Kit registration, approval, signature or full diK release qualification.'}
    if graph:
        graph=Path(graph).resolve()
        # Actual graph structure and references are checked by coverage tool.
        query_locales=locales if locales else [x['tag'] for x in content['languages']][:10]
        if not query_locales: raise DictionaryError('no locale selected for coverage')
        coverage=make_report(graph_path=graph,catalog_path=catalog,registry_path=registry,
                             crosswalk_path=crosswalk,locales=query_locales)
        check_schema(coverage,'kristal-dik-coverage-report.schema.json')
        validate_counts(coverage)
        report['graph']={'sha256':sha256(graph),'graph_id':coverage['graph_id'],
            'semantic_reference_count':coverage['semantic_reference_count'],
            'coverage_by_locale':[{ 'locale':row['tag'],
                'KQ':{k:row['KQ'][k] for k in ('total','direct','fallback','missing','conflicted')},
                'KP':{k:row['KP'][k] for k in ('total','direct','fallback','missing','conflicted')}}
                for row in coverage['locales']]}
    elif locales:
        raise DictionaryError('--locales requires --graph')
    return report


def _write_new(path:Path,payload:str):
    path.parent.mkdir(parents=True,exist_ok=True)
    # x prevents overwriting existing reports; output is derived only.
    with path.open('x',encoding='utf-8') as f:
        f.write(payload); f.flush();os.fsync(f.fileno())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',type=Path,required=True)
    parser.add_argument('--registry',type=Path,required=True)
    parser.add_argument('--crosswalk',type=Path,required=True)
    parser.add_argument('--graph',type=Path)
    parser.add_argument('--locales',help='comma-separated explicitly requested locales, requires --graph')
    parser.add_argument('--kit-import-candidate',action='store_true',help='require only Wikidata incoming layers')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        result=preflight(catalog=args.catalog,registry=args.registry,crosswalk=args.crosswalk,
            graph=args.graph,locales=args.locales.split(',') if args.locales else None,
            kit_import_candidate=args.kit_import_candidate)
        payload=_canonical_json(result)
        if args.output:
            _write_new(args.output,payload)
        print(payload,end='')
    except (DictionaryError,OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        raise SystemExit(f'v11 diK/Kit interop preflight REFUSED: {exc}') from exc

if __name__=='__main__':main()
