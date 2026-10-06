# Architecture

## 1. Layer model

Kristal v9 introduces a four-layer architecture around the existing semantic and epistemic contracts.

```text
                 ┌────────────────────────┐
                 │   LOGICAL STATE        │
                 │                        │
                 │ immutable snapshot     │
                 │ logical artifacts      │
                 │ pinned references      │
                 │ authority boundaries   │
                 └───────────┬────────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │   DERIVATION GRAPH     │
                 │                        │
                 │ declared inputs        │
                 │ transforms             │
                 │ parameters/toolchain   │
                 │ build lineage          │
                 └───────────┬────────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │ MATERIALIZATION LAYER  │
                 │                        │
                 │ profiles               │
                 │ manifests              │
                 │ segments/dictionaries  │
                 │ physical descriptors   │
                 └───────────┬────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
              ┌──────────┐      ┌──────────┐
              │ EXCHANGE │      │ RUNTIME  │
              │ portable │      │ derived  │
              │ verified │      │ optimized│
              └──────────┘      └──────────┘
```

The logical state is authoritative for logical membership. Derivation explains production. Materialization explains physical representation. Exchange and Runtime are consumption surfaces.

## 2. Logical state

A state snapshot is an immutable composition of logical artifacts and pinned external references. The state is not defined by a single required file format.

A logical artifact declares its own logical contract. The core can therefore compose objects with different internal shapes without pretending that they share the same native model.

## 3. Derivation graph

The derivation graph makes build causality explicit:

```text
source snapshot
      │
      │ normalize@2
      ▼
normalized domain artifact
      │
      │ project@9
      ▼
logical artifact
      │
      │ materialize@1
      ▼
exchange representation
      │
      │ index@3
      ▼
runtime read model
```

The graph is not itself an epistemic authority. It describes reproducibility and lineage.

## 4. Materialization layer

Materialization translates logical content into a physical representation. The same logical artifact may have several materializations.

Examples:

```text
inline-json
native-blob
segmented-jsonl
columnar
compressed archive
encrypted envelope
runtime database
```

Only the profiles that are actually used need to be implemented by a deployment.

## 5. Exchange

Exchange is the portable, verifiable transport surface. It packages enough descriptors, manifests and blobs to reconstruct or inspect a state or selected artifacts.

```text
EXCHANGE PACKAGE != LOGICAL STATE
```

Two exchange packages may represent the same logical state while using different segmentation, compression or media types.

## 6. Runtime

Runtime material is a derived optimization surface. It may include indexes, local databases, caches, vector indexes, graph indexes or other optimized views.

Runtime structures must carry enough lineage to identify the logical state they represent.

```text
RUNTIME PACK != CANONICAL STATE
```

## 7. Anti-corruption boundaries

Adapters isolate domain-native contracts, inherited v6/v7/v8 formats and runtime-specific representations from each other.

An implementation must not reinterpret a domain field merely because a particular backend prefers a different model.

Examples:

- an ordered procedure path cannot become a set because a storage engine sorts rows;
- a semantic ID cannot become a local integer dictionary key;
- a runtime index cannot become the authoritative relationship store;
- a representation graph cannot become a proof graph merely because both use edges.

## 8. Architecture in one rule

```text
WHAT THE KNOWLEDGE MEANS
MUST NOT DEPEND ON
HOW THE BYTES ARE PACKED
```
