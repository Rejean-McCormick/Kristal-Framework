# Changelog

All notable changes to the Kristal Framework contract set are recorded here.

## 5.0.0-rc.1 — stabilization release candidate

### Added

- machine-readable release identity (`kristal-release.json`);
- deterministic contract-set and schema-set manifests with SHA-256 digests;
- explicit normativity classification;
- release validation tooling and CI gates;
- MkDocs navigation aligned to the actual v5 documentation tree;
- release and pinning guidance for downstream consumers.

### Fixed

- v4 wording remaining in the v5 reproducibility acceptance-test document;
- Claim-IR example fields that did not conform to the published v5 Claim-IR schema;
- obsolete MkDocs paths and placeholder repository URL.

### Compatibility

This stabilization release does not intentionally change the Kristal v5 epistemic model. It formalizes the existing v5 contract set for reproducible release and downstream pinning.
