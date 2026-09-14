# Changelog

All notable changes to the Kristal Framework contract set are recorded here.

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
