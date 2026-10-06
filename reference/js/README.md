# Kristal JavaScript Reference Implementation — v9.0.0-draft.1

> **Non-normative.** The Kristal specification, schemas and TCK define conformance. This package demonstrates executable behavior without becoming semantic authority.

The reference runtime targets **Kristal v9 Semantic State Architecture** while retaining the v6 portable-state, v7/v8 read/query, and legacy v5 compatibility code paths.

```text
v6 portable state ─┐
v7 KQ/KP/KA/KS ────┼─> inherited v8 reader/query/language
v8 query/language ─┘

v9 Logical Artifact ─> Logical Commitment ─┐
v9 State Snapshot  ─> State Commitment  ───┼─> materialization / publish / activate
v9 Derivation      ─> build lineage      ──┘
```

## Requirements

- Node.js 22+
- no npm dependencies

## Implemented v9 reference behavior

- `V9-State-Reader` basics for Logical Artifacts and State Snapshots;
- baseline `kristal.logical/jcs-sha256-v1` logical commitments;
- baseline `kristal.state-commitment/jcs-sha256-v1` state commitments;
- materialization-manifest verification;
- derivation, exchange and activation structural verification;
- immutable local state publication into a content-addressed state directory;
- atomic local activation-pointer replacement with optional compare-and-swap protection;
- inherited v6/v7/v8 readers and v8 query/language tooling.

The reference package does **not** claim a distributed consensus protocol, remote CAS protocol, columnar codec, protected-commitment profile, or automatic materialization planner.

## Run all tests

```bash
npm test
```

## Main v9 commands

```text
node bin/kristal-ref.mjs v9-capabilities
node bin/kristal-ref.mjs logical-commitment-v9 <logical-artifact.json>
node bin/kristal-ref.mjs verify-logical-artifact-v9 <logical-artifact.json>
node bin/kristal-ref.mjs state-commitment-v9 <state-snapshot.json>
node bin/kristal-ref.mjs verify-state-v9 <state-snapshot.json>
node bin/kristal-ref.mjs verify-materialization-v9 <materialization.json>
node bin/kristal-ref.mjs verify-derivation-v9 <derivation.json>
node bin/kristal-ref.mjs verify-exchange-v9 <exchange.json>
node bin/kristal-ref.mjs verify-activation-v9 <activation.json>
node bin/kristal-ref.mjs publish-state-v9 <state.json> <store-dir>
node bin/kristal-ref.mjs activate-state-v9 <activation.json> <pointer-file>
```

## Commitment boundaries

The v9 logical artifact commitment commits to domain-normalized payload content, logical scope, logical extensions and pinned logical dependencies. It deliberately does not use the semantic `artifact_id` as content identity.

The v9 state commitment commits to owned member commitments, pinned external references and logical scope. It deliberately ignores publication timestamps, signatures, parent lineage and physical materialization details.

```text
SEMANTIC IDENTITY != CONTENT IDENTITY
LOGICAL COMMITMENT != BLOB DIGEST
```

## Inherited v8 commands

The existing v8 commands (`v8-capabilities`, `semantic-fingerprint`, `query-v8`, `build-query-index`, `compile-ai-context`, lexical resolution, etc.) remain available and unchanged.

## Adapter boundary

A v9 reader may inspect inherited artifacts without rewriting them. V9 physical optimization never grants semantic authority, and derived indexes remain rebuildable read models.
