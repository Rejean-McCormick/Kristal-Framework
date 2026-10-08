# v10 status

- Proposed Standard version: `10.0.0-draft.2`
- Architecture name: **Hosted Kristal Network Architecture**
- Semantic-state baseline: unchanged Kristal v9
- Compatibility baseline: v6 + v7 + v8 + v9
- First host profile: `kristal.host/github/1.0`

V10 adds node manifests, host bindings, publication records and directories. It explicitly preserves v9 commitments so moving a Kristal between repositories or hosts is not a logical revision.

The first implementation target is a GitHub-hosted network with account-level bootstrap plus per-repository bootstrap for public/private collections and a root directory.
