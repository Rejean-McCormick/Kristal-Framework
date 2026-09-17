# Changelog

All notable changes to the Kristal Framework contract set are recorded here.

## 5.0.0-rc.2 — release-integrity and identity-boundary corrections

### Corrected

- retired the stale per-file `schema-set.manifest.json` release model and legacy `tools/build_manifests.py` generator;
- made canonicalization profile **and version** explicit in framework release metadata and downstream lock examples;
- hardened JSON Schema example validation to enforce declared `format` constraints;
- made format validation fail closed by requiring `jsonschema[format-nongpl]` and probing active `date-time`/`uri` enforcement before repository example validation;
- changed source release archives to use Git-tracked files only and exclude local snapshot metadata;
- clarified that Exchange content identity is independent of compiler/build-run identity while build provenance remains recorded separately;
- aligned Reference Exchange lifecycle rules with authority-recognition requirements;
- aligned Runtime Pack format version examples on `5.0.0` and distribution artifact type on `runtime_pack_manifest`;
- expanded CI to validate on Linux and Windows;
- aligned Runtime Pack policy enums/required parameters between the normative policy document and JSON Schema;
- added `kristal.v5:runtime-pack-portable-conformance@1` with exact RP-2 ordering, RP-3 row-group, RP-4 KBF1 Bloom, and RP-5 canonical Roaring portable bytes;
- added executable golden vectors for RP-2 through RP-5.

### Qualification

- rc.2 remains a candidate until the complete framework gate passes and the release commit/tag exist;
- compiler/verifier implementation conformance, cryptographic signature vectors, and full EX/RP cross-implementation proof remain separate promotion gates.

## 2026-09-16 — executable conformance suite

- Added Exchange identity and Runtime Pack identity/integrity golden vectors.
- Added `tools/kristal_tck.mjs`, `tools/validate_conformance.py`, and `tools/validate_all.py`.
- Added the `kristal.v5:runtime-pack-id-core@1` TCK identity profile.
- Added explicit PASS/NOT TESTED separation between framework-vector and implementation conformance.
- Corrected stale v3 wording in the v5 reproducibility acceptance criteria.
- Made the full validation suite the GitHub Actions conformance gate.

## Unreleased — operational/Kristal materialization boundary clarification

### Clarified

- Kristal is the portable epistemic artifact layer, not a shared mutable application database.
- Product-owned operational state remains authoritative in the owning product; Kristal ingestion uses immutable source snapshots/artifact references with provenance.
- In the kOA deployment profile, Da’at is the mapping boundary from source-owned artifacts into Kristal-native epistemic structures; Interaction Kernel transports references/requests but owns neither operational state nor Kristal storage.
- Runtime Packs may contain deterministic query-oriented materializations, but those materializations are derived, immutable for a build identity, non-authoritative, and rebuildable from declared Kristal inputs.
- Core v5 does not standardize a writable SQLite/application-database profile. A future database-like Runtime Pack representation requires an explicit profile and must remain read-only/derived unless a future normative contract states otherwise.

### Compatibility

This clarification does not change the published JSON Schemas or the Kristal v5 epistemic model.

## 5.0.0-rc.1 — stabilization release candidate

### Added

- machine-readable release identity (`kristal-release.json`);
- curated contract-surface index (`contract-set.manifest.json`);
- explicit normativity classification;
- release validation tooling and CI gates;
- MkDocs navigation aligned to the actual v5 documentation tree;
- release and pinning guidance for downstream consumers.

### Simplified

- Git tag + commit SHA are the authoritative immutable release identity;
- removed generated per-file release hashes and exhaustive schema/file manifests;
- release validation checks contract surfaces and conformance, not a byte-for-byte repository inventory;
- annotated Git tags are the default release mechanism; signed tags remain optional.

### Fixed

- v4 wording remaining in the v5 reproducibility acceptance-test document;
- Claim-IR example fields that did not conform to the published v5 Claim-IR schema;
- obsolete MkDocs paths and placeholder repository URL.

### Compatibility

This stabilization release does not intentionally change the Kristal v5 epistemic model. It formalizes the existing v5 contract surfaces for release and downstream pinning.
