# Authority Recognition

## Status

Draft. Normative core specification for Kristal v5.

## Spec

```text
Spec: Kristal v5
Version: 5.0
Normative: true
```

## Purpose

Authority recognition defines how a Kristal v5 authority channel accepts, rejects, disputes, delegates, revokes, or conditionally recognizes a target.

A target may be:

```text
artifact
shard
assertion
authority_channel
dataset
runtime_pack
reader_policy
validation_decision
```

Authority recognition answers:

```text
Who recognizes this target?
As what?
For which scope?
Under which policy?
With which evidence?
For how long?
With which revocation path?
```

Authority recognition does **not** define universal truth.

Recognition by one authority channel does not imply recognition by another authority channel. Kristal v5 supports plural authority, scoped recognition, disagreement preservation, and reader-selected trust policies.

---

## Core principle

Kristal v5 separates:

```text
artifact existence
artifact integrity
assertion status
certainty level
validation decision
authority recognition
reader visibility
```

An artifact MAY exist, be signed, hash-valid, queryable, and distributable without being recognized by any authority channel.

An assertion MAY be valid as a hypothesis, mythological corpus, fictional corpus, publisher declaration, disputed position, technical specification, institutional reference, or high-confidence factual claim.

Authority recognition MUST always be scoped.

A recognition record MUST NOT silently convert scoped recognition into universal truth.

---

## Definitions

### Authority channel

An authority channel is a declared source of recognition for a scope.

Examples:

```text
authority:unesco-global-reference
authority:who-health
authority:microsoft-product-docs
authority:local-school-board
authority:research-lab-example
authority:mythology-archive
authority:community-review-group
```

An authority channel can represent an institution, government, association, company, standards body, research collective, community, AI validator, individual, or hybrid collective.

Authority channels are declared in an Authority Registry.

---

### Authority recognition

An authority recognition is a signed or otherwise verifiable record stating that one authority channel recognizes a target under declared rules.

It may recognize:

```text
a Kristal artifact
a shard
an assertion
another authority channel
a dataset
a runtime pack
a validation decision
a reader policy
```

Recognition is not an assertion that the target is universally true.

It is a scoped statement of acceptance by the issuing authority channel.

---

### Validation decision

A validation decision records the outcome of applying a validation policy.

It answers:

```text
Was this target evaluated?
What status was assigned?
What was it validated as?
At what certainty level?
Under which policy?
By which authority channel?
```

A validation decision may be used as evidence for authority recognition, but it is not identical to authority recognition.

---

### Reader policy

A reader policy determines what a reader, application, runtime, AI system, or user-facing surface chooses to show.

A reader policy may use authority recognition as an input.

Reader policy decides visibility. Authority recognition decides scoped acceptance.

---

## Required invariant

The following invariant applies across all Kristal v5 files, schemas, profiles, manifests, and examples:

```text
A Kristal may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.

A Kristal must not present an assertion as validated or recognized outside the authority channel, scope, certainty level, and validation policy that support that status.
```

---

## Recognition targets

A recognition record MUST declare a `target_level`.

Allowed values:

```text
artifact
shard
assertion
authority_channel
dataset
runtime_pack
reader_policy
validation_decision
```

### `artifact`

Recognition applies to a whole Kristal artifact, such as an Exchange or Reference Artifact.

This does not imply that every assertion inside the artifact has the same certainty level.

### `shard`

Recognition applies to a shard.

This is useful for domain, jurisdiction, dataset, tenant, time-window, or authority-specific partitions.

### `assertion`

Recognition applies to one assertion.

This is the most precise recognition target.

### `authority_channel`

Recognition applies to another authority channel.

This enables delegated or federated authority.

Example:

```text
authority:unesco-global-reference recognizes authority:who-health for health reference material.
```

### `dataset`

Recognition applies to a dataset or external corpus.

Example:

```text
authority:example recognizes Wikidata Seed Kristal as a seed reference corpus.
```

### `runtime_pack`

Recognition applies to a Runtime Pack.

This means the pack is recognized for a scope or channel. It does not imply that runtime activation equals assertion validation.

### `reader_policy`

Recognition applies to a reader policy.

Example:

```text
authority:school-board recognizes reader_policy:curriculum-reference-only for school use.
```

### `validation_decision`

Recognition applies to a validation decision.

This allows an authority channel to accept the result of another validator or review process.

---

## Recognition status

Authority recognition status MUST use one of the following values:

```text
recognized
conditionally_recognized
under_review
disputed
rejected
deprecated
revoked
```

### `recognized`

The issuing authority channel accepts the target under the declared scope and policy.

### `conditionally_recognized`

The target is accepted only under declared conditions.

Conditions MUST be explicit.

### `under_review`

The authority channel has not reached a final recognition status.

### `disputed`

The authority channel records a dispute, unresolved objection, competing interpretation, or conflict.

### `rejected`

The authority channel rejects the target for the declared scope.

### `deprecated`

The authority channel no longer recommends the target for new use, but does not necessarily revoke historical recognition.

### `revoked`

The authority channel withdraws prior recognition.

Revocation MUST preserve enough information to identify what was revoked and why.

---

## Recognized as

The `recognized_as` field states what the target is recognized as.

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

Recognition MUST NOT omit `recognized_as`.

Recognition does not always imply high certainty.

Examples:

```text
recognized_as = "hypothesis"
recognized_as = "mythological_corpus"
recognized_as = "publisher_declaration"
recognized_as = "technical_specification"
recognized_as = "institutional_reference"
recognized_as = "high_confidence_fact"
```

A mythology Kristal can be recognized as mythology.

A fictional Kristal can be recognized as fiction.

A company’s system description can be recognized as a publisher declaration.

A scientific claim can be recognized as a high-confidence fact only under a policy and authority channel that support that status.

---

## Scope

Every authority recognition MUST declare a scope.

A scope MUST include `domain`.

Recommended scope shape:

```json
{
  "domain": "health",
  "subdomain": "clinical-guidelines",
  "jurisdiction": null,
  "time_window": null,
  "tenant_id": null,
  "environment": null,
  "language": "en"
}
```

Allowed top-level domains:

```text
general
wikidata
science
health
education
heritage
law
policy
technology
environment
culture
mythology
fiction
research
operations
civic
local_notes
```

Recognition outside the declared scope MUST NOT be inferred.

---

## Authority delegation

Authority channels MAY recognize other authority channels.

This enables scoped delegation.

Example:

```text
authority:unesco-global-reference
  recognizes authority:who-health
  for domain = "health"
  recognized_as = "institutional_reference"
```

Delegated authority MUST be explicit.

Recognition of an authority channel MUST declare:

```text
issuer_authority_channel
target authority_channel
scope
recognition_status
recognized_as
validation_policy_ref
created_at
```

Recognition of an authority channel does not grant authority outside the declared scope.

Authority delegation is not transitive by default.

If transitive recognition is allowed, the policy MUST explicitly declare:

```text
transitive = true
max_depth
allowed_target_types
allowed_scope_constraints
```

Default:

```text
transitive = false
```

---

## Recognition and validation

Authority recognition and validation decisions are related but distinct.

A validation decision may say:

```text
This assertion was reviewed and validated as a high-confidence fact by authority:example-health under policy P.
```

An authority recognition may say:

```text
authority:unesco-global-reference recognizes authority:example-health as competent for domain health.
```

or:

```text
authority:unesco-global-reference recognizes this health shard as an institutional reference because it was validated by authority:who-health.
```

A recognition record MAY reference validation decisions.

A recognition record MUST NOT replace validation decisions when the validation outcome itself is required.

---

## Recognition and certainty

Recognition MUST NOT be treated as maximum certainty.

Recognition states that an authority accepts a target as something.

Certainty states how strong the assertion is within its scope.

Examples:

```json
{
  "recognition_status": "recognized",
  "recognized_as": "hypothesis",
  "certainty_level": "speculative"
}
```

```json
{
  "recognition_status": "recognized",
  "recognized_as": "mythological_corpus",
  "certainty_level": "not_applicable"
}
```

```json
{
  "recognition_status": "recognized",
  "recognized_as": "high_confidence_fact",
  "certainty_level": "high"
}
```

If certainty is represented in a recognition record, it MUST use the Kristal v5 certainty ladder:

```text
unknown
speculative
low
medium
high
established
not_applicable
```

---

## Recognition and federation

Federation composes multiple Kristals, shards, or authority channels without silently merging their claims.

Recognition is a key input to federation.

A federation manifest MAY use recognition records to decide:

```text
which shards are included
which shards are visible by default
which authority channel has precedence for a given scope
which disagreements must be preserved
which claims are marked disputed
which claims are excluded by a reader policy
```

Federation MUST preserve attribution.

Federation MUST NOT erase disagreement.

Federation MUST NOT make one authority’s recognition appear to be another authority’s recognition.

---

## Recognition and reader policy

Reader policies MAY use authority recognition to determine visibility.

Examples:

```text
reference_only
validated_only
high_certainty_only
research
creative
all_with_labels
custom
```

A `validated_only` or `reference_only` reader policy MAY require recognition from selected authority channels.

Example:

```json
{
  "reader_policy_id": "reader_policy:validated_only",
  "allowed_authority_channels": [
    "authority:unesco-global-reference",
    "authority:who-health"
  ],
  "allowed_recognition_statuses": [
    "recognized",
    "conditionally_recognized"
  ],
  "show_labels": true
}
```

A reader policy MUST NOT hide recognition scope when showing recognized material.

A reader policy MUST NOT flatten scoped recognition into universal truth.

---

## Recognition object

A recognition record SHOULD use this shape.

```json
{
  "schema_version": "5.0",
  "artifact_type": "authority_recognition",
  "recognition_id": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "created_at": "2026-06-12T00:00:00Z",
  "expires_at": null,

  "issuer_authority_channel": "authority:example",
  "target_ref": {
    "artifact_type": "reference_exchange",
    "artifact_id": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
  },
  "target_level": "artifact",

  "recognition_status": "recognized",
  "recognized_as": "institutional_reference",
  "certainty_level": "high",

  "scope": {
    "domain": "education",
    "subdomain": "curriculum",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },

  "validation_policy_ref": {
    "policy_id": "kristal.v5:validation-policy:example",
    "policy_version": "1"
  },

  "evidence_refs": [],
  "validation_decision_refs": [],
  "reason_codes": [
    "authority_recognized",
    "policy_satisfied"
  ],

  "content_hash": {
    "alg": "sha256",
    "value": "2222222222222222222222222222222222222222222222222222222222222222"
  },

  "signatures": []
}
```

---

## Required fields

An authority recognition record MUST include:

```text
schema_version
artifact_type
recognition_id
created_at
issuer_authority_channel
target_ref
target_level
recognition_status
recognized_as
scope
validation_policy_ref
reason_codes
content_hash
signatures
```

`expires_at` MAY be `null`.

`certainty_level` SHOULD be included when recognition concerns assertions, datasets, shards, or artifacts whose epistemic strength matters.

`validation_decision_refs` SHOULD be included when recognition relies on validation decisions.

`evidence_refs` SHOULD be included when recognition relies on external evidence.

---

## Field definitions

### `schema_version`

MUST be:

```text
5.0
```

### `artifact_type`

MUST be:

```text
authority_recognition
```

### `recognition_id`

Content-addressed ID of the recognition record.

Recommended form:

```text
sha256:<hex>
```

The `recognition_id` field itself MUST be excluded from its own hash target.

### `created_at`

RFC3339 timestamp.

Timestamps MUST NOT affect content-addressed IDs unless the profile explicitly includes them in the hash target.

### `expires_at`

Optional RFC3339 timestamp or `null`.

If present, recognition SHOULD be treated as inactive after expiry unless a reader policy or authority policy explicitly allows historical use.

### `issuer_authority_channel`

Authority channel issuing the recognition.

Pattern:

```text
authority:<slug>
```

### `target_ref`

Reference to the target being recognized.

The target may be content-addressed, URI-addressed, or both.

### `target_level`

Level at which recognition applies.

Allowed values:

```text
artifact
shard
assertion
authority_channel
dataset
runtime_pack
reader_policy
validation_decision
```

### `recognition_status`

Status assigned by the issuer.

Allowed values:

```text
recognized
conditionally_recognized
under_review
disputed
rejected
deprecated
revoked
```

### `recognized_as`

What the target is recognized as.

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

### `certainty_level`

Optional but recommended.

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

### `scope`

Declared recognition scope.

Recognition MUST NOT be applied outside this scope unless another recognition record explicitly extends it.

### `validation_policy_ref`

Reference to the policy used to issue recognition.

### `evidence_refs`

References to supporting evidence, documents, datasets, observations, audits, expert reviews, or external artifacts.

### `validation_decision_refs`

References to validation decisions used as input to recognition.

### `reason_codes`

Stable reason codes explaining the recognition outcome.

### `content_hash`

Hash of the canonicalized recognition hash target.

Use:

```json
{
  "alg": "sha256",
  "value": "<64 lowercase hex chars>"
}
```

Use `alg`, not `algo`.

### `signatures`

Signatures over the canonicalized recognition hash target.

Signatures MUST be excluded from the signed hash target.

---

## Recommended reason codes

Recognition reason codes SHOULD use stable strings.

Recommended codes:

```text
authority_recognized
authority_not_recognized
authority_delegated
authority_delegation_expired
scope_satisfied
scope_mismatch
policy_satisfied
policy_failed
provenance_sufficient
provenance_insufficient
evidence_sufficient
evidence_insufficient
validation_decision_accepted
validation_decision_missing
validation_decision_rejected
signature_valid
signature_invalid
hash_valid
hash_invalid
conflict_detected
disagreement_preserved
certainty_too_low_for_policy
recognized_by_parent_authority
rejected_by_authority_channel
revoked_by_authority_channel
expired
superseded
```

Reason codes SHOULD be machine-readable.

Human-readable explanations MAY be provided in `notes`.

---

## Recognition lifecycle

A recognition record MAY move through these states:

```text
under_review
recognized
conditionally_recognized
disputed
deprecated
revoked
```

A recognition record SHOULD NOT be mutated in place after publication if it is content-addressed.

Instead, later records SHOULD reference earlier records using:

```text
supersedes
revokes
replaces
derived_from
```

A revoked recognition remains part of history, but reader policies SHOULD treat it according to revocation rules.

---

## Revocation

Authority recognition can be revoked.

A revocation MUST identify:

```text
the recognition being revoked
the authority channel issuing the revocation
the reason codes
the effective time
the signature or trust root authorizing revocation
```

Revocation does not delete the earlier recognition record.

Revocation changes how the recognition is interpreted.

A revocation SHOULD use the Kristal v5 revocation schema when available.

---

## Expiry

Recognition MAY expire.

If `expires_at` is set, consumers SHOULD treat the recognition as inactive after that time unless the reader policy explicitly allows historical recognition.

Expired recognition SHOULD NOT be silently treated as active recognition.

---

## Conditional recognition

A conditionally recognized target MUST declare conditions.

Recommended shape:

```json
{
  "recognition_status": "conditionally_recognized",
  "conditions": [
    {
      "condition_id": "condition:example",
      "description": "Recognized only for educational use, not clinical use.",
      "scope": {
        "domain": "education"
      },
      "expires_at": null
    }
  ]
}
```

Conditions MUST be visible to readers, validators, and federation policies.

---

## Conflicting recognitions

Multiple authority channels may issue conflicting recognitions.

Example:

```text
authority:A recognizes target X.
authority:B rejects target X.
authority:C marks target X disputed.
```

This is valid.

Kristal v5 MUST preserve the conflict.

Conflict resolution belongs to:

```text
federation composition policy
reader policy
authority registry policy
application policy
```

A conflict MUST NOT be silently collapsed into a single universal answer.

---

## Recognition inheritance

Recognition does not automatically inherit across:

```text
forks
derived artifacts
runtime packs
federations
translations
summaries
exports
reader projections
```

Recognition inheritance MAY occur only when an explicit policy permits it.

If recognition is inherited, the inheritance policy MUST declare:

```text
source recognition
target artifact
transform type
allowed scope
loss conditions
reason codes
```

Default:

```text
recognition_inheritance = false
```

---

## Recognition of forks

A forked Kristal MAY preserve lineage to the source artifact.

It MUST NOT inherit recognition from the source unless an authority channel explicitly recognizes the fork or a policy explicitly permits recognition inheritance.

A fork SHOULD declare:

```text
source artifact
fork author
fork reason
changed assertions
authority channel
scope
reader policy implications
```

Divergent forks are allowed.

Divergent forks MUST preserve attribution and recognition boundaries.

---

## Recognition of fiction, mythology, and symbolic material

A fiction, mythology, or symbolic Kristal MAY be recognized.

Examples:

```text
recognized_as = "fictional_corpus"
recognized_as = "mythological_corpus"
recognized_as = "symbolic_model"
certainty_level = "not_applicable"
```

Such recognition MUST NOT be presented as validation of physical-world truth unless an authority channel explicitly recognizes that epistemic mode.

Reader policies SHOULD allow users to include or exclude these scopes.

---

## Recognition of publisher declarations

A publisher MAY be the appropriate authority for its own declarations.

Example:

```text
authority:microsoft-product-docs recognizes a system documentation Kristal as publisher_declaration.
```

This means the publisher declares the system behavior.

It does not automatically mean:

```text
the system is safe
the system is compliant
the system is environmentally sound
the system has no security issues
```

Other authority channels may recognize, dispute, audit, or reject those aspects under their own scopes.

---

## Recognition of institutional references

An institutional reference is a target recognized by an authority channel for broad use in a declared scope.

Example:

```text
authority:who-health recognizes a medical guideline shard as institutional_reference for health.
```

Another authority may then recognize the authority channel itself:

```text
authority:unesco-global-reference recognizes authority:who-health for health education references.
```

This creates layered recognition without requiring one authority to inspect every assertion directly.

---

## Recognition record hash target

The content hash of an authority recognition record MUST exclude:

```text
recognition_id
content_hash
signatures
runtime cache data
operational logs
non-declared external fetch results
```

The content hash SHOULD include:

```text
schema_version
artifact_type
created_at
expires_at
issuer_authority_channel
target_ref
target_level
recognition_status
recognized_as
certainty_level
scope
validation_policy_ref
evidence_refs
validation_decision_refs
reason_codes
conditions
lineage
extensions if declared hash-relevant
```

Hashing MUST use:

```text
canonicalization_profile = kristal.v5:jcs-rfc8785
canonicalization_version = 1
hash_alg = sha256
```

---

## Signature requirements

Authority recognition records SHOULD be signed by the issuing authority channel.

A signature MUST declare:

```text
key_id
alg
signature
created_at
```

Recommended signature algorithm:

```text
ed25519
```

Use `alg`, not `algo`.

The signer SHOULD be resolvable through the Authority Registry or another declared trust root.

Signatures are excluded from their own hash target.

---

## Authority Registry relationship

The Authority Registry declares authority channels, trust roots, scopes, validation policies, revocation policies, and recognition constraints.

Authority recognition records SHOULD reference authority channels declared in an Authority Registry.

A consumer MAY reject or mark recognition as untrusted if:

```text
issuer_authority_channel is unknown
issuer authority is outside scope
required trust roots are missing
signature verification fails
authority registry is stale beyond policy limits
revocation data is unavailable when required
```

Unknown authority does not make the target false.

It means the recognition is not accepted under the consumer’s active policy.

---

## Query requirements

Kristal v5 query systems SHOULD support filters for authority recognition.

Recommended filters:

```text
issuer_authority_channel
target_level
target_ref
recognition_status
recognized_as
certainty_level
scope.domain
scope.subdomain
scope.jurisdiction
validation_policy_ref
created_at
expires_at
reason_codes
include_expired
include_revoked
include_disputed
```

Query results SHOULD preserve enough metadata to show:

```text
who recognized the target
what was recognized
as what
for which scope
under which policy
with what status
```

---

## Rendering requirements

Architect, reader, and application renderers MUST NOT flatten authority recognition into universal truth.

Rendered summaries SHOULD preserve:

```text
recognition_status
recognized_as
issuer_authority_channel
scope
certainty_level
validation_policy_ref
dispute/revocation/expiry indicators
```

Examples of acceptable labels:

```text
Recognized by authority:who-health as institutional_reference for health.
Recognized by authority:mythology-archive as mythological_corpus.
Rejected by authority:example-science-channel for physical-world claim scope.
Under review by authority:local-board for education/curriculum.
```

Examples of unacceptable labels:

```text
True.
Official truth.
Validated everywhere.
Canonical.
Universally accepted.
```

---

## Minimal example: authority recognizes another authority

```json
{
  "schema_version": "5.0",
  "artifact_type": "authority_recognition",
  "recognition_id": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "created_at": "2026-06-12T00:00:00Z",
  "expires_at": null,
  "issuer_authority_channel": "authority:unesco-global-reference",
  "target_ref": {
    "artifact_type": "authority_channel",
    "artifact_id": "authority:who-health"
  },
  "target_level": "authority_channel",
  "recognition_status": "recognized",
  "recognized_as": "institutional_reference",
  "certainty_level": "not_applicable",
  "scope": {
    "domain": "health",
    "subdomain": "public-health-guidance",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },
  "validation_policy_ref": {
    "policy_id": "kristal.v5:authority-recognition:institutional-delegation",
    "policy_version": "1"
  },
  "evidence_refs": [],
  "validation_decision_refs": [],
  "reason_codes": [
    "authority_recognized",
    "scope_satisfied",
    "policy_satisfied"
  ],
  "content_hash": {
    "alg": "sha256",
    "value": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "signatures": []
}
```

---

## Minimal example: publisher declaration

```json
{
  "schema_version": "5.0",
  "artifact_type": "authority_recognition",
  "recognition_id": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "created_at": "2026-06-12T00:00:00Z",
  "expires_at": null,
  "issuer_authority_channel": "authority:example-company-docs",
  "target_ref": {
    "artifact_type": "reference_exchange",
    "artifact_id": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
  },
  "target_level": "artifact",
  "recognition_status": "recognized",
  "recognized_as": "publisher_declaration",
  "certainty_level": "not_applicable",
  "scope": {
    "domain": "technology",
    "subdomain": "product-documentation",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },
  "validation_policy_ref": {
    "policy_id": "kristal.v5:publisher-declaration",
    "policy_version": "1"
  },
  "evidence_refs": [],
  "validation_decision_refs": [],
  "reason_codes": [
    "authority_recognized",
    "policy_satisfied"
  ],
  "content_hash": {
    "alg": "sha256",
    "value": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
  },
  "signatures": []
}
```

---

## Minimal example: mythological corpus

```json
{
  "schema_version": "5.0",
  "artifact_type": "authority_recognition",
  "recognition_id": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
  "created_at": "2026-06-12T00:00:00Z",
  "expires_at": null,
  "issuer_authority_channel": "authority:example-cultural-archive",
  "target_ref": {
    "artifact_type": "reference_exchange",
    "artifact_id": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
  },
  "target_level": "artifact",
  "recognition_status": "recognized",
  "recognized_as": "mythological_corpus",
  "certainty_level": "not_applicable",
  "scope": {
    "domain": "mythology",
    "subdomain": "comparative-mythology",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },
  "validation_policy_ref": {
    "policy_id": "kristal.v5:cultural-corpus-recognition",
    "policy_version": "1"
  },
  "evidence_refs": [],
  "validation_decision_refs": [],
  "reason_codes": [
    "authority_recognized",
    "scope_satisfied",
    "policy_satisfied"
  ],
  "content_hash": {
    "alg": "sha256",
    "value": "2222222222222222222222222222222222222222222222222222222222222222"
  },
  "signatures": []
}
```

---

## Minimal example: rejected physical-world claim

```json
{
  "schema_version": "5.0",
  "artifact_type": "authority_recognition",
  "recognition_id": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
  "created_at": "2026-06-12T00:00:00Z",
  "expires_at": null,
  "issuer_authority_channel": "authority:example-science-channel",
  "target_ref": {
    "artifact_type": "assertion",
    "artifact_id": "sha256:4444444444444444444444444444444444444444444444444444444444444444"
  },
  "target_level": "assertion",
  "recognition_status": "rejected",
  "recognized_as": "rejected_claim",
  "certainty_level": "high",
  "scope": {
    "domain": "science",
    "subdomain": "physical-world-claims",
    "jurisdiction": null,
    "time_window": null,
    "tenant_id": null,
    "environment": null,
    "language": "en"
  },
  "validation_policy_ref": {
    "policy_id": "kristal.v5:science-reference-review",
    "policy_version": "1"
  },
  "evidence_refs": [],
  "validation_decision_refs": [],
  "reason_codes": [
    "rejected_by_authority_channel",
    "evidence_insufficient",
    "policy_satisfied"
  ],
  "content_hash": {
    "alg": "sha256",
    "value": "5555555555555555555555555555555555555555555555555555555555555555"
  },
  "signatures": []
}
```

---

## Conformance requirements

A Kristal v5 implementation that handles authority recognition MUST:

1. Preserve recognition scope.
2. Preserve issuer authority channel.
3. Preserve target level.
4. Preserve recognition status.
5. Preserve `recognized_as`.
6. Preserve certainty level when present.
7. Preserve validation policy reference.
8. Preserve revocation and expiry status.
9. Preserve signatures and content hashes.
10. Avoid treating recognition as universal truth.
11. Avoid inheriting recognition across forks or derived artifacts unless explicitly permitted by policy.
12. Avoid silently merging conflicting recognitions.
13. Expose recognition labels to reader and rendering layers.
14. Support recognition filtering in query systems where authority-aware query is supported.

---

## Non-goals

Authority recognition does not:

```text
define universal truth
replace validation decisions
replace assertion status
replace certainty level
replace reader policy
replace federation composition policy
replace provenance
replace signatures
replace revocation handling
make one authority globally dominant
```

---

## Summary

Authority recognition is the Kristal v5 mechanism for scoped acceptance by named authorities.

It makes it possible to say:

```text
This target is recognized by this authority,
as this kind of thing,
for this scope,
under this policy,
with these reasons,
until this expiry or revocation.
```

It also makes it possible to preserve disagreement without confusion.

Recognition is plural.

Recognition is scoped.

Recognition is inspectable.

Recognition is not universal truth.
