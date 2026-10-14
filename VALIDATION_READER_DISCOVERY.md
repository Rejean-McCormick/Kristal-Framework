# Validation — draft.3.2 Reader Discovery

Build date: 2026-10-13. Scope: read-only local validation, no live hosted integration.

- Full `python tools/validate_all.py`: **PASS** (including unchanged v9/v10 compatibility locks, v6–v9 vectors, contract bundle, link/nav checking, JS tests, 38 GitHub Bootstrap tests).
- `node reference/js/tests/run_reader_discovery_tests.mjs`: **15 tests PASS**, including matching Kit 3.3.0 fixture, JSON versus JSONL planning, type fallback, path escape, symlink, size/digest drift, missing metadata, encryption and compression.
- `python tools/check_reader_discovery_profile.py`: **PASS**, validating the three example files against mirrored Kit schemas and local fixture bytes.
- `python tools/check_v10_ecosystem_alignment.py`: **PASS** for local contract references. No external Manager/Bootstrap/Kompiler integration or simdjson execution asserted.
- Frozen v9 semantic contracts and historical compatibility locks untouched. Version label has advanced to `10.0.0-draft.3.2` for this optional operational addition.

**Limitations:** The inspector cannot independently regenerate the Local Kit's source-input fingerprint; Kit `check` should validate freshness. It does not parse domain payloads, detect actual compression format, enforce external authorization or implement simdjson. Measured sizes cover registered local bytes only. This test report is not publication approval or epistemic certification.
