# v10 status

- Proposed Standard version: `10.0.0-draft.3.1`
- Architecture name: **Hosted Kristal Network Architecture**
- Semantic-state baseline: unchanged Kristal v9
- Compatibility baseline: v6 + v7 + v8 + v9
- First host profile: `kristal.host/github/1.0`

V10 adds node manifests, host bindings, publication records and directories. It explicitly preserves v9 commitments so moving a Kristal between repositories or hosts is not a logical revision.

The first implementation target is a GitHub-hosted network with account-level bootstrap plus per-repository bootstrap for public/private collections and a root directory.

Draft.3 additionally standardizes GitHub AI/read-surface verification and collection indexes for high-scale hosted traversal without changing v9 semantics.

## Implementation alignment status

This repo's Framework-local GitHub read-surface, sync-manifest and collection-index contracts are checked by `python tools/check_v10_ecosystem_alignment.py --json` and the native conformance suite. The result is not cross-repository qualification. See [v10 ecosystem alignment](28_V10_ECOSYSTEM_ALIGNMENT.md). The proposed Standard **remains draft.3.1** until a separate standards decision.
