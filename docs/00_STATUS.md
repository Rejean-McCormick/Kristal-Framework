# v9 status

## Proposed baseline

- Proposed Standard version: `9.0.0-draft.1`
- Architecture name: **Semantic State Architecture**
- Compatibility baseline: Kristal v6 + Kristall v7 + Kristal v8
- Status of this directory: informative architecture/authoring documentation; normative v9 draft surfaces now live under `spec/v9`, `schemas/v9`, and `tck/v9`

## What is considered stable enough to document

The following decisions are treated as architectural anchors for v9:

1. V9 is additive above v6/v7/v8.
2. Domain-native knowledge shapes remain legal and first-class.
3. A logical artifact is independent of its physical representation.
4. A state snapshot is immutable.
5. Stable semantic identity, logical commitment and physical blob digest are distinct.
6. Materialization profiles are explicit and replaceable.
7. A shard is a semantic/lifecycle boundary; a segment is a physical storage boundary.
8. Query indexes and runtime packs are derived material.
9. Epistemic provenance and build provenance are different authorities.
10. Build, publish and activate are separate lifecycle operations.
11. Repack, recompression, resegmentation and index rebuild are not logical mutations.
12. Parent states may pin child states without copying their semantic content.
13. Composition does not merge authority or ownership.
14. Existing v6/v7/v8 contracts remain frozen compatibility surfaces.
15. Small Kristals must remain simple and inexpensive.

## What is not frozen yet

The draft now fixes baseline machine contracts for Logical Artifacts, State Snapshots, Derivations, Materialization Manifests, Exchange, Activation and Capabilities. Remaining pre-RC work is intentionally narrower:

- protected/private commitment profiles for sensitive artifacts;
- broader polymorphic workload vectors beyond the compact reference examples;
- external KristalDiag qualification profiles for v9;
- operational guidance for remote/distributed activation transports;
- optional advanced materialization profiles (for example columnar codecs).

## Compatibility posture

V9 must not make a valid v6, v7 or v8 artifact invalid merely because the artifact does not use v9 features.

A deployment may participate in v9 by wrapping or referencing inherited artifacts. For example, an unchanged `kristal_state/6.0` can be a logical artifact in a v9 state without rewriting its internal assertions.

```text
V9 ADOPTION != V6 REWRITE
```

## Implementation posture

The first reference implementation should prefer clarity and determinism over advanced storage optimization. The initial proof should demonstrate:

- stable logical commitment across two physical materializations;
- deterministic reconstruction;
- immutable snapshot publication;
- atomic local activation;
- unchanged v6 projection behavior;
- at least one large relational workload and one non-tabular workload.

Advanced codecs, remote object stores, Merkle membership proofs and automatic materialization planning should follow only after the core model is stable.
