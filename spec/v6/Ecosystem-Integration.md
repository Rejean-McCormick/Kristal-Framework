# Ecosystem Integration

Kristal v6 is a knowledge/state artifact layer. It is designed to participate in a broader system without absorbing the authorities of those systems.

## Typical kOA pattern

```text
source system / acquisition
        ↓ immutable snapshot / evidence
      DaaT / ACL
        ↓ admitted explicit contract mapping
     Kristal State
        ↓ projection / actionability
Interaction Kernel / owner contract
        ↓
Orgo / Konnaxion / other operational owner
```


## DaaT boundary

In Interaction Kernel deployments, **DaaT** (`daat`) is the narrow anti-corruption/admission and explicit contract-mapping boundary in front of Kristal. It does not acquire or store sources, perform general corpus normalization, own application state, or mint Kristall v7 semantic identities.

## Interaction Kernel

IK transports explicit versioned Profiles and admission semantics. A Kristal artifact may inform an action, but IK/owner contracts remain the boundary for execution.

## Orgo

Orgo may consume Kristal artifact-ready events as Signals and route deterministic vs human-required work using actionability metadata. It does not let Kristal directly mutate Cases or Tasks.

## SemantiK Architect / communication

A communication system should not ingest arbitrary Kristal content and infer what must be said. An ACL should select the assertions that are intentionally communicable and preserve their traceability, valuations, applicability and actionability as context.

## Projection is not canon

Consumer indexes, databases, timelines, UI summaries and Runtime-like packs are rebuildable views. They do not become a second source of truth merely because they are convenient to query.
