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
V10_SCHEMA_ROOT = ROOT / 'schemas' / 'v10'
V10_VECTORS = ROOT / 'tck' / 'v10' / 'vectors'
V10_EXAMPLES = ROOT / 'examples' / 'v10'
GITHUB_PROFILE_SCHEMA = ROOT / 'profiles' / 'github' / 'schemas' / 'kristal-github-binding.schema.json'
GITHUB_READ_SURFACE_SCHEMA = ROOT / 'profiles' / 'github' / 'schemas' / 'kristal-github-read-surface.schema.json'
GITHUB_SYNC_MANIFEST_SCHEMA = ROOT / 'profiles' / 'github' / 'schemas' / 'kristal-github-sync-manifest.schema.json'
GITHUB_COLLECTION_INDEX_SCHEMA = ROOT / 'profiles' / 'github' / 'schemas' / 'kristal-github-collection-index.schema.json'
V9_SCHEMA_ROOT = ROOT / 'schemas' / 'v9'
V9_VECTORS = ROOT / 'tck' / 'v9' / 'vectors'
V9_EXAMPLES = ROOT / 'examples' / 'v9'
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
EXPECTED_V10_SCHEMAS = {
    'kristal-node-manifest.schema.json',
    'kristal-host-binding.schema.json',
    'kristal-publication.schema.json',
    'kristal-directory.schema.json',
    'kristal-v10-capabilities.schema.json',
}

EXPECTED_V9_SCHEMAS = {
    'kristal-activation.schema.json',
    'kristal-derivation.schema.json',
    'kristal-exchange.schema.json',
    'kristal-logical-artifact.schema.json',
    'kristal-materialization-manifest.schema.json',
    'kristal-state-snapshot.schema.json',
    'kristal-v9-capabilities.schema.json',
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
V9_PAIRINGS = {
    'logical-artifact.example.json': 'kristal-logical-artifact.schema.json',
    'state-snapshot.example.json': 'kristal-state-snapshot.schema.json',
    'derivation.example.json': 'kristal-derivation.schema.json',
    'materialization-manifest.example.json': 'kristal-materialization-manifest.schema.json',
    'exchange.example.json': 'kristal-exchange.schema.json',
    'activation.example.json': 'kristal-activation.schema.json',
    'v9-capabilities.example.json': 'kristal-v9-capabilities.schema.json',
}

V10_PAIRINGS = {
    'node-manifest.example.json': 'kristal-node-manifest.schema.json',
    'publication.example.json': 'kristal-publication.schema.json',
    'directory.example.json': 'kristal-directory.schema.json',
    'v10-capabilities.example.json': 'kristal-v10-capabilities.schema.json',
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
    for ver in ('v10', 'v9', 'v8', 'v7', 'v6'):
        if (ROOT / f'spec/{ver}/02-schemas').exists() or (ROOT / f'spec/{ver}/09-test-vectors').exists():
            raise AssertionError(f'active {ver} machine contracts must not be duplicated under spec/{ver}')
    if (ROOT / 'VERSION').read_text(encoding='utf-8').strip() != '10.0.0-draft.3.1':
        raise AssertionError('unexpected active VERSION')


def check_schemas():
    actual7 = {p.name for p in V7_SCHEMA_ROOT.glob('*.schema.json')}
    if actual7 != EXPECTED_V7_SCHEMAS:
        raise AssertionError(f'v7 schema set drift: {sorted(actual7 ^ EXPECTED_V7_SCHEMAS)}')
    actual8 = {p.name for p in V8_SCHEMA_ROOT.glob('*.schema.json')}
    if actual8 != EXPECTED_V8_SCHEMAS:
        raise AssertionError(f'v8 schema set drift: {sorted(actual8 ^ EXPECTED_V8_SCHEMAS)}')
    actual9 = {p.name for p in V9_SCHEMA_ROOT.glob('*.schema.json')}
    if actual9 != EXPECTED_V9_SCHEMAS:
        raise AssertionError(f'v9 schema set drift: {sorted(actual9 ^ EXPECTED_V9_SCHEMAS)}')
    actual10 = {p.name for p in V10_SCHEMA_ROOT.glob('*.schema.json')}
    if actual10 != EXPECTED_V10_SCHEMAS:
        raise AssertionError(f'v10 schema set drift: {sorted(actual10 ^ EXPECTED_V10_SCHEMAS)}')
    for root in (V7_SCHEMA_ROOT, V8_SCHEMA_ROOT, V9_SCHEMA_ROOT, V10_SCHEMA_ROOT):
        for p in sorted(root.glob('*.schema.json')):
            Draft202012Validator.check_schema(load(p))
    Draft202012Validator.check_schema(load(V6_SCHEMA))
    Draft202012Validator.check_schema(load(GITHUB_PROFILE_SCHEMA))


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
    proc=subprocess.run(['node',str(ROOT/'reference/js/bin/kristal-ref.mjs'),'state-id',str(V7_VECTORS/'v6-compatible-projection.example.json')],check=True,capture_output=True,text=True,cwd=ROOT/'reference/js')
    identity=json.loads(proc.stdout)
    if projection.get('state_id') != identity.get('state_id') or projection.get('content_hash',{}).get('value') != identity.get('sha256_hex'):
        raise AssertionError('v7 v6-compatible projection declared identity does not match unchanged v6 canonicalization')


def check_v9_examples_and_vectors():
    check_examples_and_vectors(V9_PAIRINGS, V9_SCHEMA_ROOT, V9_EXAMPLES, V9_VECTORS, 'v9')

def check_v10_examples_and_vectors():
    check_examples_and_vectors(V10_PAIRINGS, V10_SCHEMA_ROOT, V10_EXAMPLES, V10_VECTORS, 'v10')
    generic = load(V10_SCHEMA_ROOT/'kristal-host-binding.schema.json')
    validate(load(V10_EXAMPLES/'github-binding.example.json'), generic, 'v10 generic host binding example')
    validate(load(V10_VECTORS/'github-binding.example.json'), generic, 'v10 generic host binding vector')
    validate(load(V10_EXAMPLES/'github-binding.example.json'), load(GITHUB_PROFILE_SCHEMA), 'v10 GitHub host profile example')


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


def _compatibility_errata_by_path():
    doc=load(ROOT/'contracts/compatibility-errata.json')
    if doc.get('format') != 'kristal.compatibility-errata/v1':
        raise AssertionError('unexpected compatibility errata format')
    if doc.get('release') != '10.0.0-draft.3.1':
        raise AssertionError('compatibility errata release mismatch')
    out={}
    for e in doc.get('entries',[]):
        path=e.get('path')
        if not path or path in out:
            raise AssertionError('invalid or duplicate compatibility errata path')
        out[path]=e
    return out

def _verify_locked_or_erratum(entry, *, label):
    p=ROOT/entry['path']; b=p.read_bytes(); h='sha256:'+hashlib.sha256(b).hexdigest()
    if h == entry['sha256'] and len(b) == entry['bytes']:
        return
    err=_compatibility_errata_by_path().get(entry['path'])
    if not err:
        raise AssertionError(f'{label}: {entry["path"]}')
    if err.get('locked_sha256') != entry['sha256'] or err.get('locked_bytes') != entry['bytes']:
        raise AssertionError(f'errata does not bind historical lock: {entry["path"]}')
    if h != err.get('corrected_sha256') or len(b) != err.get('corrected_bytes'):
        raise AssertionError(f'corrected compatibility fixture drift: {entry["path"]}')
    mirror=err.get('mirror')
    if mirror and (ROOT/mirror).read_bytes() != b:
        raise AssertionError(f'compatibility errata mirror drift: {mirror}')

def check_compatibility_errata():
    entries=_compatibility_errata_by_path()
    if set(entries) != {'tck/v7/vectors/v6-compatible-projection.example.json'}:
        raise AssertionError('unexpected compatibility errata set')
    e=entries['tck/v7/vectors/v6-compatible-projection.example.json']
    projection=load(ROOT/e['path'])
    proc=subprocess.run(['node',str(ROOT/'reference/js/bin/kristal-ref.mjs'),'state-id',str(ROOT/e['path'])],check=True,capture_output=True,text=True,cwd=ROOT/'reference/js')
    identity=json.loads(proc.stdout)
    if projection.get('state_id') != identity.get('state_id'):
        raise AssertionError('corrected v7 portable projection state_id mismatch')
    if projection.get('content_hash',{}).get('value') != identity.get('sha256_hex'):
        raise AssertionError('corrected v7 portable projection content_hash mismatch')
    if identity.get('state_id') != e.get('declared_identity_after'):
        raise AssertionError('compatibility errata declared_identity_after mismatch')

def check_v8_compatibility_lock():
    lock=load(ROOT/'contracts/v8-compatibility-lock.json')
    for e in lock['files']:
        _verify_locked_or_erratum(e, label='v8 changed frozen v6/v7 compatibility surface')


def check_v9_compatibility_lock():
    lock=load(ROOT/'contracts/v9-compatibility-lock.json')
    if lock.get('release') != '9.0.0-draft.1':
        raise AssertionError('v9 compatibility lock release mismatch')
    for e in lock['files']:
        _verify_locked_or_erratum(e, label='v9 changed frozen v6/v7/v8 compatibility surface')


def check_v10_compatibility_lock():
    lock=load(ROOT/'contracts/v10-compatibility-lock.json')
    if lock.get('release') != '10.0.0-draft.1':
        raise AssertionError('v10 compatibility lock release mismatch')
    for e in lock['files']:
        p=ROOT/e['path']; b=p.read_bytes(); h='sha256:'+hashlib.sha256(b).hexdigest()
        if h != e['sha256'] or len(b) != e['bytes']:
            raise AssertionError(f'v10 changed frozen v9 compatibility surface: {e["path"]}')


def check_v10_invariants():
    invariants=(ROOT/'spec/v10/Core-Invariants.md').read_text(encoding='utf-8')
    for token in (
        'HOST LOCATION != SEMANTIC IDENTITY','REPOSITORY != KRISTAL NODE',
        'HOST BINDING != LOGICAL STATE','PUBLICATION RECORD != LOGICAL STATE',
        'DIRECTORY != AUTHORITY','DISCOVERY != FEDERATION MEMBERSHIP',
        'HOST ATTESTATION != EPISTEMIC AUTHORITY','AUTOMATION != AUTHORITY',
        'MIRROR != LOGICAL REVISION'):
        if token not in invariants: raise AssertionError(f'missing v10 invariant: {token}')
    conformance=(ROOT/'spec/v10/Conformance.md').read_text(encoding='utf-8')
    for profile in ('V10-Node-Reader','V10-Publisher','V10-Directory','V10-GitHub-Host','V10-Full'):
        if profile not in conformance: raise AssertionError(f'missing v10 conformance profile: {profile}')
    caps=load(V10_EXAMPLES/'v10-capabilities.example.json')
    if caps['compatibility']['semantic_state_baseline'] != 'kristal.state/9.0':
        raise AssertionError('v10 must preserve v9 semantic-state baseline')



def check_github_read_surface_profile():
    pairs = [
        (GITHUB_READ_SURFACE_SCHEMA, ROOT/'profiles/github/examples/github-read-surface.example.json'),
        (GITHUB_SYNC_MANIFEST_SCHEMA, ROOT/'profiles/github/examples/github-sync-manifest.example.json'),
        (GITHUB_COLLECTION_INDEX_SCHEMA, ROOT/'profiles/github/examples/github-collection-index.example.json'),
    ]
    for schema_path, example_path in pairs:
        schema = load(schema_path)
        Draft202012Validator.check_schema(schema)
        validate(load(example_path), schema, f'GitHub profile example {example_path.name}')
    profile=(ROOT/'spec/v10/GitHub-Reference-Profile.md').read_text(encoding='utf-8')
    for token in ('kristal.github-read-surface/1.0','kristal.github-sync-manifest/1.0','kristal.github-collection-index/1.0','READ SURFACE != SEMANTIC STATE','COLLECTION INDEX != AUTHORITY'):
        if token not in profile:
            raise AssertionError(f'missing GitHub read-surface profile token: {token}')

def check_v10_reference_tools():
    commands=[
        ('verify-node-v10','node-manifest.example.json'),
        ('verify-host-binding-v10','github-binding.example.json'),
        ('verify-github-binding-v10','github-binding.example.json'),
        ('verify-publication-v10','publication.example.json'),
        ('verify-directory-v10','directory.example.json'),
    ]
    for cmd,name in commands:
        proc=subprocess.run(['node',str(ROOT/'reference/js/bin/kristal-ref.mjs'),cmd,str(V10_VECTORS/name)],check=True,capture_output=True,text=True,cwd=ROOT/'reference/js')
        if not json.loads(proc.stdout)['ok']:
            raise AssertionError(f'v10 reference command failed: {cmd}')
    profile_commands=[
        ('verify-github-read-surface-v10', ROOT/'profiles/github/examples/github-read-surface.example.json'),
        ('verify-github-sync-manifest-v10', ROOT/'profiles/github/examples/github-sync-manifest.example.json'),
        ('verify-github-collection-index-v10', ROOT/'profiles/github/examples/github-collection-index.example.json'),
    ]
    for cmd,file in profile_commands:
        proc=subprocess.run(['node',str(ROOT/'reference/js/bin/kristal-ref.mjs'),cmd,str(file)],check=True,capture_output=True,text=True,cwd=ROOT/'reference/js')
        if not json.loads(proc.stdout)['ok']:
            raise AssertionError(f'GitHub read-surface reference command failed: {cmd}')
    proc=subprocess.run(['node',str(ROOT/'reference/js/bin/kristal-ref.mjs'),'v10-capabilities'],check=True,capture_output=True,text=True,cwd=ROOT/'reference/js')
    if json.loads(proc.stdout).get('schema_version') != '10.0':
        raise AssertionError('v10 capabilities command drift')


def check_v9_invariants():
    invariants=(ROOT/'spec/v9/Core-Invariants.md').read_text(encoding='utf-8')
    for token in (
        'LOGICAL STATE != PHYSICAL MATERIALIZATION','KNOWLEDGE != ASSERTION LIST',
        'SEMANTIC IDENTITY != CONTENT IDENTITY','LOGICAL COMMITMENT != BLOB DIGEST',
        'REPACK != LOGICAL REVISION','INDEX != SOURCE OF TRUTH','SHARD != SEGMENT',
        'STATE COMPOSITION != AUTHORITY MERGE','EPISTEMIC PROVENANCE != BUILD PROVENANCE',
        'PARTIAL AVAILABILITY != NEGATION','SMALL KRISTAL MUST STAY SMALL'):
        if token not in invariants: raise AssertionError(f'missing v9 invariant: {token}')
    conformance=(ROOT/'spec/v9/Conformance.md').read_text(encoding='utf-8')
    for profile in ('V9-State-Reader','V9-Builder','V9-Materializer','V9-Publisher','V9-Full'):
        if profile not in conformance: raise AssertionError(f'missing v9 conformance profile: {profile}')
    caps=load(V9_EXAMPLES/'v9-capabilities.example.json')
    if not {'kristal_state/6.0','kristall/7.0','kristall/8.0','kristal.state/9.0'}.issubset(set(caps['compatibility']['reads'])):
        raise AssertionError('v9 capability descriptor lost inherited reads')


def check_v9_commitment_vectors():
    vectors=load(V9_VECTORS/'logical-commitment-vectors.json')
    for v in vectors.get('vectors',[]):
        file=V9_VECTORS/v['file']
        cmd='logical-commitment-v9' if v['kind']=='logical_artifact' else 'state-commitment-v9'
        proc=subprocess.run(['node',str(ROOT/'reference/js/bin/kristal-ref.mjs'),cmd,str(file)],check=True,capture_output=True,text=True,cwd=ROOT/'reference/js')
        actual=json.loads(proc.stdout)['digest']
        if actual != v['expected_digest']:
            raise AssertionError(f'v9 commitment vector drift: {v["id"]}')


def check_v9_polymorphic_workloads():
    root=ROOT/'tck/v9/workloads'
    art_schema=load(V9_SCHEMA_ROOT/'kristal-logical-artifact.schema.json')
    state_schema=load(V9_SCHEMA_ROOT/'kristal-state-snapshot.schema.json')
    required_contracts={
        'workload.relation','workload.procedure-graph','workload.multiplex-graph','workload.formula-ir','workload.epistemic-corpus'
    }
    seen=set()
    for p in sorted(root.glob('*.logical-artifact.json')):
        doc=load(p); validate(doc,art_schema,f'v9 polymorphic workload {p.name}')
        seen.add(doc['logical_contract']['id'])
        proc=subprocess.run(['node',str(ROOT/'reference/js/bin/kristal-ref.mjs'),'verify-logical-artifact-v9',str(p)],check=True,capture_output=True,text=True,cwd=ROOT/'reference/js')
        if not json.loads(proc.stdout)['ok']: raise AssertionError(f'v9 workload commitment failed: {p.name}')
    if seen != required_contracts: raise AssertionError(f'v9 polymorphic workload set drift: {sorted(seen ^ required_contracts)}')
    fed=root/'federation.state-snapshot.json'; validate(load(fed),state_schema,'v9 federated workload')
    proc=subprocess.run(['node',str(ROOT/'reference/js/bin/kristal-ref.mjs'),'verify-state-v9',str(fed)],check=True,capture_output=True,text=True,cwd=ROOT/'reference/js')
    if not json.loads(proc.stdout)['ok']: raise AssertionError('v9 federated workload commitment failed')


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


def check_icon_profile_tooling():
    schema_path = ROOT/'tools/icons/kristal-icon-profile.schema.json'
    example_path = ROOT/'examples/v8/icon-profile.example.json'
    desktop_example_path = ROOT/'examples/v8/desktop.ini.example'
    schema = load(schema_path)
    Draft202012Validator.check_schema(schema)
    validate(load(example_path), schema, 'icon profile example')
    generator = (ROOT/'tools/icons/index.html').read_text(encoding='utf-8')
    for token in (
        "kristal-icon-pack/1.3", "kristal-icon/1.0", "#1e6864",
        "REF", "COL", "MOD", "PRT", "TWN", "INV", "SRC",
        "16,20,24,32,40,48,64,96,128,256",
        "KR-${type}-${p.map(d=>safe(d.id)).join('-')}-M${maturity}"
    ):
        if token not in generator:
            raise AssertionError(f'icon generator/profile drift: missing {token}')
    desktop = desktop_example_path.read_text(encoding='utf-8')
    for token in (
        '[.ShellClassInfo]', 'IconResource=', 'InfoTip=', '[Kristal]',
        'Profile=kristal-desktop/1.0', 'IconProfile=kristal-icon/1.0',
        'IconCode=KR-MOD-AUTO-ELEC-NET-M4', 'Maturity=4'
    ):
        if token not in desktop:
            raise AssertionError(f'desktop binding example drift: missing {token}')
    spec = (ROOT/'spec/v8/Kristal-Icon-Code.md').read_text(encoding='utf-8')
    for token in (
        'kristal-desktop/1.0', 'DESKTOP.INI != SEMANTIC AUTHORITY',
        'NAME • NATURE • DOMAINS • MATURITY • VOLUME'
    ):
        if token not in spec:
            raise AssertionError(f'desktop binding spec drift: missing {token}')


def check_active_version_text():
    version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    release = load(ROOT/'contracts/release.json')
    contract_set = load(ROOT/'contracts/contract-set.json')
    if not (release.get('version') == contract_set.get('version') == version):
        raise AssertionError('active release/version surfaces disagree')
    core = (ROOT/'spec/v10/01-core-spec/kristal-v10-core-spec.md').read_text(encoding='utf-8')
    if version not in core:
        raise AssertionError('v10 core spec not aligned to active VERSION')
    status = (ROOT/'spec/v10/00-overview/specification-status.md').read_text(encoding='utf-8')
    if version not in '\n'.join(status.splitlines()[:8]):
        raise AssertionError('active v10 specification status is stale')

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
        ('v10 examples/vectors', check_v10_examples_and_vectors),
        ('v9 examples/vectors', check_v9_examples_and_vectors),
        ('v8 examples/vectors', check_v8_examples_and_vectors),
        ('v7 examples/vectors', check_v7_examples_and_vectors),
        ('v6 portable contract', check_v6_portable_contract),
        ('v7 invariants', check_v7_invariants),
        ('v8 invariants', check_v8_invariants),
        ('v10 invariants', check_v10_invariants),
        ('v9 invariants', check_v9_invariants),
        ('compatibility errata', check_compatibility_errata),
        ('v8 compatibility lock', check_v8_compatibility_lock),
        ('v10 compatibility lock', check_v10_compatibility_lock),
        ('v9 compatibility lock', check_v9_compatibility_lock),
        ('v9 commitment vectors', check_v9_commitment_vectors),
        ('v9 polymorphic workloads', check_v9_polymorphic_workloads),
        ('GitHub read-surface profile', check_github_read_surface_profile),
        ('v10 reference tools', check_v10_reference_tools),
        ('v8 language helper', check_language_reference_tools),
        ('v8 query helpers', check_query_reference_tools),
        ('icon profile tooling', check_icon_profile_tooling),
        ('active version text', check_active_version_text),
        ('DaaT boundary', check_daat_boundary),
    ]
    for label, fn in checks:
        fn(); print(f'PASS: {label}')
    print('Kristal standard validation: PASS')

if __name__ == '__main__':
    main()
