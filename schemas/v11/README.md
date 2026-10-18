# v11 additive schemas

`kristal-identity-registry`, `kristal-semantic-graph`, `kristal-lexical-dictionary`, `kristal-external-crosswalk` and `kristal-legacy-resolution-requests` are strict **new** contracts. They do not change the v7 entity registry or v8 lexicon schemas. Shape validation alone is insufficient: run `tools/v11/validate_v11.py` for identity and mapping invariants.

Draft.2 adds `kristal-dictionary-catalog`, `kristal-wikidata-lexical-record` (JSONL lines) and `kristal-curated-dictionary` (reviewed human additions/overrides). These do not replace the v11 basic lexical dictionary schema. Use `tools/v11/dictionaries.py audit` for layer digests, namespace and source-record validation.


Draft.3 adds typed third-party `external` catalog layers with provenance and approved KQ/KP alignment (`kristal-external-lexical-record`), plus `kristal-dik-coverage-report` (graph × language metrics) and `kristal-dik-conversion-plan` (read-only approval record). Use `tools/v11/dik_coverage.py` to compute and audit coverage, and `tools/v11/dik_conversion_plan.py` to verify plans and source digests. The latter **never executes edits**. See `spec/v11/diK-Interoperability.md`.
