# Authoring and implementation guide

## 1. For a new domain

Do not begin by choosing a database or segment codec.

Begin by identifying the native logical shape and authority boundary.

Ask:

1. What is the domain's actual canonical object model?
2. Which identities must remain stable across revisions?
3. Which information is canonical versus derived?
4. Which collections are ordered, set-like or maps?
5. Which external systems retain authority?
6. Which portable projections are needed?
7. What is the expected scale and access pattern?

## 2. Choose logical artifact boundaries

A good logical artifact boundary usually has coherent:

```text
schema
identity rules
authority
lifecycle
commitment profile
```

Avoid making every physical file a logical artifact automatically.

Avoid making the entire repository one artifact when independent lifecycle or authority clearly exists.

## 3. Define the logical contract

Document:

- shape;
- required fields;
- collection semantics;
- internal references;
- default/null rules;
- validation;
- commitment normalization;
- identity continuity.

If the artifact is naturally a DAG, keep the DAG.

If it is naturally a large relation, keep the relation.

## 4. Add epistemic structure

Determine where v6-style assertion envelopes or domain-native epistemic fields belong.

Options include:

- epistemics embedded in the logical artifact;
- an explicit epistemic overlay;
- a portable v6 projection.

Do not duplicate the same epistemic information in several canonical forms unless the contract explicitly requires it.

## 5. Define a commitment profile

Write commitment test vectors before optimizing storage.

Include cases for:

```text
field order
collection order
absent/null/default
presentation metadata
derived metadata
```

## 6. Create the first state snapshot

Compose the logical artifacts and pin external dependencies.

Do not introduce segmentation unless it is already needed.

A small domain can have:

```text
State Snapshot
  → one inline Logical Artifact
```

and still be fully v9-compatible.

## 7. Declare derivations

Record the source snapshots, transformation versions and policy/configuration inputs used to build derived artifacts.

Keep epistemic evidence separate from build mechanics.

## 8. Optimize materialization only after correctness

When scale requires it, measure:

```text
space amplification
read amplification
materialization amplification
verification amplification
rebuild amplification
```

Then select an explicit profile.

Do not optimize solely for compressed archive size.

## 9. Keep runtime derived

Indexes, reverse maps, search documents and caches should be rebuildable unless the domain deliberately declares otherwise.

If a convenient structure cannot be rebuilt from canon, determine whether it actually contains canonical knowledge that has been mislabeled as an index.

## 10. Publish safely

Use the lifecycle:

```text
BUILD
  ↓
VALIDATE
  ↓
PUBLISH IMMUTABLE SNAPSHOT
  ↓
ACTIVATE
```

Never rewrite a previously published snapshot in place.
