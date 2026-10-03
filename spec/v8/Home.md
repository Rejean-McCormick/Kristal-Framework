# Kristal v8

**Standard version:** `8.0.0`

Kristal v8 is the compatibility-preserving capability release of Kristal. It keeps the v6 portable interchange artifact and the v7 semantic identity model intact while standardizing two optional layers:

1. the **Language Layer**, which externalizes human lexicalization into composable lexical Kristals; and
2. the **AI Query Layer**, which provides exact semantic query, typed traversal, federation, bounded context compilation and compact AI-oriented projections.

The governing rule is:

```text
v6/v7 semantic truth + optional v8 capabilities = v8 deployment
```

Language artifacts, query indexes, query results, AI context bundles and caches are never semantic authority merely because they are useful or fast.

## Why v8 exists

v7 established opaque semantic identity (`KQ`, `KP`, `KA`, `KS`), KOS mappings, Mesh traversal, projections and sharding. v8 finishes two boundaries that should not be embedded in that semantic core:

- **human language** is a representation of meaning, not the meaning itself;
- **AI retrieval context** is a bounded read model, not the canonical state.

v8 therefore optimizes access without mutating truth.

## Normative map

- [Core specification](01-core-spec/kristal-v8-core-spec.md)
- [Compatibility contract](01-core-spec/compatibility-contract.md)
- [Core invariants](Core-Invariants.md)
- [Architecture](Architecture.md)
- [Language Layer](Language-Layer.md)
- [Semantic Universe and lexical Kristals](Semantic-Universe-and-Lexical-Kristals.md)
- [Lexical resolution](Lexical-Resolution.md)
- [AI Query Layer](AI-Query-Layer.md)
- [Query Protocol](Query-Protocol.md)
- [Query algebra and planning](Query-Algebra-and-Planning.md)
- [Federation, pagination and continuations](Federation-Pagination-and-Continuations.md)
- [AI Context Compiler](AI-Context-Compiler.md)
- [AI compact encoding](AI-Compact-Encoding.md)
- [Semantic fingerprints and integrity](Semantic-Fingerprints-and-Integrity.md)
- [Security and trust boundaries](Security-and-Trust-Boundaries.md)
- [v6/v7 adapters](Adapters-v6-v7.md)
- [Conformance](Conformance.md)
- [Migration](Migration-v7-to-v8.md)

## Compatibility first

A v8 implementation MUST accept valid v6 and v7 artifacts unchanged. Enabling v8 features does not authorize rewriting a source artifact. v8 capabilities are negotiated and may be absent.
