# Kristal v9 Core Specification

Version `9.0.0-draft.1`.

Kristal v9 defines a polymorphic semantic-state architecture. It standardizes stable logical identity, immutable state composition, declared derivation, representation-independent commitments, materialization descriptors, and publication lifecycle without forcing every knowledge domain into one data shape.

## Normative architecture

A v9 system distinguishes:

```text
KNOWLEDGE != BUILD != MATERIALIZATION != READ MODEL
```

A logical artifact is interpreted by its named `logical_contract`. A state snapshot is an immutable composition of owned logical members and pinned external references. Physical materializations MAY be inline, segmented, factorized, encrypted, columnar, graph-native, or otherwise domain-appropriate.

## Required invariants

Implementations claiming v9 conformance MUST preserve the invariants in [Core-Invariants.md](../Core-Invariants.md), MUST obey the compatibility contract, and MUST validate the machine surfaces listed by `contracts/contract-set.json`.

## Core contracts

- `kristal_logical_artifact`
- `kristal_state_snapshot`
- `kristal_derivation`
- `kristal_materialization_manifest`
- `kristal_exchange`
- `kristal_activation`
- `kristal_v9_capabilities`

The JSON Schemas under `schemas/v9/` are normative machine contracts.
