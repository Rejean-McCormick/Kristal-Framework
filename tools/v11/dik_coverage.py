#!/usr/bin/env python3
"""diK coverage reference: versioned file-backed, read-only graph×locale report.

Batched per-layer lookup (not N identifiers * N file reads), exact and fallback
coverage separately. Does not download Wikidata or migrate Kristals.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from dictionaries import (DictionaryError, audit, check_schema,
                          layer_records, read_json, safe_file, sha256)


def _references(graph, registry):
    check_schema(graph, 'kristal-semantic-graph.schema.json')
    check_schema(registry, 'kristal-identity-registry.schema.json')
    if graph['namespace_id'] != registry['namespace_id']:
        raise DictionaryError('graph/registry namespace mismatch')
    registered = {entry['id']: entry['kind'] for entry in registry['identities']}
    def check(kid, kind):
        if registered.get(kid) != kind:
            raise DictionaryError(f'unregistered {kind}: {kid}')
    entities, properties = set(graph['entities']), set(graph['properties'])
    for eid in entities:
        check(eid, 'entity')
    for pid in properties:
        check(pid, 'property')
    for sid in graph['sources']:
        check(sid, 'source')
    for stmt in graph['assertions']:
        check(stmt['id'], 'assertion')
        if stmt['subject'] not in entities or stmt['predicate'] not in properties:
            raise DictionaryError('graph assertion outside declared semantic reference sets')
        for sid in stmt['sources']:
            if sid not in graph['sources']:
                raise DictionaryError('graph assertion source missing from source set')
        def entity_object(obj):
            if obj['kind'] == 'entity' and obj['id'] not in entities:
                raise DictionaryError('graph assertion entity object missing from entity set')
        entity_object(stmt['object'])
        for q in stmt.get('qualifiers', []):
            if q['predicate'] not in properties:
                raise DictionaryError('graph qualifier predicate missing from property set')
            entity_object(q['object'])
    return {'KQ': entities, 'KP': properties}


def _index_locale(catalog_dir, entry, needed):
    """One pass per layer. Audit's prior check eliminates equal-priority conflicts."""
    index = {}
    for layer in entry['layers']:
        path = safe_file(catalog_dir, layer['path'])
        for item, _ in layer_records(path, layer['kind']):
            kid = item['semantic_id']
            if kid not in needed:
                continue
            current = index.get(kid)
            candidate = (layer['priority'], item['preferred_term'])
            if current is None or current[0] < candidate[0]:
                index[kid] = candidate
            elif current[0] == candidate[0] and current[1] != candidate[1]:
                raise DictionaryError(f'conflicting labels for {entry["tag"]}/{kid}')
    return set(index)


def make_report(*, graph_path, catalog_path, registry_path, crosswalk_path,
                locales=None, missing_sample_limit=25):
    if missing_sample_limit < 0:
        raise DictionaryError('negative sample size')
    audit(catalog_path, crosswalk_path, registry_path)
    graph = read_json(graph_path)
    registry = read_json(registry_path)
    catalog = read_json(catalog_path)
    if graph['namespace_id'] != catalog['namespace_id']:
        raise DictionaryError('graph/catalog namespace mismatch')
    refs = _references(graph, registry)
    languages = {entry['tag']: entry for entry in catalog['languages']}
    selected = list(locales if locales is not None else languages)
    if not selected or len(set(selected)) != len(selected):
        raise DictionaryError('locales must be nonempty and unique')
    unknown = sorted(set(selected) - set(languages))
    if unknown:
        raise DictionaryError('undeclared catalog locales: ' + ', '.join(unknown))
    needed = refs['KQ'] | refs['KP']
    # Only load the required locales and their expressly declared fallback locales.
    used = set(selected)
    for tag in selected:
        used.update(languages[tag]['fallbacks'])
    root = Path(catalog_path).resolve().parent
    direct_by_locale = {tag: _index_locale(root, languages[tag], needed) for tag in sorted(used)}
    rows = []
    across_direct = {'KQ': set(refs['KQ']), 'KP': set(refs['KP'])}
    across_usable = {'KQ': set(refs['KQ']), 'KP': set(refs['KP'])}
    for tag in selected:
        direct = direct_by_locale[tag]
        effective = set(direct)
        for fallback_tag in languages[tag]['fallbacks']:
            effective.update(direct_by_locale[fallback_tag])
        counts = {}
        for kind in ('KQ', 'KP'):
            all_ids = refs[kind]
            d = all_ids & direct
            f = (all_ids & effective) - d
            m = all_ids - effective
            across_direct[kind].intersection_update(d)
            across_usable[kind].intersection_update(d | f)
            missing = sorted(m)
            counts[kind] = {
                'total': len(all_ids),
                'direct': len(d),
                'fallback': len(f),
                'missing': len(m),
                'conflicted': 0,  # Unresolved source-level conflicts fail the catalog audit.
                'missing_ids_sample': missing[:missing_sample_limit],
                'sample_truncated': len(missing) > missing_sample_limit,
            }
        rows.append({
            'tag': tag, **counts,
            'complete_direct': all(counts[k]['direct'] == counts[k]['total'] for k in ('KQ','KP')),
            'complete_usable': all(counts[k]['missing'] == 0 for k in ('KQ','KP')),
        })
    source_hash = sha256(graph_path)
    cat_hash = sha256(catalog_path)
    report_seed = json.dumps([graph['graph_id'], source_hash, cat_hash, selected], ensure_ascii=False, separators=(',',':'))
    report_id = 'dik-coverage-' + hashlib.sha256(report_seed.encode('utf-8')).hexdigest()[:20]
    report = {
        'schema_version': '11.0',
        'artifact_type': 'kristal_dik_coverage_report',
        'report_id': report_id,
        'namespace_id': graph['namespace_id'],
        'graph_id': graph['graph_id'], 'graph_sha256': source_hash,
        'catalog_id': catalog['catalog_id'], 'catalog_sha256': cat_hash,
        'semantic_reference_count': {k:len(refs[k]) for k in ('KQ','KP')},
        'locales': rows,
        'all_locales': {
            'direct': {k:len(across_direct[k]) for k in ('KQ','KP')},
            'usable': {k:len(across_usable[k]) for k in ('KQ','KP')},
        }
    }
    check_schema(report, 'kristal-dik-coverage-report.schema.json')
    validate_counts(report)
    return report


def validate_counts(report):
    """Cross-field constraints not expressible simply with portable JSON Schema."""
    seen = set()
    totals = report['semantic_reference_count']
    for row in report['locales']:
        if row['tag'] in seen:
            raise DictionaryError('duplicate locale in coverage report')
        seen.add(row['tag'])
        for kind in ('KQ', 'KP'):
            item = row[kind]
            if item['total'] != totals[kind]:
                raise DictionaryError('coverage denominator differs from graph')
            if sum(item[k] for k in ('direct','fallback','missing','conflicted')) != item['total']:
                raise DictionaryError('coverage categories do not add up')
            if len(item['missing_ids_sample']) > item['missing']:
                raise DictionaryError('missing sample larger than missing count')
            if len(item['missing_ids_sample']) < item['missing'] and not item['sample_truncated']:
                raise DictionaryError('undisclosed truncated missing sample')
            if (not item['sample_truncated']) and len(item['missing_ids_sample']) != item['missing']:
                raise DictionaryError('untruncated missing sample count mismatch')
            if any(not kid.startswith(kind) for kid in item['missing_ids_sample']):
                raise DictionaryError('wrong identity family in missing IDs')
        if row['complete_direct'] != all(row[k]['direct']==row[k]['total'] for k in ('KQ','KP')):
            raise DictionaryError('incorrect direct completeness flag')
        if row['complete_usable'] != all(row[k]['missing']==0 and row[k]['conflicted']==0 for k in ('KQ','KP')):
            raise DictionaryError('incorrect usable completeness flag')
    for typ in ('direct','usable'):
        for kind in ('KQ','KP'):
            if report['all_locales'][typ][kind] > totals[kind]:
                raise DictionaryError('all-language coverage exceeds graph total')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('graph','catalog','registry','crosswalk'):
        parser.add_argument('--'+arg, type=Path, required=True)
    parser.add_argument('--locales', help='Comma-separated catalog locale tags; defaults to all declared locales')
    parser.add_argument('--missing-sample-limit', type=int, default=25)
    parser.add_argument('--output', type=Path, help='Report file (omit for stdout)')
    args = parser.parse_args()
    try:
        result = make_report(graph_path=args.graph, catalog_path=args.catalog,
            registry_path=args.registry, crosswalk_path=args.crosswalk,
            locales=args.locales.split(',') if args.locales else None,
            missing_sample_limit=args.missing_sample_limit)
        serialized = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized, encoding='utf-8')
            print(f'diK coverage report: {args.output}')
        else:
            print(serialized, end='')
    except (DictionaryError, OSError, ValueError, json.JSONDecodeError) as e:
        raise SystemExit(f'diK coverage failed: {e}')


if __name__ == '__main__':
    main()
