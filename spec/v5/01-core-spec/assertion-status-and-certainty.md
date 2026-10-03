# Assertion Status and Certainty

## Status

Draft
Spec: Kristal v5
Version: 5.0
Normative: true

## Purpose

This document defines how Kristal v5 represents assertion status, certainty level, validation scope, and authority-bound recognition.

Kristal v5 does not assume that every assertion inside a Kristal has the same epistemic weight. A Kristal may contain hypotheses, claims, sourced statements, reviewed assertions, validated facts, disputed positions, mythological structures, fictional corpora, publisher declarations, technical specifications, rejected claims, or retracted assertions.

The purpose of this specification is to ensure that those different states can coexist without confusion.

The core rule is:

> A Kristal MAY contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.
> A Kristal MUST NOT present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

## Scope

This document defines:

* assertion status values;
* certainty level values;
* `validated_as` values;
* required assertion-level metadata;
* the distinction between validation, certainty, authority recognition, and reader visibility;
* lifecycle rules for assertion status changes;
* reader-policy implications;
* federation behavior for disputed or divergent assertions.

This document does not define:

* full Exchange manifest structure;
* full Structured Epistemic State structure;
* authority registry schema;
* validation report schema;
* reader policy schema;
* Runtime Pack activation policy;
* user interface rendering rules.

Those are defined by their respective Kristal v5 documents and schemas.

## Core distinction

Kristal v5 separates the following concepts:

```text
artifact existence
≠ artifact integrity
≠ assertion status
≠ certainty level
≠ validation status
≠ authority recognition
≠ reader visibility
```

An artifact can be well-formed, signed, content-addressed, and reproducible while containing assertions that are hypothetical, disputed, fictional, low-certainty, or rejected by a particular authority channel.

The system’s responsibility is not to make every assertion true. The system’s responsibility is to prevent status confusion.

## Assertion

An assertion is a structured statement or claim-like unit inside a Kristal artifact.

An assertion may describe:

* a physical-world fact;
* a historical claim;
* a scientific claim;
* a legal or policy position;
* a technical specification;
* an institutional declaration;
* a research hypothesis;
* a mythological or religious corpus;
* a fictional-world statement;
* a disputed or rejected position;
* a symbolic or interpretive model.

Assertions are not required to be factual claims about the physical world. Their epistemic mode must be explicit when ambiguity is possible.

## Required assertion fields

Every assertion in a Kristal v5 artifact MUST be representable with the following minimum fields:

```json
{
  "assertion_id": "sha256:<hex>",
  "statement": {},
  "assertion_status": "sourced",
  "certainty_level": "medium",
  "validated_as": "sourced_claim",
  "scope": {
    "domain": "general"
  },
  "provenance_refs": [],
  "evidence_refs": [],
  "authority_recognition_refs": [],
  "validation_refs": [],
  "lineage": {}
}
```

The exact shape of `statement` is defined by the artifact type, profile, or schema using the assertion.

## Assertion ID

`assertion_id` is the stable identifier for an assertion.

Recommended form:

```text
sha256:<hex>
```

The assertion ID SHOULD be content-addressed when the assertion can be represented by a deterministic hash target.

The hash target SHOULD exclude:

* signatures;
* transient workflow metadata;
* UI rendering metadata;
* operational logs;
* fields that would cause the identifier to change merely because the assertion was reviewed, rendered, or transported.

When assertion identity depends on a profile-specific hash target, that profile MUST declare the hash target.

## Assertion status

`assertion_status` describes the current epistemic state of the assertion itself.

Allowed values:

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

The assertion is explicitly speculative.

Use when:

* the assertion is a research idea;
* the assertion is proposed for investigation;
* evidence is incomplete;
* the assertion is intentionally exploratory.

A hypothesis may be valid as a hypothesis.

A hypothesis MUST NOT be presented as a validated physical-world fact unless a validation decision explicitly changes its status and scope.

### `claimed`

The assertion has been stated by a publisher, source, author, institution, model, extractor, or contributor, but has not yet been sufficiently sourced or reviewed.

Use when:

* the assertion exists as a claim;
* the publisher is known;
* evidence may be absent or not yet assessed.

### `sourced`

The assertion is linked to one or more sources or evidence references.

Use when:

* provenance exists;
* evidence is attached or referenced;
* the assertion has not necessarily been reviewed or validated.

A sourced assertion may still be wrong, outdated, disputed, or low-certainty.

### `disputed`

The assertion is contested by at least one relevant source, reviewer, authority channel, or competing Kristal.

Use when:

* competing assertions exist;
* authority channels disagree;
* evidence conflicts;
* the assertion is known to be controversial within the declared scope.

Disputed assertions SHOULD preserve references to the disagreement.

### `reviewed`

The assertion has been inspected under a declared review process.

Use when:

* human review occurred;
* AI-assisted review occurred;
* institutional review occurred;
* review criteria are recorded.

Reviewed does not automatically mean validated.

### `validated`

The assertion has been accepted under a declared validation policy by a declared authority channel for a declared scope.

A validated assertion MUST declare:

* `validated_as`;
* `certainty_level`;
* `scope`;
* `validation_refs`;
* authority channel through `validation_refs`, `authority_recognition_refs`, or equivalent metadata.

Validation is always scoped.

An assertion MUST NOT be marked `validated` without enough metadata to answer:

```text
validated as what?
validated by whom?
under which policy?
for which scope?
at what certainty level?
```

### `rejected`

The assertion has been rejected by a validation decision, review process, authority channel, or reader policy.

Rejected does not mean the assertion must disappear. It may remain visible in research, audit, dispute, or lineage contexts.

### `retracted`

The publisher or responsible authority has withdrawn the assertion.

Retracted assertions SHOULD preserve lineage and reason codes.

### `superseded`

The assertion has been replaced by a newer assertion.

Superseded assertions SHOULD point to the replacing assertion when possible.

## Certainty level

`certainty_level` describes the strength or applicability of the assertion within its declared scope.

Allowed values:

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

The certainty level has not been evaluated or cannot be determined.

Use when:

* evidence exists but has not been assessed;
* imported data lacks certainty metadata;
* the system cannot infer confidence reliably.

### `speculative`

The assertion is exploratory, conjectural, imaginative, or early-stage.

Use for:

* research hypotheses;
* design proposals;
* speculative models;
* creative exploration.

### `low`

The assertion has weak support, limited evidence, or low confidence.

Use when:

* evidence is thin;
* sources are unreliable;
* review is incomplete;
* the assertion is plausible but fragile.

### `medium`

The assertion has meaningful support but is not yet high-confidence.

Use when:

* sources are credible but incomplete;
* review exists but is limited;
* some disagreement remains;
* confidence is moderate.

### `high`

The assertion has strong support in the declared scope.

Use when:

* evidence is strong;
* review is substantial;
* authority recognition exists;
* disagreement is low or well-addressed.

### `established`

The assertion is stable enough to function as a reference-level assertion in a declared authority channel and scope.

Use when:

* the assertion is broadly recognized by selected authority channels;
* evidence and review are strong;
* the assertion is suitable for default reference views.

`established` MUST NOT be used as a universal truth marker. It is always scoped.

### `not_applicable`

Certainty is not the correct dimension for this assertion.

Use for:

* fictional-world statements;
* mythological corpora;
* symbolic structures;
* religious narratives;
* artistic interpretations;
* publisher declarations;
* technical self-descriptions;
* legal or policy positions where the relevant question is authority or applicability rather than empirical confidence.

Example:

```json
{
  "assertion_status": "validated",
  "validated_as": "mythological_corpus",
  "certainty_level": "not_applicable"
}
```

## Validated-as

`validated_as` describes the epistemic mode under which the assertion is accepted.

Allowed values:

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

### `hypothesis`

The assertion is accepted as a valid hypothesis.

This does not imply that the hypothesis is true.

### `claim`

The assertion is accepted as a claim made by a source or publisher.

### `sourced_claim`

The assertion is accepted as a claim with attached source material.

### `reviewed_claim`

The assertion is accepted as having passed review under a declared process.

### `high_confidence_fact`

The assertion is accepted as a high-confidence factual assertion within the declared scope.

This status SHOULD require strong provenance, evidence, review, and authority support.

### `institutional_reference`

The assertion is accepted as reference material by an institution or recognized authority channel.

Example:

```json
{
  "authority_channel": "authority:who",
  "validated_as": "institutional_reference",
  "scope": {
    "domain": "health"
  }
}
```

### `publisher_declaration`

The assertion is accepted as the publisher’s declared position or description.

Example:

A company may publish a Kristal describing its own system. The assertion may be validated as the company’s declaration without implying that all external claims about safety, impact, performance, or public value are independently validated.

### `technical_specification`

The assertion is accepted as a technical specification.

Use for:

* APIs;
* schemas;
* system contracts;
* protocol definitions;
* implementation requirements.

### `legal_or_policy_position`

The assertion is accepted as a legal, regulatory, governance, or policy position.

This does not automatically imply empirical truth. It means the position is recognized within the declared legal, institutional, or policy scope.

### `mythological_corpus`

The assertion is accepted as part of a mythological, religious, symbolic, cultural, or narrative corpus.

It MUST NOT be silently presented as a validated physical-world fact.

### `fictional_corpus`

The assertion is accepted as part of a fictional world or creative corpus.

It MUST NOT be silently presented as a validated physical-world fact.

### `symbolic_model`

The assertion is accepted as symbolic, interpretive, conceptual, or metaphorical.

### `disputed_position`

The assertion is accepted as a position that exists in a dispute.

This does not mean the assertion is accepted as fact.

### `rejected_claim`

The assertion is accepted as a claim that has been rejected by a declared authority, policy, review, or validation decision.

Rejected claims may still be preserved for audit, education, dispute mapping, lineage, or research.

## Validation status vs assertion status

`assertion_status` describes the assertion itself.

`validation_status` describes the outcome of a validation process.

Allowed validation status values are defined in the validation report and validation decision specifications:

```text
not_evaluated
in_review
validated
conditionally_validated
disputed
rejected
revoked
```

An assertion may have:

```json
{
  "assertion_status": "hypothesis",
  "validation_status": "validated",
  "validated_as": "hypothesis"
}
```

This means the assertion is validated as a hypothesis, not as an established fact.

## Authority recognition

Authority recognition describes whether an authority channel recognizes an assertion, artifact, shard, dataset, runtime pack, or another authority channel.

Recognition is not universal.

Recognition by one authority channel MUST NOT imply recognition by another authority channel.

Example:

```json
{
  "assertion_status": "validated",
  "certainty_level": "high",
  "validated_as": "high_confidence_fact",
  "authority_recognition_refs": [
    {
      "id": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "artifact_type": "authority_recognition"
    }
  ],
  "scope": {
    "domain": "science",
    "subdomain": "astronomy"
  }
}
```

## Reader visibility

Reader visibility is controlled by reader policy.

An assertion may exist in a Kristal but be hidden, marked, downgraded, or excluded from a particular reader view.

Reader policies may filter by:

* `assertion_status`;
* `certainty_level`;
* `validated_as`;
* `validation_status`;
* `authority_channel`;
* `recognition_status`;
* `scope.domain`;
* `scope.subdomain`;
* disputed status;
* fictional status;
* mythological status.

A reader policy MUST NOT change the underlying assertion. It only controls visibility and presentation.

## “Validated-only” does not mean maximum certainty

A reader policy may show only validated assertions.

This does not mean every visible assertion has maximum certainty.

“Validated-only” means:

```text
all visible assertions satisfy the active reader policy’s validation requirements
```

It does not mean:

```text
all visible assertions are universally true
all visible assertions have maximum certainty
all authorities agree
all assertions describe physical-world facts
```

Example:

```json
{
  "reader_policy_id": "reader_policy:validated_only",
  "mode": "validated_only",
  "allowed_validation_statuses": [
    "validated",
    "conditionally_validated"
  ],
  "allowed_certainty_levels": [
    "unknown",
    "speculative",
    "low",
    "medium",
    "high",
    "established",
    "not_applicable"
  ],
  "show_labels": true
}
```

This policy allows validated assertions at multiple certainty levels, provided their labels remain visible.

## Status transitions

Kristal v5 does not require a single universal assertion lifecycle.

However, implementations SHOULD preserve a transition history when assertion status changes.

Common transitions include:

```text
hypothesis -> claimed
claimed -> sourced
sourced -> reviewed
reviewed -> validated
validated -> disputed
validated -> superseded
validated -> revoked
disputed -> reviewed
disputed -> rejected
rejected -> superseded
claimed -> retracted
```

Implementations MUST NOT erase prior status when it is needed for audit, lineage, dispute analysis, reproducibility, or authority comparison.

## Transition record

A status transition SHOULD be recorded as:

```json
{
  "transition_id": "sha256:<hex>",
  "assertion_id": "sha256:<hex>",
  "from_status": "sourced",
  "to_status": "reviewed",
  "changed_at": "2026-01-07T12:34:56Z",
  "changed_by": {
    "authority_channel": "authority:example-review-body"
  },
  "reason_codes": [
    "evidence_sufficient",
    "policy_satisfied"
  ],
  "evidence_refs": [],
  "validation_refs": [],
  "signatures": []
}
```

Transition records MAY be stored in review bundles, validation reports, authority recognition artifacts, transparency logs, or artifact lineage.

## Reason codes

Reason codes SHOULD use stable bounded strings.

Recommended values:

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
rejected_by_authority_channel
revoked_by_authority_channel
reader_policy_filtered
reader_policy_unsupported
projection_unavailable
profile_execution_failed
timeout
memory_limit_exceeded
access_denied
```

## Federation behavior

Federation MUST preserve disagreement.

If two Kristals contain incompatible assertions, federation MUST NOT silently merge them into a single assertion unless an explicit composition policy permits the merge and preserves lineage.

When assertions conflict, a federation manifest or composition policy SHOULD use one of the following strategies:

```text
preserve_disagreement
authority_precedence
mark_disputed
exclude_conflict
require_reader_choice
```

Default v5 behavior SHOULD be:

```text
preserve_disagreement
```

## Divergent forks

Divergent forks are allowed.

A forked Kristal may contain assertions rejected by another authority channel.

A fork MUST preserve lineage when derived from another artifact.

A fork MUST NOT inherit validation or recognition from the source unless that recognition explicitly applies to the fork.

Example:

```json
{
  "assertion_id": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "statement": {
    "subject": "earth",
    "predicate": "shape",
    "object": "flat"
  },
  "assertion_status": "validated",
  "certainty_level": "low",
  "validated_as": "disputed_position",
  "scope": {
    "domain": "science",
    "subdomain": "astronomy"
  },
  "authority_recognition_refs": [
    {
      "id": "authority:example-flat-earth-association",
      "artifact_type": "authority_recognition"
    }
  ],
  "validation_refs": [],
  "lineage": {
    "derived_from": []
  }
}
```

This assertion may be valid as a disputed position within a specific authority channel. It must not be presented as established scientific reference unless a reader policy and authority channel explicitly choose that interpretation.

## Mythology and fiction

A mythology or fiction Kristal may be valid as mythology or fiction.

Example:

```json
{
  "assertion_id": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "statement": {
    "subject": "unicorn",
    "predicate": "appears_in",
    "object": "medieval_bestiary"
  },
  "assertion_status": "validated",
  "certainty_level": "not_applicable",
  "validated_as": "mythological_corpus",
  "scope": {
    "domain": "mythology",
    "subdomain": "medieval-symbolic-animals"
  }
}
```

This means the assertion is valid within a mythological or cultural corpus. It does not mean the system treats unicorns as physical-world animals.

## Publisher declarations

A publisher declaration can be valid as a declaration without validating every external implication of the declaration.

Example:

```json
{
  "assertion_id": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  "statement": {
    "subject": "example-system",
    "predicate": "supports_feature",
    "object": "offline_query"
  },
  "assertion_status": "validated",
  "certainty_level": "not_applicable",
  "validated_as": "publisher_declaration",
  "scope": {
    "domain": "technology",
    "subdomain": "system-documentation"
  },
  "authority_recognition_refs": [
    {
      "id": "authority:example-publisher",
      "artifact_type": "authority_recognition"
    }
  ]
}
```

Other authorities may separately validate performance, safety, interoperability, security, or environmental claims.

## Wikidata seed assertions

A Wikidata Seed Kristal SHOULD preserve source structure as much as possible, including:

* entities;
* properties;
* statements;
* qualifiers;
* references;
* ranks;
* labels;
* aliases;
* descriptions.

Imported Wikidata assertions SHOULD NOT automatically be treated as universally established facts.

A Wikidata Seed Kristal may validate the corpus packaging, lineage, and source identity while preserving mixed assertion certainty.

Example:

```json
{
  "assertion_id": "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "statement": {
    "subject": "Q42",
    "predicate": "P31",
    "object": "Q5"
  },
  "assertion_status": "sourced",
  "certainty_level": "medium",
  "validated_as": "sourced_claim",
  "scope": {
    "domain": "wikidata"
  },
  "provenance_refs": [
    {
      "id": "wikidata:Q42",
      "artifact_type": "external_dataset"
    }
  ]
}
```

## Conformance requirements

A conforming Kristal v5 implementation MUST:

1. Support `assertion_status`.
2. Support `certainty_level`.
3. Support `validated_as` when assertions are validated, reviewed, rejected, fictional, mythological, symbolic, or scoped by authority.
4. Preserve assertion-level provenance references.
5. Preserve assertion-level evidence references when available.
6. Preserve validation references when a validation decision exists.
7. Preserve authority recognition references when recognition exists.
8. Prevent unqualified `validated = true` semantics.
9. Support reader-policy filtering without mutating assertion status.
10. Preserve disagreement during federation unless an explicit composition policy declares otherwise.
11. Avoid presenting scoped validation as universal truth.
12. Avoid presenting fiction, mythology, symbolic models, or publisher declarations as physical-world facts unless an explicit authority channel validates that epistemic mode.

## Non-conforming patterns

The following patterns are non-conforming:

```json
{
  "validated": true
}
```

Reason: validation is unscoped.

```json
{
  "assertion_status": "validated"
}
```

Reason: validated as what, by whom, under which policy, for which scope, and at what certainty level are not declared.

```json
{
  "certainty_level": "established",
  "scope": {}
}
```

Reason: established status requires declared scope.

```json
{
  "validated_as": "fictional_corpus",
  "certainty_level": "high"
}
```

Reason: fictional validity should normally use `not_applicable`, unless a profile explicitly defines a different interpretation.

```json
{
  "assertion_status": "validated",
  "validated_as": "publisher_declaration",
  "scope": {
    "domain": "technology"
  }
}
```

Reason: publisher declaration needs publisher or authority-channel context.

## Recommended rendering rule

Any rendering system, including Architect, browsers, AI agents, dashboards, and Runtime Pack readers, SHOULD preserve the following labels when they are relevant:

```text
assertion_status
certainty_level
validated_as
validation_status
authority_channel
recognition_status
scope
disputed status
fictional or mythological status
```

A rendering system MUST NOT flatten scoped validation into universal truth.

## Summary

Kristal v5 treats assertion status and certainty as first-class epistemic metadata.

Validation is scoped.
Authority is plural.
Certainty is explicit.
Reader policy controls visibility.
Federation preserves disagreement.
Integrity protects artifacts, not ideology.
