#!/usr/bin/env python3
"""Read-only diK conversion-plan verification; never edits a source Kristal.

An 'approved' operation is documentation, NOT execution authorization.
Only a future migration producer can verify semantic field roles and new commitments.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from dictionaries import DictionaryError, check_schema, read_json, sha256


def json_pointer(document, pointer):
    current = document
    for raw_part in pointer.split('/')[1:]:
        part = raw_part.replace('~1', '/').replace('~0', '~')
        try:
            if isinstance(current, list):
                if not part.isdecimal() or (len(part) > 1 and part[0] == '0'):
                    raise LookupError('invalid JSON array index')
                current = current[int(part)]
            elif isinstance(current, dict):
                current = current[part]
            else:
                raise LookupError('path is not traversable')
        except (IndexError, KeyError, ValueError, LookupError) as exc:
            raise DictionaryError(f'unresolvable JSON pointer: {pointer}') from exc
    return current


def verify_plan(plan, *, registry, source_path=None, require_all_approved=False):
    check_schema(plan, 'kristal-dik-conversion-plan.schema.json')
    check_schema(registry, 'kristal-identity-registry.schema.json')
    if plan['namespace_id'] != registry['namespace_id']:
        raise DictionaryError('conversion plan namespace differs from identity registry')
    kinds = {item['id']: item['kind'] for item in registry['identities']}
    used_paths, used_ids = set(), set()
    status_counts = {'approved': 0, 'pending': 0, 'rejected': 0}
    source_document = None
    if source_path is not None:
        if sha256(source_path) != plan['source']['sha256']:
            raise DictionaryError('conversion plan source digest mismatch')
        source_document = read_json(source_path)
    for op in plan['operations']:
        ident, path = op['operation_id'], op['source_path']
        if ident in used_ids or path in used_paths:
            raise DictionaryError('duplicate operation ID or duplicate source path')
        used_ids.add(ident); used_paths.add(path)
        expected = op['semantic_role']
        if kinds.get(op['target_id']) != expected:
            raise DictionaryError(f'undeclared/wrong-kind conversion target: {op["target_id"]}')
        status = op['decision']['status']
        status_counts[status] += 1
        if status == 'approved':
            for ref in op['decision']['evidence_refs']:
                if kinds.get(ref) != 'source':
                    raise DictionaryError('approved conversion uses unknown KS evidence')
        if source_document is not None:
            found = json_pointer(source_document, path)
            if not isinstance(found, str) or found != op['original_value']:
                raise DictionaryError(f'original source value differs at {path}')
    if require_all_approved and (status_counts['pending'] or status_counts['rejected']):
        raise DictionaryError('unapproved operations in conversion plan')
    return {'plan_id': plan['plan_id'], 'operations': len(plan['operations']),
            'decisions': status_counts, 'source_digest_verified': source_path is not None,
            'status': 'structural_check_only_no_execution_permission'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--registry', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--require-all-approved', action='store_true')
    args = parser.parse_args()
    try:
        result=verify_plan(read_json(args.plan), registry=read_json(args.registry),
            source_path=args.source, require_all_approved=args.require_all_approved)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (DictionaryError, OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f'diK conversion plan invalid: {exc}')


if __name__ == '__main__':
    main()
