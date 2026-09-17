# Kristal v5 Test Compatibility Kit (TCK)

## Purpose

The Kristal TCK separates two claims that MUST NOT be conflated:

1. **framework-vector conformance** — the published contracts and golden vectors are internally executable and self-consistent;
2. **implementation conformance** — a concrete compiler/verifier produces the required artifacts and rejects invalid ones.

`node tools/kristal_tck.mjs` currently proves the first claim for the implemented vector surfaces.

The Exchange vectors use the payload identity profile `kristal.v5:exchange-id-core@1`. They are payload/hash-target fixtures rather than complete Exchange Manifest instances; compiler/build-run identity is recorded by the manifest and does not define `kristal_id`.

The Runtime Pack vectors use `runtime_pack_version = "5.0.0"`. Runtime Pack format version is independent of the framework release-candidate suffix (`rc.N`).

## Current automated coverage

| Acceptance criterion | Framework vector | Implementation proof |
|---|---:|---:|
| EX-1 same-toolchain Exchange identity determinism | PASS-capable | adapter/compiler required |
| EX-2 cross-toolchain expected Exchange ID | PASS-capable | second implementation required |
| EX-3 signature-envelope invariance | PASS-capable | adapter/compiler required |
| EX-4 fail-closed Exchange integrity | partial: hash-target vectors | verifier/signature adapter required |
| RP-1 Runtime Pack identity + inventory determinism | PASS-capable | compiler adapter required |
| RP-2 stable ordering bytes | contract only | compiler adapter required |
| RP-3 row-group determinism | contract only | compiler adapter required |
| RP-4 membership-filter determinism | contract only | byte-format profile + compiler required |
| RP-5 bitmap determinism | contract only | byte-format profile + compiler required |
| RP-6 fail-closed payload verification | PASS-capable | loader/verifier adapter required |

A framework-vector PASS therefore MUST NOT be reported as full implementation conformance.

## Commands

Run release integrity and TCK vectors:

```bash
python tools/validate_all.py --skip-doc-build
```

Authoritative CI SHOULD run without `--skip-doc-build` so `mkdocs build --strict` is also required.

## Next adapter surface

A later TCK revision SHOULD add a process adapter for a concrete compiler/verifier with these logical operations:

- `exchange_id`
- `verify_exchange`
- `build_runtime_pack`
- `verify_runtime_pack`

That adapter will allow the same fixture corpus to score EX-1..EX-4 and RP-1..RP-6 against real implementations without embedding implementation logic in the framework repo.

### Runtime Pack portable materialization profile

RP-2 through RP-5 use `kristal.v5:runtime-pack-portable-conformance@1` and `runtime-pack/portable-vectors.json`. The TCK compares exact output bytes, not only semantic values. This closes the framework-vector gap for ordering, row-group boundaries, Bloom-filter construction/pruning, and canonical Roaring portable serialization.

