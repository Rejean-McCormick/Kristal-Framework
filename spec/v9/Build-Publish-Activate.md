# Build, Publish and Activate

```text
BUILD != PUBLISH != ACTIVATE
```

These transitions are deliberately separate so compilation success cannot silently become deployment authority.

## BUILD

BUILD produces candidate logical artifacts and physical materializations from declared derivations. It does not alter the active state.

## PUBLISH

PUBLISH validates candidates and creates a new immutable `kristal_state_snapshot`. Publication MUST NOT modify an existing published snapshot in place.

Recommended local order:

```text
1. write candidate blobs
2. verify blob digests
3. write materialization manifests
4. verify logical reconstruction / commitments
5. write the immutable state snapshot
6. validate the snapshot
7. make the snapshot discoverable/published
```

Failure before ACTIVATE MUST leave the previous active pointer unchanged. Unreferenced candidate blobs may later be garbage-collected by implementation policy.

## ACTIVATE

ACTIVATE changes a mutable channel pointer such as `production` or `HEAD` to a published immutable state.

The baseline `kristal_activation` contract records:

- `channel_id`;
- `active_state`;
- optional `previous_state`;
- optional `expected_previous` for compare-and-swap behavior;
- monotonic/non-negative `sequence` within the deployment policy;
- optional timestamp and signatures.

When `expected_previous` is supplied, an implementation MUST reject activation if the current active logical commitment differs from the expected commitment.

The update of the activation pointer MUST be atomic for the transport/profile being claimed. V9.0 does not define distributed consensus.

## Concurrent publishers

A publisher SHOULD build from a known base state. If the active pointer advances before publication/activation, the implementation MUST re-evaluate assumptions rather than apply unconditional last-writer-wins behavior.

```text
STORAGE CONFLICT != SEMANTIC CONFLICT
```

Domain-level semantic conflict resolution remains outside generic storage arbitration.

## Rollback

Rollback selects a retained prior immutable snapshot. It does not recreate or rewrite that snapshot as a new fake history entry. Recognition/revocation policy may still prohibit activation of a technically available older state.
