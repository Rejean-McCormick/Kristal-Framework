# Kristal v5 Core Specification

## Status

Draft (normative core)

## Purpose

Define the minimal normative requirements for Kristal v5 conformance.

Kristal v5 is a deterministic, portable epistemic artifact system. It allows structured knowledge, hypotheses, references, technical declarations, institutional records, research claims, fictional corpora, mythological corpora, disputed positions, and validated reference material to coexist without being confused.

The core specification focuses on:

* deterministic artifact identity;
* canonical JSON serialization;
* content hashing;
* signature handling;
* structured epistemic inputs;
* working and reference artifacts;
* validation status;
* certainty metadata;
* authority recognition;
* federation;
* Runtime Pack derivation;
* reader-policy-aware query surfaces;
* cross-implementation interoperability.

Everything not explicitly required here is either:

* specified as an optional standardized profile;
* specified in a schema document;
* provided as non-normative implementation guidance;
* owned by another layer such as Orgo, Konnaxion, Architect, or SenTient.

## Scope and Non-goals

### In scope

Kristal v5 core defines:

* artifact type vocabulary;
* core content-addressed identity rules;
* JCS canonicalization requirements;
* SHA-256 hashing requirements;
* signature exclusion rules;
* minimal manifest requirements;
* distinction between Working Exchange and Reference Exchange;
* Structured Epistemic State as the normative input unit;
* Claim-IR as an optional extractor proposal profile;
* validation status and certainty metadata requirements;
* authority-recognition references;
* federation composition principles;
* Runtime Pack source-status requirements;
* reader-policy visibility requirements;
* deterministic reproducibility requirements;
* required conformance tests.

### Out of scope

Kristal v5 core does not define:

* full SPARQL semantics;
* a workflow engine;
* a review UI;
* voting systems;
* reputation systems;
* task routing;
* institutional governance process;
* legal authority;
* final truth arbitration;
* specific database engines;
* specific indexing engines;
* specific runtime performance guarantees;
* specific UI behavior beyond preservation of required labels and status metadata.

Orgo owns workflow, review process, approvals, audit, routing, operational policies, and lifecycle control.

Konnaxion owns distribution, channel policy, offline availability, runtime activation, cache management, and rollback/downgrade enforcement.

Architect owns deterministic rendering and must preserve validation, certainty, authority, and reader-policy labels.

SenTient may support extraction, reconciliation, disambiguation, normalization, and Claim-IR production, but Kristal v5 does not require all inputs to pass through SenTient.

## Normative Language

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as normative requirements.

## Core Definition

Kristal v5 is a deterministic, portable epistemic artifact system.

It supports the following invariant:

> A Kristal may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.
>
> A Kristal must not present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

Kristal v5 separates:

```text
artifact existence
≠ artifact integrity
≠ assertion validity
≠ certainty
≠ authority recognition
≠ reader visibility
```

A technically valid artifact may contain weak, speculative, disputed, fictional, or false assertions. The core requirement is that status, certainty, provenance, scope, and authority recognition remain explicit and machine-readable.

## Global Constants

Kristal v5 core uses the following default constants unless a specific profile declares otherwise:

```text
SPEC_NAME = "Kristal v5"
SPEC_VERSION = "5.0"
SCHEMA_BASE_URL = "https://kristal.org/schemas/v5/"
CANONICALIZATION_PROFILE = "kristal.v5:jcs-rfc8785"
CANONICALIZATION_VERSION = "1"
HASH_ALG = "sha256"
DEFAULT_SIGNATURE_ALG = "ed25519"
```

Schemas for core artifacts SHOULD use:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://kristal.org/schemas/v5/<schema-name>.schema.json",
  "schema_version": "5.0"
}
```

## Artifact Types

Kristal v5 core recognizes the following artifact types:

```text
structured_epistemic_state
claim_ir
working_exchange
reference_exchange
runtime_pack_manifest
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

Implementations MAY define additional artifact types through explicit profiles, but they MUST NOT redefine the semantics of the core artifact types.

## Artifact Status

Every compiled Exchange or derived artifact MUST declare a machine-readable artifact status.

Core artifact statuses are:

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

Status meanings:

* `draft`: incomplete or pre-compilation material.
* `working`: compiled and usable under policy, but not recognized as reference material.
* `under_review`: submitted to a review or validation process.
* `recognized`: accepted by at least one authority channel under a declared scope and policy.
* `reference`: recognized as reference material under one or more declared authority channels.
* `deprecated`: retained for history or compatibility, but no longer recommended.
* `superseded`: replaced by another artifact.
* `revoked`: explicitly invalidated by an authority, publisher, or policy process.

Implementations MUST NOT infer `reference` status only by convention. It MUST be declared.

## Structured Epistemic State

Structured Epistemic State is the normative input unit for Kristal v5 compilation.

A Structured Epistemic State represents a bounded, structured body of assertions, provenance, evidence, scope, certainty metadata, and policy references that can be compiled into a Working Exchange.

A minimal Structured Epistemic State SHOULD contain:

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

A Structured Epistemic State MAY be produced by:

* a human expert;
* an institution;
* an editor;
* a research collective;
* a dataset import process;
* an LLM-assisted extractor;
* an OCR pipeline;
* a parser;
* a scraper;
* a reconciliation system;
* a collaborative review process.

## Claim-IR Role

Claim-IR is retained in Kristal v5 as an extractor proposal profile.

Claim-IR MAY be used by extraction systems that propose claims from raw or semi-structured material.

Claim-IR MUST NOT be required as the universal input format for Kristal v5.

Valid pathways include:

```text
LLM / OCR / parser / scraper -> Claim-IR -> Structured Epistemic State
```

and:

```text
human expert -> Structured Epistemic State
institutional dataset -> Structured Epistemic State
Wikidata seed corpus -> Structured Epistemic State or Exchange-compatible corpus
```

Claim-IR artifacts MUST NOT imply validation, authority recognition, reference status, or high certainty.

## Assertions

An assertion is a structured claim about a subject, predicate, object, relation, source, classification, or status.

A minimal assertion SHOULD include:

```json
{
  "assertion_id": "sha256:<hex>",
  "statement": {},
  "assertion_status": "sourced",
  "certainty_level": "medium",
  "validated_as": "sourced_claim",
  "scope": {},
  "provenance_refs": [],
  "evidence_refs": [],
  "authority_recognition_refs": [],
  "lineage": {}
}
```

Assertions MAY be true, false, speculative, fictional, mythological, disputed, reviewed, rejected, or validated under a declared authority channel and scope.

Assertions MUST preserve enough metadata for readers and systems to determine:

* what is asserted;
* who asserted it;
* what evidence supports it;
* what certainty level is declared;
* what validation status applies;
* which authority channels recognize or reject it;
* which scope governs the assertion.

## Assertion Status

Core assertion statuses are:

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

Status meanings:

* `hypothesis`: proposed idea or possible claim.
* `claimed`: asserted by a publisher or source.
* `sourced`: linked to evidence, citation, dataset, observation, or document.
* `disputed`: contested by at least one declared source, channel, or policy.
* `reviewed`: inspected under a declared review process.
* `validated`: accepted under a declared validation policy and authority channel.
* `rejected`: rejected under a declared validation policy or authority channel.
* `retracted`: withdrawn by its publisher or authority.
* `superseded`: replaced by a later assertion.

The value `validated` MUST NOT be used alone to imply universal truth.

A validated assertion MUST declare, directly or by reference:

* `validated_as`;
* `authority_channel`;
* `scope`;
* `validation_policy_ref`;
* `certainty_level`.

## Certainty Levels

Core certainty levels are:

```text
unknown
speculative
low
medium
high
established
not_applicable
```

Certainty meanings:

* `unknown`: no usable certainty assessment is available.
* `speculative`: exploratory or hypothetical.
* `low`: weak support or limited evidence.
* `medium`: supported but not settled.
* `high`: strong support within the declared scope.
* `established`: accepted as stable reference material under the active authority channel and scope.
* `not_applicable`: certainty is not a factual-world scale for this assertion, such as fiction, mythology, symbolic models, or publisher declarations.

Validation and certainty are separate.

Validation answers:

```text
Who accepts this status, under which rules, for which scope?
```

Certainty answers:

```text
How strong is the assertion within that scope?
```

## Validated-as Values

Core `validated_as` values are:

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

Examples:

* A hypothesis may be validated as a hypothesis.
* A mythological corpus may be validated as mythology.
* A fictional world may be validated as fiction.
* A company may validate a technical description as its publisher declaration.
* A health authority may validate a medical assertion as a high-confidence fact within its scope.
* A standards body may validate a technical specification.

## Scope

Every assertion, validation decision, authority recognition, federation rule, and reader policy SHOULD be scoped.

A standard scope object is:

```json
{
  "domain": "string",
  "subdomain": "string|null",
  "jurisdiction": "string|null",
  "time_window": "string|null",
  "tenant_id": "string|null",
  "environment": "string|null",
  "language": "string|null"
}
```

`domain` is required where scope is required.

Core domain values SHOULD include:

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

Profiles MAY add domain-specific vocabularies.

## Exchange

An Exchange is a structured Kristal artifact compiled from one or more Structured Epistemic States, datasets, shards, or source artifacts.

There are two core Exchange statuses:

```text
working_exchange
reference_exchange
```

A Working Exchange is compiled, structured, queryable, and reproducible, but not necessarily recognized as reference material.

A Working Exchange MAY have `artifact_status = "recognized"` when one or more authority channels recognize the artifact but it has not been issued as a Reference Exchange. Recognition alone does not change `artifact_type`; promotion to a Reference Exchange is an explicit lifecycle action.

A Reference Exchange is a Working Exchange or equivalent compiled artifact that has been recognized by one or more authority channels under declared validation policies and scopes.

A minimal Exchange SHOULD include:

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

An Exchange MUST NOT be described as a universal truth object.

An Exchange MAY be a structured reference, a working artifact, a research artifact, a cultural artifact, an institutional artifact, or a reference artifact depending on its status, scope, authority recognition, and reader policy.

## Reference Exchange

A Reference Exchange MUST declare:

* `artifact_type = "reference_exchange"`;
* `artifact_status = "reference"` when issued as a current reference artifact; a previously issued Reference Exchange MAY later carry `deprecated`, `superseded`, or `revoked` lifecycle status without ceasing to be identifiable as a `reference_exchange`;
* at least one `authority_recognition_ref`;
* the scope of recognition;
* the validation or recognition policy used;
* the source Working Exchange or source state lineage.

Reference status is scoped.

Recognition by one authority channel MUST NOT imply recognition by another authority channel unless an explicit authority-recognition record says so.

## Runtime Pack

A Runtime Pack is a derived offline-usable package produced from an Exchange.

A Runtime Pack MUST declare:

* its source Exchange reference;
* whether the source is a Working Exchange or Reference Exchange;
* its query contract;
* its packaging policies;
* its content hash;
* its build information;
* its signatures, if present;
* its reader-policy references, if applicable.

A minimal Runtime Pack manifest SHOULD include:

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

A Runtime Pack derived from a Working Exchange MUST NOT be treated as equivalent to a Runtime Pack derived from a Reference Exchange unless a reader policy explicitly allows that equivalence.

Runtime Pack possession does not imply authorization to use it.

Runtime Pack integrity does not imply epistemic validation.

## Authority Channel

An authority channel is a scoped authority context that may recognize, validate, reject, dispute, deprecate, or revoke artifacts, shards, assertions, Runtime Packs, datasets, or other authority channels.

A minimal authority channel SHOULD include:

```json
{
  "authority_channel_id": "authority:<slug>",
  "name": "string",
  "authority_type": "institution",
  "scope": {},
  "recognized_by": [],
  "trust_roots": [],
  "validation_policies": [],
  "revocation_policy_ref": null
}
```

Core authority types are:

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

No authority channel has universal monopoly over all Kristal truth.

Authority recognition is scoped.

Authorities MAY recognize other authorities.

Recognition by one authority channel MUST NOT imply recognition by another.

## Authority Recognition

Authority recognition declares that an authority channel accepts a target under a declared scope and policy.

A minimal authority-recognition artifact SHOULD include:

```json
{
  "recognition_id": "sha256:<hex>",
  "artifact_type": "authority_recognition",
  "issuer_authority_channel": "authority:<slug>",
  "target_ref": {},
  "target_level": "artifact",
  "recognition_status": "recognized",
  "recognized_as": "institutional_reference",
  "scope": {},
  "validation_policy_ref": {},
  "reason_codes": [],
  "evidence_refs": [],
  "created_at": "RFC3339",
  "expires_at": null,
  "signatures": []
}
```

Core recognition statuses are:

```text
recognized
conditionally_recognized
under_review
disputed
rejected
deprecated
revoked
```

Authority recognition MUST NOT be collapsed into a boolean.

The following is insufficient:

```json
{
  "recognized": true
}
```

## Validation Decision

A validation decision records the result of applying a validation policy to a target.

A minimal validation decision SHOULD include:

```json
{
  "validation_decision_id": "sha256:<hex>",
  "artifact_type": "validation_decision",
  "target_ref": {},
  "target_level": "artifact",
  "validation_status": "validated",
  "validated_as": "high_confidence_fact",
  "certainty_level": "high",
  "authority_channel": "authority:<slug>",
  "validation_policy_ref": {},
  "scope": {},
  "findings": [],
  "reason_codes": [],
  "created_at": "RFC3339",
  "signatures": []
}
```

Core validation statuses are:

```text
not_evaluated
in_review
validated
conditionally_validated
disputed
rejected
revoked
```

Validation MAY affect:

* reference status;
* publication eligibility;
* reader visibility;
* authority recognition;
* Runtime Pack activation policy;
* warning labels;
* query filtering.

Validation MUST NOT be treated as a universal compile blocker.

Compilation may produce a Working Exchange even when validation has not occurred, is incomplete, is disputed, or is rejected for reference use.

## Reader Policy

A reader policy determines which artifacts, assertions, validation statuses, certainty levels, authority channels, and scopes are visible or usable in a reading surface.

A minimal reader policy SHOULD include:

```json
{
  "reader_policy_id": "reader_policy:<slug>",
  "mode": "validated_only",
  "allowed_authority_channels": [],
  "allowed_validation_statuses": [],
  "allowed_certainty_levels": [],
  "allowed_validated_as": [],
  "include_disputed": false,
  "include_fictional": false,
  "include_mythological": false,
  "show_labels": true,
  "fallback_behavior": "show_unavailable"
}
```

Core reader modes are:

```text
reference_only
validated_only
high_certainty_only
research
creative
all_with_labels
custom
```

A reader policy MAY allow users or applications to use only validated material.

“Validated-only” means all visible assertions satisfy the active reader policy. It does not mean:

* all visible assertions have maximum certainty;
* all visible assertions are universally true;
* all authority channels agree;
* all assertions are factual-world claims.

Reader surfaces MUST preserve labels for validation, certainty, authority, scope, and dispute status.

## Federation

Federation composes multiple Kristal artifacts, shards, authority channels, scopes, or datasets without silently merging their authority, provenance, or disagreement.

A federation manifest SHOULD include:

```json
{
  "schema_version": "5.0",
  "artifact_type": "exchange_federation_manifest",
  "federation_id": "sha256:<hex>",
  "created_at": "RFC3339",
  "authority_registry_ref": {},
  "shards": [],
  "composition_policy": {},
  "reader_policy_refs": [],
  "publisher": {},
  "content_hash": {},
  "signatures": [],
  "extensions": {}
}
```

Federation MUST preserve source identities.

Federation MUST NOT rewrite shard identities.

Federation MUST declare composition policy.

Federation MUST preserve disagreement unless an explicit reader policy, authority policy, or composition profile declares otherwise.

Default v5 conflict strategy SHOULD be:

```text
preserve_disagreement
```

## Composition Policy

A composition policy defines how overlapping shards, assertions, scopes, or authority channels are presented.

A minimal composition policy SHOULD include:

```json
{
  "policy_id": "kristal.v5:composition-policy:<slug>",
  "policy_version": "1",
  "overlap_strategy": "authority_precedence",
  "conflict_strategy": "preserve_disagreement",
  "default_visibility": "reader_policy",
  "ordering": "stable",
  "parameters": {}
}
```

Core overlap strategies are:

```text
authority_precedence
latest_time_window
explicit_allow_deny
preserve_all
reader_policy_selected
```

Core conflict strategies are:

```text
preserve_disagreement
authority_precedence
mark_disputed
exclude_conflict
require_reader_choice
```

Composition MUST NOT make one authority appear to speak for another.

## Canonical JSON

Kristal v5 core uses RFC 8785 JSON Canonicalization Scheme for JSON content-addressed identity.

Artifacts and manifests that declare content hashes MUST declare:

```text
canonicalization_profile = "kristal.v5:jcs-rfc8785"
canonicalization_version = "1"
```

Where a profile uses a different canonicalization surface, that profile MUST declare its canonicalization method, version, and hash target.

The term canonicalization in Kristal v5 refers only to deterministic byte representation for hashing and signing. It does not imply canonical truth.

## Content Hashing

Core JSON content hashes MUST use SHA-256 over canonicalized JSON bytes.

The standard hash object shape is:

```json
{
  "alg": "sha256",
  "value": "<64 lowercase hex characters>"
}
```

Implementations MUST use `alg`, not `algo`.

For content-addressed IDs, implementations SHOULD use:

```text
sha256:<hex>
```

Examples:

```text
kristal_id = "sha256:<hex>"
state_id = "sha256:<hex>"
assertion_id = "sha256:<hex>"
shard_id = "sha256:<hex>"
federation_id = "sha256:<hex>"
runtime_pack_id = "sha256:<hex>"
validation_decision_id = "sha256:<hex>"
recognition_id = "sha256:<hex>"
```

Policy artifacts MAY use richer namespaced identifiers if their schemas explicitly allow them.

## Hash Target Rules

Each artifact schema or profile MUST define its hash target.

Unless explicitly stated otherwise, the hash target excludes:

* signatures;
* detached signatures;
* proofs;
* tenant-local access-control metadata;
* workflow state;
* approval queues;
* distribution state;
* runtime activation state;
* local cache state;
* reader session state;
* transient UI state.

The hash target MAY include validation references, certainty summaries, authority recognition references, or reader-policy references when the artifact schema declares them part of the artifact content boundary.

The hash target MUST be test-vectorized for core artifacts.

## Signature Rules

If an artifact or manifest includes signatures, signatures MUST be placed in a clearly separated signature envelope.

The default signature location is:

```json
{
  "signatures": []
}
```

The minimal signature object is:

```json
{
  "key_id": "string",
  "alg": "ed25519",
  "signature": "string",
  "created_at": "RFC3339"
}
```

The signing and verification workflow is:

```text
remove signature material
canonicalize declared hash target
hash canonical bytes
verify or attach signature
```

A valid signature verifies artifact integrity and signer identity under the relevant trust roots.

A valid signature does not imply:

* authority recognition;
* validation;
* high certainty;
* universal truth;
* reader-policy visibility.

## Integrity Verification

If an artifact or manifest declares content hashes, signatures, signer identity, key references, or integrity material, verifiers MUST check the declared integrity material before accepting the artifact under any policy that requires it.

If declared integrity material is malformed, incomplete, ambiguous, unsupported, or mismatched, the verifier MUST report a structured verification issue.

If the active policy requires the integrity material, the artifact MUST NOT be accepted under that policy.

Recommended verification statuses are:

```text
verified
verification_failed
verification_not_possible
algorithm_unsupported
hash_mismatch
signature_invalid
signature_missing
malformed_integrity_material
```

This is a policy outcome about artifact acceptance. It is not a statement about the factual truth or falsity of the assertions inside the artifact.

## Build Records

A v5-aware build record SHOULD distinguish:

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
created_at
```

Recommended build status values:

```json
{
  "compile_status": "succeeded",
  "validation_status": "not_evaluated",
  "review_status": "not_required",
  "recognition_status": "none",
  "publication_status": "not_published",
  "activation_status": "not_applicable",
  "working_outputs": [],
  "reference_outputs": [],
  "reason_codes": [],
  "created_at": "RFC3339"
}
```

Compilation success MUST NOT imply validation success.

Validation success MUST NOT imply authority recognition unless a recognition artifact is present.

Authority recognition MUST NOT imply universal truth.

Runtime activation MUST remain governed by the active tenant, channel, integrity, compatibility, and reader policies.

## Determinism and Reproducibility

Kristal v5 requires deterministic compilation within the declared reproducibility surface.

A reproducibility surface SHOULD declare:

* source artifact references;
* source snapshots;
* compiler name;
* compiler version;
* compiler configuration hash;
* schema versions;
* canonicalization profile;
* canonicalization version;
* policy selections;
* ordering rules;
* normalization rules;
* profile activation;
* extension activation;
* build environment constraints when relevant.

Given identical inputs and identical declared policy selections, implementations MUST reproduce:

* the same content hashes;
* the same content-addressed IDs;
* the same deterministic exports;
* the same Runtime Pack outputs where portable policies are identical.

If two builds differ because policy selections differ, that difference MUST be declared in the manifests.

## Query Semantics

Runtime-capable Kristal artifacts MUST expose or reference a constrained query contract.

At minimum, query-capable artifacts SHOULD support filtering or exposing:

```text
artifact_status
assertion_status
certainty_level
validated_as
validation_status
authority_channel
recognition_status
scope.domain
scope.subdomain
reader_policy
include_disputed
include_fictional
include_mythological
```

Query results MUST preserve enough metadata for the reader to know:

* what artifact supplied the result;
* what assertion status applies;
* what certainty level applies;
* which authority channels recognize the result;
* what reader policy allowed the result to appear;
* whether disagreement or dispute exists.

Query surfaces MUST NOT silently flatten scoped validation into universal truth.

## Profiles and Extensions

Optional capabilities MUST be specified as explicit profiles.

If a profile is enabled or claimed:

* it MUST be declared in manifests;
* it MUST be testable;
* it MUST NOT redefine core identity semantics;
* it MUST NOT redefine validation as universal truth;
* it MUST NOT hide authority, certainty, scope, or reader-policy metadata required by core.

Core standardized profile categories include:

* RDF WDQS export;
* RDF integrity using RDFC;
* JSON-LD export;
* Provenance using Nanopub and PROV-O;
* SHACL validation;
* ShEx validation;
* TPF-like query pagination;
* transparency logs;
* reader policy profiles.

## RDF Exports

If an implementation supports RDF exports, the export MUST be deterministic under its declared export profile.

RDF exports MAY support:

* full statements;
* truthy or best-rank projections;
* named graphs;
* references;
* qualifiers;
* ranks;
* provenance graphs;
* authority recognition graphs;
* validation-decision graphs;
* certainty metadata.

RDF export integrity is not core identity. RDF-level hashing belongs to the RDF Integrity profile.

RDF export integrity does not imply epistemic validation.

## Wikidata-Compatible Seed Corpora

A Wikidata-compatible Kristal seed corpus SHOULD preserve as much source structure as possible, including:

* entities;
* properties;
* statements;
* qualifiers;
* references;
* ranks;
* labels;
* aliases;
* descriptions;
* source identifiers.

A Wikidata-compatible seed MUST NOT collapse full statement structure into only a truthy view unless the artifact explicitly declares that reduced projection as its content boundary.

The recommended language is:

```text
Kristal-compatible packaging or alignment of the Wikidata corpus.
```

Implementations SHOULD NOT describe this as a transformation of truth.

## Multi-tenancy

Kristal v5 separates global content identity from tenant access control.

Tenant identifiers, ACLs, approvals, workflow state, distribution state, and runtime activation state MUST NOT influence global content IDs unless a tenant-scoped artifact profile explicitly declares them inside the content boundary.

Tenant isolation SHOULD be enforced by:

* access control;
* tenant-scoped artifact handles;
* signing domains;
* trust roots;
* distribution channels;
* reader policies;
* Runtime Pack activation policies;
* tenant-scoped logs.

The same content MAY produce the same global content ID across tenants.

Different tenants MAY sign the same content with different keys.

Different tenants MAY recognize, reject, hide, or expose the same content differently.

## Security and Trust

Kristal v5 protects artifact integrity and makes epistemic status explicit.

It does not guarantee that all contained assertions are true.

Implementations MUST preserve the distinction between:

* valid artifact;
* valid signature;
* recognized artifact;
* validated assertion;
* high-certainty assertion;
* visible result under reader policy.

Security controls SHOULD prevent:

* authority laundering;
* hidden downgrade or rollback;
* cross-tenant leakage;
* cross-channel cache confusion;
* signature trust-root confusion;
* silent merging of disagreements;
* presentation of fictional, mythological, or disputed claims as factual-world reference material.

## Authority Laundering

Authority laundering occurs when a claim, artifact, shard, or Runtime Pack recognized under one authority channel is presented as if it were recognized by another authority channel.

Implementations MUST NOT launder authority.

Reader surfaces MUST preserve:

* issuer authority channel;
* recognition status;
* validation policy;
* scope;
* certainty level;
* dispute status;
* rejection status where relevant.

## Fiction, Mythology, Symbolic Models, and Creative Corpora

A mythology or fiction Kristal MAY be valid as mythology or fiction.

It MUST NOT be represented as validated physical-world truth unless an authority channel explicitly validates that epistemic mode.

Examples:

```text
validated_as = "mythological_corpus"
certainty_level = "not_applicable"
scope.domain = "mythology"
```

```text
validated_as = "fictional_corpus"
certainty_level = "not_applicable"
scope.domain = "fiction"
```

Such artifacts MAY be first-class Kristals and MAY be queryable, federated, cited, versioned, and preserved.

## Divergent Forks

Divergent forks are allowed.

A divergent fork MUST preserve lineage.

A divergent fork MUST declare its publisher or authority channel where available.

A divergent fork MUST declare scope.

A divergent fork MUST NOT inherit recognition from its source unless explicitly recognized by the relevant authority channel.

Federation SHOULD preserve divergent views rather than silently rewriting them.

## Revocation and Supersession

Kristal v5 artifacts MAY be revoked, deprecated, or superseded.

Revocation records SHOULD declare:

* target reference;
* target level;
* issuing authority or publisher;
* scope;
* reason codes;
* evidence references;
* created timestamp;
* signatures.

Revocation of an artifact under one authority channel MUST NOT imply universal revocation unless recognized by the active reader policy or authority channel.

Supersession SHOULD preserve lineage to the superseded artifact.

## Forward Compatibility

Readers MUST ignore unknown non-integrity fields unless the active profile declares them required.

Readers MUST NOT ignore malformed or mismatched declared integrity material when the active policy requires integrity verification.

Writers SHOULD avoid breaking schema changes. If breaking changes are unavoidable, writers MUST bump schema version and declare profile compatibility.

Unknown artifact types MAY be retained and displayed as unsupported, but MUST NOT be presented as validated or recognized unless the relevant status can be verified.

## Conformance

An implementation is Kristal v5 Core Conformant if it:

1. Implements JCS canonicalization for core JSON artifacts.
2. Implements SHA-256 content hashing for core content-addressed IDs.
3. Excludes signatures from content hash targets.
4. Uses `schema_version = "5.0"` for v5 core artifacts.
5. Uses `canonicalization_profile = "kristal.v5:jcs-rfc8785"` where applicable.
6. Supports Structured Epistemic State as a normative input unit.
7. Treats Claim-IR as an optional extractor proposal profile.
8. Distinguishes Working Exchange from Reference Exchange.
9. Preserves artifact status, assertion status, certainty level, validation status, authority recognition, and reader-policy metadata.
10. Does not treat validation as a universal compile blocker.
11. Does not treat a valid artifact or valid signature as universal truth.
12. Supports deterministic reproducibility within declared reproducibility surfaces.
13. Preserves federation source identities and disagreement.
14. Supports Runtime Pack manifests with source artifact status.
15. Passes required JCS and hashing test vectors.
16. Reports structured issues for integrity, validation, recognition, and policy failures.
17. Does not present scoped recognition as universal recognition.
18. Does not hide fictional, mythological, disputed, rejected, or low-certainty status where that status is known.

## Required Test Vectors

A conformant implementation MUST ship or reference test vectors for:

* JCS canonicalization;
* SHA-256 content hashing;
* signature exclusion;
* tenant metadata exclusion;
* artifact status preservation;
* assertion status preservation;
* certainty level preservation;
* authority recognition references;
* validation decision references;
* federation disagreement preservation;
* Runtime Pack source-status declaration;
* reader-policy filtering.

If an implementation fails the core canonicalization or hashing vectors, its content-addressed IDs are not interoperable.

## Non-conformance

An implementation is not Kristal v5 Core Conformant if it:

* computes content IDs from non-canonical JSON;
* includes signatures in content hashes;
* changes global content IDs based on tenant-local metadata;
* requires Claim-IR as the only possible input;
* prevents all compilation before validation;
* presents Working Exchange as Reference Exchange without recognition;
* collapses validation into universal truth;
* hides certainty level or authority scope;
* silently merges conflicting authority channels;
* hides dispute status where known;
* ignores required integrity failures under an active policy;
* presents Runtime Packs from Working Exchanges as equivalent to Reference Exchange Runtime Packs without policy declaration.

## Minimal Core File Set

The Kristal v5 core expects the following related files to exist:

```text
01-core-spec/ids-canonicalization-hashing.md
01-core-spec/signatures-trust.md
01-core-spec/structured-epistemic-state.md
01-core-spec/assertion-status-and-certainty.md
01-core-spec/authority-recognition.md

02-schemas/structured-epistemic-state.schema.json
02-schemas/assertion-status.schema.json
02-schemas/authority-recognition.schema.json
02-schemas/claim-ir.schema.json
02-schemas/exchange-manifest.schema.json
02-schemas/exchange-shard-manifest.schema.json
02-schemas/exchange-federation-manifest.schema.json
02-schemas/runtime-pack-manifest.schema.json
02-schemas/validation-report.schema.json
02-schemas/reader-policy.schema.json

04-query/query-contract.md
04-query/reader-policy-profiles.md

09-test-vectors/jcs/README.md
09-test-vectors/jcs/vectors.json
09-test-vectors/jcs/expected-hashes.txt
```

## Summary

Kristal v5 core defines portable epistemic artifacts with deterministic identity, explicit status, scoped validation, plural authority, queryable certainty, and reader-policy-aware visibility.

The core invariant is:

```text
A Kristal may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.

A Kristal must not present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.
```

Kristal v5 therefore provides:

```text
deterministic identity
+ structured epistemic state
+ working artifacts
+ reference artifacts
+ scoped validation
+ explicit certainty
+ plural authority recognition
+ federation without silent merging
+ reader-policy visibility
+ reproducible runtime packaging
```

The result is not a universal truth machine.

It is a structured, portable, verifiable artifact system for knowledge whose status remains explicit.
