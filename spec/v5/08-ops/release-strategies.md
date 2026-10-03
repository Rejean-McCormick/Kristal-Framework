# Release Strategies for Kristal Runtime Packs (Blue/Green, Canary)

## Status

Draft — non-normative operational guidance for Kristal v5.

## Purpose

This document defines operational release strategies for distributing **Kristal Runtime Packs** to online, offline, constrained, or intermittently connected environments.

It provides recommended operational patterns for Orgo as the control plane and Konnaxion as the distribution and client-facing layer.

The goals are to preserve:

* deterministic artifacts;
* required integrity verification;
* auditable release records;
* downgrade and rollback safety;
* clear artifact status;
* validation, certainty, authority, and reader-policy labels.

This document is **non-normative**. It does not change Kristal artifact formats, schema conformance, validation policy, authority recognition, or reader-policy semantics.

It assumes channels may use a signed channel index, such as `pack_index.json`, as the primary control surface for rollout, rollback, staged activation, and client selection.

---

# 1. Terms and goals

## 1.1 Terms

* **Pack**: a Kristal Runtime Pack artifact, including manifest and payloads.
* **Pack version**: a monotonic version within a channel used for activation and downgrade prevention, commonly recorded as `pack_version`.
* **Runtime Pack ID**: content-addressed identifier for an immutable Runtime Pack.
* **Source artifact status**: whether the pack derives from a `working` artifact, `reference` artifact, or other declared source status.
* **Release**: a versioned publication event, normally recorded by Orgo, referencing a pack, channel scope, signer, status, and policy context.
* **Channel**: a distribution target grouping, such as tenant, environment, region, device cohort, authority channel, or reader-policy channel.
* **Channel pack index**: a signed per-channel index, for example `pack_index.json`, containing channel metadata, latest pointers, pinned pointers, minimum allowed version, revoked pack IDs, reader-policy constraints, and activation rules.
* **Cohort**: a deterministic subset of a channel, such as 1% of devices.
* **Reader policy**: a declared policy controlling which data is visible to a user or application.
* **Authority channel**: a scoped authority source whose recognition, validation, or publication status may affect reader-policy selection.
* **Activation**: the local switch from one active Runtime Pack to another.

## 1.2 Goals

Release strategies SHOULD:

* minimize blast radius of a bad pack release;
* prevent activation of packs that fail required integrity, schema, compatibility, or policy checks;
* support explicit rollback without creating downgrade vulnerabilities;
* maintain auditable linkage from build to release to distribution index to device state;
* preserve validation labels, certainty labels, authority-channel labels, source lineage, and reader-policy context;
* allow offline clients to make deterministic activation decisions from locally available policy data.

A “bad pack” may mean:

* corrupted or incomplete payloads;
* invalid signatures or hashes;
* incompatible query contract;
* broken indexes;
* unacceptable performance;
* missing labels required by reader policy;
* missing authority registry or revocation data required by activation policy;
* incorrect pack construction relative to declared policies.

It does not mean that all contained assertions are globally false or true. Kristal v5 separates Runtime Pack integrity from semantic validation, authority recognition, and certainty.

---

# 2. Release invariants

These invariants SHOULD hold regardless of rollout strategy.

## 2.1 Immutable pack identity

A `runtime_pack_id` identifies immutable content.

Implementations MUST NOT “fix” a Runtime Pack in place.

If the manifest, payloads, indexes, labels, policies, or metadata change, the result is a new Runtime Pack with a new content-addressed identity.

## 2.2 Required verification

If signatures, hashes, trust roots, authority registry references, revocation requirements, or compatibility requirements are declared by the active channel policy, every distribution node and client SHOULD verify them before activation.

If a signed channel index is used, clients SHOULD verify the index using pinned trust roots or an Authority Registry policy before applying it.

A pack that fails required verification MUST NOT become active for that channel.

It MAY remain inspectable as an inactive or diagnostic candidate if the interface clearly marks it as not accepted under the selected policy.

## 2.3 Activation gating and atomic activation

Activation SHOULD occur only after required checks pass.

Typical checks include:

* manifest schema validity;
* content hash verification;
* payload file presence;
* signature verification, if required;
* authority registry availability, if required;
* revocation policy evaluation, if required;
* downgrade and rollback policy evaluation;
* query contract compatibility;
* reader-policy compatibility;
* Runtime Pack construction-policy compatibility;
* required label availability;
* local smoke tests.

Activation SHOULD be an atomic switch from old to new.

Partial activation SHOULD NOT occur.

## 2.4 Auditable release records

Every activation SHOULD be traceable to:

* `channel_id`;
* `runtime_pack_id`;
* `pack_version`;
* `source_exchange_ref`;
* `source_artifact_status`;
* signer;
* authority channel, if applicable;
* reader policy, if applicable;
* activation policy;
* timestamp;
* local verification result;
* Orgo release record, if present.

## 2.5 Explicit rollback and downgrade policy

Downgrades SHOULD be prevented by default.

Rollback SHOULD be explicit, auditable, deterministic, and revocation-aware.

A client SHOULD NOT activate an older pack unless the channel index, local policy, or operator action explicitly authorizes rollback.

## 2.6 Label preservation

Release and activation procedures MUST NOT erase or flatten Kristal v5 epistemic labels.

The following labels, when present and required by reader policy, SHOULD remain traceable after release:

* `artifact_status`;
* `assertion_status`;
* `validation_status`;
* `certainty_level`;
* `validated_as`;
* `authority_channel`;
* `recognition_status`;
* `scope`;
* `provenance_refs`;
* `evidence_refs`;
* `lineage`.

A release process MUST NOT present a pack derived from a working artifact as a reference artifact unless a valid recognition or release policy explicitly supports that status.

---

# 3. Channel pack index

## 3.1 Purpose

A channel pack index is a signed control object used to determine which Runtime Pack is current, staged, pinned, revoked, or allowed for a given channel.

Common filename:

```text
pack_index.json
```

The exact schema is deployment-specific unless standardized by a separate profile.

## 3.2 Recommended contents

A channel pack index SHOULD contain:

* `channel_id`;
* `channel_scope`;
* `latest`;
* `pinned`;
* `staged`;
* `canary`;
* `minimum_allowed_version`;
* `revoked`;
* `reader_policy_refs`;
* `authority_registry_ref`;
* `activation_policy_ref`;
* `rollback_policy_ref`;
* `updated_at`;
* `signer_key_id`;
* `signatures`.

## 3.3 Latest pointer

`latest` identifies the pack or packs that should normally become active for the channel.

## 3.4 Pinned pointer

`pinned` identifies known-good packs that may be used for rollback, recovery, or offline continuity.

A pinned pack is not automatically current. It is a controlled fallback target.

## 3.5 Staged pointer

`staged` identifies candidate packs that may be downloaded, verified, warmed up, or tested before activation.

## 3.6 Canary pointer

`canary` identifies packs that should be activated only by selected cohorts.

Cohort selection SHOULD be deterministic.

## 3.7 Minimum allowed version

`minimum_allowed_version` prevents activation of packs below a declared version threshold.

Clients SHOULD persist the highest activated version per channel and apply local anti-downgrade policy alongside the signed channel index.

## 3.8 Revoked packs

`revoked` identifies pack IDs or versions that must not be activated under the channel policy.

Revocation SHOULD include a reason code and effective time.

---

# 4. Blue/Green releases

## 4.1 Concept

Blue/Green releases maintain two production slots per channel:

* **Blue**: current active pack version;
* **Green**: new candidate pack version.

Devices or nodes switch to Green only after Green has passed required checks under the channel policy.

## 4.2 Procedure

### Step 1 — Publish Green

Orgo publishes a release record referencing:

* new `runtime_pack_id`;
* `pack_version`;
* source artifact references;
* source artifact status;
* channel scope;
* signer;
* build record;
* declared Runtime Pack policies;
* reader-policy references;
* authority registry reference, if applicable.

Konnaxion replicates pack payloads to the Green slot or staged cache location.

### Step 2 — Verify at rest

Edge nodes or devices verify:

* manifest schema validity;
* payload file presence;
* payload hashes;
* signatures, if required;
* channel index signature, if used;
* Authority Registry reference, if required;
* revocation policy, if required;
* query contract compatibility;
* Runtime Pack policy compatibility;
* reader-policy compatibility;
* required label availability.

Any required verification failure blocks activation.

The candidate may remain staged for diagnostics.

### Step 3 — Warm-up and readiness checks

Run pack-local checks such as:

* query smoke tests;
* pagination checks;
* join behavior checks;
* reader-policy filter checks;
* authority-channel filter checks;
* validation-status and certainty-level filter checks;
* memory footprint thresholds;
* latency thresholds;
* payload integrity re-checks where appropriate.

Outcomes SHOULD be logged with correlation IDs.

### Step 4 — Switch traffic through signed channel index

Update the channel pack index:

* set `latest` to the Green pack;
* optionally keep Blue in `pinned`;
* update `minimum_allowed_version` if needed;
* add revoked pack IDs if needed;
* preserve reader-policy and authority-policy metadata.

Sign the updated index.

Clients verify the updated index before applying it.

Devices activate Green using an atomic switch.

### Step 5 — Post-switch monitoring

Observe:

* verification failures;
* activation failures;
* query error rates;
* pagination errors;
* unsupported filter errors;
* reader-policy mismatches;
* latency;
* memory pressure;
* pack download failures;
* unexpected rollback attempts.

If thresholds fail, trigger explicit rollback.

## 4.3 Advantages

Blue/Green releases provide:

* simple operational model;
* predictable rollback target;
* clean staging;
* offline-friendly activation;
* easy auditability.

## 4.4 Pitfalls

Blue/Green releases may require:

* additional storage;
* explicit split-brain tolerance for offline devices;
* clear audit records for asynchronous activation;
* careful handling of reader-policy and authority-policy changes.

Offline devices may remain on Blue longer than online devices. This is acceptable if the pack remains valid under channel policy.

---

# 5. Canary releases

## 5.1 Concept

Canary releases roll out a new pack to a small cohort first, observe behavior, then expand.

Canary is recommended for high-risk changes, such as:

* new Runtime Pack construction policies;
* new query contract versions;
* new reader-policy filtering;
* new authority-channel filtering;
* new validation or certainty materialization;
* large dataset changes;
* new client versions;
* new compression or index formats.

## 5.2 Procedure

### Step 1 — Create cohorts

Example stages:

* 1%;
* 10%;
* 50%;
* 100%.

Cohorts SHOULD be stable and deterministic.

Example cohort rule:

```text
hash(device_id) mod 100 < cohort_percentage
```

### Step 2 — Publish candidate pack

Publish and stage the pack as in Blue/Green.

The pack should be available before cohort activation begins.

### Step 3 — Update channel index for canary

Update the channel pack index so only selected cohorts resolve current pack selection to the canary pack.

The distribution index is the primary control point for staged releases.

The index update SHOULD include:

* canary pack pointer;
* cohort rule;
* cohort percentage;
* observation window;
* rollback target;
* relevant reader policy;
* relevant authority policy.

Sign and distribute the updated index.

Clients verify the index before applying it.

### Step 4 — Activation gating

Canary devices verify:

* integrity;
* schema validity;
* contract compatibility;
* reader-policy compatibility;
* authority registry requirements;
* revocation requirements;
* local smoke tests.

Activation occurs only if required checks pass.

### Step 5 — Promote

After the observation window, expand cohorts by updating and signing the channel index.

Promotion steps SHOULD be auditable and deterministic.

### Step 6 — Abort and rollback

If health metrics fail:

* stop promotion;
* revert affected cohorts to previous index pointers;
* mark the failed pack as blocked or revoked if appropriate;
* preserve release and activation audit records;
* avoid silent downgrade behavior.

## 5.3 Metrics to watch

Canary metrics SHOULD include:

* manifest verification failures;
* payload hash verification failures;
* index signature verification failures;
* Runtime Pack activation failures;
* query error rates;
* pagination errors;
* unsupported filter errors;
* reader-policy mismatch errors;
* authority-registry mismatch errors;
* validation-status filter errors;
* certainty-level filter errors;
* median and P95 query latency;
* memory pressure;
* out-of-memory events;
* pack download failures;
* excessive download size complaints;
* unexpected cardinality or pagination behavior.

## 5.4 Pitfalls

Canary releases require:

* stable cohort assignment;
* clean cohort targeting;
* auditable index updates;
* compatible offline behavior.

Offline devices may skip cohorts or activate later. Treat cohort targeting as best-effort and rely on activation-time verification, local checks, and audit records.

---

# 6. Rollback and downgrade safety

Rollback is operationally necessary.

Uncontrolled downgrade is a security and integrity risk.

## 6.1 Default anti-downgrade rule

Clients SHOULD NOT activate a pack whose `pack_version` is lower than the currently active pack for the same channel unless an explicit rollback policy authorizes it.

Clients SHOULD persist:

* active pack ID;
* active pack version;
* highest activated pack version;
* active channel ID;
* activation timestamp;
* activation policy;
* rollback authorization, if any.

## 6.2 Rollback targets

Preferred rollback targets are:

* a pinned known-good pack;
* the last-known-good previously active pack;
* a recovery pack explicitly authorized by policy.

A rollback target must still satisfy applicable verification, revocation, and activation requirements.

## 6.3 Minimum version pin

A channel index SHOULD maintain:

```text
minimum_allowed_version
```

Clients SHOULD NOT activate packs below this minimum, even if cached, unless an explicit emergency policy allows it.

## 6.4 Revocation

If a pack is discovered to be invalid, vulnerable, corrupted, mislabeled, or unsafe to activate:

* add it to `revoked` in the signed channel index;
* update revocation lists if used;
* raise `minimum_allowed_version` if needed;
* publish a replacement pack when appropriate.

## 6.5 Rollback audit

Rollback events SHOULD record:

* rollback reason;
* operator or authority;
* previous pack;
* rollback target;
* channel ID;
* device or cohort scope;
* timestamp;
* policy reference;
* verification result.

---

# 7. Offline and constrained environments

## 7.1 Activation is local and asynchronous

Offline devices may:

* download a pack later than publication;
* activate it later than download;
* miss intermediate canary stages;
* remain on older packs for extended periods.

Therefore:

* required verification SHOULD occur at activation time;
* activation decisions SHOULD be stored locally;
* devices SHOULD record audit markers;
* clients SHOULD avoid silent downgrade.

Recommended audit marker:

```text
channel_id + runtime_pack_id + pack_version + activation_policy + timestamp
```

## 7.2 Holding behavior

If a device is offline and only has older packs available, and rollback is not explicitly authorized, the correct behavior is to hold the current active pack rather than silently downgrade.

If the current pack is revoked and no valid replacement is available, the client SHOULD expose a clear inactive, degraded, or unavailable status according to deployment policy.

## 7.3 Storage constraints

If devices cannot hold Blue and Green simultaneously, they SHOULD retain at minimum:

* current active manifest;
* previous active manifest, if available;
* signatures;
* pack index material;
* revocation material;
* enough metadata to justify activation and rollback decisions.

Deployments MAY implement a checkpoint pack strategy, retaining last-known-good payloads where feasible.

## 7.4 Delta updates

If packs are large, deployments MAY use delta distribution at the transport layer.

The final reconstructed payloads MUST match the hashes declared in the Runtime Pack manifest.

Delta transport MUST NOT change Runtime Pack identity.

---

# 8. Suggested control-plane data model

A practical Orgo/Konnaxion release system typically maintains the following records.

## 8.1 Build Record

```text
BuildRecord(
  build_id,
  runtime_pack_id,
  source_exchange_ref,
  source_artifact_status,
  compiler_version,
  config_hash,
  policies,
  inputs,
  signatures,
  compile_status,
  validation_status,
  recognition_status,
  created_at
)
```

## 8.2 Release Record

```text
ReleaseRecord(
  release_id,
  channel_id,
  runtime_pack_id,
  pack_version,
  signing_key_id,
  source_artifact_status,
  reader_policy_refs,
  authority_registry_ref,
  published_at,
  status
)
```

## 8.3 Channel Pack Index

```text
ChannelPackIndex(
  channel_id,
  latest,
  staged,
  canary,
  pinned,
  minimum_allowed_version,
  revoked,
  reader_policy_refs,
  authority_registry_ref,
  signature,
  signer_key_id,
  updated_at
)
```

## 8.4 Device State

```text
DeviceState(
  device_id,
  channel_id,
  active_pack_id,
  active_pack_version,
  highest_activated_pack_version,
  active_reader_policy,
  authority_registry_ref,
  last_verified_at,
  verification_status,
  activation_status
)
```

These models are illustrative. Exact implementation is system-specific.

---

# 9. Recommended default strategy

For most deployments:

* use Blue/Green as the default;
* add Canary for high-risk changes;
* keep a pinned known-good pack during the rollback window;
* sign channel pack indexes;
* verify required material before activation;
* preserve activation audit records.

Canary is especially useful for:

* new portable policies;
* new ordering or row-grouping strategies;
* new membership filters;
* new bitmap formats;
* large schema changes;
* new query extensions;
* new reader-policy behavior;
* new authority-channel filters;
* new validation or certainty materialization;
* new client versions.

---

# 10. Checklist

## 10.1 Blue/Green

* [ ] Pack published and staged.
* [ ] Manifest schema verified.
* [ ] Payload hashes verified.
* [ ] Signatures verified if required.
* [ ] Authority Registry available if required.
* [ ] Revocation policy evaluated if required.
* [ ] Query contract compatibility checked.
* [ ] Runtime Pack policy compatibility checked.
* [ ] Reader-policy compatibility checked.
* [ ] Required labels available.
* [ ] Smoke tests pass.
* [ ] Channel index updated and signed.
* [ ] Green set as `latest`.
* [ ] Blue retained as pinned rollback target.
* [ ] Monitoring and rollback window defined.
* [ ] `minimum_allowed_version` updated when needed.
* [ ] `revoked` updated when needed.
* [ ] Activation audit records preserved.

## 10.2 Canary

* [ ] Cohorts stable and targetable.
* [ ] Candidate pack published and staged.
* [ ] Canary targeting represented in signed channel index.
* [ ] Observation metrics defined.
* [ ] Promotion steps defined.
* [ ] Rollback target defined.
* [ ] Abort path defined.
* [ ] Offline activation still verifies required material.
* [ ] Smoke tests include reader-policy and query behavior.
* [ ] Audit records preserve cohort, pack, channel, signer, and policy context.

---

# 11. Summary

Kristal v5 Runtime Pack releases are operational events over immutable artifacts.

Blue/Green provides a clean default rollout strategy.

Canary reduces risk for high-impact changes.

Rollback is allowed, but it must be explicit, auditable, policy-bound, and downgrade-safe.

Release strategy does not decide what is universally true. It decides which immutable pack is active for a channel, under which policy, with which verification, reader-policy, authority, validation, certainty, and audit context.
