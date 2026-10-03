# What is Kristal?

Kristal v6 is a **portable structured memory and actionability layer** for knowledge, state, rules, observations and decisions.

## One-sentence definition

> Kristal preserves domain knowledge as atomic, contextual, traceable assertions whose measurements, roles, applicability and automation boundaries remain explicit and reusable over time.

Kristal is deliberately domain-neutral. It does not impose one universal ontology for mathematics, biology, regulation, recipes, diagnostics or organizational operations. It provides a stable infrastructure in which each domain can define its own geometry and measurement semantics without losing provenance, validation or identity.

## What Kristal is for

Kristal is useful when you need to:

- preserve useful human and AI work instead of recreating it;
- keep facts, rules, observations and local policies distinct;
- represent uncertainty or graded properties without forcing binary answers;
- keep source, evidence, validation and authority separate;
- preserve disagreement and superseded knowledge;
- derive views, paths, diagnostics or workflows from canonical assertions;
- automate deterministic portions of a process without silently taking authority away from humans or source systems;
- move the same structured knowledge between applications without turning Kristal into their mutable database.

## What Kristal is not

Kristal is not:

- one global truth database;
- one universal domain ontology;
- a workflow engine;
- an operational application database;
- an authority that makes a rule official merely by storing it;
- an actuator that may execute an action merely because it is marked `automatic`.

## Three common kinds of information

### 1. External authoritative constraints

Examples: laws, official procedures, standards, manufacturer requirements.

Kristal records their identity, source, applicability and succession. It does not “improve” them.

### 2. Neutral observed state

Examples: document received, temperature measured, symptom observed, payment recorded.

Kristal records what happened, when, where and from which source.

### 3. Organizational knowledge

Examples: internal thresholds, preferred diagnostic order, escalation policy, review rules, definitions of “ready”.

Kristal preserves these as organization-scoped rules instead of pretending they are universal facts.

These three categories can coexist in one state while remaining distinguishable through `record_role`, provenance and applicability.

## Actionable without over-automation

Kristal separates representation from execution:

```text
nuanced world
    ↓
Kristal State
    ↓
policy + actionability
    ↓
┌──────────────┬────────────────┐
│ deterministic│ human expertise│
│ automation   │ review/decision│
└──────────────┴────────────────┘
```

The system can automate what does not require human judgment while routing ambiguity, authority, safety, interpretation and exceptions to people whose expertise is useful.
