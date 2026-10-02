# Artifact: Validation Report

A **Validation Report** records a applicability enveloped validation decision and the findings behind it.

It does not turn a claim into universal truth. It records what was evaluated, by whom or by which validator, under which policy, for which applicability envelope, with which result.

---

## What it can validate

A Validation Report may target:

- an assertion;
- a Kristal State;
- an Exchange;
- a shard;
- a Federation Manifest;
- a Runtime Pack;
- a dataset;
- a reader policy;
- a validation policy;
- an authority channel.

---

## What it records

At a high level, it records:

- target artifact or assertion;
- target level;
- applicability envelope;
- issuer authority channel;
- validation policy reference;
- validation status;
- valuation level;
- `validated_as` classification;
- findings;
- evidence and provenance references;
- authority recognition references;
- warnings and errors;
- signatures when applicable.

---

## Common validation statuses

- `not_evaluated`
- `in_review`
- `validated`
- `conditionally_validated`
- `disputed`
- `rejected`
- `revoked`

---

## Why it matters

Validation Reports make it possible to show readers:

- validated as what;
- by whom;
- under which policy;
- for which applicability envelope;
- with what valuation;
- with what evidence;
- with what limitations.

---

## Relationship to other artifacts

- Exchanges and Shards may reference Validation Reports.
- Federation Manifests may require Validation Reports for included shards.
- Reader Policies may expose only assertions with matching validation status.
- Runtime Packs must preserve validation labels when materializing indexes.

---

## Technical details

- Schema: `kristal-docs-v5/02-schemas/validation-report.schema.json`
- Example: `kristal-docs-v5/10-examples/validation-report.example.json`
