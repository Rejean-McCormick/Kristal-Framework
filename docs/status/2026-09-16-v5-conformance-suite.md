# Kristal v5 — conformance suite status

**Date:** 2026-09-16  
**Framework candidate:** `5.0.0-rc.2` (not published until tagged)  
**Suite state:** framework vectors executable  
**Implementation conformance:** not yet claimed

## Current verdict

The repository now has two distinct validation layers:

1. `tools/validate_release.py` validates framework/release integrity;
2. `tools/validate_conformance.py` validates the executable Kristal v5 TCK corpus.

Run both plus the strict documentation build with:

```bash
python tools/validate_all.py
```

For a local environment without MkDocs installed:

```bash
python tools/validate_all.py --skip-doc-build
```

The skip flag is a local convenience only. Authoritative CI requires `mkdocs build --strict`.

## Automated framework-vector coverage

| Surface | Status | Evidence |
|---|---:|---|
| Release files / metadata | PASS-capable | `tools/validate_release.py` |
| JSON Schema metaschema | PASS-capable | `tools/validate_release.py` |
| Examples vs schemas | PASS-capable | `tools/validate_release.py` |
| RFC 8785 / JCS vectors | PASS-capable | `09-test-vectors/jcs/` |
| Exchange ID golden vector | PASS-capable | `09-test-vectors/exchange/` |
| Exchange signature-envelope invariance | PASS-capable | `EX-003` |
| Exchange declared-hash tamper rejection | PASS-capable | `EX-004` |
| Status-bearing Exchange identity change | PASS-capable | `EX-STATUS-001` |
| Runtime Pack identity profile vector | PASS-capable | `09-test-vectors/runtime-pack/` |
| Runtime Pack payload hash/size verification | PASS-capable | `RP-001`, `RP-006` |
| Runtime Pack ordering bytes | PASS-capable | `RP-002` |
| Runtime Pack row-group boundaries | PASS-capable | `RP-003` |
| Runtime Pack Bloom bytes + pruning | PASS-capable | `RP-004` |
| Runtime Pack Roaring portable bytes | PASS-capable | `RP-005`, `RP-005-NORUN` |
| Strict docs build | CI gate | `.github/workflows/conformance.yml` |

## What this does not prove

A PASS of the framework suite does not prove that an external Kristal implementation is conformant.

The following still require a concrete compiler/verifier or a byte-format-specific profile:

- EX-1 rebuild determinism against a production compiler;
- EX-2 convergence of two independent implementations;
- EX-4 cryptographic signature failure handling against a real verifier;
- RP-1 full Runtime Pack compiler rebuild determinism;
- RP-2 through RP-5 against arbitrary production storage profiles that do not claim `kristal.v5:runtime-pack-portable-conformance@1`;
- RP-6 loader rejection against a production Runtime Pack loader;
- cross-platform XP-1.

These must remain `NOT TESTED` rather than being inferred from framework-vector success.

## Exchange identity profile

The Exchange TCK uses `kristal.v5:exchange-id-core@1`. Its vectors are stable payload/hash-target fixtures; they are not complete Exchange Manifest objects. Compiler identity and build-run metadata remain reproducibility evidence outside `kristal_id`.

## Runtime Pack identity profile

The TCK now pins the first executable Runtime Pack identity profile:

`kristal.v5:runtime-pack-id-core@1`

It excludes only explicitly volatile or self-referential fields from the Runtime Pack ID target:

- `runtime_pack_id`;
- `created_at`;
- `build.build_id`;
- `compiler.build_platform`;
- pack/manifest integrity hashes that would otherwise self-reference;
- signatures and attestations.

The remaining stable manifest material is identity-bearing for this TCK profile.

## Promotion path

Before claiming **reference implementation conformance**, connect a compiler/verifier adapter to the TCK and make EX-1..EX-4 and RP-1..RP-6 executable against that implementation.

Before claiming **ecosystem integration validated**, additionally run the Da'at + Interaction Kernel lifecycle end-to-end and verify ArtifactRef return/consumption without shared-database writes.

## Portable Runtime Pack materialization profile

The framework now publishes `kristal.v5:runtime-pack-portable-conformance@1`. Under that profile, RP-2 through RP-5 have exact golden bytes and are executable framework-vector surfaces. External implementations must independently reproduce the vectors before claiming implementation conformance to the profile.
