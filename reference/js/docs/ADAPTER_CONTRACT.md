# Adapter contract

The JavaScript reference package is a non-normative compatibility and execution adapter for the Kristal monorepo.

## Read boundary

It accepts canonical artifacts without rewriting them:

- `kristal_state/6.0` portable state;
- v7 KQ/KP/KA/KS registries and Mesh artifacts;
- v8 language/query/read-model artifacts;
- v9 Logical Artifacts, State Snapshots, Derivations, Materialization Manifests, Exchange manifests and Activation pointers.

A v6 identity is not silently promoted to KQ. A physical segment ordinal is never promoted to semantic identity.

## Derived boundary

The following remain rebuildable/read-side products and never canonical authority:

- identity, graph, search and segment indexes;
- exported v8 query indexes;
- KQP query results and AI contexts;
- v9 Runtime Packs and cache structures;
- physical materialization choices.

## Lifecycle boundary

The reference implementation demonstrates local immutable publication and atomic pointer activation. It does not define distributed consensus. `BUILD != PUBLISH != ACTIVATE` remains explicit.

## Compatibility

V9 is additive. Existing v6/v7/v8 artifacts remain readable under their frozen contracts.
