# Governance

The Kristal standard separates semantic authority from implementation convenience.

Normative behavior is defined by the specification, canonical schemas, compatibility contracts and TCK. Reference implementations and helper tools are non-normative.

## v8 governance rules

- v6/v7 compatibility surfaces are protected by `contracts/v8-compatibility-lock.json`.
- New v8 capabilities must remain additive; they cannot redefine inherited semantic identity or portable-state fields.
- Lexical communities may steward language/domain lexicons without becoming semantic authority over the referenced concepts.
- Domain communities may steward federated semantic shards under shared global identity/provenance/query contracts.
- Query indexes, AI contexts, caches and renderers are read models and cannot promote themselves to canonical state.
- Changes to fingerprint profiles, KQP semantics or lexical-resolution behavior require versioned contracts and TCK coverage.
