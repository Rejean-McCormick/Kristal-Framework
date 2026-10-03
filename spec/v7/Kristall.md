# Kristall

Kristall is the encyclopedic knowledge space and meta-orchestrator introduced by v7.

## Logical components

A Kristall implementation normally maintains:

- source Kristal registry;
- canonical entity registry;
- entity-resolution candidate ledger;
- assertion families;
- subject regions;
- Mesh shards/indexes;
- orientation axis registry;
- crystallization ledger;
- projection recipes/catalog;
- optional vector/search indexes;
- provenance and validation references.

## Not monolithic

`kristall_manifest` is the root descriptor. Large deployments SHOULD shard registries and Mesh data. The logical Kristall can therefore scale without requiring one giant document.

## Encyclopedia, not oracle

Kristall is encyclopedic because it can traverse and project a large corpus. It MUST preserve incompatible assertions, unresolved identity candidates, source boundaries and temporal scope. It is not allowed to manufacture one globally authoritative answer merely because it contains many sources.
