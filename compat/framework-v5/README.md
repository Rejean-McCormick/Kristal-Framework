# Frozen v5 compatibility note

The retained `knowledge-model-contract.v1.json` pins a historical `contract-set.manifest.json` of 2628 bytes with SHA-256 `b29573d9241900096188880e066e5c5fbe1decd34ff56260d6e4eb0def7baf3c`. That exact payload is not present in the three supplied source snapshots used for this consolidation.

The monorepo therefore preserves the v1 contract and verifies its own bundle identity, but does **not** fabricate or substitute the missing historical contract-set payload. Current v5 specification/vector material is preserved under `spec/v5/`.
