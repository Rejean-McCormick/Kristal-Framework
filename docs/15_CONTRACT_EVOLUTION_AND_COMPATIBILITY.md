# Contract evolution and compatibility

## 1. Additive evolution

V9 follows the compatibility philosophy already used by v8.

```text
v6 portable substrate      frozen
v7 semantic identity       frozen
v8 language/query layer    frozen
v9 state architecture      additive
```

A new capability should normally receive a new contract rather than silently reinterpret an inherited field.

## 2. Compatibility lock

A v9 release should carry a compatibility lock or equivalent manifest that pins inherited machine contracts by digest.

This prevents a release from claiming compatibility while shipping modified v6/v7/v8 schemas under the same identifiers.

## 3. Contract version versus Standard version

A domain logical contract evolves independently from the Kristal Standard version.

Example:

```text
recipes.procedure-graph/3.0
```

may evolve to:

```text
recipes.procedure-graph/3.1
```

without requiring Kristal v10.

Likewise, a new physical materialization profile does not imply a new semantic Standard version.

## 4. Classes of change

Domain contracts should distinguish at least:

### Compatible addition

A new optional field or capability that does not change existing interpretation.

### Presentation-only change

Labels, UI metadata or other excluded presentation fields change without logical commitment change under the applicable profile.

### Rename

A field name changes while preserving the same logical identity and semantics. A migration/projection rule may be required.

### Semantic replacement

A concept or rule is replaced by a different logical concept.

### Split/merge

One previous logical object becomes several, or several objects become one.

### Identity migration

The rule defining semantic identity changes.

### Commitment-profile migration

Logical normalization or commitment boundaries change.

The last two must never happen silently.

## 5. Profile immutability

Once a commitment profile identifier is published, implementations must not change:

- its inclusion/exclusion rules;
- ordering semantics;
- canonical scalar representation;
- hash algorithm;
- domain separator.

A change produces a new profile identifier.

## 6. V6 compatibility

An unchanged `kristal_state/6.0` remains valid.

V9 can treat it as a logical artifact whose logical contract is the inherited v6 contract.

A v9 domain may additionally provide a projection into v6 for interoperability.

That projection must not be mislabeled as the domain-native canon if it is not.

## 7. V7 compatibility

KQ/KP/KA/KS identities remain stable and must not be recycled or reinterpreted by v9.

V9 artifact IDs may reference or contain inherited semantic IDs.

## 8. V8 compatibility

V8 semantic fingerprints remain valid under their original profiles.

A v9 logical commitment does not retroactively replace a v8 fingerprint.

```text
v8 semantic fingerprint
    query/cache semantic key

v9 logical commitment
    logical artifact/state commitment
```

The two may coexist.

## 9. Downgrade

Projecting a v9-native artifact to an older contract may lose capabilities.

Loss must be declared rather than compensated by rewriting semantics.

```text
DOWNGRADE LOSS != SEMANTIC REWRITE
```
## Compatibility fixture errata

A frozen compatibility lock records historical bytes; it must not be silently rewritten to hide a defective fixture. If a historical TCK/example fixture is proven internally inconsistent with an unchanged identity rule, the active tree may carry a narrowly scoped correction only when an explicit `kristal.compatibility-errata/v1` record binds the historical locked hash to the corrected hash, states the unchanged rule, and declares whether semantic behavior changed. Conformance must verify both sides of that record.

