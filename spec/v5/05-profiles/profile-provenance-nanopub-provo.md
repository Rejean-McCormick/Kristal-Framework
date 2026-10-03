# Profile: Provenance Packaging (Nanopublication + PROV-O)

## Status

Draft (Kristal v5 optional standardized profile)

## Purpose

Provide a portable, interoperable way to package **assertions + provenance + publication metadata** for Kristal exports using:

* **Nanopublication structure**: named graphs for Head, Assertion, Provenance, and PubInfo
* **PROV-O** relations for provenance modeling
* Kristal v5 identifiers for assertions, evidence, source artifacts, validation decisions, authority recognition, certainty, and reader policy context

This profile is **optional** and MUST NOT affect core Kristal identity, hashing, signing, validation status, authority recognition, certainty level, or Runtime Pack activation unless explicitly declared by a separate integrity, validation, or distribution profile.

This profile is for packaging and interoperability. It does not decide whether an assertion is true, validated, recognized, high-certainty, disputed, fictional, mythological, rejected, or visible under a reader policy.

---

## Scope

This profile defines:

* the required named graphs and minimum required triples for a nanopublication
* how Kristal assertion and evidence identifiers map into nanopublication and provenance structures
* how to reference source artifacts, including Structured Epistemic States, Exchanges, shards, federations, Runtime Packs, validation decisions, recognition records, and build metadata
* how to carry validation, certainty, and authority-recognition metadata without collapsing them into universal truth
* interoperability rules for stable IRIs, deterministic emission, and serialization

Non-scope:

* defining trust roots, key distribution, or signature algorithms
* mandating RDF dataset hashing
* mandating full PROV completeness beyond the minimal required terms
* determining which authority channels are trusted
* determining whether an assertion is visible under a given reader policy
* turning a signed, exported, or packaged assertion into a validated assertion

Signing and trust behavior is handled by `01-core-spec/signatures-trust.md`.

RDF dataset hashing, when required, is handled by the RDF integrity profile.

Reader visibility is handled by reader policy profiles.

---

## Profile identifier

* `profile_id`: `kristal.v5:provenance-nanopub-provo`
* `profile_version`: `2.0`
* `spec_version`: `5.0`

---

## Inputs

Inputs MAY include any of the following Kristal v5 artifacts:

* a **Structured Epistemic State**
* a **Working Exchange**
* a **Reference Exchange**
* an **Exchange Shard**
* an **Exchange Federation**
* a **Runtime Pack manifest**
* a **Validation Decision**
* an **Authority Recognition** artifact
* a **Revocation** artifact
* source evidence artifacts
* deterministic RDF projections produced by an RDF export profile

The profile operates over Kristal v5 identifiers including:

* `assertion_id`
* `evidence_id`
* `state_id`
* `kristal_id`
* `shard_id`
* `federation_id`
* `runtime_pack_id`
* `validation_decision_id`
* `recognition_id`
* `revocation_id`
* `build_id`

Legacy `claim_id` values MAY be included for compatibility when the source pipeline produced Claim-IR, but Kristal v5 provenance packaging MUST treat `assertion_id` as the primary assertion identifier.

Claim-IR is an extractor proposal profile in Kristal v5. It is not the universal required input to this profile.

---

## Outputs

The output is one or more nanopublications, each expressed as RDF with named graphs:

* `:Head`
* `:Assertion`
* `:Provenance`
* `:PubInfo`

Recommended serialization:

* N-Quads, preferred for transport and tooling
* TriG, acceptable for human-readable named graph exchange

This profile does not require RDF dataset hashing. If RDF hashing is required, the export MUST explicitly declare an RDF integrity profile.

---

## Normative requirements

### R1. Graph structure

Each nanopublication MUST contain exactly these four named graphs:

1. **Head graph**: links the nanopublication to the other graphs
2. **Assertion graph**: contains the assertion triples
3. **Provenance graph**: contains provenance about the assertion
4. **PubInfo graph**: contains publication metadata such as creator, time, software, source Kristal identifiers, validation references, and authority-recognition references

The Head graph MUST identify the Assertion, Provenance, and PubInfo graphs.

The Assertion, Provenance, and PubInfo graphs MUST be distinct graph IRIs.

---

### R2. Stable identifiers

Nanopublication and graph IRIs MUST be stable and deterministic for a given assertion bundle and export policy.

A conforming implementation MUST use one of the following strategies.

#### Strategy A: content-addressed nanopublication IRI

Recommended.

```text
np_id = sha256(deterministic_representation_of(assertion_bundle + export_policy))
base IRI = urn:kristal:np:<np_id>
```

Graph IRIs:

```text
urn:kristal:np:<np_id>#Head
urn:kristal:np:<np_id>#Assertion
urn:kristal:np:<np_id>#Provenance
urn:kristal:np:<np_id>#PubInfo
```

#### Strategy B: deterministic hierarchical IRI

The base IRI is derived from:

```text
source artifact identity + assertion_id OR deterministic assertion bundle id + export policy id
```

Graph IRIs are formed by suffixing:

```text
#Head
#Assertion
#Provenance
#PubInfo
```

The chosen strategy MUST be declared in export metadata.

Implementations MUST NOT generate random nanopublication IRIs for deterministic exports.

---

### R3. Assertion mapping

The Assertion graph MUST correspond to one of:

* a single Kristal `assertion_id`; or
* a deterministic bundle of assertions; or
* a deterministic entity, topic, shard, or scope projection, provided bundling rules are deterministic and recorded.

The Assertion graph MUST contain:

* RDF triples representing the assertion or assertion bundle under the selected RDF export profile
* a link back to each Kristal `assertion_id`
* any legacy `claim_id` only as compatibility metadata, not as the primary v5 identifier

Recommended predicates:

```text
kristal:assertionId
kristal:legacyClaimId
kristal:assertionStatus
kristal:certaintyLevel
kristal:validatedAs
kristal:validationStatus
kristal:authorityChannel
kristal:recognitionStatus
```

A conforming implementation MAY use equivalent stable predicates, but the predicates MUST be declared in export metadata.

---

### R4. Provenance mapping

The Provenance graph MUST express at least one provenance relation from the assertion or assertion bundle to its evidence, source artifact, or derivation record.

Evidence MUST be identified using deterministic IDs, stable source URIs, or source artifact references.

The minimal requirement is:

```text
<assertionNode> prov:wasDerivedFrom <evidenceNode> .
```

If the assertion was compiled from a Structured Epistemic State, the Provenance graph SHOULD include:

```text
<assertionNode> prov:wasDerivedFrom <stateIRI> .
```

If the assertion was included in an Exchange, shard, federation, or Runtime Pack, the Provenance graph SHOULD include references to those artifacts.

Recommended predicates:

```text
kristal:sourceStateId
kristal:kristalId
kristal:shardId
kristal:federationId
kristal:runtimePackId
kristal:evidenceId
kristal:buildId
```

---

### R5. Validation, certainty, and recognition metadata

This profile MUST preserve validation, certainty, and authority-recognition metadata when such metadata is present in the source artifact or export policy.

The export MUST NOT flatten scoped validation into universal truth.

The export MUST distinguish:

```text
artifact identity
assertion identity
assertion status
certainty level
validation status
validated-as status
authority channel
authority recognition
reader policy
```

A signed or exported nanopublication MUST NOT be interpreted as validated unless a validation decision, authority recognition record, or policy explicitly supports that interpretation.

If validation metadata is included, it SHOULD reference explicit Kristal v5 records:

```text
validation_decision_id
recognition_id
authority_channel_id
reader_policy_id
```

Recommended predicates:

```text
kristal:validationDecisionId
kristal:recognitionId
kristal:authorityChannelId
kristal:readerPolicyId
kristal:validatedAs
kristal:certaintyLevel
kristal:assertionStatus
kristal:validationStatus
kristal:recognitionStatus
```

---

### R6. Publication info

The PubInfo graph MUST include:

* `prov:generatedAtTime`
* `prov:wasAttributedTo`
* a pointer to the software or tooling version that produced the nanopublication
* the profile identifier and profile version used for the export

The PubInfo graph SHOULD include:

* source artifact identifiers
* build identifiers
* compiler identity and version
* RDF export profile identifier
* serialization format
* IRI strategy
* bundling policy
* selected reader policy, if the export was produced under one
* authority channel context, if applicable

Required pattern:

```text
<npIRI> prov:generatedAtTime "YYYY-MM-DDThh:mm:ssZ"^^xsd:dateTime .
<npIRI> prov:wasAttributedTo <agentIRI> .
<npIRI> kristal:profileId "kristal.v5:provenance-nanopub-provo" .
<npIRI> kristal:profileVersion "2.0" .
<npIRI> kristal:compilerVersion "..." .
```

---

### R7. Deterministic emission

Given identical inputs, export profile, reader policy selection, bundling policy, IRI strategy, serialization format, and ordering rules, implementations MUST emit byte-stable nanopublication datasets.

Determinism MUST cover:

* nanopublication IRIs
* graph IRIs
* assertion node IRIs
* evidence node IRIs
* ordering of triples or quads
* ordering of evidence references
* ordering of validation and recognition references
* serialization format
* namespace prefix declarations, if the serialization format exposes them

This requirement is about deterministic export generation.

Hashing the RDF dataset is not required by this profile.

---

### R8. No changes to core identity

Enabling this provenance packaging profile MUST NOT change:

* `state_id`
* `kristal_id`
* `shard_id`
* `federation_id`
* `runtime_pack_id`
* Exchange `content_hash`
* Runtime Pack content hashes
* authority recognition identifiers
* validation decision identifiers

unless a separate integrity profile explicitly includes these exports in hash coverage.

This profile packages provenance. It does not redefine core Kristal identity.

---

### R9. Working, reference, and research material

Nanopublication export MAY be performed for working, reference, research, archival, disputed, fictional, mythological, or low-certainty material if the active export policy allows it.

The export MUST preserve the relevant status labels.

A nanopublication generated from a Working Exchange MUST NOT be labeled as a Reference Exchange unless an authority recognition or validation decision supports that status.

A nanopublication generated from research or low-certainty material MUST NOT omit its uncertainty, scope, or validation status when that status is available in the source artifact.

---

### R10. Reader policy context

If an export is produced under a reader policy, the PubInfo graph SHOULD identify that policy.

Reader policy context MAY explain why some assertions were included or excluded.

A provenance nanopublication MUST NOT imply that excluded assertions do not exist. It only represents the selected projection.

Recommended predicate:

```text
kristal:readerPolicyId
```

---

## Recommended conventions

### C1. One nanopublication per assertion

Default behavior SHOULD be one nanopublication per `assertion_id` for maximal addressability and incremental updates.

Bundled nanopublications MAY be used when:

* the bundle is deterministic;
* the bundle policy is declared;
* each included `assertion_id` remains addressable;
* the export preserves assertion-level provenance and status.

---

### C2. Include pointers to source artifacts and build metadata

PubInfo SHOULD include:

* `kristal:stateId`
* `kristal:kristalId`
* `kristal:shardId`
* `kristal:federationId`
* `kristal:runtimePackId`
* `kristal:buildId`
* compiler identity
* compiler version
* RDF export profile
* serialization profile

---

### C3. Use PROV-O consistently

Use PROV-O terms:

* `prov:Entity` for evidence artifacts, source states, Exchanges, shards, Runtime Packs, and exported datasets
* `prov:Activity` for build, extraction, normalization, compilation, review, validation, recognition, publication, and export steps
* `prov:Agent` for organizations, services, individuals, validators, authority channels, compilers, distributors, and publishers

Recommended activity labels:

```text
kristal:IngestActivity
kristal:ExtractActivity
kristal:NormalizeActivity
kristal:CompileActivity
kristal:ReviewActivity
kristal:ValidateActivity
kristal:RecognizeActivity
kristal:PublishActivity
kristal:ExportActivity
```

Implementations SHOULD NOT assume that every Kristal v5 artifact passed through Claim-IR, resolution, validation, and compile stages in that exact order.

---

### C4. Preserve uncertainty

When the source artifact includes uncertainty, dispute, fictional scope, mythological scope, rejection, revocation, or low-certainty status, the export SHOULD preserve it.

Recommended values to preserve:

```text
assertion_status
certainty_level
validated_as
validation_status
recognition_status
authority_channel
scope
```

---

### C5. Avoid authority laundering

Exports SHOULD avoid ambiguous labels such as:

```text
true
official
canonical
trusted
safe
```

unless the label is scoped by authority channel, validation policy, recognition status, certainty level, and reader policy.

Preferred labels include:

```text
recognized by <authority channel>
validated as <status>
reference under <reader policy>
asserted by <publisher>
signed by <issuer>
not evaluated
disputed
rejected
revoked
low certainty
fictional
mythological
```

---

## Minimal required triples

### Head graph

Required pattern:

```text
<npIRI> np:hasAssertion <assertionGraphIRI> .
<npIRI> np:hasProvenance <provenanceGraphIRI> .
<npIRI> np:hasPublicationInfo <pubInfoGraphIRI> .
```

Exact nanopublication predicates depend on the chosen nanopublication vocabulary. The implementation MUST declare vocabulary IRIs in export metadata.

---

### Assertion graph

Required pattern:

```text
<assertionNode> kristal:assertionId "<assertion_id>" .
```

If the export contains RDF projection triples for the assertion, those triples MUST appear in the Assertion graph.

Recommended pattern when metadata is available:

```text
<assertionNode> kristal:assertionStatus "<assertion_status>" .
<assertionNode> kristal:certaintyLevel "<certainty_level>" .
<assertionNode> kristal:validatedAs "<validated_as>" .
<assertionNode> kristal:validationStatus "<validation_status>" .
```

---

### Provenance graph

Required pattern:

```text
<assertionNode> prov:wasDerivedFrom <evidenceNode> .
```

Recommended pattern:

```text
<evidenceNode> kristal:evidenceId "<evidence_id>" .
<assertionNode> prov:wasDerivedFrom <sourceArtifactNode> .
<sourceArtifactNode> kristal:kristalId "<kristal_id>" .
```

If a validation decision is referenced:

```text
<assertionNode> kristal:validationDecisionId "<validation_decision_id>" .
```

If an authority recognition is referenced:

```text
<assertionNode> kristal:recognitionId "<recognition_id>" .
```

---

### PubInfo graph

Required pattern:

```text
<npIRI> prov:generatedAtTime "YYYY-MM-DDThh:mm:ssZ"^^xsd:dateTime .
<npIRI> prov:wasAttributedTo <agentIRI> .
<npIRI> kristal:profileId "kristal.v5:provenance-nanopub-provo" .
<npIRI> kristal:profileVersion "2.0" .
<npIRI> kristal:compilerVersion "..." .
```

Recommended pattern:

```text
<npIRI> kristal:sourceStateId "<state_id>" .
<npIRI> kristal:kristalId "<kristal_id>" .
<npIRI> kristal:buildId "<build_id>" .
<npIRI> kristal:rdfExportProfileId "<profile_id>" .
<npIRI> kristal:readerPolicyId "<reader_policy_id>" .
<npIRI> kristal:iriStrategy "<strategy_id>" .
<npIRI> kristal:serializationFormat "application/n-quads" .
```

---

## Interoperability constraints

Implementations MUST document:

* which nanopublication vocabulary is used
* which PROV-O vocabulary version is used
* the IRI strategy
* bundling rules, if bundling is used
* the serialization format
* deterministic ordering rules
* RDF export profile used
* whether validation, certainty, and authority-recognition metadata are included
* whether reader policy context is included
* whether the export is covered by any RDF integrity profile

Implementations SHOULD declare these settings in machine-readable export metadata.

---

## Failure modes and required behaviors

### Missing source artifact identity

If the source artifact identity cannot be determined, export MAY proceed only if the export policy allows anonymous or source-limited exports.

The missing identity MUST be reflected in export metadata or validation output.

---

### Missing assertion identifier

If an assertion lacks a deterministic `assertion_id`, nanopublication emission MUST NOT proceed for that assertion.

---

### Missing evidence

If an evidence link is missing for an assertion:

* emission MUST NOT proceed if the active export policy requires evidence;
* emission MAY proceed if the active export policy allows evidence-limited assertions;
* the emitted nanopublication MUST preserve the assertion’s status, certainty level, and warning metadata when available.

This profile MUST NOT assume that missing evidence is always fatal. Fatality depends on export policy, validation policy, and reader policy.

---

### Validation not completed

If validation has not been completed for an assertion or artifact, nanopublication emission MAY proceed if the export policy allows non-validated material.

The export MUST NOT represent the assertion as validated.

---

### Validation rejected or revoked

If an assertion, artifact, validation decision, or authority recognition is rejected or revoked, nanopublication emission MAY proceed for archival, audit, research, diagnostic, or transparency purposes if the export policy allows it.

The export MUST preserve the rejected or revoked status.

---

### Unsupported serialization

If an implementation cannot emit the declared serialization format, export MUST fail for that profile execution.

---

### Non-deterministic bundle

If bundling rules are non-deterministic, export MUST fail for that bundle.

---

## Conformance tests

A conforming implementation MUST provide fixtures demonstrating:

* deterministic nanopublication IRI generation for the same inputs and policies
* deterministic dataset emission for the same inputs and policies
* correct mapping of `assertion_id` into the Assertion graph
* compatibility mapping of legacy `claim_id`, when present
* correct mapping of `evidence_id` and evidence links into PROV-O relations
* preservation of assertion status
* preservation of certainty level
* preservation of validation status
* preservation of `validated_as`
* preservation of authority recognition references
* preservation of reader policy context, when used
* one nanopublication per assertion
* deterministic bundled nanopublications
* enforcement that this profile does not alter core identity or hashing
* export of working material without falsely labeling it as reference material
* export of validated material without implying universal truth
* export of rejected, disputed, fictional, or mythological material with labels preserved

Conformance tests SHOULD include:

* Structured Epistemic State input
* Working Exchange input
* Reference Exchange input
* shard input
* federation input
* Runtime Pack reference
* validation decision reference
* authority recognition reference
* reader-policy-filtered export
* missing-evidence warning case
* missing-evidence fatal case
* rejected assertion export
* mythological corpus export
* fictional corpus export
* independent research bundle export
* Wikidata Seed Kristal export

---

## Security and correctness considerations

Implementations SHOULD defend against:

* provenance laundering
* authority laundering
* converting publication metadata into validation metadata
* converting signatures into universal trust
* omitting uncertainty labels
* omitting rejection, revocation, or disputed status
* silently dropping evidence references
* silently changing assertion identifiers
* non-deterministic IRI generation
* non-deterministic triple ordering
* graph IRI collisions
* bundle ambiguity
* reader-policy confusion
* exporting a filtered projection as if it were the complete corpus

A provenance nanopublication is a packaging artifact. It is not, by itself, proof that the assertion is true, validated, high-certainty, or recognized by any particular authority channel.

---

## Open questions

The following profile decisions remain open:

* Which nanopublication vocabulary will be standardized, or should a small allowed set be supported?
* Should one nanopublication per assertion become a MUST instead of a SHOULD?
* Should multiple evidence nodes per assertion be mandatory when available?
* Should evidence node ordering be defined by lexical IRI order, deterministic source order, or canonicalized evidence object hash?
* Should reader policy context be mandatory for filtered exports?
* Should validation and authority recognition references be required for Reference Exchange exports?
* Should profile exports optionally include a compact JSON sidecar for non-RDF runtimes?
* Should RDF integrity be recommended by default for public authority-recognized exports?
* Should rejected or revoked assertions be exportable by default only in archival or audit modes?
