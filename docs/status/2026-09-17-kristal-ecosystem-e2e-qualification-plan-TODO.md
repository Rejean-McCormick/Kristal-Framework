# Kristal Ecosystem End-to-End Qualification Plan

**Status:** TODO  
**Scope:** Local ecosystem integration qualification  
**Applies to:** Kristal v5 / Interaction Kernel / Da’at / Orgo integration  
**Purpose:** Define the mandatory end-to-end test campaign required after framework and reference-implementation conformance.

---

## 1. Objective

Validate the complete local artifact-production and delivery flow across the Kristal ecosystem:

```text
Orgo
  ↓ immutable operational snapshot/export
Interaction Kernel
  ↓ kristal.build.request
Da’at
  ↓ mapping / compilation
Kristal
  ↓ Exchange + Runtime Pack
Interaction Kernel
  ↓ kristal.artifact.ready
Orgo
  ↓ ArtifactRef persisted
```

The campaign must prove that the ecosystem can produce, verify, deliver, retry, recover, and reference immutable Kristal artifacts without violating identity, integrity, trust, determinism, idempotency, or operational ownership boundaries.

---

## 2. Qualification Boundary

This campaign is separate from Kristal framework conformance.

The following are already covered by framework/reference validation and are prerequisites to this plan:

- Kristal schema and contract validation;
- JCS / RFC 8785 canonicalization;
- Exchange identity and verification;
- Runtime Pack identity and verification;
- RP-2 through RP-5 portable byte-level conformance;
- signature verification;
- trust and revocation handling;
- adversarial framework tests;
- release integrity and reproducibility.

This E2E campaign validates how those guarantees behave across real component boundaries.

---

## 3. Required Components

The local qualification environment must include:

- Orgo;
- Interaction Kernel;
- Da’at;
- Kristal framework contracts;
- a Kristal implementation/compiler/verifier;
- persistent operational storage used by Orgo;
- local artifact storage;
- test evidence output.

Component versions and configuration must be recorded for every run.

---

## 4. Mandatory Test Scenarios

### E2E-001 — Happy Path

Create an immutable operational snapshot in Orgo.

Submit a valid `kristal.build.request` through the Interaction Kernel.

Da’at must transform/compile the request into valid Kristal artifacts.

Kristal must produce and validate:

- Exchange artifact;
- Runtime Pack artifact;
- manifests;
- declared identities and hashes.

The Interaction Kernel must deliver `kristal.artifact.ready`.

Orgo must persist the resulting ArtifactRef.

**Expected result:** PASS.

---

### E2E-002 — Deterministic Rebuild

Execute the same build from:

- the same immutable snapshot;
- the same build configuration;
- the same declared profiles.

Verify that all identity-relevant outputs are identical.

Where byte-level determinism is declared, payload bytes must also be identical.

**Expected result:** PASS with no identity drift.

---

### E2E-003 — Idempotent Request Replay

Submit the same logical request twice using the same idempotency key.

The system must not create conflicting builds or duplicate logical artifacts.

**Expected result:** one logical outcome.

---

### E2E-004 — Equivalent Requests With Different Transport IDs

Submit semantically identical build requests using different transport/request identifiers.

Transport metadata must not alter Kristal artifact identity.

**Expected result:** stable artifact identity.

---

### E2E-005 — Duplicate `kristal.artifact.ready`

Deliver the same ready event more than once.

Orgo must not create duplicate operational references.

**Expected result:** idempotent persistence.

---

### E2E-006 — Timeout Before Receipt

Allow the build to complete but simulate loss or timeout before the caller receives confirmation.

Retry the request.

**Expected result:** recovery of the existing logical result without conflicting duplicate artifacts.

---

### E2E-007 — Da’at Failure Before Artifact Completion

Stop or fail Da’at before a valid artifact is fully produced.

No incomplete artifact may be reported as ready.

**Expected result:** fail closed.

---

### E2E-008 — Failure After Build, Before Ready Event

Complete artifact production, then fail before `kristal.artifact.ready` is delivered.

Retry or recover the workflow.

**Expected result:** existing valid immutable artifacts are rediscovered or reused safely.

---

### E2E-009 — Tampered Exchange

Modify Exchange content after build.

Verification must fail.

The artifact must not reach the accepted ArtifactRef path.

**Expected result:** rejection.

---

### E2E-010 — Tampered Runtime Pack

Modify a Runtime Pack payload file without updating the manifest.

**Expected result:** rejection by hash/size verification.

---

### E2E-011 — Incorrect Declared Digest

Provide an incorrect digest for an otherwise valid artifact.

Receiving components must not trust transport metadata over artifact verification.

**Expected result:** rejection.

---

### E2E-012 — Invalid Signature

Test:

- invalid signature;
- wrong public key;
- modified signed payload.

**Expected result:** rejection.

---

### E2E-013 — Trust / Revocation Failure

Test:

- revoked key;
- expired key;
- unknown key;
- not-yet-valid key.

**Expected result:** fail closed according to Kristal trust rules.

---

### E2E-014 — Artifact Supersession

Produce a valid artifact for snapshot A.

Produce a later valid artifact for snapshot B.

The original Kristal artifact must remain immutable.

Operational references may move only through explicit lifecycle behavior.

**Expected result:** no mutation of previously issued immutable artifacts.

---

### E2E-015 — Invalid Build Request

Submit malformed or contract-invalid `kristal.build.request` payloads.

**Expected result:** rejection at the appropriate admission boundary before artifact production.

---

### E2E-016 — Unsupported Profile or Policy

Request an unsupported Kristal profile, compiler profile, or Runtime Pack policy.

**Expected result:** explicit deterministic failure; no silent fallback.

---

### E2E-017 — ArtifactRef Integrity

Verify that the final ArtifactRef:

- resolves the intended immutable Kristal artifact;
- includes sufficient identity information;
- does not embed mutable operational state that belongs to Orgo;
- cannot resolve ambiguously to multiple artifacts.

**Expected result:** PASS.

---

### E2E-018 — Ownership Boundary

Verify that:

- Orgo owns operational state;
- Interaction Kernel owns admission/routing/coordination behavior;
- Da’at owns transformation/compilation work;
- Kristal owns immutable semantic/export artifacts.

No component may silently persist or redefine another component’s operational responsibility.

**Expected result:** PASS.

---

## 5. Evidence Requirements

Every E2E scenario must produce machine-readable evidence containing at least:

```text
scenario_id
run_id
component_versions
input_snapshot_id
request_id
idempotency_key
build_id
exchange_id
runtime_pack_id
artifact_ref
expected_result
actual_result
verdict
```

Where applicable, evidence must also include:

- SHA-256 digests;
- manifest paths;
- signature verification result;
- trust decision;
- retry count;
- timestamps;
- error code;
- recovery action;
- emitted Interaction Kernel envelopes.

---

## 6. Acceptance Gate

The baseline ecosystem E2E qualification is successful only when all mandatory scenarios pass.

Target:

```text
0 FAIL
0 ERROR
0 unexpected duplicate artifacts
0 integrity bypasses
0 trust bypasses
0 non-deterministic rebuilds
0 ownership-boundary violations
```

Warnings must be reviewed explicitly before the campaign can be considered complete.

---

## 7. Qualification Claim

A successful campaign establishes the following local qualification claim:

> Given an immutable operational snapshot and fixed build configuration, the Kristal ecosystem can deterministically produce, verify, deliver, reference, retry, and recover immutable Exchange and Runtime Pack artifacts without corrupting artifact identity, integrity, trust semantics, idempotency, or operational ownership boundaries.

This claim applies only to the tested local component versions and configurations.

---

## 8. Out of Scope for This Baseline

The first E2E qualification does not yet establish:

- production deployment readiness;
- large-scale concurrency;
- sustained load behavior;
- multi-region operation;
- federation across independent operators;
- disaster recovery;
- long-duration soak behavior;
- arbitrary third-party compiler interoperability.

These belong to later qualification phases.

---

## 9. Follow-Up Qualification Phases

After the baseline E2E campaign passes, later work should cover:

1. concurrency and race conditions;
2. multi-consumer artifact delivery;
3. high-volume rebuild campaigns;
4. recovery after partial infrastructure failure;
5. federation;
6. long-running replay/recovery;
7. operational observability;
8. production deployment qualification.

---

## 10. Current Status

```text
Framework conformance          PASS
Reference implementation       PASS
Runtime Pack conformance       PASS
Signature / trust              PASS
LevelUpDiag Deep Split         PASS

Ecosystem E2E                  TODO
Production qualification       NOT YET
```

This document is the official TODO plan for the next Kristal qualification phase.
