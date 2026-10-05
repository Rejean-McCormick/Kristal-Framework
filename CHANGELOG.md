## Unreleased — 2026-10-04

- adds the informative `kristal-desktop/1.0` Windows folder-binding convention;
- standardizes `InfoTip` as `NAME • NATURE • DOMAINS • MATURITY • VOLUME`, targeting a compact 120–180 character human summary;
- defines a machine-readable `[Kristal]` `desktop.ini` section as a regenerable local cache, never semantic authority;
- adds the informative `kristal-icon/1.0` presentation profile: domain band + nature pictogram + maturity;
- standardizes nature codes `REF`, `COL`, `MOD`, `PRT`, `TWN`, `INV`, `SRC`;
- fixes the central pictogram color to `#1e6864` in the reference renderer;
- standardizes Windows multi-resolution ICO output at 16, 20, 24, 32, 40, 48, 64, 96, 128 and 256 px;
- standardizes deterministic names as `KR-{NATURE}-{DOMAIN...}-M{0..5}.ico`;
- adds a browser-only reference icon generator under `tools/icons/`;
- keeps icon metadata and generated images explicitly outside semantic identity and canonical authority.

## 8.0.0 — 2026-10-03

Finalized v8 as an additive capability standard over unchanged v6/v7 semantics.

- finalized external composable Language Layer with BCP 47 locale handling;
- finalized typed KQP query scope/traversal, budgets, pagination and continuation semantics;
- added explicit result completeness and partial-result rules;
- replaced bucket-first AI context selection with semantic atoms and optional compact symbol tables;
- standardized semantic-fingerprint vs byte-hash distinction;
- added AI trust boundaries: model-as-untrusted-planner, provenance-aware context and layered validation;
- incorporated read-model/CQRS, anti-corruption, sharding/federation, claim-check and graceful-degradation principles where they affect the standard;
- preserved the v6/v7 compatibility lock unchanged at the inherited machine surfaces.
- upgraded the zero-dependency JavaScript reference runtime to execute local v8 Reader, Language, exact KQP Query, AI Context and Integrity behavior while preserving v6/v5 compatibility tests;

## 8.0.0-draft.1 — 2026-10-03

- Adds a **Language Layer** with external composable lexical Kristals, lexicon stacks, deterministic precedence, explicit missing/conflict states, and a non-normative lexical-delta generator.
- Establishes `SEMANTICS != LANGUAGE`, `LEXICON != SEMANTIC AUTHORITY`, and `MISSING LEXICALIZATION != MISSING MEANING` as v8 invariants.
- Adds the **Kristal Query Protocol (KQP)** for exact semantic query, evidence closure, graph traversal, semantic slices, cross-Kristal query and explicit query plans.
- Adds rebuildable non-authoritative query-index contracts and token-budgeted AI context bundles.
- Establishes `QUERY INDEX != SOURCE OF TRUTH`, `FUZZY DISCOVERY != SEMANTIC ANSWER`, `AI CONTEXT != CANONICAL STATE`, and `OMISSION BY BUDGET != NEGATION`.
- Keeps `kristal_state/6.0` unchanged as the portable contract and the v7 KQ/KP/KA/KS model unchanged as the semantic baseline.
- Adds a v8 compatibility lock that verifies inherited v6/v7 machine contracts and v7 TCK vectors remain byte-identical in this draft.
- Existing v7 human labels remain valid compatibility/display fallbacks; v8 does not require rewriting existing v7 artifacts.

# Changelog

## 7.0.0-draft.3.2 — 2026-10-03

- Normalizes the human-facing integration name to **DaaT** and preserves `daat` as the machine identifier.
- Defines DaaT as an optional external IK anti-corruption/admission and explicit contract-mapping boundary, not as part of Kristal/Kristall semantic authority.
- Explicitly excludes source acquisition/storage, general corpus normalization, operational-state ownership, and KQ/KP/KA/KS minting or crystallization authority from DaaT.
- Keeps `kristal_state/6.0` unchanged as the portable interchange contract beneath Kristall v7.
- Adds the DaaT boundary to the v7 documentation/navigation and strengthens the v7/v6 compatibility rule for external adapters.
- No v6 or v7 JSON Schema shape changed in this draft.

## Repository consolidation — 2026-10-02

- Consolidates `Kristal-Standard`, `kristal-framework`, and `kristal-reference` into one monorepo.
- Establishes canonical `spec/`, `schemas/`, `tck/`, `reference/`, and `tools/` ownership boundaries.
- Promotes the Standard snapshot `7.0.0-draft.3.1` as the active baseline.
- Removes active v5/v6 documentation duplication between Standard and framework.
- Moves the JavaScript reference implementation under `reference/js` and rewires its tests to canonical monorepo assets.

## 6.0.0 — 2026-10-01

- Makes `kristal_state` (`schema_version: 6.0`) the canonical v6 artifact.
- Replaces the single universal certainty assumption with typed `valuations[]`.
- Adds explicit `coordinates`, `applicability`, `record_role` and `actionability` semantics.
- Defines value semantics for boolean, categorical, set, ordinal, scalar, interval, probability, distribution, vector, partial order, state and temporal values.
- Separates non-known value states (`unknown`, `not_applicable`, `indeterminate`, `not_measured`) from actual values.
- Formalizes preservation of human/AI work as cumulative structured memory.
- Formalizes automation boundaries without treating actionability as execution authority.
- Adds the v6 core specification, JSON Schema and conformance fixture.
- Retains the complete v5 specification and contract surfaces as legacy compatibility material.
- Keeps `knowledge-model-contract.v1.json` frozen for v5 and introduces `knowledge-model-contract.v2.json` for v6.

## 5.0.0-rc.3 — 2026-09-28

- Freeze Referent Registry 1.0.0.
- Keep domain classification shallow and assertions/provenance in Structured Epistemic State.
- Explicitly separate internal refs from external identifiers such as Wikidata.
- Distinguish work, edition and manifestation for documentary projections.

# Changelog

## Unreleased — 2026-09-24

- Document dogma as a source-backed, scoped content classification using existing assertions and qualifiers.
- Add a synthetic schema-valid example and positive/negative release validation coverage.
- Keep all core schemas, enums and release identifiers unchanged; this archive is a modified working snapshot, not a newly published official release.


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
- In the kOA deployment profile, DaaT is the mapping boundary from source-owned artifacts into Kristal-native epistemic structures; Interaction Kernel transports references/requests but owns neither operational state nor Kristal storage.
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
