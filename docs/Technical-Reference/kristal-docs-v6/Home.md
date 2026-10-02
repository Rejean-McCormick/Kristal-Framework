# Kristal Framework — Wiki

**Active baseline: Kristal Standard 6.0.0.**

Kristal is a deterministic, portable knowledge/state artifact system. Its purpose is to preserve structured work — human or machine — as explicit, traceable, reusable assertions that can be enriched over time and made actionable without confusing knowledge with authority or automation with permission to act.

Kristal v6 generalizes the older epistemic vocabulary into a domain-neutral state model:

```text
referents + atomic assertions
        │
        ├── valuations[]          typed measures / states
        ├── coordinates          domain geometry
        ├── applicability        where / when / for whom
        ├── record_role          what kind of record this is
        ├── actionability        automation / human boundary
        ├── provenance/evidence  why and where it came from
        ├── validation           policy evaluation
        ├── recognition          scoped authority
        ├── conflict/succession  disagreement and replacement
        └── lineage              derivation / specialization
        │
        ▼
reader policies + derived projections + authorized actions
```

The central canonical artifact is **`kristal_state`**.

---

## Start here

- [Quickstart](Quickstart.md)
- [What-is-Kristal](What-is-Kristal.md)
- [Concepts-and-Mental-Model](Concepts-and-Mental-Model.md)
- [Kristal-State](Kristal-State.md)
- [Valuations-and-Value-Semantics](Valuations-and-Value-Semantics.md)
- [Record-Roles](Record-Roles.md)
- [Actionability-and-Human-Boundaries](Actionability-and-Human-Boundaries.md)
- [Glossary](Glossary.md)

---

## Why v6 matters

Kristal no longer assumes that one field called “certainty” always means the same thing. A domain may use an ordered valuation for proof closure, diagnostic support, constitutive necessity, applicability, taxonomic acceptance, intervention necessity, consensus, compatibility, or another explicit dimension.

Likewise, values are not forced into one numeric scale. Kristal v6 can represent:

- boolean values;
- categorical values;
- sets;
- ordinal scales;
- continuous scalars;
- intervals;
- probabilities;
- distributions;
- vectors;
- partial orders;
- state-machine states;
- temporal values.

`unknown`, `not_applicable`, `indeterminate`, and `not_measured` are value states, not disguised numbers.

---

## Core separation

```text
artifact identity
≠ assertion content
≠ valuation
≠ applicability
≠ validation
≠ authority recognition
≠ reader visibility
≠ actionability
≠ execution authority
```

This separation lets Kristal preserve nuance while still deriving simple operational decisions.

A rule may be authoritative. An observation may simply record state. An organizational rule may reflect local practice. A derived conclusion may be machine-produced. An action may be eligible for automation. None of these roles silently changes who is allowed to execute the action.

---

## Human + AI memory

Kristal is designed so useful AI work does not disappear after one answer.

```text
research / extraction / reasoning
        ↓
traceable assertions
        ↓
Kristal State
        ↓
human correction / validation / new evidence
        ↓
richer Kristal State
        ↓
next human or AI starts from accumulated work
```

This makes the corpus a cumulative institutional memory rather than a sequence of disposable conversations.

---

## Main v6 concepts

- [Kristal-State](Kristal-State.md) — canonical structured artifact
- [Valuations-and-Value-Semantics](Valuations-and-Value-Semantics.md) — typed measures and state semantics
- [Coordinates-and-Applicability](Coordinates-and-Applicability.md) — geometry vs applicability envelope
- [Record-Roles](Record-Roles.md) — external constraints, observations, rules, derivations, decisions and actions
- [Actionability-and-Human-Boundaries](Actionability-and-Human-Boundaries.md) — automate deterministic work without bypassing authority
- [Identity-and-Determinism](Identity-and-Determinism.md) — content identity, hashing and reproducibility
- [Trust-Authority-and-Signatures](Trust-Authority-and-Signatures.md) — integrity vs recognition
- [Query](Query.md) — read/query projected material without creating parallel truth
- [Ecosystem-Integration](Ecosystem-Integration.md) — IK, Da’at, Orgo and communication boundaries

---

## Legacy v5 surfaces

Exchange and Runtime Pack documentation is retained for migration and compatibility context. It is no longer the conceptual center of Kristal v6.

- [Artifact-Exchange](Artifact-Exchange.md) — historical/compatibility surface
- [Artifact-Runtime-Pack](Artifact-Runtime-Pack.md) — historical/derived runtime surface

Use [Migration-v5-to-v6](Migration-v5-to-v6.md) when translating old field names or old consumers.
