# Konnaxion distribution contract (Kristal v5 integration)

## Status

Draft (v5 integration contract)

## Purpose

This document defines the contract for how **Konnaxion** distributes, verifies, caches, activates, and exposes **Kristal v5 Runtime Packs** and associated metadata for offline and low-bandwidth operation.

Konnaxion’s responsibilities in the ecosystem are to:

* distribute versioned offline packages;
* verify declared hashes, signatures, trust roots, compatibility constraints, and revocation policies;
* provide predictable activation, rollback, downgrade-prevention, and cache behavior;
* surface pack provenance, version metadata, source status, authority channels, validation state, certainty metadata, and reader policy metadata to higher-level modules;
* support user-facing and application-facing reader policies, including reference-only, validated-only, high-certainty-only, research, creative, all-with-labels, and custom views.

Konnaxion distributes and activates Runtime Packs. It does not decide universal truth. It enforces declared distribution policy, artifact integrity, compatibility, reader-policy behavior, and channel-specific authority requirements.

Konnaxion's own mutable operational/domain state remains Konnaxion-owned and is not stored in Kristal merely because a Runtime Pack is present. Consultations, participants, votes, DecisionRecords, session state, delivery jobs, and other application records remain outside the Runtime Pack unless represented as immutable source evidence or derived epistemic knowledge under an explicit contract.

Normative keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.

---

## 1. Scope and non-goals

### 1.1 In scope

This contract covers:

* Runtime Pack bundle packaging and required metadata;
* distribution channels and signed channel indexes;
* authority registries and trust roots used by distribution channels;
* verification requirements for declared hashes, signatures, manifests, trust roots, compatibility constraints, and revocation lists;
* versioning, activation, rollback, downgrade prevention, and substitution prevention;
* reader policy distribution and application;
* offline caching behavior and storage layout expectations;
* distribution channels scoped by tenant, environment, region, audience, authority channel, or reader policy;
* telemetry and feedback signals as operational signals.

### 1.2 Out of scope

This contract does not define:

* how Kristal artifacts are compiled;
* how Structured Epistemic States are authored;
* how assertions are validated;
* how authority channels decide recognition;
* how facts, claims, myths, hypotheses, or disputed positions are debated;
* full device management or MDM integration;
* user interface design;
* Runtime Pack internal query semantics, except where query-contract compatibility affects activation;
* Konnaxion's transactional/domain database schema or write model.

Build workflows are owned by Orgo and the Kristal compiler. Validation and recognition are represented by Kristal validation decisions and authority recognition records. Konnaxion consumes those records according to distribution policy and reader policy.

---

## 2. Artifact types and identifiers

### 2.1 Runtime Pack bundle

A distributable Runtime Pack bundle MUST include:

* `runtime-pack-manifest.json`;
* pack payload files, such as tables, indexes, filters, dictionaries, projections, manifests, and policy payloads;
* file inventory metadata sufficient for offline verification;
* optional detached or embedded signature envelopes;
* optional signed channel index;
* optional authority registry;
* optional revocation list;
* optional reader policies;
* optional validation decision records;
* optional authority recognition records;
* optional transparency log entries.

Pack payload files are derived, read-oriented materializations. A Runtime Pack MAY contain a profile-defined database-like query file only when the applicable profile declares it and the file is bound to the pack/source identity. Konnaxion MUST treat such a file as immutable/read-only for that pack build and MUST NOT use it as its authoritative mutable application database or write back local mutations as Kristal knowledge.

The Runtime Pack Manifest MUST conform to:

```text
02-schemas/runtime-pack-manifest.schema.json
```

Backward compatibility aliases such as `pack_manifest.json` MAY be accepted by local tooling, but v5 emitters SHOULD publish:

```text
runtime-pack-manifest.json
```

### 2.2 Required identifiers

Each Runtime Pack bundle intended for distribution MUST be uniquely and unambiguously identified by the following metadata, carried either in the Runtime Pack Manifest, channel index, or both:

* `schema_version = "5.0"`;
* `artifact_type = "runtime_pack_manifest"`;
* `runtime_pack_id`;
* `runtime_pack_version`;
* `release_id`;
* `build_id`;
* source artifact reference;
* source artifact status;
* created timestamp for audit and debugging;
* distribution channel;
* signer key identifier where signatures are declared;
* content hash;
* query contract reference;
* reader policy references;
* authority registry reference where authority checks are required;
* revocation list reference where revocation checks are required.

Konnaxion MUST treat `runtime_pack_id` as the primary identity for pack selection, verification binding, caching, and activation.

### 2.3 Source artifact reference

A Runtime Pack MUST reference the source artifact or source composition from which it was compiled.

The source MAY be:

* `working_exchange`;
* `reference_exchange`;
* `exchange_shard_manifest`;
* `exchange_federation_manifest`;
* another declared source artifact type supported by the Runtime Pack profile.

A Runtime Pack derived from a Working Exchange is not equivalent to a Runtime Pack derived from a Reference Exchange.

Konnaxion MUST preserve and expose source status metadata to consumers, reader policies, search surfaces, and AI-facing integrations.

### 2.4 Source artifact status

A Runtime Pack MUST declare source artifact status.

Allowed source statuses SHOULD include:

* `working`;
* `under_review`;
* `recognized`;
* `reference`;
* `deprecated`;
* `superseded`;
* `revoked`.

Konnaxion MUST NOT infer that a pack is a reference pack from artifact existence alone.

### 2.5 Compatibility aliases

For transition and compatibility, consumers MAY accept older or alternate field names internally, but v5 emitters SHOULD use v5 names.

Compatibility aliases MAY include:

* `pack_id` as alias for `runtime_pack_id`;
* `pack_version` as alias for `release_id`;
* `source_kristal_id` as alias for a source artifact identifier;
* `kid` as alias for `key_id`.

Konnaxion MUST normalize accepted aliases to the v5 internal field names before verification, activation, and policy enforcement.

---

## 3. Distribution channels and indexes

### 3.1 Channels

Packs MUST be distributed via channels.

A channel MUST be scoped at minimum by:

* `tenant_id`;
* `environment`.

A channel MAY additionally be scoped by:

* `region`;
* `jurisdiction`;
* `audience_segment`;
* `authority_channel`;
* `reader_policy`;
* `domain`;
* `subdomain`;
* `language`;
* `deployment cohort`.

Konnaxion MUST NOT mix trust roots, authority registries, revocation state, reader policy defaults, verification policy, activation state, rollback state, or downgrade-prevention state across channels unless explicitly configured.

### 3.2 Channel identity

A channel SHOULD have a stable identifier:

```text
channel_id
```

The `channel_id` SHOULD be deterministic from declared channel scope or explicitly assigned by deployment policy.

Example channel dimensions:

```json
{
  "tenant_id": "tenant:example",
  "environment": "prod",
  "region": "ca-qc",
  "domain": "education",
  "reader_policy": "reader_policy:validated_only",
  "authority_channel": "authority:unesco"
}
```

### 3.3 Signed channel index

Konnaxion SHOULD consume a signed distribution index per channel.

A channel index is a control artifact that tells Konnaxion which Runtime Pack or pack set should be installed, staged, pinned, rejected, revoked, or activated.

If present, the channel index MUST be verified using the channel’s declared trust roots and authority policy before it is used for activation decisions.

A channel index MUST include at minimum:

* `schema_version`;
* `artifact_type = "distribution_channel_index"`;
* `channel_id`;
* `created_at`;
* `current` pointer;
* signing identity;
* signatures.

The `current` pointer MUST include:

* `release_id`;
* `runtime_pack_id`;
* source artifact status;
* required reader policy references, if any;
* required authority registry reference, if any;
* required revocation list reference, if any.

A channel index SHOULD additionally include:

* staged or canary pointers;
* cohort targeting metadata;
* pinned known-good packs;
* minimum allowed release ID;
* revoked artifact IDs or release IDs;
* revocation epoch marker;
* rollback authorization records;
* compatibility constraints;
* reader policy defaults;
* authority channel defaults;
* domain/subdomain constraints.

If a verified channel index is present, Konnaxion MUST treat it as the primary control plane for what to install or activate, subject to local verification, compatibility checks, downgrade prevention, reader policy constraints, and activation requirements.

---

## 4. Versioning and release semantics

### 4.1 Release identifiers

Konnaxion MUST treat release identifiers as structured, not ad hoc strings.

The authoritative monotonic field is:

```text
release_id
```

`release_id` is monotonic within a channel.

Implementations MUST define deterministic comparison rules per channel.

Recommended scheme:

```text
integer sequence
```

Compatibility aliases such as `pack_version` MAY be accepted, but Konnaxion MUST normalize to a single internal `release_id`.

### 4.2 Runtime Pack identity vs release identity

`runtime_pack_id` identifies artifact content.

`release_id` identifies a channel release position.

The same Runtime Pack MAY appear in multiple channels or releases if policy permits.

The same `release_id` MUST NOT point to different Runtime Pack IDs in the same channel unless a verified reissue authorization is present.

### 4.3 Source version metadata

The Runtime Pack Manifest SHOULD record:

* source artifact ID;
* source artifact type;
* source artifact status;
* source artifact content hash;
* source scope;
* authority recognition references;
* validation decision references;
* reader policy references;
* build ID;
* compiler identity;
* config hash.

Konnaxion SHOULD surface this metadata to higher-level modules.

---

## 5. Activation semantics

### 5.1 Activation rule

Konnaxion MUST only activate a Runtime Pack when all channel-required checks pass.

At minimum, activation requires:

1. Runtime Pack Manifest parses and passes schema validation.
2. Runtime Pack Manifest declares `schema_version = "5.0"`.
3. Runtime Pack Manifest declares deterministic build intent where required.
4. Runtime Pack Manifest includes a complete file inventory with hashes sufficient for offline verification.
5. Required files referenced by the manifest exist in the bundle.
6. Required file hashes verify.
7. Required signatures verify.
8. Required trust roots are available.
9. Required authority registry checks pass.
10. Required revocation checks pass.
11. Required reader policies are present and schema-valid.
12. Query contract compatibility is satisfied.
13. Required optional profiles are supported.
14. Pack is compatible with the client runtime.
15. Channel index, if used, authorizes the pack.
16. Downgrade-prevention and substitution-prevention rules pass.

Activation MUST be atomic.

Konnaxion MUST NOT leave the runtime in a partially activated state.

### 5.2 Activation does not mean truth

Activation means that the Runtime Pack is installed and usable under the declared channel and reader policies.

Activation MUST NOT be represented as universal validation, universal truth, maximum certainty, or recognition by every authority.

Activation does not change assertion status.

Activation does not create authority recognition.

Activation does not raise certainty.

### 5.3 Working and reference packs

Konnaxion MAY activate packs derived from Working Exchanges if channel policy permits.

Konnaxion MAY restrict some channels to packs derived from Reference Exchanges only.

Konnaxion MUST make source status available to the reader policy layer.

A user-facing or API-facing surface MUST NOT present a working pack as a reference pack unless a policy explicitly defines such behavior and labels remain visible.

### 5.4 Required labels

Activated packs MUST preserve enough metadata for consumers to distinguish:

* working vs reference source status;
* assertion status;
* validation status;
* recognition status;
* authority channel;
* certainty level;
* validated-as mode;
* scope;
* disputed status;
* rejected status;
* revoked status;
* fictional mode;
* mythological mode.

---

## 6. Downgrade prevention and substitution safety

### 6.1 Downgrade prevention

Konnaxion MUST implement downgrade prevention with deterministic, persisted state.

Minimum required rule:

Konnaxion MUST NOT activate an artifact with a lower `release_id` than the highest previously activated release in the same channel unless a policy-authorized rollback is present.

Konnaxion MUST persist per channel:

* `highest_activated_release_id`;
* active `runtime_pack_id`;
* active source artifact reference;
* active source artifact status;
* active reader policy references;
* active authority registry reference, if any;
* last successful verification metadata.

Konnaxion SHOULD also persist:

* `highest_seen_release_id`;
* last successful activation timestamp;
* signer key identifier;
* channel index hash;
* revocation list hash;
* compatibility decision metadata.

### 6.2 Substitution prevention

If a pack is received with the same `release_id` but a different `runtime_pack_id`, Konnaxion MUST treat this as an error unless a verified reissue authorization is present.

A reissue authorization MUST be:

* signed or otherwise verified under the channel policy;
* scoped to the channel;
* explicit about the replaced artifact;
* explicit about the replacement artifact;
* recorded for audit.

### 6.3 Revocation-aware activation

Konnaxion MUST NOT activate packs listed as revoked in a verified channel index, revocation list, authority registry policy, or equivalent verified revocation mechanism applicable to the channel.

Konnaxion MUST apply revocations according to:

* scope;
* authority channel;
* effective time;
* target type;
* channel policy;
* reader policy, where relevant.

---

## 7. Rollback behavior

### 7.1 Rollback modes

Konnaxion MUST support at least one rollback mode:

* **Pinned rollback**: activate a previously pinned known-good pack.
* **Last-known-good rollback**: activate the most recent previously active pack that is still present, verified, compatible, and not revoked.

### 7.2 Rollback authorization

Rollback MUST be explicit and policy-authorized.

Authorization MAY be conveyed through:

* a verified channel index containing a rollback authorization record;
* a verified operator action;
* a deployment-specific governance action;
* an Orgo workflow event referenced by a verified distribution policy.

If rollback is permitted, it MUST NOT occur silently.

### 7.3 Rollback constraints

A rollback target MUST satisfy:

* manifest schema validation;
* file inventory verification;
* required signature verification;
* required trust-root verification;
* revocation checks;
* compatibility checks;
* reader policy availability;
* channel scope compatibility.

Rollback MUST NOT bypass required verification.

Rollback MUST NOT silently change reader policy, authority channel, source status, or scope.

### 7.4 Rollback triggers

Rollback MAY be triggered by:

* explicit operator action;
* verified channel index update;
* current pack revocation;
* failed activation;
* local runtime health signals, if permitted by deployment policy;
* Orgo workflow event;
* compatibility failure after staged rollout.

Rollback MUST be deterministic given the same trigger event sequence and verified inputs.

---

## 8. Verification requirements

### 8.1 Verification scope

If the Runtime Pack Manifest, channel index, authority registry, revocation list, reader policy, validation decision, authority recognition record, or bundle declares any required verification material, Konnaxion MUST verify it before relying on the corresponding policy.

Verification material may include:

* hashes;
* file inventory hashes;
* signatures;
* signer identity;
* trust roots;
* authority registry references;
* revocation list references;
* compatibility constraints;
* reader policy references;
* validation decision references;
* authority recognition references.

### 8.2 Verification failure

If verification fails, Konnaxion MUST NOT treat the affected artifact as satisfying the corresponding policy.

Verification failure does not mean the bytes cannot exist, be inspected, quarantined, debugged, or used in a non-trusted diagnostic context.

Verification failure MUST block activation when activation depends on the failed verification.

### 8.3 Trust roots

Konnaxion MUST pin trust roots per channel.

Trust roots MUST be available offline at activation time.

Trust roots MUST NOT be fetched over the network at activation time as a dependency for correctness.

Trust roots may be:

* pre-provisioned;
* securely cached;
* delivered through a previously verified channel update;
* provided through a signed authority registry.

### 8.4 Recommended verification order

Recommended order:

1. Verify channel index, if used.
2. Verify authority registry, if required.
3. Verify revocation list, if required.
4. Verify reader policy artifacts, if required.
5. Verify Runtime Pack Manifest schema.
6. Verify Runtime Pack Manifest signatures, if required.
7. Verify Runtime Pack Manifest content hash, if applicable.
8. Verify bundle file inventory hashes.
9. Verify validation decision and authority recognition references needed for the active policy.
10. Verify compatibility constraints.
11. Activate atomically.

Implementations MAY choose a different order if the result is deterministic and no policy is treated as satisfied before its prerequisites are verified.

---

## 9. Reader policy distribution and application

### 9.1 Reader policy role

Reader policies define which assertions, artifacts, authority channels, validation statuses, certainty levels, and epistemic modes are visible to a reader or application.

Konnaxion MUST support distribution of reader policies when Runtime Packs depend on them.

Reader policies MAY be embedded in the pack, referenced by content hash, distributed through the channel index, or provided by local deployment policy.

### 9.2 Reader policy modes

Reader policies SHOULD support the following modes:

* `reference_only`;
* `validated_only`;
* `high_certainty_only`;
* `research`;
* `creative`;
* `all_with_labels`;
* `custom`.

### 9.3 Validated-only semantics

A `validated_only` reader policy means that all visible assertions satisfy the active reader policy.

It does not mean:

* all visible assertions are universally true;
* all visible assertions have maximum certainty;
* all visible assertions are recognized by every authority;
* all authorities agree.

### 9.4 Reader policy metadata

Konnaxion MUST preserve and expose reader-policy-relevant metadata, including:

* `artifact_status`;
* `source_artifact_status`;
* `assertion_status`;
* `validation_status`;
* `recognition_status`;
* `authority_channel`;
* `certainty_level`;
* `validated_as`;
* `scope`;
* disputed status;
* rejected status;
* revoked status;
* fictional mode;
* mythological mode.

### 9.5 Label preservation

Konnaxion MUST NOT hide labels required to distinguish certainty, authority, validation, recognition, dispute, rejection, fiction, mythology, or revocation state unless a reader policy explicitly filters the corresponding assertion out of view.

A reader policy MAY simplify presentation, but it MUST NOT silently launder scoped validation into universal truth.

---

## 10. Offline caching and storage contract

### 10.1 Storage layout

Konnaxion SHOULD store packs in a layout that supports:

* multiple installed versions per channel;
* multiple reader policies per channel;
* multiple authority registries per channel where configured;
* atomic activation;
* garbage collection with pinning rules;
* persisted per-channel safety state;
* last-known-good recovery.

Example layout:

```text
/<tenant>/<env>/<channel>/packs/<runtime_pack_id>/...
/<tenant>/<env>/<channel>/active -> <runtime_pack_id>
/<tenant>/<env>/<channel>/reader-policies/<reader_policy_id>.json
/<tenant>/<env>/<channel>/authority/authority-registry.json
/<tenant>/<env>/<channel>/authority/revocations.json
/<tenant>/<env>/<channel>/state.json
```

### 10.2 Cache policy

Konnaxion MUST define deterministic cache policies.

Cache policies MUST define:

* maximum disk usage per channel;
* eviction policy;
* pinned-pack behavior;
* minimum retained packs;
* treatment of revoked packs;
* treatment of deprecated packs;
* treatment of reader policy artifacts;
* treatment of authority registries and revocation lists.

Recommended minimum retained set:

* active pack;
* last-known-good pack;
* pinned packs;
* active reader policy artifacts;
* active authority registry;
* active revocation list.

### 10.3 Offline behavior

If offline, Konnaxion MUST:

* continue serving from the active pack;
* continue applying the active reader policy;
* continue using cached trust roots, authority registry, and revocation list;
* not attempt activation requiring network-dependent trust roots;
* not treat unavailable network state as new validation or recognition.

Konnaxion SHOULD surface stale metadata where useful, including:

* active release ID;
* active source status;
* active reader policy;
* active authority registry version;
* active revocation list version;
* last successful update check;
* last successful activation.

---

## 11. Compatibility checks

Before activation, Konnaxion MUST verify compatibility from the Runtime Pack Manifest and channel policy.

Compatibility checks MUST include:

* schema version compatibility;
* Runtime Pack manifest version compatibility;
* query contract compatibility;
* required profile support;
* required data projections;
* required reader policy support;
* required authority registry support;
* required revocation support;
* source artifact status policy;
* policy selections within the allowed portable policy set;
* runtime engine support.

If incompatible, Konnaxion MUST:

* not activate the pack;
* emit a deterministic error code;
* emit a diagnostic payload;
* preserve the currently active pack if possible.

### 11.1 Source status compatibility

A channel MAY require:

* reference packs only;
* working packs allowed;
* research packs allowed;
* creative packs allowed;
* specific authority channels;
* specific reader policies;
* specific certainty thresholds.

Konnaxion MUST enforce these requirements before activation.

---

## 12. Telemetry and feedback signals

Konnaxion MAY emit operational signals to Orgo.

Operational signals MAY include:

* download failures;
* verification failures;
* activation success or failure;
* rollback events;
* downgrade-prevention events;
* substitution-prevention events;
* query runtime errors;
* performance summaries;
* pack usage metrics;
* reader policy usage metrics;
* stale-pack events;
* missing authority registry events;
* missing revocation list events;
* missing reader policy events.

These signals MUST NOT mutate Kristal Exchange directly.

These signals SHOULD create Cases, Tasks, release records, distribution adjustments, or review workflows.

Telemetry MUST NOT silently change assertion status, certainty level, validation status, authority recognition, or reference status.

---

## 13. Error codes

Konnaxion SHOULD emit deterministic error codes for activation and verification failures.

Recommended codes:

* `manifest_schema_invalid`;
* `manifest_missing_required_field`;
* `file_inventory_missing`;
* `file_hash_mismatch`;
* `signature_invalid`;
* `signature_missing`;
* `trust_root_missing`;
* `authority_registry_missing`;
* `authority_registry_invalid`;
* `revocation_list_missing`;
* `revocation_list_invalid`;
* `runtime_pack_revoked`;
* `source_artifact_revoked`;
* `reader_policy_missing`;
* `reader_policy_invalid`;
* `query_contract_unsupported`;
* `profile_unsupported`;
* `release_id_downgrade_blocked`;
* `release_id_substitution_blocked`;
* `rollback_not_authorized`;
* `source_status_not_allowed`;
* `authority_channel_not_allowed`;
* `certainty_policy_not_satisfied`;
* `activation_incomplete`;
* `activation_aborted`.

---

## 14. Conformance tests

A Konnaxion implementation claiming v5 conformance MUST provide tests for:

* Runtime Pack Manifest schema validation;
* file inventory hash verification;
* signature verification success and failure;
* trust-root verification;
* authority registry verification;
* revocation-list behavior;
* activation blocking when required verification fails;
* atomic activation and no partial state;
* downgrade prevention with persisted `highest_activated_release_id`;
* same `release_id` with different `runtime_pack_id` substitution rejection;
* policy-authorized rollback;
* rollback rejection without authorization;
* offline behavior using active cached pack;
* no network dependency for activation correctness;
* cache eviction respecting pinned and last-known-good packs;
* reader policy presence and schema validation;
* `validated_only` reader policy behavior;
* source status enforcement;
* reference-pack-only channel enforcement;
* working-pack-allowed channel behavior;
* revoked pack rejection;
* revoked key rejection;
* unsupported query contract rejection;
* unsupported profile rejection.

### 14.1 Reader policy tests

Reader policy conformance tests SHOULD verify that Konnaxion:

* preserves labels required for certainty, validation, recognition, and authority;
* does not present working data as reference data;
* does not treat scoped validation as universal truth;
* filters rejected, revoked, fictional, mythological, disputed, or low-certainty assertions according to active policy;
* serves active reader policy behavior offline.

### 14.2 Federation tests

Federation-related distribution tests SHOULD verify that Konnaxion:

* activates federation-derived packs only when required shards are present;
* verifies shard references and hashes;
* applies required authority registries;
* handles optional shards according to declared policy;
* does not silently merge conflicting claims;
* preserves source status and authority metadata.

---

## 15. Open questions

* Do v5 core channels require pre-activation verification of all bundle file hashes, or should verify-on-first-use be a declared profile?
* Should delta update manifests be standardized as a Runtime Pack distribution profile?
* Should the distribution channel index have its own JSON Schema under `02-schemas/`?
* Should reader policies be embedded in Runtime Packs by default or distributed as separate signed artifacts?
* Should authority registries be channel-bound, pack-bound, or both?
* Should Konnaxion require active revocation lists for all reference-only channels?
* Should stale-pack metadata be a mandatory API surface or a recommended UX feature?
* Should `runtime-pack-manifest.json` be the only canonical filename, with alias support limited to migration tools?
