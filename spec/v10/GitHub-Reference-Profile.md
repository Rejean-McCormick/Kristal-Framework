# GitHub Reference Host Profile

Profile identifier: `kristal.host/github/1.0`.

The GitHub profile maps v10 hosted-network concepts to GitHub primitives while leaving semantic state independent of GitHub.

| Kristal concept | GitHub realization |
| --- | --- |
| account-wide integration | `.github` repository, workflow templates, profile/community defaults |
| node host | repository |
| proposal | pull request |
| deterministic qualification | Actions / checks |
| immutable publication | release + assets |
| materialization distribution | release assets and/or GHCR |
| build/publication witness | artifact attestations |
| activation surface | deployment/environment |
| operational metadata | repository custom properties (organization mode) |
| directory/root | dedicated Kristal directory repository |

The profile does not require every optional GitHub feature. Plan-dependent features MUST degrade explicitly rather than changing semantic behavior.

The normative GitHub binding schema is `profiles/github/schemas/kristal-github-binding.schema.json`.
## Reference account topology

The reference bootstrap uses two GitHub configuration levels:

1. **Account/organization level** — a public `.github` integration repository, an optional `.github-private` member profile for organizations, a private root Kristal directory, and optional organization custom properties.
2. **Node/repository level** — `.kristal/node.json`, a GitHub host binding, capabilities, qualification/publication workflows, and optional GitHub protection/publication features.

A conforming GitHub deployment containing confidential nodes SHOULD keep the authoritative all-node directory private. It SHOULD contain at least one public and one private collection when both publication classes are intended. Additional collection or directory repositories MAY be added without changing the semantic-state commitment rules.

The framework used by generated public-repository workflows MUST be readable from those workflows without embedding reusable credentials. The reference bootstrap therefore requires a public framework repository whenever public Kristal nodes use the default cross-repository checkout mechanism.



## Draft.2 managed workflow profile

The managed bootstrap profile pins the framework and external Actions to full commit SHAs. Qualification runs read-only and emits a receipt bound to the candidate commit and framework commit. Publication treats the state path as untrusted data, builds a verifiable publication bundle, creates a draft Release targeted at the exact candidate commit, re-downloads and verifies the bundle, and only then finalizes the Release.

`best_effort` host features are not equivalent to required guarantees. In particular, an optional Environment may be created for observability without being referenced as an approval gate; only `required` Environment mode is emitted as a publication job environment.
