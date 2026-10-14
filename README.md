# Kristal

**Current standard baseline:** `10.0.0-draft.3.2`

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
