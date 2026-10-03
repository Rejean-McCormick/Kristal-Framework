# Artifact: Shard Manifest

> **Legacy / compatibility note (v6):** this page documents a v5-era packaging/materialization surface. New v6 domain models should treat `kristal_state` as the canonical state and use this surface only when a consumer contract explicitly requires it.


A **Shard Manifest** describes a scoped shard of Kristal material and the metadata needed to verify, validate, recognize, and compose it.

A shard may represent a domain, subdomain, tenant, time window, authority channel, dataset subset, or federation slice.

---

## What it is

A Shard Manifest is a verifiable pointer to shard content or a shard Exchange, annotated with:

- shard identity;
- artifact status;
- scope;
- authority channel;
- validation references;
- authority recognition references;
- integrity metadata;
- lineage;
- reader-policy-relevant labels.

---

## When it exists

You create a Shard Manifest when:

- a publisher produces a domain-scoped artifact;
- an authority channel publishes only a scoped subset;
- a federation needs to compose many sources;
- a tenant, environment, or time window needs independent update cadence;
- you want validation and authority metadata at the shard boundary.

---

## How consumers use it

Consumers typically:

1. read the shard scope;
2. verify integrity metadata if required;
3. inspect validation report references;
4. inspect authority recognition references;
5. check the authority registry and reader policy;
6. decide whether the shard can be used, hidden, rejected, or exposed with labels.

---

## Relationship to other artifacts

- **Exchange**: shard content may be an Exchange or Exchange-derived payload.
- **Validation Report**: records checks on the shard.
- **Authority Registry**: determines authority acceptance for the shard scope.
- **Federation Manifest**: composes shard manifests.
- **Runtime Pack**: may materialize a shard or federated shard set.

---

## Technical details

- Schema: `kristal-docs-v5/02-schemas/exchange-shard-manifest.schema.json`
- Example: `kristal-docs-v5/10-examples/exchange-shard-manifest.example.json`
