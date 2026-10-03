# Multi-tenancy Boundaries (Global Content IDs + Tenant Access Control Layering)

## Status

Draft

## Purpose

Define the multi-tenancy boundary model for Kristal v5 so that:

* IDs remain globally content-addressed where the artifact identity is content-derived;
* tenant isolation is enforced by access control, trust roots, signing domains, distribution channels, and reader policies;
* global references can be reused safely across tenants without cross-tenant leakage;
* operational systems such as Orgo and Konnaxion can manage builds, review, authority recognition, publication, offline distribution, and runtime activation without confusing artifact identity with tenant visibility.

This document is normative where it uses MUST, SHOULD, or MAY.

## Definitions

* **Tenant**: an isolated administrative, security, governance, or operational domain. A tenant may represent an organization, deployment, customer, jurisdiction, community, institution, or environment.
* **Exchange**: a structured Kristal artifact containing portable epistemic content, provenance, validation references, authority recognition references, certainty metadata, and query-relevant structure.
* **Working Exchange**: an Exchange that has been compiled and may be reviewed, inspected, distributed, or used under policy, but is not necessarily recognized as a reference artifact by an authority channel.
* **Reference Exchange**: an Exchange recognized by one or more declared authority channels for a declared scope and validation policy.
* **Runtime Pack**: a derived offline-usable package produced from an Exchange for query, reading, or local runtime use.
* **Global content ID**: an ID derived only from canonicalized artifact content, excluding signatures and tenant-local control-plane metadata.
* **Tenant artifact handle**: a tenant-scoped handle that maps to a global content ID while hiding or contextualizing it for access-control and correlation-risk purposes.
* **Access layer**: authorization, reader policy, tenant policy, and distribution controls that determine who can obtain, view, activate, or use an artifact.
* **Signing domain**: key material, trust roots, and signature policies used to sign or verify artifacts within a tenant, environment, authority channel, or distribution channel.
* **Authority channel**: a scoped authority context that may recognize, validate, reject, dispute, or revoke artifacts, shards, assertions, runtime packs, or other authority channels.
* **Reader policy**: a policy that determines which validation statuses, certainty levels, authority channels, scopes, and artifact statuses are visible or usable in a given reading surface.

## Core Model

### 1. Global content IDs

Kristal v5 uses content-addressed identity for artifacts whose identity is derived from their canonicalized content.

When an Exchange declares a global content ID:

* `kristal_id` MUST be computed solely from canonicalized Exchange content.
* `kristal_id` MUST exclude signatures.
* `kristal_id` MUST exclude tenant-local access control metadata.
* `kristal_id` MUST exclude workflow state, approval state, distribution state, and runtime activation state.
* The same Exchange content produced in two tenants MUST yield the same `kristal_id`.

Rationale: global content IDs enable caching, deduplication, reproducible builds, cross-implementation comparability, public reference reuse, and independent verification.

### 2. Tenant isolation is layered above IDs

Tenant separation MUST be enforced above content identity by:

* access control;
* tenant-scoped artifact handles;
* signing keys and trust roots;
* distribution channels;
* reader policies;
* authority-channel recognition policies;
* runtime activation policies;
* tenant-separated operational records.

Tenant isolation MUST NOT be implemented by altering the core content hash of the same artifact.

### 3. Tenant metadata must not influence global content hashes

Tenant identifiers, ACLs, approvals, workflow state, review queues, distribution status, runtime activation status, and tenant-local UI state MUST NOT be included in:

* Exchange canonicalization for `kristal_id`;
* Exchange `content_hash`;
* global artifact identity;
* Runtime Pack content hash, unless a separate declared integrity profile explicitly includes tenant packaging metadata.

Tenant metadata belongs in Orgo, Konnaxion, tenant registries, access-control records, release records, reader-policy records, or distribution-channel records.

It does not belong in global Kristal payload identity.

## Artifact Visibility and Authorization

### 4. Access decisions

Implementations MUST enforce access control at the following boundaries:

* Exchange lookup;
* Exchange fetch;
* Exchange read;
* shard lookup;
* shard fetch;
* Runtime Pack lookup;
* Runtime Pack fetch;
* Runtime Pack activation;
* offline cache use;
* reader-policy view construction;
* authority-recognition inspection when the recognition record is tenant-private.

Access checks MUST be tenant-scoped.

Access checks MUST prevent:

* cross-tenant enumeration of artifact existence;
* inference through error messages;
* unauthorized inspection of authority-channel membership;
* unauthorized discovery of distribution-channel contents;
* unauthorized activation of Runtime Packs;
* unauthorized reuse of tenant-private cached artifacts.

Where appropriate, systems SHOULD use consistent “not found or not authorized” responses rather than revealing whether a given global content ID exists in another tenant.

### 5. Content-addressability and privacy

Global content IDs can create correlation risk. If two tenants independently produce identical content, they may share the same `kristal_id`.

Deployments SHOULD consider:

* restricting exposure of raw `kristal_id` values outside authorized contexts;
* using tenant-scoped artifact handles in UI and public APIs;
* avoiding raw content IDs in unauthenticated URLs;
* preventing existence checks against raw IDs;
* ensuring logs containing raw IDs are tenant-scoped;
* applying rate limits to artifact lookup endpoints;
* separating public reference registries from private tenant registries.

If a deployment requires no cross-tenant correlation in external surfaces, it MUST use a tenant-scoped indirection layer while keeping global content IDs internally.

## Tenant Artifact Handles

### 6. Tenant-scoped indirection

A tenant MAY expose a tenant artifact handle instead of a raw global content ID.

Recommended shape:

```json
{
  "tenant_artifact_handle": "tenant-artifact:<tenant-scope>:<opaque-id>",
  "tenant_id": "tenant:<slug>",
  "target": {
    "artifact_type": "working_exchange",
    "kristal_id": "sha256:<hex>"
  },
  "allowed_channels": [],
  "reader_policy_refs": [],
  "authority_channel_refs": [],
  "trust_root_refs": [],
  "created_at": "RFC3339"
}
```

Tenant artifact handles MAY be opaque.

Tenant artifact handles MUST NOT be treated as global artifact identity.

A tenant artifact handle MAY be revoked, rotated, hidden, or remapped without changing the underlying global content ID.

### 7. Public reference artifacts

Some Kristals are intended to be cross-tenant by design, such as public education packs, public standards, public institutional records, or public Wikidata-derived reference artifacts.

Such artifacts SHOULD be published through a declared public tenant, public authority channel, public distribution channel, or shared reference registry.

A public reference artifact may expose raw global content IDs when correlation is intended and safe.

Private tenants MAY still map public reference artifacts through tenant-local handles if their access model requires it.

## Signing, Trust Roots, and Tenant Domains

### 8. Tenant-scoped signing domains

Each tenant or environment MUST have a defined trust root set used to verify signatures.

Trust root sets MAY include:

* tenant keys;
* environment keys;
* authority-channel keys;
* publisher keys;
* distribution-channel keys;
* public reference registry keys;
* delegated trust roots.

Artifacts MAY be signed by tenant-specific keys even when their global content IDs are identical.

Verification MUST use the trust roots pinned by the active tenant, authority channel, distribution channel, or reader policy.

### 9. Same content, different signatures

It MUST be possible for:

* Tenant A and Tenant B to publish the same Exchange with the same `kristal_id`;
* Tenant A and Tenant B to sign that Exchange with different keys;
* different authority channels to recognize or reject the same Exchange independently;
* different distribution channels to package the same Exchange differently.

Signatures MUST be treated as metadata over declared content hashes or manifest targets.

Signatures MUST NOT change `kristal_id`.

### 10. Trust roots and authority recognition

Trust roots verify signatures.

Authority recognition declares that an authority channel accepts an artifact, shard, assertion, runtime pack, dataset, or another authority channel under a declared scope and policy.

These concepts MUST remain separate.

A valid signature does not imply authority recognition.

Authority recognition does not imply universal truth.

A tenant may trust a signer for distribution while not recognizing the artifact as reference material.

A tenant may recognize an authority channel for one scope while rejecting it for another.

## Distribution Channel Isolation

### 11. Distribution channels

Runtime Pack distribution MUST be isolated per tenant or per declared public channel by one or more of:

* separate package indexes;
* tenant-authenticated endpoints;
* tenant-specific offline bundle channels;
* public reference channels;
* signed release channels;
* pinned channel manifests;
* access-controlled replication.

Clients MUST NOT activate packs from channels that are not trusted under the active tenant or reader policy.

Clients MUST NOT assume that a valid signature under another tenant’s trust roots authorizes local activation.

### 12. Runtime Pack source status

Runtime Packs MUST declare the status of the source artifact from which they were produced.

At minimum, the manifest SHOULD distinguish:

* `working_exchange`;
* `reference_exchange`;
* `deprecated_exchange`;
* `revoked_exchange`, when relevant.

A Runtime Pack derived from a Working Exchange may be usable in research, review, creative, or internal contexts.

A Runtime Pack derived from a Reference Exchange may be usable in stricter reader policies, depending on authority recognition, validation status, certainty level, and tenant policy.

The source status MUST be visible to policy engines and reader surfaces.

## Control Plane vs Data Plane

### 13. Orgo as control plane

Orgo SHOULD store tenant-scoped control-plane records, including:

* workflow state;
* review state;
* approval state;
* build requests;
* validation tasks;
* authority-recognition workflow;
* distribution status;
* audit logs;
* policy configuration;
* reader-policy assignments;
* key references;
* trust-root sets;
* tenant artifact handles;
* operational release records.

Kristal artifacts SHOULD store:

* content;
* manifests;
* provenance;
* validation references;
* authority-recognition references;
* certainty metadata;
* reproducibility policy selections;
* query semantics;
* signatures;
* integrity hashes.

Workflow state MUST NOT be required to compute global artifact identity.

### 14. Konnaxion distribution and offline caching

Konnaxion clients and nodes MUST:

* verify signatures against the active trust roots before activating a pack;
* check distribution-channel authorization;
* enforce tenant-separated caches;
* enforce reader-policy visibility;
* preserve artifact status labels;
* preserve validation and certainty labels;
* prevent unauthorized cross-tenant cache reuse;
* enforce rollback and downgrade policies within each tenant or channel;
* distinguish between local possession and tenant-authorized use.

Konnaxion MAY store the same underlying bytes once for efficiency, but only if cache access is logically partitioned and authorization is checked before every tenant-visible use.

### 15. Architect rendering

Architect and other rendering systems MUST preserve tenant, authority, validation, certainty, and reader-policy labels when rendering Kristal content.

Rendering systems MUST NOT flatten scoped recognition into universal truth.

Rendering systems MUST NOT show tenant-private artifacts to unauthorized readers.

Rendering systems SHOULD make it clear when the current view is filtered by tenant, authority channel, certainty level, validation status, or reader policy.

## Reproducibility and Comparability Across Tenants

### 16. Tenant-independent reproducibility

Given identical inputs, canonicalization rules, and policy selections, two tenants compiling the same Exchange content MUST be able to produce:

* identical Exchange content hashes;
* the same `kristal_id`;
* byte-identical exports when using the same export profile and serialization rules;
* reproducible Runtime Packs when using the same portable runtime policies.

Tenant-local approvals, access controls, logs, and distribution status MUST NOT break reproducibility of the underlying Exchange content.

### 17. Tenant-configurable policy selection

Tenants MAY choose different portable policies for Runtime Packs, including:

* row groups;
* ordering policies;
* query indexes;
* subset recipes;
* reader-policy filters;
* authority-channel selection;
* offline packaging options;
* distribution-channel constraints.

When tenants choose different portable policies, those selections MUST be recorded in the relevant manifests so artifacts remain comparable and reproducible within their policy class.

### 18. Reader-policy-specific outputs

A tenant may generate different reader-policy views from the same underlying Exchange.

For example:

* `reference_only`;
* `validated_only`;
* `high_certainty_only`;
* `research`;
* `creative`;
* `all_with_labels`;
* `custom`.

These views MUST NOT alter the underlying global content ID unless they create a distinct derived artifact with its own declared content boundary.

Reader-policy views MUST preserve enough metadata to show what was included, excluded, or hidden by policy.

## Authority Channels Across Tenants

### 19. Tenant authority channels

A tenant may define local authority channels.

A tenant may recognize external authority channels.

A tenant may reject or ignore external authority channels.

A tenant may delegate recognition to another authority channel for a declared scope.

Example:

```text
A tenant may recognize WHO for health guidance.
A tenant may recognize UNESCO for heritage or global education references.
A tenant may recognize a company for documentation of its own systems.
A tenant may recognize a local board for municipal policy.
```

Recognition MUST remain scoped.

Recognition by one tenant or authority channel MUST NOT imply recognition by another.

### 20. Shared authority channels

Multiple tenants MAY subscribe to the same authority channel.

When they do, each tenant MUST still declare or inherit:

* which trust roots are accepted;
* which scopes are recognized;
* which validation policies apply;
* which reader policies use the recognition;
* which revocation sources are monitored.

Shared authority channels simplify reference reuse, but they do not remove tenant access-control obligations.

## Threat Considerations

### 21. Correlation risk

Global IDs can reveal that two tenants have identical content if IDs are exposed publicly.

Mitigations SHOULD include:

* opaque handles externally;
* tenant-authenticated lookup;
* avoiding raw IDs in public URLs;
* rate-limited artifact lookup;
* consistent “not found or not authorized” responses;
* tenant-scoped logs;
* separated public and private registries.

### 22. Downgrade and rollback attacks

Clients MUST apply a per-tenant or per-channel rollback and downgrade prevention policy.

Signed latest pointers, pinned release channels, monotonic version channels, revocation records, or transparency logs SHOULD be used where appropriate.

A client MUST NOT activate an older Runtime Pack if the active tenant or channel policy rejects rollback to that version.

### 23. Cross-tenant cache pollution

Client caches MUST be logically partitioned by tenant and channel.

Package indices MUST be tenant-authenticated or channel-authenticated.

A client MUST NOT satisfy a tenant request with cached content from another tenant unless explicit policy allows it and all authorization, signature, trust-root, and reader-policy checks succeed.

### 24. Unauthorized inference

Systems MUST avoid revealing sensitive tenant information through:

* error messages;
* timing differences;
* package index enumeration;
* signature metadata exposure;
* authority-channel membership queries;
* release-channel probing;
* log access;
* shared cache hits.

Where correlation risk matters, deployments SHOULD prefer opaque handles and tenant-authenticated lookup.

### 25. Trust-root confusion

Clients MUST verify artifacts under the active tenant or channel trust roots.

A signature valid under one tenant’s trust roots MUST NOT be accepted as valid under another tenant unless that second tenant explicitly recognizes the signer, trust root, or authority channel.

### 26. Reader-policy confusion

A user interface MUST NOT present an artifact as visible, recognized, validated, or high-certainty unless it satisfies the active reader policy.

Possession of a Runtime Pack does not imply permission to use it.

Successful integrity verification does not imply reader-policy acceptance.

Authority recognition does not imply visibility for every tenant.

## Recommended Implementation Patterns

### Tenant-scoped artifact registry

Use a tenant-scoped artifact registry that maps:

```text
tenant_artifact_handle
→ kristal_id
→ allowed_channels
→ authority_channel_refs
→ trust_root_refs
→ reader_policy_refs
→ policy_class
→ visibility_state
```

The registry may store:

* tenant-local handles;
* raw global content IDs;
* channel membership;
* trust-root bindings;
* visibility policies;
* access grants;
* revocation status;
* release-channel state.

### Public reference registry

Use a separate public reference registry for intentionally shared Kristals.

The public registry may expose raw global content IDs when correlation is intended.

Private tenants may mirror public reference artifacts through local handles.

### Cache partitioning

Implementations MAY deduplicate bytes internally, but MUST partition access logically by:

* tenant;
* environment;
* distribution channel;
* reader policy;
* activation status;
* trust-root set.

### Structured logs

Structured logs SHOULD include fields such as:

```json
{
  "tenant_id": "tenant:<slug>",
  "environment": "prod",
  "build_id": "build:<id>",
  "kristal_id": "sha256:<hex>",
  "tenant_artifact_handle": "tenant-artifact:<tenant-scope>:<opaque-id>",
  "authority_channel": "authority:<slug>",
  "reader_policy_id": "reader_policy:<slug>",
  "runtime_pack_id": "sha256:<hex>",
  "event": "runtime_pack_activation_checked"
}
```

Log access MUST be tenant-scoped.

Logs SHOULD avoid exposing raw global content IDs in contexts where correlation risk matters.

## Conformance

A deployment conforms to this multi-tenancy boundary model if:

* global content IDs are derived from canonicalized content, not tenant metadata;
* tenant isolation is enforced through access control, trust roots, signing domains, distribution channels, and reader policies;
* signatures do not alter global content IDs;
* Runtime Pack caches are tenant-separated or logically partitioned;
* cross-tenant artifact enumeration is prevented;
* tenant-local handles are used where correlation risk requires them;
* Orgo control-plane records do not affect global artifact identity;
* Konnaxion activation checks are tenant- and channel-scoped;
* authority recognition remains scoped;
* reader-policy visibility remains explicit;
* downgrade and rollback protections are enforced per tenant or channel.

A deployment is not conformant if:

* tenant metadata changes `kristal_id` for identical Exchange content;
* raw global IDs are exposed in unauthenticated contexts where correlation risk is prohibited;
* clients can activate packs from untrusted tenant or channel contexts;
* signatures from one tenant are accepted in another without explicit trust-root or authority recognition;
* cross-tenant caches leak private artifacts;
* UI surfaces hide tenant, validation, certainty, authority, or reader-policy distinctions.

## Summary

Kristal v5 keeps artifact identity and tenant access control separate.

The same content may produce the same global content ID across tenants, but access, visibility, recognition, signing, distribution, activation, and reader-policy use are tenant-scoped.

The rule is:

> Global content identity enables reproducibility and shared references.
> Tenant policy decides who can see, trust, recognize, activate, or use them.

Multi-tenancy in Kristal v5 is therefore a layering model:

```text
global artifact identity
+ tenant-scoped handles
+ access control
+ signing domains
+ authority recognition
+ distribution channels
+ reader policies
+ runtime activation policy
```

This preserves reproducibility without weakening tenant isolation.
