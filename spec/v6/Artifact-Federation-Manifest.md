# Artifact: Federation Manifest

> **Legacy / compatibility note (v6):** this page documents a v5-era packaging/materialization surface. New v6 domain models should treat `kristal_state` as the canonical state and use this surface only when a consumer contract explicitly requires it.


A **Federation Manifest** defines deterministic composition across shards, authority channels, validation policies, reader policies, and disagreement-preserving rules.

Federation does not rewrite shards or erase disagreement. It preserves shard identity, source authority, validation status, certainty level, and scope.

---

## What it is for

Use a Federation Manifest when you need to:

- combine multiple shards into one federated Kristal view;
- preserve the authority channel behind each shard;
- expose different views through reader policies;
- keep conflicts visible rather than silently resolving them;
- update one shard without rebuilding every other shard;
- distribute a single composition entrypoint.

---

## What it contains conceptually

A Federation Manifest typically records:

- federation identity;
- shard references;
- shard scopes;
- authority channel references;
- validation report references;
- authority recognition references;
- reader policy references;
- validation policy references;
- composition policy;
- trust requirements;
- publisher signatures;
- optional conflict summaries.

---

## Conflict strategy

Kristal v5’s default federation strategy is:

```text
preserve_disagreement
```

This means a federation may contain multiple claims or positions about the same topic when their authority, certainty, validation status, or scope differs.

Reader policies decide which material is visible.

---

## Relationship to other artifacts

- **Shard Manifest**: referenced by the federation.
- **Authority Registry**: defines which authority channels are acceptable.
- **Validation Report**: records validation findings for shards or the federation.
- **Reader Policy**: selects which federated material is visible.

---

## Technical details

- Schema: `kristal-docs-v5/02-schemas/exchange-federation-manifest.schema.json`
- Example: `kristal-docs-v5/10-examples/exchange-federation-manifest.example.json`
- Overview: `kristal-docs-v5/00-overview/sharding-and-federation.md`
