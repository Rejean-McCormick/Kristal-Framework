# Plural Validation and Federated Authority

## Status

Draft (v5 normative overview)

## Purpose

This document defines how Kristal v5 handles plural validation, authority channels, certainty levels, divergent forks, and federated knowledge.

Kristal v5 does not assume that one institution, platform, model, government, company, association, or community owns truth for every domain.

Instead, Kristal v5 makes authority explicit.

A Kristal may contain hypotheses, sourced claims, disputed claims, fictional structures, mythological corpora, research drafts, institutional records, technical declarations, and high-confidence reference material. These may coexist in the same ecosystem without being confused.

The core rule is:

> A Kristal may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.
> A Kristal must not present an assertion as validated outside the authority channel, scope, certainty level, and validation policy that support that status.

Validation is scoped.

Authority is plural.

Certainty is explicit.

Readers choose policy.

Federation preserves disagreement.

Integrity protects artifact identity and provenance.

---

## 1. Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

---

## 2. Core model

Kristal v5 separates six concepts that MUST NOT be collapsed:

```text
artifact existence
artifact integrity
assertion status
certainty level
authority recognition
reader visibility
```

A Kristal object may exist and be well-formed without being recognized by any authority.

A Kristal object may be signed and content-addressed without being accepted as a reference artifact.

An assertion may be validated as a hypothesis without being validated as a high-confidence fact.

A mythological corpus may be valid as mythology without being valid as a physical-world claim.

A reader may choose to show only material accepted by selected authority channels, but that reader policy does not erase the existence of other material.

---

## 3. Artifact existence

A Kristal may be created by:

* an individual;
* a research collective;
* an association;
* a company;
* a government;
* an academic institution;
* an intergovernmental organization;
* an AI-assisted validator;
* a community;
* a hybrid human-machine process.

Creation does not imply recognition.

Publication does not imply recognition.

Signature does not imply recognition.

Distribution does not imply recognition.

Existence only means that the object exists as a structured Kristal artifact.

---

## 4. Artifact integrity

Artifact integrity answers questions such as:

* Is the artifact well-formed?
* Does it match its schema?
* Does its hash match its declared content?
* Are its signatures valid?
* Is its provenance structurally present?
* Does it preserve lineage?
* Is it reproducible under the declared profile?

Artifact integrity does not answer:

* Is the assertion true?
* Is the assertion high certainty?
* Is the authority competent?
* Is the artifact accepted by a given institution?
* Should a reader show this artifact by default?

Integrity protects the object.

It does not decide truth.

---

## 5. Assertion status

Assertions in Kristal v5 SHOULD carry an explicit `assertion_status`.

Recommended assertion statuses are:

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

An assertion status describes the epistemic state of the assertion inside a declared process.

It MUST NOT be interpreted without scope, provenance, and authority context.

For example:

```text
validated
```

is incomplete unless the system can also answer:

```text
validated as what?
validated by whom?
validated under which policy?
validated for which scope?
validated at what certainty level?
```

---

## 6. Certainty level

Assertions in Kristal v5 SHOULD carry an explicit `certainty_level`.

Recommended certainty levels are:

```text
unknown
speculative
low
medium
high
established
not_applicable
mixed
```

Certainty describes the strength, confidence, or applicability of an assertion within its declared scope.

Certainty is not the same as validation.

A claim may be:

```text
validated as a hypothesis
```

while still having:

```text
certainty_level = speculative
```

A fictional or mythological assertion may be:

```text
validated as fictional_corpus
```

or:

```text
validated as mythological_corpus
```

with:

```text
certainty_level = not_applicable
```

A technical declaration by a company about its own system may be:

```text
validated as publisher_declaration
```

without being independently validated as a physical, legal, environmental, or social impact claim.

---

## 7. Validation mode

Validation MUST be scoped by `validated_as`.

Recommended validation modes are:

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

Validation does not always mean maximum certainty.

Validation means:

```text
accepted as X
by authority channel Y
under policy Z
for scope S
with certainty level C
```

A reader may choose to use only validated data, but that does not mean every visible assertion has the same certainty level or the same epistemic mode.

For example, a `validated_only` reader policy may include:

* validated hypotheses;
* validated institutional references;
* validated technical specifications;
* validated mythology corpora;
* validated high-confidence facts;
* validated publisher declarations.

The reader policy decides which of those validation modes are visible.

---

## 8. Authority channels

An authority channel declares who is recognized for a domain, under which scope, and according to which policy.

An authority channel SHOULD include:

```json
{
  "authority_channel_id": "authority:<slug>",
  "name": "string",
  "authority_type": "institution|government|association|company|research_collective|individual|ai_validator|community|standards_body",
  "scope": {},
  "recognized_by": [],
  "trust_roots": [],
  "validation_policies": [],
  "revocation_policy_ref": null
}
```

Authority channels MAY represent:

* individual researchers;
* research groups;
* universities;
* companies;
* governments;
* associations;
* standards bodies;
* expert bodies;
* community groups;
* intergovernmental organizations;
* AI-assisted validation systems;
* hybrid human-machine collectives.

No authority channel has universal scope unless an explicit policy defines the scope and other authority channels recognize it.

Recognition by one authority channel MUST NOT imply recognition by another.

---

## 9. Authority delegation

Authority channels MAY recognize other authority channels.

Examples:

* an international education channel may recognize a scientific organization for a science education scope;
* a government may recognize a national statistics agency for population data;
* a standards body may recognize a technical working group for a protocol profile;
* a university may recognize a laboratory for a research shard;
* a company may be recognized as the primary publisher for documentation about its own systems.

Delegation MUST be explicit.

A delegated authority MUST have:

* a declared scope;
* a recognition record;
* a validation policy or policy reference;
* a revocation or correction path, when applicable.

Delegation MUST NOT erase attribution.

A downstream reader MUST be able to distinguish:

```text
directly validated by authority A
```

from:

```text
recognized by authority A because authority A recognizes authority B for this scope
```

---

## 10. Authority recognition

Authority recognition records that an authority channel accepts a target under a declared scope and policy.

The target MAY be:

```text
artifact
shard
assertion
authority_channel
dataset
runtime_pack
reader_policy
```

Recommended shape:

```json
{
  "recognition_id": "sha256:<hex>",
  "artifact_type": "authority_recognition",
  "issuer_authority_channel": "authority:<slug>",
  "target_ref": {},
  "target_level": "artifact|shard|assertion|authority_channel|dataset|runtime_pack",
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

Recommended recognition statuses are:

```text
recognized
conditionally_recognized
under_review
disputed
rejected
deprecated
revoked
```

Recognition is not universal unless the recognition scope says so and the reader policy chooses to treat it that way.

---

## 11. Validation reports

A validation report records what was checked, by whom or by what system, under which policy, for which target.

A validation report MAY apply to:

* an artifact;
* a Structured Epistemic State;
* an Exchange;
* a shard;
* a federation;
* an assertion;
* an authority channel;
* an authority registry;
* a runtime pack;
* a reader policy;
* a dataset;
* an export.

A validation report MUST NOT be reduced to a single universal boolean.

The following is insufficient:

```json
{
  "validated": true
}
```

A v5 validation report SHOULD instead record:

```json
{
  "validation_status": "validated",
  "validated_as": "high_confidence_fact",
  "certainty_level": "high",
  "authority_channel": "authority:<slug>",
  "validation_policy_ref": {},
  "scope": {}
}
```

Validation reports may support recognition decisions, reader policies, publication decisions, or runtime decisions, but they do not automatically make every consuming system accept the target.

---

## 12. Reader policies

A reader policy decides what a person, application, AI system, or runtime surface chooses to display or use.

Reader policy is not the same as validation.

Reader policy is not the same as authority recognition.

Reader policy is a visibility and selection rule.

Recommended reader modes are:

```text
reference_only
validated_only
high_certainty_only
research
creative
all_with_labels
custom
```

A reader policy MAY filter by:

* artifact status;
* assertion status;
* validation status;
* certainty level;
* validated-as mode;
* authority channel;
* recognition status;
* domain;
* subdomain;
* jurisdiction;
* time window;
* language;
* inclusion of disputed material;
* inclusion of fictional material;
* inclusion of mythological material.

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

A reader may choose “only validated data.”

That means:

```text
all visible assertions satisfy the active reader policy
```

It does not mean:

```text
all visible assertions have maximum certainty
all authorities agree
all assertions are universally true
all omitted assertions do not exist
```

---

## 13. Federation

Federation allows multiple Kristals, shards, authority channels, or corpora to coexist and be composed without silent merging.

Federation MUST preserve:

* source identity;
* shard identity;
* authority channel;
* validation status;
* certainty metadata;
* scope;
* provenance;
* lineage;
* disagreement.

Federation MUST NOT silently collapse conflicting assertions into a single unlabelled claim.

Recommended federation rule:

```text
preserve disagreement by default
```

A federation policy MAY define precedence rules, but precedence MUST be explicit and visible.

Examples of composition strategies:

```text
authority_precedence
latest_time_window
explicit_allow_deny
preserve_all
reader_policy_selected
```

Examples of conflict strategies:

```text
preserve_disagreement
authority_precedence
mark_disputed
exclude_conflict
require_reader_choice
```

The default v5 conflict strategy SHOULD be:

```text
preserve_disagreement
```

---

## 14. Divergent forks

A Kristal MAY be copied, forked, extended, reinterpreted, or republished under another authority channel.

Forking is permitted.

Forking MUST preserve lineage.

A forked Kristal MUST NOT inherit authority recognition from the source unless that recognition is explicitly preserved by the recognizing authority channel.

A forked Kristal SHOULD declare:

* source artifact reference;
* lineage;
* publisher;
* authority channel;
* scope;
* validation policy;
* recognition status;
* certainty metadata;
* reader-policy recommendations.

Divergent forks are valid artifacts when they are well-formed and preserve their labels.

They are not necessarily reference artifacts.

They are not necessarily recognized by the same authorities as the source.

---

## 15. Disputed and fringe positions

Kristal v5 allows disputed, minority, speculative, or fringe positions to be represented as structured artifacts.

This is intentional.

The system’s job is not to prevent divergent world-models from being expressed.

The system’s job is to prevent them from being mislabeled.

For example, a group may publish a Kristal containing its arguments for a disputed physical-world claim.

Such a Kristal may be:

```text
artifact_status = working
authority_channel = authority:<group>
validated_as = disputed_position
certainty_level = low
recognition_status = recognized by that group
```

Another authority channel may mark the same assertion as:

```text
validation_status = rejected
validated_as = rejected_claim
certainty_level = established
authority_channel = authority:<scientific-body>
```

Federation preserves both records without making them equivalent.

Reader policies decide what is visible by default.

---

## 16. Mythology, fiction, and symbolic systems

A Kristal may describe mythology, fiction, religious narratives, symbolic systems, games, simulations, or imaginary worlds.

Such a Kristal may be valid within its own scope.

Examples:

```text
validated_as = mythological_corpus
certainty_level = not_applicable
scope.domain = mythology
```

```text
validated_as = fictional_corpus
certainty_level = not_applicable
scope.domain = fiction
```

A mythology Kristal MUST NOT be presented as validated physical-world truth unless a declared authority channel explicitly validates that epistemic mode and the reader policy includes that mode.

A fiction Kristal MUST NOT be presented as historical or scientific reference unless such a mapping is explicitly declared and validated by an appropriate authority channel.

---

## 17. Research and independent claims

Kristal v5 supports independent research.

An independent researcher may publish a Kristal containing:

* hypotheses;
* evidence;
* prototype data;
* experiments;
* models;
* citations;
* objections;
* responses;
* uncertainty;
* replication requests.

Such a Kristal may begin as:

```text
assertion_status = hypothesis
certainty_level = speculative
artifact_status = working
```

It may later receive:

* peer review;
* institutional validation;
* expert-body recognition;
* governmental recognition;
* intergovernmental recognition;
* replication evidence;
* rejection or correction.

The system MUST preserve the research lifecycle without requiring final recognition before materialization.

---

## 18. Institutional and publisher declarations

A company, agency, institution, or organization may publish Kristals describing its own systems, policies, datasets, or operations.

Such Kristals may be validated as:

```text
publisher_declaration
technical_specification
legal_or_policy_position
institutional_reference
```

A publisher declaration is not automatically a high-confidence independent fact.

For example:

* a software company may be authoritative for the declared interface of its own API;
* it may not be the only authority for security impact, environmental impact, legal compliance, or social consequences;
* those other scopes may require other authority channels.

Kristal v5 MUST allow multiple authority channels to attach separate recognition and validation records to the same target.

---

## 19. Wikidata Seed Kristal

The first global seed corpus may be represented as a Wikidata Seed Kristal.

This means a Kristal-compatible packaging or alignment of the Wikidata corpus.

It SHOULD preserve as much of the source structure as possible, including:

* entities;
* properties;
* statements;
* qualifiers;
* references;
* ranks;
* labels;
* aliases;
* descriptions;
* source identifiers.

The seed corpus MAY be recognized as an institutional or public reference corpus.

That recognition MUST NOT imply that every inherited statement is maximally certain.

A Wikidata Seed Kristal may contain mixed certainty levels and multiple assertion statuses.

A reader policy may choose a high-confidence view, a full-statement view, a best-rank projection, or a research view.

The source corpus remains valuable because it provides a structured base for further validation, correction, extension, and federation.

---

## 20. Global reference authority

An intergovernmental or international organization MAY act as a global reference authority channel for selected scopes.

Such an authority channel MAY:

* recognize seed corpora;
* recognize other authority channels;
* recognize expert bodies;
* validate public reference artifacts;
* publish global reader policies;
* define correction and revocation processes;
* delegate domain-specific authority.

It MUST NOT be treated as owning all truth.

It MUST declare scope.

It MUST expose policy.

It MUST preserve lineage.

It MUST allow other authorities to exist.

It SHOULD make delegated recognition visible.

Example pattern:

```text
authority:global-reference
recognizes authority:health-organization
for scope.domain = health
under validation_policy_ref = policy:global-health-reference
```

The global authority does not need to revalidate every assertion manually if it explicitly recognizes another authority channel as competent for the scope.

---

## 21. Authority laundering

Authority laundering occurs when recognition or validation from one scope is presented as if it came from another scope or stronger authority.

Kristal v5 MUST prevent authority laundering.

Examples of authority laundering include:

* presenting a community-recognized claim as if it were recognized by a scientific body;
* presenting a company declaration as if it were independent audit;
* presenting a mythological corpus as physical-world fact;
* presenting a reader-policy selection as universal truth;
* hiding that a claim is disputed;
* dropping rejected-status metadata during export;
* omitting authority channel labels from a rendered view.

Systems that render, query, export, distribute, or summarize Kristals MUST preserve authority labels when they affect meaning.

---

## 22. Rendering obligations

User-facing systems SHOULD make the following visible or inspectable:

* assertion status;
* certainty level;
* validated-as mode;
* authority channel;
* recognition status;
* validation policy;
* scope;
* provenance;
* evidence references;
* dispute status;
* lineage;
* reader policy currently active.

A summary or UI MAY simplify presentation, but it MUST NOT flatten scoped validation into universal truth.

Architect, readers, search surfaces, agents, exports, and dashboards SHOULD preserve labels whenever omission would mislead the user.

---

## 23. Query obligations

Kristal v5 query systems SHOULD be able to filter or expose:

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

A query result SHOULD indicate whether it is filtered by a reader policy.

A query result MUST NOT imply that omitted material does not exist unless the query explicitly searched the complete source set.

---

## 24. Export obligations

Exports such as JSON-LD, RDF, WDQS-compatible projections, runtime packs, summaries, reports, and static bundles MUST preserve status metadata when that metadata affects meaning.

An export MAY be filtered.

If filtered, it SHOULD declare:

* export policy;
* reader policy;
* included authority channels;
* included validation statuses;
* included certainty levels;
* included validated-as modes;
* projection mode.

Exporting a Kristal MUST NOT silently remove disagreement in a way that changes the meaning of the remaining artifact.

---

## 25. Runtime and distribution obligations

Runtime systems and distribution systems MAY choose stricter activation or display policies.

For example, a runtime may choose:

* only reference artifacts;
* only selected authority channels;
* only high-certainty assertions;
* only validated assertions;
* no disputed material;
* no fictional or mythological material unless explicitly enabled.

Such choices are reader or runtime policies.

They do not define global truth.

Runtime systems SHOULD preserve enough metadata for users and downstream systems to understand what was included, excluded, or deferred.

---

## 26. Correction, revocation, and supersession

Authority channels SHOULD support correction and revocation paths.

A recognition may be:

```text
deprecated
revoked
superseded
```

An assertion may be:

```text
retracted
superseded
rejected
```

Revocation MUST preserve history and lineage sufficient to understand what was revoked and by whom.

A revocation by one authority channel does not automatically revoke recognition by all other authority channels unless a policy explicitly links them.

---

## 27. Minimal conforming plural authority behavior

A Kristal v5 implementation that supports plural validation and federated authority MUST:

1. represent authority channels explicitly;
2. represent scope explicitly;
3. distinguish validation status from certainty level;
4. distinguish artifact integrity from assertion status;
5. support validation or recognition references;
6. avoid universal `validated = true` semantics;
7. preserve disagreement under federation;
8. avoid silent authority laundering;
9. expose reader policy where filtering is applied;
10. preserve lineage when forking or composing artifacts.

---

## 28. Non-goals

This document does not define:

* which authority channels should be trusted by default;
* which institution should validate a specific domain;
* which reader policy a platform must use;
* whether a disputed claim is correct;
* how social consensus is formed;
* how expert review is conducted operationally;
* how an AI validator reaches a judgment;
* how Orgo workflows approve submissions;
* how Konnaxion distributes runtime packs;
* how SenTient resolves ambiguous source material;
* how Architect renders every UI state.

Those concerns are handled by other Kristal v5 documents, ecosystem contracts, authority policies, and implementation-specific workflows.

This document defines the shared conceptual and normative boundary:

> multiple authorities may exist;
> validation is scoped;
> certainty is explicit;
> readers choose policy;
> federation preserves disagreement;
> no authority recognition may be silently borrowed from another scope.
