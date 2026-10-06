# Migration from v8 to v9

## 1. Migration philosophy

V9 is additive. A repository does not need to rewrite valid v6/v7/v8 artifacts before adopting v9 architecture.

The preferred migration strategy is:

```text
preserve inherited contracts
      ↓
identify logical artifacts
      ↓
separate derived/runtime duplication
      ↓
introduce state snapshot + commitments
      ↓
introduce explicit derivations
      ↓
optimize materialization only where useful
```

## 2. Step 1 — inventory authority

Before changing formats, classify repository content into categories such as:

```text
canonical domain payload
portable projection
derived index/runtime
source snapshot
build/derivation metadata
presentation/view
external reference
```

Do not optimize until the source-of-truth boundary is explicit.

## 3. Step 2 — preserve inherited portable state

Keep existing:

```text
kristal_state/6.0
KQ/KP/KA/KS identities
v8 query/lexicon artifacts
```

valid under their original contracts.

V9 metadata should reference or wrap them rather than mutate their schemas.

## 4. Step 3 — identify logical artifacts

Determine which domain-native units deserve their own logical contracts.

Examples:

- RecipeVariant ProcedureGraph;
- Vehicle diagnostic graph;
- Formula IR;
- Pokémon learnset relation;
- UCKK course state;
- Clinical Commons definition set.

Do not create a separate artifact for every file merely because files already exist. The boundary should be logical and lifecycle-relevant.

## 5. Step 4 — separate read-side duplication

Look for structures that can be rebuilt from canonical content:

```text
*_by_id maps
reverse indexes
search documents
query indexes
coverage reports
statistics
AI context bundles
```

Move their authority designation to Runtime/Derived even if the first migration leaves files physically where they are.

## 6. Step 5 — define logical commitment profiles

For each logical contract, specify:

- ordered/set-like collection semantics;
- logical fields;
- excluded physical/presentation fields;
- default/null rules;
- canonicalization profile.

Generate test vectors before changing storage.

## 7. Step 6 — create a v9 state snapshot

Create an immutable v9 State Snapshot that references the existing logical artifacts and inherited v6/v7/v8 surfaces.

At this stage, materializations may remain unchanged.

This proves that v9 adoption does not require immediate data migration.

## 8. Step 7 — make derivations explicit

Convert existing build recipes into machine-readable derivation records where useful.

Prioritize:

- source normalization;
- canonical artifact build;
- portable v6 projection;
- query index build;
- runtime package build.

## 9. Step 8 — optimize large artifacts

Only after logical commitments are stable should large artifacts be repartitioned or factorized.

For Pokémon-like workloads:

```text
expanded monolith
    ↓
shared envelope + dictionaries + segments
```

For a recipe or math AST, the correct migration may be no physical change at all.

## 10. Step 9 — introduce atomic activation

Replace mutable in-place release updates with:

```text
publish immutable snapshot
      ↓
atomically select snapshot
```

Rollback should select a retained previous snapshot.

## 11. Step 10 — remove obsolete duplicated canon

Only after rebuild/reconstruction tests pass should duplicate canonical-looking structures be removed or downgraded to derived artifacts.

## 12. Repository migration checklist

A migration is healthy when:

- old v6/v7/v8 validation still passes;
- no semantic ID is silently reminted;
- logical commitments are covered by TCK vectors;
- runtime/index deletion does not destroy canonical content;
- materialization rebuild preserves logical commitments;
- active snapshot transitions are atomic;
- domain-native structures remain intact;
- authority boundaries are preserved.
