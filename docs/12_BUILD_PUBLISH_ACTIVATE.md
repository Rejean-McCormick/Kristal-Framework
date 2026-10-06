# Build, publish and activate

## 1. Three separate operations

V9 makes the lifecycle boundary explicit:

```text
BUILD != PUBLISH != ACTIVATE
```

### Build

Produces candidate logical artifacts and physical materializations.

### Publish

Creates an immutable State Snapshot and makes it available as a released/published object according to deployment policy.

### Activate

Moves a mutable operational pointer or channel to a published snapshot.

## 2. Build

A build may produce many temporary or candidate artifacts.

It must not modify the active state merely because computation succeeded.

Typical build flow:

```text
source snapshot
      ↓
normalize
      ↓
validate candidate logical artifact
      ↓
calculate logical commitment
      ↓
materialize
      ↓
verify blobs
```

## 3. Publish

Publication should occur only after required validation gates succeed.

A published snapshot is immutable.

```text
S42 remains S42 forever
```

A new logical state is `S43`, not a mutation of `S42`.

## 4. Activation

An activation pointer can be represented conceptually as:

```text
production → S42
```

then atomically changed to:

```text
production → S43
```

Readers already pinned to `S42` may continue using it according to retention policy.

## 5. Safe publication ordering

A recommended order is:

```text
1. write blobs
2. verify blob digests
3. write materialization manifests
4. reconstruct/verify logical artifacts
5. construct immutable State Snapshot
6. validate snapshot
7. publish snapshot
8. atomically advance activation pointer
```

The active pointer is moved last.

## 6. Crash consistency

If a process crashes before activation:

- the old active snapshot remains valid;
- newly written but unreferenced blobs are not logically active;
- orphan cleanup can occur later.

A partially written new state must never replace a valid active state.

## 7. Optimistic concurrency

A publisher may build from base snapshot `S42`.

Before activation it checks:

```text
current active == S42 ?
```

If yes, it may advance to `S43` atomically.

If not, the implementation must apply an explicit conflict/rebase/rebuild policy.

## 8. Semantic conflict

A head-pointer conflict is not automatically a semantic conflict.

Two independent changes may be composable.

Two incompatible revisions of the same domain object may require domain or epistemic resolution.

```text
STORAGE CONFLICT != SEMANTIC CONFLICT
```

V9 must not default to last-writer-wins for semantic conflicts.

## 9. Rollback

Rollback selects a previously published immutable snapshot.

```text
production → S43
```

may become:

```text
production → S42
```

according to policy.

Rollback does not rewrite history or fabricate a new state that pretends S43 never existed.

## 10. Orthogonal statuses

Implementations should preserve distinctions such as:

```text
built
validated
recognized
published
active
revoked
```

A successful build is not automatically validated, recognized or activated knowledge.
