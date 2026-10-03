# Query Basics

Kristal v6 queries should preserve labels that matter to interpretation.

## Basic flow

1. Select a `kristal_state` or derived read model.
2. Apply applicability and reader/view policy.
3. Filter by content and/or semantic metadata.
4. Return assertions with enough labels to avoid semantic ambiguity.

## Common filters

- subject / predicate / object;
- `assertion_status`;
- `record_role`;
- valuation `dimension`;
- valuation `value_semantics`;
- valuation `value_state`;
- coordinates;
- applicability;
- actionability mode;
- source/evidence;
- validation/recognition.

## Do not flatten valuations

A query asking for `high` without a dimension is usually ambiguous. Prefer:

```text
dimension = diagnostic_support
value = high
```

not simply:

```text
value = high
```

## `unknown` vs `not_applicable`

Treat these as different states. Do not sort either as numeric zero.
