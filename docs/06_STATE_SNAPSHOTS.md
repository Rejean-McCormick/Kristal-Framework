# State snapshots

## 1. Definition

A **State Snapshot** is an immutable logical composition.

It binds a set of owned logical artifacts and pinned external references into one versioned state without requiring those members to share a physical encoding or internal data model.

## 2. Snapshot properties

A state snapshot should carry enough information to determine:

- state identity or namespace;
- exact logical commitment of the state;
- member logical identities and commitments;
- pinned external references;
- parent lineage where applicable;
- scope/applicability relevant to state composition;
- contract versions required to interpret the composition.

It should not depend on:

- segment boundaries;
- compression;
- physical storage URIs;
- local caches;
- query indexes;
- activation pointer state.

## 3. Example

```json
{
  "contract": "kristal.state/9.0",
  "state_ref": "urn:kristal:state:pokemon",
  "logical_commitment": {
    "profile": "kristal.state-commitment/1",
    "digest": "sha256:..."
  },
  "members": [
    {
      "artifact_id": "urn:kristal:pokemon:species",
      "logical_contract": "pokemon.species-registry/1.0",
      "logical_commitment": "sha256:..."
    },
    {
      "artifact_id": "urn:kristal:pokemon:learnsets",
      "logical_contract": "pokemon.learnset-relation/1.0",
      "logical_commitment": "sha256:..."
    }
  ],
  "references": [],
  "parents": []
}
```

This remains explanatory prose; the draft machine contract is now `schemas/v9/kristal-state-snapshot.schema.json`.

## 4. Immutable references

A state snapshot must not depend logically on mutable selectors such as:

```text
latest
HEAD
main
current
```

A build may resolve such selectors, but publication must pin the selected revision or logical commitment.

```text
MUTABLE DISCOVERY
    ↓ resolve
IMMUTABLE SNAPSHOT REFERENCE
```

## 5. Parent lineage

`parents` describes state history or derivation ancestry. It is not necessarily part of the logical knowledge commitment unless the applicable profile explicitly says that lineage is logically meaningful.

This matters because two independent builders can sometimes produce identical logical state through different operational histories.

## 6. State commitment

The state commitment should be calculated from a canonical logical member description, not from physical manifests.

Conceptually:

```text
state scope
+ ordered canonical member identities/commitments
+ pinned reference identities/commitments
+ logical state policies
        ↓
state commitment profile
        ↓
logical state digest
```

## 7. Composition and authority

A state may compose members governed by different authorities.

Composition does not imply that the parent now owns the children or that all members share one trust policy.

```text
STATE COMPOSITION != AUTHORITY MERGE
```

## 8. Deletion and historical membership

If artifact `A` is a member of `S1` but not `S2`, v9 does not imply that `A` has been erased from history.

A domain-level retraction, supersession or revocation is distinct from simple state membership change and must use the relevant semantic/epistemic contract.
