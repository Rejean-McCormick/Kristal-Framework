# Kristal Framework v5 — validation status

**Date:** 2026-09-16  
**Current candidate:** `5.0.0-rc.2`  
**Current candidate tag:** pending; do not claim a release until `v5.0.0-rc.2` is created  
**Previous published baseline:** `v5.0.0-rc.1` at `af703bf02ee04a69a5f2ad6694fa8b8e56ae2b19`  
**Overall status:** **FRAMEWORK / RELEASE INTEGRITY + FRAMEWORK-VECTOR CONFORMANCE PASS LOCALLY; IMPLEMENTATION CONFORMANCE PENDING**

## 1. Executive status

The rc.2 candidate corrects release-tooling drift and cross-document identity/lifecycle inconsistencies discovered after rc.1. The published rc.1 baseline remains immutable; these corrected bytes require the new rc.2 identity if released.

The current repository has two executable validation layers:

1. `tools/validate_release.py` — framework/release integrity;
2. `tools/validate_conformance.py` / `tools/kristal_tck.mjs` — executable framework-vector conformance.

Run both, plus the strict documentation build, with:

```bash
python tools/validate_all.py
```

A framework-vector PASS proves that the published vector corpus and framework rules exercised by that corpus are executable and self-consistent. It does **not** prove that an external compiler/verifier implementation is conformant.

| Validation layer | Current status |
|---|---|
| Framework / release integrity | **PASS locally** |
| JSON Schema corpus | **PASS** |
| JSON Schema declared formats | **PASS for mapped examples/TCK Runtime Pack fixtures** |
| Published examples against schemas | **PASS** |
| JCS golden vectors | **PASS** |
| Exchange framework vectors | **PASS** |
| Runtime Pack framework vectors | **PASS** |
| Documentation navigation/local links | **PASS** |
| Strict MkDocs build | **CI gate configured; not executed in this review environment** |
| Linux + Windows CI matrix | **configured; CI execution evidence pending** |
| Exchange implementation reproducibility | **NOT YET PROVEN** |
| Runtime Pack implementation reproducibility | **NOT YET PROVEN** |
| Independent implementation convergence | **NOT YET PROVEN** |
| Real cryptographic signature/trust fail-closed | **NOT YET PROVEN** |
| Da’at / IK end-to-end | **PENDING** |
| Orgo / Konnaxion end-to-end | **PARTIAL / NOT YET FULLY PROVEN** |

## 2. Release-integrity corrections validated in rc.2 candidate

The candidate now enforces the intended Git-based release identity:

```text
semantic version
+ immutable Git tag
+ resolved full commit SHA
+ canonicalization profile/version
```

`contract-set.manifest.json` is a curated public-surface index, not a repository checksum inventory.

The retired per-file release model is intentionally removed:

```text
schema-set.manifest.json
tools/build_manifests.py
```

`validate_release.py` fails if either file remains present.

The release metadata and consumer lock now record both:

```text
canonicalization_profile = kristal.v5:jcs-rfc8785
canonicalization_version = 1
```

## 3. Schema and lifecycle corrections

Example validation now uses JSON Schema `FormatChecker`, so declared formats such as `date-time` and `uri` are actually enforced instead of being silently ignored.

The Exchange lifecycle is aligned as follows:

- `working_exchange` may be `draft`, `working`, `under_review`, `recognized`, `deprecated`, `superseded`, or `revoked`;
- `reference_exchange` requires at least one `authority_recognition_ref`;
- a current Reference Exchange is issued with `artifact_status = reference`;
- an already-issued Reference Exchange may later become `deprecated`, `superseded`, or `revoked`;
- validation references alone cannot create a Reference Exchange.

The mapped Reference Exchange example passes the corrected schema. A reference artifact with no authority-recognition reference is rejected.

## 4. Exchange identity boundary

The core Exchange identity profile is now named:

```text
kristal.v5:exchange-id-core@1
```

`kristal_id` identifies the stable Exchange payload. Compiler name/version/revision, host platform, build correlation ID, wall-clock metadata, and `build.config_hash` remain reproducibility/build evidence and do not define `kristal_id` merely because they are present in an Exchange Manifest or package envelope.

This preserves the EX-2 requirement that two independent conforming compilers can converge on the same Exchange identity when they produce the same stable payload.

The current Exchange TCK fixtures are payload/hash-target fixtures, not complete `exchange-manifest.schema.json` instances. Full implementation conformance still requires a concrete compiler/verifier adapter.

## 5. Runtime Pack corrections

Core Runtime Pack format examples and TCK fixtures use:

```text
runtime_pack_version = 5.0.0
artifact_type = runtime_pack_manifest
```

The Runtime Pack format version is intentionally independent of the framework release-candidate suffix. Publishing `5.0.0-rc.2` therefore does not mechanically alter Runtime Pack content identity solely because the framework RC number changed.

The current framework TCK exercises Runtime Pack identity/inventory vectors and fail-closed payload hash/size verification. Byte-level compiler behavior for ordering, row groups, membership filters, and bitmap encodings still requires a concrete implementation/profile.

## 6. Source archive qualification

`tools/build_release_archive.py` now builds from Git-tracked files only and refuses a dirty working tree by default.

Local validation confirmed:

- two builds from the same clean commit produced identical ZIP SHA-256 values;
- untracked `.levelupdiag/` evidence and an arbitrary untracked temporary file did not alter the archive when diagnostic `--allow-dirty` mode was used;
- those untracked files were absent from the archive;
- `CODE_SNAPSHOT_MANIFEST.md` is intentionally excluded from framework release archives;
- the retired schema-set manifest and manifest generator were absent from the archive.

This closes the previously observed local-evidence contamination path.

## 7. Executed local gates

Executed successfully in the review environment:

```text
python tools/validate_release.py                         PASS
python tools/validate_conformance.py                    PASS
python tools/validate_all.py --skip-doc-build           PASS
node tools/kristal_tck.mjs                              PASS
Python bytecode compilation of tools                    PASS
archive determinism / untracked contamination checks    PASS
```

The local environment did not contain MkDocs, so `mkdocs build --strict` was not executed here. The authoritative CI workflow installs `requirements-dev.txt` and keeps the strict docs build as a required gate.

## 8. What remains before stronger claims

### Reference implementation conformance

Still required:

```text
EX-1 production compiler rebuild determinism
EX-2 convergence of independent implementations
EX-3 signature-envelope invariance through the real verifier
EX-4 fail-closed content/signature verification through the real verifier
RP-1 production Runtime Pack rebuild determinism
RP-2 deterministic record ordering
RP-3 deterministic row-group boundaries
RP-4 deterministic membership-filter bytes
RP-5 deterministic bitmap bytes when claimed
RP-6 fail-closed production Runtime Pack loader/verifier
```

### Security qualification

Still required with real cryptographic material:

- valid signature acceptance;
- wrong signature rejection;
- wrong key rejection;
- payload/signature tamper rejection;
- expired/revoked key behavior;
- trust-root rotation behavior;
- downgrade/rollback policy integration.

### Ecosystem qualification

Still required end-to-end:

```text
operational owner
→ immutable export/snapshot
→ Interaction Kernel request
→ Da’at mapping/compilation
→ Kristal artifact verification
→ optional Runtime Pack derivation
→ kristal.artifact.ready / ArtifactRef
→ operational consumer linkage
```

Retries, duplicate messages, crash recovery, idempotency, timeout-before-receipt, revocation, and rollback scenarios must also be exercised.

## 9. Promotion rule

The candidate may be tagged as `v5.0.0-rc.2` only after the complete repository gate is green from a clean committed tree, including strict MkDocs and the Linux/Windows CI matrix.

A green rc.2 framework gate should be described as:

```text
FRAMEWORK / RELEASE INTEGRITY VALIDATED
FRAMEWORK-VECTOR CONFORMANCE VALIDATED
IMPLEMENTATION CONFORMANCE PENDING
```

Do not shorten that to “Kristal v5 is production-qualified.”
