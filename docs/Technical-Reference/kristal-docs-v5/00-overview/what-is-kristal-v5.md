# What is Kristal v5?

## Status

Draft

## Purpose

This document defines Kristal v5 at the overview level: what it is, what it is for, what it is not for, and how its main concepts fit together.

Kristal v5 is a deterministic, portable epistemic artifact system.

It allows claims, hypotheses, references, myths, technical declarations, research claims, institutional corpora, and disputed forks to coexist without confusion.

Validation is scoped.
Authority is plural.
Certainty is explicit.
Readers choose policy.
Federation preserves disagreement.
Integrity protects artifacts.

---

## 1. Definition

A **Kristal** is a portable, verifiable, offline-executable unit of structured epistemic knowledge.

A Kristal is **not** a document, article, mutable application database, raw database dump, free-text file, or model output. It is a compiled artifact with deterministic identity, explicit provenance, queryable structure, and machine-readable epistemic metadata.

Operational records remain authoritative in the system that owns their lifecycle. A source system may publish an immutable snapshot/export or stable artifact reference for Kristal compilation; the resulting Kristal artifact is a distinct knowledge artifact with provenance back to that source, not a transfer of ownership of the live record.

A Kristal can contain:

* factual assertions;
* sourced claims;
* hypotheses;
* unresolved or disputed assertions;
* mythological corpora;
* fictional corpora;
* symbolic models;
* technical specifications;
* publisher declarations;
* research claims;
* institutional references;
* authority recognition records;
* validation decisions;
* provenance and evidence links.

The core responsibility of Kristal v5 is not to guarantee that every assertion inside an artifact is true. Its responsibility is to prevent confusion between different epistemic states.

An assertion may exist without being validated.
An assertion may be validated without being maximally certain.
An assertion may be valid as fiction, mythology, hypothesis, publisher declaration, or high-confidence fact.
An assertion recognized by one authority channel is not automatically recognized by every other authority channel.

---

## 2. Core invariant

Kristal v5 is governed by this invariant:

> A Kristal may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.
> A Kristal must not present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

This means artifact existence, artifact integrity, assertion validity, certainty, authority recognition, and reader visibility are distinct.

```text
artifact existence
≠ artifact integrity
≠ assertion validity
≠ certainty
≠ authority recognition
≠ reader visibility
```

A Kristal can be technically valid, content-addressed, reproducible, signed, and queryable while still containing assertions that are low-certainty, disputed, rejected by some authorities, fictional, or mythological.

That is acceptable when the metadata is explicit.

---

## 3. What Kristal v5 is for

Kristal v5 is designed for:

* compiling structured epistemic states into portable artifacts;
* preserving provenance, evidence, certainty, and assertion status;
* supporting plural authority and scoped validation;
* making disagreement visible instead of silently merging it;
* enabling offline knowledge access;
* enabling deterministic query surfaces;
* supporting Wikidata/Wikibase-aligned data models;
* supporting institutional, scientific, civic, cultural, creative, and research corpora;
* allowing people and applications to choose reader policies;
* enabling AI systems to reason over structured, labeled knowledge without flattening authority or certainty.

Kristal v5 is especially useful when knowledge must be:

* portable;
* inspectable;
* versioned;
* queryable;
* reproducible;
* federated;
* provenance-bearing;
* authority-aware;
* usable offline;
* safe to render through AI or deterministic generation systems.

---

## 4. What Kristal v5 is not

Kristal v5 is not:

* a universal truth authority;
* a single global fact database;
* a shared mutable transactional database for Orgo, Konnaxion, or other applications;
* a bidirectional synchronization mechanism between product databases and Kristal artifacts;
* a replacement for scientific, legal, cultural, or institutional review;
* a claim that all included assertions are true;
* a guarantee that all authorities agree;
* a document format for prose;
* a workflow engine;
* a debate platform;
* a user interface;
* a social voting system;
* a full SPARQL engine;
* a replacement for Orgo, Konnaxion, SenTient, or Architect.

Kristal provides artifact contracts and epistemic structure. Other systems handle workflow, distribution, resolution, rendering, governance, and user experience.

---

## 5. The v5 epistemic model

Kristal v5 separates five concerns that are often confused.

### 5.1 Artifact validity

Artifact validity answers:

> Is this artifact well-formed, reproducible, content-addressed, and verifiable under its declared schema and policies?

Artifact validity does not mean every assertion inside the artifact is true.

### 5.2 Assertion status

Assertion status answers:

> What state is this assertion in?

Common assertion statuses include:

* `hypothesis`
* `claimed`
* `sourced`
* `disputed`
* `reviewed`
* `validated`
* `rejected`
* `retracted`
* `superseded`

### 5.3 Certainty level

Certainty answers:

> How strong is this assertion within its declared scope?

Common certainty levels include:

* `unknown`
* `speculative`
* `low`
* `medium`
* `high`
* `established`
* `not_applicable`

`not_applicable` is used when certainty is not the right scale, such as fiction, mythology, symbolic models, or declared publisher descriptions.

### 5.4 Validation

Validation answers:

> Who accepts this assertion or artifact, as what, under which rules, for which scope?

Validation is always scoped.

A claim can be validated as:

* a hypothesis;
* a sourced claim;
* a reviewed claim;
* a high-confidence fact;
* an institutional reference;
* a publisher declaration;
* a technical specification;
* a mythological corpus;
* a fictional corpus;
* a symbolic model;
* a disputed position;
* a rejected claim.

Validation does not always mean high certainty.

### 5.5 Authority recognition

Authority recognition answers:

> Which authority channel recognizes this target, and under what policy?

Authorities may include:

* individuals;
* communities;
* associations;
* research collectives;
* academic institutions;
* standards bodies;
* companies;
* governments;
* intergovernmental organizations;
* AI validators;
* hybrid collectives.

No authority channel has a universal monopoly by default. Recognition by one authority channel does not imply recognition by another.

---

## 6. Authority channels

An **Authority Channel** is a scoped source of recognition.

An authority channel may define:

* who can issue validation decisions;
* what scope it covers;
* which evidence standards it requires;
* which policies apply;
* which trust roots are valid;
* which other authorities it recognizes;
* how revocation works;
* how conflict is handled.

Examples:

```text
authority:unesco
authority:who
authority:microsoft
authority:canada-statistics
authority:local-history-society
authority:flat-earth-association-example
authority:independent-researcher-example
authority:fictional-world-author-example
```

An authority channel may recognize another authority channel for a scope.

For example:

```text
UNESCO may recognize WHO for a health reference scope.
A government may recognize its statistical agency for national demographic data.
A company may be the primary authority for its own published system specifications.
A research institution may recognize a lab for a specific experimental corpus.
```

Authority recognition is explicit, scoped, and revocable.

---

## 7. Reader policies

A **Reader Policy** determines which parts of a Kristal are visible or usable for a reader, application, institution, or AI system.

Reader policies may filter by:

* artifact status;
* assertion status;
* validation status;
* recognition status;
* authority channel;
* certainty level;
* validated-as mode;
* domain;
* subdomain;
* jurisdiction;
* time window;
* fictional mode;
* mythological mode;
* disputed status;
* rejected status;
* revoked status.

Common reader modes include:

* `reference_only`
* `validated_only`
* `high_certainty_only`
* `research`
* `creative`
* `all_with_labels`
* `custom`

A `validated_only` reader policy means all visible assertions satisfy the active reader policy.

It does not mean:

* all visible assertions are universally true;
* all visible assertions have maximum certainty;
* all visible assertions are accepted by every authority;
* all authorities agree.

---

## 8. Claim-IR and Structured Epistemic State

Kristal v5 uses **Structured Epistemic State** as the normative input unit.

A Structured Epistemic State is schema-constrained, provenance-bearing, scope-aware, and explicit about assertion status, certainty, validation references, authority recognition references, and lineage.

It may originate from:

* human authorship;
* institutional datasets;
* collaborative editing;
* Wikidata/Wikibase snapshots;
* research workflows;
* publisher declarations;
* creative worldbuilding;
* mythological corpora;
* automated extraction;
* hybrid human/AI authoring.

**Claim-IR** remains supported, but its role is narrower.

Claim-IR is an extractor proposal profile. It is useful when LLMs, OCR systems, scrapers, parsers, or other extractors propose claims from unstructured sources.

```text
LLM / OCR / parser / scraper
-> Claim-IR
-> Structured Epistemic State
-> Working Exchange
```

But Claim-IR is not the universal required input format.

```text
human expert
-> Structured Epistemic State

institutional dataset
-> Structured Epistemic State

Wikidata seed
-> Structured Epistemic State or Exchange-compatible corpus
```

---

## 9. Core artifact families

Kristal v5 defines several artifact families.

### 9.1 Structured Epistemic State

The normative input unit for compilation.

It contains:

* assertions;
* provenance;
* evidence references;
* source references;
* status metadata;
* certainty metadata;
* scope;
* lineage;
* review references;
* validation references;
* authority recognition references;
* policy references.

### 9.2 Working Exchange

A compiled, content-addressed artifact representing a Structured Epistemic State.

A Working Exchange may contain assertions that are:

* uncertain;
* partial;
* disputed;
* fictional;
* mythological;
* speculative;
* incomplete;
* erroneous;
* not yet validated;
* not yet recognized.

Working Exchange existence does not imply reference status.

### 9.3 Reference Exchange

A compiled artifact recognized under one or more authority channels for a declared scope.

Reference status is scoped. A Reference Exchange recognized by one authority channel is not automatically recognized by another.

A Reference Exchange must preserve traceability to its source state, validation decisions, recognition records, and build metadata.

### 9.4 Runtime Pack

A derived offline-executable artifact optimized for constrained queries.

A Runtime Pack declares:

* its source artifact;
* source artifact status;
* query contract;
* reader policy references;
* validation references where applicable;
* authority recognition references where applicable;
* file inventory;
* build metadata;
* integrity metadata.

A Runtime Pack derived from a Working Exchange is not equivalent to one derived from a Reference Exchange.

Runtime Pack payloads are **derived query materializations**. They MAY use tables, indexes, dictionaries, columnar files, or other profile-defined read-oriented structures. Such materializations MUST NOT become a second writable authority for the source knowledge. For a declared build identity they are immutable and reproducible from the declared source artifact and build inputs.

Kristal v5 core does not standardize a writable SQLite or general-purpose application-database representation. A database-like file MAY be introduced by an explicit Runtime Pack profile only when it is bound to the source artifact/build identity, treated as read-only derived state, and does not alter the authoritative epistemic state.

### 9.5 Shard

A scoped Exchange artifact representing part of a corpus.

A shard may be scoped by:

* domain;
* subdomain;
* jurisdiction;
* tenant;
* environment;
* language;
* time window;
* authority channel;
* dataset boundary.

### 9.6 Federation Manifest

A composition artifact that references multiple shards or exchanges and declares deterministic composition rules.

Federation does not rewrite source shards.

Federation preserves:

* source identity;
* lineage;
* scope;
* authority recognition;
* validation status;
* disagreement.

A federation must not silently merge conflicting assertions as though they agree.

### 9.7 Authority Registry

Pinned, versioned policy data describing:

* authority channels;
* trust roots;
* allowed scopes;
* required profiles;
* recognition rules;
* validation rules;
* revocation policy.

### 9.8 Validation Decision

A machine-readable record that describes validation for a target.

Targets may include:

* assertions;
* artifacts;
* shards;
* datasets;
* authority channels;
* runtime packs.

A validation decision declares:

* target;
* authority channel;
* validation policy;
* scope;
* validation status;
* validated-as mode;
* certainty level;
* findings;
* reason codes;
* signatures where applicable.

### 9.9 Authority Recognition

A record by which one authority channel recognizes a target.

Targets may include:

* assertions;
* artifacts;
* shards;
* datasets;
* runtime packs;
* authority channels.

Authority recognition supports delegated authority and plural validation.

### 9.10 Reader Policy

A machine-readable policy defining what is visible or usable for a reader or application.

Reader Policy is how Kristal supports strict reference views, research views, creative views, institutional views, and custom authority-channel views.

---

## 10. Conceptual flow

Kristal v5 follows this conceptual flow:

```text
Signal / Draft / Dataset / Submission
-> Structured Epistemic State
-> Compile
-> Working Exchange
-> Review / Validation / Attestation / Federation
-> Authority Recognition
-> Reference Exchange
-> Runtime Pack
-> Reader Policy
-> Query / Render / Use
```

This is not a single mandatory workflow. It is a conceptual map.

A project may start from a Wikidata snapshot.
A company may start from its own technical specification.
A researcher may start from an evidence bundle.
A fiction author may start from a fictional world model.
A cultural institution may start from a mythological corpus.
A parser may start from Claim-IR.
A federation may compose multiple shards from different authorities.

The common requirement is that status, certainty, provenance, scope, validation, authority, and lineage remain explicit.

---

## 11. Federation and disagreement

Kristal v5 is designed to make disagreement legible.

Different groups may publish different Kristals about the same domain. Different authorities may recognize different shards. Some assertions may be validated by one authority and rejected by another.

This is allowed.

Federation provides the structure for coexistence:

* source shards keep their identities;
* authority recognition remains scoped;
* conflicts are preserved or handled under explicit policy;
* reader policies decide what is visible by default;
* lineage remains traceable.

A divergent fork may exist. It must not inherit recognition from its source unless that recognition is explicitly granted.

---

## 12. Wikidata alignment

Kristal v5 is designed to be Wikidata/Wikibase-aligned.

A Wikidata Seed Kristal should preserve as much of the source structure as possible, including:

* entities;
* properties;
* statements;
* qualifiers;
* references;
* ranks;
* labels;
* aliases;
* descriptions.

The seed should be understood as Kristal-compatible packaging or alignment of the Wikidata corpus, not as a semantic transformation that changes the meaning of the source data.

Reader policies and export profiles may provide simplified projections, such as truthy or best-rank views, but the source artifact should preserve the richer statement structure where possible.

---

## 13. Integrity and verification

Kristal v5 uses deterministic identity, canonicalization, hashing, signatures, trust roots, manifests, and revocation records to protect artifact integrity.

The v5 canonicalization profile is:

```text
kristal.v5:jcs-rfc8785
```

The v5 canonicalization version is:

```text
1
```

Hash objects use:

```json
{
  "alg": "sha256",
  "value": "<64 lowercase hexadecimal characters>"
}
```

Core hashing rules include:

* use `alg`, not `algo`;
* exclude output ID fields from their own hash targets;
* exclude signatures from primary content hash targets;
* exclude equivalent proof or attestation overlays unless a profile declares otherwise;
* do not let `created_at` affect content-addressed IDs unless explicitly profile-bound.

Integrity verification protects artifact identity and policy satisfaction. It does not itself prove that every assertion is true.

---

## 14. Runtime and offline use

Kristal Runtime Packs are designed for offline and low-bandwidth environments.

Runtime Packs:

* are derived from declared Kristal source artifacts and do not replace those source artifacts;
* do not become writable operational stores for consuming applications;
* do not require live SPARQL endpoints;
* do not require network access for normal local queries;
* do not require LLMs for execution;
* use constrained query contracts;
* preserve source status and reader policy metadata;
* support predictable local execution;
* can be distributed, cached, activated, rolled back, and versioned by Konnaxion.

Offline use does not remove epistemic labels. The reader still needs to know what is validated, by whom, under which scope, with which certainty, and under which reader policy.

---

## 15. Ecosystem roles

### Kristal

Kristal owns:

* compiled epistemic artifacts;
* artifact identity;
* schemas;
* manifests;
* deterministic compilation contracts;
* assertion status;
* certainty metadata;
* validation decision references;
* authority recognition references;
* query contracts;
* reader policy hooks;
* federation semantics.

### Orgo

Orgo owns:

* workflow;
* intake;
* review routing;
* approvals;
* audit;
* lifecycle control;
* release coordination;
* build records;
* operational governance.

### Konnaxion

Konnaxion owns:

* distribution;
* offline access;
* Runtime Pack activation;
* caching;
* rollback;
* reader surfaces;
* search and navigation;
* user-facing policy selection.

### SenTient

SenTient owns:

* resolution;
* disambiguation;
* normalization;
* extraction support;
* Claim-IR profile support;
* ambiguity preservation.

SenTient is useful for extraction and reconciliation workflows, but it is not required for every Structured Epistemic State.

### Architect

Architect owns:

* deterministic rendering;
* traceable summaries;
* multilingual or structured outputs;
* label-preserving generated views.

Architect must not hide authority, certainty, validation status, disputed status, fictional mode, mythological mode, rejection, or revocation when those labels are relevant to the output.

---

## 16. Minimal mental model

A Kristal is not “the truth”.

A Kristal is a structured, portable, verifiable epistemic artifact.

It can contain different kinds of assertions, at different levels of certainty, recognized by different authorities, under different policies, for different scopes.

The important question is not only:

```text
Is this in the Kristal?
```

The important questions are:

```text
What does it claim?
What status does it have?
How certain is it?
Who validates it?
As what?
Under which policy?
For which scope?
Who recognizes it?
Who rejects or disputes it?
Which reader policy is active?
```

Kristal v5 exists to make those answers explicit, portable, queryable, and usable offline.

---

## 17. Document map

* Overview: `00-overview/`
* Normative core: `01-core-spec/`
* Schemas: `02-schemas/`
* Reproducibility: `03-reproducibility/`
* Query and reader policy: `04-query/`
* Profiles: `05-profiles/`
* Integration contracts: `06-integration/`
* Security and tenancy: `07-security/`
* Operational guidance: `08-ops/`
* Test vectors: `09-test-vectors/`
* Examples: `10-examples/`
