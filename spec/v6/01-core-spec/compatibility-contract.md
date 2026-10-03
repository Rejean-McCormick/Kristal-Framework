# v6 / v5 compatibility contract

Kristal v6 is a breaking semantic standard, but the repository preserves v5 contracts so ecosystem applications can migrate incrementally.

## Compatibility rule

A v5 consumer MAY continue to consume v5 SES, Exchange and Runtime Pack artifacts using the frozen v5 schemas and identity profiles.

A v6 consumer SHOULD consume `kristal_state` directly.

A compatibility adapter MAY project v6 state into a legacy v5 surface, but it MUST declare any information loss. In particular, a projection MUST NOT silently collapse:

- multiple valuation dimensions into one misleading certainty value;
- non-known value states into numbers;
- actionability into execution permission;
- record role into authority;
- contextual applicability into global truth.

## Safe migration order

1. add v6 readers/verifiers;
2. preserve v5 adapters for old consumers;
3. migrate domain models to explicit valuations/roles/actionability;
4. migrate readers/projections;
5. retire a v5 surface only when no consumer depends on it.
