# Workflow: Build & Validate

## Inputs

A v6 build may begin from:

- observations;
- official rules/documents;
- extracted assertions;
- organizational policies;
- prior Kristal States;
- human decisions;
- machine-derived conclusions.

## Build

Normalize the input into atomic assertions with explicit:

- referents / statements;
- `coordinates` where domain geometry matters;
- `applicability` where scope matters;
- `valuations[]` where a measurement/state applies;
- `record_role` where the functional role matters;
- provenance/evidence;
- actionability only when a real policy defines it.

Then compute canonical identity/hash using the active v6 canonicalization contract.

## Validate

Validation evaluates declared policies. It should not silently overwrite:

- the underlying measurement;
- source provenance;
- authority recognition;
- applicability;
- actionability.

A failed or incomplete validation does not necessarily mean the state may not exist. It means consumers must preserve the failure/unknown state and must not present unsupported recognition.

## Human review

Human review is useful when:

- applicability is ambiguous;
- sources conflict;
- a value cannot be defensibly measured;
- the action requires judgment/authority;
- a derived rule would change organizational behavior.

The resulting human decision can itself be recorded as traceable state.

## Checklist

- [ ] Are assertions independently addressable?
- [ ] Are valuation dimensions explicit?
- [ ] Are `unknown` and `not_applicable` preserved correctly?
- [ ] Are coordinates distinct from applicability?
- [ ] Is source/evidence distinct from validation?
- [ ] Is authority recognition explicit?
- [ ] Is actionability distinct from measurement?
- [ ] Would an automatic path still cross the target owner's authority boundary?
