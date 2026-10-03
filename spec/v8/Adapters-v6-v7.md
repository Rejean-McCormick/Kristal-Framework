# v6/v7 adapters

## Purpose

Adapters are anti-corruption boundaries. They let a v8 engine operate over earlier Kristal versions without leaking v8 assumptions into the older canonical artifacts.

## v6 adapter

A v6 adapter:

- reads `kristal_state/6.0` unchanged;
- preserves referent namespaces, assertion status, valuation semantics, coordinates, applicability and source/evidence links;
- exposes stable v6 referents through `identity_space: kristal_v6` unless an already-declared v7 mapping is available;
- never invents `KQ` equivalence merely to simplify querying.

## v7 adapter

A v7 adapter directly exposes KQ/KP/KA/KS, Mesh, KOS, axes, source and projection metadata. Existing labels may be offered as display fallback material but do not become v8 lexical authority.

## External KOS adapter

External vocabularies remain external identities/mappings. Adapter code translates transport/schema differences at the edge and must not redefine Kristall identity.

## Adapter determinism

Given the same source snapshot and adapter profile, normalized read output SHOULD be reproducible. Adapter version/profile is part of derived lineage.
