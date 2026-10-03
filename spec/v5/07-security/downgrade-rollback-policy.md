# Downgrade and Rollback Policy (Kristal v5)

## Status

Draft (normative)

## Purpose

Define how Kristal v5 distributors, clients, Runtime Pack consumers, and authority-channel-controlled distribution flows prevent:

* **downgrade attacks**: maliciously providing an older, vulnerable, revoked, or compromised artifact;
* unsafe **rollbacks**: unintended reversion to older packs due to caching, sync conflicts, stale indexes, or operator error;
* authority-channel confusion: applying trust roots, reader policies, activation rules, or recognition status from one channel to another;
* silent substitution: replacing an artifact with another artifact using the same version label but a different content identity.

This policy is required to make signed Runtime Packs, Exchange release pointers, authority-recognized references, and offline Kristal distributions safe to use at scale, especially in offline or intermittently connected environments.

This policy protects artifact identity, distribution integrity, and activation state. It does not assert that all content inside an artifact is universally true, high-certainty, or recognized by every authority channel.

---

## Scope

In scope:

* Versioning and monotonic update rules for Runtime Packs and Exchange release pointers
* Minimum metadata required to enforce downgrade and rollback prevention
* Client enforcement behavior: accept, reject, hold, activate, rollback, or quarantine
* Offline-friendly mechanisms that do not rely on live services at activation time
* Planned rollback and emergency rollback
* Interaction with pinned trust roots and offline revocation data where available
* Channel-scoped activation rules for tenants, environments, regions, audiences, authority channels, and reader policies
* Relationship between Runtime Pack activation, artifact verification, authority recognition, validation status, and reader policy

Out of scope:

* Key lifecycle procedures beyond what is required for downgrade and rollback enforcement
* Full content trust model beyond artifact identity, signature verification, pinned trust roots, and declared policy
* UI/UX specifics
* Determining whether an assertion is true, high-certainty, validated, rejected, mythological, fictional, disputed, or visible under a given reader policy
* Defining authority-channel governance rules beyond the metadata required for enforcement

See also:

* `01-core-spec/signatures-trust.md`
* `01-core-spec/authority-recognition.md`
* `02-schemas/runtime-pack-manifest.schema.json`
* `02-schemas/exchange-manifest.schema.json`
* `02-schemas/authority-registry.schema.json`
* `02-schemas/reader-policy.schema.json`
* `06-integration/konnaxion-distribution-contract.md`
* `08-ops/release-strategies.md`

---

## Normative keywords

MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as normative requirement keywords.

---

## Core concepts

### Artifact types

Rollback and downgrade policies apply to the following Kristal v5 artifacts:

* **Working Exchange**: a compiled, portable artifact that may contain unvalidated, partially validated, research, disputed, low-certainty, fictional, mythological, or otherwise scoped material.
* **Reference Exchange**: an Exchange that is recognized under one or more authority channels or reader policies for a declared scope.
* **Runtime Pack**: a derived, offline-usable distribution payload identified by `runtime_pack_id` and scoped by channel, version, source Exchange, build, and reader policy context.
* **Exchange Shard**: a scoped subset of Exchange content, identity, provenance, validation references, and recognition references.
* **Exchange Federation**: a manifest that composes shards or Exchanges without silently merging identities, authorities, scopes, or disagreements.
* **Authority Registry**: a registry of authority channels, trust roots, scopes, validation policies, and recognition relationships.
* **Authority Recognition**: a scoped record saying that an authority channel recognizes, conditionally recognizes, rejects, revokes, or classifies a target.
* **Validation Decision**: a scoped decision saying that an artifact, shard, assertion, Runtime Pack, or authority channel has a validation status under a declared policy.
* **Reader Policy**: a policy that determines which authority channels, certainty levels, validation statuses, and artifact statuses are visible or trusted in a reader or runtime context.

Rollback and downgrade policies apply most critically to Runtime Packs, but SHOULD also apply to Exchange release pointers, federation manifests, authority registries, validation decisions, recognition records, and reader policies where stale or substituted versions could affect trust or visibility.

---

## Terminology mapping

To avoid ambiguity:

* **`release_id`**: the monotonic, channel-scoped version identifier used by a distribution channel.
* **`pack_version`**: the Runtime Pack’s monotonic version within a channel.
* **Runtime Pack release**: `release_id == pack_version`.
* **Exchange release pointer**: a channel-scoped pointer to a Working Exchange or Reference Exchange.
* **Reference pointer**: a pointer to an artifact recognized under a declared authority channel or reader policy.
* **Channel**: a distribution and activation context scoped by tenant, environment, region, audience, authority channel, and optionally reader policy.
* **Activation**: the local act of making a Runtime Pack or pointer active for a client, node, runtime, or reader policy.
* **Rollback**: an explicit, authorized activation of an older version.
* **Downgrade**: unauthorized activation or acceptance of an older version when a newer valid version is already known or active.
* **Reissue**: a signed, policy-authorized replacement of a pack or pointer using the same version label but a different content identity.
* **Hold state**: a non-activation state in which the client keeps the current active artifact and records why the candidate was not activated.
* **Quarantine state**: a state in which a candidate artifact is preserved for diagnostics or audit but cannot be activated under the active policy.

---

## Threat model

This policy defends against:

* a malicious distributor or compromised mirror serving old artifacts;
* a network attacker replaying older signed artifacts;
* offline caches or sync conflicts reactivating older Runtime Packs;
* operator mistakes pushing the wrong version to a region, audience, or channel;
* “same version, different bytes” substitution;
* trust-root confusion between tenants, environments, regions, audiences, or authority channels;
* reader-policy confusion, where a pack intended for one visibility policy is activated under another;
* stale authority registries, validation decisions, recognition records, or revocation lists;
* accidental use of a Working Exchange as if it were a Reference Exchange.

This policy assumes:

* signature verification exists for artifacts that declare signatures;
* trust roots are pinned per channel and can be verified offline;
* Runtime Pack distribution is offline-friendly;
* revocation data MAY or MAY NOT be available offline;
* clients may operate for long periods without network access;
* different reader policies may intentionally expose different subsets of validated, uncertain, disputed, fictional, mythological, research, or low-certainty material.

This policy does not assume that a valid signature means universal truth, universal validation, or maximum certainty.

---

## Cryptographic and integrity baseline

### Supported signature algorithms

An implementation MUST support:

* `ed25519`

An implementation MAY support additional algorithms through profiles, but such algorithms MUST NOT replace `ed25519` as the mandatory-to-implement baseline for Kristal v5 signature verification.

### Hashing baseline

Where a hash object is used, it MUST use:

```json
{
  "alg": "sha256",
  "value": "<hex>"
}
```

The field name MUST be `alg`, not `algo`.

### Canonicalization baseline

The default Kristal v5 canonicalization profile is:

```text
kristal.v5:jcs-rfc8785
```

RDF-specific integrity profiles MAY define additional canonicalization rules for RDF datasets, but they MUST NOT alter the core JSON artifact identity rules unless explicitly declared by that profile.

---

## Runtime Pack signing scope

A Runtime Pack MUST be distributable as an integrity-protected bundle.

At minimum:

* the Runtime Pack manifest MUST be signed when the channel policy requires signed packs;
* the Runtime Pack manifest MUST include hashes for all payload files it declares;
* consumers MUST verify declared payload file hashes when the active policy requires payload integrity;
* signatures MUST be excluded from the hash target;
* self-identity fields MUST be excluded from their own hash targets.

This ensures offline caches cannot silently substitute payload files while keeping the manifest identity or signature apparently valid.

---

## Required metadata for enforcement

### A. Runtime Pack identifiers

Each Runtime Pack bundle MUST be uniquely identified by:

* `runtime_pack_id`
* `runtime_pack_version`
* `pack_version`
* `source_exchange_ref`
* `source_artifact_status`
* `build.build_id`
* `channel_id`
* `content_hash`
* `signatures`, when required by policy

`source_artifact_status` MUST distinguish at least:

```text
working
reference
deprecated
revoked
```

A Runtime Pack derived from a Working Exchange MUST NOT be represented as derived from a Reference Exchange unless an authority recognition or validation decision supports that status.

---

### B. Channel and trust scoping

Packs MUST be distributed through channels scoped at minimum by:

* `tenant_id`
* `environment`

Channels SHOULD also declare:

* `region`
* `audience_segment`
* `authority_channel`
* `reader_policy_id`
* `scope.domain`
* `scope.subdomain`
* `distribution_purpose`

A client MUST NOT mix trust roots, version state, activation rules, reader policies, authority-channel rules, or rollback permissions across channels unless explicitly configured.

---

### C. Channel distribution index

Clients SHOULD consume a signed channel index as the primary “what to install or activate” control plane.

Example filename:

```text
pack_index.json
```

If present, the channel index MUST be verified using the channel’s pinned trust roots before it can satisfy any policy requiring a verified index.

A channel index SHOULD contain, at minimum:

* `channel_id`
* `tenant_id`
* `environment`
* optional `region`
* optional `audience_segment`
* optional `authority_channel`
* optional `reader_policy_id`
* `latest` pointer or pointers
* optional `pinned` pointer or pointers
* optional `minimum_allowed_version`
* optional `maximum_allowed_version`
* optional `revoked` list or reference to revocation artifacts
* optional staged pointers or cohorts
* optional `reissue_allowed`
* optional `reissue_flags`
* optional rollback authorization records or references
* `created_at`
* `expires_at`, recommended
* `content_hash`
* `signatures`

A channel index MUST NOT be used as authority recognition unless an authority-recognition policy explicitly defines that behavior.

---

### D. Offline revocation data

If an offline revocation artifact is provided, then clients MUST treat it as policy input for activation decisions.

Example artifact:

```text
revocations.json
```

If the active channel policy requires revocation checking and no acceptable revocation data is available offline, the client MUST NOT activate a candidate that depends on that revocation check.

The client MAY keep the current active pack and enter a hold state.

Recommended revocation metadata:

* `revocation_id`
* `target_ref`
* `target_level`
* `revocation_status`
* `authority_channel`
* `scope`
* `issued_at`
* `expires_at`
* `reason`
* `signatures`

---

### E. Timestamps and signatures

Timestamps such as `created_at`, `issued_at`, and `expires_at` MAY be present for audit, validity windows, and policy evaluation.

Timestamps MUST NOT affect content-addressed IDs unless a profile explicitly includes them in the identity target.

Signature and attestation material MUST be excluded from hash targets wherever it appears.

---

## Monotonic version formats

An implementation MUST choose one monotonic scheme and enforce it consistently per channel.

Allowed schemes:

* integer sequence, recommended;
* semantic version with strict deterministic ordering rules;
* hybrid integer sequence plus human label.

Examples:

```text
42
43
44
```

```text
5.0.0+channel.42
5.0.0+channel.43
```

Comparison MUST be deterministic and documented.

A version string MUST NOT be compared lexically unless the chosen scheme explicitly defines lexical ordering as valid.

---

## Client state requirements

Clients MUST persist per channel:

* `highest_activated_pack_version[channel]`
* `highest_seen_pack_version[channel]`
* `current_active_pack_version[channel]`
* `current_active_runtime_pack_id[channel]`
* `current_reader_policy_id[channel]`, when applicable
* `current_authority_channel[channel]`, when applicable
* last successful identity verification metadata
* last successful signature verification metadata
* last successful index verification metadata
* last revocation-check status
* last activation decision
* rollback authorization state, if applicable

Clients SHOULD also persist:

* `highest_seen_release_id[channel]`
* `last_reference_exchange_id[channel]`
* `last_working_exchange_id[channel]`
* `last_authority_registry_id[channel]`
* `last_reader_policy_hash[channel]`
* correlation IDs for activation, rollback, and rejection events

Client state MUST be scoped by channel. It MUST NOT be globally reused across unrelated tenants, environments, regions, audiences, authority channels, or reader policies.

---

## Client enforcement rules

### 1. Basic rule: never activate a lower version without authorization

A client MUST NOT activate a Runtime Pack with a lower `pack_version` than the highest previously activated version in the same channel unless an explicit rollback authorization permits it.

A client SHOULD NOT activate a Runtime Pack lower than `highest_seen_pack_version[channel]` unless:

* a rollback authorization permits it; or
* a policy explicitly allows activation from cache under a constrained offline mode.

---

### 2. Verification before activation

Before switching active packs, clients MUST evaluate the checks required by the active channel policy.

Depending on policy, checks MAY include:

* channel index signature verification;
* Runtime Pack manifest signature verification;
* Runtime Pack payload hash verification;
* source Exchange identity verification;
* source Exchange status check;
* authority registry verification;
* authority recognition verification;
* validation decision verification;
* reader policy verification;
* revocation status check;
* version monotonicity check;
* rollback authorization check;
* reissue authorization check.

If a required check is not satisfied, the candidate MUST NOT be activated under that policy.

The client MAY preserve, inspect, cache, or quarantine the candidate if policy allows.

---

### 3. Atomic activation

Activation MUST be an atomic switch from old pack to new pack.

A client MUST NOT partially activate a Runtime Pack.

If activation fails after verification but before completion, the previous active pack SHOULD remain active.

If the previous active pack is unavailable, the client SHOULD enter hold state or recovery state according to deployment policy.

---

### 4. Channel isolation

Downgrade and rollback decisions MUST be scoped by channel.

At minimum, channel scope includes:

```text
tenant_id
environment
```

When present, the following MUST also participate in channel isolation:

```text
region
audience_segment
authority_channel
reader_policy_id
scope.domain
scope.subdomain
```

A client MUST NOT activate a pack from one channel into another channel unless a signed channel policy explicitly allows cross-channel use.

---

### 5. Equal version, different identity

If a client receives a pack with the same `pack_version` but a different `runtime_pack_id`, the client MUST treat this as a substitution conflict unless an explicit reissue authorization is present in a verified channel index or equivalent signed policy artifact.

Reissue authorization MUST bind:

* `channel_id`
* `pack_version`
* previous `runtime_pack_id`, if known
* allowed replacement `runtime_pack_id`
* reason
* issuer
* issued_at
* optional `expires_at`
* signatures

Clients MUST log reissue activations.

Clients MUST NOT silently accept same-version identity changes.

---

### 6. Revocation-aware blocking

If a verified channel index includes a `revoked` list or references a revocation artifact, clients MUST NOT activate any target revoked under the active channel policy.

If `minimum_allowed_version` is present in a verified index, clients MUST NOT activate packs below that minimum unless an explicit rollback authorization overrides the minimum and the policy allows that override.

If a source Exchange, Runtime Pack, validation decision, authority recognition, reader policy, or key is revoked, the client MUST evaluate the revocation according to active policy before activation.

---

### 7. Reader policy compatibility

A Runtime Pack MAY be built for a specific reader policy or set of reader policies.

If the Runtime Pack declares `reader_policy_refs`, a client MUST NOT activate it under an incompatible reader policy unless a compatibility policy explicitly allows it.

A Runtime Pack built for a permissive research or creative policy MUST NOT be activated as a strict `reference_only` or `validated_only` pack unless the pack also satisfies that stricter policy.

A Runtime Pack built for `validated_only` view MAY contain assertions validated at different certainty levels, provided every visible assertion satisfies the active reader policy.

---

### 8. Authority-channel compatibility

If a Runtime Pack, Exchange, shard, federation, recognition, or validation decision declares an `authority_channel`, the client MUST evaluate whether that channel is allowed by the active distribution or reader policy.

Recognition by one authority channel MUST NOT be treated as recognition by another authority channel unless an authority-recognition relationship explicitly supports that interpretation.

---

### 9. Working versus reference artifacts

A Runtime Pack derived from a Working Exchange MAY be activated under research, review, diagnostic, archival, or creative policies if allowed.

A Runtime Pack derived from a Working Exchange MUST NOT be activated as a Reference Exchange Runtime Pack under a strict reference policy unless a recognized authority channel or validation policy supports that status.

Clients SHOULD expose whether the active pack is derived from:

```text
working_exchange
reference_exchange
mixed_federation
research_bundle
archival_bundle
```

---

## Policy-authorized rollback

Rollback is operationally necessary but MUST be explicit and signed when it crosses monotonic version boundaries.

### Rollback authorization record

A rollback MUST be authorized by a signed rollback authorization record, either embedded in the channel index or distributed alongside it.

The record MUST contain:

* `rollback_authorization_id`
* `channel_id`
* `authorized_rollback_to_pack_version`
* optional `target_runtime_pack_id`, recommended
* `reason`
* `issued_at`
* optional `expires_at`, recommended
* `issuer`
* `authority_channel`, if applicable
* `reader_policy_id`, if applicable
* `scope`, if applicable
* signatures by an authority key or deployment key accepted by the channel policy

Clients MUST:

* verify authorization signature;
* ensure the authorization is within the required validity window when the policy enforces expiry;
* ensure the rollback target is not revoked or blocked by active policy;
* ensure the rollback target matches the authorized identity if `target_runtime_pack_id` is specified;
* record that rollback occurred.

### Rollback activation state

When rollback authorization is present, clients MAY activate the rollback target even if it is lower than the highest previously activated version.

Clients MUST:

* keep `highest_seen_pack_version[channel]` unchanged;
* preserve evidence that a newer release was seen;
* record `current_active_pack_version[channel]` separately from `highest_activated_pack_version[channel]`;
* log rollback activation with reason and authorization reference.

Clients SHOULD set a rollback mode marker until a newer non-rollback release is activated.

---

## Emergency rollback

Emergency rollback MAY be used when a current pack, key, validation decision, authority recognition, reader policy, or source Exchange is compromised, unsafe, revoked, or operationally broken.

Emergency rollback SHOULD prefer one of the following:

1. a new higher `pack_version` containing the corrective content;
2. a signed reissue of the same `pack_version`, if reissue is allowed;
3. a rollback to an older pack authorized by a signed rollback record.

If a key compromise occurs, rollback to an older pack is allowed only if:

* the older pack was signed by keys still trusted under the active policy; or
* the active policy explicitly recognizes an emergency trust path;
* revocation policy does not invalidate the older pack;
* the rollback authorization itself is verifiable.

Clients SHOULD prefer a new higher `pack_version` over rollback whenever feasible.

---

## Offline and sync edge cases

### Offline clients without index updates

If a client is offline and only has cached artifacts, it MUST NOT activate a lower `pack_version` than previously active in that channel unless a cached rollback authorization is present and valid under the active policy.

If only an older pack is available and no valid rollback authorization exists, the client SHOULD enter hold state rather than silently downgrading.

The client MAY continue using the current active pack if policy allows.

The client SHOULD record that no acceptable newer or rollback-authorized pack was available.

---

### Offline revocation uncertainty

If revocation data is unavailable offline:

* if the active policy requires current revocation data, the candidate MUST NOT be activated;
* if the active policy allows stale or unavailable revocation data, the activation decision MAY proceed with status labels indicating revocation was not fully checked.

Recommended revocation-check statuses:

```text
not_checked
not_revoked
revoked
unknown
unavailable_offline
stale
not_applicable
```

---

### Sync conflicts

When Orgo, Konnaxion, device sync, mirror sync, or operator workflows introduce conflicting current pointers, the client MUST choose the highest valid `pack_version` according to channel rules unless rollback authorization exists.

Conflicts SHOULD be logged with correlation IDs.

If conflict resolution cannot be completed safely under policy, the client SHOULD enter hold state.

---

### Stale authority registry

If a Runtime Pack or Exchange depends on an Authority Registry that is older than the active policy allows, the client MUST NOT activate the candidate under policies requiring fresh authority registry data.

If policy allows stale authority registry data, the client MAY activate with status labels indicating the registry freshness state.

---

### Reader policy drift

If a Runtime Pack was produced under one reader policy but a client attempts to activate it under another, the client MUST evaluate compatibility.

If compatibility cannot be proven, activation MUST NOT proceed under the new reader policy.

---

## Operational rollout patterns

Recommended rollout patterns include:

* **Canary releases**: channel index lists cohorts or staged pointers; clients still gate activation locally with verification, version checks, and policy checks.
* **Blue/green**: clients keep active and standby slots; activation is atomic after checks pass.
* **Staged rollouts**: progressively advance `latest` or cohort pointers in the signed channel index.
* **Pinned reference releases**: clients remain on a selected Reference Exchange or Runtime Pack until the active authority channel advances the pointer.
* **Research channel releases**: clients may consume Working Exchanges or lower-certainty material under explicit research reader policies.
* **Emergency channel override**: a constrained channel policy temporarily permits rollback, reissue, or pinning.

---

## Logging and observability

Clients and distributors SHOULD emit structured events.

Recommended events:

```text
PACK_CANDIDATE_SEEN
PACK_IDENTITY_VERIFIED
PACK_SIGNATURE_VERIFIED
PACK_PAYLOAD_HASHES_VERIFIED
PACK_POLICY_SATISFIED
PACK_POLICY_NOT_SATISFIED
PACK_REJECTED
PACK_HELD
PACK_QUARANTINED
PACK_ACTIVATED
DOWNGRADE_BLOCKED
ROLLBACK_AUTH_ACCEPTED
ROLLBACK_AUTH_REJECTED
ROLLBACK_ACTIVATED
REISSUE_ACCEPTED
REISSUE_REJECTED
REVOCATION_BLOCKED
AUTHORITY_CHANNEL_MISMATCH
READER_POLICY_MISMATCH
REFERENCE_STATUS_MISMATCH
```

Recommended event fields:

* `runtime_pack_id`
* `pack_version`
* `source_exchange_ref`
* `source_artifact_status`
* `build_id`
* `channel_id`
* `tenant_id`
* `environment`
* `region`
* `audience_segment`
* `authority_channel`
* `reader_policy_id`
* `signer_key_id`
* `verification_status`
* `revocation_status`
* `activation_status`
* `reason_code`
* `device_id` or `node_id`
* `correlation_id`

---

## Reason codes

Implementations SHOULD use stable reason codes.

Recommended reason codes:

```text
schema_valid
schema_invalid
identity_verified
identity_mismatch
signature_valid
signature_invalid
missing_signature
missing_key
unsupported_alg
hash_valid
hash_invalid
payload_hash_mismatch
trust_root_missing
trust_root_mismatch
authority_recognized
authority_not_recognized
authority_channel_mismatch
reader_policy_satisfied
reader_policy_not_satisfied
reader_policy_mismatch
validation_policy_satisfied
validation_policy_failed
version_monotonic
downgrade_blocked
rollback_authorized
rollback_not_authorized
rollback_expired
rollback_target_revoked
reissue_authorized
reissue_not_authorized
same_version_identity_conflict
revocation_checked
revocation_unavailable
revoked_by_authority_channel
minimum_version_blocked
source_status_mismatch
working_not_allowed_by_policy
reference_required_by_policy
activation_succeeded
activation_blocked
held_for_policy
quarantined_for_diagnostics
```

---

## Minimum acceptance criteria

A deployment satisfies this policy if:

1. Clients persist per-channel highest seen, highest activated, and current active versions.
2. Clients block downgrades unless an explicit signed rollback authorization permits them.
3. Rollbacks require explicit signed authorization.
4. “Same version but different identity” is rejected unless explicitly authorized by a signed reissue policy.
5. Required identity, signature, payload-hash, trust-root, reader-policy, authority-channel, and revocation checks are evaluated before activation.
6. Trust roots are pinned or bundled for offline verification.
7. Offline clients hold rather than silently downgrading when no valid rollback authorization exists.
8. Runtime Pack integrity covers declared payload files.
9. Working Exchange packs are not activated as Reference Exchange packs unless recognition or validation policy supports that status.
10. Reader policy and authority-channel scope are preserved during activation.
11. Verification, validation, recognition, certainty, and reader visibility remain distinct in logs and APIs.

---

## Conformance tests

A conforming implementation MUST provide fixtures demonstrating:

* normal activation of a higher valid `pack_version`;
* downgrade blocked without rollback authorization;
* rollback accepted with valid signed authorization;
* rollback rejected with expired authorization;
* rollback rejected when target pack is revoked;
* same version and same identity accepted;
* same version and different identity rejected without reissue authorization;
* same version and different identity accepted with valid reissue authorization;
* identity mismatch blocked by policy;
* payload hash mismatch blocked by policy;
* missing required signature blocked by policy;
* unsupported required algorithm blocked by policy;
* missing trust root blocked by policy;
* stale or unavailable revocation data handled according to policy;
* activation under matching reader policy;
* activation blocked under incompatible reader policy;
* activation under matching authority channel;
* activation blocked under authority-channel mismatch;
* Working Exchange pack allowed in research mode;
* Working Exchange pack blocked in reference-only mode;
* Reference Exchange pack activated under a matching reference policy;
* offline cached older pack held rather than silently activated;
* sync conflict resolved by highest valid version;
* sync conflict held when no valid policy resolution exists.

Conformance tests SHOULD include:

* tenant-scoped channels;
* environment-scoped channels;
* region-scoped channels;
* audience-segment-scoped channels;
* authority-channel-scoped trust roots;
* reader-policy-scoped activation;
* signed channel indexes;
* offline revocation artifacts;
* authority registry updates;
* validation decision references;
* authority recognition references;
* Runtime Packs derived from federations;
* Runtime Packs derived from shards.

---

## Security and correctness considerations

Implementations SHOULD defend against:

* replay of old signed artifacts;
* mirror compromise;
* stale cache activation;
* same-version substitution;
* trust-root substitution;
* authority-channel confusion;
* reader-policy confusion;
* stale authority registry use;
* stale or missing revocation data;
* rollback authorization reuse outside its scope;
* expired rollback authorization;
* cross-tenant or cross-environment activation;
* treating a Working Exchange as a Reference Exchange;
* treating a valid signature as universal validation;
* treating authority recognition from one channel as recognition by another;
* hiding downgrade or rollback decisions from logs;
* partial Runtime Pack activation;
* non-deterministic version comparison.

User interfaces and APIs SHOULD avoid ambiguous labels such as:

```text
safe
official
canonical
true
trusted
```

unless they are scoped by:

```text
authority_channel
reader_policy
validation_status
recognition_status
certainty_level
artifact_status
```

Preferred labels include:

```text
identity verified
signature verified
payload verified
recognized by <authority channel>
reference under <reader policy>
validated as <status>
not activated
held by policy
rollback authorized
downgrade blocked
reader-policy mismatch
authority-channel mismatch
revoked
```

---

## Open questions

The following profile decisions remain open:

* Whether `pack_version` is global per tenant or strictly per channel, region, and audience segment.
* Whether a signed channel index is required in all production environments.
* Whether revocation artifacts are mandatory for production channels.
* What freshness rules should apply to offline revocation artifacts.
* Whether reader policies must be signed before being bundled into Runtime Packs.
* Whether authority registries must use monotonic versions similar to Runtime Packs.
* Whether rollback authorization should always require expiry.
* Whether emergency rollback should require dual signatures from operations and authority-channel owners.
* Whether Runtime Packs derived from federations require additional shard-level rollback metadata.
* Whether Reference Exchange pointers and Runtime Pack pointers should share one channel index format or use separate indexes.
