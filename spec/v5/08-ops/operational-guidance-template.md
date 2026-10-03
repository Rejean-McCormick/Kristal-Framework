# Operational guidance template

## Status

Template, non-normative.

## Purpose

A consistent structure for operational and implementation guidance across the Kristal ecosystem:

```text
Kristal
Orgo
SenTient
Architect
Konnaxion
Compiler
Client
Reader
Runtime
```

This template is **non-normative**. It does not define conformance requirements for Kristal artifacts.

Use it to document failure paths, resilience, observability, operational trade-offs, degraded conditions, reader policy behavior, authority recognition handling, and least-worst implementation choices.

This template describes operational behavior. It does not define truth, authority, certainty, validation status, or recognition status.

---

## 1) Concept

**Name:**
**One-liner:**
What it is.

**Applies to:**

```text
Kristal / Orgo / SenTient / Architect / Konnaxion / Compiler / Client / Reader / Runtime
```

**Lifecycle stage:**

```text
ingest
extract
normalize
structure
compile
review
validate
recognize
federate
package
distribute
activate
query
render
observe
recover
```

**Primary goal:**
Examples:

```text
availability
correctness
reproducibility
integrity
isolation
traceability
reader safety
status transparency
```

**Secondary goals:**
Examples:

```text
latency
cost
debuggability
operator clarity
offline usability
ecosystem interoperability
```

**Kristal v5 concepts involved:**

```text
Structured Epistemic State
Working Artifact
Reference Artifact
Exchange
Shard
Federation Manifest
Runtime Pack
Authority Channel
Authority Registry
Validation Decision
Authority Recognition
Reader Policy
Assertion Status
Certainty Level
```

---

## 2) Problem

**What can go wrong?**

Failure modes:

```text
timeouts
partial outputs
poisoned inputs
overload
nondeterminism
cache corruption
hash mismatch
signature mismatch
authority registry unavailable
reader policy mismatch
scope mismatch
stale runtime pack
incomplete shard
conflicting federation inputs
ambiguous assertion status
missing certainty metadata
missing validation decision
missing authority recognition
profile artifact mismatch
projection mismatch
```

Blast radius:

```text
single assertion
single shard
single build
single runtime pack
single authority channel
single tenant
single reader policy
single region
federated distribution
global distribution
```

User-facing impact:

```text
missing pack
stale knowledge
incorrect rendering
unavailable query
incomplete labels
blocked publication
blocked activation
unrecognized artifact
disputed result shown without enough context
validated-only view hiding lower-status material
research view exposing disputed material with labels
```

**How it fails today, if known:**

Symptoms:

```text
```

Triggers:

```text
```

Observed frequency:

```text
```

---

## 3) Solution

**Approach:**
What you do and why.

**Mechanics:**

Inputs:

```text
```

Outputs:

```text
```

State transitions:

```text
```

Retry policy:

```text
```

Backoff policy:

```text
```

Quarantine / dead-letter policy:

```text
```

Timeouts and resource limits:

```text
```

Determinism guarantees:

```text
```

Specify what must remain identical across reruns, such as:

```text
content-addressed IDs
canonicalized hash targets
query results under the same snapshot and reader policy
build records
validation decision references
authority recognition references
runtime pack manifests
```

**Data contracts / artifacts involved:**

Use only the relevant entries:

```text
Structured Epistemic State
Exchange
Exchange Shard Manifest
Exchange Federation Manifest
Runtime Pack Manifest
Authority Registry
Validation Decision
Authority Recognition
Reader Policy
Validation Report
Review Bundle
Revocation Record
Claim-IR
Resolved Claim-IR
```

`Claim-IR` and `Resolved Claim-IR` are extraction or resolution profiles. They are not the universal required input path for Kristal v5.

**IDs that must be carried end-to-end:**

Use only the relevant entries:

```text
build_id
state_id
kristal_id
exchange_id
shard_id
federation_id
runtime_pack_id
assertion_id
evidence_id
validation_decision_id
recognition_id
authority_channel_id
reader_policy_id
tenant_id
correlation_id
```

**Security and integrity considerations:**

```text
trust roots
signature verification points
hash verification points
authority registry verification
reader policy enforcement
tenant isolation boundaries
downgrade and rollback rules
revocation handling
key rotation
runtime pack activation requirements
profile artifact verification
```

**Status and policy considerations:**

Specify how the solution preserves or reports:

```text
artifact_status
assertion_status
certainty_level
validation_status
validated_as
recognition_status
authority_channel
scope
reader_policy
reason_codes
```

---

## 4) When to use

**Use when:**

Examples:

```text
a dependency is flaky
workload spikes
offline distribution is required
RDF canonicalization is expensive
authority registry access is intermittent
runtime pack activation must be delayed
reader policy must hide non-recognized material
a shard is incomplete but still useful for review
a validation decision is pending
a research view should expose lower-certainty material
```

**Do not use when:**

Examples:

```text
it would hide status labels
it would mask integrity failures
it would present unresolved ambiguity as resolved fact
it would present scoped validation as universal truth
it would introduce nondeterministic content-addressed outputs
it would silently merge conflicting authority channels
it would enlarge the normative surface area without need
```

**Preconditions / dependencies:**

Examples:

```text
feature flags
queue support
local disk cache
stable clock
monotonic counters
authority registry snapshot
reader policy snapshot
runtime pack inventory
signature verification keys
revocation list
profile support
local query index
```

---

## 5) Pitfalls and trade-offs

**Pitfalls:**

Examples:

```text
silent degradation
retry storms
inconsistent caches
partial acceptance of probabilistic results
ambiguous authority labels
missing certainty labels
reader policy drift
authority channel confusion
profile verification treated as truth validation
runtime activation treated as authority recognition
operational metadata affecting content hashes
downstream generation introducing new facts
```

**Trade-offs:**

Correctness vs availability:

```text
```

Latency vs cost:

```text
```

Reproducibility vs performance:

```text
```

Isolation vs deduplication:

```text
```

Strict reader policy vs exploratory access:

```text
```

Authority consistency vs plural federation:

```text
```

Offline usability vs freshness:

```text
```

**Anti-patterns to avoid:**

```text
Bypassing required integrity verification when integrity is declared.
Writing unresolved ambiguity as resolved fact.
Presenting scoped validation as universal truth.
Treating ShEx, SHACL, JSON Schema, or RDF projection conformance as authority recognition.
Treating runtime pack activation as claim validation.
Letting operational metadata affect content hashes or IDs.
Making downstream generation introduce new facts.
Silently merging conflicting shards.
Hiding disputed, rejected, fictional, mythological, or low-certainty status.
Treating "validated-only" as "maximum certainty only."
```

---

## 6) Observability

**Logs: structured fields**

Required where applicable:

```text
tenant_id
build_id
state_id
kristal_id
exchange_id
shard_id
federation_id
runtime_pack_id
assertion_id
validation_decision_id
recognition_id
authority_channel_id
reader_policy_id
stage
attempt
duration_ms
outcome
error_code
reason_codes
dependency
correlation_id
```

Allowed `outcome` values:

```text
success
fail
partial
blocked
skipped
degraded
not_applicable
```

**Metrics:**

```text
throughput_items_per_sec
success_rate
failure_rate
partial_rate
blocked_rate
retry_rate
queue_depth
queue_lag_ms
cache_hit_rate
hash_verification_failures
signature_verification_failures
authority_registry_failures
validation_error_counts_by_code
recognition_error_counts_by_code
reader_policy_exclusion_counts
runtime_pack_activation_failures
query_error_rate
render_label_omission_count
```

**Tracing:**

Correlation IDs SHOULD be propagated across services.

Recommended spans:

```text
ingest
extract
normalize
structure
compile
review
validate
recognize
federate
package
distribute
activate
query
render
profile_verify
recover
```

**Dashboards / alerts:**

SLOs:

```text
```

Paging thresholds:

```text
```

Anomaly detection:

```text
```

Recommended alert dimensions:

```text
authority_channel_id
reader_policy_id
tenant_id
runtime_pack_id
stage
error_code
reason_code
```

---

## 7) Runbook

**Detection:**

What alerts fire?

```text
```

What dashboards to check first?

```text
```

**Mitigation:**

Step-by-step actions, ordered:

```text
1.
2.
3.
```

Safe fallback modes:

```text
```

Fallback modes must preserve:

```text
deterministic behavior where declared
status visibility
authority labels
certainty labels
reader policy behavior
artifact identity
integrity labels
```

How to quarantine inputs:

```text
```

How to disable a profile:

```text
```

How to roll back a runtime pack:

```text
```

How to block activation without deleting the candidate artifact:

```text
```

How to preserve user-visible labels during degraded operation:

```text
```

**Recovery:**

Criteria for returning to normal mode:

```text
```

Post-incident checks:

```text
reproducibility tests
hash verification
signature verification
authority registry consistency
reader policy consistency
runtime pack inventory consistency
cache consistency
query consistency
render label checks
revocation checks
```

**Postmortem notes:**

Root cause:

```text
```

Prevent recurrence:

```text
```

Action items:

```text
-
-
-
```

---

## 8) Example

Optional.

**Scenario:**

```text
```

**Before:**

```text
```

**After:**

```text
```

**Key outputs: sample log fields**

```json
{
  "tenant_id": "tenant:example",
  "build_id": "build:2026-06-12T00:00:00Z:example",
  "state_id": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "kristal_id": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "shard_id": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "authority_channel_id": "authority:example",
  "reader_policy_id": "reader_policy:validated_only",
  "stage": "validate",
  "attempt": 1,
  "duration_ms": 1234,
  "outcome": "partial",
  "error_code": "AUTHORITY_REGISTRY_TIMEOUT",
  "reason_codes": [
    "authority_not_recognized"
  ],
  "dependency": "authority-registry",
  "correlation_id": "corr:example"
}
```

---

## 9) Versioning and ownership

**Owner team:**

```text
```

**Last updated:**

```text
```

**Applies to versions:**

```text
Kristal v5.0
```

Optional ecosystem versions:

```text
Orgo:
SenTient:
Architect:
Konnaxion:
Compiler:
Runtime:
Reader:
```

**Change policy:**

This template is non-normative. Changes to the template do not change Kristal artifact conformance requirements.

If a guidance page introduces normative requirements, those requirements must be moved to the appropriate Kristal v5 specification, schema, profile, or contract.

**Change log:**

```text
YYYY-MM-DD:
```
