# AI Query Layer

## Goal

The AI Query Layer lets an AI retrieve compact, exact semantic context without loading an entire Kristal or relying only on prose/chunk retrieval.

The preferred flow is:

```text
natural-language request
    ↓ approximate discovery (optional)
candidate semantic IDs
    ↓ deterministic identity resolution
exact graph / assertion / evidence query
    ↓ typed KQP plan
semantic result / continuation
    ↓ context compiler
bounded AI context bundle
```

Approximate discovery may use lexical search, embeddings or ranking techniques. Candidate discovery MUST remain distinguishable from exact semantic query.

## Query families

v8 standardizes these modes:

- `identity_lookup`
- `neighborhood`
- `semantic_traversal`
- `evidence_closure`
- `authority_resolution`
- `temporal`
- `diff`
- `capability`
- `constraints`
- `cross_kristal`
- `lexical`
- `unknowns`
- `semantic_slice`

Implementations MAY add namespaced custom modes but MUST expose the normalized plan and capability support.

## Progressive disclosure

Large payloads SHOULD use a claim-check style: return semantic/evidence references, digests and compact metadata first, then allow explicit `expand`/follow-up queries. AI clients should not receive full source payloads unless needed.

## Exactness boundary

After identity resolution, traversal over assertions, relations and evidence uses declared semantic IDs and canonical source references. A similarity score, LLM confidence or embedding distance is never itself a factual assertion.

## Planner boundary

An AI model MAY propose a KQP request. The query engine validates and normalizes it deterministically. The model does not acquire additional authority by asking for a wider scope, more shards, more budget or privileged material.
