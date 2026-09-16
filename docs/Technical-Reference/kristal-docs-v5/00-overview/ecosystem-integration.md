# Kristals in the Ecosystem: Konnaxion × Orgo × Architect × SenTient

## 1) What “Kristal” is in your stack

**Kristal is the portable, offline-usable epistemic artifact format of the kOA ecosystem.** It is not a document and not free text; it is a **compiled knowledge artifact** designed to be **Wikidata/Wikibase-aligned**, **traceable**, **AI-ready**, **queryable**, and **usable offline**.

A Kristal can contain claims, hypotheses, references, institutional records, technical declarations, mythological corpora, fictional structures, disputed positions, and high-confidence factual knowledge. The point is not that every Kristal is automatically true. The point is that its claims carry explicit structure: provenance, scope, authority channel, validation status, certainty level, lineage, and reader-policy visibility.

Kristal exists as a **standard + compilation model + exchange format + runtime pack**:

* **Structured Epistemic State**: the normative input unit for Kristal v5. It represents structured claims, evidence, uncertainty, provenance, scope, and status before they become portable artifacts.
* **Claim-IR**: an extractor proposal profile. Probabilistic extractors such as LLMs, classical extractors, OCR systems, and hybrids may emit Claim-IR, but Claim-IR is not the universal required input to Kristal.
* **Resolution (SenTient)**: maps surface forms to candidate QIDs/PIDs, normalizes values, and preserves unresolved ambiguity instead of forcing premature certainty.
* **Validation & Recognition**: scoped decisions made by declared authority channels under explicit validation policies. Validation does not always mean maximum certainty; it means accepted as something, by someone, for some scope, under some policy.
* **Kristal Exchange**: Wikibase-aligned, content-addressed structured reference artifact. It is the artifact you cite, inspect, compare, federate, and use as the source for runtime packs.
* **Kristal Runtime Pack**: derived, offline-usable indexed form optimized for constrained query and local access. It does not require SPARQL, a live network, or an LLM dependency.
* **Deterministic Rendering (Architect)**: renders query results into natural language or other user-facing outputs while preserving Kristal labels: authority, validation status, certainty, scope, and disagreement.

## 2) Landscape: where Kristals sit

**Kristals sit between messy reality and user-facing platforms + operational systems**, as the structured knowledge substrate that makes claims portable, inspectable, filterable, and reusable.

They are not meant to erase disagreement. They make disagreement legible.

**High-level flow: authoring → structuring → validation/recognition → distribution → use → feedback**

### A. Inputs

Inputs may include:

* documents;
* web pages;
* PDFs;
* datasets;
* emails or archives;
* institutional submissions;
* human expert drafts;
* research notes;
* cultural corpora;
* fictional or mythological material;
* optional hints, mappings, or source references.

### B. Knowledge compilation

The Kristal stack turns inputs into structured artifacts:

* input material or dataset;
* Structured Epistemic State;
* optional Claim-IR when extraction is probabilistic;
* SenTient resolution and normalization;
* validation decisions, authority recognition, review records, and provenance;
* Kristal Exchange;
* Runtime Pack.

Compilation and validation are distinct. A system may compile a working artifact before final recognition. Reader policies then decide which artifacts or assertions are visible in a given context.

### Operational-state boundary

Kristal does not replace the operational databases of ecosystem products. Mutable product state remains owned by the product responsible for that domain. Knowledge compilation consumes immutable source-owned exports/snapshots or stable artifact references carrying revision/digest and provenance.

The authority direction is one-way:

```text
product operational state
  -> immutable source artifact / snapshot
  -> Kristal epistemic artifact
  -> deterministic Runtime Pack materialization
```

The layers are linked by references and lineage, not by bidirectional database synchronization or distributed dual writes. In the **kOA deployment profile**, Da’at is the mapping boundary that translates source-owned artifacts into Kristal-native epistemic structures; Interaction Kernel may transport requests, ArtifactRefs, receipts, and completion events, but owns neither product state nor Kristal artifact storage.

### C. Consumers in the ecosystem

* **Konnaxion** consumes Kristals to power discovery, search, navigation, knowledge delivery, education, civic workflows, collective curation, and offline-oriented user experiences.
* **Orgo** consumes Kristals to turn knowledge into operational work, and produces operational signals that can trigger new Kristal builds, reviews, validations, or revisions.
* **Architect** consumes Kristal query results and produces deterministic multilingual text or other generated outputs while preserving labels and not laundering scoped validation into universal truth.
* **SenTient** is the reconciliation engine that bridges unstructured or ambiguous inputs into Wikidata/Wikibase-shaped identifiers and normalized values.

## 3) Clear role boundaries

### Kristal: the epistemic substrate

**Primary job:** produce portable, traceable, queryable, offline-usable knowledge artifacts with deterministic identity, provenance, status, and policy-aware semantics.

Kristal owns:

* structured epistemic states;
* exchange artifacts;
* runtime pack manifests;
* schemas;
* content-addressed identity;
* canonicalization for hashing;
* signatures and trust roots;
* assertion status;
* certainty metadata;
* authority recognition references;
* validation decision references;
* federation manifests;
* query contracts.

**Non-goals:**

* Kristal is not a workflow engine.
* Kristal is not a voting system.
* Kristal is not a user interface.
* Kristal is not a shared mutable application database or operational system of record.
* Kristal is not a bidirectional database synchronization layer between products.
* Kristal is not a monopoly over truth.
* Kristal Runtime Packs do not need full SPARQL semantics; they intentionally constrain query execution to remain offline, predictable, and portable.

### SenTient: the resolver / reconciler

**Primary job:** convert ambiguity into ranked candidate identities and normalized values.

SenTient handles:

* surface-form detection;
* QID/PID candidate generation;
* semantic ranking;
* value normalization;
* ambiguity preservation;
* confidence signals;
* reconciliation warnings.

SenTient does not decide universal truth. It provides resolution support that downstream Kristal validation policies may use.

### Architect: the deterministic renderer

**Primary job:** transform Kristal query results into deterministic text or other user-facing outputs without changing the epistemic status of the underlying claims.

Architect must preserve:

* validation labels;
* authority labels;
* certainty labels;
* scope labels;
* disputed status;
* fictional, mythological, symbolic, or speculative mode when applicable.

Architect must not flatten scoped validation into universal truth.

### Konnaxion: the mass platform layer

**Primary job:** provide a unified multi-module platform with global navigation, search, content delivery, offline access, collective intelligence, and public-facing knowledge surfaces.

Konnaxion uses Kristals as:

* search primitives;
* offline knowledge payloads;
* educational references;
* debate references;
* civic-process references;
* curation targets;
* distribution units;
* user-selectable knowledge layers.

Konnaxion can expose different reader policies, such as validated-only, reference-only, research, creative, or all-with-labels.

### Orgo: the operating system layer

**Primary job:** ingest messy signals and turn them into structured work under operational constraints such as multi-tenancy, identity separation, auditability, offline sync, routing, approvals, and lifecycle management.

Orgo handles:

* cases;
* tasks;
* assignments;
* approvals;
* review workflows;
* validation requests;
* publication workflows;
* distribution status;
* operational audit logs;
* feedback loops;
* sync conflicts.

Orgo does not own the Kristal knowledge payload. It orchestrates the work around that payload. Conversely, Kristal does not own Orgo Cases, Tasks, Workflow state, outbox/retry state, or other mutable Orgo operational records. Orgo contributes knowledge through immutable snapshots/artifact references rather than dual-writing live records into Kristal.

## 4) The place of Kristals inside each product

### 4.1 Kristals inside Konnaxion

Konnaxion’s platform structure is ideal for Kristals because it already wants:

1. one global search/navigation layer across modules;
2. offline and low-bandwidth delivery modes;
3. weighted curation and expert review workflows;
4. versioned offline packages;
5. public-facing knowledge surfaces;
6. support for civic disagreement without silent merging.

**Concrete placement:**

* **Kristal Runtime Packs become offline knowledge payloads** distributed to devices, users, schools, organizations, regions, or communities.
* **Kristal Exchanges become auditable structured references** for knowledge items that Konnaxion modules can cite, compare, discuss, rank, or attach to civic processes.
* **Konnaxion reader policies decide what users see by default.** A user or institution may choose a strict view containing only selected authority channels and validated material, or a broader research/creative view that includes hypotheses, disputed material, mythology, fiction, or divergent forks with labels.
* **Ekoh/Konsensus can weight recognition, visibility, distribution priority, featured packs, recommended references, or curation status** without pretending that a vote alone decides physical-world truth.
* **Smart Vote and other civic mechanisms can refer to Kristals** as structured evidence or policy references while preserving the difference between claims, validation, authority, and certainty.

**What this unlocks on massive platforms:**

* a consistent knowledge primitive for feeds, search results, debate references, educational modules, and moderation/verification badges;
* offline access without relying on live endpoints;
* transparent disagreement between authority channels;
* user-selectable trust and certainty layers;
* structured feedback that can become future Kristal work.

### 4.2 Kristals inside Orgo

Orgo is about converting messy signals into structured work and doing it safely at scale: multi-tenant, identity-aware, auditable, and offline-capable.

**Concrete placement:**

* **Orgo becomes the operational control plane for Kristal production, review, validation, recognition, publication, and distribution.**
* When Orgo ingests signals such as email, HTTP submissions, offline imports, documents, or datasets, it can trigger “needs-a-kristal” workflows.
* Orgo can create Cases and Tasks for structuring, extraction, reconciliation, review, validation, authority recognition, release, revocation, and update.
* Orgo’s offline nodes and sync sessions can distribute Kristal packs to constrained environments such as schools, field devices, regulated deployments, local communities, or disaster-response contexts.
* Orgo feedback can trigger new Kristal versions, new authority decisions, new review bundles, or new divergent forks.

**Orgo ↔ Kristal division of labor:**

* Orgo stores assignments, cases, approvals, review workflows, operational audit logs, distribution status, sync conflicts, and lifecycle events.
* Kristal stores the structured epistemic payload: assertions, provenance, scopes, validation decisions, authority recognitions, exchange artifacts, runtime packs, and query contracts.

### 4.3 Kristals inside SenTient

SenTient provides the resolution layer that maps ambiguity into structured identifiers and normalized values.

Kristal relies on SenTient where inputs contain unresolved ambiguity:

* ambiguous names;
* entity references;
* property references;
* dates;
* units;
* multilingual labels;
* partial statements;
* conflicting identifiers;
* uncertain mappings.

SenTient’s funnel architecture operationalizes this at scale:

1. fast candidate spotting;
2. semantic scoring;
3. ranking;
4. QA / judging;
5. unresolved ambiguity preservation.

**Concrete placement:**

* SenTient acts as the resolver service for Claim-IR and other structured input profiles.
* SenTient outputs ranked candidates, normalized values, warnings, and unresolved ambiguity records.
* Those outputs feed Kristal validation, review, and reference-building processes.
* SenTient does not force certainty when evidence is insufficient.
* SenTient does not replace authority recognition. It supports it.

### 4.4 Kristals inside Architect

Architect renders Kristal query results into human-facing output.

Architect is already designed as a build pipeline with clear stages:

* filesystem;
* indexer;
* JSON;
* orchestrator/factory;
* compiled artifacts;
* worker/API.

Kristal gives Architect a structured epistemic source to render from.

**Concrete placement:**

* Architect consumes queries over Kristal Runtime Packs or Exchange-derived query results.
* Architect produces human-readable articles, snippets, multilingual variants, structured educational pages, summaries, civic explanations, and interface text.
* Architect must preserve claim status, validation status, certainty level, authority channel, and scope.
* Architect can render different reader-policy modes:

  * reference-only;
  * validated-only;
  * high-certainty-only;
  * research;
  * creative;
  * all-with-labels;
  * custom authority channels.

Architect’s deterministic ethos aligns with Kristal’s model: preserve uncertainty, preserve labels, be deterministic in rendering, and do not introduce unsupported facts.

## 5) The core operating loop

### Loop 1: Reality → Kristal

1. **Signal enters** through Konnaxion submission, Orgo case, email/import/API, web/PDF ingestion, dataset import, institutional submission, or human-authored draft.
2. **Structured Epistemic State is produced** with claims, status, scope, provenance, evidence, uncertainty, and lineage.
3. **Claim-IR may be used** when the source is probabilistic extraction, but it is not mandatory for all inputs.
4. **SenTient resolves** surfaces to ranked QIDs/PIDs and normalized values when resolution is needed.
5. **A working Kristal Exchange is compiled** as a structured, content-addressed artifact.
6. **Review, validation, and authority recognition occur** according to explicit policies.
7. **Some artifacts or assertions become recognized references** under one or more authority channels.
8. **Runtime Packs are compiled** for offline access and constrained query execution.

### Loop 2: Kristal → People

9. **Konnaxion distributes** runtime packs and reference surfaces through versioned packages, PWA/offline mode, low-bandwidth UX, and platform search/navigation.
10. **Architect renders** user-facing text from Kristal query results while preserving labels and policies.
11. **Orgo operationalizes** gaps, verification requests, publication processes, distribution issues, and review needs.

### Loop 3: People → System feedback

12. **Feedback becomes structured signals** through Orgo cases, Konnaxion votes, curation signals, expert reviews, institutional updates, user reports, and conflicting submissions.
13. **Feedback can trigger new Kristals**, updated authority decisions, revisions, revocations, forks, or new reader-policy surfaces.

## 6) Validation, certainty, and reader policy

Kristal separates five things that are often confused:

1. artifact existence;
2. artifact integrity;
3. assertion status;
4. certainty level;
5. authority recognition;
6. reader visibility.

A Kristal may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.

A Kristal must not present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

### Validation

Validation answers:

* Who accepts this?
* Under which policy?
* For which domain or scope?
* As what kind of assertion?

Validation does not always mean high certainty.

An assertion may be validated as:

* a hypothesis;
* a sourced claim;
* a reviewed claim;
* a high-confidence fact;
* an institutional reference;
* a publisher declaration;
* a technical specification;
* a legal or policy position;
* a mythological corpus;
* a fictional corpus;
* a symbolic model;
* a disputed position;
* a rejected claim.

### Certainty

Certainty answers how strong the assertion is within its declared scope.

A simple certainty ladder can include:

* unknown;
* speculative;
* low;
* medium;
* high;
* established;
* not applicable.

“Not applicable” is useful for fiction, mythology, symbolic models, doctrine, publisher declarations, or other cases where physical-world certainty is not the right measure.

### Reader policy

People and applications can choose how strict they want the reading surface to be.

Examples:

* **reference-only**: show only material recognized as reference by selected authority channels;
* **validated-only**: show only material accepted under chosen validation policies, even if some claims are validated as hypotheses or low-certainty statements;
* **high-certainty-only**: show only high or established certainty claims;
* **research**: include hypotheses, disputed claims, drafts, and lower-certainty material with visible labels;
* **creative**: include fictional, mythological, speculative, or symbolic Kristals when the user intentionally enters that scope;
* **all-with-labels**: show everything allowed by access control, while keeping labels visible;
* **custom**: let the user, institution, or application select authority channels, scopes, and certainty thresholds.

“100% validated data” means that all visible assertions satisfy the active reader policy. It does not mean all assertions have maximum certainty, all authorities agree, or all statements are universally true.

## 7) Federation and plural authority

Kristal does not assume one universal authority over truth.

Different authorities may publish, approve, reject, recognize, or fork different versions of the same corpus, shard, or assertion. A government, association, company, research collective, expert body, religious community, standards organization, international institution, AI-assisted validator, or individual may participate under explicit scope and policy.

Federation keeps those views composable without silently merging them.

A federation manifest should preserve:

* source identity;
* shard identity;
* publisher identity;
* authority channel;
* validation policy;
* certainty level;
* recognition status;
* lineage;
* conflict strategy;
* reader policy.

The default federation rule is:

**Preserve disagreement. Do not silently merge conflicting claims. Do not let one authority masquerade as another.**

### Authority recognition

Authority channels may recognize other authority channels.

Examples:

* UNESCO may recognize WHO for public-health reference material.
* A government may recognize its national statistics agency for demographic datasets.
* A standards body may recognize a technical working group for a specification.
* A university may recognize a lab for a research shard.
* A company may be the primary authority on the declared structure of its own systems, while other authorities may evaluate safety, compliance, environmental claims, or social impact.

Recognition by one authority channel does not imply recognition by every other channel.

## 8) Practical deployment model

### Model A — Kristals as an internal backbone

This is the recommended first deployment model.

* **Orgo runs the Kristal workflow**: ingest → structure → resolve → review → validate → recognize → publish → distribute.
* **SenTient runs as a resolution service** invoked by the workflow when ambiguity needs reconciliation.
* **Kristal produces Exchange artifacts and Runtime Packs**.
* **Konnaxion consumes Runtime Packs** for offline knowledge delivery, search, navigation, education, curation, and civic workflows.
* **Architect consumes Kristal query results** for deterministic publishing and multilingual output.
* **Reader policies control visibility** according to user, institution, domain, scope, and selected authority channels.

Outputs per release may include:

* Structured Epistemic State;
* working Exchange;
* reference Exchange;
* authority recognition records;
* validation decisions;
* federation manifest;
* runtime pack;
* query contract;
* reader policies;
* revocation or update records when needed.

### Model B — Kristals as a public standard

Once stable internally, the Kristal format can be published externally as the interoperability layer for portable epistemic artifacts.

The public standard should expose:

* schemas;
* exchange manifests;
* runtime pack manifests;
* validation decision formats;
* authority recognition formats;
* reader policy profiles;
* federation manifests;
* query contracts;
* examples for Wikidata-aligned data, research claims, institutional submissions, mythology, fiction, disputed forks, and authority-recognized references.

Orgo and Konnaxion remain operational advantages: they provide workflow, distribution, adoption, offline access, and user-facing integration around the standard.

## 9) One-sentence placement summary

**Kristals are portable, traceable, offline-usable epistemic artifacts; SenTient resolves ambiguity into structured identifiers; Architect renders labeled knowledge without changing its status; Orgo operationalizes workflows, review, validation, recognition, and distribution; Konnaxion delivers Kristals at platform scale through search, navigation, offline access, reader policies, and collective curation.**
