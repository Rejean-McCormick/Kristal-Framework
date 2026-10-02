# Kristal Standard v6

> **Active baseline:** `6.0.0`

Kristal is a deterministic, portable **structured-memory and actionability standard** for preserving human and machine work as explicit, contextual, traceable assertions that can be enriched over time.

The v6 canonical artifact is **`kristal_state`**.

```text
referents + atomic assertions
        │
        ├── valuations[]          typed measures / states
        ├── coordinates           domain geometry
        ├── applicability         where / when / for whom
        ├── record_role           what kind of record this is
        ├── actionability         automation / human boundary
        ├── provenance/evidence   why and where it came from
        ├── validation            policy evaluation
        ├── recognition           scoped authority
        ├── conflict/succession   disagreement and replacement
        └── lineage               derivation / specialization
        │
        ▼
reader policies + derived projections + authorized actions
```

## Why v6

Kristal no longer assumes that a field called “certainty” has one universal meaning. Domains can represent proof closure, diagnostic support, constitutive necessity, administrative applicability, taxonomic acceptance, maintenance necessity, compatibility or other explicit dimensions through typed valuations.

Supported value semantics include boolean, categorical, set, ordinal, scalar, interval, probability, distribution, vector, partial order, state and temporal values. `unknown`, `not_applicable`, `indeterminate` and `not_measured` are value states, not disguised numbers.

v6 also makes the human/automation boundary explicit. `actionability.mode = automatic` means that the represented policy does not require human judgment before an action path can be attempted; it **does not grant permission to mutate another system**.

## Stable separations

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

These separations let Kristal preserve laws and official procedures, neutral observations, organization-specific rules, machine-derived state, human decisions and actions in one portable memory without confusing their roles.

## Human + AI memory

Kristal is designed so useful AI work does not disappear after one answer:

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

Deterministic work can be automated while ambiguity, interpretation, authority, exceptions and high-value judgment remain with humans.

## Start here

1. [`docs/Technical-Reference/kristal-docs-v6/What-is-Kristal.md`](docs/Technical-Reference/kristal-docs-v6/What-is-Kristal.md)
2. [`docs/Technical-Reference/kristal-docs-v6/Concepts-and-Mental-Model.md`](docs/Technical-Reference/kristal-docs-v6/Concepts-and-Mental-Model.md)
3. [`docs/Technical-Reference/kristal-docs-v6/01-core-spec/kristal-v6-core-spec.md`](docs/Technical-Reference/kristal-docs-v6/01-core-spec/kristal-v6-core-spec.md)
4. [`docs/Technical-Reference/kristal-docs-v6/Kristal-State.md`](docs/Technical-Reference/kristal-docs-v6/Kristal-State.md)
5. [`docs/Technical-Reference/kristal-docs-v6/Valuations-and-Value-Semantics.md`](docs/Technical-Reference/kristal-docs-v6/Valuations-and-Value-Semantics.md)
6. [`docs/Technical-Reference/kristal-docs-v6/Record-Roles.md`](docs/Technical-Reference/kristal-docs-v6/Record-Roles.md)
7. [`docs/Technical-Reference/kristal-docs-v6/Actionability-and-Human-Boundaries.md`](docs/Technical-Reference/kristal-docs-v6/Actionability-and-Human-Boundaries.md)
8. [`docs/Technical-Reference/kristal-docs-v6/Migration-v5-to-v6.md`](docs/Technical-Reference/kristal-docs-v6/Migration-v5-to-v6.md)

## Normative v6 surfaces

- Core spec: `docs/Technical-Reference/kristal-docs-v6/01-core-spec/kristal-v6-core-spec.md`
- Kristal State schema: `docs/Technical-Reference/kristal-docs-v6/02-schemas/kristal-state.schema.json`
- v6 test vector: `docs/Technical-Reference/kristal-docs-v6/09-test-vectors/kristal-state/`
- Release metadata: `VERSION`, `kristal-release.json`, `contract-set.manifest.json`
- Knowledge-model bundle: `knowledge-model-contract.v2.json`

The active canonicalization profile is `kristal.v6:jcs-rfc8785`.

## Legacy v5 compatibility

The full v5 specification and schemas remain under:

`docs/Technical-Reference/kristal-docs-v5/`

Structured Epistemic State, Exchange, Runtime Pack, shard and federation surfaces remain valid for legacy consumers and compatibility adapters. They are no longer the conceptual center of new v6 domain models.

The frozen v5 knowledge-model bundle remains at `knowledge-model-contract.v1.json`.

## Conformance

Run:

```bash
python tools/validate_all.py
```

The v6 gate validates release metadata, the v6 schema and fixture, canonical identity semantics and retained v5 compatibility surfaces. External implementation conformance remains a separate claim until an implementation/reference adapter is tested.

## Authority boundary

Kristal represents knowledge, state, policy and actionability. It does not manufacture legal authority, organizational authority or execution permission by storing a record.
