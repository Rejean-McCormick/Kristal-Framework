# v8 architecture

## 1. Layer model

```text
                 canonical / authoritative
┌─────────────────────────────────────────────────────┐
│ v6 portable state + v7 semantic registries / Mesh  │
└─────────────────────────────────────────────────────┘
               │                         │
               │                         │
       lexical companions          derived read models
               │                         │
        Language Resolver          KQP Query Engine
               │                         │
               └──────────┬──────────────┘
                          │
                   Context Compiler
                          │
                 human / AI projections
```

v8 follows a CQRS-like separation: canonical state is optimized for integrity and semantic fidelity; derived read models are optimized for lookup and presentation. The pattern does not require asynchronous infrastructure or a particular database.

## 2. Anti-corruption boundaries

Adapters isolate v6, v7 and external KOS formats from v8 query internals. An implementation MUST NOT leak an external vocabulary's identifier semantics into KQ identity or reinterpret legacy fields merely for convenience.

## 3. Federation and sharding

Large semantic and lexical universes MAY be sharded by subject, jurisdiction, organization or operational locality. Sharding is an operational partition. Semantic identity remains stable across shards.

Federated governance SHOULD allow domain owners to curate specialist shards while global contracts preserve identity, provenance, query and compatibility rules.

## 4. Derived material

The following are derived/read-side material unless another inherited contract explicitly says otherwise:

- query indexes;
- search/vector indexes;
- lexical-resolution caches;
- semantic slices;
- AI context bundles;
- compact symbol tables;
- query plans;
- rendered human views.

Derived material MUST carry enough lineage to identify its source state or snapshot.

## 5. Graceful degradation

Optional capability failure MUST degrade explicitly:

- missing lexicon → preserve semantic ID;
- unavailable index → slower exact query or declared unsupported operation;
- unavailable shard → partial result with missing-shard disclosure;
- exhausted budget → truncated result with continuation/omission metadata;
- unavailable tokenizer → byte/item budget remains authoritative and token estimate is omitted or marked unavailable.

No degradation path may fabricate semantic content.
