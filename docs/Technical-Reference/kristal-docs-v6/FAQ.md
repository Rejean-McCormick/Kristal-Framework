# FAQ

## What is Kristal, in one sentence?
Kristal v6 is a deterministic portable knowledge/state system that preserves atomic assertions with typed valuations, applicability, provenance, roles and explicit human/automation boundaries.

## Is Kristal a database?
Not primarily. It can be indexed or materialized into databases, but its canonical role is portable, traceable artifact/state representation.

## Is it only about epistemic certainty?
No. v6 generalizes the old certainty field into typed `valuations[]`. A valuation may represent proof closure, diagnostic support, necessity, applicability, compatibility, probability, state or another explicit dimension.

## Is `high` a probability?
Not unless the valuation uses probability semantics. In an ordinal valuation, `high` only has meaning on that declared scale.

## Does `unknown` mean zero?
No. `unknown`, `not_applicable`, `indeterminate` and `not_measured` are value states.

## What is `record_role`?
It describes whether a record is, for example, an external authoritative constraint, observed state, organizational rule, reference knowledge, derived state, decision, action or structural record.

## Does `authoritative_constraint` make a rule official?
No. Authority comes from the actual source/provenance/recognition chain.

## What is `actionability`?
It represents whether a proposed action is automatic, human-gated, manual/prohibited or lacks sufficient information under the declared policy.

## Does `automatic` let Kristal execute the action?
No. Execution authority remains with the owning system and its admission/authorization contract.

## What happened to Working/Reference Exchange?
They are retained as legacy/compatibility concepts. In v6, the canonical `kristal_state` has lifecycle/status, validation and recognition without requiring two universal artifact classes.

## What happened to Runtime Pack?
Runtime/query materializations remain useful derived artifacts, but they are not the canonical truth layer.

## Can AI enrich a Kristal over time?
Yes. That is a primary design goal: extraction, reasoning, human corrections, validation, decisions and new observations can accumulate as traceable structured work.

## Can a domain reinterpret the main scale?
Yes, by declaring the valuation dimension and semantics explicitly. The structural protocol is shared; domain meaning is specialized.

## How do I migrate v5 data?
See [Migration-v5-to-v6](Migration-v5-to-v6.md).
