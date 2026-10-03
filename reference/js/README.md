# Kristal JavaScript Reference Implementation — v8.0.0

> **Non-normative.** The Kristal specification, schemas and TCK define conformance. This package demonstrates executable behavior without becoming semantic authority.

The reference runtime now targets **Kristal v8** while retaining the existing v6 portable-state and v5 compatibility code paths.

```text
v6 portable state ─┐
                   ├─> v8 reader/adapters ─> exact KQP ─> AI context
v7 KQ/KP/KA/KS ────┘             │
                                  └─> external lexical Kristals
```

## Requirements

- Node.js 22+
- no npm dependencies

## Implemented v8 profiles

The reference runtime implements local/reference behavior for:

- **V8-Reader** — detects and reads v6, v7 and v8 artifacts without rewriting v6/v7;
- **V8-Language** — BCP 47 parsing through `Intl.Locale`, deterministic lexicon-stack precedence, explicit missing/conflict behavior;
- **V8-Query** — exact identity lookup, neighborhood, semantic traversal, evidence closure, semantic slices and unknown-root inspection;
- **V8-AI-Context** — deterministic semantic-atom selection, byte budgets, optional token estimates and `symbol_table_v1` compact payloads;
- **V8-Integrity** — inherited byte fingerprints plus a documented non-normative semantic-fingerprint profile;
- derived query indexes for identity, incoming/outgoing edges, predicate use, assertions and evidence.

The package does **not** claim remote **V8-Federation** transport conformance. A dataset may contain multiple local source artifacts, but remote shard coordination/availability is deliberately not simulated and capabilities report `federation: false`.

## Run all tests

```bash
npm test
```

This executes v6 compatibility tests, v8 reference tests and retained v5 compatibility tests.

## Main v8 commands

Inspect any supported artifact:

```text
node bin/kristal-ref.mjs inspect-artifact <artifact.json>
```

Advertise actual reference-runtime capabilities:

```text
node bin/kristal-ref.mjs v8-capabilities
```

Compute the reference semantic fingerprint:

```text
node bin/kristal-ref.mjs semantic-fingerprint <artifact.json>
```

Resolve a semantic identity through a lexical stack:

```text
node bin/kristal-ref.mjs resolve-lexicon KQ1001 <stack.json> \
  --lexicon <fr-core.json> --lexicon <fr-domain.json>
```

Execute an exact KQP query over one or more canonical artifacts:

```text
node bin/kristal-ref.mjs query-v8 <request.json> \
  --artifact <entity-registry.json> \
  --artifact <property-registry.json> \
  --artifact <assertion-registry.json> \
  --artifact <source-registry.json> \
  --artifact <mesh.json> \
  --output <query-result.json>
```

Build rebuildable query indexes:

```text
node bin/kristal-ref.mjs build-query-index \
  --artifact <entity-registry.json> \
  --artifact <mesh.json> \
  --output-dir <index-dir>
```

Compile a bounded AI context bundle:

```text
node bin/kristal-ref.mjs compile-ai-context <query-result.json> \
  --max-bytes 131072 \
  --encoding symbol_table_v1 \
  --output <ai-context.json>
```

A token limit can also be supplied with `--max-tokens` and `--tokenizer-id`. The zero-dependency CLI uses the deterministic reference estimate of approximately four UTF-8 bytes per token and marks the bundle estimate as `heuristic`; production engines should inject the actual tokenizer.

## Semantic fingerprint profile

The implementation exposes the non-normative profile:

```text
kristal.reference:semantic-fingerprint/v1
```

It is domain-separated from byte identity. For non-lexical artifacts it excludes presentation fields such as `preferred_label`, `label`, descriptions and titles, plus derived hash/signature fields. Lexical Kristals keep lexical content because lexical content is their purpose. Changing a semantic field changes the digest; changing a v7 display label does not.

This reference profile is **not** a replacement for inherited v6/v7 byte/content hashes.

## KQP behavior

The reference query engine:

- requires exact identity discovery for semantic answers;
- distinguishes `kristall`, `kristal_v6` and external identities;
- builds non-authoritative in-memory indexes;
- honors typed direction/property/edge-semantic constraints;
- binds pagination cursors to the normalized query and source fingerprint set;
- returns `partial` rather than a false negative when limits truncate output;
- carries source fingerprints and explicit unresolved roots;
- never mutates canonical source artifacts.

Valid KQP modes not implemented by this small reference engine return an explicit `error` result rather than being guessed.

## v6 commands

```text
node bin/kristal-ref.mjs state-id <kristal-state.json>
node bin/kristal-ref.mjs verify-state <kristal-state.json> [--require-identity]
node bin/kristal-ref.mjs summarize-state <kristal-state.json>
```

## Legacy v5 compatibility

The former Exchange/Runtime Pack/security adapter remains available for old consumers:

```text
exchange-id
verify-exchange
build-runtime-pack
verify-runtime-pack
verify-runtime-profile
verify-signature
verify-trust
verify-referent-registry
verify-knowledge-model-contract
```

## Authority boundary

The runtime validates, adapts, indexes, queries and projects. It does not define factual truth, legal authority, organizational policy or execution permission.

```text
READ MODEL != CANONICAL STATE
MODEL OUTPUT != AUTHORITY
PARTIAL RESULT != NEGATIVE RESULT
LEXICON != SEMANTIC AUTHORITY
```
