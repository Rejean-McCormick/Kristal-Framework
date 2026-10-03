# Kristal v5 — Runtime Pack Portable Conformance Status

**Date:** 2026-09-16  
**Framework candidate:** `5.0.0-rc.2`  
**Profile:** `kristal.v5:runtime-pack-portable-conformance@1`

## Status

The framework now publishes executable byte-level fixtures for the previously open Runtime Pack acceptance surfaces RP-2 through RP-5.

| Acceptance test | Framework vector | Status |
|---|---|---:|
| RP-2 stable ordering | `RP-002` | PASS-capable |
| RP-3 row-group boundaries | `RP-003` | PASS-capable |
| RP-4 membership filter determinism + pruning | `RP-004` | PASS-capable |
| RP-5 Roaring run-optimized bytes | `RP-005` | PASS-capable |
| RP-5 Roaring non-run bytes | `RP-005-NORUN` | PASS-capable |

The profile fixes exact comparison, grouping, KBF1 Bloom, and canonical 32-bit Roaring portable serialization rules so these tests no longer depend on host/library defaults.

## Validation

The native framework TCK recomputes all golden bytes and SHA-256 values. An independent Python cross-check was also used during preparation to recompute the same five payloads from the written profile rules.

Reference implementation conformance remains a separate claim: an external implementation must independently reproduce the official vectors. `kristal-reference >= 0.2.0` provides such an adapter surface for LevelUpDiag K15.

## Qualification impact

Once the external adapter passes RP-002 through RP-005-NORUN, the previous RP-2..RP-5 implementation-conformance warning can be removed. Production storage profiles that do not claim this portable profile still require their own byte-level reproducibility contract where physical bytes are part of the conformance claim.
