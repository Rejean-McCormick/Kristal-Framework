# Orgo Workflow Contract

## Status

Draft — Kristal v5 normative integration contract

## Purpose

This document defines the required **workflow orchestration**, **governance**, **review**, **validation**, **recognition**, **release**, and **auditability** behavior for Orgo when Orgo acts as the control plane for Kristal production and distribution.

This contract is concerned with:

* managing Kristal workflow lifecycle;
* recording structured inputs, outputs, decisions, and releases;
* separating compilation from validation and authority recognition;
* supporting review and validation workflows across multiple authority channels;
* ensuring every build is reproducible where reproducibility is claimed;
* ensuring production and distribution actions are auditable and tenant-safe;
* preserving feedback as structured signals that may produce new artifacts, revisions, validations, recognitions, or forks.

This document does **not** define the internal Orgo task model beyond what is necessary for Kristal interoperability.

---

## Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

---

# 1. Roles and responsibilities

## 1.1 Orgo is the workflow control plane

Orgo MUST:

* create and manage the lifecycle of Kristal workflows;
* store workflow state, assignments, approvals, review outcomes, validation decisions, recognition decisions, release decisions, and audit logs;
* record build inputs, outputs, and their content-addressed identifiers;
* record authority channels, validation policies, reader policies, and release policies used by a workflow;
* trigger publication and distribution actions;
* track publication and distribution status;
* surface deterministic errors, warnings, and blocking conditions to operators;
* preserve tenant boundaries and trust-root boundaries;
* preserve provenance from input signals through released artifacts.

Orgo MUST NOT:

* mutate Kristal Exchange artifacts in place as a result of feedback signals;
* treat compilation, validation, and authority recognition as the same state;
* present an artifact or assertion as recognized outside the authority channel, validation policy, scope, and certainty level that support that status;
* silently override validation, recognition, integrity, tenant, or release-policy decisions.

## 1.2 Pipeline systems referenced by Orgo

Orgo may orchestrate interactions with:

* input systems that provide documents, datasets, web pages, PDFs, submissions, emails, forms, archives, APIs, or offline imports;
* extractors that may output Claim-IR as an extractor proposal profile;
* human editors, reviewers, domain experts, institutional validators, or AI-assisted validators;
* SenTient for resolution, reconciliation, normalization, and ambiguity preservation;
* Kristal compiler services for Structured Epistemic State, Exchange, shard, federation, and Runtime Pack creation;
* validation engines;
* authority registries;
* signing and trust-root services;
* Konnaxion or other distribution systems;
* Architect or other rendering systems;
* transparency logs or audit archives.

## 1.3 Kristal-owned versus Orgo-owned responsibilities

Kristal owns:

* structured epistemic states;
* exchange artifacts;
* runtime pack manifests;
* schemas;
* content-addressed identity;
* canonicalization for hashing;
* signatures and trust roots;
* assertion status;
* certainty metadata;
* authority recognition references;
* validation decision references;
* federation manifests;
* query contracts.

Orgo owns:

* its mutable operational database/state and transactional lifecycle;
* workflow lifecycle;
* operational cases and tasks;
* review routing;
* approval routing;
* human and institutional coordination;
* validation request tracking;
* authority recognition request tracking;
* build records;
* release records;
* distribution records;
* tenant-scoped audit logs;
* feedback handling;
* operational remediation.

Orgo MUST NOT make a live domain record simultaneously authoritative in both its operational store and Kristal. When Orgo-originated state contributes to Kristal compilation, Orgo SHOULD provide an immutable source snapshot/export or stable source artifact reference with revision/digest and provenance. The resulting Kristal artifact is a separate knowledge artifact and MUST preserve lineage to that source.

In the kOA deployment profile, Da’at MAY perform the mapping from the Orgo-owned source artifact into Kristal-native Structured Epistemic State or another supported Kristal input. Transport through Interaction Kernel does not transfer state ownership to Interaction Kernel.

---

# 2. Workflow model

## 2.1 Required workflow capabilities

A Kristal workflow managed by Orgo MUST be able to represent the following stages:

1. **Ingest**
2. **Structure**
3. **Resolve**
4. **Compile Working Artifact**
5. **Review**
6. **Validate**
7. **Recognize**
8. **Compile or Select Reference Artifact**
9. **Compile Runtime Pack**
10. **Verify Release Requirements**
11. **Publish**
12. **Distribute**
13. **Post-release monitoring**
14. **Feedback and revision**

Orgo MAY split these stages into sub-stages.

Orgo MAY omit stages that are not applicable to a given workflow, provided that omitted stages are recorded as not applicable rather than silently ignored.

## 2.2 No universal required path

Orgo MUST NOT assume that every Kristal workflow begins with Claim-IR.

Valid inputs may include:

* Structured Epistemic State;
* existing datasets;
* Wikidata-aligned corpora;
* institutional submissions;
* expert-authored claims;
* research bundles;
* fictional or mythological corpora;
* Claim-IR produced by an extractor;
* Resolved Claim-IR produced through SenTient;
* prior Kristal Exchanges;
* prior shards;
* prior federations;
* prior Runtime Packs;
* feedback-derived structured signals.

Claim-IR MAY be used where probabilistic extraction is involved. It is not the universal required input format.

## 2.3 Compilation and validation are distinct

Orgo MUST support workflows where a working Kristal artifact is compiled before final validation or authority recognition.

Compilation materializes structured work into portable artifacts.

Validation records whether an artifact, shard, assertion, dataset, or authority channel is accepted under a declared policy and scope.

Authority recognition records whether an authority channel recognizes an artifact, shard, assertion, dataset, Runtime Pack, or other authority channel.

These states MUST remain distinct.

## 2.4 Recommended stage order

A common workflow SHOULD follow this order:

1. **Ingest**
2. **Structure → Structured Epistemic State**
3. **Optional extraction → Claim-IR**
4. **Optional resolution → SenTient outputs**
5. **Compile → Working Exchange**
6. **Review**
7. **Validation decision**
8. **Authority recognition**
9. **Reference Exchange selection or compilation**
10. **Runtime Pack compilation**
11. **Release verification**
12. **Publish and distribute**
13. **Monitor and collect feedback**

This order is recommended, not universal. Orgo MAY support alternative workflows when policy allows them and records the reason.

---

# 3. Stage semantics

## 3.1 Ingest

The Ingest stage records input material.

Orgo MUST record:

* input source;
* input snapshot reference;
* tenant scope;
* submitter or publisher identity when available;
* access-control constraints;
* timestamps;
* source format;
* declared domain or scope when available.

Orgo SHOULD produce content-addressed references for every input snapshot.

## 3.2 Structure

The Structure stage produces or registers a **Structured Epistemic State**.

A Structured Epistemic State SHOULD include:

* assertions;
* scope;
* provenance;
* evidence references;
* uncertainty;
* assertion status;
* certainty level;
* lineage;
* policy references;
* review references where available.

Orgo MUST record the Structured Epistemic State reference used by subsequent stages.

## 3.3 Extraction

Extraction is optional.

When probabilistic extractors are used, Orgo SHOULD require their direct output to be Claim-IR or another declared extractor proposal profile.

Orgo MUST record:

* extractor identity;
* extractor version;
* input snapshot refs;
* output refs;
* configuration refs;
* uncertainty and confidence fields when supplied;
* whether extractor outputs were frozen for replay.

## 3.4 Resolution

Resolution is optional but SHOULD be used when inputs contain ambiguous names, properties, entities, dates, units, or multilingual labels.

Orgo may invoke SenTient to produce:

* candidate QIDs/PIDs;
* ranking signals;
* normalized values;
* ambiguity records;
* unresolved references;
* warnings.

Orgo MUST preserve unresolved ambiguity rather than forcing certainty when resolution is insufficient.

## 3.5 Compile Working Artifact

The Compile Working Artifact stage produces a working Kristal artifact such as a `working_exchange`.

Orgo MUST record:

* compiler identity;
* compiler version;
* configuration hash;
* canonicalization profile;
* canonicalization version;
* source input refs;
* output artifact refs;
* compile status;
* reason codes where applicable.

A working artifact MAY contain uncertain, disputed, incomplete, fictional, mythological, speculative, or erroneous assertions, provided that their statuses are explicit.

## 3.6 Review

The Review stage coordinates human, institutional, expert, automated, or hybrid review.

Orgo SHOULD record:

* reviewer identity or reviewer group;
* authority channel, if applicable;
* review policy;
* scope;
* review result;
* review comments or structured findings;
* reviewed targets;
* timestamps;
* signatures or attestations when applicable.

Review is not the same as validation unless a validation policy explicitly treats a review outcome as a validation decision.

## 3.7 Validation

The Validation stage records scoped validation decisions.

A validation decision MUST declare:

* target reference;
* target level: artifact, shard, assertion, authority channel, dataset, or Runtime Pack;
* validation status;
* validated-as mode;
* certainty level, where applicable;
* authority channel;
* validation policy reference;
* scope;
* findings;
* reason codes;
* timestamp;
* signatures where required.

Orgo MUST NOT record validation as a bare boolean.

Invalid:

```json
{ "validated": true }
```

Required pattern:

```json
{
  "validation_status": "validated",
  "validated_as": "sourced_claim",
  "certainty_level": "medium",
  "authority_channel": "authority:example",
  "validation_policy_ref": "policy:example",
  "scope": {
    "domain": "science"
  }
}
```

## 3.8 Recognition

Recognition records whether an authority channel accepts or recognizes a target.

A recognition decision MAY target:

* an assertion;
* a shard;
* an Exchange;
* a Runtime Pack;
* a dataset;
* a federation;
* another authority channel;
* a validation policy.

Recognition MUST be scoped.

Recognition by one authority channel MUST NOT imply recognition by another authority channel.

## 3.9 Reference Artifact

A Reference Artifact is an artifact recognized as a reference under one or more authority channels and scopes.

Orgo MUST preserve the distinction between:

* working artifacts;
* under-review artifacts;
* recognized artifacts;
* reference artifacts;
* deprecated artifacts;
* revoked artifacts.

Orgo MUST NOT present a working artifact as a reference artifact unless recognition and release policy allow it.

## 3.10 Runtime Pack compilation

A Runtime Pack is a derived, offline-usable indexed form of a Kristal Exchange.

Orgo MUST record:

* source Exchange reference;
* source artifact status;
* compiler identity;
* build configuration hash;
* query contract reference;
* reader policy references;
* runtime pack manifest reference;
* file hashes;
* integrity metadata;
* signatures where applicable.

A Runtime Pack MUST declare whether it is derived from a working artifact or a reference artifact.

## 3.11 Release verification

Before publication or distribution, Orgo MUST verify release requirements declared by the applicable release policy.

Release verification MAY include:

* hash verification;
* signature verification;
* trust-root verification;
* schema conformance;
* tenant-scope conformance;
* authority-channel requirements;
* validation-status requirements;
* recognition-status requirements;
* reader-policy availability;
* downgrade-prevention requirements;
* revocation checks.

If required verification fails, Orgo MUST block the release action and record the failure reason.

## 3.12 Publish and distribute

Publication makes artifacts available to declared channels.

Distribution moves artifacts, manifests, or Runtime Packs to target environments.

Orgo MUST record:

* release ID;
* artifact references;
* runtime pack references;
* target channels;
* tenant or audience scope;
* release timestamp;
* verification status;
* distribution status;
* rollout strategy where applicable.

---

# 4. Status model

## 4.1 Workflow status

Orgo MUST represent workflow status using stable values.

Recommended values:

* `draft`
* `ingesting`
* `structuring`
* `resolving`
* `compiling_working_artifact`
* `under_review`
* `validating`
* `recognizing`
* `compiling_reference_artifact`
* `compiling_runtime_pack`
* `verifying_release`
* `publishing`
* `distributing`
* `released`
* `blocked`
* `failed`
* `revoked`
* `deprecated`
* `superseded`

## 4.2 Compile status

Recommended values:

* `not_started`
* `succeeded`
* `failed`
* `partial`
* `blocked`

## 4.3 Review status

Recommended values:

* `not_required`
* `pending`
* `in_progress`
* `completed`
* `blocked`
* `rejected`

## 4.4 Validation status

Recommended values:

* `not_evaluated`
* `in_review`
* `validated`
* `conditionally_validated`
* `disputed`
* `rejected`
* `revoked`

## 4.5 Recognition status

Recommended values:

* `none`
* `recognized`
* `conditionally_recognized`
* `under_review`
* `disputed`
* `rejected`
* `deprecated`
* `revoked`

## 4.6 Publication status

Recommended values:

* `not_published`
* `published`
* `blocked`
* `revoked`

## 4.7 Distribution status

Recommended values:

* `not_started`
* `pending`
* `in_progress`
* `distributed`
* `partially_distributed`
* `failed`
* `rolled_back`
* `revoked`

---

# 5. Build Record requirements

For every Kristal build, Orgo MUST persist a **Build Record**.

## 5.1 Identifiers

The Build Record MUST contain:

* `build_id`;
* `tenant_id` in multi-tenant deployments;
* `workflow_id`;
* `case_id` or task reference when applicable;
* `created_at`;
* `created_by` or triggering actor when available.

## 5.2 Inputs

The Build Record MUST contain `input_snapshots[]`.

Input snapshots MAY include:

* source dataset snapshots;
* document snapshots;
* web archive snapshots;
* API snapshots;
* user submissions;
* institutional submissions;
* Claim-IR snapshots;
* Structured Epistemic State snapshots;
* prior Exchange refs;
* prior Runtime Pack refs;
* configuration snapshots.

## 5.3 Compiler identity and configuration

The Build Record MUST contain:

* `compiler.name`;
* `compiler.version`;
* `config_hash`;
* `canonicalization_profile`;
* `canonicalization_version`.

For Kristal v5, the canonicalization profile SHOULD be:

```text
kristal.v5:jcs-rfc8785
```

and the canonicalization version SHOULD be:

```text
1
```

## 5.4 Policy selections

The Build Record MUST record policy selections that affect outputs or decisions.

These MAY include:

* compilation policy;
* validation policy;
* recognition policy;
* reader policy;
* federation composition policy;
* query policy;
* runtime pack policy;
* release policy;
* tenant policy;
* trust-root policy;
* downgrade-prevention policy.

## 5.5 Outputs

The Build Record SHOULD distinguish:

* `working_outputs[]`;
* `reference_outputs[]`;
* `runtime_pack_outputs[]`;
* `validation_decisions[]`;
* `authority_recognitions[]`;
* `review_records[]`;
* `release_records[]`;
* `revocation_records[]`.

Each output SHOULD be content-addressed when possible.

## 5.6 Status summary

The Build Record MUST distinguish:

* `compile_status`;
* `review_status`;
* `validation_status`;
* `recognition_status`;
* `publication_status`;
* `distribution_status`;
* `activation_status`, when applicable.

These statuses MUST NOT be collapsed into one pass/fail field.

## 5.7 Reason codes

The Build Record SHOULD include stable reason codes.

Recommended codes include:

* `schema_valid`;
* `schema_invalid`;
* `provenance_sufficient`;
* `provenance_insufficient`;
* `evidence_sufficient`;
* `evidence_insufficient`;
* `authority_recognized`;
* `authority_not_recognized`;
* `scope_mismatch`;
* `policy_satisfied`;
* `policy_failed`;
* `signature_valid`;
* `signature_invalid`;
* `hash_valid`;
* `hash_invalid`;
* `conflict_detected`;
* `disagreement_preserved`;
* `certainty_too_low_for_policy`;
* `rejected_by_authority_channel`;
* `revoked_by_authority_channel`.

---

# 6. Integrity verification requirements

## 6.1 Verification before release

Before publishing or distributing Exchange or Runtime Pack artifacts, Orgo MUST verify all integrity material required by the active release policy.

This MAY include:

* declared content hashes;
* manifest hashes;
* pack hashes;
* signatures;
* signing keys;
* trust roots;
* revocation status;
* schema conformance;
* tenant-scope conformance.

If required verification fails, Orgo MUST:

* block the release or distribution action;
* record the failure reason;
* preserve the failed candidate for inspection if policy allows;
* prevent the candidate from being represented as released, recognized, or trusted for that channel.

## 6.2 Declared integrity material

If an artifact declares integrity material, Orgo MUST verify it according to the applicable trust-root, tenant, release, and reader policies before using it as trusted material.

Orgo MUST NOT “publish anyway” when required verification fails.

Orgo MUST treat malformed required integrity fields as errors.

## 6.3 Diagnostic access

Orgo MAY allow operators to inspect failed candidates, malformed artifacts, or unrecognized artifacts in diagnostic or review contexts.

Such access MUST clearly mark the artifact status and MUST NOT present the artifact as recognized, released, or trusted.

---

# 7. Distribution workflow requirements

## 7.1 Versioned Release records

Orgo MUST create a **Release Record** per published version.

A Release Record MUST include:

* release ID;
* release version;
* tenant or channel scope;
* Exchange references;
* Runtime Pack references;
* source artifact status;
* authority recognition references where applicable;
* validation decision references where applicable;
* reader policy references;
* target channels;
* publish timestamp;
* verification status;
* distribution status.

## 7.2 Rollout controls

Orgo SHOULD support progressive rollout strategies:

* staged rollouts by cohort;
* canary releases;
* blue/green releases;
* region-scoped releases;
* tenant-scoped releases;
* device-cohort releases;
* automatic rollback on required verification failures;
* rollback on high operational error rates where policy allows.

These rollout mechanics are operational guidance. The Release Record MUST remain auditable.

## 7.3 Downgrade prevention

If the distribution environment supports version pinning, Orgo MUST provide a mechanism to prevent downgrade to a vulnerable, invalid, revoked, or disallowed pack version.

Orgo MUST record pinned minimum versions per channel when used.

## 7.4 Revocation-aware distribution

Orgo SHOULD check revocation records before publishing or distributing artifacts.

If an artifact or signing authority is revoked under the applicable policy, Orgo MUST block distribution unless the release policy explicitly permits diagnostic or archival distribution.

---

# 8. Multi-tenancy and isolation

## 8.1 Tenant scoping

All workflow records MUST be tenant-scoped in multi-tenant deployments.

Orgo MUST prevent cross-tenant visibility of build inputs, outputs, validation decisions, recognition decisions, and release records unless explicitly configured for shared artifacts.

## 8.2 Shared artifacts

If artifacts are shared across tenants, Orgo MUST record:

* source tenant or publisher;
* sharing policy;
* permitted target tenants;
* authority channels;
* trust roots;
* reader policies;
* access-control constraints.

## 8.3 Keys and signing

Signing keys MAY be tenant-scoped even when artifact IDs are global and content-addressed.

Orgo MUST:

* record which keys signed which artifacts or releases;
* record which trust roots were used for verification;
* enforce that verification uses the correct trust roots for the tenant, channel, and release policy.

---

# 9. Feedback loop handling

## 9.1 Feedback must not mutate Exchange directly

Orgo MUST represent feedback as:

* Cases;
* Tasks;
* review requests;
* validation requests;
* recognition requests;
* structured signals;
* correction proposals;
* revocation requests;
* fork requests;
* new Structured Epistemic States;
* new Claim-IR proposals where extraction is involved.

Orgo MUST NOT edit Exchange artifacts in place due to votes, curation, user edits, operator comments, or feedback signals.

Orgo MUST also NOT write those changes into a Runtime Pack query/materialization store as a substitute for producing a new source/epistemic artifact and derived build. Runtime Pack state is read-oriented derived state, not Orgo's transactional write model.

## 9.2 Feedback-to-build linkage

Orgo SHOULD link:

* feedback signals;
* cases;
* tasks;
* review records;
* validation decisions;
* recognition decisions;
* resulting builds;
* resulting releases.

This linkage makes governance auditable.

## 9.3 Fork handling

If feedback produces a divergent corpus or shard, Orgo MAY initiate a fork workflow.

Fork workflows MUST preserve:

* source lineage;
* fork reason;
* publisher;
* authority channel;
* validation scope;
* recognition status;
* relationship to the source artifact.

A fork MUST NOT inherit recognition from the source unless the recognizing authority explicitly recognizes the fork.

---

# 10. Validation and authority workflows

## 10.1 Validation requests

Orgo SHOULD support validation requests targeting:

* assertions;
* shards;
* Exchanges;
* Runtime Packs;
* datasets;
* authority channels;
* reader policies.

A validation request SHOULD declare:

* target;
* requested authority channel;
* validation policy;
* scope;
* requested validated-as mode;
* evidence refs;
* submitter;
* deadline or review window where applicable.

## 10.2 Authority recognition requests

Orgo SHOULD support authority recognition requests.

Recognition requests MAY ask one authority channel to recognize:

* an artifact;
* a shard;
* an assertion;
* another authority channel;
* a dataset;
* a validation policy;
* a Runtime Pack;
* a release.

Recognition MUST be recorded as scoped.

## 10.3 Delegated authority

Authority channels MAY recognize other authority channels.

Examples:

* an international organization recognizes a health authority for public-health references;
* a government recognizes a national statistics office for demographic data;
* a standards body recognizes a working group for a technical specification;
* a company is recognized as the primary source for its own declared system architecture.

Orgo MUST record delegated recognition explicitly.

---

# 11. Observability requirements

Orgo SHOULD emit structured logs or events for each stage.

Events SHOULD include:

* `build_id`;
* `workflow_id`;
* `case_id`;
* `tenant_id`;
* `kristal_id`;
* `exchange_id`;
* `runtime_pack_id`;
* `release_id`;
* stage name;
* stage outcome;
* compile status;
* review status;
* validation status;
* recognition status;
* publication status;
* distribution status;
* reason codes;
* hash verification result;
* signature verification result;
* authority channel;
* reader policy;
* correlation ID.

Logs MUST NOT leak cross-tenant data.

---

# 12. Minimal API surface

This section is informative.

Orgo implementations typically expose operations equivalent to:

* `CreateKristalWorkflow(input_snapshots, config_ref, policy_selections)`
* `RegisterStructuredEpistemicState(workflow_id, state_ref)`
* `AttachClaimIR(workflow_id, claim_ir_ref)`
* `RequestResolution(workflow_id, target_ref)`
* `AdvanceStage(workflow_id, stage, outputs)`
* `CreateReviewTask(workflow_id, target_ref, reviewer_ref, policy_ref)`
* `RecordReviewOutcome(workflow_id, review_record_ref)`
* `RequestValidation(workflow_id, target_ref, authority_channel, policy_ref)`
* `RecordValidationDecision(workflow_id, validation_decision_ref)`
* `RequestAuthorityRecognition(workflow_id, target_ref, authority_channel, policy_ref)`
* `RecordAuthorityRecognition(workflow_id, recognition_ref)`
* `CompileWorkingExchange(workflow_id)`
* `CompileReferenceExchange(workflow_id)`
* `CompileRuntimePack(workflow_id)`
* `GetBuildRecord(build_id)`
* `CreateRelease(build_id, channels, reader_policies)`
* `VerifyRelease(release_id)`
* `PublishRelease(release_id)`
* `GetReleaseStatus(release_id)`
* `CreateRevisionWorkflow(source_artifact_ref, feedback_refs)`
* `CreateForkWorkflow(source_artifact_ref, fork_policy_ref)`

API shape is implementation-specific.

---

# 13. Conformance checklist

Orgo satisfies this contract if it:

* manages Kristal workflows as auditable lifecycle objects;
* supports Structured Epistemic State as the normative input unit;
* treats Claim-IR as an optional extractor proposal profile, not a universal required input;
* distinguishes compilation from review, validation, recognition, publication, distribution, and activation;
* records build inputs, configuration, policies, outputs, statuses, and reason codes in Build Records;
* records scoped validation decisions;
* records scoped authority recognitions;
* records Runtime Pack and Exchange references separately;
* verifies required hashes, signatures, trust roots, revocation status, and release requirements before trusted publication or distribution;
* blocks release or distribution when required verification fails;
* creates auditable versioned Release Records;
* isolates multi-tenant workflows and enforces correct trust roots;
* preserves feedback as structured signals that trigger new workflows rather than in-place Exchange edits;
* supports forks without silently inheriting authority recognition;
* keeps reader-policy, authority-channel, validation, certainty, and scope information available to downstream systems.

---

# 14. Core invariant

A Kristal workflow may produce artifacts that contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.

Orgo’s responsibility is not to erase those states. Orgo’s responsibility is to make sure each state is recorded, scoped, auditable, and never presented as more recognized, certain, validated, or authoritative than the applicable policies and authority channels allow.
