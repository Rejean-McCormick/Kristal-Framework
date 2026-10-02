# Kristal Standard 6.0 specification status

**Active baseline:** `6.0.0`.

Kristal Standard v6 makes `kristal_state` the canonical structured artifact and introduces typed valuations, explicit record roles and explicit actionability boundaries.

## Normative v6 surfaces

- `01-core-spec/kristal-v6-core-spec.md`
- `02-schemas/kristal-state.schema.json`
- `09-test-vectors/kristal-state/`
- root release metadata (`VERSION`, `kristal-release.json`, `contract-set.manifest.json`)

The reference adapter snapshot supplied with the v6 work uses the same semantic enums and the same canonicalization profile.

## Legacy compatibility

The complete v5 technical reference remains under `../kristal-docs-v5/`. Its SES/Exchange/Runtime Pack contracts are retained for migration and old consumers; they do not define the v6 canonical state.

## Breaking semantic changes

The main migration is semantic, not a blind field rename:

- SES → `kristal_state`;
- `certainty_level` / `uncertainty` → typed `valuations[]`;
- `qualifiers` → `coordinates`;
- `scope` → `applicability`;
- implicit information kind → optional `record_role`;
- implicit automation assumptions → explicit `actionability`.

See [Migration v5 → v6](../Migration-v5-to-v6.md).
