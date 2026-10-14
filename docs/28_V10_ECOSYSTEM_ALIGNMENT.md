# v10 ecosystem alignment — implementation guide (informative)

This page records the **implementation boundaries and acceptance gates** for the GitHub reference profile. It is not a new normative contract, a qualification receipt, or an authorization to publish.

**Current proposed baseline:** `10.0.0-draft.3.2` (`draft`). Its v9 semantic-state model and commitment profiles are unchanged. The exact Framework Git commit and `contracts/contract-set.json` digest used by each downstream component must be recorded and independently verified; a version label alone is not a pin.

## Responsibility and contract matrix

| Responsibility | Owner | Contract / interface | Acceptance boundary |
| --- | --- | --- | --- |
| Semantic model, normative conformance, compatibility | Kristal Framework | `contracts/release.json`, `contract-set.json`, v9/v10 TCK | No silent edits to frozen compatibility locks or commitment algorithms |
| Local authoring and derived read surface | Authoring Kit | `kristal.github-read-surface/1.0` | Only exact validated files; `ready` and source provenance must be explicit |
| Independent candidate qualification | KristalDiag / C1 | Qualification receipt (candidate until adopted) | Must bind the exact candidate, operation and revision; no self-attestation |
| Human policy / hosting bootstrap | Bootstrap / C2 | Scope-limited authorization (candidate until adopted) | Separate signers, validity, destination, visibility, and revocation checks |
| Workspace inventory and read-surface sync | Kristal Manager | `kristal.github-sync-manifest/1.0`, `kristal.github-collection-index/1.0` | Verify byte digests, allowlist and authorized destination *before* remote writes |
| Hosted collection and immutable publication | GitHub host / C3 | v10 node, binding, collection index and release artifacts | C3 integrity alone does not replace independent C1/C2 evidence |
| Read-only navigation and contextual consumption | Konstellation / Kompiler | Verified index, read surface, Reader Policy | A hosted topology is not generic decoding of domain-native v9 concepts |
| Archetype design library | Arketype | Non-normative templates and metadata | Not an authoritative inventory or hosted domain state |
| Legacy registers | Kristal-Kollection | Archived source-specific registry | A legacy registry entry does not establish a hosted v10 state |

## Lifecycle separation and the public-sync boundary

```text
LOCAL BUILD != INDEPENDENT QUALIFICATION != HOSTING SYNC
HOSTING SYNC != IMMUTABLE PUBLICATION != ACTIVATION
READ SURFACE != CANONICAL SEMANTIC STATE
GIT SHA != STATE COMMITMENT != BYTE SHA-256
```

A **sync to a public GitHub repository exposes bytes immediately**, even if no immutable Kristal publication has occurred. Implementations must perform an owner-approved scope and visibility check, and verify required C1/C2 evidence, *before* the first public upload, commit, pull request containing sensitive content, or sync operation. Renaming this action “staging” or “ingestion” does not remove that disclosure risk. Private hosts require their own access controls; no Framework document grants permission to publish any individual Kristal.

A missing or incomplete `kristals/index.json` may represent a collection not yet materialized. The reference verifier can return a structural `not-yet-created` status for that case. **This is not collection qualification.** A deployment intending to serve a verified collection must require a present, valid index and exact per-Kristal sync manifests. Refuse stale hashes, missing files, altered commitments, unauthorized visibility, unverified grants, and unknown trust roots.

## Version and integration verification

From an exact checkout:

```bash
python tools/check_v10_ecosystem_alignment.py --json
python tools/validate_all.py
```

The first command checks **Framework-local** version, profile schema and contract-set consistency. Its explicit `external_consumers` status is `NOT_EVALUATED`; it does not contact GitHub or imply that Manager, C1, C2, C3, Kompiler or Konstellation is deployed or mutually qualified. The second command runs native validation and conformance tests.

Before claiming end-to-end alignment, produce evidence for the **same** `state_ref`, State Commitment, read-surface digest, collection index and exact GitHub revision across an authorized, nonsensitive pilot. Validate user-facing privacy (including hidden names, counts and facets), expiry/revocation, and reproducible rollback. Keep the Framework in `draft` until a separate standards release decision is made.

## Host/profile interoperability status

- **Implemented and checked locally:** Framework v10 schemas, JS reference verifiers, v9 compatibility and the in-repository GitHub profile tests.
- **Documented interfaces:** Authoring Kit 3.2.4+ read surfaces; Manager synchronization; Bootstrap hosting; C1/C2/C3 gates; Konstellation/Kompiler consumption.
- **Not established by this repository:** live GitHub host readiness, a complete Manager checkout, independent qualification receipts, deployment permissions, published releases, or a full cross-repository pass.

Further work on a normative profile **must** be proposed in `spec/v10/`, schema, reference implementation and TCK together, with an explicit compatibility decision. Do not silently turn design guidance into new canonical rules.

The optional `kristal.discovery/1.0` reader-profile extension in draft.3.2 is locally validated but is not a claim of Manager, Bootstrap, Kompiler or simdjson end-to-end compatibility.
