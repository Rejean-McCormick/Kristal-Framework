# Vision and scope (Kristal v5)

Kristal is the portable, verifiable, offline-executable unit of structured epistemic knowledge in the ecosystem. A Kristal is **not a document** and not free text. It is a **compiled epistemic artifact** designed to be **Wikidata/Wikibase-aligned**, **traceable**, **AI-ready**, **federable**, and **executable offline**.

Kristal v5 makes structured knowledge usable without pretending that all knowledge has the same status. A Kristal may contain claims, hypotheses, references, myths, technical declarations, research claims, institutional corpora, disputed forks, and validated assertions. The system’s role is to keep those states explicit, queryable, and non-confused.

Validation in Kristal v5 is scoped. It means that an assertion, artifact, shard, authority channel, or dataset is accepted **as something**, **by someone**, **under a policy**, **for a scope**. It does not automatically mean universal truth or maximum certainty.

Certainty is explicit. Readers, applications, institutions, and AI systems can choose policies such as reference-only, validated-only, high-certainty-only, research, creative, or custom authority-channel views.

## Goals

Kristal v5 aims to:

1. **Interoperable identity**

   * Identical content yields identical IDs across languages and toolchains.
   * Hashing and signature verification behavior is fully specified.
   * Artifact identity remains stable across implementations.

2. **Deterministic compilation**

   * Exchange and Runtime Pack generation is reproducible.
   * Build-affecting policies and parameters are recorded in manifests.
   * Compilation does not imply validation, recognition, or reference status.

3. **Structured epistemic states**

   * The normative input unit is a **Structured Epistemic State**.
   * A Structured Epistemic State is schema-constrained, provenance-bearing, scope-aware, and explicit about assertion status and certainty.
   * Claim-IR remains available as an extractor proposal profile, but it is not the universal required input format.

4. **Plural validation**

   * Validation is expressed through authority channels, validation policies, scopes, and validation decisions.
   * An assertion may be validated as a hypothesis, a sourced claim, a high-confidence fact, a publisher declaration, a technical specification, a mythological corpus, a fictional corpus, or a disputed position.
   * Recognition by one authority channel does not imply recognition by every other authority channel.

5. **Explicit certainty**

   * Assertions carry machine-readable certainty levels.
   * A validated assertion does not need to have maximum certainty.
   * A mythology corpus may be valid as mythology; a fictional corpus may be valid as fiction; a technical declaration may be valid as a publisher’s declared system description.

6. **Federated authority**

   * Kristals can be sharded and federated without rewriting source artifacts.
   * Different authorities may recognize different versions of the same corpus, shard, or assertion.
   * Federation preserves disagreement and prevents silent merging of incompatible claims.

7. **Reader policy**

   * Readers and applications choose which authority channels, validation states, certainty levels, and epistemic modes they accept.
   * A “validated-only” reader view means all visible assertions satisfy the active reader policy.
   * It does not mean that all visible assertions are universally true, maximally certain, or accepted by all authorities.

8. **Offline execution**

   * Runtime Packs are executable offline and do not depend on SPARQL endpoints, network access, or LLMs.
   * Query semantics are intentionally constrained to remain predictable and portable.
   * Runtime Packs declare whether they are derived from working artifacts, reference artifacts, or another declared source status.

9. **Standards-aligned exports**

   * Define stable export profiles, including JSON-LD and RDF/WDQS-aligned projections.
   * Preserve Wikidata/Wikibase structures where appropriate, including entities, properties, statements, qualifiers, references, ranks, labels, aliases, and descriptions.
   * Provide optional integrity, provenance, validation, and transparency profiles for high-assurance contexts.

## Non-goals

Kristal v5 does **not** attempt to:

* Provide full SPARQL semantics in Runtime Packs.
* Make every compiled artifact a validated or recognized reference.
* Declare one universal authority over truth.
* Collapse all validation into a single global score.
* Treat all assertions inside a Kristal as having the same certainty.
* Hide disagreement between authority channels.
* Prevent creative, fictional, mythological, speculative, or divergent Kristals from existing.
* Replace Orgo’s operational logging, auditing, workflow, and governance systems.
* Guarantee identical performance across implementations.
* Guarantee truth by artifact existence alone.

Kristal records epistemic structure, provenance, certainty, validation status, recognition status, build metadata, and queryable artifact identity. Orgo records workflow and governance. Konnaxion handles distribution and reader-facing access. Architect renders traceable outputs. SenTient supports resolution and extraction workflows where needed.

## Core model and artifacts

Kristal exists as: **standard + compilation model + artifact contracts + runtime pack**.

### Core artifacts

Kristal v5 defines the following primary artifact families:

1. **Structured Epistemic State**

   * The normative input unit for compilation.
   * Contains assertions, provenance, evidence references, scope, certainty, status, lineage, and policy references.
   * May originate from human authorship, institutional datasets, collaborative editing, automated extraction, research workflows, imported corpora, or hybrid human/AI processes.

2. **Working Exchange**

   * A compiled, content-addressed artifact representing a structured epistemic state.
   * May contain uncertain, partial, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.
   * Must distinguish artifact validity from assertion validity and certainty.

3. **Reference Exchange**

   * A compiled artifact recognized under one or more authority channels for a declared scope.
   * Recognition does not erase uncertainty or disagreement.
   * A Reference Exchange must retain traceability to its source state, validation decisions, and authority recognition records.

4. **Kristal Runtime Pack**

   * A derived, offline-executable indexed form for constrained queries.
   * Optimized for offline distribution and predictable execution.
   * Declares its source artifact status, reader policy references, query contract, build metadata, and integrity material.

5. **Shard**

   * A scoped Exchange artifact representing a domain, subdomain, time window, jurisdiction, tenant, environment, or other declared boundary.
   * Enables smaller offline packages, targeted publication, and distributed authority.

6. **Federation Manifest**

   * A composition artifact that references multiple shards and declares deterministic composition rules.
   * Does not rewrite shard content, shard identity, or source recognition.
   * Preserves disagreement unless an explicit reader policy or composition policy selects otherwise.

7. **Authority Registry**

   * Pinned, versioned policy data defining authority channels, trust roots, allowed scopes, required profiles, recognition rules, and revocation policy.
   * Supports plural authority and scoped recognition.

8. **Validation Decision**

   * A machine-readable record describing the validation status of an artifact, shard, assertion, authority channel, dataset, or runtime pack.
   * Always declares target, authority channel, validation policy, scope, certainty level, and validated-as mode.

9. **Authority Recognition**

   * A record by which one authority channel recognizes an artifact, shard, assertion, dataset, runtime pack, or another authority channel.
   * Supports delegated authority, such as one institution recognizing a specialized authority for a domain.

10. **Reader Policy**

* A machine-readable policy defining which validation statuses, certainty levels, authority channels, scopes, and epistemic modes are visible to a reader or application.
* Enables reference-only, validated-only, high-certainty-only, research, creative, all-with-labels, and custom views.

### Conceptual flow

1. **Signal / Draft / Dataset / Submission**

   * Documents, datasets, Wikidata/Wikibase corpora, institutional submissions, research claims, creative corpora, operational signals, human drafts, or extractor outputs.

2. **Structured Epistemic State**

   * Assertions are represented with status, certainty, provenance, evidence, scope, lineage, and policy references.

3. **Compile**

   * A deterministic compiler produces a Working Exchange.
   * Compilation records build-affecting inputs, compiler identity, policy selections, configuration hashes, and output identities.

4. **Review / Validation / Attestation**

   * Assertions, artifacts, shards, datasets, or authority channels may be reviewed, validated, rejected, disputed, revoked, or recognized.
   * Validation decisions are scoped and authority-bound.

5. **Authority Recognition**

   * An authority channel may recognize a target as a reference for a declared scope.
   * Authorities may also recognize other authorities.

6. **Reference Exchange**

   * A Working Exchange may become a Reference Exchange under one or more authority channels.
   * Reference status is not universal unless explicitly recognized by the relevant authority channels.

7. **Federation**

   * Multiple shards or reference artifacts can be composed without rewriting them.
   * Composition policies define precedence, conflict behavior, visibility, and reader policy defaults.

8. **Runtime Pack**

   * Offline executable packs are compiled from declared source artifacts.
   * Packs preserve source status, authority references, validation references, and reader policy metadata.

9. **Render / Query / Use**

   * Architect, Konnaxion, AI systems, readers, and other consumers query or render Kristal data.
   * Rendering must preserve labels for validation, authority, certainty, disagreement, fiction, mythology, and rejected or disputed status.

## Normative core vs profiles

Kristal v5 is structured as:

* **Core (normative, required):** artifact identity, deterministic compilation, Structured Epistemic State, assertion status, certainty, validation decisions, authority recognition, federation basics, reader policy hooks, and constrained query behavior.
* **Profiles (optional, standardized):** advanced features for export, validation, provenance, transparency, pagination, RDF integrity, and high-assurance distribution.

### v5 Core includes

* RFC 8785 (JCS) canonicalization for hashed JSON objects.
* Explicit hashing material and exclusions.
* Signatures excluded from hashed payloads.
* Output ID fields excluded from their own hash targets.
* `created_at` excluded from content-addressed IDs unless a profile explicitly says otherwise.
* Standard hash object shape using `alg`, not `algo`.
* Deterministic build requirements and reproducible manifests.
* Structured Epistemic State contracts.
* Assertion status and certainty model.
* Validation Decision records.
* Authority Recognition records.
* Authority Registry contracts.
* Federation and sharding contracts.
* Reader Policy contracts.
* Core schemas and core test vectors.
* Required verification for declared hashes, signatures, trust roots, compatibility constraints, and revocation policies.

### Profiles include

* JSON-LD export profile.
* RDF/WDQS-aligned export profile.
* RDF Integrity profile using RDFC and resource limits.
* Provenance packaging profile using nanopublication and PROV-O patterns.
* Validation profiles such as SHACL and ShEx.
* Query pagination profile with TPF-like semantics.
* Transparency Log profile for recognition, validation, revocation, and correction events.
* Reader Policy profiles for reference-only, validated-only, high-certainty, research, creative, and custom views.

## Ecosystem integration placement (Orgo × SenTient × Architect × Konnaxion)

* **Orgo**

  * Operational control plane for Kristal workflows.
  * Owns intake, review routing, approvals, audit, lifecycle, release coordination, and operational governance.
  * Records workflow state, build records, review records, distribution status, and governance events.

* **SenTient**

  * Resolver and reconciler for extraction-oriented workflows.
  * Supports Claim-IR as an extractor proposal profile.
  * Performs disambiguation, normalization, candidate ranking, and unresolved ambiguity preservation where needed.
  * Is not required for every Structured Epistemic State.

* **Architect**

  * Deterministic renderer consuming Kristal query results and producing traceable outputs.
  * Must not introduce unsupported facts.
  * Must preserve labels for certainty, validation, authority channel, recognition status, disputed status, fictional mode, mythological mode, and rejected status.
  * Must not flatten scoped validation into universal truth.

* **Konnaxion**

  * Distribution, offline UX, search, navigation, reader policy, and Runtime Pack access layer.
  * Handles reader-facing policy selection, caching, versioning, verification, rollback/downgrade rules, and low-bandwidth access.
  * Allows users, institutions, and applications to choose which authority channels and certainty levels they accept.

Operational patterns such as circuit breakers, DLQs, CQRS framing, canary/blue-green rollout, structured logs, and correlation IDs are used as **non-normative guidance** for the build and distribution system. They are not embedded into Kristal artifact schemas unless a specific profile declares them.

## Document map

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


## Domain-neutral referents (rc.3)

Kristal may identify the things assertions are about through Referent Registry `1.0.0`. The registry is deliberately shallow: it distinguishes stable referent kinds such as person, collective, work, concept, place, installation and process without imposing a universal domain ontology.

Assertions, provenance, evidence, certainty, validation and authority remain in Structured Epistemic State. A consumer's primary navigation lens is a projection choice rather than a Kristal semantic priority. External IDs such as Wikidata QIDs remain external anchors.
