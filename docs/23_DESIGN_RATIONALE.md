# Design rationale

## 1. Why v9 is necessary

The main pressure is not that JSON compresses poorly. Repetitive Kristal JSON often compresses extremely well.

The deeper issue is that a monolithic expanded representation causes operational amplification:

```text
small logical change
    → large rewrite
small query
    → large parse/read surface
small validation scope
    → large validation surface
one representation
    → identity accidentally tied to packing
```

V9 therefore targets representation independence rather than compression alone.

## 2. Why not replace JSON with a binary format?

A binary format can improve size and speed but cannot by itself solve:

- stable identity across encodings;
- native-shape preservation;
- partial publication;
- authority boundaries;
- derivation lineage;
- runtime/canon separation.

V9 must first define logical equality and materialization contracts. Codecs can then evolve independently.

## 3. Why Logical Artifact instead of Assertion Family?

Assertion-family factorization is powerful for Pokémon-like relations, but it is not a suitable universal model for:

- recipe DAGs;
- mathematical ASTs;
- conditional diagnostic graphs;
- federated curriculum hierarchies;
- protected clinical compartments.

Logical Artifact is intentionally weaker: it standardizes the envelope and lifecycle while delegating internal shape to a contract.

## 4. Why not make everything v6 assertions?

V6 assertions remain an excellent portable epistemic substrate. Their atomicity gives independent addressability.

But atomic addressability does not imply that every domain-native model should be physically or canonically flattened into assertion objects.

Recipes already demonstrate the healthier pattern: domain-native ProcedureGraph as business canon, portable v6 as a derived interoperability projection.

V9 generalizes that pattern.

## 5. Why immutable snapshots?

Immutable snapshots simplify:

- reproducibility;
- historical comparison;
- concurrent readers;
- rollback;
- cache identity;
- audit;
- partial distribution.

Mutable operational systems can remain outside the snapshot and publish observations/decisions into new states.

## 6. Why separate publish and activate?

A new state can be valid and published without being appropriate for production activation.

Keeping activation separate permits:

- staged rollout;
- explicit governance;
- fast rollback;
- concurrent verification;
- environment-specific channels.

## 7. Why state commitment over artifact commitments?

A state commitment should describe logical composition, not a physical package.

This permits:

- repack without semantic revision;
- multiple exchanges for one state;
- local versus remote storage choices;
- encrypted versus plaintext materializations where policy permits.

## 8. Why no mandatory Merkle semantic tree in 9.0?

Merkle structures can enable efficient membership proofs and incremental updates, but freezing a specific semantic tree too early risks coupling identity to an optimization.

The base commitment should first establish stable logical equality. More advanced commitment structures can be introduced through future profiles.

## 9. Why no mandatory planner?

Kristal historically favors explicit policies and reproducible profiles over hidden optimizer behavior.

An automatic planner can be excellent tooling, but the selected materialization must still be explicit and reproducible.

## 10. Why distinguish shard and segment?

UCKK demonstrates semantic shards whose boundaries are educational identity/lifecycle. Pokémon demonstrates physical segments needed only for scale.

Conflating them would cause physical optimization choices to rewrite semantic governance.

## 11. Why protected commitments?

Hospital-style domains show that even revealing stable deterministic hashes can disclose equality or support guessing attacks for low-entropy content.

The v9 architecture therefore leaves commitment visibility/security profile-driven rather than assuming every logical digest is public.

## 12. Why preserve v6/v7/v8 instead of rewriting them?

The existing generations already contain the conceptual foundations v9 needs:

- deterministic build/release discipline;
- v6 portable epistemic state;
- v7 semantic IDs and factorization;
- v8 read-model separation and semantic fingerprints.

V9 is strongest when it consolidates these boundaries rather than creating a parallel replacement ecosystem.
