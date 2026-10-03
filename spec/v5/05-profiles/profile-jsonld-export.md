# 05-profiles/profile-jsonld-export.md

# JSON-LD export profile

## Status

Draft (v5 profile)

## Purpose

This document defines the **JSON-LD 1.1 export profile** for Kristal v5.

Goals:

* Provide a **deterministic**, **portable**, and **Wikibase-aligned** JSON-LD representation of Kristal Exchange content.
* Ensure exporters across languages and toolchains produce **byte-stable output** given the same source artifact and export policy.
* Define clear boundaries between:

  * Kristal Exchange payloads as structured reference artifacts; and
  * JSON-LD export artifacts as derived interoperability projections.

This profile is optional, but if enabled, it is conformance-testable.

JSON-LD export does not decide validation, certainty, authority recognition, or reader visibility. It serializes selected Kristal content into an interoperable JSON-LD representation while preserving the relevant identifiers, provenance, status, and scope metadata.

---

## 1. Scope and non-goals

### 1.1 In scope

This profile defines:

* Deterministic JSON-LD 1.1 structure for exporting claims, assertions, statements, and related metadata from a Kristal Exchange.
* Stable `@context` and `@type` usage to enable consistent RDF interpretation.
* Deterministic ordering rules so the export is byte-stable.
* Rules for encoding:

  * entities;
  * properties;
  * literals;
  * datatypes;
  * language tags;
  * qualifiers;
  * references;
  * evidence pointers;
  * ranks, where present;
  * assertion status;
  * certainty level;
  * validation references;
  * authority recognition references;
  * scope metadata;
  * full or best-rank projections.

### 1.2 Out of scope

This profile does not define:

* the Kristal Exchange schema itself;
* Structured Epistemic State schema;
* validation policy semantics;
* authority recognition semantics;
* reader policy selection;
* Runtime Pack query behavior;
* RDF Dataset Canonicalization;
* RDF-level hashing;
* which claims should be accepted as true.

RDF dataset canonicalization and RDF hashing are handled by:

```text
05-profiles/profile-rdf-integrity-rdfc.md
```

---

## 2. Profile identification

If JSON-LD export is produced, the exporter MUST declare:

```text
export_profile_id = "kristal.v5:jsonld-1.1"
export_profile_version = "1"
```

The export metadata MUST also record:

* `schema_version = "5.0"`;
* the source artifact reference;
* the source artifact type;
* the `kristal_id` of the source Exchange, when exporting from an Exchange;
* the `state_id`, when exporting from a Structured Epistemic State profile that explicitly permits export;
* the `canonicalization_profile` used by the source artifact;
* the `canonicalization_version` used by the source artifact;
* the export projection;
* the statement model;
* the export policy or reader policy used, if any filtering was applied.

Recommended metadata shape:

```json
{
  "schema_version": "5.0",
  "artifact_type": "jsonld_export",
  "export_profile_id": "kristal.v5:jsonld-1.1",
  "export_profile_version": "1",
  "source_artifact": {
    "artifact_type": "reference_exchange",
    "kristal_id": "sha256:<hex>",
    "uri": "https://example.org/kristals/<id>"
  },
  "source_canonicalization": {
    "canonicalization_profile": "kristal.v5:jcs-rfc8785",
    "canonicalization_version": "1"
  },
  "statement_model": "wikibase-aligned",
  "projection": "full"
}
```

---

## 3. Export source

### 3.1 Supported source artifacts

A JSON-LD export MAY be produced from:

* `working_exchange`;
* `reference_exchange`;
* another Exchange-compatible artifact explicitly allowed by profile.

A JSON-LD export SHOULD NOT be produced directly from an arbitrary raw source, draft, scraper output, or unstructured dataset unless that source has first been represented as a Kristal v5 artifact.

### 3.2 Source status preservation

Exporters MUST preserve source status metadata when present and selected by export policy.

Relevant metadata includes:

* `artifact_status`;
* `assertion_status`;
* `certainty_level`;
* `validated_as`;
* `validation_refs`;
* `authority_recognition_refs`;
* `scope`;
* `provenance_refs`;
* `evidence_refs`;
* `lineage`.

Exporting to JSON-LD MUST NOT flatten scoped validation into universal truth.

### 3.3 Derived artifact boundary

A JSON-LD export is a derived artifact.

It MAY have its own export ID, content hash, signature, or publication record.

Those fields identify the export artifact itself. They do not replace the identity of the source Exchange.

---

## 4. Determinism requirements

### 4.1 Byte-stable export

Given identical source artifact content, export policy, reader policy, profile version, context version, and projection settings, two implementations MUST output identical JSON bytes after applying:

* the serialization rules declared for export artifacts;
* the deterministic ordering rules in this profile.

The recommended serialization method for byte-stable JSON-LD export artifacts is RFC 8785 JCS.

### 4.2 Export canonicalization metadata

If the JSON-LD export artifact itself is content-addressed, signed, or tested for byte stability, it MUST record:

```json
{
  "canonicalization_profile": "kristal.v5:jcs-rfc8785",
  "canonicalization_version": "1"
}
```

This describes the export artifact’s serialization profile, not necessarily the source Exchange’s own content hash target.

### 4.3 Ordering rules

Where arrays represent conceptually unordered sets, they MUST be sorted deterministically.

Minimum required ordering:

* entities: by entity ID or `@id`, lexicographically;
* assertions/statements: by `assertion_id` if present;
* source-system statements: by `statement_id` if present and `assertion_id` is absent;
* fallback statement ordering: by `(subject, property, value, qualifiers_hash, references_hash)`;
* qualifiers: by `(property, value)` lexicographically;
* references and evidence pointers: by stable `evidence_id`, `reference_id`, or equivalent;
* validation references: by referenced ID lexicographically;
* authority recognition references: by referenced ID lexicographically;
* language maps: by language code lexicographically;
* graph nodes: by `@id` lexicographically when `@id` exists.

No field MAY be emitted in an implementation-dependent order.

### 4.4 Normalization rules

Exporters MUST preserve normalized values present in the source artifact.

Exporters MUST NOT:

* re-normalize numbers or dates during export;
* coerce datatypes beyond what is declared in the source artifact;
* resolve unresolved ambiguity by guessing;
* hide assertion status, certainty level, or authority scope when those fields are selected for export;
* silently discard references or evidence pointers needed to preserve meaning.

If an export policy intentionally excludes metadata, the policy MUST be declared.

---

## 5. JSON-LD document structure

### 5.1 Top-level document shape

The export MUST be a JSON-LD document with:

* `@context`; and
* one of:

  * `@graph`; or
  * a top-level node array, if explicitly declared by profile extension.

The recommended v5 shape is:

```json
{
  "@context": { },
  "@graph": [ ]
}
```

The exporter MUST choose one shape and keep it stable within `export_profile_version`.

### 5.2 Metadata node

The export SHOULD include a metadata node describing the export artifact.

Recommended shape:

```json
{
  "@id": "kristal-export:sha256:<hex>",
  "@type": "kristal:JsonLdExport",
  "kristal:schemaVersion": "5.0",
  "kristal:exportProfileId": "kristal.v5:jsonld-1.1",
  "kristal:exportProfileVersion": "1",
  "kristal:sourceArtifact": {
    "@id": "kristal:sha256:<hex>"
  },
  "kristal:projection": "full",
  "kristal:statementModel": "wikibase-aligned"
}
```

The metadata node MUST NOT be used to overwrite or reinterpret the source artifact’s validation status.

### 5.3 Context requirements

The `@context` MUST:

* be stable;
* be versioned;
* define compact terms for:

  * entity identifiers;
  * property identifiers;
  * assertion or statement model fields;
  * qualifiers;
  * references;
  * evidence pointers;
  * ranks;
  * provenance pointers;
  * assertion status;
  * certainty level;
  * validation references;
  * authority recognition references;
  * scope fields.

Recommended context strategy:

* Use a stable context URI per profile version, for example:

```text
https://kristal.org/contexts/v5/jsonld/v1
```

* Include explicit prefix mappings when using Wikidata-style IRIs, such as:

```text
wd:
wdt:
p:
ps:
pq:
pr:
prov:
xsd:
kristal:
```

A profile MAY use an embedded context, but the embedded context MUST be byte-stable under the export profile.

---

## 6. Node identity

### 6.1 Entity nodes

Entity nodes MUST have stable `@id` values derived from the entity identifier.

Recommended Wikidata-compatible mapping:

```text
Q123 -> wd:Q123
P456 -> wd:P456
```

A Kristal-native profile MAY use Kristal IRIs instead, such as:

```text
kristal-entity:Q123
kristal-property:P456
```

The chosen mapping MUST be declared in export metadata.

### 6.2 Assertion or statement nodes

Assertion or statement nodes SHOULD have stable `@id` values.

Recommended:

```text
assertion_id -> kristal-assertion:sha256:<hex>
statement_id -> wikibase statement IRI or kristal-statement:<id>
```

If both `assertion_id` and source-system `statement_id` are present:

* `assertion_id` SHOULD be the Kristal identity;
* `statement_id` SHOULD be preserved as a source-system identifier.

### 6.3 Evidence and reference nodes

Evidence and reference nodes SHOULD have stable `@id` values derived from:

* `evidence_id`;
* `reference_id`;
* content hash;
* source URI, if no stronger identifier exists.

Large raw evidence blobs MUST NOT be embedded unless enabled by an explicit profile extension.

---

## 7. Statement model

### 7.1 Supported models

The export MUST represent assertions/statements using one declared statement model:

```text
statement_model = "wikibase-aligned"
```

or:

```text
statement_model = "kristal-native"
```

An implementation MAY support both, but each export artifact MUST declare exactly one primary statement model.

### 7.2 Wikibase-aligned model

In the Wikibase-aligned model, statements SHOULD be represented in a way that preserves:

* subject entity;
* property;
* main value;
* qualifiers;
* references;
* rank, when present;
* assertion identity;
* source statement identity, when present;
* evidence and provenance pointers.

The export MAY use Wikidata-style IRIs and statement reification patterns.

### 7.3 Kristal-native model

In the Kristal-native model, statements SHOULD be represented using Kristal terms while preserving explicit mappings to Wikibase concepts when available.

A Kristal-native statement SHOULD include:

* `kristal:assertionId`;
* `kristal:subject`;
* `kristal:property`;
* `kristal:value`;
* `kristal:qualifier`;
* `kristal:reference`;
* `kristal:evidence`;
* `kristal:assertionStatus`;
* `kristal:certaintyLevel`;
* `kristal:validatedAs`;
* `kristal:scope`;
* `kristal:validationRef`;
* `kristal:authorityRecognitionRef`.

### 7.4 Assertion identity inclusion

If `assertion_id` exists in the source artifact, it MUST be included in the export.

If `statement_id` exists in the source artifact, it SHOULD be included as a source-system identifier.

If neither exists, exporters MUST compute a deterministic surrogate key for ordering. The surrogate key MUST NOT be presented as a Kristal content-addressed ID unless explicitly defined by a profile.

---

## 8. Literals and datatypes

### 8.1 Typed literals

Typed values MUST be expressed using JSON-LD value objects:

```json
{
  "@value": "2020-01-01",
  "@type": "xsd:date"
}
```

### 8.2 Language-tagged strings

Language values MUST be expressed using:

```json
{
  "@value": "Bonjour",
  "@language": "fr"
}
```

Language tags SHOULD be lowercase unless the source artifact intentionally preserves a specific normalized form.

### 8.3 Entity references

Values that are entities MUST be represented as `@id` references, not as plain strings.

Example:

```json
{
  "@id": "wd:Q123"
}
```

### 8.4 Numeric and temporal values

Exporters MUST preserve the normalized lexical form from the source artifact.

Exporters MUST NOT reinterpret precision, timezone, calendar model, unit, or datatype unless the source artifact explicitly contains a mapping that allows it.

---

## 9. Qualifiers and references

### 9.1 Qualifiers

Qualifiers MUST be represented as arrays or objects that remain deterministic under the export profile.

If arrays are used, they MUST be sorted according to Section 4.3.

A qualifier SHOULD preserve:

* property;
* value;
* datatype;
* source pointer, if available;
* certainty or validation metadata, if the qualifier itself is status-bearing.

### 9.2 References and evidence pointers

References MUST include stable pointers back to source evidence or reference objects.

Minimum requirement:

* `evidence_id`, `reference_id`, or equivalent stable identifier;
* source URI, when available;
* content hash, when available;
* provenance pointer, when available.

Export MUST NOT embed large raw evidence blobs unless explicitly enabled by an additional profile.

### 9.3 Provenance

When provenance metadata is selected for export, it SHOULD preserve:

* source artifact references;
* source URI;
* publisher or contributor identity;
* derivation references;
* merge references;
* transformation references;
* validation or review references.

Provenance export MUST preserve attribution and MUST NOT silently merge different authority channels.

---

## 10. Assertion status, certainty, and authority metadata

### 10.1 Assertion status

If present in the source artifact and selected by export policy, `assertion_status` MUST be exported.

Recommended values are:

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

### 10.2 Certainty level

If present in the source artifact and selected by export policy, `certainty_level` MUST be exported.

Recommended values are:

```text
unknown
speculative
low
medium
high
established
not_applicable
mixed
```

### 10.3 Validated as

If present in the source artifact and selected by export policy, `validated_as` MUST be exported.

Recommended values include:

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

### 10.4 Authority recognition references

Authority recognition references SHOULD be exported when they are present and selected by policy.

The export MUST preserve the distinction between:

* who published a claim;
* who validated a claim;
* who recognized a claim;
* which scope the recognition applies to;
* which policy was used.

A claim validated or recognized under one authority channel MUST NOT be represented as validated or recognized under another authority channel unless the source artifact explicitly records that recognition.

### 10.5 Scope metadata

Scope metadata SHOULD be exported when present and selected by policy.

Recommended scope fields:

* `domain`;
* `subdomain`;
* `jurisdiction`;
* `time_window`;
* `tenant_id`;
* `environment`;
* `language`.

---

## 11. Full and best-rank projections

### 11.1 Supported projections

This profile supports two projections:

```text
projection = "full"
```

and:

```text
projection = "best_rank"
```

The `full` projection exports all selected statements and preserves rank metadata when present.

The `best_rank` projection exports selected statements according to a deterministic rank policy.

### 11.2 Default projection

The default projection is:

```text
projection = "full"
```

If best-rank rules are not implemented, exporters MUST emit only `projection = "full"`.

### 11.3 Best-rank projection rules

If `best_rank` is supported, the exporter MUST:

* define the rule;
* keep it deterministic;
* declare the rule in export metadata;
* preserve enough metadata for consumers to understand that the export is a projection;
* avoid presenting omitted statements as nonexistent.

Recommended metadata:

```json
{
  "projection": "best_rank",
  "projection_policy": {
    "policy_id": "kristal.v5:projection-policy:wikibase-best-rank",
    "policy_version": "1"
  }
}
```

### 11.4 Compatibility alias

For Wikibase compatibility, a profile MAY expose `best_rank` as equivalent to a “truthy” projection.

When this term is used, it MUST be treated as a technical projection label, not as a universal truth claim.

---

## 12. Export policies and reader policies

### 12.1 Export policy

An export policy defines what content is included in the JSON-LD artifact.

It MAY filter by:

* artifact status;
* assertion status;
* validation status;
* certainty level;
* validated-as mode;
* authority channel;
* recognition status;
* domain;
* jurisdiction;
* language;
* projection;
* reader policy.

### 12.2 Reader policy linkage

If a JSON-LD export is produced from a reader policy, the export metadata MUST record the reader policy reference.

Example:

```json
{
  "reader_policy_ref": {
    "ref": "reader_policy:validated_only"
  }
}
```

### 12.3 Visibility is policy-bound

If content is excluded due to export policy, the export SHOULD record the policy used.

The absence of an assertion from a filtered export MUST NOT be interpreted as proof that the assertion does not exist in the source artifact.

---

## 13. Integrity linkage

The JSON-LD export SHOULD include:

* `source_kristal_id`;
* `source_artifact_ref`;
* `source_content_hash`, when available;
* `export_content_hash`, when the export artifact is content-addressed;
* `export_artifact_id`, when defined;
* export profile ID and version;
* projection policy ID and version, when applicable.

Recommended content hash shape:

```json
{
  "alg": "sha256",
  "value": "<lowercase-hex>"
}
```

If the system uses signatures:

* the JSON-LD export MAY be signed as a derived artifact;
* signatures MUST follow the v5 signature and hashing rules;
* signatures MUST NOT be interpreted as validation of truth unless the signature is part of a declared authority recognition or validation policy.

---

## 14. Example skeleton

A minimal JSON-LD export SHOULD follow this general shape:

```json
{
  "@context": "https://kristal.org/contexts/v5/jsonld/v1",
  "@graph": [
    {
      "@id": "kristal-export:sha256:<hex>",
      "@type": "kristal:JsonLdExport",
      "kristal:schemaVersion": "5.0",
      "kristal:exportProfileId": "kristal.v5:jsonld-1.1",
      "kristal:exportProfileVersion": "1",
      "kristal:sourceArtifact": {
        "@id": "kristal:sha256:<hex>"
      },
      "kristal:projection": "full",
      "kristal:statementModel": "wikibase-aligned"
    },
    {
      "@id": "wd:Q123",
      "@type": "kristal:Entity",
      "kristal:assertion": {
        "@id": "kristal-assertion:sha256:<hex>"
      }
    },
    {
      "@id": "kristal-assertion:sha256:<hex>",
      "@type": "kristal:Assertion",
      "kristal:subject": {
        "@id": "wd:Q123"
      },
      "kristal:property": {
        "@id": "wdt:P31"
      },
      "kristal:value": {
        "@id": "wd:Q5"
      },
      "kristal:assertionStatus": "validated",
      "kristal:certaintyLevel": "high",
      "kristal:validatedAs": "high_confidence_fact",
      "kristal:authorityRecognitionRef": {
        "@id": "authority-recognition:sha256:<hex>"
      }
    }
  ]
}
```

This example is illustrative. Conformance depends on the normative rules in this profile, not on this exact shape.

---

## 15. Conformance tests

An implementation claiming conformance to:

```text
kristal.v5:jsonld-1.1
```

MUST provide fixtures that validate:

* deterministic output bytes for a fixed source artifact and export policy;
* correct profile metadata;
* correct context versioning and stability;
* correct ordering of entities, assertions, qualifiers, references, validation references, and authority recognition references;
* correct encoding of typed literals;
* correct encoding of language-tagged strings;
* correct encoding of entity references as `@id`;
* preservation of assertion identity;
* preservation of source statement identity when present;
* preservation of assertion status when selected by policy;
* preservation of certainty level when selected by policy;
* preservation of validation and authority recognition references when selected by policy;
* correct handling of `full` projection;
* correct handling of `best_rank` projection, if supported;
* byte-stable output across at least two independent runs.

An implementation MUST NOT claim conformance if its export order depends on map iteration order, database return order, filesystem order, locale-dependent sorting, or nondeterministic runtime behavior.

---

## 16. Required implementation declarations

A conforming exporter MUST declare:

```text
export_profile_id
export_profile_version
schema_version
source_artifact_ref
source_artifact_type
statement_model
projection
context_version_or_uri
canonicalization_profile_for_export
canonicalization_version_for_export
```

If filtering is applied, it MUST also declare one or more of:

```text
export_policy_ref
reader_policy_ref
authority_channel_filter
certainty_filter
validation_status_filter
assertion_status_filter
scope_filter
```

---

## 17. Non-goals

This profile does not determine whether an assertion should be trusted.

It only defines how selected Kristal content is projected into deterministic JSON-LD.

Authority, validation, certainty, and reader visibility remain explicit metadata and policy decisions. They MUST NOT be hidden by the export process.
