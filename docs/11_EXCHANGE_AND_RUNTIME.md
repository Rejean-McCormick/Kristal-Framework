# Exchange and runtime

## 1. Exchange

Kristal Exchange is the portable distribution surface.

A v9 exchange can carry:

- an immutable State Snapshot;
- artifact descriptors;
- materialization manifests;
- required physical blobs;
- optional derivation records;
- optional signatures and validation evidence.

Exchange is a package of representations. It is not itself the logical state.

```text
EXCHANGE PACKAGE != LOGICAL STATE
```

## 2. Multiple exchanges for one state

The same logical state may be distributed as:

```text
one small archive
many content-addressed blobs
compressed JSONL segments
native domain files
```

Those exchanges may have different byte hashes while representing the same state commitment.

## 3. Repack invariance

A repack may:

- merge or split segments;
- change compression;
- change physical ordering;
- move blobs between stores;
- rebuild dictionaries;
- remove/rebuild indexes.

If logical content is unchanged, the logical commitments must remain unchanged.

## 4. Runtime Pack

A Runtime Pack is a derived materialization optimized for access.

It may contain:

```text
SQLite
Arrow
Parquet
search indexes
vector indexes
bitmap indexes
graph indexes
precomputed adjacency maps
caches
```

None of these technologies are required by the Standard.

## 5. Source binding

Every Runtime Pack must identify the logical state or artifact commitments from which it was built.

A runtime consumer must be able to detect that an index built for state `S42` is stale when the active state becomes `S43`.

## 6. Rebuildability

Where a runtime profile promises determinism, deleting and rebuilding the runtime pack from declared inputs should produce the declared equivalent output.

The canonical knowledge must survive loss of the runtime pack.

```text
DELETE RUNTIME
    +
REBUILD
    =
SAME LOGICAL STATE
```

## 7. Read-side duplication

Domain repositories sometimes store both canonical collections and convenience maps such as:

```text
components[]
components_by_id{}
```

V9 treats the second structure as a read model when it can be deterministically reconstructed from the first.

This prevents query convenience from doubling canonical state.

## 8. Runtime mutation boundary

Applications may maintain mutable operational databases. Such systems remain authoritative for their own mutable records.

A Runtime Pack must not silently become the authoritative writable application state merely because it is efficient.

New observations or decisions should flow through the owning application's contract and produce traceable new logical state when appropriate.
