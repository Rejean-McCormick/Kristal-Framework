# Actionability & Human Boundaries

Kristal v6 can represent **whether an action is ready for automation or requires a human**, while keeping execution authority outside the knowledge artifact.

## Typical modes

A profile may distinguish modes such as:

- `automatic`;
- `human_review`;
- `human_decision`;
- `manual`;
- `prohibited`;
- `insufficient_information`;
- `not_applicable`.

## The critical invariant

```text
actionability = automatic
≠ permission to mutate another system
```

`automatic` means that, according to the represented knowledge/policy, no human judgment is required before the action path can be attempted.

The target system still decides whether the caller is authorized and whether the request is admissible.

## Operational pattern

```text
Kristal State
   ↓ actionability
routing / orchestration
   ↓
explicit owner contract
   ↓
authority + admission check
   ↓
owner-local mutation
   ↓
receipt / observation / decision
   ↓
new Kristal evidence/state
```

## Why this matters

The goal is not to redesign an organization's processes. It is to make the existing process explicit enough that deterministic work can be automated with minimal friction.

Humans are then reserved for:

- ambiguity;
- interpretation;
- legal/organizational authority;
- exceptions;
- negotiation;
- safety-sensitive judgment;
- novel cases;
- policy changes.

A human decision can itself become a traceable decision record and, when appropriate, later be generalized into a new organizational rule. That is how the system improves over time without silently learning rules that nobody approved.
