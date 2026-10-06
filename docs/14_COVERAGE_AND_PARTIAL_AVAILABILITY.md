# Coverage and partial availability

## 1. Purpose

V8 already defines:

```text
PARTIAL RESULT != NEGATIVE RESULT
OMISSION BY BUDGET != NEGATION
```

V9 provides the state/materialization metadata that makes those query guarantees practical when not all artifacts or segments are locally available.

## 2. Coverage

A materialization or runtime package may declare which logical scope it includes.

Conceptual example:

```json
{
  "coverage": {
    "state": "sha256:...",
    "included": [
      "pokemon.species",
      "pokemon.moves"
    ],
    "omitted": [
      "pokemon.encounters"
    ]
  }
}
```

Baseline coverage fields now exist in `schemas/v9/kristal-materialization-manifest.schema.json`; query-result completeness semantics remain owned by v8 KQP.

## 3. Availability is not truth

If `pokemon.encounters` is absent locally, a query for encounters cannot safely conclude:

```text
no encounter exists
```

It can conclude only that the available material did not provide a complete answer.

```text
NOT PRESENT LOCALLY != LOGICALLY ABSENT
```

## 4. Coverage dimensions

Coverage may need to be expressed by:

- artifact;
- shard;
- logical key range;
- time/version scope;
- query capability;
- authority domain.

A materialization profile should expose only dimensions it can state reliably.

## 5. Complete versus partial

A query engine can combine v9 coverage metadata with v8 query semantics to return statuses such as:

```text
complete
partial
truncated
unsupported
unknown
```

The query protocol remains a v8 responsibility. V9 supplies source coverage and material availability facts.

## 6. Remote materialization

A local runtime may hold only part of a state while a resolver knows where additional immutable blobs can be obtained.

A missing local blob may therefore be:

```text
available remotely
intentionally omitted
not authorized
unknown
```

Those states must not be collapsed into one generic `not found` when epistemic correctness depends on the difference.

## 7. Partial verification

A segmented exchange should allow a consumer to verify each retrieved blob against its physical digest and, where the applicable profile supports it, verify reconstruction against the logical artifact commitment.

Advanced membership proofs may be added later; they are not required for the base architecture.
