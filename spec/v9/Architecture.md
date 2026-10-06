# Architecture

```text
State Snapshot
  ├─ owned Logical Artifact(s)
  └─ pinned external reference(s)
          │
          ▼
   Derivation Graph
          │
          ▼
   Materialization Layer
      ┌───┴───┐
   Exchange  Runtime
```

The state layer identifies logical content. Derivations explain how artifacts were produced. Materializations explain how logical content is encoded physically. Exchange packages are portable representations. Runtime packs are rebuildable read/compute models.

The logical topology MAY be cyclic. Physical packaging MAY use a Merkle DAG; the two topologies are independent.
