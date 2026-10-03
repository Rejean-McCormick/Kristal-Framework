# Kristal Query Protocol (KQP)

Protocol: `kristal-query/1.0`

KQP is the machine contract for v8 AI-oriented query. It is a read protocol unless an independent write/admission protocol explicitly says otherwise.

## Request

A request declares:

- `query_id` and `mode`;
- semantic roots;
- optional discovery method;
- source/namespace/shard scope;
- typed traversal direction and property constraints;
- semantic/status/source filters;
- evidence policy;
- pagination/continuation cursor;
- hard resource budget;
- optional lexical rendering request;
- output encoding preference.

Free-form intent text MAY guide ranking but MUST NOT override typed constraints.

## Budget

KQP budgets are deterministic control-plane limits. Recommended hard dimensions are:

- `deadline_ms`;
- `max_items`;
- `max_nodes` / `max_edges` where relevant;
- `max_bytes`;
- optional `max_tokens` when accompanied by a declared `tokenizer_id`.

Byte/item/time limits remain interpretable without a model-specific tokenizer. Child/federated queries consume the parent budget; they do not receive fresh independent budgets.

## Result

A result declares:

- executed mode and normalized plan;
- source-state fingerprints;
- resolved roots and discovery candidates;
- returned semantic material;
- conflicts and unresolved items;
- `status: complete|partial|error`;
- semantic/evidence/source completeness;
- truncation reasons;
- continuation cursor when more results exist;
- explicit omissions.

`partial` means the returned material may be useful but is not complete under the requested scope. It MUST NOT be interpreted as a negative answer about omitted material.

## Pagination

Pagination MUST preserve declared semantic ordering. Cursor state is opaque to clients. A continuation MUST bind to the same normalized query and source snapshot/fingerprint set or fail explicitly.

## Derived status

A KQP result is derived output. It MUST NOT be used as semantic authority when canonical source artifacts are available.
