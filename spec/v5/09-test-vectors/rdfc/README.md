# RDFC Test Vectors and Fixtures

## Status

Draft.

## Purpose

This directory contains pointers and packaging conventions for the optional Kristal v5 profile:

```text
profile-rdf-integrity-rdfc@2
```

This profile covers RDF dataset canonicalization, `rdf_hash`, fixture packaging, and CI gating for RDF projections of Kristal artifacts.

The goal is to make RDF integrity **verifiable, reproducible, and interoperable** by:

* standardizing how fixtures are stored and referenced;
* standardizing how expected hashes are recorded;
* documenting which RDFC conformance tests are gated in CI;
* capturing resource limits alongside fixtures;
* keeping RDF structural integrity separate from Kristal validation, certainty, authority recognition, and reader policy decisions.

RDFC fixtures help answer:

```text
Do these RDF projection bytes canonicalize and hash as expected?
```

They do not answer:

```text
Is this assertion true?
Is this assertion validated?
Who recognizes this artifact?
At what certainty level?
Under which reader policy should it be visible?
```

Those questions belong to Kristal v5 validation decisions, authority recognition, certainty metadata, federation semantics, and reader policies.

---

## Scope

In scope:

* fixture layout and naming;
* required metadata for reproducing `rdf_hash`;
* expected output recording;
* CI gating configuration pointers;
* resource limit declaration;
* projection coverage boundaries;
* integrity verification of RDF canonicalization outputs.

Out of scope:

* shipping the full W3C RDFC test suite inside this repository;
* making RDFC mandatory for Kristal v5 core conformance;
* using RDFC as proof of truth, authority recognition, or assertion validation;
* defining RDF export semantics directly;
* defining reader policy behavior.

Implementations MAY vendor the W3C RDFC test suite, reference it externally, or maintain a minimal local subset for CI.

---

## Relationship to Kristal v5

RDFC is an integrity profile for RDF projections.

Kristal v5 distinguishes:

```text
artifact integrity
assertion status
certainty level
validation status
authority recognition
reader visibility
```

RDFC affects only the RDF projection integrity layer.

A passing RDFC fixture means:

```text
The RDF projection canonicalizes and hashes as expected under the declared profile, algorithm, coverage boundaries, and resource limits.
```

It does not imply:

```text
assertion_status = "validated"
certainty_level = "high"
validation_status = "validated"
recognition_status = "recognized"
artifact_status = "reference"
```

Those statuses require explicit Kristal v5 metadata or records.

---

## Directory layout

Recommended layout:

```text
09-test-vectors/rdfc/
  README.md

  fixtures/
    wdqs-full/
      case-0001/
        export.rdf.nq
        export.manifest.json
        expected.rdf_hash.sha256
      case-0002/
        ...

    wdqs-truthy/
      case-0001/
        export.rdf.nq
        export.manifest.json
        expected.rdf_hash.sha256

    jsonld-rdf/
      case-0001/
        export.rdf.nq
        export.manifest.json
        expected.rdf_hash.sha256

    implementation-defined/
      case-0001/
        export.rdf.nq
        export.manifest.json
        expected.rdf_hash.sha256

    stress/
      case-0001/
        export.rdf.nq
        export.manifest.json
        expected.rdf_hash.sha256

  ci/
    rdfc-gating.json
    rdfc-gating-notes.md
```

---

## Fixture case contents

Each `case-XXXX/` directory MUST include the following files.

### 1. `export.rdf.nq`

The RDF dataset export for the declared projection.

Requirements:

* MUST be deterministic for the declared export profile;
* MUST use N-Quads when named graphs are relevant;
* MUST follow the RDF export profile’s sorting and serialization rules before RDFC canonicalization;
* MUST correspond exactly to the coverage boundaries declared in `export.manifest.json`.

The file MAY contain RDF derived from:

```text
Exchange
Exchange Shard
Exchange Federation Manifest
Structured Epistemic State
Authority Registry
Validation Decision
Authority Recognition
Reader Policy
Runtime Pack metadata
```

Only the declared projection is covered.

---

### 2. `export.manifest.json`

The fixture manifest.

It MUST declare:

* fixture ID;
* Kristal spec version;
* RDF export profile ID and version;
* projection ID;
* projection mode;
* integrity profile ID and version;
* source artifact reference;
* coverage boundaries;
* canonicalization algorithm ID and version;
* resource limits used for canonicalization;
* skolemization policy, if applicable;
* blank node handling policy;
* expected hash file path;
* whether the fixture is included in default CI gating.

Recommended profile IDs:

```text
profile-rdf-wdqs-export@2
profile-jsonld-export@2
profile-rdf-integrity-rdfc@2
```

---

### 3. `expected.rdf_hash.sha256`

A single line containing the expected SHA-256 hash hex string.

Requirements:

* MUST contain exactly 64 lowercase hexadecimal characters;
* MUST NOT include prefixes such as `sha256:`;
* SHOULD end with a newline;
* MUST correspond to the RDF canonicalization output declared in `export.manifest.json`.

Example:

```text
0000000000000000000000000000000000000000000000000000000000000000
```

---

## Optional fixture files

A fixture case MAY include:

```text
notes.md
expected.canonical.nq
expected.profile-status.json
expected.validation-report.json
```

Meanings:

* `notes.md`: explains special modeling cases such as blank nodes, datatypes, ranks, named graphs, provenance graphs, validation decision graphs, or authority recognition graphs.
* `expected.canonical.nq`: stores canonicalized RDF output for debugging.
* `expected.profile-status.json`: stores expected profile-level status.
* `expected.validation-report.json`: stores expected structural validation or CI report output.

`expected.canonical.nq` can be useful for diagnosis, but it may increase repository size. It SHOULD be included only for small or strategically important fixtures unless the repository explicitly chooses to store canonical outputs.

---

## Naming conventions

Fixture groups SHOULD use stable names.

Recommended projection groups:

```text
wdqs-full/
wdqs-truthy/
jsonld-rdf/
implementation-defined/
stress/
```

Meanings:

* `wdqs-full/`: RDF WDQS export preserving full statements, qualifiers, references, ranks, and supporting graphs where applicable.
* `wdqs-truthy/`: RDF WDQS export using a truthy or best-rank projection.
* `jsonld-rdf/`: RDF interpreted from the JSON-LD export profile.
* `implementation-defined/`: implementation-specific RDF projection with explicit projection metadata.
* `stress/`: fixtures that exceed default CI limits or are intended for performance, memory, or pathological canonicalization testing.

Case IDs:

```text
case-0001
case-0002
case-0003
```

Case IDs MUST be stable.

If a fixture changes in a way that affects semantics, projection coverage, canonicalized output, or expected hash, create a new case ID rather than overwriting the old one.

---

## Coverage boundaries

Fixtures MUST explicitly record coverage boundaries because RDFC hashing is meaningful only relative to what the RDF projection includes.

A fixture MUST declare:

* which projection is covered;
* which artifact type is the source;
* which named graphs are included;
* which named graphs are excluded;
* whether provenance graphs are included;
* whether validation decision graphs are included;
* whether authority recognition graphs are included;
* whether reader policy graphs are included;
* whether operational metadata is excluded;
* whether timestamps are excluded;
* whether signatures are excluded;
* whether content-addressed ID fields are excluded from their own hash target.

A fixture without explicit coverage boundaries is non-conformant to this profile.

---

## Projection modes

Recommended projection modes:

```text
full
truthy
jsonld
authority
validation
reader_policy
federated
implementation_defined
```

Projection mode meanings:

* `full`: preserves all available RDF-representable statements and metadata in the selected profile.
* `truthy`: exports a reduced or best-rank view.
* `jsonld`: RDF derived from the JSON-LD profile.
* `authority`: emphasizes authority registry and recognition records.
* `validation`: emphasizes validation decisions and assertion status metadata.
* `reader_policy`: emphasizes reader policy filters and visibility metadata.
* `federated`: covers a composed federation projection.
* `implementation_defined`: projection is defined by the implementation and must be fully described in the manifest.

---

## Resource limits

Because RDF dataset canonicalization may have worst-case behavior, each fixture MUST record the resource limits used when generating the expected hash.

Required limits:

```text
timeout_ms
max_triples
max_blank_nodes
```

Recommended limits:

```text
max_memory_mb
max_named_graphs
max_bytes
```

If a fixture exceeds default limits on a reference implementation, it SHOULD be moved to:

```text
fixtures/stress/
```

Stress fixtures SHOULD NOT be part of default CI gating unless the implementation explicitly opts in.

---

## Skolemization policy

If the RDF projection uses skolem IRIs, the fixture manifest MUST declare:

```text
skolemization.enabled
skolemization.policy_id
skolemization.base_iri
skolemization.deterministic
```

If no skolemization is used, the fixture manifest MUST declare:

```json
{
  "skolemization": {
    "enabled": false
  }
}
```

Blank node handling MUST be explicit because it affects RDF canonicalization.

---

## CI gating configuration

The file:

```text
ci/rdfc-gating.json
```

SHOULD define:

* which RDFC test suite and version is used;
* which subset is gated;
* which local fixture cases are included in CI;
* which stress fixtures are excluded by default;
* resource limits used in CI;
* expected profile ID and version;
* expected algorithm ID and version.

Example:

```json
{
  "profile": "profile-rdf-integrity-rdfc@2",
  "spec_version": "5.0",
  "rdfc_suite": {
    "name": "W3C RDFC-1.0",
    "version": "1.0",
    "source": "external"
  },
  "gated_tests": [
    "t001",
    "t002",
    "t010"
  ],
  "fixtures": [
    {
      "path": "fixtures/wdqs-full/case-0001",
      "projection_mode": "full",
      "included_in_default_ci": true
    },
    {
      "path": "fixtures/wdqs-truthy/case-0001",
      "projection_mode": "truthy",
      "included_in_default_ci": true
    }
  ],
  "excluded_by_default": [
    {
      "path": "fixtures/stress/case-0001",
      "reason": "resource_limits_exceeded"
    }
  ],
  "limits": {
    "timeout_ms": 30000,
    "max_triples": 500000,
    "max_blank_nodes": 200000,
    "max_named_graphs": 10000,
    "max_memory_mb": 1024
  }
}
```

---

## Minimal `export.manifest.json`

Non-normative example:

```json
{
  "fixture_id": "rdfc:wdqs-full:case-0001",
  "spec_version": "5.0",
  "source_ref": {
    "artifact_type": "reference_exchange",
    "artifact_id": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "content_hash": {
      "alg": "sha256",
      "value": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  },
  "rdf_export_profile": {
    "id": "profile-rdf-wdqs-export@2",
    "projection_mode": "full",
    "version": "2"
  },
  "integrity_profile": {
    "id": "profile-rdf-integrity-rdfc@2",
    "version": "2"
  },
  "canonicalization": {
    "algorithm": "RDFC-1.0",
    "algorithm_version": "1.0",
    "hash_alg": "sha256"
  },
  "coverage": {
    "included_graphs": [
      "assertions",
      "provenance",
      "evidence",
      "validation_decisions",
      "authority_recognition"
    ],
    "excluded_graphs": [
      "operational_metadata",
      "runtime_cache",
      "signatures"
    ],
    "includes_provenance": true,
    "includes_validation_decisions": true,
    "includes_authority_recognition": true,
    "includes_reader_policy": false,
    "excludes_timestamps": true,
    "excludes_signatures": true,
    "excludes_output_id_from_own_hash": true
  },
  "skolemization": {
    "enabled": false
  },
  "limits": {
    "timeout_ms": 30000,
    "max_triples": 500000,
    "max_blank_nodes": 200000,
    "max_named_graphs": 10000,
    "max_memory_mb": 1024
  },
  "files": {
    "rdf_export": "export.rdf.nq",
    "expected_hash": "expected.rdf_hash.sha256",
    "expected_canonical": null
  },
  "ci": {
    "included_in_default_ci": true,
    "stress": false
  }
}
```

---

## Expected hash semantics

The expected hash file records the SHA-256 hash of the canonical RDF dataset bytes produced by the declared RDFC algorithm and fixture manifest.

The expected hash MUST be computed over:

```text
canonical RDF output bytes
```

It MUST NOT be computed over:

```text
export.manifest.json
expected.rdf_hash.sha256
signatures
operational logs
runtime cache files
timestamps excluded by coverage policy
```

If another profile explicitly includes RDFC artifacts in a larger package hash, that package hash is separate from `rdf_hash`.

---

## Verification procedure

Implementers SHOULD use this directory as follows:

1. Generate an RDF export for a fixture case using the declared RDF export profile.
2. Verify that the export matches the declared projection and coverage boundaries.
3. Apply `profile-rdf-integrity-rdfc@2`.
4. Produce canonical RDF bytes.
5. Compute SHA-256 over the canonical RDF bytes.
6. Compare the result to `expected.rdf_hash.sha256`.
7. Run the CI gate subset defined in `ci/rdfc-gating.json`.
8. Report profile status.

Recommended profile status values:

```text
not_declared
declared
verified
verification_failed
execution_not_run
execution_passed
execution_failed
unsupported
resource_limit_exceeded
```

---

## Failure semantics

If a fixture cannot be verified, implementations SHOULD report a fixture-level or profile-level failure.

Examples:

```json
{
  "profile": "profile-rdf-integrity-rdfc@2",
  "fixture_id": "rdfc:wdqs-full:case-0001",
  "profile_status": "verification_failed",
  "reason_codes": [
    "hash_invalid"
  ]
}
```

Recommended reason codes:

```text
manifest_missing
rdf_export_missing
expected_hash_missing
hash_invalid
coverage_missing
coverage_mismatch
projection_mismatch
unsupported_projection
unsupported_rdfc_algorithm
resource_limit_exceeded
canonicalization_error
nondeterministic_output
```

A failed RDFC fixture means the RDF integrity profile failed for that fixture.

It does not mean that the underlying Kristal assertion is false, rejected, unrecognized, or low-certainty.

---

## Reader policy interaction

Reader policies MAY use RDFC fixture or package verification status as a structural quality signal.

Examples:

* a strict reference-only reader policy MAY require RDF integrity verification for RDF-backed views;
* a validated-only reader policy MAY ignore RDF fixture status if it does not rely on RDF projection;
* a research reader policy MAY show RDF-backed material with visible verification warnings;
* a creative reader policy MAY ignore RDFC fixtures entirely.

Reader policies MUST NOT treat RDFC verification as authority recognition.

---

## Authority recognition interaction

An authority channel MAY require RDFC verification as one input to its validation policy.

Example:

```text
authority:example-data-body
requires:
  - schema validation
  - provenance sufficiency
  - RDF projection coverage declaration
  - RDFC hash verification
  - review by declared validator
```

In that case, RDFC verification is evidence used by the authority channel.

The authority recognition record remains the place to express:

```text
recognition_status
recognized_as
scope
validation_policy_ref
reason_codes
```

---

## Notes on full vs truthy projections

For Wikidata-aligned exports:

* `full` fixtures SHOULD preserve full statements, qualifiers, references, ranks, and supporting graphs where applicable.
* `truthy` fixtures MAY expose a reduced best-rank projection.
* The fixture manifest MUST state which mode is used.
* A `truthy` fixture MUST NOT be treated as equivalent to a full reference artifact.

The source Kristal may preserve more structure than a given RDF projection exposes.

---

## Open questions

To finalize:

* Whether to store `expected.canonical.nq` for all default fixtures or only selected debug fixtures.
* Whether to vendor a minimal RDFC subset locally or require implementations to pull the suite externally.
* Whether to include additional projections beyond `full`, `truthy`, `jsonld`, and `implementation_defined`.
* Whether stress fixtures should have a separate CI profile.
* Whether profile status reports should be stored beside each fixture by default.
* Whether authority and validation graphs should be included in default `wdqs-full` fixtures or split into dedicated fixture groups.
