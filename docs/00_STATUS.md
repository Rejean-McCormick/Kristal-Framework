# Active draft: v11

- Proposed Framework version: `11.0.0-draft.4`
- Additive canonical KQ/KP/KA/KS graph, lexical dictionaries and external Wikidata crosswalk
- Draft.2: versioned dictionary catalog (300+ sparse locales), immutable Wikidata source layers, reviewed curated layers, snapshot/hash provenance and offline reference importer/auditor
- Draft.3: diK interoperability profile, third-party dictionary provenance, per-Kristal multilingual coverage and read-only conversion plans.
- Draft.4: read-only diK alpha.7 / Authoring Kit draft.3 catalog preflight, updated toolchain handoff docs and aligned wiki; normative v11 schema and TCK bytes still draft.3.
- Historical v10 baseline below is preserved; local v11 test pass does not qualify other repositories or deployed collections.

---

# v10 status

- Proposed Standard version: `10.0.0-draft.3.2`
- Architecture name: **Hosted Kristal Network Architecture**
- Semantic-state baseline: unchanged Kristal v9
- Compatibility baseline: v6 + v7 + v8 + v9
- First host profile: `kristal.host/github/1.0`

V10 adds node manifests, host bindings, publication records and directories. It explicitly preserves v9 commitments so moving a Kristal between repositories or hosts is not a logical revision.

The first implementation target is a GitHub-hosted network with account-level bootstrap plus per-repository bootstrap for public/private collections and a root directory.

Draft.3 additionally standardizes GitHub AI/read-surface verification and collection indexes for high-scale hosted traversal without changing v9 semantics.

## Implementation alignment status

This repo's Framework-local GitHub read-surface, sync-manifest and collection-index contracts are checked by `python tools/check_v10_ecosystem_alignment.py --json` and the native conformance suite. The result is not cross-repository qualification. See [v10 ecosystem alignment](28_V10_ECOSYSTEM_ALIGNMENT.md). This updated release is **draft.3.2**, an optional reader-discovery addition; it is not a final standard or cross-tool certification.

Draft.3.2 adds [Reader Discovery](29_READER_DISCOVERY_INTEGRATION.md) as a noncanonical companion with unchanged v9 commitments and historical compatibility locks.
