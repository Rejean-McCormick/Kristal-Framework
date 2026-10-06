# Contract Evolution and Compatibility

Kristal v9 uses additive versioning rather than silent reinterpretation.

```text
v6 portable state      frozen inherited substrate
v7 semantic identity   frozen inherited substrate
v8 language/query      frozen inherited substrate
v9 state architecture  additive contracts
```

`contracts/v9-compatibility-lock.json` freezes inherited v6-v8 normative prose, machine contracts and TCK vectors for the v9 draft. A change to those files MUST fail the v9 compatibility check unless a future Standard explicitly performs a compatibility-breaking migration.

## Domain logical contracts

A domain `logical_contract` versions independently from the Kristal Standard. Domain changes SHOULD be classified as one of:

- compatible addition;
- presentation-only change;
- rename preserving identity;
- semantic replacement;
- split;
- merge;
- identity migration;
- commitment-profile migration.

## Identity migrations

Changing what constitutes a semantic object is not a mere schema rename. An identity migration MUST be explicit and trace old identifiers to the new identifier or identifiers.

## Commitment-profile migrations

Any change to logical projection, field inclusion/exclusion, set/sequence normalization, domain separation, canonicalization or hash algorithm requires a new commitment profile identifier. Existing profiles are immutable.

## Compatibility projection

A v9 domain MAY provide a declared projection to `kristal_state/6.0`. The projection MUST declare its coverage/loss properties and MUST NOT automatically become the richer domain-native source of truth.
