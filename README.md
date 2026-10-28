# Kristal Framework v11 — draft.4

**Active draft:** `11.0.0-draft.4` — Canonical Semantic Identity & Lexical Separation.

The v11 strict semantic graph uses only namespace-scoped **KQ / KP / KA / KS** identities; translations are in separate lexical dictionaries, and Wikidata **Q / P** identifiers remain in a versioned external crosswalk. The non-destructive resolver proposes mappings for explicitly selected legacy words; it does **not** rewrite old Kristals or mint identities automatically.

[Read the v11 specifications](spec/v11/Home.md) | [Conformance](spec/v11/Conformance.md) | [Wikidata crosswalk](spec/v11/Identity-and-Wikidata.md) | [300+ language dictionary management](spec/v11/Dictionary-Management.md) | [diK interop profile](spec/v11/diK-Interoperability.md) | [UNESCO subject classification (companion)](profiles/unesco/README.md) | [diK/Kit v11 handoff](docs/30_DIK_AUTHORING_KIT_HANDOFF.md)

```bash
python tools/validate_all.py
python tools/v11/validate_v11.py
python tools/v11/dictionaries.py audit --catalog examples/v11/dictionaries/catalog.json --crosswalk examples/v11/external-crosswalk.example.json --registry examples/v11/identity-registry.example.json
python tools/v11/dictionaries.py resolve --catalog examples/v11/dictionaries/catalog.json --id KQ1001 --locale fr-CA
python tools/v11/dik_coverage.py --graph examples/v11/semantic-graph.example.json --registry examples/v11/identity-registry.example.json --crosswalk examples/v11/external-crosswalk.example.json --catalog examples/v11/dictionaries/catalog.json --locales fr,en,fr-CA
python tools/v11/interop_preflight.py --catalog examples/v11/dictionaries/catalog.json --registry examples/v11/identity-registry.example.json --crosswalk examples/v11/external-crosswalk.example.json --graph examples/v11/semantic-graph.example.json --locales fr,en,fr-CA
python tools/v11/dik_conversion_plan.py --plan examples/v11/dik-conversion-plan.example.json --registry examples/v11/identity-registry.example.json --source examples/v11/dik-legacy-sample.json
python tools/v11/resolve_legacy.py --requests examples/v11/legacy-resolution-requests.example.json --lexicon examples/v11/lexicon-fr.example.json --crosswalk examples/v11/external-crosswalk.example.json
```

**Companion update (2026-10-28, non-normative):** local subject classification and Icon Generator integration use only the pinned UNESCO Thesaurus 7-domain / 88-microthesaurus reference; Arketype continues to describe structure/usage separately. Historical ISCED-F identifiers are not migrated into UNESCO codes. `profiles/unesco/` contains the optional mapping schema, examples and a read-only checker; this does not modify v11 schemas, TCK, commitments or any Windows folders. The Manager folder-icon opt-in remains **off by default**.

**Draft.4:** adds a *read-only* diK alpha.7 / Authoring Kit draft.3 catalog preflight and aligned integration docs/wiki. **All v11 semantic schemas and TCK fixtures remain byte-identical to draft.3.** No cross-repository or full-dump certification is implied.

Draft.2 adds file-backed, versioned dictionary catalogs, layered Wikidata import/curation, offline import/audit/lookup tools and reference tests. Draft.3 additionally provides typed third-party dictionary layers, graph-specific direct/fallback/missing coverage, and a non-executable reviewed conversion-plan contract for diK. **The diK app itself and an approved migration executor are not included.** This is **not** a certified 300-language production service or an online dump downloader.

All v6–v10 normative schemas, historical TCK fixtures and original commitment profiles remain preserved. **v11 is an additive draft**, not an assertion that the Local Authoring Kit, hosted consumers or legacy Kristals have been migrated. The bundled tests provide Framework-local evidence only.

---

# Kristal

**Historical v10 baseline:** `10.0.0-draft.3.2`

Kristal is a portable, deterministic knowledge-state standard. **Kristal v10 — Hosted Kristal Network Architecture** preserves the frozen v6 portable epistemic state, v7 semantic identity model, v8 language/query layer, and v9 Semantic State Architecture while adding portable node discovery, host bindings, publication records, directories and host profiles.

## v10 in one sentence

```text
v6 epistemics + v7 identity + v8 language/query + v9 semantic state + v10 hosted network
```

## Core v10 rule

```text
SEMANTIC STATE != HOSTING != PUBLICATION LOCATION != DISCOVERY DIRECTORY
```

V10 deliberately keeps v9 logical artifacts, state snapshots and commitment profiles unchanged. GitHub is the first reference host profile (`kristal.host/github/1.0`), not a dependency of semantic identity.

## New v10 surfaces

```text
.kristal/node.json              -> node identity and roles
.kristal/bindings/*.json        -> replaceable host bindings
kristal_publication             -> exact state -> retrievable host resources
kristal_directory               -> discovery/routing across many nodes
```

A large deployment can therefore use many repositories/collections and a root directory without making repository layout part of the knowledge commitment.

## Validate

```bash
python tools/validate_all.py
cd reference/js && npm test
node bin/kristal-ref.mjs v10-capabilities
```

Start with [v10 Home](spec/v10/Home.md), the [Core Specification](spec/v10/01-core-spec/kristal-v10-core-spec.md), and the [GitHub Reference Profile](spec/v10/GitHub-Reference-Profile.md).

## GitHub bootstrap

The companion one-time account/repository bootstrap is bundled under [`tools/github-bootstrap/`](tools/github-bootstrap/README.md). It manages account-wide GitHub integration, a private root directory, initial public/private Kristal collections, and later one-time initialization of additional Kristal repositories.


## Draft.3.1 compatibility-fixture correction

Draft.3.1 is a maintenance correction. It fixes the declared v6 `state_id` / `content_hash` in the v7 portable projection fixture after independently recomputing the v6 JCS identity with `extensions.kristal_v7` present. No v6/v7/v8/v9 semantic rule or v9 commitment algorithm changes. The historical compatibility locks are preserved byte-for-byte; the correction is recorded explicitly in `contracts/compatibility-errata.json`.

## Draft.3 GitHub AI/read surfaces

The GitHub reference profile now standardizes the operational contracts used by Local Kit 3.2.4+, Manager alpha.11+ and Bootstrap alpha.10+ for efficient AI traversal of large collections: exact per-Kristal read surfaces, sync manifests and a compact collection index. These are derived host surfaces and do not alter v9 semantic commitments.

## Ecosystem alignment and qualification boundaries

[The v10 alignment guide](docs/28_V10_ECOSYSTEM_ALIGNMENT.md) records the Framework/Authoring Kit/Manager/Bootstrap/C1/C2/C3 reader contracts and explicit publication gates. Check Framework-local versions and schema/profile consistency with:

```bash
python tools/check_v10_ecosystem_alignment.py --json
```

This reports only **local contract consistency**. It does not check live GitHub collection readiness or authorize any sync, release or activation. A public GitHub sync already discloses the uploaded bytes and requires authorization **before** remote writes.

## Draft.3.2 — Arketype / Reader Discovery companion profile

The optional [Reader Discovery Profile](spec/v10/Reader-Discovery-Profile.md) mirrors Local Authoring Kit 3.3.0 discovery, inventory and reader-hint schemas. [A JS reference inspector](profiles/reader-discovery/README.md) validates the metadata triple and, with `--verify-files`, local tracked file size and SHA-256. It produces a **non-executable** parser plan (including JSON versus JSONL), defaults unknown profiles to generic and leaves simdjson implementation to a separately authorized reader. No v9 commitments or hosted-publication rights change. See [the French integration guide](GUIDE_INTEGRATION_DISCOVERY_FR.md).
