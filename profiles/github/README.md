# GitHub host profile

Profile: `kristal.host/github/1.0`.

The host binding remains the normative bridge between a Kristal v10 node and a GitHub repository. Draft.3 adds three **operational reader/ingest contracts** used by Local Kit, Manager and the GitHub collection workflow:

- `kristal.github-read-surface/1.0` — exact derived file projection intended for efficient GitHub/AI traversal;
- `kristal.github-sync-manifest/1.0` — hosted ownership/integrity manifest for one `kristals/<slug>/` subtree;
- `kristal.github-collection-index/1.0` — derived collection navigation index for thousands of hosted Kristals.

These contracts are host/read projections. They MUST NOT alter v9 Logical or State Commitments, and sync MUST NOT be treated as v10 Publication or v9 Activation. Materialization bytes may use Git, Releases, GHCR, LFS or another locator according to host policy; they are not implicitly forced into the Git tree.

Schemas are under `profiles/github/schemas/`.
