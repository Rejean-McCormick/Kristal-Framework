# Validation, Certainty, and Authority

## Status

Draft (Kristal v5 normative overview)

## Purpose

This document defines how Kristal v5 separates:

* validation;
* certainty;
* authority recognition;
* artifact integrity;
* reader policy;
* federation.

Kristal v5 does not assume that every compiled artifact is final, universally true, expert-approved, or high-certainty. It allows hypotheses, sourced claims, disputed assertions, research bundles, fictional worlds, mythological corpora, technical declarations, institutional records, and high-confidence reference material to coexist without being confused.

The core invariant is:

> A Kristal MAY contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.
>
> A Kristal MUST NOT present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

This document provides the shared vocabulary and model used by schemas, examples, query contracts, federation manifests, authority registries, validation reports, Runtime Packs, and reader policies.

---

## Normative keywords

MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as normative requirement keywords.

---

## Core distinction

Kristal v5 separates five concepts that are often conflated:

```text
artifact existence
≠ artifact integrity
≠ assertion validity
≠ certainty level
≠ authority recognition
≠ reader visibility
```

A Kristal artifact may be structurally valid, content-addressed, signed, and reproducible while containing assertions that are speculative, disputed, fictional, mythological, low-certainty, or not yet evaluated.

A signature proves that a key signed an artifact identity. It does not prove that the artifact is true.

A validation decision says that a target was evaluated under a policy. It does not automatically imply universal truth or maximum certainty.

An authority recognition says that a channel accepts, rejects, classifies, or references a target within a declared scope. It does not grant authority outside that scope.

A reader policy decides what a user, runtime, interface, application, or AI system chooses to expose or rely on.

---

## Short definition

Kristal v5 is a deterministic, portable epistemic artifact system.

It allows claims, hypotheses, references, myths, technical declarations, research claims, institutional corpora, and disputed forks to coexist without confusion.

Validation is scoped.

Authority is plural.

Certainty is explicit.

Readers choose policy.

Federation preserves disagreement.

Integrity protects artifacts.

---

## Conceptual model

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

This is not a universal mandatory pipeline.

Some artifacts may begin as institutional datasets. Some may come from human experts. Some may come from Wikidata-compatible source data. Some may come from extractors, OCR, LLMs, parsers, or scrapers. Some may be fictional or mythological corpora.

Claim-IR MAY be used as an extractor proposal profile.

Claim-IR MUST NOT be treated as the universal required input to Kristal v5.

Structured Epistemic State is the normative input model for compiled epistemic content.

---

## Validation

Validation answers:

```text
Who accepted this?
As what?
Under which policy?
For which scope?
At which target level?
```

Validation does not answer, by itself:

```text
Is this universally true?
Does every authority agree?
Is this maximum certainty?
Should every reader display it?
```

A validation decision MUST be scoped.

A validation decision SHOULD identify:

* the target being validated;
* the target level;
* the validation status;
* the validated-as status;
* the certainty level, if applicable;
* the authority channel;
* the validation policy;
* the scope;
* the evidence or review basis;
* the time of decision;
* the issuer;
* signatures, when required by policy.

A validation decision MUST NOT be represented only as:

```json
{ "validated": true }
```

This is insufficient in Kristal v5 because it hides authority, scope, policy, and certainty.

---

## Validation status

The standard validation status values are:

```text
validation_status:
  - not_evaluated
  - in_review
  - validated
  - conditionally_validated
  - disputed
  - rejected
  - revoked
```

### `not_evaluated`

The target has not been evaluated under the relevant validation policy.

### `in_review`

The target is undergoing review or validation.

### `validated`

The target satisfies the declared validation policy for the declared scope and validated-as status.

### `conditionally_validated`

The target satisfies the declared validation policy only under stated conditions, limitations, time windows, jurisdictions, reader policies, or authority-channel constraints.

### `disputed`

The target is actively contested, or conflicting authority channels disagree about its status.

### `rejected`

The target was evaluated and rejected under the declared validation policy.

### `revoked`

A previous validation or recognition was withdrawn by the relevant authority channel or policy process.

---

## Validated-as status

Validation does not always mean high certainty.

An assertion may be validated as a hypothesis, as a publisher declaration, as a mythological corpus, as a fictional statement, as an institutional reference, or as a high-confidence factual assertion.

The standard `validated_as` values are:

```text
validated_as:
  - hypothesis
  - claim
  - sourced_claim
  - reviewed_claim
  - high_confidence_fact
  - institutional_reference
  - publisher_declaration
  - technical_specification
  - legal_or_policy_position
  - mythological_corpus
  - fictional_corpus
  - symbolic_model
  - disputed_position
  - rejected_claim
```

### `hypothesis`

The assertion is valid as a hypothesis. It may be useful for research or reasoning without being established as fact.

### `claim`

The assertion is recorded as a claim by a source, publisher, person, institution, model, or dataset.

### `sourced_claim`

The assertion is linked to evidence, references, or source material.

### `reviewed_claim`

The assertion has been reviewed by a person, system, group, or authority process, but may not yet be accepted as a reference.

### `high_confidence_fact`

The assertion is accepted as high-confidence factual content under the declared authority channel and validation policy.

### `institutional_reference`

The assertion or artifact is recognized as a reference by an institution or authority channel for a declared scope.

### `publisher_declaration`

The assertion is validated as a statement made by its publisher.

For example, a company may publish a Kristal describing its own systems. That does not make every downstream safety, policy, or environmental implication validated by external authorities.

### `technical_specification`

The assertion is validated as a technical specification under a declared authority or publisher scope.

### `legal_or_policy_position`

The assertion is validated as a legal, regulatory, civic, or policy position. This may be jurisdiction-specific and time-bound.

### `mythological_corpus`

The assertion or artifact is validated as mythology, cultural memory, symbolic narrative, religious corpus, or heritage material.

This MUST NOT be represented as validated physical-world truth unless an authority channel explicitly validates that epistemic mode.

### `fictional_corpus`

The assertion or artifact is validated as fiction or creative world-building.

This MUST NOT be represented as validated physical-world truth.

### `symbolic_model`

The assertion is validated as a symbolic, metaphorical, representational, or interpretive model.

### `disputed_position`

The assertion is valid as a position held by a declared source or authority channel, while remaining disputed by other channels.

### `rejected_claim`

The assertion is validated as rejected under a declared policy. This is useful for preserving audit trails, refutations, reviews, and disagreement.

---

## Certainty

Certainty answers:

```text
How strong is the assertion within its declared scope?
```

Certainty does not answer:

```text
Who validates it?
Who recognizes it?
Which reader should display it?
Whether it is signed?
Whether it is globally true?
```

The standard certainty levels are:

```text
certainty_level:
  - unknown
  - speculative
  - low
  - medium
  - high
  - established
  - not_applicable
```

### `unknown`

No certainty level has been assigned, or the certainty level is unavailable.

### `speculative`

The assertion is exploratory, conjectural, creative, early-stage, or weakly supported.

### `low`

The assertion has limited support, uncertain evidence, unresolved ambiguity, or weak confidence.

### `medium`

The assertion has meaningful support but remains open to revision, context dependency, or further review.

### `high`

The assertion has strong support under the declared scope and policy.

### `established`

The assertion is accepted as established within the declared authority channel, scope, and validation policy.

`established` MUST NOT be interpreted as universal or permanent truth.

### `not_applicable`

Certainty does not apply in the ordinary factual sense.

Use this for fiction, mythology, symbolic models, publisher declarations, legal positions, cultural corpora, and other contexts where “truth strength” is not the right evaluation dimension.

---

## Assertion status

Assertion status describes the current epistemic state of an assertion.

The standard values are:

```text
assertion_status:
  - hypothesis
  - claimed
  - sourced
  - disputed
  - reviewed
  - validated
  - rejected
  - retracted
  - superseded
```

### `hypothesis`

The assertion is intentionally recorded as a hypothesis.

### `claimed`

The assertion is stated by a source, author, publisher, model, institution, or dataset.

### `sourced`

The assertion has evidence, references, provenance, or source links.

### `disputed`

The assertion is contested or has unresolved disagreement.

### `reviewed`

The assertion has been reviewed under a declared process.

### `validated`

The assertion has a validation decision under a declared authority channel, policy, and scope.

### `rejected`

The assertion was rejected under a declared authority channel, policy, and scope.

### `retracted`

The assertion was withdrawn by its publisher, source, or authority channel.

### `superseded`

The assertion has been replaced by a newer assertion, artifact, or version.

---

## Authority channels

Kristal v5 does not define one universal authority over truth.

An authority channel declares:

* who or what is acting as an authority;
* what scope the authority covers;
* which trust roots are used;
* which validation policies are accepted;
* which publishers, validators, or other authorities it recognizes;
* how recognition, rejection, revocation, and disputes are handled.

Authority channels may include:

```text
authority_type:
  - individual
  - community
  - association
  - research_collective
  - academic_institution
  - standards_body
  - company
  - government
  - intergovernmental_organization
  - ai_validator
  - hybrid_collective
```

A recognition by one authority channel MUST NOT be interpreted as recognition by another authority channel unless an explicit recognition relationship supports that interpretation.

---

## Authority recognition

Authority recognition answers:

```text
Does this authority channel recognize this target?
Recognized as what?
For which scope?
Under which policy?
```

Recognition may target:

```text
target_level:
  - artifact
  - shard
  - assertion
  - authority_channel
  - dataset
  - runtime_pack
```

The standard recognition statuses are:

```text
recognition_status:
  - recognized
  - conditionally_recognized
  - under_review
  - disputed
  - rejected
  - deprecated
  - revoked
```

Authority recognition SHOULD be represented through an explicit Authority Recognition artifact.

An authority recognition record SHOULD include:

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

---

## Delegated authority

Authority channels MAY recognize other authority channels.

For example:

* an international organization may recognize a health authority for public health reference material;
* a government may recognize a national statistical agency;
* a university may recognize a laboratory for a research shard;
* a standards body may recognize a technical working group;
* a company may recognize a product team for documentation about its own systems.

Delegated recognition MUST be explicit.

A delegated authority relationship SHOULD specify:

* recognizing authority;
* recognized authority;
* scope;
* domain;
* subdomain;
* jurisdiction, if applicable;
* validation policy;
* expiration, if applicable;
* revocation path;
* signatures.

Delegated recognition MUST NOT grant universal authority outside the declared scope.

---

## Reader policy

Reader policy answers:

```text
What should this reader, application, runtime, AI system, or user interface include or hide?
```

A reader policy may choose strict or permissive views.

The standard reader modes are:

```text
reader_mode:
  - reference_only
  - validated_only
  - high_certainty_only
  - research
  - creative
  - all_with_labels
  - custom
```

### `reference_only`

Display only artifacts or assertions recognized as reference material under selected authority channels and reader policies.

### `validated_only`

Display only material that satisfies selected validation policies.

This does not necessarily mean maximum certainty.

A `validated_only` view MAY include assertions validated as hypotheses, publisher declarations, mythological corpora, fictional corpora, or legal positions if the active reader policy explicitly allows those validated-as statuses.

### `high_certainty_only`

Display only material whose certainty level satisfies the policy threshold.

### `research`

Display working, uncertain, disputed, low-certainty, or not-yet-validated material with labels preserved.

### `creative`

Display fictional, mythological, symbolic, speculative, or imaginative corpora when the user intentionally enters that scope.

### `all_with_labels`

Display all available material allowed by access policy, with validation, certainty, dispute, authority, and scope labels preserved.

### `custom`

A user-defined or deployment-defined reader policy.

---

## Reader policy object

A reader policy SHOULD be machine-readable.

Recommended shape:

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

Reader policies MUST NOT silently remove labels required to understand validation, certainty, scope, or authority.

A reader policy that filters material MUST NOT imply that excluded material does not exist.

---

## Artifact status

Artifact status describes the lifecycle state of an artifact.

The standard artifact status values are:

```text
artifact_status:
  - draft
  - working
  - under_review
  - recognized
  - reference
  - deprecated
  - superseded
  - revoked
```

### `draft`

The artifact is incomplete or local.

### `working`

The artifact is compiled and usable as structured material, but it is not necessarily recognized as reference material.

### `under_review`

The artifact is being evaluated.

### `recognized`

The artifact has been recognized by at least one declared authority channel.

### `reference`

The artifact is accepted as reference material under one or more declared authority channels, scopes, and reader policies.

### `deprecated`

The artifact is still identifiable but no longer recommended.

### `superseded`

The artifact has been replaced by another artifact.

### `revoked`

The artifact has been withdrawn or invalidated by the relevant authority, publisher, or policy process.

---

## Working artifacts and reference artifacts

A Working Artifact may contain:

* hypotheses;
* claims;
* sourced claims;
* disputed assertions;
* unresolved assertions;
* research material;
* fictional or mythological corpora;
* low-certainty material;
* rejected claims preserved for audit;
* incomplete structures.

A Reference Artifact is an artifact recognized by one or more authority channels or reader policies for a declared scope.

A Working Artifact MUST NOT be represented as a Reference Artifact unless a recognition or validation decision supports that status.

A Reference Artifact MUST NOT be represented as universally true unless a scope and authority policy explicitly support that claim.

---

## Federation and disagreement

Federation allows multiple Kristals, shards, authorities, or reference views to coexist.

Federation MUST preserve:

* source identity;
* publisher identity;
* authority channel;
* validation status;
* recognition status;
* certainty level;
* scope;
* lineage;
* conflict status;
* reader policy context.

Federation MUST NOT silently merge conflicting claims as if they came from the same authority or had the same status.

The default conflict strategy in Kristal v5 is:

```text
conflict_strategy = "preserve_disagreement"
```

Other conflict strategies MAY be used if explicitly declared by a composition policy.

---

## Divergent forks

Divergent forks are allowed.

A fork may be produced for:

* research;
* criticism;
* alternative authority recognition;
* local governance;
* education;
* fictional or mythological exploration;
* minority or dissenting interpretations;
* error correction;
* experimental modeling.

A divergent fork MUST preserve lineage.

A divergent fork MUST declare its authority channel, scope, reader policy context, or lack of recognition when applicable.

A fork MUST NOT inherit recognition from its source unless the recognizing authority explicitly recognizes the fork.

---

## Fiction, mythology, and symbolic corpora

A Kristal may represent fiction, mythology, symbolic systems, cultural memory, religious corpora, or imaginative worlds.

Such a Kristal may be valid and reference-worthy within its declared scope.

For example:

```text
validated_as = "mythological_corpus"
certainty_level = "not_applicable"
scope.domain = "mythology"
```

or:

```text
validated_as = "fictional_corpus"
certainty_level = "not_applicable"
scope.domain = "fiction"
```

A mythological or fictional Kristal MUST NOT be represented as validated physical-world truth unless a declared authority channel explicitly validates that epistemic mode.

---

## Research and hypotheses

A hypothesis may be valid as a hypothesis.

A research bundle may be valuable before expert consensus exists.

A low-certainty assertion may be worth preserving if its uncertainty is explicit.

Kristal v5 therefore allows research material to be compiled, distributed, cited, queried, and reviewed without presenting it as established fact.

A reader or runtime MAY choose to hide such material by default under strict policies.

---

## Institutional and delegated references

Some artifacts are reference-worthy because a competent institution declares or recognizes them.

Examples:

* a health authority recognizing clinical guidance;
* a standards body recognizing a technical specification;
* a government agency recognizing official statistics;
* a company publishing authoritative documentation about its own systems;
* a museum or cultural institution recognizing a heritage corpus.

Institutional recognition MUST be scoped.

A company may be authoritative for its own product documentation but not for independent safety claims.

A health authority may be authoritative for medical guidance but not for unrelated technical standards.

An international organization may recognize an authority channel without independently re-validating every assertion inside every artifact.

---

## Wikidata-compatible seed corpora

A Wikidata-compatible seed Kristal may package a Wikidata corpus as structured Kristal-compatible material.

Such a seed SHOULD preserve, as applicable:

* entities;
* properties;
* statements;
* qualifiers;
* references;
* ranks;
* labels;
* aliases;
* descriptions;
* source identity;
* provenance;
* compatible export structures.

A seed corpus may be recognized as a reference corpus without implying that every statement inside it is maximum-certainty or universally true.

The recognition status of the corpus and the certainty status of individual assertions MUST remain distinguishable.

---

## Required fields for validation-aware assertions

A validation-aware assertion SHOULD include:

```json
{
  "assertion_id": "sha256:<hex>",
  "statement": {},
  "assertion_status": "sourced",
  "certainty_level": "medium",
  "validated_as": "sourced_claim",
  "validation_status": "not_evaluated",
  "scope": {},
  "provenance_refs": [],
  "evidence_refs": [],
  "authority_recognition_refs": [],
  "validation_decision_refs": [],
  "lineage": {}
}
```

The following fields SHOULD be queryable:

```text
assertion_id
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

---

## Validation decision shape

A validation decision SHOULD follow this general shape:

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

Validation decision identifiers SHOULD be content-addressed unless a profile defines another deterministic identifier scheme.

---

## Authority recognition shape

An authority recognition record SHOULD follow this general shape:

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

Recognition identifiers SHOULD be content-addressed unless a profile defines another deterministic identifier scheme.

---

## Reason codes

Implementations SHOULD use stable reason codes when reporting validation, recognition, dispute, rejection, or reader-policy decisions.

Recommended reason codes:

```text
schema_valid
schema_invalid
provenance_sufficient
provenance_insufficient
evidence_sufficient
evidence_insufficient
authority_recognized
authority_not_recognized
scope_mismatch
policy_satisfied
policy_failed
signature_valid
signature_invalid
hash_valid
hash_invalid
conflict_detected
disagreement_preserved
certainty_too_low_for_policy
validated_as_not_allowed_by_policy
rejected_by_authority_channel
revoked_by_authority_channel
reader_policy_satisfied
reader_policy_not_satisfied
```

---

## Query implications

A Kristal v5 query system SHOULD support filtering by:

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

A query result SHOULD preserve the fields needed to explain why a result is visible.

A query result MUST NOT hide that an assertion is disputed, rejected, fictional, mythological, low-certainty, not evaluated, or recognized only by a specific authority channel when that status is known.

---

## Runtime Pack implications

A Runtime Pack SHOULD declare:

* whether it derives from a Working Artifact or Reference Artifact;
* which reader policies it supports;
* which authority channels it includes;
* which validation statuses it includes;
* which certainty levels it includes;
* whether disputed material is included;
* whether fictional or mythological material is included;
* which source artifact and build produced it.

A Runtime Pack built for a permissive research or creative view MUST NOT be activated as a strict reference-only or validated-only pack unless it satisfies that stricter policy.

---

## Rendering implications

Rendering systems such as Architect MUST preserve:

* validation labels;
* authority labels;
* certainty labels;
* disputed status;
* rejected or revoked status;
* fictional or mythological scope;
* reader policy context.

Rendering systems MUST NOT flatten scoped validation into universal truth.

Rendering systems MUST NOT hide that a claim is validated only by a specific authority channel.

---

## Examples

### Example 1: validated hypothesis

```json
{
  "assertion_status": "hypothesis",
  "validation_status": "validated",
  "validated_as": "hypothesis",
  "certainty_level": "speculative",
  "authority_channel": "authority:research-lab-alpha",
  "scope": {
    "domain": "research",
    "subdomain": "early-stage-model"
  }
}
```

This means the assertion is valid as a hypothesis under the research lab’s policy.

It does not mean the assertion is established fact.

---

### Example 2: mythology corpus

```json
{
  "assertion_status": "validated",
  "validation_status": "validated",
  "validated_as": "mythological_corpus",
  "certainty_level": "not_applicable",
  "authority_channel": "authority:cultural-heritage-institute",
  "scope": {
    "domain": "mythology",
    "subdomain": "classical-greek"
  }
}
```

This means the artifact is validated as mythology or cultural material.

It does not mean the events are validated as physical-world history.

---

### Example 3: company technical declaration

```json
{
  "assertion_status": "validated",
  "validation_status": "validated",
  "validated_as": "publisher_declaration",
  "certainty_level": "not_applicable",
  "authority_channel": "authority:company-example",
  "scope": {
    "domain": "technology",
    "subdomain": "product-documentation"
  }
}
```

This means the company declares the content as its own product documentation.

It does not automatically validate independent claims about safety, compliance, or social impact.

---

### Example 4: medical institutional reference

```json
{
  "assertion_status": "validated",
  "validation_status": "validated",
  "validated_as": "institutional_reference",
  "certainty_level": "high",
  "authority_channel": "authority:health-organization",
  "scope": {
    "domain": "health",
    "subdomain": "clinical-guidance"
  },
  "authority_recognition_refs": [
    "recognition:global-health-reference"
  ]
}
```

This means the content is recognized as a health reference under the declared authority channel and scope.

---

### Example 5: divergent fork

```json
{
  "artifact_status": "working",
  "validation_status": "not_evaluated",
  "recognition_status": "recognized",
  "validated_as": "disputed_position",
  "certainty_level": "low",
  "authority_channel": "authority:local-association-example",
  "scope": {
    "domain": "research",
    "subdomain": "minority-position"
  },
  "lineage": {
    "forked_from": [
      "sha256:<source-artifact-id>"
    ]
  }
}
```

This means a local association recognizes the fork as its own position.

It does not imply recognition by scientific, educational, governmental, or international authority channels.

---

## Conformance requirements

A Kristal v5 conformant implementation MUST:

1. distinguish validation status from certainty level;
2. distinguish signature verification from validation;
3. distinguish validation from authority recognition;
4. distinguish artifact status from assertion status;
5. support scoped validation decisions;
6. support plural authority channels;
7. preserve validation, authority, certainty, and scope labels in federation;
8. allow reader policies to select which statuses and channels are visible;
9. avoid representing working material as reference material without recognition;
10. avoid representing fictional, mythological, disputed, rejected, or low-certainty material as high-confidence physical-world truth.

A conformant implementation SHOULD:

1. expose validation and certainty fields in query results;
2. expose authority-channel context in reader interfaces;
3. preserve disagreement during federation;
4. support delegated authority recognition;
5. support reader policies for strict, research, creative, and all-with-labels modes;
6. preserve uncertainty and rejected claims when used for audit, review, or research.

---

## Anti-patterns

The following patterns are non-conformant or strongly discouraged:

```text
validated = true
```

without authority, scope, policy, and validated-as status.

```text
signed = true
therefore true = true
```

because signatures do not imply truth.

```text
recognized by one authority
therefore recognized by all authorities
```

because authority is scoped.

```text
mythology corpus
therefore validated physical-world fact
```

because mythological validity is not physical-world validation.

```text
reader hides rejected claims
therefore rejected claims do not exist
```

because reader visibility is not corpus existence.

```text
federation merges conflicting claims silently
```

because federation must preserve disagreement or declare a policy for conflict handling.

---

## Open questions

The following decisions remain open:

* Should `established` be allowed as a certainty level, or should `high` be the strongest level?
* Should `validated_as` be a closed enum in the base schema, or an extensible controlled vocabulary?
* Should `reader_policy` be required on all Runtime Packs?
* Should `authority_channel` be required on all validation decisions?
* Should `recognition_status` be required on all Reference Artifacts?
* Should delegated authority recognition always require expiry?
* Should fictional and mythological corpora use `certainty_level = not_applicable` by default?
* Should `validated_only` reader mode allow validated hypotheses by default, or require explicit inclusion?
* Should `reference` be an artifact status or only a reader-policy result?
