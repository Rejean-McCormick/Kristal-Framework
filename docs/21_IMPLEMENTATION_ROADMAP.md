# Implementation roadmap

## 1. Guiding principle

V9 should prove representation independence before optimizing every storage path.

The implementation roadmap is intentionally staged to prevent the Standard from becoming a collection of database features.

## 2. Phase A — normative design

Freeze the first versions of:

```text
kristal.state/9.0
kristal.artifact-descriptor/9.0
kristal.derivation/9.0
kristal.materialization/9.0
```

and the baseline logical commitment profile.

Deliverables:

- normative prose in `spec/v9/`;
- JSON Schemas in `schemas/v9/`;
- compatibility lock updates;
- TCK vectors;
- KristalDiag support.

## 3. Phase B — minimal reference implementation

Implement only:

- state snapshot parse/validate;
- artifact descriptor parse/validate;
- logical commitment generation;
- derivation records;
- inline JSON materialization;
- segmented JSONL materialization;
- local filesystem content store;
- v6 portable projection compatibility;
- immutable local publish;
- atomic local activation pointer.

Do not begin with a distributed store.

## 4. Phase C — reference workloads

Run at least:

### Small workload

Pi Theory or an equivalent small artifact should remain simple and readable.

### Large relation workload

Pokémon should demonstrate localized materialization and partial reads without requiring expanded v6 internally.

### Native graph/DAG workload

Recipes or VehicleDiag should demonstrate that no forced relational/assertion flattening is required.

### Federation workload

UCKK should demonstrate pinned child references.

### Multi-authority workload

HospitalOps or MathKristal should demonstrate preserved authority boundaries.

## 5. Phase D — operational hardening

Add:

- crash/failure injection tests;
- concurrent publisher tests;
- retention/GC tooling;
- stale runtime detection;
- remote blob resolver interface;
- coverage metadata;
- release qualification integration.

## 6. Phase E — performance profiles

After the architecture is stable, evaluate:

- Zstandard segmented profile;
- columnar profile;
- Arrow runtime profile;
- SQLite runtime profile;
- optional Parquet interoperability profile;
- multi-segment indexes;
- Bloom/range pruning metadata.

These profiles should be benchmark-driven.

## 7. Phase F — advanced trust/distribution

Possible later work:

- remote content-addressed federation;
- logical membership proofs;
- protected/keyed commitment profiles;
- signed activation records;
- transparency/log anchoring profiles.

These features should not block `9.0.0` unless a concrete security requirement proves they are foundational.

## 8. KristalDiag roadmap

Suggested new qualification areas:

```text
logical commitment vectors
materialization equivalence
repack invariance
identity continuity
compatibility locks
derivation completeness
snapshot immutability
atomic activation
coverage correctness
```

## 9. Performance benchmarks

Track more than compressed size.

Recommended metrics:

### Space Amplification

```text
physical bytes / useful logical bytes
```

### Read Amplification

```text
bytes read / logical bytes required
```

### Materialization Amplification

```text
bytes rewritten / logical bytes changed
```

### Verification Amplification

```text
bytes verified / logical scope verified
```

### Rebuild Amplification

```text
artifacts rebuilt / artifacts logically affected
```

The Pokémon case demonstrates why a tiny compressed archive can still have poor read/rebuild characteristics when its logical representation is monolithic.

## 10. Release gate

V9 should not reach final status until:

- inherited v6/v7/v8 conformance remains green;
- logical commitment vectors are frozen;
- at least two materially different materializations pass equivalence tests;
- at least five distinct workload shapes pass polymorphism tests;
- crash-consistent publication is demonstrated;
- no reference workload requires conversion into a foreign native shape.
