# Adapter contract

The JavaScript reference package is a non-normative compatibility and execution adapter for the Kristal monorepo.

## Read boundary

It accepts canonical artifacts without rewriting them:

- `kristal_state/6.0` portable state;
- v7 KQ/KP/KA/KS registries and Mesh artifacts;
- v8 companion artifacts such as lexical Kristals, lexicon stacks, KQP requests/results, query indexes and AI context bundles.

A v6 identity is not silently promoted to KQ. External/source-local IDs remain external unless a declared mapping says otherwise.

## Derived boundary

The following are rebuildable/read-side products and never canonical authority:

- in-memory identity and graph indexes;
- exported `kristall_query_index` payloads;
- KQP query results;
- semantic fingerprints;
- AI context bundles;
- lexical projections.

## AI boundary

The model/client may propose a typed KQP request. The deterministic runtime validates and executes supported operators. Free-form intent can influence ranking but cannot override typed scope, traversal, filters, budgets or authority boundaries.

## Compatibility

v8 functionality is additive. Existing v6/v5 functions remain in place, and v7 source artifacts are consumed without schema mutation.
