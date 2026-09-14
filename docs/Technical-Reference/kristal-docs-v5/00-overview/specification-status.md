# Kristal v5 specification status

**Release candidate:** `5.0.0-rc.1`  
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

## Stable release identity

A stable Kristal release is identified by all of the following:

1. semantic release version;
2. signed Git tag resolving to one immutable commit;
3. `contract_set_digest` from `contract-set.manifest.json`;
4. `schema_set_digest` from `schema-set.manifest.json`;
5. the canonicalization profile and version declared in `kristal-release.json`.

The Git commit is intentionally **not embedded** into a file inside the same commit. Consumers resolve the signed tag to the commit and record that commit in their own lock file.

## Immutability rule

After a stable release is tagged, files classified as normative for that release MUST NOT be changed in place. A semantic change produces a new release version. A published schema identified by its `$id` MUST remain byte-stable within a release.

## Release candidate rule

`5.0.0-rc.1` is a stabilization release candidate. It may receive corrections before `5.0.0`. The stable `5.0.0` tag MUST be cut only after all release validation gates pass and the contract set is intentionally frozen.

## Consumer pinning

Da'at, kOA, Konnaxion, Orgo, and other consumers SHOULD pin:

- `version`;
- signed Git tag;
- resolved full Git commit SHA;
- `contract_set_digest`;
- `schema_set_digest`;
- canonicalization profile/version.

Consumers MUST NOT use floating references such as `main`, `latest`, or `5.x` for high-assurance interoperability.
