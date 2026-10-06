# Open questions

This document tracks decisions that should be resolved before the v9 contracts become normative.

## 1. Exact state commitment boundary

What fields are part of a State Snapshot's logical commitment?

Likely included:

```text
state logical identity/scope
owned member semantic IDs + logical commitments
pinned external references + commitments
logical state policies that affect interpretation
```

Likely excluded:

```text
physical manifests
blob digests
storage URIs
activation status
runtime indexes
build timestamps
signatures over the snapshot
```

The exact boundary needs golden vectors.

## 2. Parent lineage and commitment

Should state parent lineage participate in the logical state commitment?

Two possible models:

### Content identity model

Identical logical content has the same logical commitment even if produced through different histories.

### Historical-state model

Lineage is logically meaningful and changes commitment.

The likely v9 answer is to keep content commitment independent and record lineage separately, but this requires a deliberate normative decision.

## 3. Semantic artifact ID namespace

Should v9 define a new first-party artifact-ID namespace, or allow domain URIs plus inherited KQ/KP/KA/KS?

A new ID class should be introduced only if existing identity systems cannot express artifact identity cleanly.

## 4. Identity profile minimum

What must every identity profile specify?

Candidate minimum:

```text
namespace
minting rule
continuity rule
non-reuse rule
migration reference
```

## 5. Protected commitment profiles

What minimum support should v9.0 provide for private/sensitive logical artifacts?

Options include:

- commitment stored only inside protected metadata;
- keyed commitment profile;
- externally anchored opaque commitment;
- no standardized protected commitment until v9.1.

The Standard should not invent cryptography but must avoid forcing unsafe public digests.

## 6. Activation contract scope

Should `kristal.activation/9.0` be a normative core contract, or an operational profile?

The core likely needs only semantic requirements:

```text
atomic pointer transition
pinned immutable target
rollback traceability
```

Storage/transport-specific compare-and-swap mechanisms can remain deployment-specific.

## 7. Projection versus materialization metadata

How should descriptors distinguish:

```text
same logical contract / different physical representation
```

from:

```text
different logical contract produced by projection
```

This distinction must be machine-readable to avoid treating a lossy portable projection as a lossless materialization.

## 8. Materialization reconstruction contract

Must every materialization profile support full reconstruction, or can some be explicitly query-only/read-side?

Recommended direction:

- `materialization` should mean logically reconstructible;
- query-only indexes should be Runtime/Derived profiles instead.

## 9. Segment descriptor minimum

Possible mandatory fields:

```text
media_type
digest
size
```

Optional fields may include compression, encryption and pruning metadata.

The Standard should avoid overloading segment descriptors with index-specific features.

## 10. Logical commitment algorithm agility

The baseline will likely be JCS + SHA-256 for JSON-compatible logical projections. The contract should still permit future algorithms via new profiles without changing logical artifact identity.

## 11. Set canonicalization

What canonical ordering is used for set-like JSON values containing nested structures?

Potential rule:

```text
normalize each member
JCS-encode member
sort by canonical byte sequence
```

This requires careful vectors for numbers, strings, nested objects and duplicate semantics.

## 12. Duplicate semantics

A set rejects duplicates. A multiset preserves multiplicity. An ordered sequence preserves order.

Logical contracts need an explicit way to communicate that distinction to commitment tooling.

## 13. Cross-artifact references

When artifact A refers to artifact B within the same State Snapshot, should the logical reference include:

```text
semantic ID only
```

or:

```text
semantic ID + expected commitment
```

The latter is safer for exact snapshot interpretation but may duplicate state-level membership information.

## 14. Release naming

Potential names for the new primary contract include:

```text
kristal.state/9.0
kristal.semantic-state/9.0
kristal.state-snapshot/9.0
```

The final name should avoid confusion with the inherited `kristal_state/6.0` portable contract.

## 15. V9 finalization gate

No open question should be resolved only by intuition. Each should be tested against:

```text
Pokémon
Recipes
VehiculeDiag
Pi Theory
HospitalOps
UCKK
MathKristal
kOA Ecosystem
```

and encoded in TCK vectors before `9.0.0` final.
