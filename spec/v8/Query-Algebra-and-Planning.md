# Query algebra and planning

## Purpose

KQP uses a typed algebra so different engines can execute the same semantic request without interpreting arbitrary JSON differently.

## Core operators

A conforming engine SHOULD normalize supported requests into a plan composed from operations equivalent to:

```text
RESOLVE(roots)
SCOPE(namespaces, kristals, shards, sources)
TRAVERSE(direction, properties, depth, limits)
FILTER(status, role, time, source, property)
EVIDENCE(closure, depth)
PROJECT(fields, encoding)
PAGE(cursor, size)
```

Mode names are conveniences over the algebra. Engines MAY optimize execution order but MUST preserve declared semantics.

## Directionality

Graph traversal is not implicitly bidirectional. `out`, `in` and `both` are explicit. A property MAY define an inverse semantic relation, but following an incoming edge is not the same as asserting the inverse relation.

## Cost-based planning

Implementations MAY choose indexes or shard order based on estimated cost. Planning metadata SHOULD expose the indexes used, shards contacted and limits applied. Query optimization MUST NOT change semantic filters or silently broaden the query.

## Discovery vs resolution

`semantic_similarity` and `hybrid` discovery can produce candidates. Exact traversal begins only after the relevant identity is resolved. If identity remains ambiguous, the result MUST expose candidates/conflict rather than select one silently.

## Validation pipeline

```text
parse
 ↓
schema validation
 ↓
semantic validation
 ↓
capability/scope validation
 ↓
budget normalization
 ↓
plan
 ↓
execute
```

Schema validity alone does not prove semantic validity, authorization or support.
