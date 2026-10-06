# State Snapshots

A `kristal_state_snapshot` is an immutable logical composition. Logical mutation creates a new snapshot; snapshots are never edited in place.

## Owned members

`members[]` contains logical artifact references whose membership is owned by the snapshot. Each reference pins a `logical_commitment`; mutable selectors are not legal state membership.

## External references

`references[]` may point to an external logical artifact or external state. A reference pins exact logical content and MAY preserve `authority_ref` metadata, but composition does not transfer authority or ownership.

```text
REFERENCE != OWNERSHIP TRANSFER
STATE COMPOSITION != AUTHORITY MERGE
```

## Mutable selectors

Selectors such as `HEAD`, `main`, `current`, or `latest` MAY be used during discovery/build. They MUST be resolved to immutable logical commitments before a snapshot is published.

## Parents

`parents[]` records lineage/history. Parent lineage is intentionally excluded from the baseline state logical commitment: two independently produced snapshots containing the same logical membership may therefore share a logical commitment while retaining different publication histories.

## State identity

`state_ref` is semantic identity and is separate from the state content commitment. It is likewise excluded from the baseline state-content commitment.

## Commitment

The exact baseline projection and algorithm are normative in [Identity and Commitments](Identity-and-Commitments.md). Physical segment layout, compression, encryption envelope, indexes, timestamps and signatures do not contribute to that baseline commitment.
