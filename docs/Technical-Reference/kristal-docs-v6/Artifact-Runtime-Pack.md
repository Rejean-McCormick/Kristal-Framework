# Artifact: Runtime Pack

> **Legacy / compatibility note (v6):** this page documents a v5-era packaging/materialization surface. New v6 domain models should treat `kristal_state` as the canonical state and use this surface only when a consumer contract explicitly requires it.


A **Runtime Pack** is an offline-capable runtime/query artifact derived from an Exchange or shard set.

It is optimized for activation and query performance while preserving the Kristal v5 labels needed for validation, certainty, authority, scope, provenance, and reader policy.

---

## What it is for

Use a Runtime Pack when you need to:

- activate a Kristal in a local or service runtime;
- serve queries efficiently;
- support offline operation;
- record runtime policies that affect reproducibility;
- preserve labels required by reader policies;
- support safe rollout, rollback, and compatibility checks.

---

## What it contains conceptually

A Runtime Pack typically includes:

- manifest identity;
- source Exchange or federation reference;
- source artifact status;
- data files;
- indexes and auxiliary structures;
- query contract reference;
- reader policy references;
- runtime policies;
- validation and authority labels;
- integrity and signature metadata.

---

## What it must preserve

Runtime Pack construction must preserve or faithfully index:

- artifact status;
- assertion status;
- validation status;
- certainty level;
- `validated_as`;
- authority channel;
- recognition status;
- scope;
- provenance references;
- evidence references;
- lineage.

A Runtime Pack must not flatten scoped validation into universal truth.

---

## Activation

Runtime activation is separate from artifact existence and validation.

A pack may exist and verify technically, but still be unavailable under a deployment’s reader policy, authority policy, environment, tenant, or rollback constraints.

---

## Related pages

- [Artifact-Exchange](Artifact-Exchange.md)
- [Query-Basics](Query-Basics.md)
- [Workflow-Activate-Rollback-Downgrade](Workflow-Activate-Rollback-Downgrade.md)
- [Operations-Release-Strategy](Operations-Release-Strategy.md)

---

## Technical details

- Schema: `kristal-docs-v5/02-schemas/runtime-pack-manifest.schema.json`
- Example: `kristal-docs-v5/10-examples/runtime-pack-manifest.example.json`
- Runtime policies: `kristal-docs-v5/03-reproducibility/allowed-runtime-pack-policies.md`
