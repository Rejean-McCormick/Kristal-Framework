# Kristal Standard 6.0 — Core specification

## Status

This document defines the active conceptual and wire-level center of Kristal Standard 6.0. The canonical artifact is `kristal_state` with `schema_version: "6.0"`.

Legacy v5 Structured Epistemic State, Exchange, Runtime Pack, shard and federation surfaces remain available as compatibility contracts under `../kristal-docs-v5/`. They are not the conceptual center of new v6 domain models.

## 1. Purpose

Kristal is a portable structured-memory and actionability layer for knowledge, state, rules, observations, decisions and actions. It preserves work performed by humans and machines as explicit, contextual, traceable assertions that can be enriched over time.

Kristal MUST NOT silently convert storage into authority or automation into permission to act.

## 2. Canonical state

A v6 state MUST declare:

```json
{
  "schema_version": "6.0",
  "artifact_type": "kristal_state"
}
```

A state contains atomic assertions and MAY contain state-level applicability, source references, provenance, validation/recognition references, reader-policy references, lineage, build metadata, warnings, extensions, signatures and deterministic identity metadata.

## 3. Atomic assertions

The canonical content unit remains an independently addressable statement:

```text
subject → predicate → object
```

Two statements that differ in evidence, applicability, valuation, authority, role or actionability SHOULD be independently representable even when they appear together in prose.

## 4. Typed valuations

v6 replaces the assumption of one universal `certainty_level` with `valuations[]`.

A valuation MUST declare:

- `dimension` — what is being measured;
- `value_semantics` — the shape of the value;
- `value_state` — whether the value is known/applicable/measured;
- `value` only when `value_state = known`.

Supported semantic families are:

- `boolean`;
- `categorical`;
- `set`;
- `ordinal`;
- `scalar`;
- `interval`;
- `probability`;
- `distribution`;
- `vector`;
- `partial_order`;
- `state`;
- `temporal`.

Supported value states are:

- `known`;
- `unknown`;
- `not_applicable`;
- `indeterminate`;
- `not_measured`.

`unknown` MUST NOT be treated as zero. `not_applicable` MUST NOT be treated as low, false or zero.

## 5. Coordinates and applicability

`coordinates` describe where an assertion sits in the domain geometry. They can represent scale, layer, variant, operating condition, process phase, taxonomy, technological axis or another domain-defined dimension.

`applicability` describes where/when/for whom an assertion is applicable. Typical dimensions include domain, subdomain, jurisdiction, time window, environment, language and tenant/context.

A temporal coordinate describing an event MUST NOT automatically be interpreted as an applicability window.

## 6. Record roles

`record_role` identifies the functional role of an assertion. Core roles are:

- `authoritative_constraint`;
- `observed_state`;
- `organizational_rule`;
- `reference_knowledge`;
- `derived_state`;
- `decision`;
- `action`;
- `structural_record`.

A role classifies the record; it does not manufacture source authority.

## 7. Actionability

`actionability` describes whether the represented policy requires human judgment before an action path can be attempted.

Core modes are:

- `automatic`;
- `human_review`;
- `human_decision`;
- `manual`;
- `prohibited`;
- `insufficient_information`;
- `not_applicable`.

The invariant is:

```text
actionability.mode = automatic
≠ execution authority
```

A target system MUST still enforce its own authentication, authorization, admission and mutation contracts.

## 8. Traceability

Kristal keeps the following concepts distinct:

```text
evidence
≠ provenance
≠ validation
≠ authority recognition
≠ signature integrity
```

Evidence supports an assertion. Provenance records where the representation came from and how it was produced. Validation evaluates under a policy. Recognition records scoped authority acceptance. Signatures prove integrity/authorship under a trust model.

## 9. Conflict, succession and lineage

Assertions MAY preserve disagreement through `conflicts_with`, replacement through `supersedes`, and derivation/specialization through `lineage`.

Consumers MUST NOT erase conflicting assertions solely to force a single global truth view.

## 10. Identity and canonicalization

The active canonicalization profile is:

```text
kristal.v6:jcs-rfc8785
```

The v6 state hash target excludes:

- `state_id`;
- `content_hash`;
- `signatures`.

Equivalent hash-target content MUST produce the same canonical bytes and SHA-256 state identity.

Identity proves content equality; it does not prove validity or authority.

## 11. Organizational memory

A state MAY combine external constraints, observed state, organizational rules, reference knowledge, derived state, decisions and actions while preserving their roles.

This enables cumulative human/AI work:

```text
research / observation / reasoning
        ↓
traceable assertions
        ↓
validation / correction / new evidence
        ↓
richer state
        ↓
next human or machine inherits prior work
```

A human decision MAY later be generalized into an organizational rule only through an explicit, traceable organizational process. Kristal MUST NOT silently infer durable policy from one decision.

## 12. Derived views and legacy surfaces

Reader policies, indexes, timelines, diagnostic trees, pathways, query stores and runtime materializations are derived views. They SHOULD remain rebuildable from canonical state plus declared policy/transform inputs.

Legacy v5 Exchange and Runtime Pack surfaces MAY remain in production through adapters. New v6 domain models SHOULD use `kristal_state` as the canonical truth layer.
