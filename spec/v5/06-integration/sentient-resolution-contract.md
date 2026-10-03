# 06-integration/sentient-resolution-contract.md

# SenTient Resolution Contract

## Status

Draft (v5 normative integration contract)

## Purpose

Define the required **inputs**, **outputs**, and **deterministic semantics** for SenTient when SenTient acts as a resolution, disambiguation, normalization, or extraction-support engine for Kristal v5.

This contract ensures:

* ambiguity is preserved explicitly;
* outputs are schema-valid and deterministically structured;
* downstream compilation, validation, review, federation, and recognition remain reproducible and auditable;
* failure modes are explicit;
* SenTient does not silently convert uncertainty into validated knowledge.

This document does **not** prescribe SenTient’s internal retrieval, scoring, judging, or modeling architecture. It specifies the interoperability boundary only.

## Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

---

# 1. SenTient role in Kristal v5

SenTient supports Kristal v5 by resolving and normalizing source material into structured forms usable by Kristal artifacts.

SenTient may operate on:

* Claim-IR batches emitted by extractors;
* Structured Epistemic States;
* datasets;
* human-authored drafts;
* institutional submissions;
* unresolved assertion fragments;
* source-system records such as Wikidata-compatible statements.

SenTient may produce:

* ranked candidate identifiers;
* normalized typed literals;
* explicit unresolved ambiguity structures;
* warnings and errors;
* extraction proposals;
* resolution metadata;
* candidate mappings to existing entities, properties, references, or authority channels.

SenTient MUST NOT:

* force disambiguation without sufficient evidence;
* silently coerce ambiguous surfaces into single IDs;
* introduce new assertions beyond what the input or resolution policy permits;
* mark an assertion as validated or recognized by an authority channel;
* hide ambiguity from downstream Kristal artifacts.

In Kristal v5, SenTient is not the universal proposal boundary. Claim-IR is an extractor proposal profile. Structured Epistemic State is the normative Kristal v5 input form.

---

# 2. Inputs

## 2.1 Supported inputs

SenTient MUST accept at least one of the following input types, depending on implementation scope:

* a Claim-IR batch conforming to `02-schemas/claim-ir.schema.json`;
* a Structured Epistemic State conforming to `02-schemas/structured-epistemic-state.schema.json`;
* an Exchange or Exchange fragment;
* a dataset record batch declared by profile;
* a source-system statement batch declared by profile.

A SenTient implementation MUST declare which input profiles it supports.

## 2.2 Claim-IR input

When SenTient accepts Claim-IR, it treats Claim-IR as an extractor proposal profile, not as the universal Kristal v5 input requirement.

Claim-IR input SHOULD include:

* `claim_id` or stable local ID;
* surface forms for entities and properties;
* proposed literals or values;
* evidence pointers;
* uncertainty representation;
* source references;
* extraction metadata.

SenTient MAY emit a Resolved Claim-IR batch when operating in a Claim-IR compatibility profile.

## 2.3 Structured Epistemic State input

When SenTient accepts a Structured Epistemic State, the input SHOULD include:

* `state_id`, if already content-addressed;
* assertions or assertion fragments;
* surface forms requiring resolution;
* provenance references;
* evidence references;
* certainty metadata, if available;
* scope metadata;
* policy references;
* prior resolution references, if available.

SenTient MAY emit an updated Structured Epistemic State, a resolution bundle, or resolution findings referencing the input state.

## 2.4 Optional hints and constraints

SenTient MAY accept optional hints, including:

* preferred language or locale;
* candidate constraints;
* allowed QID/PID sets;
* tenant-specific mapping overlays;
* domain or subdomain constraints;
* jurisdiction constraints;
* time-window constraints;
* authority-channel hints;
* prior resolution state;
* corpus snapshot IDs;
* reader-policy hints;
* validation-policy hints.

If hints are used, SenTient MUST:

* treat them as advisory unless the active resolution policy says otherwise;
* record their presence in output metadata;
* preserve enough metadata for downstream systems to understand how hints affected the resolution run.

---

# 3. Outputs

## 3.1 Supported output types

SenTient MAY output one or more of:

* Resolved Claim-IR batch;
* Structured Epistemic State;
* Resolution Bundle;
* Validation Report findings;
* candidate mapping bundle;
* normalized literal bundle;
* warnings and errors attached to the input object;
* lineage or provenance records.

An implementation MUST declare which output profiles it supports.

## 3.2 Resolved Claim-IR compatibility output

When outputting Resolved Claim-IR, SenTient MUST conform to:

```text
02-schemas/resolved-claim-ir.schema.json
```

The output MUST preserve a stable mapping to input Claim-IR items.

Every output resolution result MUST reference the originating `claim_id`.

## 3.3 Structured Epistemic State output

When outputting or updating a Structured Epistemic State, SenTient MUST preserve:

* source assertion identity where present;
* provenance references;
* evidence references;
* unresolved ambiguity;
* scope;
* certainty metadata unless explicitly changed under policy;
* lineage from input to output.

SenTient MUST NOT silently replace a lower-certainty state with a higher-certainty one.

If SenTient changes certainty metadata, it MUST record the reason and policy basis for the change.

## 3.4 Resolution Bundle output

A Resolution Bundle SHOULD include:

* `resolution_bundle_id`;
* `schema_version = "5.0"`;
* `artifact_type = "resolution_bundle"`;
* `created_at`;
* `created_by`;
* `input_refs`;
* `resolution_run_id`;
* `resolution_policy_ref`;
* `scope`;
* `results`;
* `warnings`;
* `errors`;
* `lineage`;
* `signatures`, when applicable.

A Resolution Bundle is a support artifact. It does not itself validate or recognize claims.

---

# 4. Resolution results per surface

For each resolvable surface, including entity surfaces, property surfaces, value normalization targets, references, authority-channel candidates, or scope candidates, SenTient MUST provide an explicit result.

## 4.1 Ranked candidates

A resolution result SHOULD include ranked candidates.

Each candidate SHOULD include:

* `id`;
* `candidate_type`;
* `score`;
* `evidence_refs`;
* optional `features`;
* optional `source_corpus_ref`;
* optional `authority_channel`, when the candidate is authority-scoped.

Candidate lists MUST be sorted deterministically.

## 4.2 Decision state

One of the following decision states MUST be explicitly recorded:

```text
resolved_single
resolved_multi
unresolved
error
not_applicable
```

Meanings:

* `resolved_single`: resolved to one selected candidate.
* `resolved_multi`: multiple candidates remain plausible; no single candidate is forced.
* `unresolved`: no adequate candidate is available.
* `error`: resolution process failed in a defined way.
* `not_applicable`: the surface does not require resolution.

## 4.3 Selected binding

If the decision state is `resolved_single`, SenTient MUST provide:

* `selected.id`;
* `selected.score`, when scoring is used;
* selected candidate type.

If the decision state is `resolved_multi`, SenTient MUST NOT provide a selected binding unless a profile explicitly marks it as a non-authoritative UI suggestion.

If the decision state is `unresolved` or `error`, SenTient MUST NOT provide a selected binding.

## 4.4 Ambiguity preservation

If evidence is insufficient for unique resolution, SenTient MUST use:

```text
resolved_multi
```

or:

```text
unresolved
```

SenTient MUST NOT hide unresolved ambiguity by selecting a single candidate for convenience.

---

# 5. Determinism and portability

## 5.1 Output structure determinism

SenTient output MUST be deterministic in structure:

* stable field names;
* stable types;
* stable decision-state vocabulary;
* stable ordering rules;
* stable serialization behavior when canonicalized.

This does not require scores to remain identical across model versions.

It requires that:

* the output is well formed;
* candidate ranking is explicit;
* ambiguity is explicit;
* the same scoring run produces stable ordering.

## 5.2 Candidate list truncation

If SenTient returns only top-K candidates:

* K MUST be declared in output metadata;
* truncation MUST be consistent by surface type;
* truncation MUST be reported when it may affect interpretation.

Recommended declaration:

```json
{
  "candidate_top_k": {
    "entity": 20,
    "property": 10,
    "authority_channel": 10,
    "literal_normalization": 5
  }
}
```

## 5.3 Stable sorting rules

SenTient MUST define deterministic tie-breakers for candidates.

Default ordering:

1. score descending;
2. stable identifier ascending lexicographically;
3. deterministic hash of `(surface, candidate_id, candidate_type)`.

This avoids nondeterminism when scores collide.

## 5.4 Literal normalization determinism

When normalizing literals such as dates, quantities, coordinates, identifiers, time ranges, or units, SenTient MUST:

* produce typed outputs in a deterministic schema form;
* include explicit unit, precision, calendar, timezone, or coordinate system fields when relevant;
* record lossy normalization decisions as warnings;
* preserve the original surface form when relevant.

---

# 6. Output metadata

SenTient output MUST include metadata sufficient for downstream compilation, validation, review, federation, and audit.

## 6.1 Required metadata

SenTient output MUST include:

* `resolution_run_id`;
* `schema_version`;
* `sentient_version` or resolver version string;
* `created_at`;
* `input_refs`;
* `hints_used`;
* `hint_refs`, if hints were used;
* `policies`, including:

  * `candidate_top_k`;
  * `tie_breakers`;
  * `normalization_ruleset_id`;
  * `resolution_policy_ref`.

## 6.2 Optional metadata

SenTient output MAY include:

* resource limits encountered;
* timeouts;
* corpus snapshot IDs;
* model identifiers used for semantic scoring;
* source corpus versions;
* tenant scope;
* authority-channel hints;
* reader-policy hints;
* validation-policy hints.

If optional metadata is recorded, it MUST NOT affect core identity unless included in the declared hash target or reproducibility surface.

---

# 7. Warnings and errors

## 7.1 Structured codes

SenTient MUST emit warnings and errors as structured records containing:

* machine-readable `code`;
* severity;
* human-readable `message`;
* optional `details`;
* input linkage, where applicable;
* surface linkage, where applicable.

Severity values SHOULD be:

```text
info
warning
error
```

Codes MUST be stable across minor versions.

## 7.2 Required warning categories

SenTient SHOULD include warning codes for:

* unresolved entity surfaces;
* unresolved property surfaces;
* ambiguous multi-candidate surfaces;
* literal normalization loss;
* unit coercion;
* precision loss;
* date or time ambiguity;
* evidence insufficiency;
* weak grounding;
* top-K truncation;
* timeout;
* upstream outage;
* tenant overlay conflict;
* scope mismatch;
* authority-channel ambiguity.

## 7.3 Failure behavior

If SenTient cannot complete resolution for a claim or assertion due to transient issues, resource limits, upstream outages, or internal errors, SenTient MUST:

* return a syntactically valid output object for the declared output profile;
* mark affected surfaces as `unresolved` or `error`;
* emit explicit error codes;
* preserve input linkage;
* avoid silently dropping claims, assertions, evidence, or provenance.

---

# 8. Interaction with validation, recognition, and compilation

Validation stages MUST be able to interpret SenTient outputs deterministically.

Therefore SenTient MUST:

* keep all resolution states explicit;
* keep warning and error codes stable and structured;
* provide all required metadata needed to interpret results;
* preserve provenance and ambiguity.

SenTient output MAY be compiled into a Working Exchange when the compilation policy permits.

SenTient output MUST NOT by itself imply:

* validation;
* authority recognition;
* high certainty;
* reference status;
* reader visibility.

A validation report may cite SenTient results as evidence, findings, or diagnostics. It must not treat SenTient resolution as automatic truth.

---

# 9. Security and multi-tenancy

## 9.1 Tenant scoping

If SenTient is used in a multi-tenant environment:

* tenant-specific hints and overlays MUST be isolated by `tenant_id`;
* output metadata MUST indicate tenant scope when applicable;
* candidate generation MUST NOT leak tenant-private records into another tenant’s output.

## 9.2 Input confidentiality

SenTient MUST NOT leak:

* evidence pointers;
* source snippets;
* private corpus references;
* tenant-specific mappings;
* internal candidate features;

across tenants or unauthorized authority contexts.

## 9.3 Authority-channel isolation

If authority-channel-specific mappings or hints are used, SenTient MUST preserve which authority channel supplied or constrained them.

A candidate preferred under one authority channel MUST NOT be presented as generally preferred unless the policy explicitly permits that interpretation.

---

# 10. Conformance checklist

SenTient satisfies this contract if it:

* accepts and declares at least one supported Kristal v5 input profile;
* produces at least one declared Kristal v5 output profile;
* emits ranked candidates where resolution is attempted;
* records explicit decision states;
* preserves ambiguity;
* avoids silent coercion;
* applies deterministic sorting and tie-breakers;
* produces deterministic literal normalization structures;
* emits structured warnings and errors with stable codes;
* preserves input linkage;
* preserves provenance and evidence references;
* returns valid outputs even on partial failure;
* does not mark claims as validated, recognized, or high-certainty without an explicit validation or authority policy outside SenTient’s resolution role.
