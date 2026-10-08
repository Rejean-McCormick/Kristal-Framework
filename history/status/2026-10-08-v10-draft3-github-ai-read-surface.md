# Kristal v10.0.0-draft.3 — GitHub AI/read-surface alignment

Draft.3 is an additive hosted-network/profile update. It does not change v9 logical artifacts, State Snapshots or commitment algorithms.

It formalizes the GitHub operational contracts already used by the toolchain:

- `kristal.github-read-surface/1.0`;
- `kristal.github-sync-manifest/1.0`;
- `kristal.github-collection-index/1.0`.

The reference CLI can verify those documents and can verify a hosted `kristals/<slug>/` subtree or an entire collection. The GitHub collection index is explicitly a derived navigation surface, not semantic authority. The bundled GitHub Bootstrap is aligned to 1.1.0-alpha.10.
