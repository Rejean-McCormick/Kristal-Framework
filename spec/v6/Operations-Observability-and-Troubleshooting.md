# Operations: Observability & Troubleshooting

## Identity failures

Check standard/schema version, canonicalization profile, content boundary and hash/signature inputs.

## Query returns unexpected material

Check:

- reader/view policy;
- `applicability` filters;
- valuation dimension/value state;
- `record_role`;
- validation/recognition filters;
- conflicts/supersession.

## Automation unexpectedly blocked

Check `actionability.mode`, `requires_human_validation`, missing inputs and the downstream owner admission/authority policy.

## Automation unexpectedly attempted

Verify that a consumer did not infer actionability from valuation magnitude. `high` never means “execute”.

## Missing/incorrect measurements

Verify that the valuation dimension and `value_semantics` are correct and that `unknown`/`not_applicable` have not been coerced.

## Projection drift

Recompute the projection from the pinned source state and declared transform/profile. A derived store should be disposable and reproducible.
