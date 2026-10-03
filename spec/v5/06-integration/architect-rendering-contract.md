# Architect rendering contract

## Status

Draft (Kristal v5 integration contract)

## Purpose

This document defines the contract between **Architect** and **Kristal v5**.

Architect is the deterministic renderer. It produces text and other publishable outputs from Kristal query results without introducing new factual claims, without hiding provenance, and without flattening scoped validation into universal truth.

Architect does not decide what is true. It renders what the selected Kristal input and active reader policy allow it to render.

This contract applies to rendering from:

* Runtime Pack query result bundles;
* Exchange-derived query result bundles;
* Structured Epistemic State projections;
* federation-derived query results;
* authority-recognized reference artifacts;
* working artifacts when the active reader policy allows them.

Normative keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.

---

## 1. Scope and non-goals

### 1.1 In scope

* Inputs Architect is allowed to consume
* Reader policy requirements
* Determinism requirements for rendering
* Prohibitions on introducing new factual claims
* Traceability requirements
* Authority, validation, certainty, and scope preservation
* Error and refusal behavior
* Multilingual rendering rules and templating boundaries
* Output packaging
* Machine-readable trace maps
* Render bundle identity and optional signing

### 1.2 Out of scope

* How Kristals are built
* How review workflows are routed
* How authority channels are governed
* Runtime query engine implementation details
* Konnaxion UI presentation requirements
* Editorial policy beyond deterministic rendering, traceability, and status preservation

---

## 2. Contract overview

Architect rendering is a pure function over explicit inputs:

* input bundle;
* reader policy;
* rendering request;
* template or render profile;
* language and locale parameters.

Architect MUST produce deterministic output for identical inputs.

Architect MUST NOT introduce factual claims that are not supported by the input bundle.

Architect MUST preserve visible distinctions between:

* artifact status;
* assertion status;
* validation status;
* certainty level;
* validated-as mode;
* authority channel;
* recognition status;
* scope;
* disputed status;
* fictional, mythological, symbolic, speculative, or research mode.

Architect MAY render uncertain, disputed, fictional, mythological, speculative, or low-certainty material when the active reader policy permits it.

Architect MUST NOT present such material as higher-certainty, more broadly validated, or more widely recognized than the input supports.

---

## 3. Inputs

### 3.1 Allowed input types

Architect MUST accept only declared Kristal input bundles.

Allowed input types are:

**A) Runtime Pack query result bundle**

* `runtime_pack_id` or pack content ID;
* `runtime_pack_manifest` or manifest reference;
* `source_exchange_ref`;
* `source_artifact_status`;
* `query_contract_version`;
* `reader_policy_ref` or embedded reader policy;
* `query_results`;
* `result_provenance`;
* integrity metadata.

**B) Exchange-derived query result bundle**

* `source_kristal_id`;
* `exchange_manifest` or manifest reference;
* `artifact_type`, either `working_exchange` or `reference_exchange`;
* deterministic query spec;
* `query_results`;
* validation, recognition, or status metadata for the returned claims;
* proof that results were computed from the referenced Exchange under a declared query contract.

**C) Structured Epistemic State projection bundle**

* `state_id`;
* `schema_version`;
* `scope`;
* `assertions`;
* `projection_policy_ref`;
* provenance references;
* assertion status, certainty, and validation metadata.

**D) Federation-derived query result bundle**

* `federation_id`;
* `exchange_federation_manifest`;
* `authority_registry_ref`;
* `composition_policy`;
* `reader_policy_ref` or embedded reader policy;
* ordered query results;
* source shard references;
* conflict and disagreement metadata where applicable.

Architect MUST reject or refuse inputs that:

* cannot be traced to a stable Kristal artifact, state, shard, federation, Exchange, or Runtime Pack;
* do not provide stable assertion or statement identifiers;
* do not provide enough provenance to support trace maps;
* do not declare the active reader policy;
* do not declare validation, certainty, authority, and scope metadata where factual claims are rendered;
* violate the active reader policy.

Architect MUST NOT reject an input merely because it contains uncertainty, dispute, fiction, mythology, speculation, or low-certainty claims. Those are valid Kristal states when explicitly labeled and allowed by the reader policy.

---

## 4. Required identifiers

Inputs MUST include enough identifiers to support complete traceability.

At minimum, an input bundle MUST include one or more of:

* `kristal_id`;
* `runtime_pack_id`;
* `state_id`;
* `federation_id`;
* `shard_id`;
* `exchange_id`;
* `source_artifact_ref`.

For each rendered factual assertion, inputs MUST provide:

* `assertion_id` or deterministic assertion pointer;
* statement or claim pointer;
* evidence pointer, source pointer, or provenance reference;
* assertion status;
* certainty level;
* validation status;
* validated-as mode, when evaluated;
* authority channel, when validated or recognized;
* scope.

If no stable identifier exists, Architect MAY use a deterministic surrogate pointer derived from:

* subject;
* predicate;
* object;
* qualifiers;
* source artifact ID;
* content hash;
* scope.

The surrogate pointer MUST be recorded in the trace map.

---

## 5. Rendering request specification

Architect MUST take a rendering request object.

The rendering request MUST include:

* `render_kind`, such as `article`, `snippet`, `summary`, `qa`, `card`, `report`, `compare`, or `explain`;
* `language`, as a BCP-47 tag, such as `en` or `fr-CA`;
* `template_id` or `render_profile_id`;
* `template_version` or `render_profile_version`;
* `reader_policy_id` or embedded reader policy;
* `projection`, when supported;
* `constraints`.

The rendering request MAY include:

* `audience_profile`;
* `tone_profile`;
* `length_target`;
* `format`;
* `locale`;
* `citation_style`;
* `include_trace_summary`;
* `include_disputed_material`;
* `include_uncertainty_labels`;
* `include_authority_labels`;
* `include_certainty_labels`.

Audience and tone profiles MUST NOT change factual content.

---

## 6. Reader policy

Architect MUST render under an active reader policy.

The reader policy determines which material is eligible for rendering.

A reader policy MAY restrict:

* artifact statuses;
* assertion statuses;
* validation statuses;
* certainty levels;
* validated-as modes;
* authority channels;
* recognition statuses;
* domains;
* scopes;
* jurisdictions;
* languages;
* disputed material;
* fictional material;
* mythological material;
* symbolic material;
* speculative or research material.

Supported reader modes SHOULD include:

* `reference_only`;
* `validated_only`;
* `high_certainty_only`;
* `research`;
* `creative`;
* `all_with_labels`;
* `custom`.

### 6.1 Validated-only does not mean maximum certainty

A `validated_only` reader policy means that all rendered assertions satisfy the active validation policy.

It does not mean:

* all rendered assertions have maximum certainty;
* all rendered assertions are universally true;
* all authority channels agree;
* all assertions are physical-world factual claims.

For example:

* a hypothesis may be validated as a hypothesis;
* a mythological corpus may be validated as mythology;
* a fictional corpus may be validated as fiction;
* a technical document may be validated as a publisher declaration;
* a scientific claim may be validated as a high-confidence fact.

Architect MUST preserve these distinctions in output metadata and, when required by the render profile, in visible text.

---

## 7. Deterministic rendering rules

### 7.1 Determinism requirement

For identical:

* input bundle bytes;
* reader policy;
* template or render profile ID and version;
* language;
* locale;
* rendering parameters;

Architect MUST produce identical render bundles, modulo explicitly declared nondeterministic fields that are excluded from output hashing.

Examples of excluded fields MAY include:

* run timestamp;
* local execution environment ID;
* non-factual logging correlation ID.

### 7.2 No new factual claims

Architect MUST NOT introduce any factual assertion that is not supported by at least one input assertion, statement, claim, or provenance-bearing source.

This includes:

* numbers;
* dates;
* names;
* causal relationships;
* rankings;
* comparisons;
* superlatives;
* categorical claims;
* historical claims;
* scientific claims;
* legal claims;
* policy claims;
* institutional claims.

Architect MUST NOT add “common knowledge” filler if that filler asserts a new fact.

Architect MUST NOT use external enrichment from the network for factual claims.

Architect MAY add:

* headings;
* transitions;
* formatting;
* connective phrasing;
* summaries that are fully supported by traced input;
* uncertainty language when uncertainty is present in the input;
* non-factual stylistic phrasing that does not add information.

### 7.3 Status preservation

Architect MUST preserve the status of input claims.

Architect MUST NOT convert:

* `hypothesis` into fact;
* `claimed` into validated;
* `sourced` into high-confidence;
* `disputed` into settled;
* `fictional_corpus` into physical-world truth;
* `mythological_corpus` into physical-world truth;
* one authority’s recognition into another authority’s recognition;
* scoped validation into universal validation.

### 7.4 Ambiguity preservation

If input contains unresolved ambiguity, Architect MUST either:

* render the ambiguity explicitly;
* omit the ambiguous claim;
* refuse to render the ambiguous claim as factual;
* fail deterministically if the render request requires a single resolved fact.

Architect MUST NOT silently choose one disambiguation unless the input explicitly declares a resolved selection.

### 7.5 Disagreement preservation

If input contains conflicting claims, Architect MUST follow the active reader policy.

Architect MAY:

* preserve disagreement;
* show multiple authority-scoped positions;
* select one position according to authority precedence;
* mark a claim as disputed;
* omit claims outside the reader policy.

Architect MUST NOT silently merge conflicting claims.

Architect MUST NOT hide that a claim is disputed when the input declares dispute and the render profile requires dispute visibility.

### 7.6 Projection consistency

If the input bundle declares a projection, Architect MUST:

* render only from that projection;
* record the projection in render metadata;
* preserve projection limitations in the trace map.

If the requested projection and input projection conflict, Architect MUST refuse or return a deterministic error.

---

## 8. Output requirements

Architect MUST output a render bundle.

A render bundle MUST include:

1. `rendered_text` or structured rendered blocks;
2. `trace_map`;
3. `render_metadata`;
4. `status`.

A render bundle MAY include:

* `render_hash`;
* signatures;
* template references;
* reader policy snapshot;
* warnings;
* refusal details;
* render diagnostics.

---

## 9. Render metadata

`render_metadata` MUST include:

* `schema_version`;
* `artifact_type`;
* `render_kind`;
* `language`;
* `template_id`;
* `template_version`;
* `reader_policy_id`;
* `reader_mode`;
* `source_refs`;
* `query_contract_version`, if from runtime query results;
* `projection`;
* `build_id`;
* `created_at`.

`artifact_type` MUST be:

```text
architect_render_bundle
```

`schema_version` MUST be:

```text
5.0
```

`source_refs` MUST identify the source artifact or artifacts, such as:

* Runtime Pack;
* Exchange;
* Structured Epistemic State;
* Federation;
* Shard;
* query bundle.

---

## 10. Trace map

The trace map MUST provide complete coverage of factual assertions.

### 10.1 Required structure

The trace map MUST include:

* `segments[]`;
* `source_refs[]`;
* `coverage_summary`.

Each segment MUST include:

* `segment_id`;
* `text_span`, byte offsets, token indices, or `block_id`;
* `segment_kind`;
* `assertions[]`;
* `status_labels[]`, when applicable.

Each assertion trace MUST include:

* `assertion_id` or deterministic assertion pointer;
* `support[]`;
* `assertion_status`;
* `certainty_level`;
* `validation_status`;
* `validated_as`, when evaluated;
* `authority_channel`, when evaluated or recognized;
* `recognition_status`, when recognized;
* `scope`;
* `notes`, if needed.

Each support pointer MUST include:

* statement ID, claim ID, or deterministic statement pointer;
* evidence IDs or reference pointers;
* source artifact reference;
* source kind, such as `exchange`, `runtime_pack`, `structured_epistemic_state`, `federation`, or `shard`;
* content hash, when available.

### 10.2 Coverage rule

Every factual statement in `rendered_text` MUST have at least one support entry in `trace_map`.

If a segment cannot be supported, Architect MUST do one of the following:

* omit the unsupported claim;
* render it only as explicitly marked uncertainty, if that uncertainty is supported by the input;
* fail the render with a deterministic error.

### 10.3 Label coverage

When the render profile requires visible labels, Architect MUST expose:

* uncertainty;
* dispute;
* fiction;
* mythology;
* symbolic mode;
* low certainty;
* scoped validation;
* authority channel;
* rejection or revocation;
* recognition status.

When the render profile does not require visible labels, Architect MUST still preserve them in machine-readable metadata.

---

## 11. Validation and refusal behavior

Architect MUST implement deterministic status and refusal behavior.

The top-level render status MUST be one of:

```text
ok
refused
error
partial
```

Architect MUST return:

* `status`;
* `code`;
* `message`;
* `details`, when applicable.

### 11.1 Required refusal and error codes

Architect MUST support at least:

* `INPUT_INTEGRITY_UNVERIFIED`;
* `MISSING_TRACE_IDS`;
* `MISSING_READER_POLICY`;
* `READER_POLICY_VIOLATION`;
* `AUTHORITY_POLICY_MISMATCH`;
* `CERTAINTY_POLICY_MISMATCH`;
* `VALIDATION_POLICY_MISMATCH`;
* `RECOGNITION_POLICY_MISMATCH`;
* `AMBIGUOUS_INPUT`;
* `DISPUTED_INPUT_NOT_ALLOWED`;
* `FICTIONAL_INPUT_NOT_ALLOWED`;
* `MYTHOLOGICAL_INPUT_NOT_ALLOWED`;
* `UNSUPPORTED_RENDER_KIND`;
* `PROJECTION_MISMATCH`;
* `POLICY_VIOLATION_NEW_FACT_RISK`;
* `UNSUPPORTED_LANGUAGE`;
* `UNSUPPORTED_TEMPLATE`;
* `TRACE_COVERAGE_FAILED`.

### 11.2 Refusal is not epistemic judgment

A refusal means the render request cannot be satisfied under the given input, policy, or template.

A refusal does not mean the underlying Kristal is false.

A refusal may mean:

* required provenance is missing;
* the reader policy excludes the material;
* uncertainty labels are required but unavailable;
* authority recognition is insufficient for the selected mode;
* the template would require unsupported factual claims;
* ambiguity cannot be resolved under the requested constraints.

---

## 12. Multilingual rendering

### 12.1 Language fidelity

Architect MAY translate labels, connective text, headings, and explanatory text.

Architect MUST NOT alter factual content.

Architect MUST preserve named entities, identifiers, quantities, dates, and scoped claims unless the input or template provides a deterministic localization rule.

### 12.2 Localized formatting

Architect MAY apply locale-specific formatting for:

* numbers;
* dates;
* currencies;
* units;
* punctuation;
* typography.

Localized formatting MUST NOT change meaning.

The underlying normalized value MUST remain traceable.

### 12.3 Cross-language determinism

Rendering in different languages may produce different bytes.

For each language, output MUST be deterministic given the same:

* input bundle;
* reader policy;
* language;
* locale;
* template;
* rendering parameters.

### 12.4 Translation of status labels

Status labels SHOULD be localized when the render profile requires human-readable labels.

The localized label MUST map back to the machine-readable source status.

For example:

```text
assertion_status = "hypothesis"
```

may render in French as:

```text
hypothèse
```

but the trace map MUST preserve:

```text
hypothesis
```

---

## 13. Security and offline constraints

Architect MUST NOT require network calls to produce correct factual output.

If network calls are used for non-factual assets, such as fonts or templates, they MUST NOT affect factual assertions.

If inputs are signed, Architect SHOULD verify signatures or rely on a verified delivery chain from Orgo, Konnaxion, or another declared runtime authority.

Architect MUST reject inputs that cannot satisfy the active deployment’s integrity and reader policy requirements.

Architect MUST preserve authority, validation, certainty, and scope metadata in offline rendering.

Offline rendering MUST NOT silently upgrade material from one status to another.

---

## 14. Render bundle identity and hashing

Architect render bundles MAY be content-addressed.

When content-addressed, the render hash MUST be computed over a deterministic serialization of:

* rendered output;
* trace map;
* render metadata;
* reader policy snapshot or reference;
* source refs;
* template refs.

The following fields MUST be excluded from the hash target unless a profile explicitly includes them:

* signatures;
* local runtime logs;
* non-factual correlation IDs;
* nondeterministic timestamps.

Hash objects MUST use:

```json
{
  "alg": "sha256",
  "value": "<hex>"
}
```

Architect MUST use `alg`, not `algo`.

Signatures MUST be outside the hash target.

---

## 15. Conformance tests

An implementation claiming conformance to this contract MUST provide tests for:

* deterministic rendering;
* trace coverage;
* no-new-facts enforcement;
* ambiguity preservation;
* disagreement preservation;
* reader policy enforcement;
* authority channel filtering;
* certainty filtering;
* validation status filtering;
* fictional and mythological scope handling;
* projection handling;
* multilingual determinism;
* render hash stability, when render hashing is supported.

### 15.1 Minimum test cases

A conforming implementation MUST include at least the following tests:

1. Same input bundle and render request produce identical render bundles.
2. Every factual claim has support pointers.
3. Unsupported factual additions are refused or removed.
4. Ambiguous input is rendered as ambiguous or refused.
5. Disputed input is preserved, labeled, omitted, or refused according to reader policy.
6. A `validated_only` reader policy excludes non-validated material.
7. A `research` reader policy may include lower-certainty material with labels.
8. A `creative` reader policy may include fictional or mythological material with labels.
9. A mythological claim is not rendered as physical-world fact.
10. Authority recognition by one channel is not rendered as recognition by another channel.
11. Projection mismatch triggers deterministic refusal or error.
12. Trace coverage failure triggers deterministic refusal or error.

---

## 16. Implementation notes

Architect should be boring.

It should not infer hidden truth.

It should not “improve” facts.

It should not smooth away disagreement.

It should not erase uncertainty.

It should not translate scoped recognition into universal recognition.

Architect’s job is to render clearly, deterministically, and traceably from Kristal artifacts under a selected reader policy.

The core invariant is:

> A rendered claim must never appear more certain, more validated, more recognized, more factual, or more universal than the Kristal input and reader policy support.
