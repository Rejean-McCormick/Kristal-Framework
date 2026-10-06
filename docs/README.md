# Kristal v9 documentation

**Status:** informative architecture and authoring documentation for Kristal `9.0.0-draft.1`; normative draft surfaces live under `spec/v9`, `schemas/v9`, and `tck/v9`.

This directory describes the v9 **Semantic State Architecture**. It is intentionally separate from `spec/`: the material here explains the design, implementation model, migration strategy and reference workloads. Once a v9 surface is stabilized, its normative requirements should be promoted into `spec/v9/`, schemas into `schemas/v9/`, and golden vectors into `tck/v9/`.

Kristal v9 is additive. It does not replace the v6 portable epistemic state, the v7 semantic identity layer, or the v8 language/query layer. It adds a state architecture that separates logical knowledge from the way that knowledge is built, materialized, distributed and consumed.

The foundational distinction is:

```text
KNOWLEDGE
    !=
BUILD
    !=
MATERIALIZATION
    !=
READ MODEL
```

The second foundational rule is:

```text
OPTIMIZATION MUST NOT SILENTLY CHANGE SEMANTICS
```

## Reading order

1. [Status](00_STATUS.md)
2. [Vision and scope](01_VISION_AND_SCOPE.md)
3. [Architecture](02_ARCHITECTURE.md)
4. [Core invariants](03_CORE_INVARIANTS.md)
5. [Concepts and mental model](04_CONCEPTS_AND_MENTAL_MODEL.md)
6. [Logical artifacts](05_LOGICAL_ARTIFACTS.md)
7. [State snapshots](06_STATE_SNAPSHOTS.md)
8. [Identity and commitments](07_IDENTITY_AND_COMMITMENTS.md)
9. [Authority, provenance and trust](08_AUTHORITY_PROVENANCE_AND_TRUST.md)
10. [Derivations and reproducibility](09_DERIVATIONS_AND_REPRODUCIBILITY.md)
11. [Materialization](10_MATERIALIZATION.md)
12. [Exchange and runtime](11_EXCHANGE_AND_RUNTIME.md)
13. [Build, publish and activate](12_BUILD_PUBLISH_ACTIVATE.md)
14. [Federation, shards and references](13_FEDERATION_SHARDS_AND_REFERENCES.md)
15. [Coverage and partial availability](14_COVERAGE_AND_PARTIAL_AVAILABILITY.md)
16. [Contract evolution and compatibility](15_CONTRACT_EVOLUTION_AND_COMPATIBILITY.md)
17. [Security and confidentiality](16_SECURITY_AND_CONFIDENTIALITY.md)
18. [Conformance and testing](17_CONFORMANCE_AND_TESTING.md)
19. [Reference profiles](18_REFERENCE_PROFILES.md)
20. [Polymorphic workloads](19_POLYMORPHIC_WORKLOADS.md)
21. [Migration from v8](20_MIGRATION_V8_TO_V9.md)
22. [Implementation roadmap](21_IMPLEMENTATION_ROADMAP.md)
23. [Glossary](22_GLOSSARY.md)
24. [Design rationale](23_DESIGN_RATIONALE.md)
25. [Open questions](24_OPEN_QUESTIONS.md)
26. [Repository guide](25_REPOSITORY_GUIDE.md)
27. [Authoring and implementation guide](26_AUTHORING_GUIDE.md)
28. [FAQ](27_FAQ.md)

## Relationship to the existing Standard

The existing repository already separates normative specification, schemas, conformance vectors, examples, reference implementations and release tooling. V9 keeps that discipline.

The architectural lineage is:

```text
v5  deterministic builds, exchange/runtime separation, reproducibility
 ↓
v6  portable epistemic state and independently addressable assertions
 ↓
v7  stable semantic identity, axes, factorization and projections
 ↓
v8  language/query separation, read models and semantic fingerprints
 ↓
v9  representation-independent logical state and materialization lifecycle
```

V9 should therefore be understood as consolidation and extension, not as a restart.

## Reference workloads

The v9 design is tested against intentionally different knowledge shapes:

- Pokémon: very large homogeneous relation sets;
- Kristal-Recipes: domain-native procedural DAGs;
- Kristal-VehiculeDiag: conditional multiplex diagnostic graphs;
- Kristal-Pi-Theory: a small layered epistemic corpus;
- Kristal-HospitalOps: security-separated operational and knowledge planes;
- UCKK: hierarchical federation through pinned child Kristals;
- MathKristal: formal objects, theory/proof/representation graphs and derived action graphs;
- Kristal-kOA-Ecosystem: heterogeneous ecosystem/property graph and authority boundaries.

A v9 core feature should not be accepted merely because it optimizes one of these workloads. It must preserve the native semantics of the others or remain an optional profile/tooling feature.
