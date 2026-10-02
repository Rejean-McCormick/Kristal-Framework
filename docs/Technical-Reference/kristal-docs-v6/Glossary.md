# Glossary

## Applicability
The envelope in which an assertion applies: domain, jurisdiction, time window, environment, language or other declared context.

## Assertion
An atomic statement, typically subject → predicate → object, wrapped with semantic/traceability metadata.

## Actionability
The policy-oriented human/automation boundary for an action. It does not itself grant execution authority.

## Authority recognition
A scoped recognition decision by an authority channel. Distinct from validation and signatures.

## Canonicalization
Technical process that turns JSON content into stable bytes for hashing/signing. Not a truth or authority judgment.

## Coordinates
Domain-specific position/context of an assertion: scale, layer, variant, operating condition, taxonomy axis, process phase, etc.

## Derived projection
A rebuildable view/index/materialization produced from canonical state and declared transform/policy inputs.

## Evidence
Material directly supporting an assertion. Distinct from provenance and validation.

## Kristal State
The primary v6 canonical structured artifact (`artifact_type: kristal_state`).

## `not_applicable`
A value state saying the valuation dimension does not apply to the assertion. Not equivalent to low or zero.

## `unknown`
A value state saying the dimension applies but the value is unresolved. Not equivalent to zero.

## Provenance
Trace of where an assertion/representation came from and how it was produced.

## Reader / view policy
Policy controlling which labeled material a consumer may expose.

## Record role
Functional role of a record, such as authoritative constraint, observed state, organizational rule, reference knowledge, derived state, decision, action or structural record.

## Referent
Stable identity for what assertions are about. Distinct from the assertions themselves.

## Validation
Policy evaluation of an assertion/artifact. Distinct from source existence and authority recognition.

## Valuation
Typed measurement/state attached to an assertion. It declares a dimension, value semantics, value state and optional value/method/unit/scale metadata.

## Value semantics
The mathematical/semantic shape of a valuation: boolean, categorical, set, ordinal, scalar, interval, probability, distribution, vector, partial order, state or temporal.

## Working / Reference Exchange
Legacy v5 packaging terminology retained for migration/compatibility. In v6 prefer Kristal State lifecycle/status plus validation/recognition.
