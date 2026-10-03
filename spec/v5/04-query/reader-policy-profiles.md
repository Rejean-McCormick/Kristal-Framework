# Reader Policy Profiles

## Status

Draft (Kristal v5 normative query profile)

## Purpose

This document defines how Kristal v5 readers, query engines, Runtime Packs, APIs, applications, and AI systems select which artifacts and assertions are visible or usable under a given policy.

Kristal v5 allows material at many epistemic states to coexist:

* hypotheses;
* claims;
* sourced claims;
* disputed assertions;
* rejected assertions;
* fictional corpora;
* mythological corpora;
* symbolic models;
* research bundles;
* publisher declarations;
* institutional references;
* high-confidence factual assertions.

Reader policies make this usable by declaring which statuses, certainty levels, validation decisions, authority channels, scopes, and artifact states are included in a given view.

A reader policy does not determine whether an artifact exists.

A reader policy determines what a reader, runtime, query surface, application, or user chooses to expose or rely on.

---

## Normative keywords

MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as normative requirement keywords.

---

## Core invariant

A Kristal MAY contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.

A reader policy MAY hide or include those assertions.

A reader policy MUST NOT erase their status.

A reader policy MUST NOT present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

---

## Scope

This document defines:

* standard reader policy modes;
* required and recommended reader policy fields;
* filtering semantics for validation status, certainty level, authority channel, artifact status, and assertion status;
* how Runtime Packs declare supported reader policies;
* how query systems apply reader policy profiles;
* how applications preserve labels when rendering filtered results;
* conformance requirements for strict, research, creative, and custom views.

This document does not define:

* authority-channel governance;
* trust-root distribution;
* signature algorithms;
* validation policy internals;
* user interface layout;
* access-control or authentication rules;
* RDF export behavior.

Access control MAY be layered on top of reader policy, but access control and reader policy MUST remain distinct.

---

## Reader policy definition

A **Reader Policy** is a machine-readable object that specifies which Kristal material is visible, trusted, queryable, or active in a given reader context.

Reader policies may be used by:

* query engines;
* Runtime Pack activators;
* Konnaxion readers;
* Architect renderers;
* Orgo review surfaces;
* AI agents;
* search indexes;
* exports;
* offline clients;
* educational interfaces;
* research tools;
* creative tools.

Reader policy answers:

```text
What should this reader include?
What should this reader hide?
Which authority channels are allowed?
Which validation statuses are allowed?
Which certainty levels are allowed?
Which labels must remain visible?
What happens when required data is unavailable?
```

Reader policy does not answer:

```text
Is this universally true?
Does every authority agree?
Is this assertion maximum-certainty?
Is this artifact signed?
Is this source globally authoritative?
```

---

## Standard reader modes

Kristal v5 defines these standard reader modes:

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

Implementations MAY define additional modes, but custom modes MUST declare explicit filtering rules.

---

## Reader mode semantics

### `reference_only`

The strictest standard mode.

A `reference_only` reader SHOULD include only artifacts or assertions that are recognized as reference material under selected authority channels, scopes, and reader policies.

Typical filters:

```json
{
  "mode": "reference_only",
  "allowed_artifact_statuses": ["reference"],
  "allowed_recognition_statuses": ["recognized", "conditionally_recognized"],
  "allowed_validation_statuses": ["validated", "conditionally_validated"],
  "include_disputed": false,
  "include_rejected": false,
  "include_revoked": false,
  "include_fictional": false,
  "include_mythological": false,
  "show_labels": true
}
```

A `reference_only` view MUST NOT include Working Artifacts unless an explicit policy recognizes them as reference material for that scope.

---

### `validated_only`

A `validated_only` reader includes material that satisfies selected validation policies.

This mode does not necessarily mean maximum certainty.

A validated assertion may be validated as:

* a hypothesis;
* a publisher declaration;
* a sourced claim;
* a reviewed claim;
* a mythological corpus;
* a fictional corpus;
* a legal or policy position;
* a high-confidence fact;
* an institutional reference.

The policy MUST specify which `validated_as` values are allowed.

Typical filters:

```json
{
  "mode": "validated_only",
  "allowed_validation_statuses": ["validated", "conditionally_validated"],
  "allowed_validated_as": [
    "sourced_claim",
    "reviewed_claim",
    "high_confidence_fact",
    "institutional_reference"
  ],
  "include_disputed": false,
  "include_rejected": false,
  "include_revoked": false,
  "show_labels": true
}
```

If `validated_as = "hypothesis"` is allowed, the reader MUST preserve the hypothesis label.

---

### `high_certainty_only`

A `high_certainty_only` reader includes material whose certainty level satisfies a configured threshold.

Typical filters:

```json
{
  "mode": "high_certainty_only",
  "allowed_certainty_levels": ["high", "established"],
  "include_disputed": false,
  "include_rejected": false,
  "include_revoked": false,
  "show_labels": true
}
```

This mode MUST NOT treat certainty as authority recognition.

A high-certainty assertion under one authority channel may still be rejected or ignored by another authority channel.

---

### `research`

A `research` reader includes working, uncertain, disputed, low-certainty, not-yet-validated, or exploratory material with labels preserved.

Typical filters:

```json
{
  "mode": "research",
  "allowed_artifact_statuses": ["draft", "working", "under_review", "recognized", "reference"],
  "allowed_validation_statuses": [
    "not_evaluated",
    "in_review",
    "validated",
    "conditionally_validated",
    "disputed",
    "rejected"
  ],
  "allowed_certainty_levels": ["unknown", "speculative", "low", "medium", "high", "established", "not_applicable"],
  "include_disputed": true,
  "include_rejected": true,
  "include_revoked": false,
  "include_fictional": false,
  "include_mythological": false,
  "show_labels": true
}
```

A research reader MAY include rejected material for audit, refutation, review, or epistemic comparison.

Rejected or disputed material MUST be clearly labeled.

---

### `creative`

A `creative` reader includes fictional, mythological, symbolic, speculative, and imaginative corpora when the user or application intentionally enters that scope.

Typical filters:

```json
{
  "mode": "creative",
  "allowed_validated_as": [
    "fictional_corpus",
    "mythological_corpus",
    "symbolic_model",
    "hypothesis",
    "claim",
    "sourced_claim"
  ],
  "allowed_certainty_levels": ["unknown", "speculative", "low", "medium", "not_applicable"],
  "include_fictional": true,
  "include_mythological": true,
  "include_disputed": true,
  "include_rejected": false,
  "include_revoked": false,
  "show_labels": true
}
```

A creative reader MUST NOT present fictional or mythological material as validated physical-world truth.

---

### `all_with_labels`

An `all_with_labels` reader includes all material allowed by access-control and distribution policy, while preserving all relevant labels.

Typical filters:

```json
{
  "mode": "all_with_labels",
  "allowed_artifact_statuses": ["draft", "working", "under_review", "recognized", "reference", "deprecated", "superseded"],
  "allowed_validation_statuses": [
    "not_evaluated",
    "in_review",
    "validated",
    "conditionally_validated",
    "disputed",
    "rejected",
    "revoked"
  ],
  "allowed_certainty_levels": ["unknown", "speculative", "low", "medium", "high", "established", "not_applicable"],
  "include_disputed": true,
  "include_rejected": true,
  "include_revoked": true,
  "include_fictional": true,
  "include_mythological": true,
  "show_labels": true
}
```

This mode is useful for audit, debugging, governance, provenance review, transparency logs, and expert inspection.

---

### `custom`

A `custom` reader policy MUST explicitly declare its inclusion and exclusion rules.

A custom policy MUST NOT rely only on the label `"custom"`.

It SHOULD declare:

* artifact statuses;
* assertion statuses;
* validation statuses;
* certainty levels;
* validated-as statuses;
* recognition statuses;
* authority channels;
* scopes;
* dispute inclusion;
* rejected inclusion;
* revoked inclusion;
* fictional inclusion;
* mythological inclusion;
* fallback behavior;
* required label visibility.

---

## Reader policy object

A reader policy SHOULD use the following shape:

```json
{
  "schema_version": "5.0",
  "artifact_type": "reader_policy",
  "reader_policy_id": "reader_policy:<slug>",
  "name": "string",
  "mode": "validated_only",

  "scope": {
    "domain": "string",
    "subdomain": "string|null",
    "jurisdiction": "string|null",
    "time_window": "string|null",
    "tenant_id": "string|null",
    "environment": "string|null",
    "language": "string|null"
  },

  "allowed_authority_channels": [],
  "denied_authority_channels": [],

  "allowed_artifact_statuses": [],
  "allowed_assertion_statuses": [],
  "allowed_validation_statuses": [],
  "allowed_recognition_statuses": [],
  "allowed_certainty_levels": [],
  "allowed_validated_as": [],

  "include_disputed": false,
  "include_rejected": false,
  "include_revoked": false,
  "include_deprecated": false,
  "include_superseded": false,
  "include_fictional": false,
  "include_mythological": false,
  "include_symbolic": false,
  "include_not_evaluated": false,

  "require_provenance": false,
  "require_evidence": false,
  "require_signature": false,
  "require_validation_decision": false,
  "require_authority_recognition": false,

  "fallback_behavior": "show_unavailable",
  "show_labels": true,
  "label_requirements": [],

  "ordering_policy": {
    "primary": "authority_precedence",
    "secondary": "certainty_level",
    "tie_breaker": "stable_id"
  },

  "conflict_policy": {
    "strategy": "preserve_disagreement",
    "require_user_choice": false
  },

  "created_at": "RFC3339",
  "created_by": {},
  "policy_refs": [],
  "signatures": [],
  "extensions": {}
}
```

---

## Field semantics

### `reader_policy_id`

The stable identifier for the reader policy.

Recommended format:

```text
reader_policy:<slug>
```

A content-addressed identifier MAY be used when policies are immutable or signed as artifacts.

---

### `mode`

The standard reader mode.

Allowed values:

```text
reference_only
validated_only
high_certainty_only
research
creative
all_with_labels
custom
```

---

### `scope`

Defines where the reader policy applies.

A reader policy MAY be global, domain-scoped, tenant-scoped, environment-scoped, jurisdiction-scoped, or language-scoped.

If a policy declares a scope, implementations MUST NOT silently apply it outside that scope.

---

### `allowed_authority_channels`

List of authority channels whose validation or recognition may be included.

An empty list means policy-defined default behavior.

A strict implementation SHOULD treat an empty list as “no authority channels allowed” unless the policy profile defines a default registry.

Recommended values:

```text
authority:<slug>
```

---

### `denied_authority_channels`

List of authority channels explicitly excluded.

If an authority channel appears in both allowed and denied lists, denial SHOULD win unless the policy explicitly declares another precedence rule.

---

### `allowed_artifact_statuses`

Allowed artifact lifecycle states.

Standard values:

```text
draft
working
under_review
recognized
reference
deprecated
superseded
revoked
```

---

### `allowed_assertion_statuses`

Allowed assertion states.

Standard values:

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

---

### `allowed_validation_statuses`

Allowed validation states.

Standard values:

```text
not_evaluated
in_review
validated
conditionally_validated
disputed
rejected
revoked
```

---

### `allowed_recognition_statuses`

Allowed authority recognition states.

Standard values:

```text
recognized
conditionally_recognized
under_review
disputed
rejected
deprecated
revoked
```

---

### `allowed_certainty_levels`

Allowed certainty levels.

Standard values:

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

### `allowed_validated_as`

Allowed validated-as statuses.

Standard values:

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

---

### Inclusion flags

The following flags provide readable shortcuts for common policy decisions:

```text
include_disputed
include_rejected
include_revoked
include_deprecated
include_superseded
include_fictional
include_mythological
include_symbolic
include_not_evaluated
```

If an inclusion flag conflicts with an explicit allowed list, the explicit allowed list SHOULD take precedence.

---

### Requirement flags

The following flags declare minimum requirements for inclusion:

```text
require_provenance
require_evidence
require_signature
require_validation_decision
require_authority_recognition
```

For example, if `require_evidence = true`, assertions without evidence MUST NOT be included unless an explicit exception rule applies.

---

### `fallback_behavior`

Defines what happens when required policy information is unavailable.

Allowed values:

```text
show_unavailable
hide_unavailable
show_with_warning
hold
error
```

#### `show_unavailable`

Show that relevant data exists but cannot be displayed under the active policy.

#### `hide_unavailable`

Silently hide material that cannot be evaluated.

This SHOULD be avoided for audit, research, and governance contexts.

#### `show_with_warning`

Show material with a clear warning that policy evaluation was incomplete.

#### `hold`

Do not activate or publish the view until required policy data becomes available.

#### `error`

Treat policy evaluation failure as an error for this operation.

---

### `show_labels`

If `show_labels` is true, readers MUST preserve relevant validation, certainty, authority, dispute, and scope labels.

If `show_labels` is false, the policy MUST explain why labels may be hidden.

A strict or public-facing reader SHOULD keep `show_labels = true`.

---

### `label_requirements`

A reader policy MAY require specific labels to be displayed.

Recommended values:

```text
artifact_status
assertion_status
validation_status
validated_as
certainty_level
authority_channel
recognition_status
scope
source
provenance
evidence
dispute_status
reader_policy
```

---

## Policy evaluation model

A reader evaluates a candidate artifact or assertion by applying the active reader policy.

Recommended evaluation order:

1. Check access-control and distribution permissions.
2. Check artifact status.
3. Check assertion status.
4. Check validation status.
5. Check validated-as status.
6. Check certainty level.
7. Check authority channel.
8. Check authority recognition.
9. Check scope compatibility.
10. Check provenance and evidence requirements.
11. Check signature or identity requirements.
12. Check dispute, rejection, revocation, deprecated, and superseded flags.
13. Check reader-mode-specific rules.
14. Apply conflict policy.
15. Return included, excluded, held, or included-with-warning.

Evaluation MUST be deterministic given the same inputs and policy.

---

## Policy evaluation result

Implementations SHOULD expose policy evaluation results.

Recommended shape:

```json
{
  "reader_policy_id": "reader_policy:<slug>",
  "target_ref": {},
  "target_level": "assertion",
  "decision": "included",
  "reason_codes": [],
  "labels_required": [],
  "warnings": [],
  "evaluated_at": "RFC3339"
}
```

Allowed decisions:

```text
included
included_with_warning
excluded
held
error
not_evaluated
```

---

## Reason codes

Implementations SHOULD use stable reason codes.

Recommended reason codes:

```text
artifact_status_allowed
artifact_status_not_allowed
assertion_status_allowed
assertion_status_not_allowed
validation_status_allowed
validation_status_not_allowed
validated_as_allowed
validated_as_not_allowed
certainty_allowed
certainty_too_low_for_policy
authority_channel_allowed
authority_channel_denied
authority_channel_missing
recognition_status_allowed
recognition_status_not_allowed
scope_match
scope_mismatch
provenance_present
provenance_missing
evidence_present
evidence_missing
signature_required
signature_present
signature_missing
signature_failed
validation_decision_required
validation_decision_missing
authority_recognition_required
authority_recognition_missing
disputed_included
disputed_excluded
rejected_included
rejected_excluded
revoked_included
revoked_excluded
fictional_included
fictional_excluded
mythological_included
mythological_excluded
not_evaluated_included
not_evaluated_excluded
conflict_preserved
conflict_requires_user_choice
fallback_show_unavailable
fallback_hide_unavailable
fallback_show_with_warning
fallback_hold
fallback_error
```

---

## Conflict policy

Reader policies MUST specify or inherit a conflict policy.

Recommended shape:

```json
{
  "strategy": "preserve_disagreement",
  "require_user_choice": false,
  "preferred_authority_order": [],
  "show_conflict_labels": true
}
```

Standard conflict strategies:

```text
preserve_disagreement
authority_precedence
mark_disputed
exclude_conflict
require_reader_choice
```

Default:

```text
preserve_disagreement
```

A reader policy MUST NOT silently merge conflicting claims unless a declared composition policy explicitly permits that behavior.

---

## Ordering policy

Reader policies MAY specify result ordering.

Recommended shape:

```json
{
  "primary": "authority_precedence",
  "secondary": "certainty_level",
  "tie_breaker": "stable_id"
}
```

Allowed ordering terms:

```text
authority_precedence
certainty_level
validation_status
recognition_status
artifact_status
created_at
updated_at
source_order
stable_id
```

Ordering MUST be deterministic.

If `authority_precedence` is used, the policy MUST define or reference an authority order.

---

## Runtime Pack relationship

A Runtime Pack MAY declare the reader policies it supports.

Recommended field:

```json
{
  "reader_policy_refs": [
    {
      "reader_policy_id": "reader_policy:validated-only-global-reference",
      "policy_hash": {
        "alg": "sha256",
        "value": "<hex>"
      }
    }
  ]
}
```

A Runtime Pack built for a permissive research or creative view MUST NOT be activated as a strict `reference_only` or `validated_only` Runtime Pack unless it also satisfies that stricter policy.

A Runtime Pack SHOULD declare:

* source artifact status;
* included authority channels;
* included validation statuses;
* included certainty levels;
* included validated-as statuses;
* whether disputed material is included;
* whether rejected material is included;
* whether fictional material is included;
* whether mythological material is included;
* supported reader policies.

---

## Query contract relationship

Query systems SHOULD accept a reader policy parameter.

Example:

```json
{
  "query": {
    "type": "entity_lookup",
    "entity_id": "Q42"
  },
  "reader_policy_id": "reader_policy:validated-only-global-reference"
}
```

Query results SHOULD include policy explanation metadata.

Example:

```json
{
  "result_id": "sha256:<hex>",
  "included": true,
  "reader_policy_id": "reader_policy:validated-only-global-reference",
  "policy_decision": "included",
  "reason_codes": [
    "validation_status_allowed",
    "authority_channel_allowed",
    "certainty_allowed"
  ],
  "visible_labels": {
    "validation_status": "validated",
    "validated_as": "institutional_reference",
    "certainty_level": "high",
    "authority_channel": "authority:global-reference"
  }
}
```

A query result MUST NOT hide that a visible assertion is disputed, rejected, fictional, mythological, low-certainty, not evaluated, or recognized only by a specific authority channel when that status is known.

---

## Federation relationship

Federations may contain shards or Exchanges with different authority channels, validation statuses, certainty levels, scopes, and conflict statuses.

A reader policy applied to a federation MUST evaluate each included target according to policy.

Federation MUST preserve source identity.

Reader policy MUST NOT silently erase:

* shard identity;
* source artifact identity;
* publisher identity;
* authority channel;
* validation status;
* recognition status;
* certainty level;
* scope;
* lineage;
* conflict status.

---

## Authority-channel relationship

A reader policy MAY select authority channels.

Examples:

```json
{
  "allowed_authority_channels": [
    "authority:unesco-global-reference",
    "authority:who-health",
    "authority:wikidata-community"
  ]
}
```

Authority selection is scoped.

Recognition by one authority channel MUST NOT be treated as recognition by another unless an explicit authority-recognition relationship supports that interpretation.

If delegated authority is allowed, the reader policy SHOULD declare whether delegated channels are included.

Recommended field:

```json
{
  "include_delegated_authorities": true,
  "delegation_depth": 1
}
```

---

## Strict validated-only profile

Recommended profile:

```json
{
  "schema_version": "5.0",
  "artifact_type": "reader_policy",
  "reader_policy_id": "reader_policy:strict-validated-only",
  "name": "Strict validated-only",
  "mode": "validated_only",

  "allowed_artifact_statuses": ["recognized", "reference"],
  "allowed_assertion_statuses": ["validated"],
  "allowed_validation_statuses": ["validated"],
  "allowed_recognition_statuses": ["recognized"],
  "allowed_certainty_levels": ["medium", "high", "established"],
  "allowed_validated_as": [
    "reviewed_claim",
    "high_confidence_fact",
    "institutional_reference",
    "technical_specification"
  ],

  "include_disputed": false,
  "include_rejected": false,
  "include_revoked": false,
  "include_deprecated": false,
  "include_superseded": false,
  "include_fictional": false,
  "include_mythological": false,
  "include_symbolic": false,
  "include_not_evaluated": false,

  "require_provenance": true,
  "require_evidence": true,
  "require_signature": true,
  "require_validation_decision": true,
  "require_authority_recognition": true,

  "fallback_behavior": "show_unavailable",
  "show_labels": true,
  "label_requirements": [
    "validation_status",
    "validated_as",
    "certainty_level",
    "authority_channel",
    "recognition_status",
    "scope"
  ],

  "conflict_policy": {
    "strategy": "preserve_disagreement",
    "require_user_choice": false,
    "show_conflict_labels": true
  }
}
```

---

## Research profile

Recommended profile:

```json
{
  "schema_version": "5.0",
  "artifact_type": "reader_policy",
  "reader_policy_id": "reader_policy:research",
  "name": "Research",
  "mode": "research",

  "allowed_artifact_statuses": ["draft", "working", "under_review", "recognized", "reference", "deprecated", "superseded"],
  "allowed_assertion_statuses": ["hypothesis", "claimed", "sourced", "disputed", "reviewed", "validated", "rejected", "superseded"],
  "allowed_validation_statuses": ["not_evaluated", "in_review", "validated", "conditionally_validated", "disputed", "rejected"],
  "allowed_recognition_statuses": ["recognized", "conditionally_recognized", "under_review", "disputed", "rejected", "deprecated"],
  "allowed_certainty_levels": ["unknown", "speculative", "low", "medium", "high", "established", "not_applicable"],
  "allowed_validated_as": [
    "hypothesis",
    "claim",
    "sourced_claim",
    "reviewed_claim",
    "high_confidence_fact",
    "institutional_reference",
    "publisher_declaration",
    "technical_specification",
    "legal_or_policy_position",
    "disputed_position",
    "rejected_claim"
  ],

  "include_disputed": true,
  "include_rejected": true,
  "include_revoked": false,
  "include_deprecated": true,
  "include_superseded": true,
  "include_fictional": false,
  "include_mythological": false,
  "include_symbolic": true,
  "include_not_evaluated": true,

  "require_provenance": false,
  "require_evidence": false,
  "require_signature": false,
  "require_validation_decision": false,
  "require_authority_recognition": false,

  "fallback_behavior": "show_with_warning",
  "show_labels": true
}
```

---

## Creative profile

Recommended profile:

```json
{
  "schema_version": "5.0",
  "artifact_type": "reader_policy",
  "reader_policy_id": "reader_policy:creative",
  "name": "Creative",
  "mode": "creative",

  "allowed_artifact_statuses": ["draft", "working", "under_review", "recognized", "reference"],
  "allowed_assertion_statuses": ["hypothesis", "claimed", "sourced", "disputed", "reviewed", "validated"],
  "allowed_validation_statuses": ["not_evaluated", "in_review", "validated", "conditionally_validated", "disputed"],
  "allowed_recognition_statuses": ["recognized", "conditionally_recognized", "under_review", "disputed"],
  "allowed_certainty_levels": ["unknown", "speculative", "low", "medium", "not_applicable"],
  "allowed_validated_as": [
    "hypothesis",
    "claim",
    "sourced_claim",
    "mythological_corpus",
    "fictional_corpus",
    "symbolic_model",
    "disputed_position"
  ],

  "include_disputed": true,
  "include_rejected": false,
  "include_revoked": false,
  "include_deprecated": false,
  "include_superseded": false,
  "include_fictional": true,
  "include_mythological": true,
  "include_symbolic": true,
  "include_not_evaluated": true,

  "require_provenance": false,
  "require_evidence": false,
  "require_signature": false,
  "require_validation_decision": false,
  "require_authority_recognition": false,

  "fallback_behavior": "show_with_warning",
  "show_labels": true
}
```

---

## All-with-labels profile

Recommended profile:

```json
{
  "schema_version": "5.0",
  "artifact_type": "reader_policy",
  "reader_policy_id": "reader_policy:all-with-labels",
  "name": "All with labels",
  "mode": "all_with_labels",

  "allowed_artifact_statuses": ["draft", "working", "under_review", "recognized", "reference", "deprecated", "superseded", "revoked"],
  "allowed_assertion_statuses": ["hypothesis", "claimed", "sourced", "disputed", "reviewed", "validated", "rejected", "retracted", "superseded"],
  "allowed_validation_statuses": ["not_evaluated", "in_review", "validated", "conditionally_validated", "disputed", "rejected", "revoked"],
  "allowed_recognition_statuses": ["recognized", "conditionally_recognized", "under_review", "disputed", "rejected", "deprecated", "revoked"],
  "allowed_certainty_levels": ["unknown", "speculative", "low", "medium", "high", "established", "not_applicable"],
  "allowed_validated_as": [
    "hypothesis",
    "claim",
    "sourced_claim",
    "reviewed_claim",
    "high_confidence_fact",
    "institutional_reference",
    "publisher_declaration",
    "technical_specification",
    "legal_or_policy_position",
    "mythological_corpus",
    "fictional_corpus",
    "symbolic_model",
    "disputed_position",
    "rejected_claim"
  ],

  "include_disputed": true,
  "include_rejected": true,
  "include_revoked": true,
  "include_deprecated": true,
  "include_superseded": true,
  "include_fictional": true,
  "include_mythological": true,
  "include_symbolic": true,
  "include_not_evaluated": true,

  "require_provenance": false,
  "require_evidence": false,
  "require_signature": false,
  "require_validation_decision": false,
  "require_authority_recognition": false,

  "fallback_behavior": "show_with_warning",
  "show_labels": true
}
```

---

## “100% validated” interpretation

In Kristal v5, a reader may choose a “100% validated” view.

This means:

```text
All visible assertions satisfy the active reader policy.
```

It does not mean:

```text
All assertions have maximum certainty.
All assertions are universally true.
All authorities agree.
All hidden assertions do not exist.
All material outside the policy is invalid.
```

For example, a strict validated-only reader may include a validated hypothesis if the policy allows:

```json
{
  "validation_status": "validated",
  "validated_as": "hypothesis",
  "certainty_level": "speculative"
}
```

The assertion is valid as a hypothesis, not as established fact.

---

## Missing information

Reader policies MUST define what happens when information required for policy evaluation is missing.

Examples:

* validation status missing;
* certainty level missing;
* authority channel missing;
* provenance missing;
* evidence missing;
* signature status unavailable;
* revocation status unavailable offline;
* authority registry unavailable;
* reader policy hash mismatch.

The result MUST be one of:

```text
included
included_with_warning
excluded
held
error
not_evaluated
```

A strict policy SHOULD exclude or hold when required information is unavailable.

A research policy MAY include with warning.

---

## Label preservation

Readers MUST preserve labels needed to understand why material is visible.

At minimum, when available, a reader SHOULD expose:

* artifact status;
* assertion status;
* validation status;
* validated-as status;
* certainty level;
* authority channel;
* recognition status;
* scope;
* provenance or source link;
* dispute status;
* reader policy ID.

A reader MUST NOT flatten scoped validation into universal truth.

A reader MUST NOT hide that a claim is fictional, mythological, disputed, rejected, revoked, or validated only by a specific authority channel when that status is known.

---

## Caching and offline behavior

Offline readers MAY use cached reader policies.

A cached reader policy SHOULD include:

* `reader_policy_id`;
* policy hash;
* created time;
* issuer;
* scope;
* signatures, if required;
* expiry, if required;
* source authority registry reference.

If a reader policy is expired or cannot be verified, the client MUST follow fallback behavior.

A Runtime Pack MUST NOT be activated under an unverifiable reader policy when the distribution or activation policy requires reader policy verification.

---

## Security and correctness considerations

Implementations SHOULD defend against:

* authority laundering;
* validation laundering;
* certainty laundering;
* hiding low-certainty labels;
* hiding dispute labels;
* hiding rejected or revoked status;
* presenting filtered views as complete corpora;
* applying a permissive Runtime Pack under a strict reader policy;
* applying a reader policy outside its declared scope;
* silently changing authority-channel lists;
* silently changing policy hashes;
* treating signatures as validation;
* treating authority recognition as universal authority;
* treating “validated-only” as “maximum-certainty-only”;
* treating missing evidence as equivalent to validated evidence;
* treating fictional or mythological material as physical-world truth.

---

## Conformance requirements

A Kristal v5 reader-policy implementation MUST:

1. support the standard reader modes;
2. expose or apply explicit filtering rules for each mode;
3. distinguish validation status from certainty level;
4. distinguish authority recognition from validation;
5. distinguish artifact status from assertion status;
6. preserve labels required by active policy;
7. apply policy deterministically;
8. preserve disagreement unless the policy declares another conflict strategy;
9. prevent Working Artifacts from being shown as Reference Artifacts unless recognition supports that status;
10. prevent fictional or mythological material from being shown as physical-world truth unless explicitly validated under that epistemic mode.

A conformant implementation SHOULD:

1. support signed reader policies;
2. expose policy evaluation decisions;
3. expose reason codes;
4. support offline reader policy evaluation;
5. allow runtime activation to check reader policy compatibility;
6. support delegated authority-channel selection;
7. support research and creative modes without losing labels;
8. support strict public modes for validated or reference-only views.

---

## Conformance tests

A conforming implementation MUST provide fixtures demonstrating:

* `reference_only` includes recognized reference material;
* `reference_only` excludes Working Artifacts without recognition;
* `validated_only` includes allowed validated-as statuses;
* `validated_only` preserves validated hypothesis labels when allowed;
* `high_certainty_only` excludes low-certainty material;
* `research` includes low-certainty material with labels;
* `research` includes disputed material with labels;
* `creative` includes fictional material with labels;
* `creative` includes mythological material with labels;
* `creative` does not present fiction as physical-world truth;
* `all_with_labels` preserves rejected and revoked status;
* custom mode fails if no explicit rules are declared;
* missing evidence is handled according to fallback behavior;
* missing authority channel is handled according to fallback behavior;
* reader-policy mismatch blocks Runtime Pack activation when required;
* permissive Runtime Pack is not activated as strict reference-only pack;
* conflict policy preserves disagreement by default;
* authority-channel denial overrides allowance when both are present;
* policy evaluation is deterministic for the same inputs.

---

## Open questions

The following decisions remain open:

* Should `show_labels` be required to be `true` for all public reader policies?
* Should `validated_only` include validated hypotheses by default, or require explicit inclusion?
* Should `reference_only` require authority recognition in addition to validation?
* Should reader policies be signed artifacts in all Runtime Packs?
* Should delegated authority inclusion default to false?
* Should `all_with_labels` include revoked material by default, or only under audit mode?
* Should strict public readers hide unavailable material or show unavailable placeholders?
* Should reader policy hashes be mandatory in Runtime Pack manifests?
* Should conflict strategy be part of reader policy, federation policy, or both?
* Should access control and reader policy share a profile, or remain completely separate?
