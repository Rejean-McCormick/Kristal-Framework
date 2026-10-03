# Conformance and Alignment (Kristal v5)

## Status

Draft — normative alignment guide for Kristal v5 documentation, schemas, examples, profiles, manifests, and implementation contracts.

## Purpose

This document defines the cross-file alignment rules for Kristal v5.

Its purpose is to keep the Kristal v5 specification internally consistent across:

* overview documents;
* core specification documents;
* JSON Schemas;
* reproducibility rules;
* query contracts;
* standardized profiles;
* integration contracts;
* security guidance;
* operational guidance;
* examples and test vectors.

Kristal v5 is a deterministic, portable epistemic artifact system.

It allows hypotheses, claims, references, myths, fictional corpora, institutional records, research submissions, technical declarations, disputed positions, and validated reference material to coexist without being confused.

The core conformance principle is:

> A Kristal may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.
> A Kristal must not present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

This document defines the alignment requirements that make that principle enforceable.

---

## Normative keywords

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

---

# 1. Global constants

All Kristal v5 documents, schemas, examples, profiles, and manifests MUST align with the following constants unless a profile explicitly declares a different versioned surface.

```text
SPEC_NAME = "Kristal v5"
SPEC_VERSION = "5.0"
DOC_ROOT = "kristal-docs-v5"
SCHEMA_BASE_URL = "https://kristal.org/schemas/v5/"
CANONICALIZATION_PROFILE = "kristal.v5:jcs-rfc8785"
CANONICALIZATION_VERSION = "1"
HASH_ALG = "sha256"
DEFAULT_SIGNATURE_ALG = "ed25519"
PRIMARY_LANGUAGE = "en"
```

Schema documents MUST use:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://kristal.org/schemas/v5/<schema-name>.schema.json"
}
```

Artifacts and manifests MUST use:

```json
{
  "schema_version": "5.0"
}
```

Runtime Packs SHOULD use:

```json
{
  "runtime_pack_version": "5.0.0"
}
```

Exchange artifacts SHOULD use:

```json
{
  "exchange_version": "5.0"
}
```

---

# 2. Required conceptual separation

Kristal v5 conformance depends on keeping the following concepts separate:

```text
artifact existence
≠ artifact integrity
≠ assertion status
≠ certainty level
≠ validation status
≠ authority recognition
≠ reader visibility
≠ runtime activation
```

A Kristal artifact may be:

* well-formed;
* content-addressed;
* reproducible;
* signed;
* queryable;
* distributable;

while still containing assertions that are:

* hypothetical;
* uncertain;
* disputed;
* fiction-scoped;
* mythology-scoped;
* rejected by some authority channels;
* recognized only by a local authority;
* not visible under a strict reader policy.

Conformant implementations MUST preserve this separation.

---

# 3. Required vocabulary

The following terms SHOULD be used consistently across Kristal v5:

```text
Kristal
Structured Epistemic State
Working Artifact
Reference Artifact
Exchange
Runtime Pack
Shard
Federation Manifest
Authority Channel
Authority Registry
Validation Policy
Validation Decision
Authority Recognition
Recognition Scope
Certainty Level
Assertion Status
Reader Policy
Transparency Log
```

## 3.1 Terms to avoid

The following terms MUST NOT be used as normative Kristal v5 status labels:

```text
canonical truth
truth object
canonical artifact
canonical status
source of truth
truth-plane
promotion
promoted
fail-safe
```

The following terms SHOULD NOT be used in public-facing or conceptual v5 documentation:

```text
fail-closed
no compile on fail
hard truth gate
single truth authority
universal truth authority
```

Exception: `canonicalization` is allowed because it refers to a stable byte representation for hashing, not to truth authority.

## 3.2 Replacement terms

Use the following replacements:

```text
canonical truth          -> recognized reference / validated reference / trusted-for-scope reference
truth object             -> structured reference artifact
canonical artifact       -> reference artifact
canonical status         -> recognized status / reference status
source of truth          -> reference source / authority-recognized source
promotion                -> recognition / validation decision / reference acceptance
promoted                 -> recognized / accepted / reference-approved
fail-closed              -> required verification / integrity enforcement / activation requirements
```

---

# 4. Artifact classes

Kristal v5 documents and schemas SHOULD use the following artifact type vocabulary.

```text
structured_epistemic_state
working_exchange
reference_exchange
runtime_pack
exchange_shard_manifest
exchange_federation_manifest
authority_registry
authority_recognition
validation_decision
validation_report
review_bundle
revocations
reader_policy
transparency_log_entry
```

The following artifact types MUST NOT be introduced in v5 schemas or examples:

```text
canonical_exchange
canonical_artifact
truth_artifact
```

---

# 5. Artifact status

Kristal v5 uses `artifact_status` for the lifecycle status of artifacts.

Allowed values:

```text
draft
working
under_review
recognized
reference
deprecated
superseded
revoked
```

Rules:

* `working` means the artifact exists and may be inspected, reviewed, queried, distributed, or used under policy.
* `under_review` means the artifact is being evaluated by one or more validation or recognition processes.
* `recognized` means at least one declared authority channel recognizes the artifact under a declared scope and policy.
* `reference` means the artifact is stable enough to be used as a reference under a selected authority channel and reader policy.
* `deprecated` means the artifact remains historically inspectable but is no longer preferred.
* `superseded` means another artifact replaces it under a declared lineage relationship.
* `revoked` means the artifact must not be accepted under the affected trust, validation, or recognition policy.

`artifact_status` MUST NOT be used as a substitute for assertion-level validation.

---

# 6. Assertion status

Kristal v5 uses `assertion_status` for the epistemic state of an assertion.

Allowed values:

```text
hypothesis
claimed
sourced
disputed
reviewed
validated
rejected
retracted
superseded
```

Rules:

* An assertion may be valid as a hypothesis.
* An assertion may be valid as mythology, fiction, symbolic structure, or publisher declaration.
* `validated` MUST NOT be interpreted as universal truth.
* `validated` MUST be interpreted together with `validated_as`, `certainty_level`, `authority_channel`, `validation_policy`, and `scope`.

A conformant reader MUST NOT display `assertion_status = validated` without preserving the relevant scope and authority context when that context exists.

---

# 7. Certainty levels

Kristal v5 uses `certainty_level` for the strength of an assertion inside a declared scope.

Allowed values:

```text
unknown
speculative
low
medium
high
established
not_applicable
```

Rules:

* `not_applicable` SHOULD be used for fictional, mythological, symbolic, doctrinal, or publisher-declared material when physical-world certainty is not the relevant axis.
* `established` SHOULD be reserved for high-confidence reference material under a selected authority channel and validation policy.
* A reader policy MAY include only validated data while still allowing multiple certainty levels.
* A Runtime Pack MUST NOT remove certainty labels required by its declared reader policy or query contract.

---

# 8. Validation modes

Kristal v5 uses `validated_as` to specify what kind of status has been validated.

Allowed values:

```text
hypothesis
claim
sourced_claim
reviewed_claim
high_confidence_fact
institutional_reference
publisher_declaration
technical_specification
legal_or_policy_position
mythological_corpus
fictional_corpus
symbolic_model
disputed_position
rejected_claim
```

Rules:

* Validation answers: who accepts this status, under which policy, for which scope.
* Certainty answers: how strong the assertion is within that scope.
* Validation does not always imply high certainty.
* Validation does not imply universal recognition.
* Validation by one authority channel does not imply validation by another.

A conformant validation object MUST NOT use:

```json
{ "validated": true }
```

as a complete validation representation.

It MUST instead declare, directly or by reference:

```text
validation_status
validated_as
certainty_level
authority_channel
validation_policy_ref
scope
```

---

# 9. Validation status

Allowed values for `validation_status`:

```text
not_evaluated
in_review
validated
conditionally_validated
disputed
rejected
revoked
```

Rules:

* `not_evaluated` is a valid state, not an error.
* `in_review` means evaluation is active or pending.
* `conditionally_validated` means acceptance depends on declared limits or requirements.
* `disputed` means one or more relevant authority channels or review processes contest the assertion or artifact.
* `rejected` means the target failed a validation decision under a declared authority channel and policy.
* `revoked` means a previous validation status is no longer accepted under the relevant authority channel and policy.

---

# 10. Authority recognition

Kristal v5 uses authority channels to represent scoped sources of recognition.

A conformant authority channel SHOULD include:

```text
authority_channel_id
name
authority_type
scope
trust_roots
validation_policies
recognition_policies
revocation_policy_ref
```

Allowed `authority_type` values:

```text
individual
community
association
research_collective
academic_institution
standards_body
company
government
intergovernmental_organization
ai_validator
hybrid_collective
```

Allowed `recognition_status` values:

```text
recognized
conditionally_recognized
under_review
disputed
rejected
deprecated
revoked
```

Rules:

* No authority channel has universal monopoly by default.
* Recognition is scoped.
* Authorities may recognize other authorities.
* Delegation MUST be explicit.
* Recognition by one authority channel MUST NOT be presented as recognition by another authority channel unless declared.

---

# 11. Scope

Kristal v5 uses `scope` to constrain meaning, authority, validation, recognition, and reader visibility.

Minimum shape:

```json
{
  "domain": "string"
}
```

Recommended shape:

```json
{
  "domain": "science",
  "subdomain": "climate",
  "jurisdiction": "global",
  "time_window": "2026",
  "tenant_id": "tenant:example",
  "environment": "prod",
  "language": "en"
}
```

Allowed `domain` values SHOULD include:

```text
general
wikidata
science
health
education
heritage
law
policy
technology
environment
culture
mythology
fiction
research
operations
civic
local_notes
```

Rules:

* `domain` is required.
* `subdomain` is optional but recommended for large corpora.
* `jurisdiction` SHOULD be used when legal, civic, regulatory, or governmental scope matters.
* `time_window` SHOULD be used when source validity changes over time.
* `tenant_id` SHOULD be used in multi-tenant deployments.
* `environment` SHOULD be used in deployment-specific artifacts.
* `language` SHOULD be used when language affects interpretation or reader presentation.

---

# 12. Reader policy

Reader policy controls visible material.

Allowed reader modes:

```text
reference_only
validated_only
high_certainty_only
research
creative
all_with_labels
custom
```

Rules:

* `reference_only` SHOULD include only material accepted by selected reference channels.
* `validated_only` SHOULD include only material satisfying the active validation policy.
* `high_certainty_only` SHOULD include only material at accepted high-certainty levels.
* `research` MAY include drafts, disputed claims, hypotheses, partial reviews, and lower-certainty material.
* `creative` MAY include fiction, mythological corpora, speculative models, symbolic models, and worldbuilding material.
* `all_with_labels` MAY expose broad material, but labels MUST remain visible.
* `custom` MUST declare the filters it applies.

A reader policy MUST NOT silently convert scoped validation into universal truth.

---

# 13. Structured Epistemic State

Kristal v5 uses Structured Epistemic State as the normative input unit for compiled epistemic artifacts.

Minimum shape:

```json
{
  "schema_version": "5.0",
  "artifact_type": "structured_epistemic_state",
  "state_id": "sha256:<hex>",
  "created_at": "RFC3339",
  "created_by": {},
  "scope": {},
  "source_refs": [],
  "derived_from": [],
  "merged_from": [],
  "supersedes": [],
  "assertions": [],
  "provenance": [],
  "review_refs": [],
  "policy_refs": [],
  "certainty_summary": {},
  "validation_summary": {},
  "extensions": {}
}
```

Rules:

* Structured Epistemic State is the v5 normative input surface.
* Claim-IR MAY be used as an extractor proposal profile.
* Claim-IR MUST NOT be the universal required input format for Kristal v5.
* A human expert, institution, dataset, or authority channel MAY produce Structured Epistemic State directly.

---

# 14. Claim-IR alignment

Claim-IR remains useful, but its role is narrower in Kristal v5.

Required role:

```text
Claim-IR = extractor proposal profile
```

Allowed pipeline:

```text
LLM / OCR / parser / scraper
-> Claim-IR
-> Structured Epistemic State
-> Working Artifact
```

Also allowed:

```text
human expert / institution / dataset
-> Structured Epistemic State
-> Working Artifact
```

Conformant documents MUST NOT state that Claim-IR is the only allowed proposal boundary.

Conformant documents MUST NOT state that failed validation universally blocks compilation.

---

# 15. Exchange alignment

Kristal v5 uses Exchange artifacts as structured, content-addressed references.

Exchange artifacts may be:

```text
working_exchange
reference_exchange
```

Rules:

* A `working_exchange` exists before or without reference issuance. It MAY carry `artifact_status = "recognized"` when scoped authority recognition exists but explicit reference promotion has not occurred.
* A `reference_exchange` is an explicitly issued reference artifact under one or more authority channels and reader policies. On issuance it uses `artifact_status = "reference"`; a previously issued reference artifact MAY later become `deprecated`, `superseded`, or `revoked`.
* A `reference_exchange` MUST carry at least one `authority_recognition_ref`; validation evidence alone is not sufficient to establish reference status.
* An Exchange MUST preserve provenance, source references, validation references, recognition references, and scope.
* An Exchange MUST NOT be described as a truth object.
* An Exchange MUST NOT be described as universally canonical.

Recommended fields:

```json
{
  "schema_version": "5.0",
  "artifact_type": "working_exchange",
  "exchange_version": "5.0",
  "kristal_id": "sha256:<hex>",
  "artifact_status": "working",
  "source_state_refs": [],
  "scope": {},
  "authority_recognition_refs": [],
  "validation_refs": [],
  "certainty_summary": {},
  "content_hash": {},
  "build": {},
  "signatures": [],
  "extensions": {}
}
```

---

# 16. Runtime Pack alignment

A Runtime Pack is a deployable offline package derived from an Exchange or shard set.

Rules:

* Runtime Packs MUST declare their source artifact status.
* Runtime Packs MUST preserve validation, certainty, authority, scope, provenance, and lineage labels required by their query contract or reader policy.
* Runtime Packs MAY materialize full source data or filtered reader-policy views.
* Runtime Pack tables, indexes, columnar files, and profile-defined database-like query stores are derived materializations and MUST NOT become independent writable authorities.
* Materializations that affect query results MUST be bound to the declared source/build identity and reproducibility surface, and MUST be rebuildable from declared inputs.
* Core v5 does not define a general-purpose writable SQLite/application-database profile; any database-like representation requires an explicit profile and remains read-only/derived unless a future normative contract states otherwise.
* Filtered Runtime Packs MUST NOT present themselves as containing the full source artifact.
* Runtime Pack signatures prove package integrity, not universal truth.
* Runtime Pack activation is governed by activation policy, trust roots, signatures, revocation, downgrade policy, compatibility, and reader-policy requirements.

Recommended fields:

```json
{
  "schema_version": "5.0",
  "artifact_type": "runtime_pack_manifest",
  "runtime_pack_id": "sha256:<hex>",
  "runtime_pack_version": "5.0.0",
  "source_exchange_ref": {},
  "source_artifact_status": "working",
  "reader_policy_refs": [],
  "query_contract_ref": {},
  "integrity": {},
  "build": {},
  "signatures": [],
  "extensions": {}
}
```

---

# 17. Federation alignment

Federation composes Kristal shards without silently merging their authority, identity, validation, or certainty.

Rules:

* Federation preserves source identities.
* Federation does not rewrite shards.
* Federation composes references under explicit policy.
* Federation may expose disagreement.
* Federation MUST NOT silently merge conflicting claims.
* Federation MUST preserve authority-channel boundaries.
* Federation MUST preserve validation and certainty labels.
* Federation MUST expose or reference its composition policy.

Recommended composition policy fields:

```json
{
  "policy_id": "kristal.v5:composition-policy:default",
  "policy_version": "1",
  "overlap_strategy": "authority_precedence",
  "conflict_strategy": "preserve_disagreement",
  "default_visibility": "reader_policy",
  "ordering": "stable",
  "parameters": {}
}
```

Allowed `conflict_strategy` values:

```text
preserve_disagreement
authority_precedence
mark_disputed
exclude_conflict
require_reader_choice
```

Default:

```text
preserve_disagreement
```

---

# 18. Hashing and identity alignment

Kristal v5 uses content-addressed identity.

Rules:

* JSON hash targets MUST use RFC 8785 JSON Canonicalization Scheme under `kristal.v5:jcs-rfc8785`.
* The hash algorithm MUST be `sha256`.
* Hash values MUST be lowercase hexadecimal.
* Output ID fields MUST be excluded from their own hash targets.
* Signature fields MUST be excluded from content-addressed hash targets unless a profile explicitly defines a signature-bound derived hash.
* Attestation fields MUST be excluded from identity hash targets unless a profile explicitly defines otherwise.
* Timestamps MUST NOT affect content-addressed IDs unless they are part of the declared hashed material.
* Hash object fields MUST use `alg`, not `algo`.

Required hash object shape:

```json
{
  "alg": "sha256",
  "value": "<64 lowercase hex characters>"
}
```

---

# 19. Signature alignment

Kristal v5 signatures protect declared signing targets.

Rules:

* Baseline signature algorithm is `ed25519`.
* Compatibility algorithm `rsa-pss-sha256` MAY be supported by deployment policy.
* Signatures MUST declare `key_id`.
* Signatures MUST declare `alg`.
* Signatures MUST declare `payload_hash`.
* Signature verification MUST use the declared signing target.
* Signatures MUST be excluded from the signed content hash unless a profile explicitly defines a different signing target.
* A valid signature does not imply universal validation.
* A valid signature does not imply universal authority recognition.
* A valid signature does not turn a working artifact into a reference artifact.

Recommended signature object:

```json
{
  "sig_id": "sig:example",
  "key_id": "key:example",
  "alg": "ed25519",
  "payload_hash": {
    "alg": "sha256",
    "value": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "signature": "base64url-or-multibase-signature",
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

# 20. Build record alignment

A v5-aware Build Record SHOULD distinguish:

```text
compile_status
validation_status
review_status
recognition_status
publication_status
activation_status
working_outputs[]
reference_outputs[]
reason_codes[]
```

Rules:

* Compilation may succeed before validation is complete.
* Validation may fail without invalidating the existence of the working artifact.
* Recognition is separate from validation.
* Publication is separate from recognition.
* Activation is separate from publication.
* A build record MUST NOT treat all successful compilation outputs as reference outputs.
* A build record MUST NOT treat rejected recognition as failed compilation.

Recommended shape:

```json
{
  "build_id": "build:example",
  "schema_version": "5.0",
  "compile_status": "succeeded",
  "validation_status": "in_review",
  "review_status": "pending",
  "recognition_status": "none",
  "publication_status": "not_published",
  "activation_status": "not_applicable",
  "working_outputs": [],
  "reference_outputs": [],
  "reason_codes": [],
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

# 21. Reason codes

Reason codes SHOULD be stable, machine-readable strings.

Recommended values:

```text
schema_valid
schema_invalid
provenance_sufficient
provenance_insufficient
evidence_sufficient
evidence_insufficient
authority_recognized
authority_not_recognized
scope_mismatch
policy_satisfied
policy_failed
signature_valid
signature_invalid
hash_valid
hash_invalid
conflict_detected
disagreement_preserved
certainty_too_low_for_policy
rejected_by_authority_channel
revoked_by_authority_channel
unsupported_profile
unsupported_schema_version
unsupported_policy_value
unknown_authority_channel
reader_policy_excluded
```

---

# 22. Query and reader alignment

Queries MUST preserve Kristal v5 labels when the active query contract or reader policy requires them.

Queryable dimensions SHOULD include:

```text
artifact_status
assertion_status
validation_status
certainty_level
validated_as
authority_channel
recognition_status
scope.domain
scope.subdomain
reader_policy
include_disputed
include_fictional
include_mythological
```

Rules:

* Query profiles MUST use `kristal.v5:jcs-rfc8785` for query hashing when JCS is required.
* Pagination MUST use stable ordering.
* Filtered Runtime Packs MUST include filter identity in the pack identity or manifest identity surface as defined by the relevant profile.
* Query responses MUST NOT flatten scoped validation into universal truth.
* Reader policies MUST remain visible or retrievable.

---

# 23. Runtime activation alignment

Runtime activation is the process of making a Runtime Pack active for a channel, device, tenant, or environment.

Rules:

* Activation policy MUST be explicit.
* Activation MUST check required signatures, hashes, schema validity, compatibility, revocation policy, downgrade policy, and reader-policy requirements when those are declared.
* A candidate pack that does not satisfy the active policy MUST NOT become active for that policy.
* A rejected candidate MAY remain inspectable as inactive, diagnostic, or untrusted material.
* Activation MUST preserve source artifact status.
* Activation MUST NOT convert a working artifact into a reference artifact.

Preferred language:

```text
required verification
activation requirements
integrity enforcement
policy-bound activation
```

Avoid using activation language as a global epistemic claim.

---

# 24. Schema alignment requirements

All v5 schemas MUST follow these requirements:

1. `$id` MUST use `/schemas/v5/`.
2. `schema_version` MUST be `"5.0"`.
3. Titles SHOULD say `Kristal v5`.
4. Hash fields MUST use `alg`.
5. Hash values MUST use lowercase 64-character SHA-256 hex.
6. Signature fields MUST use `signatures`.
7. Signature payload hashes MUST use the common hash object shape.
8. Schema examples MUST validate against their schemas.
9. Schemas with `additionalProperties: false` MUST declare every field used in examples.
10. Registry identifiers MUST allow v5 content-addressed or registry-scoped IDs.
11. Schema text MUST distinguish artifact integrity from validation and recognition.
12. Schemas MUST NOT introduce unqualified `canonical` truth terminology.

---

# 25. Example alignment requirements

All examples in `10-examples/` MUST align with v5 vocabulary and schema rules.

Examples SHOULD include:

```text
structured-epistemic-state.example.json
plural-authority-federation.example.json
wikidata-seed-kristal.example.json
mythology-corpus-kristal.example.json
medical-authority-recognition.example.json
publisher-declared-system-kristal.example.json
independent-research-evidence-bundle.example.json
divergent-fork.example.json
reader-policy-validated-only.example.json
```

Rules:

* Examples MUST use `schema_version = "5.0"`.
* Examples MUST use v5 schema IDs where applicable.
* Examples MUST preserve labels.
* Examples MUST avoid universal truth claims.
* Examples MUST distinguish working artifacts from reference artifacts.
* Examples MUST distinguish validation from recognition.
* Examples MUST distinguish certainty from validation.
* Examples MUST show scope.
* Examples involving fiction or mythology MUST use `certainty_level = "not_applicable"` where physical-world certainty is not relevant.
* Examples involving disputed material MUST preserve disagreement.

---

# 26. Test vector alignment

Test vectors SHOULD cover:

* identity hash stability;
* exclusion of output ID fields from hash targets;
* exclusion of signatures from hash targets;
* signature verification;
* signature failure;
* hash failure;
* unsupported schema version;
* unsupported policy value;
* reader-policy filtering;
* authority-channel filtering;
* validation-status filtering;
* certainty-level filtering;
* federation conflict preservation;
* Runtime Pack filtered materialization;
* downgrade prevention;
* revocation handling.

Test vectors SHOULD include both positive and negative cases.

Negative cases SHOULD verify that nonconforming artifacts are not accepted under the requested policy, while still allowing diagnostic inspection where implementation policy permits.

---

# 27. File naming alignment

Kristal v5 file names SHOULD describe the current model directly.

Use:

```text
what-is-kristal-v5.md
vision-and-scope.md
ecosystem-integration.md
sharding-and-federation.md
plural-validation-and-federated-authority.md
validation-certainty-and-authority.md
conformance-and-alignment.md
kristal-v5-core-spec.md
structured-epistemic-state.md
assertion-status-and-certainty.md
authority-recognition.md
reader-policy-profiles.md
```

Do not use active v5 document names such as:

```text
v4-to-v5-summary.md
migration.md
upgrade.md
errata.md
```

The v5 documentation describes what Kristal v5 is, not how earlier drafts changed.

---

# 28. Component responsibility alignment

Kristal v5 stack responsibilities SHOULD remain separated.

## 28.1 Kristal

Kristal owns:

* compiled epistemic artifacts;
* content-addressed identities;
* manifests;
* schemas;
* query contracts;
* assertion status;
* certainty metadata;
* authority recognition references;
* reproducibility rules.

## 28.2 Orgo

Orgo owns:

* workflow;
* review process;
* approvals;
* operational audit;
* routing;
* release records;
* lifecycle control.

## 28.3 Konnaxion

Konnaxion owns:

* distribution;
* reader surfaces;
* Runtime Pack activation;
* offline access;
* user-facing policy selection.

## 28.4 SenTient

SenTient owns or supports:

* resolution;
* disambiguation;
* normalization;
* extraction support;
* Claim-IR profile support.

## 28.5 Architect

Architect owns or supports:

* deterministic rendering;
* label-visible summaries;
* reader-policy-aware presentation;
* prevention of hidden authority laundering.

Architect MUST NOT hide validation, authority, certainty, or disputed-status labels when they are material to the active reader policy.

---

# 29. Public language alignment

Public-facing descriptions SHOULD use language such as:

```text
Kristal makes knowledge status explicit.
Kristal preserves disagreement without silent merging.
Kristal lets readers choose policy.
Kristal separates validation from certainty.
Kristal supports plural authority channels.
Kristal protects artifact integrity.
Kristal makes source, authority, and scope inspectable.
```

Public-facing descriptions SHOULD NOT imply that Kristal guarantees:

* zero erroneous data;
* a single universal truth;
* global expert consensus;
* universal validation;
* universal recognition;
* automatic institutional approval;
* maximum certainty.

---

# 30. Conformance classes

Kristal v5 implementations MAY claim conformance at different levels.

A repository-level framework/release validation PASS is not an implementation-conformance claim. An implementation claiming one of the classes below MUST provide executable evidence for the mandatory schemas, vectors, reproducibility tests, integrity checks, and profile/integration tests applicable to that class. Documentation that describes an acceptance test is not evidence that the test has passed.

## 30.1 Schema conformant

An implementation is schema conformant if it:

* emits artifacts that validate against the relevant v5 schemas;
* uses v5 schema IDs;
* uses v5 schema versions;
* preserves required fields;
* rejects or marks unsupported schema versions.

## 30.2 Core artifact conformant

An implementation is core artifact conformant if it:

* implements v5 canonicalization and hashing rules;
* implements content-addressed identity rules;
* preserves artifact status;
* preserves assertion status and certainty labels;
* preserves validation and recognition references;
* distinguishes working and reference artifacts.

## 30.3 Runtime Pack conformant

An implementation is Runtime Pack conformant if it:

* emits Runtime Pack manifests with v5 policies;
* records required build-affecting policies;
* preserves source artifact status;
* supports declared query contracts;
* preserves labels required by reader policy;
* enforces declared activation requirements.

## 30.4 Federation conformant

An implementation is federation conformant if it:

* preserves shard identities;
* applies explicit composition policies;
* preserves disagreement;
* preserves authority-channel boundaries;
* exposes conflicts according to policy;
* avoids silent merging.

## 30.5 Authority conformant

An implementation is authority conformant if it:

* supports authority channels;
* supports scoped recognition;
* supports validation policies;
* supports revocation policy where declared;
* does not treat one authority’s recognition as universal.

## 30.6 Reader-policy conformant

An implementation is reader-policy conformant if it:

* supports declared reader modes;
* applies filters deterministically;
* exposes labels;
* does not hide scope or authority;
* clearly marks excluded or unavailable material when appropriate.

---

# 31. Nonconformance

An artifact, implementation, schema, example, or profile is nonconforming if it:

* uses v3 or v4 schema IDs in v5 files;
* uses `schema_version = "3.0"` or `"4.0"` in v5 examples unless explicitly modeling legacy interop;
* describes Exchange as a truth object;
* describes reference status as universal truth;
* uses Claim-IR as the universal required input;
* states that validation universally blocks compilation;
* collapses validation and certainty;
* collapses authority recognition and validation;
* hides scope;
* hides reader policy;
* silently merges conflicting authorities;
* omits required labels;
* uses `algo` instead of `alg`;
* includes signatures in content hash targets without a declared profile;
* allows timestamps to alter content-addressed IDs without declaring them as hashed material;
* uses fields in examples that are forbidden by `additionalProperties: false`;
* returns partial or misleading query results under a declared capability.

---

# 32. Summary

Kristal v5 conformance is not only schema validity.

A conformant Kristal v5 system preserves the distinctions that make plural, validated, uncertain, fictional, mythological, institutional, and scientific knowledge coexist without confusion.

The alignment rules are:

```text
Use v5 versions.
Use v5 schema IDs.
Preserve artifact identity.
Preserve labels.
Separate validation from certainty.
Separate recognition from validation.
Separate reader visibility from artifact existence.
Keep authority scoped.
Keep federation explicit.
Keep Runtime Pack activation policy-bound.
Use canonicalization only for stable hashing.
Do not turn scoped acceptance into universal truth.
```

The final invariant is:

> Integrity protects artifacts.
> Authority is plural.
> Recognition is scoped.
> Certainty is explicit.
> Readers choose policy.
> Federation preserves disagreement.
