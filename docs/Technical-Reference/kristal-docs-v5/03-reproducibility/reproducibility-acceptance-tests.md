# Reproducibility Acceptance Tests (Kristal v5)

## Status
Draft (normative acceptance criteria)

## Purpose
Define the **acceptance tests** that determine whether a Kristal v5 implementation produces **reproducible** artifacts.

In v5, reproducibility is a first-class requirement:
- Exchange rebuilds MUST produce identical `kristal_id` given the same inputs and rules.
- Runtime Pack rebuilds MUST produce identical `runtime_pack_id` (legacy alias: `pack_id`) and identical declared payload hashes given the same inputs, compiler, configuration, and policy selections.

These tests are designed to prevent “works on my machine” builds and to ensure artifacts are comparable across toolchains.

## Normative language
The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

---

# 1. Definitions

## 1.1 Inputs
An **Input Snapshot** is a content-addressed reference to the exact source inputs used for a build (datasets, Claim-IR sets, resolved Claim-IR sets, configuration files, etc.).

## 1.2 Build determinism surface
The determinism surface for reproducing a **build process** is defined by:
- the declared input snapshots,
- the compiler identity and version,
- the full build configuration (identified by `config_hash`),
- and the recorded `policy_selections` (see `03-reproducibility/allowed-runtime-pack-policies.md`).

This build-process surface is broader than Exchange content identity. Under `kristal.v5:exchange-id-core@1`, compiler/build-run identity is recorded for reproducibility but does not become part of `kristal_id` merely because a particular compiler produced the payload.

## 1.3 Artifact hashes
- `kristal_id`: content hash of the stable Exchange payload under `kristal.v5:exchange-id-core@1` (signatures excluded).
- `runtime_pack_id`: content hash of Runtime Pack identity material under the applicable Runtime Pack identity profile (`pack_id` MAY be accepted only as a compatibility alias).
- `payload_hashes`: hashes of pack payload components (Parquet files, index files, etc.), as declared in the pack manifest.

---

# 2. Exchange reproducibility tests (mandatory)

## EX-1: Exchange hash determinism (same toolchain)
**Goal:** Exchange rebuild is byte-stable and ID-stable.

**Given**
- identical input snapshots
- identical compiler version
- identical config hash
- identical canonicalization profile/version

**Then**
- the rebuilt Exchange MUST produce the same `kristal_id`
- and the canonicalized Exchange bytes used for hashing MUST match (byte equality)

**Failure**
- If `kristal_id` differs, build is non-reproducible → FAIL.

---

## EX-2: Exchange hash determinism (cross toolchain)
**Goal:** Independent implementations converge on the same ID.

**Given**
- a published stable Exchange payload fixture + expected `kristal_id`
- the `kristal.v5:exchange-id-core@1` identity boundary
- canonicalization defined as RFC 8785 (JCS)

**Then**
- any v5 core conformant implementation MUST compute the expected `kristal_id`;
- two independent conforming implementations MUST converge on that ID even when their compiler names, versions, build IDs, host platforms, or CI metadata differ, provided they emit the same stable Exchange payload.

**Failure**
- mismatch → FAIL (interop-breaking).

---

## EX-3: Signature envelope invariance
**Goal:** Signature presence does not alter the hashed payload.

**Given**
- an Exchange artifact `E0` without signatures
- a signed Exchange artifact `E1` containing signatures in the signature envelope

**Then**
- the hash input (`exchange_without_signatures`) MUST be identical for `E0` and `E1`
- `kristal_id(E0)` MUST equal `kristal_id(E1)`

**Failure**
- if signatures affect hash input → FAIL.

---

## EX-4: Fail-closed verification (Exchange)
**Goal:** declared integrity cannot be ignored.

**Given**
- an Exchange artifact that declares a hash/signature
- a verifier implementation

**Then**
- verifier MUST error if:
  - signature verification fails
  - declared hash does not match computed hash
  - integrity material is malformed/ambiguous

**Failure**
- verifier continues “best effort” → FAIL.

---

# 3. Runtime Pack reproducibility tests (mandatory)

## RP-1: Pack rebuild determinism (same toolchain)
**Goal:** same inputs → identical pack.

**Given**
- identical input snapshots
- identical compiler identity + version
- identical config hash
- identical policy selections

**Then**
- rebuilt Runtime Pack MUST produce identical:
  - `runtime_pack_id`
  - `payload_hashes` (for each payload component)
  - `policy_selections` recorded in manifest

**Failure**
- any mismatch → FAIL.

---

## RP-2: Pack determinism under stable ordering policy
**Goal:** ordering is not implementation-dependent.

**Given**
- a fixed ordering policy (e.g., `ORDER_SET([SPO])`)
- a fixed tie-breaker rule (including `claim_id`)

**Then**
- the triples table ordering MUST be identical between rebuilds
- and consistent across platforms (Windows/Linux/macOS) for the same toolchain.

**Failure**
- any reordering → FAIL.

---

## RP-3: Row-group policy determinism
**Goal:** row-group assignment is deterministic.

**Given**
- a declared row-group policy (e.g., `FIXED_ROWS(500000)`)

**Then**
- the boundaries of row-groups MUST be identical across rebuilds
- and MUST NOT depend on unstable runtime factors (thread scheduling, CPU count, memory pressure)

**Failure**
- row-group boundaries differ → FAIL.

---

## RP-4: Membership filter determinism
**Goal:** filter metadata and behavior are reproducible.

**Given**
- membership filter policy declared (e.g., `BINARY_FUSE`)
- declared parameters (seed(s), bits-per-key, variant, key-space encoding)

**Then**
- the filter construction MUST be identical across rebuilds
- filter metadata recorded in manifest MUST match exactly

**And**
- filter false positives MUST be pruned deterministically against authoritative data

**Failure**
- filter differs under same seeds/params → FAIL.

---

## RP-5: Bitmap determinism (Roaring + run optimization)
**Goal:** bitmap encoding does not drift.

**Given**
- bitmap policy `ROARING`
- run optimization flag ENABLED or DISABLED

**Then**
- emitted bitmap files (or their declared hashes) MUST match across rebuilds.

**Failure**
- mismatch → FAIL.

---


## RP-2 through RP-5 portable byte profile

Kristal v5 publishes the normative profile `kristal.v5:runtime-pack-portable-conformance@1` in `05-profiles/profile-runtime-pack-portable-conformance.md`. The profile fixes the byte-level semantics needed to execute RP-2, RP-3, RP-4, and RP-5 without relying on host-specific sort behavior, row-group heuristics, probabilistic-filter library defaults, or implementation-specific Roaring run optimization.

The corresponding golden fixtures are `09-test-vectors/runtime-pack/portable-vectors.json` and are mandatory framework-vector coverage for this profile.

## RP-6: Fail-closed verification (Runtime Pack)
**Goal:** declared integrity cannot be ignored.

**Given**
- a Runtime Pack that declares payload hashes and/or signatures

**Then**
- pack loaders/verifiers MUST error if:
  - any payload hash mismatch occurs
  - any declared signature fails verification
  - integrity fields are malformed/ambiguous

**Failure**
- “load anyway” behavior → FAIL.

---

# 4. Cross-platform reproducibility tests (recommended)

## XP-1: Cross-OS rebuild reproducibility
**Goal:** avoid platform-specific drift.

**Run**
- Build the same inputs/config/policies on at least two OS environments.

**Then**
- Exchange `kristal_id` MUST match.
- Runtime Pack `runtime_pack_id` and payload hashes SHOULD match.

**Note**
If exact Runtime Pack bit identity is not feasible cross-OS due to dependency formats, the implementation MUST:
- declare which payload components are excluded from the reproducibility surface, and
- provide a deterministic canonical representation for pack identity.

---

# 5. Performance and resource invariants (recommended)

These are not core determinism requirements, but SHOULD be recorded for operational predictability:
- build wall time
- peak memory
- pack size
- index sizes (bitmaps, filters)

If recorded, these MUST NOT affect core identity unless explicitly included in the declared reproducibility surface.

---

# 6. Test artifacts and fixtures

Implementations MUST provide:
- Exchange fixtures + expected `kristal_id`
- Runtime Pack fixtures + expected `runtime_pack_id` + expected payload hashes
- JCS canonicalization vectors + expected hashes
- Query fixtures for stable paging (cursor/offset), join caps, and error modes

See `09-test-vectors/` and `10-examples/`.

---

# 7. Definition of done (reproducibility)

A Kristal v5 implementation passes reproducibility if:
- All Exchange tests EX-1 through EX-4 pass (mandatory).
- All Runtime Pack tests RP-1 through RP-6 pass (mandatory).
- Cross-platform test XP-1 is run for at least one release candidate (recommended).

Failure of any mandatory test blocks release of v5 artifacts.


## Executable TCK mapping

The executable framework-vector surface is `09-test-vectors/TCK.md` and is run by:

```bash
python tools/validate_conformance.py
```

A framework-vector PASS proves that the published vectors, hash-target rules, and fail-closed fixture expectations are internally executable. It does **not** by itself prove conformance of a production compiler or verifier. Tests that require a concrete implementation remain `NOT TESTED` until an implementation adapter is connected to the TCK.
