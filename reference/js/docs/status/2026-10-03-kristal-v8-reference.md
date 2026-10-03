# 2026-10-03 — JavaScript reference runtime upgraded to Kristal v8

The zero-dependency JavaScript reference runtime now implements local v8 Reader, Language, exact KQP Query, AI Context and Integrity behavior while retaining v6 portable-state and v5 compatibility paths.

Added runtime modules:

- `src/v8/common.mjs`
- `src/v8/reader.mjs`
- `src/v8/lexicon.mjs`
- `src/v8/query_index.mjs`
- `src/v8/query.mjs`
- `src/v8/ai_context.mjs`
- `src/v8/capabilities.mjs`

Added `tests/run_v8_tests.mjs` and v8 CLI operations for artifact inspection, lexical resolution, semantic fingerprints, exact query, derived index construction and AI-context compilation.

Remote federated-shard transport remains outside the reference runtime and is advertised as unsupported rather than simulated.
