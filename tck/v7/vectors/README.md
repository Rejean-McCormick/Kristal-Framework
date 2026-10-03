# v7 test vectors

The fixtures in this directory exercise the draft v7 meta-artifact schemas and the backward-compatible projection contract.

A conforming validator should verify:

1. each v7 example against its corresponding v7 schema;
2. `v6-compatible-projection.example.json` against the unchanged v6 `kristal-state.schema.json`;
3. its `extensions.kristal_v7` object against `kristal-v7-extension.schema.json`;
4. the projection recipe contains no more than one primary and one secondary orientation axis;
5. source v6 canonicalization remains outside the v7 meta hash contract.

Draft.2 adds semantic identity registries (`KQ/KP/KA/KS`) and the shared `semantic_resonance_set` test vector.
