# Kristal docs (v5)

> **Release status:** `5.0.0-rc.1` — stabilization release candidate. See [`VERSION`](VERSION), [`kristal-release.json`](kristal-release.json), the [release status report](docs/status/2026-09-14-v5.0.0-rc.1.md), and the [specification status](docs/Technical-Reference/kristal-docs-v5/00-overview/specification-status.md).

This repository contains the **Kristal v5 specification, normative contract set, conformance vectors, and release metadata** for a deterministic, portable epistemic artifact system.

Kristal v5 defines how **Structured Epistemic States** are compiled into immutable, portable, queryable, and verifiable artifacts while separating:

* **artifact existence** from **artifact integrity**
* **compilation** from **validation**
* **working artifacts** from **reference artifacts**
* **assertion status** from **certainty level**
* **validation status** from **authority recognition**
* **authority recognition** from **reader visibility**
* **distribution** from **runtime activation**

Kristal is designed for portable, verifiable, offline-capable knowledge operation across toolchains, authority channels, reader policies, and runtime environments.

---

## Release identity

The current release candidate is `v5.0.0-rc.1`. The release identity is deliberately small:

```text
version: 5.0.0-rc.1
git tag: v5.0.0-rc.1
git commit: resolved from the tag after the release commit exists
canonicalization: kristal.v5:jcs-rfc8785
```

Git tag + commit SHA pin the exact repository content. [`contract-set.manifest.json`](contract-set.manifest.json) only identifies the public contract surfaces; it is not an exhaustive file inventory and does not duplicate Git with per-file release hashes.

Kristal still uses JCS/SHA-256 where it is part of the **Kristal artifact identity protocol**. That domain-level hashing is separate from framework release versioning. See the [release status report](docs/status/2026-09-14-v5.0.0-rc.1.md) and [`RELEASE.md`](RELEASE.md).

---

## Start here

1. `docs/Technical-Reference/kristal-docs-v5/00-overview/what-is-kristal-v5.md`
2. `docs/Technical-Reference/kristal-docs-v5/00-overview/vision-and-scope.md`
3. `docs/Technical-Reference/kristal-docs-v5/00-overview/validation-certainty-and-authority.md`
4. `docs/Technical-Reference/kristal-docs-v5/00-overview/plural-validation-and-federated-authority.md`
5. `docs/Technical-Reference/kristal-docs-v5/00-overview/conformance-and-alignment.md`
6. `docs/Technical-Reference/kristal-docs-v5/01-core-spec/kristal-v5-core-spec.md`

If you are implementing specific surfaces:

* Core model, artifact lifecycle, and validation boundaries → `docs/Technical-Reference/kristal-docs-v5/01-core-spec/kristal-v5-core-spec.md`
* Structured Epistemic State → `docs/Technical-Reference/kristal-docs-v5/01-core-spec/structured-epistemic-state.md`
* Assertion status and certainty → `docs/Technical-Reference/kristal-docs-v5/01-core-spec/assertion-status-and-certainty.md`
* Authority recognition → `docs/Technical-Reference/kristal-docs-v5/01-core-spec/authority-recognition.md`
* IDs, technical canonicalization, and hashing → `docs/Technical-Reference/kristal-docs-v5/01-core-spec/ids-canonicalization-hashing.md`
* Signatures and trust roots → `docs/Technical-Reference/kristal-docs-v5/01-core-spec/signatures-trust.md`
* Normative JSON Schemas → `docs/Technical-Reference/kristal-docs-v5/02-schemas/`
* Reproducibility and build surfaces → `docs/Technical-Reference/kristal-docs-v5/03-reproducibility/`
* Offline query surface → `docs/Technical-Reference/kristal-docs-v5/04-query/query-contract.md`
* Reader policy profiles → `docs/Technical-Reference/kristal-docs-v5/04-query/reader-policy-profiles.md`
* Optional interoperability profiles → `docs/Technical-Reference/kristal-docs-v5/05-profiles/`
* Ecosystem contracts: Orgo, SenTient, Architect, Konnaxion → `docs/Technical-Reference/kristal-docs-v5/06-integration/`
* Security, trust roots, downgrade policy, rollback policy, and multi-tenancy → `docs/Technical-Reference/kristal-docs-v5/07-security/`
* Operational guidance → `docs/Technical-Reference/kristal-docs-v5/08-ops/`
* Golden vectors and fixtures → `docs/Technical-Reference/kristal-docs-v5/09-test-vectors/`
* Worked examples → `docs/Technical-Reference/kristal-docs-v5/10-examples/`

---

## What Kristal v5 is

Kristal v5 is a deterministic artifact system for compiling structured epistemic work.

It allows claims, hypotheses, references, myths, fictional corpora, technical declarations, research claims, institutional corpora, and disputed positions to coexist without confusion.

Core principles:

* **Validation is scoped.**
* **Authority is plural.**
* **Certainty is explicit.**
* **Readers choose policy.**
* **Federation preserves disagreement.**
* **Integrity protects artifacts.**

A Kristal may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.

A Kristal must not present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

---

## Core model

Kristal v5 keeps the following concepts separate:

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

This separation is the basis for v5 conformance.

An artifact can be well-formed, signed, content-addressed, reproducible, queryable, and distributable while still containing assertions that are hypothetical, disputed, fictional, mythological, low-certainty, rejected by one authority channel, recognized by another, or hidden by a reader policy.

---

## Core pipeline

The v5 model is:

```text
Signal / Draft / Dataset / Submission
-> Structured Epistemic State
-> Compile
-> Working Artifact
-> Review / Validation / Attestation / Federation
-> Authority Recognition
-> Reference Artifact
-> Distribution / Runtime Pack / Reader Policy
```

Compilation creates portable artifacts.

Validation evaluates assertions, artifacts, or datasets under declared policy and scope.

Authority recognition records which authority channel recognizes what, for which scope, and under which policy.

Reader policy determines what a reader or runtime is allowed to see.

---

## Input model

The normative input unit for Kristal v5 is the **Structured Epistemic State**.

`Claim-IR` may be used by extractors, resolvers, or ingestion pipelines, but it is not the universal required input boundary for Kristal v5.

A conformant v5 pipeline may compile from:

* Structured Epistemic State
* extractor proposals projected into Structured Epistemic State
* institutional datasets
* research submissions
* local notes
* mythology or fiction corpora
* technical declarations
* authority-recognized reference artifacts
* federated shard inputs

All inputs must make their provenance, scope, certainty, and validation metadata explicit when those fields are applicable.

---

## Artifact classes

Kristal v5 distinguishes at least the following artifact classes.

### 1. Structured Epistemic State

A schema-constrained, versioned, provenance-bearing assertional state suitable for compilation.

Typical contents:

* identity and revision metadata
* scope and tenant metadata where applicable
* assertions
* assertion status
* certainty level
* validation metadata
* authority recognition references
* provenance references
* evidence references
* lineage
* review or attestation references

### 2. Working Exchange

A compiled artifact representing a working epistemic state.

Properties:

* immutable
* content-addressed
* queryable
* portable
* reproducible within its declared surface
* explicitly marked as `working`

A Working Exchange may contain unvalidated, disputed, low-certainty, fictional, mythological, speculative, or incomplete assertions when those statuses are explicit.

### 3. Reference Exchange

An Exchange recognized for one or more declared scopes by one or more authority channels.

A Reference Exchange does not imply universal agreement or universal certainty. It means the artifact has been accepted as a reference under declared authority, validation, certainty, and scope constraints.

### 4. Validation Report

A scoped artifact recording validation findings, validation status, certainty level, validated-as classification, policy references, and evidence references.

A validation report may validate an assertion, artifact, shard, dataset, runtime pack, authority channel, reader policy, or federation surface.

### 5. Authority Recognition

An artifact recording recognition by an authority channel.

Authority recognition is scoped. It may be conditional, disputed, deprecated, revoked, rejected, or limited to a domain, jurisdiction, environment, tenant, language, or time window.

### 6. Federation Manifest

A manifest describing composition across shards, authority channels, reader policies, validation policies, and disagreement-preserving federation rules.

Federation does not erase disagreement. It preserves source identity, authority channel, scope, status, certainty, and validation metadata.

### 7. Runtime Pack

An offline-capable runtime/query representation derived from an Exchange or shard set.

A Runtime Pack must preserve source artifact status, reader policy constraints, validation labels, certainty labels, authority labels, and lineage.

---

## Trust and recognition model

Kristal v5 separates **artifact integrity** from **authority recognition**.

Integrity asks:

* Is the artifact well-formed?
* Does the hash match?
* Does the signature verify?
* Are the declared technical canonicalization and hashing rules satisfied?
* Is the artifact reproducible under its declared build surface?

Authority recognition asks:

* Which authority channel recognizes this artifact, assertion, dataset, shard, or policy?
* Under what scope?
* Under what validation policy?
* At what certainty level?
* As what kind of assertion or corpus?
* With what status?
* With what revocation or supersession rules?

Reader visibility asks:

* Which reader policy is active?
* Which statuses are allowed?
* Which authorities are allowed?
* Which certainty levels are allowed?
* Which domains and scopes are allowed?
* Which labels must remain visible?

Kristal v5 does not flatten these layers into a single status.

---

## Reader policies

Reader policies determine what material is visible or usable for a reader, runtime, export, or rendering surface.

Standard reader modes include:

* `reference_only`
* `validated_only`
* `high_certainty_only`
* `research`
* `creative`
* `all_with_labels`
* `custom`

A validated-only reader policy does not mean every visible assertion is a universal fact. It means every visible assertion satisfies that reader policy’s validation, authority, certainty, and scope filters.

For example, a validated-only reader policy may include:

* high-confidence scientific facts
* institutional references
* publisher declarations
* technical specifications
* legal or policy positions
* mythological corpora
* fictional corpora
* symbolic models
* disputed positions

provided those assertions are explicitly validated as such under the active policy.

---

## Conformance model

### v5 Core

Implementations claiming **Kristal v5 Core** conformance must, at minimum:

* support Structured Epistemic State as the normative input unit
* distinguish working artifacts from reference artifacts
* distinguish artifact status from assertion status
* distinguish certainty level from validation status
* distinguish validation status from authority recognition
* distinguish authority recognition from reader visibility
* support deterministic compilation within the declared reproducibility surface
* use the declared technical canonicalization and hashing rules for identity-bearing artifacts
* preserve traceability from compiled artifacts back to provenance-bearing source states
* preserve validation labels, certainty labels, authority labels, scope labels, and lineage
* produce manifests recording build-affecting configuration, policy, source identity, and compiler identity
* enforce required verification where hashes, signatures, trust roots, revocation checks, or runtime activation rules are declared as mandatory
* pass the core test vectors in `docs/Technical-Reference/kristal-docs-v5/09-test-vectors/`

### Profiles

Advanced capabilities are expressed as explicit profiles in `docs/Technical-Reference/kristal-docs-v5/05-profiles/`.

Implementations may claim profile conformance individually, including profiles such as:

* JSON-LD export
* RDF integrity and RDF dataset canonicalization
* Wikidata/Wikibase export
* SHACL validation
* ShEx validation
* provenance packaging
* transparency logs
* query pagination

Profiles must:

* state requirements and limits
* state what is hashed, signed, or identity-bearing
* state whether they affect reproducibility surfaces
* include conformance tests or fixtures where applicable
* preserve Kristal v5 labels for status, certainty, validation, authority, scope, and lineage

---

## Repository structure

* `docs/Technical-Reference/kristal-docs-v5/00-overview/` — scope, concepts, conformance, federation, authority, and ecosystem placement
* `docs/Technical-Reference/kristal-docs-v5/01-core-spec/` — normative core specification, artifact model, status model, authority model, signatures, IDs, and hashing
* `docs/Technical-Reference/kristal-docs-v5/02-schemas/` — normative JSON Schemas for v5 artifacts
* `docs/Technical-Reference/kristal-docs-v5/03-reproducibility/` — deterministic compilation rules, identity surfaces, runtime pack policies, and acceptance tests
* `docs/Technical-Reference/kristal-docs-v5/04-query/` — offline query contract and reader policy profiles
* `docs/Technical-Reference/kristal-docs-v5/05-profiles/` — optional standardized profiles
* `docs/Technical-Reference/kristal-docs-v5/06-integration/` — inter-system contracts for Orgo, SenTient, Architect, and Konnaxion
* `docs/Technical-Reference/kristal-docs-v5/07-security/` — trust roots, key management, downgrade and rollback policy, and multi-tenancy boundaries
* `docs/Technical-Reference/kristal-docs-v5/08-ops/` — operational guidance and release patterns
* `docs/Technical-Reference/kristal-docs-v5/09-test-vectors/` — golden vectors for canonicalization, hashing, manifests, and identity-bearing surfaces
* `docs/Technical-Reference/kristal-docs-v5/10-examples/` — worked examples for implementers

---

## Editing rules

* Normative language uses **MUST**, **SHOULD**, **MAY**, **MUST NOT**, and **SHOULD NOT**.
* Keep the core small and explicit.
* Do not hide optional behavior inside undocumented extensions.
* Any optional behavior that affects identity, trust, reproducibility, query semantics, reader visibility, or distribution must be expressed as a profile or an explicitly versioned core rule.
* Do not conflate:

  * compile with validate
  * working with reference
  * validation with authority recognition
  * authority recognition with reader visibility
  * certainty with validation status
  * artifact integrity with assertion validity
  * technical canonicalization with epistemic authority

---

## Versioning

Any change that affects hashes, IDs, deterministic outputs, schema semantics, validation semantics, authority recognition, reader policy behavior, runtime activation, or trust-surface behavior requires:

* updated test vectors in `docs/Technical-Reference/kristal-docs-v5/09-test-vectors/`
* an explicit version bump in the relevant schema, profile, policy, or artifact identifier
* compatibility guidance where applicable
* clear notes explaining the affected conformance surface

Major-version changes are required for changes that alter:

* core artifact classes
* identity-bearing technical canonicalization or hashing rules
* compile, validation, or recognition semantics
* trust-surface semantics
* reader policy semantics
* runtime compatibility guarantees

---

## One-sentence definition

> Kristal v5 is a deterministic, portable epistemic artifact system that compiles Structured Epistemic States into verifiable artifacts while keeping validation scoped, authority plural, certainty explicit, reader policy selectable, and disagreement preserved.
