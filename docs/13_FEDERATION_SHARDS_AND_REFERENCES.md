# Federation, shards and references

## 1. Federation is logical composition, not file concatenation

V9 supports states that compose independently governed Kristals without copying all child content into a parent artifact.

A federation should preserve:

- semantic identity;
- independent lifecycle;
- authority boundaries;
- pinned version/commitment;
- partial availability disclosure.

## 2. Shard

A **shard** is a semantic or governance boundary that can have an independent lifecycle.

A shard may correspond to:

```text
domain
jurisdiction
organization
curriculum course
specialist knowledge area
operational locality
```

The existing v8 rule remains important: semantic identity remains stable across operational sharding.

## 3. Segment

A segment is physical materialization.

```text
SHARD != SEGMENT
```

Examples:

- one Pokémon shard may use hundreds of physical segments;
- one UCKK course Kristal may be one small file but remain a distinct semantic shard/state;
- one HospitalOps deployment may keep separate authority shards even if stored in the same physical database service.

## 4. Pinned reference

A state may reference another state or artifact using an immutable identity/commitment pair.

Conceptually:

```json
{
  "state_ref": "urn:kristal:uckk:voie:IA",
  "logical_commitment": "sha256:..."
}
```

The parent may also carry an expected authority or contract constraint.

## 5. Mutable discovery versus immutable membership

A build can discover a child through a mutable channel such as `latest`, but a published parent snapshot must pin the resolved child revision.

This rule makes federation reproducible.

## 6. No-overlap composition

A strong federation pattern is that parents own topology and scope while children own their semantic payload.

UCKK illustrates this model:

```text
University
  → Voie
      → Course
```

The university artifact should not copy the course canon merely to make navigation convenient.

Derived catalogs or glossary indexes may provide cross-hierarchy navigation without becoming a second canon.

## 7. Authority

A parent that references a child does not become the child's authority.

A distribution service that hosts a child does not become its owner.

```text
HOSTING != OWNERSHIP
REFERENCE != AUTHORITY
```

## 8. Federated update

If child state `C1` becomes `C2`, the parent state does not silently change.

A new parent snapshot must explicitly pin `C2` if the federation wants to adopt it.

This gives deterministic historical composition.

## 9. Missing child

A runtime may have the parent but not the referenced child locally.

That is an availability condition, not evidence that the child content does not exist.

The query layer must be able to report missing coverage explicitly.
