#!/usr/bin/env python3
"""Kristal Framework v11 draft.3 offline schema and semantic checks.

Read-only. Distinct historical v6-v10 artifacts are not rewritten here.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / 'schemas' / 'v11'
EXAMPLES = ROOT / 'examples' / 'v11'
PAIRS = {
 'identity-registry.example.json': 'kristal-identity-registry.schema.json',
 'semantic-graph.example.json': 'kristal-semantic-graph.schema.json',
 'external-crosswalk.example.json': 'kristal-external-crosswalk.schema.json',
 'lexicon-fr.example.json': 'kristal-lexical-dictionary.schema.json',
 'lexicon-en.example.json': 'kristal-lexical-dictionary.schema.json',
 'legacy-resolution-requests.example.json': 'kristal-legacy-resolution-requests.schema.json',
}

class IntegrityError(ValueError):
    pass

def read(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding='utf-8'))

def validate_schema(data: dict, name: str) -> None:
    schema = read(SCHEMAS / name)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: str(e.absolute_path))
    if errors:
        issue = errors[0]
        raise IntegrityError(f"{name}: {issue.json_path}: {issue.message}")

def _unique(values, label):
    if len(values) != len(set(values)):
        raise IntegrityError(f'duplicate {label}')

def validate_documents(*, registry: dict, graph: dict, crosswalk: dict, lexicons: list[dict], requests: dict|None=None) -> None:
    validate_schema(registry, 'kristal-identity-registry.schema.json')
    validate_schema(graph, 'kristal-semantic-graph.schema.json')
    validate_schema(crosswalk, 'kristal-external-crosswalk.schema.json')
    for lex in lexicons:
        validate_schema(lex, 'kristal-lexical-dictionary.schema.json')
    if requests is not None:
        validate_schema(requests, 'kristal-legacy-resolution-requests.schema.json')
        _unique([v['request_id'] for v in requests['requests']], 'resolution request IDs')
    ns = registry['namespace_id']
    if graph['namespace_id'] != ns:
        raise IntegrityError('graph and registry namespaces differ')
    reg: dict[str,str] = {}
    for r in registry['identities']:
        if r['id'] in reg:
            raise IntegrityError('duplicate registry identity')
        reg[r['id']] = r['kind']
    def check(identity, kind, where):
        if reg.get(identity) != kind:
            raise IntegrityError(f'{where}: {identity} is not a declared {kind}')
    for key, kind in [('entities','entity'),('properties','property'),('sources','source')]:
        for ref in graph[key]:
            check(ref,kind,f'graph.{key}')
    def object_check(o, where):
        if o['kind'] == 'entity':
            check(o['id'],'entity',where)
            if o['id'] not in graph['entities']:
                raise IntegrityError(f'{where}: target not included in graph entity set')
    _unique([a['id'] for a in graph['assertions']], 'graph assertions')
    for a in graph['assertions']:
        check(a['id'],'assertion','graph.assertions')
        check(a['subject'],'entity','graph.subject')
        check(a['predicate'],'property','graph.predicate')
        if a['subject'] not in graph['entities'] or a['predicate'] not in graph['properties']:
            raise IntegrityError('graph assertion references entity/property outside the graph')
        object_check(a['object'],'graph.object')
        for source in a['sources']:
            check(source,'source','graph.sources')
            if source not in graph['sources']:
                raise IntegrityError('assertion source not in graph source set')
        for qualifier in a.get('qualifiers',[]):
            check(qualifier['predicate'],'property','graph.qualifier')
            if qualifier['predicate'] not in graph['properties']:
                raise IntegrityError('qualifier predicate not included in graph properties')
            object_check(qualifier['object'],'graph.qualifier_object')
    _unique([m['mapping_id'] for m in crosswalk['mappings']], 'mapping IDs')
    exact_locals: set[tuple[str,str]] = set()
    exact_externals: set[tuple[str,str,str]] = set()
    for m in crosswalk['mappings']:
        local=m['local_ref']; external=m['external_ref']
        # Framework-level validation here is for the supplied namespace registry.
        if local['namespace_id'] != ns:
            raise IntegrityError('crosswalk refers to namespace not supplied for validation')
        check(local['id'], 'entity' if local['id'].startswith('KQ') else 'property','crosswalk.local_ref')
        if m['status']=='accepted':
            for s in m['review']['evidence_refs']:
                check(s,'source','crosswalk.evidence')
        if m['status']=='accepted' and m['relation']=='exactMatch':
            l=(ns,local['id']); e=(ns,external['system'],external['id'])
            if l in exact_locals or e in exact_externals:
                raise IntegrityError('conflicting accepted exactMatch: more than one active mapping per side')
            exact_locals.add(l); exact_externals.add(e)
    for lex in lexicons:
        if lex['namespace_id'] != ns:
            raise IntegrityError('lexicon and registry namespaces differ')
        for entry in lex['entries']:
            check(entry['semantic_id'],'entity' if entry['semantic_id'].startswith('KQ') else 'property','lexicon.semantic_id')
            for domain in entry.get('domain_ids',[]):
                check(domain,'entity','lexicon.domain_id')
        _unique([e['semantic_id'] for e in lex['entries']], 'lexical dictionary entry IDs')

def fixture_documents():
    return {
      'registry':read(EXAMPLES/'identity-registry.example.json'),
      'graph':read(EXAMPLES/'semantic-graph.example.json'),
      'crosswalk':read(EXAMPLES/'external-crosswalk.example.json'),
      'lexicons':[read(EXAMPLES/'lexicon-fr.example.json'),read(EXAMPLES/'lexicon-en.example.json')],
      'requests':read(EXAMPLES/'legacy-resolution-requests.example.json'),
    }

def check_fixtures():
    for example,schema in PAIRS.items():
        data=read(EXAMPLES/example)
        vector=read(ROOT/'tck/v11/vectors'/example)
        if (EXAMPLES/example).read_bytes() != (ROOT/'tck/v11/vectors'/example).read_bytes():
            raise IntegrityError(f'v11 fixture mirror drift: {example}')
        validate_schema(data,schema)
        validate_schema(vector,schema)
    validate_documents(**fixture_documents())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry',type=Path)
    parser.add_argument('--graph',type=Path)
    parser.add_argument('--crosswalk',type=Path)
    parser.add_argument('--lexicon',type=Path,action='append')
    args=parser.parse_args()
    if any([args.registry,args.graph,args.crosswalk,args.lexicon]):
        if not all([args.registry,args.graph,args.crosswalk,args.lexicon]):
            parser.error('--registry, --graph, --crosswalk and at least one --lexicon are required together')
        validate_documents(registry=read(args.registry),graph=read(args.graph),crosswalk=read(args.crosswalk),lexicons=[read(p) for p in args.lexicon])
    else:
        check_fixtures()
    print('Kristal v11 draft.3 semantic profile: PASS (local fixture/integrity only)')

if __name__=='__main__':
    try: main()
    except (IntegrityError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f'Kristal v11 validation: FAIL: {exc}')
