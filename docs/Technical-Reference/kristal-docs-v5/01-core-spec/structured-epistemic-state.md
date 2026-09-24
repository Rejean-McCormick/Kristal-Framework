# Structured Epistemic State

## Status

Draft

## Spec

Kristal v5

## Purpose

This document defines the **Structured Epistemic State** as the primary input unit for Kristal v5.

A Structured Epistemic State is a deterministic, portable, inspectable representation of knowledge work before it becomes an Exchange, shard, federation, Runtime Pack, or recognized reference artifact.

It can contain:

* hypotheses
* claims
* sourced assertions
* reviewed assertions
* validated assertions
* disputed assertions
* rejected assertions
* fictional or mythological assertions
* institutional declarations
* technical declarations
* research material
* imported dataset statements
* authority-scoped recognition metadata

A Structured Epistemic State is not required to contain only high-certainty or fully validated material. Its role is to preserve epistemic structure: what is being asserted, by whom, from which sources, under which scope, with which status, and with which level of certainty.

## Core Principle

A Kristal may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.

A Kristal must not present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

## Definition

A **Structured Epistemic State** is a JSON-compatible artifact that groups assertions, provenance, evidence, scope, certainty metadata, validation metadata, authority references, review references, and lineage into a deterministic input for Kristal v5 compilation.

It is the preferred input boundary for Kristal v5.

It is not a workflow object, user interface object, task object, or review case. Workflow ownership belongs to Orgo. Distribution ownership belongs to Konnaxion. Rendering ownership belongs to Architect. Resolution and normalization support may be provided by SenTient. Kristal owns the artifact structure, identity, compilation semantics, and portable query contract.

## Relationship to Claim-IR

Claim-IR remains supported as an extractor proposal profile.

Claim-IR may be used when an extractor, parser, OCR system, LLM, scraper, or resolver produces proposed claims that require normalization before entering the Kristal artifact layer.

Claim-IR is not the universal required input format for Kristal v5.

Valid input paths include:

```text
LLM / OCR / parser / scraper
-> Claim-IR
-> Structured Epistemic State
-> Working Exchange
```

```text
Human expert
-> Structured Epistemic State
-> Working Exchange
```

```text
Institutional dataset
-> Structured Epistemic State
-> Working Exchange
```

```text
Wikidata-compatible corpus
-> Structured Epistemic State or Exchange-compatible source package
-> Working Exchange
```

Claim-IR should be treated as an extraction and proposal format. Structured Epistemic State is the normative Kristal v5 state format.

## Conceptual Model

A Structured Epistemic State separates:

```text
artifact existence
artifact integrity
assertion status
certainty level
validation status
authority recognition
reader visibility
```

These are independent dimensions.

A state may be structurally valid and content-addressable while containing assertions that are unresolved, low-certainty, disputed, fictional, rejected, or not yet evaluated.

A state may contain assertions that are validated at different certainty levels.

Validation does not always mean high certainty. Validation means that an assertion or artifact has been accepted as a specific kind of thing, by a specific authority channel, under a specific policy, for a specific scope.

Examples:

```text
validated as hypothesis
validated as mythological corpus
validated as publisher declaration
validated as technical specification
validated as high-confidence fact
validated as disputed position
validated as rejected claim
```

## Normative Keywords

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as described in RFC 2119 and RFC 8174 when they appear in uppercase.

## Artifact Type

The artifact type for this document is:

```text
structured_epistemic_state
```

A conforming Structured Epistemic State MUST declare:

```json
{
  "schema_version": "5.0",
  "artifact_type": "structured_epistemic_state"
}
```

## Required Top-Level Fields

A Structured Epistemic State MUST contain:

```text
schema_version
artifact_type
state_id
created_at
created_by
scope
assertions
provenance
```

A Structured Epistemic State SHOULD contain:

```text
source_refs
evidence_refs
authority_channel_refs
authority_recognition_refs
validation_refs
review_refs
policy_refs
lineage
certainty_summary
validation_summary
extensions
```

## Minimal Shape

```json
{
  "schema_version": "5.0",
  "artifact_type": "structured_epistemic_state",
  "state_id": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "created_at": "2026-01-01T00:00:00Z",
  "created_by": {
    "type": "individual",
    "id": "creator:example",
    "name": "Example Creator"
  },
  "scope": {
    "domain": "general",
    "subdomain": null,
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },
  "source_refs": [],
  "evidence_refs": [],
  "authority_channel_refs": [],
  "authority_recognition_refs": [],
  "validation_refs": [],
  "review_refs": [],
  "policy_refs": [],
  "lineage": {
    "source_artifacts": [],
    "transforms": [],
    "compiler": null,
    "policy_refs": []
  },
  "assertions": [],
  "provenance": [],
  "certainty_summary": {},
  "validation_summary": {},
  "extensions": {}
}
```

## Field Definitions

### `schema_version`

Type: string

Required value:

```text
5.0
```

Identifies the Structured Epistemic State schema version.

### `artifact_type`

Type: string

Required value:

```text
structured_epistemic_state
```

Artifact discriminator.

### `state_id`

Type: string

Recommended form:

```text
sha256:<hex>
```

The `state_id` SHOULD be content-addressed.

The `state_id` MUST NOT be included in its own hash target.

The hash target SHOULD exclude signatures and operational timestamps unless a profile explicitly declares otherwise.

### `created_at`

Type: RFC3339 date-time string

Records when this state artifact was produced.

`created_at` is operational metadata. It SHOULD NOT affect content-addressed identity unless a profile explicitly declares it part of the hash target.

### `created_by`

Type: object

Identifies the creator or producer of the state.

Allowed creator types:

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
software_agent
system_process
```

Recommended shape:

```json
{
  "type": "software_agent",
  "id": "agent:example",
  "name": "Example Extractor",
  "authority_channel_id": "authority:example-channel"
}
```

### `scope`

Type: object

Defines the domain and context of the state.

The `domain` field is required.

Recommended shape:

```json
{
  "domain": "science",
  "subdomain": "astronomy",
  "jurisdiction": null,
  "time_window": null,
  "tenant_id": null,
  "environment": null,
  "language": "en"
}
```

Allowed domain values:

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

A Structured Epistemic State SHOULD use the narrowest useful scope.

A scope MUST NOT imply global validity. Scope only defines where the state is intended to apply.

### `source_refs`

Type: array

References to source artifacts, datasets, documents, corpora, APIs, uploads, or prior Kristal artifacts.

Each source ref SHOULD include:

```text
artifact_type
id
ref
content_hash
```

Example:

```json
{
  "artifact_type": "source_document",
  "id": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "ref": "sources/source-001.pdf",
  "content_hash": {
    "alg": "sha256",
    "value": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  }
}
```

### `evidence_refs`

Type: array

References to evidence objects used by assertions.

Evidence may include documents, datasets, observations, instrument readings, citations, audit reports, prototypes, tests, or authority attestations.

Evidence references do not automatically validate an assertion. They provide material that a validation policy may evaluate.

### `authority_channel_refs`

Type: array

References to authority channels relevant to the state.

Authority channels identify who may recognize, validate, classify, or reject assertions within a declared scope.

Example:

```json
{
  "authority_channel_id": "authority:who",
  "name": "World Health Organization",
  "scope": {
    "domain": "health",
    "subdomain": "public-health",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  }
}
```

### `authority_recognition_refs`

Type: array

References to authority recognition records.

Recognition by one authority channel MUST NOT imply recognition by another authority channel.

### `validation_refs`

Type: array

References to validation reports or validation decisions.

Validation references SHOULD be scoped and SHOULD identify:

```text
target level
authority channel
validation policy
validation status
validated-as classification
certainty level
scope
```

### `review_refs`

Type: array

References to review records, review cases, audit notes, or Orgo workflow outputs.

Review is not the same as validation.

A review may support validation, but review alone does not imply recognition unless the applicable authority policy says so.

### `policy_refs`

Type: array

References to policies used to interpret, validate, compile, recognize, or read the state.

Examples:

```text
validation policy
reader policy
composition policy
runtime pack policy
authority registry policy
revocation policy
```

### `lineage`

Type: object

Records how this state relates to source material, transforms, merges, prior artifacts, and compiler behavior.

Recommended shape:

```json
{
  "source_artifacts": [],
  "transforms": [],
  "compiler": {
    "name": "kristal-compiler",
    "version": "5.0"
  },
  "policy_refs": []
}
```

Lineage is intended for traceability, not historical storytelling.

### `assertions`

Type: array

The core list of structured assertions.

Each assertion MUST have:

```text
assertion_id
statement
assertion_status
certainty_level
scope
provenance_refs
```

Each assertion SHOULD have:

```text
validated_as
validation_status
authority_channel_refs
authority_recognition_refs
evidence_refs
review_refs
policy_refs
lineage
extensions
```

### `provenance`

Type: array

Provenance records attached to source refs, assertions, evidence refs, validation refs, or state-level transformations.

Provenance SHOULD be sufficient to answer:

```text
Where did this assertion come from?
Who produced it?
When was it produced?
Which source material supports it?
Which transformations were applied?
Which authority or policy evaluated it?
```

### `certainty_summary`

Type: object

Optional summary of certainty distribution across assertions.

Example:

```json
{
  "unknown": 2,
  "speculative": 1,
  "low": 4,
  "medium": 12,
  "high": 8,
  "established": 3,
  "not_applicable": 5
}
```

### `validation_summary`

Type: object

Optional summary of validation distribution across assertions.

Example:

```json
{
  "not_evaluated": 7,
  "in_review": 3,
  "validated": 12,
  "conditionally_validated": 4,
  "disputed": 2,
  "rejected": 1,
  "revoked": 0
}
```

### `extensions`

Type: object

Implementation-specific fields.

Extensions MUST NOT change core identity, validation, certainty, authority, provenance, or compilation semantics unless a profile explicitly defines the extension as normative.

## Assertion Model

An assertion is a structured statement with metadata.

Minimal assertion shape:

```json
{
  "assertion_id": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "statement": {
    "subject": {
      "type": "entity",
      "id": "Q42"
    },
    "predicate": {
      "type": "property",
      "id": "P31"
    },
    "object": {
      "type": "entity",
      "id": "Q5"
    }
  },
  "assertion_status": "sourced",
  "certainty_level": "medium",
  "validated_as": "sourced_claim",
  "validation_status": "not_evaluated",
  "scope": {
    "domain": "wikidata",
    "subdomain": null,
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },
  "provenance_refs": [],
  "evidence_refs": [],
  "authority_channel_refs": [],
  "authority_recognition_refs": [],
  "validation_refs": [],
  "review_refs": [],
  "policy_refs": [],
  "lineage": {},
  "extensions": {}
}
```

## Statement Model

The `statement` object represents the assertion itself.

Recommended fields:

```text
subject
predicate
object
qualifiers
references
rank
```

Example:

```json
{
  "subject": {
    "type": "entity",
    "id": "Q42"
  },
  "predicate": {
    "type": "property",
    "id": "P31"
  },
  "object": {
    "type": "entity",
    "id": "Q5"
  },
  "qualifiers": [],
  "references": [],
  "rank": "normal"
}
```

The statement object MAY be compatible with Wikidata-like entity and property models, RDF-like triple models, document claims, local ontology assertions, or domain-specific structured records.

The statement object MUST be deterministic under the selected canonicalization profile.

## Assertion Status

Allowed assertion statuses:

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

### `hypothesis`

The assertion is explicitly speculative and may be useful for research, exploration, or future validation.

### `claimed`

The assertion has been made by a source or publisher but does not yet carry sufficient evidence or review metadata.

### `sourced`

The assertion has at least one source or evidence reference.

### `disputed`

The assertion is contested by at least one relevant authority channel, reviewer, or conflicting source.

### `reviewed`

The assertion has been reviewed under a declared process.

### `validated`

The assertion has been accepted under a declared validation policy, by a declared authority channel, for a declared scope.

### `rejected`

The assertion has been rejected under a declared validation policy or authority channel.

### `retracted`

The publisher or responsible authority has withdrawn the assertion.

### `superseded`

A newer assertion or artifact is intended to replace the assertion for a declared scope.

## Validation Status

Allowed validation statuses:

```text
not_evaluated
in_review
validated
conditionally_validated
disputed
rejected
revoked
```

A validation status MUST NOT be interpreted without:

```text
authority channel
validation policy
scope
validated-as value
certainty level
```

A boolean such as:

```json
{
  "validated": true
}
```

is not sufficient in Kristal v5.

## Validated-As Classification

Allowed `validated_as` values:

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

Validation answers:

```text
accepted as what?
by whom?
under which policy?
for which scope?
```

Certainty answers:

```text
how strong is the assertion within that scope?
```

## Certainty Level

Allowed certainty levels:

```text
unknown
speculative
low
medium
high
established
not_applicable
```

### `unknown`

No useful certainty estimate is available.

### `speculative`

The assertion is intentionally exploratory.

### `low`

The assertion has weak support or unresolved uncertainty.

### `medium`

The assertion has meaningful support but is not treated as high-confidence.

### `high`

The assertion is strongly supported within the declared scope.

### `established`

The assertion is stable enough to be treated as a reference-level assertion under the selected authority channel and reader policy.

### `not_applicable`

The assertion is valid in a mode where factual certainty is not the relevant measure, such as fiction, mythology, symbolic systems, publisher declarations, or technical specifications.

## Authority Channels

Authority channels are scoped.

An authority channel may recognize, validate, reject, classify, or delegate trust for a domain.

Authority recognition is not universal.

Example:

```json
{
  "authority_channel_id": "authority:example-medical-body",
  "name": "Example Medical Body",
  "authority_type": "association",
  "scope": {
    "domain": "health",
    "subdomain": "clinical-guidelines",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },
  "recognized_by": [
    "authority:example-global-reference"
  ],
  "trust_roots": [],
  "validation_policies": [],
  "revocation_policy_ref": null
}
```

Allowed authority types:

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
software_agent
system_process
```

## Reader Policy Interaction

Structured Epistemic States may contain more material than a reader chooses to display.

A reader policy determines which assertions are visible under a given context.

Reader policies may filter by:

```text
artifact status
assertion status
validation status
certainty level
validated-as value
authority channel
recognition status
scope domain
scope subdomain
disputed inclusion
fiction inclusion
mythology inclusion
```

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

“Validated-only” means all visible assertions satisfy the active reader policy.

It does not mean:

```text
all visible assertions have maximum certainty
all visible assertions are universally accepted
all authorities agree
all assertions are physical-world factual claims
```

## Compilation Semantics

A Structured Epistemic State may compile into a Working Exchange.

Compilation means that the state has been materialized into a deterministic artifact form.

Compilation does not by itself mean that all assertions are validated, recognized, high-certainty, or reference-level.

A Working Exchange may contain assertions with different statuses and certainty levels.

A Reference Exchange requires explicit validation or recognition according to the relevant authority channel, validation policy, scope, and reader policy.

## Conformance Requirements

A conforming Structured Epistemic State MUST:

1. declare `schema_version = "5.0"`;
2. declare `artifact_type = "structured_epistemic_state"`;
3. contain a deterministic `state_id`;
4. declare a scope with at least `domain`;
5. represent assertions with explicit assertion status;
6. represent certainty level explicitly;
7. preserve provenance references when available;
8. avoid representing scoped validation as universal validation;
9. avoid representing authority recognition by one channel as recognition by another;
10. remain deterministic under the declared canonicalization profile.

A conforming Structured Epistemic State SHOULD:

1. include evidence refs when assertions are sourced;
2. include validation refs when assertions have been evaluated;
3. include authority recognition refs when relevant;
4. include review refs when review occurred;
5. include policy refs for validation, reader policy, composition, or runtime use;
6. include lineage sufficient to reproduce or audit the state;
7. include summaries for validation and certainty distribution.

## Determinism Requirements

The state MUST be serializable under:

```text
kristal.v5:jcs-rfc8785
```

with canonicalization version:

```text
1
```

The hash algorithm SHOULD be:

```text
sha256
```

The content-addressed hash target SHOULD exclude:

```text
state_id
signatures
created_at
operational logs
non-deterministic runtime metadata
```

unless a profile explicitly declares otherwise.

Repeated builds from identical inputs and identical policy settings SHOULD produce identical content hashes.

## Integrity

Integrity protects artifact identity and provenance.

Integrity does not claim that every assertion is true.

A Structured Epistemic State may be integrity-valid and still contain unresolved, low-certainty, disputed, fictional, mythological, rejected, or otherwise non-reference assertions.

## Common Patterns

### Hypothesis

```json
{
  "assertion_id": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "statement": {
    "subject": {
      "type": "local_entity",
      "id": "research:prototype-x"
    },
    "predicate": {
      "type": "property",
      "id": "may_reduce_pollution"
    },
    "object": {
      "type": "boolean",
      "value": true
    }
  },
  "assertion_status": "hypothesis",
  "validation_status": "not_evaluated",
  "validated_as": "hypothesis",
  "certainty_level": "speculative",
  "scope": {
    "domain": "research",
    "subdomain": "environmental-technology",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },
  "provenance_refs": [],
  "evidence_refs": [],
  "authority_channel_refs": [],
  "authority_recognition_refs": [],
  "validation_refs": [],
  "review_refs": [],
  "policy_refs": [],
  "lineage": {},
  "extensions": {}
}
```

### Mythological Corpus Assertion

```json
{
  "assertion_id": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
  "statement": {
    "subject": {
      "type": "mythological_entity",
      "id": "example:unicorn"
    },
    "predicate": {
      "type": "property",
      "id": "has_trait"
    },
    "object": {
      "type": "text",
      "value": "horned horse-like creature"
    }
  },
  "assertion_status": "validated",
  "validation_status": "validated",
  "validated_as": "mythological_corpus",
  "certainty_level": "not_applicable",
  "scope": {
    "domain": "mythology",
    "subdomain": "example-corpus",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },
  "provenance_refs": [],
  "evidence_refs": [],
  "authority_channel_refs": [
    "authority:example-cultural-archive"
  ],
  "authority_recognition_refs": [],
  "validation_refs": [],
  "review_refs": [],
  "policy_refs": [],
  "lineage": {},
  "extensions": {}
}
```

### Publisher Declaration

```json
{
  "assertion_id": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
  "statement": {
    "subject": {
      "type": "software_system",
      "id": "vendor:system-a"
    },
    "predicate": {
      "type": "property",
      "id": "supports_feature"
    },
    "object": {
      "type": "text",
      "value": "offline query cache"
    }
  },
  "assertion_status": "validated",
  "validation_status": "validated",
  "validated_as": "publisher_declaration",
  "certainty_level": "not_applicable",
  "scope": {
    "domain": "technology",
    "subdomain": "publisher-system-description",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": "production",
    "language": "en"
  },
  "provenance_refs": [],
  "evidence_refs": [],
  "authority_channel_refs": [
    "authority:vendor"
  ],
  "authority_recognition_refs": [],
  "validation_refs": [],
  "review_refs": [],
  "policy_refs": [],
  "lineage": {},
  "extensions": {}
}
```

## Interaction With Other Kristal Artifacts

### Exchange

A Structured Epistemic State may be compiled into:

```text
working_exchange
reference_exchange
```

The output status depends on validation, recognition, and policy.

### Validation Report

A validation report may evaluate:

```text
the state as a whole
an assertion
a group of assertions
a shard
an Exchange
a Runtime Pack
```

### Authority Recognition

Authority recognition may target:

```text
artifact
shard
assertion
authority_channel
dataset
runtime_pack
```

### Runtime Pack

A Runtime Pack may be built from a Working Exchange or Reference Exchange.

The Runtime Pack MUST preserve enough metadata to determine:

```text
source artifact status
reader policy refs
validation refs
authority recognition refs
certainty labels
```

### Federation

A federation may compose shards derived from multiple Structured Epistemic States.

Federation preserves source identity and authority context. It must not silently merge disagreement.

## Security and Privacy Considerations

Structured Epistemic States may contain sensitive source references, unpublished research, personal data, institutional records, or disputed claims.

Implementations SHOULD:

* avoid leaking raw source content in logs;
* preserve source hashes instead of raw documents where possible;
* keep tenant boundaries explicit;
* avoid mixing authority scopes silently;
* preserve labels for disputed, rejected, fictional, mythological, or low-certainty assertions;
* ensure signatures and hashes protect the intended artifact target.

## Operational Notes

A Structured Epistemic State is often created before review, validation, authority recognition, or publication.

Operational systems SHOULD therefore support:

```text
partial states
draft states
working states
under-review states
validation reports
authority recognition records
reader policy filtering
revocation and replacement records
```

Operational systems SHOULD NOT assume that a compiled artifact is a reference artifact.

## Summary

Structured Epistemic State is the primary Kristal v5 state format.

It allows knowledge, hypotheses, references, myths, technical declarations, research claims, institutional corpora, and disputed forks to coexist without confusion.

Validation is scoped.

Authority is plural.

Certainty is explicit.

Readers choose policy.

Federation preserves disagreement.

Integrity protects artifacts.

## Informative example: doctrinal classification

Dogma can be represented as a corpus concept in an ordinary classification assertion. See [Dogma and doctrinal classifications](../00-overview/dogma-and-doctrinal-classification.md); this adds no core fields or enum values.
