# Profile: Validation ShEx

## Status

Optional standardized profile for Kristal v5.

## Profile ID

```text
profile-validation-shex@2
```

## Purpose

This profile defines how a Kristal v5 implementation MAY publish **ShEx (Shape Expressions)** artifacts derived from declared Kristal Exchange projections to support:

* structural conformance checking by external tooling;
* implementer guidance and ecosystem interoperability;
* debugging and validation transparency;
* inspection of how Kristal assertions, scopes, provenance, authority recognition, and certainty metadata are projected into RDF-compatible forms.

ShEx outputs are **structural validation aids**. They do not determine Kristal truth, authority recognition, assertion status, certainty level, or reader visibility.

A ShEx artifact MAY help verify that a projected graph has the expected shape. It MUST NOT be treated as proof that the underlying assertions are validated, true, recognized, high-certainty, or accepted by an authority channel.

ShEx artifacts do not change the Exchange, Shard, Federation, Runtime Pack, Authority Registry, Validation Decision, or Reader Policy schemas. They do not affect content-addressed IDs unless explicitly included in hashed material by a separate declared profile.

---

## Scope

This profile specifies:

* required and optional ShEx artifacts;
* deterministic generation rules, when deterministic generation is claimed;
* packaging and manifest references;
* integrity verification requirements when ShEx artifacts are declared;
* the relationship between ShEx structural validation and Kristal v5 validation semantics.

This profile does **not**:

* make ShEx the primary Kristal validation mechanism;
* assign assertion status;
* assign certainty levels;
* create authority recognition;
* validate claims as fact, hypothesis, myth, fiction, policy, or institutional reference;
* require ShEx for Kristal v5 core conformance;
* require specific ShEx engines or toolchains;
* require consumers to execute ShEx validation during normal reading.

Kristal v5 validation remains scoped by:

```text
authority_channel
validation_policy
validation_status
validated_as
certainty_level
scope
reader_policy
```

ShEx only describes whether a declared RDF projection conforms to declared shapes.

---

## Conformance

An implementation claims this profile by including:

```text
profile-validation-shex@2
```

in one or more of:

* the Exchange Manifest `profiles[]`, if ShEx artifacts are attached to an Exchange;
* the Exchange Shard Manifest `profiles[]`, if ShEx artifacts are attached to a shard;
* the Exchange Federation Manifest `profiles[]`, if ShEx artifacts describe a federated projection;
* the Runtime Pack Manifest `profiles[]`, if ShEx artifacts are shipped with Runtime Packs.

If an implementation claims this profile, it MUST meet the requirements below.

---

## Relationship to Kristal v5 validation

ShEx validation and Kristal validation are different operations.

### ShEx structural validation

ShEx answers:

```text
Does this RDF projection have the expected structural shape?
```

Examples:

* required predicates are present;
* values have expected datatypes;
* projected nodes match declared shape constraints;
* expected provenance or authority fields are structurally present.

### Kristal validation

Kristal validation answers:

```text
Who accepts this claim, artifact, shard, or authority channel,
under which policy,
for which scope,
as what,
and at what certainty level?
```

Examples:

* an assertion is validated as a hypothesis;
* a shard is recognized by an authority channel;
* a medical corpus is recognized through a health authority;
* a mythological corpus is valid as mythology;
* a disputed claim is structurally preserved but rejected by a selected authority channel.

A passing ShEx result MUST NOT imply:

```text
validation_status = "validated"
recognition_status = "recognized"
certainty_level = "high"
artifact_status = "reference"
```

Those statuses require Kristal v5 validation decisions, authority recognition records, or reader policy evaluation.

---

## Artifacts

### Required artifacts

If this profile is claimed, the implementation MUST provide the following artifacts.

### 1. Primary ShEx schema

Recommended path:

```text
validation/shex/kristal.shex
```

Any path is allowed if referenced in the manifest.

Supported formats:

```text
ShExC: text/shex
ShExJ: application/json
```

The schema MUST describe the shapes relevant to the declared RDF projection covered by this profile.

The schema SHOULD include shapes for projected Kristal v5 concepts when present:

* Exchange;
* Exchange Shard;
* Federation Manifest;
* assertion;
* provenance reference;
* evidence reference;
* scope;
* authority channel;
* authority recognition;
* validation decision;
* certainty level;
* reader policy reference.

The schema MUST NOT claim to validate truth, authority, certainty, or recognition unless those concepts are represented as structural fields in the projection.

---

### 2. ShEx metadata descriptor

Recommended path:

```text
validation/shex/manifest.json
```

The descriptor MUST declare:

* profile ID;
* Kristal spec version;
* schema format;
* covered export projection or projections;
* generation tool information;
* generator configuration hash;
* deterministic generation flag;
* Exchange, Shard, Federation, or Runtime Pack reference;
* whether ShEx artifacts are included in content-addressed material;
* whether ShEx execution is required by the declaring profile.

---

## Optional artifacts

The implementation MAY provide:

```text
validation/shex/examples/
validation/shex/examples/passing/
validation/shex/examples/failing/
validation/shex/mapping.md
validation/shex/reports/
```

Optional artifact meanings:

* `examples/passing/`: minimal projected RDF examples expected to pass.
* `examples/failing/`: minimal projected RDF examples expected to fail structurally.
* `mapping.md`: human-readable mapping from Kristal v5 constructs to ShEx shapes.
* `reports/`: example validation reports; not normative unless explicitly declared by a separate profile.

---

## Coverage and projection rules

ShEx shapes MUST be defined against a **declared RDF projection** of Kristal material.

Implementations MUST specify one or more of the following projections.

### Projection A: WDQS-aligned RDF

The RDF projection defined in:

```text
05-profiles/profile-rdf-wdqs-export.md
```

This projection SHOULD preserve the relevant Wikidata-compatible structures when used for Wikidata Seed Kristals or WDQS-compatible exports.

### Projection B: JSON-LD RDF mapping

The JSON-LD export defined in:

```text
05-profiles/profile-jsonld-export.md
```

interpreted as RDF.

### Projection C: implementation-defined RDF projection

Allowed only if the exact projection is specified in:

```text
validation/shex/manifest.json
```

The implementation-defined projection MUST include:

* projection ID;
* projection version;
* projection description;
* source artifact type;
* mapping rules;
* hash of the projection definition, if deterministic generation is claimed.

The ShEx schema MUST explicitly name which projection or projections it covers.

---

## Deterministic generation requirements

If the implementation claims deterministic generation for ShEx artifacts, then generation MUST be deterministic given:

* the same source artifact snapshot;
* the same declared RDF projection;
* the same generation tool name and version;
* the same generation configuration;
* the same canonicalization rules for generated artifacts.

The ShEx metadata descriptor MUST include:

```text
generator.name
generator.version
generator.config_hash
source_ref
projection.id
projection.version
deterministic = true
```

Any ordering within ShExJ output that affects bytes MUST be deterministic. This includes stable ordering of:

* shapes;
* predicates;
* node constraints;
* value constraints;
* imports;
* prefixes, when emitted in order-sensitive formats.

If deterministic generation is not claimed, the profile MAY still be used, but the metadata descriptor MUST set:

```json
"deterministic": false
```

When `deterministic` is `false`, ShEx artifacts MUST NOT be used as the basis for content-addressed Kristal IDs.

---

## Packaging and manifest references

### If attached to an Exchange

The Exchange Manifest MUST list the ShEx files in its file inventory section, if such a section is present.

Each declared ShEx file MUST include:

```text
path
media_type
sha256
size_bytes
role
```

Recommended role:

```text
metadata
```

### If attached to an Exchange Shard

The Exchange Shard Manifest MUST reference the ShEx descriptor or ShEx files when the profile is claimed for that shard.

The manifest SHOULD indicate whether the ShEx artifacts describe:

```text
the shard only
the source Exchange projection
a subset projection
a federated projection
```

### If attached to a Federation Manifest

The Federation Manifest MUST specify whether the ShEx artifacts describe:

```text
each shard independently
the composed federated projection
both
```

Federated ShEx artifacts MUST NOT hide disagreement between shards. If conflicting claims are preserved by federation, the projection and shapes SHOULD preserve enough structure to expose those conflicts.

### If attached to Runtime Packs

The Runtime Pack Manifest MUST include the ShEx files in `files[]` with:

```text
role = "metadata"
sha256
size_bytes
media_type
```

A future profile MAY define a dedicated role such as:

```text
validation_schema
```

Until then, `metadata` is the standard role.

---

## Verification requirements

If ShEx artifacts are declared in a manifest and the consumer is configured to verify package integrity, then the consumer MUST verify:

* file presence;
* declared `sha256`;
* declared `size_bytes`, if present;
* descriptor consistency;
* profile ID consistency;
* projection ID consistency.

If a declared ShEx file is missing or its hash does not match, the artifact package MUST be marked as failing integrity verification for that declared profile.

This does not mean the underlying Kristal assertions are false. It means the declared ShEx profile package is incomplete or inconsistent.

Consumers MAY continue to inspect the rest of the package according to reader policy, provided that the missing or invalid ShEx profile status is visible.

---

## ShEx execution semantics

Running a ShEx engine is OPTIONAL for consumers.

A consumer MAY execute ShEx validation to check whether a declared RDF projection conforms to the declared ShEx schema.

A consumer MUST NOT require ShEx execution for Kristal v5 core conformance unless a separate profile explicitly requires it.

A ShEx execution result MUST be interpreted as structural evidence only.

A passing ShEx result means:

```text
The tested RDF projection conforms to the declared ShEx shapes.
```

A failing ShEx result means:

```text
The tested RDF projection does not conform to the declared ShEx shapes,
or the ShEx engine could not complete validation.
```

A failing ShEx result MUST NOT automatically imply:

```text
assertion_status = "rejected"
validation_status = "rejected"
recognition_status = "revoked"
certainty_level = "low"
```

Those statuses require Kristal validation decisions or authority recognition records.

---

## Failure and status semantics

When ShEx artifacts are declared but cannot be verified, implementations SHOULD report a profile-level status.

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
```

Example:

```json
{
  "profile": "profile-validation-shex@2",
  "profile_status": "verification_failed",
  "reason_codes": ["hash_invalid"],
  "affected_files": ["validation/shex/kristal.shex"]
}
```

Recommended reason codes:

```text
schema_file_missing
descriptor_missing
hash_invalid
size_mismatch
projection_mismatch
profile_id_mismatch
unsupported_shex_format
unsupported_projection
execution_error
shape_validation_failed
```

These reason codes MAY appear in validation reports, runtime diagnostics, or reader-facing inspection panels.

---

## Interaction with reader policies

Reader policies MAY use ShEx profile status as a structural quality signal.

Examples:

* a strict reader policy MAY require declared ShEx files to verify successfully;
* a research reader policy MAY show artifacts even when ShEx execution has not been run;
* a creative reader policy MAY ignore ShEx entirely;
* a reference-only reader policy MAY require both Kristal authority recognition and ShEx package verification.

Reader policies MUST NOT treat ShEx structural conformance as equivalent to authority recognition.

---

## Interaction with authority recognition

An authority channel MAY require ShEx artifacts as part of its validation policy.

Example:

```text
authority:example-health-body
requires:
  - schema validation
  - provenance sufficiency
  - ShEx structural conformance against projection A
  - expert review
```

In that case, ShEx results are inputs to the authority’s validation policy. They are not the validation decision itself.

The authority recognition record remains the authoritative place to express:

```text
recognition_status
recognized_as
scope
validation_policy_ref
reason_codes
```

---

## Minimal `validation/shex/manifest.json` schema

This section is non-normative.

Recommended fields:

```json
{
  "profile": "profile-validation-shex@2",
  "spec_version": "5.0",
  "deterministic": true,
  "included_in_content_hash": false,
  "source_ref": {
    "artifact_type": "reference_exchange",
    "artifact_id": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "content_hash": {
      "alg": "sha256",
      "value": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  },
  "projection": {
    "id": "profile-rdf-wdqs-export@1",
    "version": "1",
    "notes": "Shapes target the WDQS-aligned RDF projection."
  },
  "schema": {
    "path": "validation/shex/kristal.shex",
    "format": "ShExC",
    "media_type": "text/shex",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "size_bytes": 0
  },
  "generator": {
    "name": "kristal-shex-gen",
    "version": "2.0.0",
    "config_hash": {
      "alg": "sha256",
      "value": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  }
}
```

---

## Minimal profile status report

This section is non-normative.

```json
{
  "profile": "profile-validation-shex@2",
  "spec_version": "5.0",
  "profile_status": "execution_passed",
  "source_ref": {
    "artifact_type": "reference_exchange",
    "artifact_id": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
  },
  "projection": {
    "id": "profile-rdf-wdqs-export@1",
    "version": "1"
  },
  "schema_ref": {
    "path": "validation/shex/kristal.shex",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "execution": {
    "engine": {
      "name": "example-shex-engine",
      "version": "1.0.0"
    },
    "started_at": "2026-06-12T00:00:00Z",
    "completed_at": "2026-06-12T00:00:01Z",
    "result": "passed"
  },
  "reason_codes": []
}
```

---

## Security and integrity notes

ShEx artifacts can improve transparency, but they also create additional files that must be tracked correctly.

Implementations SHOULD ensure that:

* ShEx files are included in package inventories when declared;
* hashes use `alg`, not `algo`;
* signatures are excluded from their own hash targets;
* generated ShExJ output is deterministically ordered when determinism is claimed;
* source artifact IDs are not recomputed using generated ShEx artifacts unless explicitly included by profile;
* profile failures are visible to readers or operators.

---

## Summary

This profile standardizes how Kristal v5 implementations may publish ShEx artifacts for structural validation of RDF projections.

ShEx helps answer:

```text
Does this projected graph have the expected shape?
```

It does not answer:

```text
Is this claim true?
Who recognizes it?
At what certainty level?
Under which authority channel?
For which reader policy?
```

Those questions remain governed by Kristal v5 validation decisions, certainty metadata, authority recognition, federation semantics, and reader policies.
