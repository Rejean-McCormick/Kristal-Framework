# Conformance and testing

## 1. Principle

The specification and TCK define behavior. Reference implementations demonstrate behavior. Independent qualification remains separate from the Standard.

V9 should extend the existing KristalDiag model rather than create a competing validator ecosystem.

## 2. Proposed conformance capabilities

### V9 State Reader

Understands:

- State Snapshot;
- Artifact Descriptor;
- inherited contracts used by the state;
- logical commitments;
- pinned references.

### V9 Builder

Adds:

- Derivation records;
- exact-input discipline;
- commitment generation;
- reproducibility claims.

### V9 Materializer

Adds:

- materialization profiles;
- physical descriptors;
- reconstruction;
- repack/resegmentation invariance tests.

### V9 Publisher

Adds:

- immutable snapshot publication;
- activation pointer semantics;
- rollback;
- crash-consistent sequencing.

### V9 Full

Supports the complete required v9 baseline plus inherited v6/v7/v8 compatibility surfaces.

Final profile names may differ, but qualification should remain capability-based.

## 3. Logical commitment vectors

The TCK must include cases for:

```text
object-key ordering
set-like array ordering
ordered array preservation
null versus absent
implicit versus explicit defaults
presentation field exclusion
logical versus physical digest
domain separation
```

## 4. Identity vectors

Tests should cover:

- stable identity with new revision;
- new identity for a different logical object;
- non-reuse;
- split migration;
- merge migration;
- continuity through presentation changes.

## 5. Materialization vectors

The same logical artifact should be provided in at least two physical materializations.

The test must prove:

```text
reconstruct(A) ==logical reconstruct(B)
```

and:

```text
logical_commitment(A) == logical_commitment(B)
```

while physical blob digests differ.

## 6. Failure vectors

Negative tests should include:

- corrupt segment digest;
- missing required segment;
- duplicate or conflicting physical member;
- incorrect dictionary reference;
- materialization reconstructing a different logical commitment;
- mutable external reference in a published snapshot;
- incompatible inherited contract digest;
- stale runtime pack;
- attempted identity-profile reuse with changed rules.

## 7. Lifecycle tests

Publisher tests should simulate failures after each stage:

```text
blob write
manifest write
state write
publication
activation
```

The old active snapshot must remain usable until successful activation.

## 8. Polymorphism tests

V9 conformance must not be demonstrated only with one relational fixture.

Reference workloads should include:

- large homogeneous relation;
- procedural DAG;
- conditional graph;
- small structured document;
- federated hierarchy;
- formal AST/graph combination;
- multi-authority sensitive composition.

## 9. KristalDiag direction

Candidate v9 diagnostic modules include:

```text
Logical Commitment
Identity Continuity
Contract Compatibility
Derivation Integrity
Materialization Equivalence
Repack Invariance
Coverage Integrity
Publication Atomicity
Rollback Integrity
Legacy Compatibility
```

The exact KristalDiag level mapping should be decided after the normative v9 contracts stabilize.
