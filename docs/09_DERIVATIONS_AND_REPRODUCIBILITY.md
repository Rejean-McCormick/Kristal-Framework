# Derivations and reproducibility

## 1. Purpose

Kristal has long required deterministic, declared builds for reproducible artifacts. V9 makes that build causality machine-readable through a Derivation Graph.

A derivation is not a knowledge claim. It is a record of computation.

## 2. Derivation model

Conceptually:

```text
declared inputs
      +
transform identity
      +
parameters
      +
toolchain/environment contract
      ↓
outputs
```

The draft contract identifier is:

```text
kristal.derivation/9.0
```

## 3. Example

```json
{
  "contract": "kristal.derivation/9.0",
  "transform": {
    "id": "pokemon.normalize-learnsets",
    "version": "2.1",
    "digest": "sha256:..."
  },
  "inputs": [
    {
      "artifact_id": "src:pokeapi:pokemon_moves",
      "logical_commitment": "sha256:..."
    }
  ],
  "parameters": {
    "normalization_profile": "pokemon.learnsets/1"
  },
  "outputs": [
    {
      "artifact_id": "urn:kristal:pokemon:learnsets",
      "logical_commitment": "sha256:..."
    }
  ],
  "determinism": {
    "claimed": true
  }
}
```

The draft machine contract is `schemas/v9/kristal-derivation.schema.json`; fields may still evolve before the release candidate.

## 4. Exact-input rule

A deterministic derivation must declare every input that can affect its output, or eliminate that source of variability.

Typical inputs include:

- source snapshots;
- schemas;
- transformation code/version;
- policies;
- configuration;
- locale when relevant;
- random seeds;
- compiler/tool versions where output depends on them;
- external data dependencies.

A build that reads undeclared mutable network state cannot claim strong deterministic reproducibility.

## 5. Environment discipline

Not every operating-system detail belongs in the logical derivation identity. The goal is to capture variables that can affect output.

Implementations should avoid contaminating derived artifacts with irrelevant:

```text
absolute local paths
wall-clock timestamps
machine-specific temporary directories
unordered filesystem traversal
unstable process IDs
```

unless those values are intentionally part of the output contract.

## 6. Derivation graph

Artifacts and transformations form a directed build graph.

```text
PokeAPI snapshot
      ↓ normalize
canonical learnset relation
      ↓ project
logical artifact
      ↓ materialize
exchange segments
      ↓ index
runtime index
```

A change should invalidate only descendants whose declared inputs or logical outputs are affected.

## 7. Logical change pruning

An implementation may rebuild a node and discover that its logical commitment is unchanged.

It may then stop downstream invalidation:

```text
source bytes changed
      ↓
rebuild logical artifact
      ↓
logical commitment unchanged
      ↓
no logical downstream rebuild required
```

This is an optimization, not a normative requirement for correctness.

## 8. Rebuild claims

A materialization or runtime profile may promise one of several reproducibility levels, for example:

```text
logical-reproducible
byte-reproducible
best-effort
non-deterministic-derived
```

The profile must not claim byte reproducibility if compression timestamps or backend-specific ordering remain uncontrolled.

## 9. Build receipts

Deployments may retain signed build receipts containing:

- derivation record;
- exact input commitments;
- output commitments/digests;
- validator results;
- execution environment evidence.

A build receipt supports audit but remains distinct from the logical state unless a contract explicitly includes it.
