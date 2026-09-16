# Kristal v5 specification status

**Candidate version:** `5.0.0-rc.2`  
**Candidate Git tag:** `v5.0.0-rc.2` — pending until release  
**Candidate resolved commit:** pending until the release tag exists  
**Core schema line:** `5.0`  
**Canonicalization profile:** `kristal.v5:jcs-rfc8785` / version `1`

## Purpose

This file defines the release and normativity boundary for the Kristal v5 framework. It does not change the epistemic model. It makes the existing v5 contract set releasable, pinnable, testable, and immutable once published.

## Normativity classes

| Class | Meaning |
|---|---|
| `core-normative` | Required for Kristal v5 core conformance. |
| `schema-normative` | Published JSON Schema contract. Published versions are immutable. |
| `reproducibility-normative` | Determinism, build, and reproducibility requirements. |
| `query-normative` | Required query-contract behavior. |
| `profile-normative` | Required only when the named optional profile is claimed. |
| `integration-normative` | Boundary contract for the named ecosystem integration. |
| `security-normative` | Trust, key, rollback, downgrade, and tenancy requirements. |
| `test-vector-normative` | Golden vectors required by the conformance claim they cover. |
| `informative` | Guidance, examples, operational notes, or explanatory material. |

The machine-readable classification is published in `contract-set.manifest.json`.

## Release identity

A published Kristal framework release is identified by all of the following:

1. semantic release version;
2. Git tag naming the release;
3. full immutable Git commit SHA resolved from that tag;
4. canonicalization profile and version declared by the release metadata.

An annotated or signed tag MAY be required by repository/release policy, but tag signing is not a separate Kristal protocol identity field.

The repository does **not** define `contract_set_digest` or `schema_set_digest` as additional release-identity requirements. `contract-set.manifest.json` classifies the public contract surface; it is not a second repository-wide checksum identity system.

The Git commit is intentionally **not embedded** into a file inside the same commit. Consumers resolve the release tag to the commit and record that commit in their own lock file.

Generated per-file release manifests are not part of the v5 release identity. In particular, `schema-set.manifest.json` and the legacy `tools/build_manifests.py` generator are retired. Schema and normative-document bytes are frozen by the Git commit referenced by the release tag.

### Current RC identity

```text
version: 5.0.0-rc.2
tag: v5.0.0-rc.2 (pending)
commit: resolve from the immutable tag after release
canonicalization: kristal.v5:jcs-rfc8785 / 1
```

## Immutability rule

After a stable release is tagged, files classified as normative for that release MUST NOT be changed in place. A semantic change produces a new release version. A published schema identified by its `$id` MUST remain byte-stable within a release.

## Release candidate rule

`5.0.0-rc.2` is the current candidate version under validation. It is not a published release identity until the corrected tree is committed and the immutable `v5.0.0-rc.2` tag is created.

The published `v5.0.0-rc.1` baseline remains immutable. An RC remains immutable once used as a pinned interoperability baseline. Corrections required after an RC is published MUST produce a new release-candidate version rather than moving the existing tag.

The stable `5.0.0` tag MUST be cut only after all release validation and required downstream integration gates pass and the contract set is intentionally frozen.

## Consumer pinning

Da'at, kOA, Konnaxion, Orgo, and other consumers SHOULD pin:

- `version`;
- Git tag;
- resolved full Git commit SHA;
- canonicalization profile/version.

Consumers MUST NOT use floating references such as `main`, `latest`, or `5.x` for high-assurance interoperability.

Kristal artifact/content hashes governed by JCS/SHA-256 remain separate protocol-level identities and MUST NOT be confused with framework release identity.
