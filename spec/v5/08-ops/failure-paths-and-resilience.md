# Failure Paths and Resilience

## Status

Non-normative operational guidance for Kristal v5

## Purpose

This document provides operational guidance for building, reviewing, validating, publishing, distributing, and rendering Kristals reliably in the ecosystem:

* **Orgo** — workflow, orchestration, review, approvals, routing, build lifecycle
* **SenTient** — resolution, disambiguation, normalization, extraction support
* **Kristal compiler** — Structured Epistemic State compile, Exchange generation, Runtime Pack compile
* **Konnaxion** — distribution, offline caching, reader-policy selection, Runtime Pack access
* **Architect** — deterministic rendering with visible status, certainty, authority, and validation labels

These patterns are **not** part of Kristal artifact schemas and do not affect conformance, except where core/spec requirements already mandate behavior such as hash verification, signature verification, deterministic builds, atomic publication, or immutable artifact identity.

## Principles

* **Preserve artifact integrity where declared.**
* **Separate compilation from validation.**
* **Preserve ambiguity instead of erasing it.**
* **Represent partial, uncertain, disputed, or unresolved work explicitly.**
* **Quarantine poison inputs instead of infinite retry or silent drop.**
* **Bound resource usage with timeouts, quotas, and cancellation.**
* **Prefer immutable snapshots: new data produces new artifacts.**
* **Keep validation status, certainty level, authority channel, and reader policy visible.**
* **Avoid silently presenting working, disputed, or low-certainty material as recognized reference material.**

Kristal v5 does not treat every unresolved or invalid claim as a pipeline failure. A build may produce a Working Artifact containing unresolved, disputed, partial, or low-certainty assertions, provided their status is explicit and the selected policy allows them.

## 1) Circuit Breaker for SenTient Resolution Calls

### Concept

A circuit breaker prevents repeated calls to an unhealthy dependency, reducing cascading failures.

### Problem It Addresses

Resolution services can fail or degrade because of timeouts, high latency, partial outages, malformed input, overloaded models, unavailable indexes, or tenant-specific limits.

Without protection, a build pipeline can stall, retries can amplify load, and Orgo queues can back up.

### Recommended Approach

* Wrap SenTient calls behind a circuit breaker per tenant and per resolver endpoint.
* Prefer scoped breakers instead of one global breaker.
* Use a fallback that preserves unresolved ambiguity when policy allows.
* Record the circuit state in the build record or operational logs.
* Keep unresolved material explicit instead of dropping or pretending it is resolved.

### Suggested States

* **Closed** — normal operation
* **Open** — calls are skipped and fail quickly with a structured reason
* **Half-open** — limited probe calls test recovery

### Trigger Thresholds

Guidance:

* Open after N consecutive timeouts or dependency errors within a short window.
* Remain open for a cooldown interval.
* Enter half-open mode with limited probes.
* Close only after successful probes.

### Output Semantics

If SenTient fails and the pipeline policy allows unresolved preservation, emit a Structured Epistemic State or build output with:

```json
{
  "resolution_status": "unresolved",
  "assertion_status": "claimed",
  "certainty_level": "unknown",
  "warnings": [
    {
      "reason_code": "RESOLVE_DEP_UNAVAILABLE",
      "correlation_id": "..."
    }
  ]
}
```

If policy does not allow unresolved preservation, the stage may be blocked, but the failure should be recorded as a workflow or policy outcome, not as a corruption of the Kristal model.

### Pitfalls

* Hiding failures: always log and surface circuit state changes.
* Global breakers: avoid one tenant taking down all tenants.
* False certainty: never mark unresolved output as reviewed, validated, or recognized.
* Silent fallback: a fallback must preserve status labels.

## 2) Dead Letter Queue for Ingestion and Build Stages

### Concept

A Dead Letter Queue stores messages, inputs, or jobs that cannot be processed after bounded retries.

### Problem It Addresses

Poison inputs can block queues indefinitely if retried endlessly, or disappear if dropped.

Examples:

* corrupt PDFs
* malformed extractor output
* pathological resolution cases
* invalid schema instances
* missing authority registry references
* invalid signatures
* incompatible Runtime Pack manifests
* unsupported value types
* oversized source bundles

### Recommended Approach

Use staged queues for:

```text
ingest
extract
normalize
resolve
compile
review
validate
recognize
publish
package
distribute
```

Each stage should have:

* bounded retries
* exponential backoff with jitter
* structured error output
* DLQ on repeated failure
* ownership for triage
* retention policy

### DLQ Payload Requirements

Guidance payload:

```json
{
  "build_id": "build:...",
  "tenant_id": "tenant:...",
  "stage": "resolve",
  "input_ref": "sha256:...",
  "artifact_ref": null,
  "error_code": "RESOLVE_TIMEOUT",
  "error_message": "Bounded diagnostic message.",
  "attempt_count": 3,
  "first_seen_at": "2026-01-01T00:00:00Z",
  "last_seen_at": "2026-01-01T00:05:00Z",
  "correlation_id": "..."
}
```

### Operational Loop

DLQ items should create Orgo Cases or Tasks automatically for triage.

Triage outcomes:

* fix input and requeue
* adjust policy if the constraint was non-core
* split the input into smaller units
* preserve as unresolved or partial if allowed
* mark the assertion as rejected with recorded reason
* revoke or supersede an artifact if publication already occurred
* close as non-actionable with explanation

### Pitfalls

* DLQ as a graveyard: require ownership, SLAs, dashboards, and expiry.
* Infinite DLQ growth: apply retention, sampling, and aggregation for high-volume failures.
* Over-redaction: preserve enough diagnostic context to repair the issue.
* Under-redaction: avoid logging sensitive input content unnecessarily.

## 3) Timeouts and Cancellation

### Concept

Every stage must have bounded execution time to prevent resource exhaustion and queue collapse.

### Recommended Guidance by Stage

#### Ingestion

* Hard timeout.
* If source acquisition fails, emit structured failure.
* Do not create a partial source artifact unless the source boundary is explicit.

#### Extraction

* Hard timeout.
* Partial extractor output may be emitted only if schema-valid and explicitly marked partial.
* Claim-IR may be used as an extractor proposal profile, but it is not the universal required input format.

#### Normalization

* Hard timeout.
* If normalization is incomplete, preserve explicit warnings.
* Do not erase source identity or provenance.

#### Resolution

* Hard timeout.
* Preserve unresolved state when policy allows.
* Record warning and correlation ID.

#### Compilation

* Hard timeout.
* Safe abort if artifact construction cannot complete.
* If partial compilation is supported, it must produce a clearly marked Working Artifact, not a Reference Artifact.
* Do not publish incomplete packs as current.

#### Review

* Timeout produces a workflow status such as `review_status = "pending"` or `review_status = "blocked"`.
* Review timeout does not necessarily invalidate the compiled artifact.

#### Validation

* Timeout produces `validation_status = "in_review"` or `validation_status = "not_evaluated"` unless policy defines another outcome.
* Validation timeout does not automatically erase the Working Artifact.
* Validation timeout prevents recognition only when the selected recognition policy requires completed validation.

#### Recognition

* Timeout or authority unavailability produces `recognition_status = "none"` or `recognition_status = "under_review"`.
* Recognition by one authority channel must not be inferred from another.

#### Runtime Pack Compilation

* Hard timeout.
* Safe abort.
* No partial pack publication as active.
* A failed pack compile does not necessarily invalidate the source Exchange.

#### Distribution

* Retry with backoff.
* Never serve incomplete packs as current.
* Preserve previous active pack until the candidate pack satisfies activation requirements.

### Cancellation Propagation

If Orgo cancels a build:

* downstream workers should stop;
* final build status should be emitted;
* partial work should be marked clearly;
* partially signed or partially published artifacts must not be exposed as active Reference Artifacts or active Runtime Packs.

### Pitfalls

* Long-tail jobs blocking worker pools.
* Cancellation creating orphaned partial artifacts.
* Validation timeouts being misrepresented as rejection.
* Partial publication without clear status.
* Hidden retries causing non-deterministic outputs.

## 4) Quotas and Rate Limiting

### Concept

Quotas bound per-tenant resource usage to protect system stability.

### Recommended Quota Dimensions

* ingest volume: bytes/day, documents/day
* extraction calls: jobs/hour, tokens/day when applicable
* resolution calls: requests/minute, candidates/build
* validation complexity: assertions/build, references/assertion
* review workload: open cases/tenant, reviewers/stage
* build concurrency: active builds/tenant
* Runtime Pack compilation: MB/build, index size
* distribution bandwidth: MB/day/region
* offline cache size: per device, per tenant, per reader policy

### Enforcement Guidance

* Enforce at the Orgo orchestration boundary.
* Return structured errors with remediation hints.
* Prefer “burst then throttle” behavior over hard drops when possible.
* Rate limiting must not change artifact content.
* Scheduling changes must not affect deterministic build outputs.

### Pitfalls

* Non-deterministic throttling affecting output.
* One tenant starving shared workers.
* Silent throttling without user-visible queue status.
* Resource exhaustion in offline nodes because pack size was not bounded.

## 5) Backpressure and Queue Hygiene

### Concept

When downstream systems are slow, upstream systems must slow down safely.

### Recommended Approach

Use bounded queues with explicit backpressure signals to producers.

Recommended queues:

```text
ingest_queue
extract_queue
resolve_queue
compile_queue
review_queue
validate_queue
recognize_queue
package_queue
distribution_queue
```

Priority classes may include:

* security rebuilds
* revocations
* rollback / recovery
* small builds
* user-facing hotfixes
* scheduled batch builds
* experimental or research builds

### Backpressure Signals

Backpressure should include:

* queue depth
* estimated delay band
* admission status
* retry-after hints
* tenant quota state
* degraded dependency state

### Pitfalls

* Priority inversion.
* Large jobs starving small jobs.
* Hotfixes bypassing validation labels.
* Queues retaining stale builds after supersession.

## 6) Integrity-Critical Points

These are operational restatements of spec-level requirements.

### Hash Verification

When a content hash is declared, verification must confirm that the bytes match the declared hash before the object is accepted for the target operation.

### Signature Verification

When signatures are declared as required by policy, signature verification must confirm:

* signing target
* key id
* algorithm
* payload hash
* signature value
* trust root or authority channel
* expiration, where relevant
* revocation state, where relevant

### Atomic Publish

A release is either fully published and verifiable, or not published.

Partially published artifacts must not be exposed as active Reference Artifacts or active Runtime Packs.

### Immutable Snapshots

Updates produce new artifact identities.

New data should create a new Exchange, shard, federation manifest, Runtime Pack, or validation/recognition record as appropriate.

### Activation Requirements

A Runtime Pack is not active just because it exists on disk.

Before activation, the system should check the declared requirements for the selected channel, reader policy, and runtime environment.

If a candidate pack does not satisfy the requirements, the previous active pack remains in place and the candidate receives a clear status.

### Validation and Recognition

A validation failure does not necessarily prevent compilation of a Working Artifact.

It prevents the artifact or assertion from being represented as validated under that validation policy.

A recognition failure does not necessarily invalidate the artifact.

It prevents the artifact from being represented as recognized by the relevant authority channel.

## 7) Release Safety: Canary and Blue-Green Distribution

### Concept

Canary and blue-green strategies reduce blast radius when shipping new Runtime Packs or Reference Artifacts.

### Recommended Approach

#### Canary

Deliver a new pack to a small cohort, device class, tenant, or region first.

Observe health signals before wider rollout.

#### Blue-Green

Keep the previous pack live while the candidate pack is verified.

Switch traffic only when the candidate satisfies the selected activation requirements.

#### Rollback

Rollback should use a signed, pinned prior release whose status remains acceptable under the active downgrade and revocation policies.

Rollback must not activate an unsigned, revoked, or policy-incompatible artifact.

### Health Signals

* hash verification success rate
* signature verification success rate
* Runtime Pack activation success rate
* query error rate
* pack download success and latency
* device cache hit rates
* offline query success rate
* reader policy application errors
* authority registry lookup failures
* validation metadata load failures
* label rendering errors in Architect

### Pitfalls

* Rollback that bypasses revocation.
* Canary cohort hiding tenant-specific failures.
* Activating a candidate pack before reader policies are available.
* Serving a pack whose source Exchange status is unclear.

## 8) Observability: Correlation IDs and Structured Logs

### Required Operational Identifiers

Guidance:

```text
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
reader_policy_id
authority_channel_id
input_ref
tenant_id
correlation_id
```

### Log Events

Log events should be emitted for:

* stage start and end
* circuit breaker state transitions
* retries
* DLQ moves
* timeout events
* cancellation propagation
* validation status changes
* review status changes
* recognition status changes
* publication attempts
* Runtime Pack activation attempts
* reader-policy selection
* authority registry loading
* revocation checks
* rollback events

### Bounded Logging

Logs should include bounded summaries, not unlimited source payloads.

Validation, extraction, and resolution failures should include:

* reason code
* stage
* target ref
* policy ref, when applicable
* authority channel, when applicable
* correlation ID
* bounded diagnostic message

### Pitfalls

* Logging sensitive source content.
* Logging too little to repair failures.
* Missing authority channel context.
* Losing the difference between validation status and recognition status.

## 9) Suggested Minimal Error Taxonomy

### Ingestion and Extraction

```text
INGEST_PARSE_ERROR
INGEST_SOURCE_UNAVAILABLE
INGEST_TOO_LARGE
EXTRACT_TIMEOUT
EXTRACT_SCHEMA_INVALID
EXTRACT_PARTIAL_OUTPUT
```

### Resolution

```text
RESOLVE_TIMEOUT
RESOLVE_DEP_UNAVAILABLE
RESOLVE_AMBIGUOUS
RESOLVE_UNSUPPORTED_VALUE
RESOLVE_POLICY_BLOCKED
```

### Compilation

```text
COMPILE_FAILED
COMPILE_PARTIAL
COMPILE_SCHEMA_INVALID
COMPILE_HASH_MISMATCH
COMPILE_UNSUPPORTED_ARTIFACT_TYPE
```

### Review and Validation

```text
REVIEW_TIMEOUT
REVIEW_BLOCKED
VALIDATION_NOT_EVALUATED
VALIDATION_IN_REVIEW
VALIDATION_FAILED
VALIDATION_TIMEOUT
VALIDATION_POLICY_MISSING
VALIDATION_SCOPE_MISMATCH
CERTAINTY_TOO_LOW_FOR_POLICY
```

### Recognition and Authority

```text
AUTHORITY_REGISTRY_MISSING
AUTHORITY_CHANNEL_UNKNOWN
AUTHORITY_NOT_RECOGNIZED
RECOGNITION_IN_REVIEW
RECOGNITION_REJECTED
RECOGNITION_REVOKED
TRUST_ROOT_UNAVAILABLE
```

### Publication and Distribution

```text
PUBLISH_ATOMICITY_FAILED
PUBLISH_POLICY_BLOCKED
RUNTIME_PACK_COMPILE_FAILED
RUNTIME_PACK_ACTIVATION_BLOCKED
VERIFY_HASH_FAILED
VERIFY_SIGNATURE_FAILED
DISTRIBUTION_FAILED
ROLLBACK_BLOCKED
REVOCATION_CHECK_FAILED
```

### Resource Control

```text
QUOTA_EXCEEDED
RATE_LIMITED
QUEUE_BACKPRESSURE
TENANT_LIMIT_REACHED
TIMEOUT
CANCELLED
```

## 10) Build Record Guidance

A Kristal v5 build record should distinguish compilation, review, validation, recognition, publication, and activation.

Recommended shape:

```json
{
  "build_id": "build:2026-01-01T00:00:00Z:example",
  "schema_version": "5.0",
  "compile_status": "succeeded",
  "review_status": "pending",
  "validation_status": "not_evaluated",
  "recognition_status": "none",
  "publication_status": "not_published",
  "activation_status": "not_applicable",
  "working_outputs": [],
  "reference_outputs": [],
  "runtime_pack_outputs": [],
  "reason_codes": [],
  "created_at": "2026-01-01T00:00:00Z",
  "correlation_id": "..."
}
```

Allowed compile statuses:

```text
succeeded
failed
partial
cancelled
```

Allowed review statuses:

```text
not_required
pending
completed
blocked
cancelled
```

Allowed validation statuses:

```text
not_evaluated
in_review
validated
conditionally_validated
disputed
rejected
revoked
```

Allowed recognition statuses:

```text
none
under_review
recognized
conditionally_recognized
disputed
rejected
revoked
```

Allowed publication statuses:

```text
not_published
published
blocked
superseded
revoked
```

Allowed activation statuses:

```text
not_applicable
candidate
activated
blocked
superseded
revoked
```

## 11) Reader Policy Resilience

Reader policies may fail to load, become unavailable, or reference authority channels that are missing from the local registry.

### Recommended Behavior

If a selected reader policy cannot be loaded:

* do not silently switch to a broader policy;
* preserve the previous reader policy when available;
* show a clear unavailable status;
* log the reason code and correlation ID.

If an authority registry cannot be loaded:

* do not infer authority recognition;
* show artifacts with available local labels;
* mark recognition status as unavailable or unresolved;
* avoid presenting scoped validation as universal validation.

### Pitfalls

* Falling back from `validated_only` to `all_with_labels` without user awareness.
* Hiding labels because metadata is unavailable.
* Treating missing authority data as rejection.
* Treating missing authority data as recognition.

## 12) Architect Rendering Resilience

Architect must render Kristal content without hiding epistemic status.

### Recommended Behavior

Architect should preserve and display:

* assertion status
* certainty level
* validation status
* validated-as classification
* authority channel
* recognition status
* scope
* disputed status
* reader policy mode

### Rendering Degradation

If some metadata is unavailable:

* show the content with an explicit status marker;
* do not present it as validated or recognized;
* do not flatten scoped validation into universal truth;
* do not hide that a claim is fictional, mythological, disputed, rejected, or validated only under a specific authority channel.

### Pitfalls

* Simplifying labels away for readability.
* Showing only the selected answer without authority context.
* Merging multiple authority positions into one statement.
* Treating absence of metadata as high confidence.

## Appendix: Recommended Least-Worst Defaults

* Circuit breaker enabled for SenTient by default.
* DLQs enabled for every pipeline stage.
* Hard timeouts for every stage.
* Quotas enforced at Orgo admission control.
* Compilation may produce Working Artifacts when validation is incomplete or unavailable, if policy allows.
* Reference Artifacts require explicit recognition or validation according to policy.
* Runtime Pack activation requires declared integrity and compatibility checks.
* Canary rollout for Runtime Packs before broad distribution.
* Previous active pack remains in place when candidate activation requirements are not satisfied.
* Reader policy fallback must never silently broaden visibility.
* Architect must preserve status, certainty, authority, and validation labels.
