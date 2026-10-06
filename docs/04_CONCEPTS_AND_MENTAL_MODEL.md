# Concepts and mental model

## 1. The three identities

V9 starts by separating three questions.

### Semantic identity

**What logical thing are we talking about?**

Examples include a v7 `KQ`, `KP`, `KA` or `KS`, or a domain-defined stable artifact identifier.

### Logical commitment

**What is the exact logical content of this revision under a named profile?**

The logical commitment is independent from compression, segment boundaries and storage location.

### Blob digest

**What exact bytes did we receive or store?**

The blob digest belongs to a physical representation.

```text
SEMANTIC ID
    !=
LOGICAL COMMITMENT
    !=
BLOB DIGEST
```

## 2. State versus artifact

A **logical artifact** is a typed unit of knowledge with its own logical contract.

A **state snapshot** is an immutable composition of artifacts and pinned references.

A state is therefore not required to be one giant semantic document.

## 3. Owned member versus pinned reference

An **owned member** participates directly in the publishing authority's state.

A **pinned external reference** points to another immutable artifact or state while preserving the external authority and ownership boundary.

The distinction is essential for federation, clinical systems, educational hierarchies and ecosystem models.

## 4. Shard versus segment

A **shard** is a semantic, governance or lifecycle boundary. A shard may be independently curated, versioned and published.

A **segment** is a physical unit chosen by a materialization profile.

One shard may contain many segments. A hierarchy may contain many shards even if every shard is stored in a single small file.

## 5. Projection versus materialization

A **projection** changes the view or contract under which logical information is exposed. It may be lossy or partial and must declare that fact.

A **materialization** changes how the same logical contract is physically represented.

Example:

```text
RecipeVariant + ProcedureGraph
        │
        ├── materialize → native JSON blob
        │
        └── project → portable v6 assertions
```

The first can preserve the same logical contract. The second exposes a different contract and therefore needs an explicit projection relation.

## 6. Derivation versus provenance

Build provenance answers:

> How did this artifact get produced?

Epistemic provenance answers:

> Why should this knowledge be believed, interpreted or trusted in this context?

The same software can build an artifact without becoming an epistemic authority over its claims.

## 7. Head versus snapshot

A state snapshot is immutable.

`HEAD`, `current`, `production` or a channel pointer is mutable and selects a snapshot.

```text
HEAD → S42
```

may later become:

```text
HEAD → S43
```

without mutating S42.

## 8. Canon versus runtime

Canonical state defines logical membership and domain truth claims under the applicable authority.

Runtime structures optimize access and may be discarded and rebuilt.

A convenient lookup table is not automatically canon simply because an application uses it heavily.
