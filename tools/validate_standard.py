#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
V8_SCHEMA_ROOT = ROOT / 'schemas' / 'v8'
V8_VECTORS = ROOT / 'tck' / 'v8' / 'vectors'
V8_EXAMPLES = ROOT / 'examples' / 'v8'
V7_SCHEMA_ROOT = ROOT / 'schemas' / 'v7'
V7_VECTORS = ROOT / 'tck' / 'v7' / 'vectors'
V7_EXAMPLES = ROOT / 'examples' / 'v7'
V6_SCHEMA = ROOT / 'schemas' / 'v6' / 'kristal-state.schema.json'
V6_VECTORS = ROOT / 'tck' / 'v6' / 'vectors'
V6_EXAMPLES = ROOT / 'examples' / 'v6'

EXPECTED_V7_SCHEMAS = {
    'kristal-v7-extension.schema.json',
    'kristall-assertion-family-registry.schema.json',
    'kristall-assertion-registry.schema.json',
    'kristall-axis-registry.schema.json',
    'kristall-axis-type-registry.schema.json',
    'kristall-crystallization-record.schema.json',
    'kristall-entity-registry.schema.json',
    'kristall-kos-registry.schema.json',
    'kristall-manifest.schema.json',
    'kristall-mesh.schema.json',
    'kristall-projection-recipe.schema.json',
    'kristall-property-registry.schema.json',
    'kristall-source-registry.schema.json',
    'kristall-toc-registry.schema.json',
    'semantic-resonance.schema.json',
}
EXPECTED_V8_SCHEMAS = {
    'kristall-ai-context-bundle.schema.json',
    'kristall-lexicon-stack.schema.json',
    'kristall-lexicon.schema.json',
    'kristall-query-index.schema.json',
    'kristall-query-request.schema.json',
    'kristall-query-result.schema.json',
    'kristall-v8-capabilities.schema.json',
}

V7_PAIRINGS = {
    'kristall-manifest.example.json': 'kristall-manifest.schema.json',
    'entity-registry.example.json': 'kristall-entity-registry.schema.json',
    'property-registry.example.json': 'kristall-property-registry.schema.json',
    'assertion-registry.example.json': 'kristall-assertion-registry.schema.json',
    'source-registry.example.json': 'kristall-source-registry.schema.json',
    'assertion-family-registry.example.json': 'kristall-assertion-family-registry.schema.json',
    'axis-registry.example.json': 'kristall-axis-registry.schema.json',
    'axis-type-registry.example.json': 'kristall-axis-type-registry.schema.json',
    'mesh.example.json': 'kristall-mesh.schema.json',
    'projection-recipe.example.json': 'kristall-projection-recipe.schema.json',
    'crystallization-record.example.json': 'kristall-crystallization-record.schema.json',
    'resonance.example.json': 'semantic-resonance.schema.json',
    'kos-registry.example.json': 'kristall-kos-registry.schema.json',
    'toc-registry-100-seed.example.json': 'kristall-toc-registry.schema.json',
}
V8_PAIRINGS = {
    'v8-capabilities.example.json': 'kristall-v8-capabilities.schema.json',
    'lexicon-fr-core.example.json': 'kristall-lexicon.schema.json',
    'lexicon-fr-chemistry.example.json': 'kristall-lexicon.schema.json',
    'lexicon-stack.example.json': 'kristall-lexicon-stack.schema.json',
    'query-index.example.json': 'kristall-query-index.schema.json',
    'query-request.example.json': 'kristall-query-request.schema.json',
    'query-result.example.json': 'kristall-query-result.schema.json',
    'ai-context-bundle.example.json': 'kristall-ai-context-bundle.schema.json',
}


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate(instance, schema, label: str):
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda e: list(e.absolute_path),
    )
    if errors:
        err = errors[0]
        where = '/' + '/'.join(map(str, err.absolute_path))
        raise AssertionError(f'{label}: {err.message} @ {where}')


def check_layout():
    for ver in ('v8', 'v7', 'v6'):
        if (ROOT / f'spec/{ver}/02-schemas').exists() or (ROOT / f'spec/{ver}/09-test-vectors').exists():
            raise AssertionError(f'active {ver} machine contracts must not be duplicated under spec/{ver}')
    if (ROOT / 'VERSION').read_text(encoding='utf-8').strip() != '8.0.0':
        raise AssertionError('unexpected active VERSION')


def check_schemas():
    actual7 = {p.name for p in V7_SCHEMA_ROOT.glob('*.schema.json')}
    if actual7 != EXPECTED_V7_SCHEMAS:
        raise AssertionError(f'v7 schema set drift: {sorted(actual7 ^ EXPECTED_V7_SCHEMAS)}')
    actual8 = {p.name for p in V8_SCHEMA_ROOT.glob('*.schema.json')}
    if actual8 != EXPECTED_V8_SCHEMAS:
        raise AssertionError(f'v8 schema set drift: {sorted(actual8 ^ EXPECTED_V8_SCHEMAS)}')
    for root in (V7_SCHEMA_ROOT, V8_SCHEMA_ROOT):
        for p in sorted(root.glob('*.schema.json')):
            Draft202012Validator.check_schema(load(p))
    Draft202012Validator.check_schema(load(V6_SCHEMA))


def check_examples_and_vectors(pairings, schema_root, examples_root, vectors_root, label):
    for ex, schema_name in pairings.items():
        schema = load(schema_root / schema_name)
        validate(load(examples_root / ex), schema, f'{label} example {ex}')
        validate(load(vectors_root / ex), schema, f'{label} vector {ex}')
        if (examples_root / ex).read_bytes() != (vectors_root / ex).read_bytes():
            raise AssertionError(f'{label} example/vector mirror drift: {ex}')


def check_v7_examples_and_vectors():
    check_examples_and_vectors(V7_PAIRINGS, V7_SCHEMA_ROOT, V7_EXAMPLES, V7_VECTORS, 'v7')
    projection = load(V7_VECTORS / 'v6-compatible-projection.example.json')
    validate(projection, load(V6_SCHEMA), 'v6-compatible projection')
    validate(projection['extensions']['kristal_v7'], load(V7_SCHEMA_ROOT/'kristal-v7-extension.schema.json'), 'v7 extension')


def check_v8_examples_and_vectors():
    check_examples_and_vectors(V8_PAIRINGS, V8_SCHEMA_ROOT, V8_EXAMPLES, V8_VECTORS, 'v8')


def check_v6_portable_contract():
    vec = V6_VECTORS / 'kristal-state' / 'kristal-state.example.json'
    ex = V6_EXAMPLES / 'kristal-state.example.json'
    validate(load(vec), load(V6_SCHEMA), 'v6 TCK example')
    validate(load(ex), load(V6_SCHEMA), 'v6 example')
    if vec.read_bytes() != ex.read_bytes():
        raise AssertionError('v6 example/vector drift')


def check_v7_invariants():
    toc = load(V7_VECTORS/'toc-registry-100-seed.example.json')
    if len(toc['subjects']) != 100 or len(toc['categories']) != 95:
        raise AssertionError('draft.3 TOC count invariant failed')
    if not all(1 <= len(x['preferred_axis_type_ids']) <= 2 for x in toc['subjects']):
        raise AssertionError('subject preferred axis type invariant failed')
    if not all(1 <= len(x['category_placements']) <= 2 for x in toc['subjects']):
        raise AssertionError('subject category placement invariant failed')
    axis_types = load(V7_VECTORS/'axis-type-registry.example.json')
    if len(axis_types['axis_types']) != 18:
        raise AssertionError('expected 18 native axis types')
    unesco = load(ROOT/'spec/v7/reference-kos/unesco-thesaurus-profile.json')
    if unesco['counts'].get('domains') != 7 or unesco['counts'].get('microthesauri') != 88:
        raise AssertionError('UNESCO 7/88 baseline drift')


def check_v8_invariants():
    invariants=(ROOT/'spec/v8/Core-Invariants.md').read_text(encoding='utf-8')
    for token in (
        'SEMANTICS != LANGUAGE', 'LEXICON != SEMANTIC AUTHORITY',
        'MISSING LEXICALIZATION != MISSING MEANING', 'QUERY INDEX != SOURCE OF TRUTH',
        'FUZZY DISCOVERY != SEMANTIC ANSWER', 'AI CONTEXT != CANONICAL STATE',
        'OMISSION BY BUDGET != NEGATION', 'PARTIAL RESULT != NEGATIVE RESULT', 'MODEL OUTPUT != AUTHORITY', 'SCHEMA VALID != SEMANTICALLY VALID', 'SEMANTIC FINGERPRINT != BYTE HASH', 'EXTENSION != CANONICAL MUTATION'):
        if token not in invariants:
            raise AssertionError(f'missing v8 invariant: {token}')
    conformance=(ROOT/'spec/v8/Conformance.md').read_text(encoding='utf-8')
    for profile in ('V8-Reader','V8-Language','V8-Query','V8-Federation','V8-AI-Context','V8-Integrity','V8-Full'):
        if profile not in conformance:
            raise AssertionError(f'missing v8 conformance profile: {profile}')


def check_compatibility_lock():
    lock=load(ROOT/'contracts/v8-compatibility-lock.json')
    for e in lock['files']:
        p=ROOT/e['path']; b=p.read_bytes(); h='sha256:'+hashlib.sha256(b).hexdigest()
        if h != e['sha256'] or len(b) != e['bytes']:
            raise AssertionError(f'v8 changed frozen v6/v7 compatibility surface: {e["path"]}')


def check_language_reference_tools():
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'delta.json'
        subprocess.run([
            sys.executable, str(ROOT/'tools/v8/build_lexicon_delta.py'),
            str(ROOT/'examples/v7/entity-registry.example.json'),
            '--language','fr','--lexicon-id','KL-test-fr',
            '--existing',str(ROOT/'examples/v8/lexicon-fr-core.example.json'),
            '--output',str(out)
        ], check=True, capture_output=True, text=True)
        doc=load(out)
        # KQ1001 is covered; KQ2001 and KQ2002 remain unresolved.
        ids={e['semantic_ref']['id'] for e in doc['entries']}
        if 'KQ1001' in ids or not {'KQ2001','KQ2002'}.issubset(ids):
            raise AssertionError(f'lexicon delta behavior unexpected: {sorted(ids)}')
        validate(doc, load(V8_SCHEMA_ROOT/'kristall-lexicon.schema.json'), 'generated lexicon delta')



def check_query_reference_tools():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        result=td/'result.json'; context=td/'context.json'
        subprocess.run([
            sys.executable, str(ROOT/'tools/v8/semantic_slice.py'),
            '--entities',str(ROOT/'examples/v7/entity-registry.example.json'),
            '--properties',str(ROOT/'examples/v7/property-registry.example.json'),
            '--assertions',str(ROOT/'examples/v7/assertion-registry.example.json'),
            '--sources',str(ROOT/'examples/v7/source-registry.example.json'),
            '--mesh',str(ROOT/'examples/v7/mesh.example.json'),
            '--root','KQ1001','--max-depth','2','--max-nodes','32','--output',str(result)
        ], check=True, capture_output=True, text=True)
        q=load(result)
        validate(q, load(V8_SCHEMA_ROOT/'kristall-query-result.schema.json'), 'generated semantic slice')
        if not any(n.get('id')=='KQ1001' for n in q['result']['nodes']):
            raise AssertionError('semantic slice lost exact root')
        subprocess.run([
            sys.executable, str(ROOT/'tools/v8/compile_ai_context.py'), str(result),
            '--max-tokens','128','--output',str(context)
        ], check=True, capture_output=True, text=True)
        c=load(context)
        validate(c, load(V8_SCHEMA_ROOT/'kristall-ai-context-bundle.schema.json'), 'generated AI context')
        if c['budget']['estimated_tokens'] > c['budget']['max_tokens']:
            raise AssertionError('AI context exceeded declared budget')

def check_active_version_text():
    version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    release = load(ROOT/'contracts/release.json')
    contract_set = load(ROOT/'contracts/contract-set.json')
    knowledge = load(ROOT/'contracts/knowledge-model-contract.v4.json')
    if not (release.get('version') == contract_set.get('version') == knowledge.get('release') == version):
        raise AssertionError('active release/version surfaces disagree')
    core = (ROOT/'spec/v8/01-core-spec/kristal-v8-core-spec.md').read_text(encoding='utf-8')
    if version not in core:
        raise AssertionError('v8 core spec not aligned to active VERSION')
    status = (ROOT/'spec/v8/00-overview/specification-status.md').read_text(encoding='utf-8')
    if version not in '\n'.join(status.splitlines()[:6]):
        raise AssertionError('active v8 specification status is stale')


def check_daat_boundary():
    doc = (ROOT/'spec/v7/DaaT-Boundary.md').read_text(encoding='utf-8')
    required = ('DaaT', '`daat`', 'kristal_state', '6.0', 'KQ', 'KP', 'KA', 'KS')
    for token in required:
        if token not in doc:
            raise AssertionError(f'missing DaaT boundary token: {token}')


def main():
    checks = [
        ('layout', check_layout),
        ('schemas', check_schemas),
        ('v8 examples/vectors', check_v8_examples_and_vectors),
        ('v7 examples/vectors', check_v7_examples_and_vectors),
        ('v6 portable contract', check_v6_portable_contract),
        ('v7 invariants', check_v7_invariants),
        ('v8 invariants', check_v8_invariants),
        ('v8 compatibility lock', check_compatibility_lock),
        ('v8 language helper', check_language_reference_tools),
        ('v8 query helpers', check_query_reference_tools),
        ('active version text', check_active_version_text),
        ('DaaT boundary', check_daat_boundary),
    ]
    for label, fn in checks:
        fn(); print(f'PASS: {label}')
    print('Kristal standard validation: PASS')

if __name__ == '__main__':
    main()
