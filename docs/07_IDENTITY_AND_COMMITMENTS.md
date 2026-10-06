# Identity and commitments

## 1. Purpose

V9 separates stable identity from revision content and from physical bytes.

This extends two existing Kristal distinctions:

- v7 semantic IDs are stable logical identifiers rather than content hashes;
- v8 semantic fingerprints are distinct from byte hashes.

V9 generalizes those ideas to logical artifacts and immutable state snapshots.

## 2. Semantic identity

Semantic identity answers:

> Which logical object is this?

Where an inherited Kristall semantic ID exists, it remains authoritative within its namespace.

Examples:

```text
KQ…   entity/item
KP…   property/relation
KA…   assertion
KS…   source
```

Domain-defined artifacts may also use stable URIs or another contract-defined namespace.

A semantic ID must not encode mutable descriptions, labels, classifications or physical location unless the identity contract explicitly makes them identity-bearing.

## 3. Logical commitment

A logical commitment answers:

> What is the exact logical content of this revision under a named profile?

Two physical representations may have the same logical commitment.

Example:

```text
learnsets.jsonl.zst  blob A ─┐
                              ├─ logical commitment L
learnsets.parquet    blob B ──┘
```

This is valid only if both representations reconstruct the same logical artifact under the same logical contract and commitment profile.

## 4. Blob digest

A blob digest binds exact bytes.

Changing any of the following will normally change the blob digest:

- compression;
- encryption envelope;
- physical ordering that is not byte-canonical;
- segmentation;
- media type serialization;
- metadata embedded in the blob.

Those changes do not necessarily affect the logical commitment.

## 5. Commitment profile

Every logical commitment must declare a profile.

A profile defines at least:

- logical contract and compatible versions;
- fields included in the logical projection;
- fields excluded as physical/derived metadata;
- collection semantics and canonical ordering;
- scalar normalization;
- domain separator;
- digest algorithm.

Processors must not invent local exclusions while claiming the same profile.

## 6. Baseline algorithm

A baseline JSON-oriented profile can follow:

```text
logical payload
      ↓
contract-specific normalization
      ↓
normalize set-like collections
      ↓
remove excluded physical/derived fields
      ↓
JCS canonicalization
      ↓
domain-separated SHA-256
```

Normalization and canonicalization are distinct operations.

JCS canonicalizes JSON syntax and object-key ordering. It does not know whether an array is semantically a set, sequence or multiset.

## 7. Ordered collections

The logical contract must define collection semantics where ordering affects equality.

Example:

```json
["A", "B"]
```

and:

```json
["B", "A"]
```

must have the same logical commitment only when that collection is explicitly set-like.

For a mathematical AST, recipe procedure path or curriculum order, sorting would change meaning and is forbidden.

## 8. Null, absent and defaults

V9 must not globally assume that:

```text
missing == null == default
```

A logical contract must determine whether:

- absence means unknown;
- absence means default;
- `null` is a value;
- an explicit default and implicit default are logically equivalent.

The commitment profile must preserve that distinction consistently.

## 9. Revision continuity

When an artifact's logical content changes but the artifact remains the same conceptual object:

```text
same semantic_id
new logical_commitment
```

Examples may include:

- improved evidence for the same assertion;
- a corrected description in a contract where descriptions are logical content;
- a new revision of a recipe variant that retains the variant identity by domain policy.

Whether continuity applies is domain-specific.

## 10. Identity profile

A domain may publish an identity profile that defines:

- how new IDs are minted;
- which properties establish continuity;
- non-reuse rules;
- how splits and merges are represented;
- how identity migrations are recorded.

An identity profile is not a hash profile.

```text
IDENTITY PROFILE != COMMITMENT PROFILE
```

## 11. Identity migration

Changing identity-bearing semantics is not an ordinary schema migration.

Example:

```text
profile v1:
subject + predicate + object
```

becoming:

```text
profile v2:
subject + predicate + object + version_group
```

may split one previous identity into several new identities.

Such a migration must be explicit and traceable.

## 12. Physical independence test

A v9 implementation should have a conformance test equivalent to:

```text
materialize A
calculate logical commitment L1
repack/recompress/resegment A
reconstruct logical artifact
calculate logical commitment L2
assert L1 == L2
```

Failure means the physical representation leaked into logical identity or reconstruction lost information.
