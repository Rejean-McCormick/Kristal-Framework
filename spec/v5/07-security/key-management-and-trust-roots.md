# Key Management and Trust Roots (Kristal v5)

## Status

Draft — implementation-ready defaults; future profiles may extend.

## Purpose

This document defines how Kristal v5 artifacts are signed, how trust roots are established, how authority channels are anchored, and how verifiers validate signatures, hashes, revocations, and signing scopes when integrity declarations are present.

This document is security and operations focused. It does **not** change Kristal’s core content-addressed identity rules. It defines the trust model around distribution, verification, authority recognition, Runtime Pack activation, and offline use.

Kristal v5 separates:

* artifact integrity;
* authority recognition;
* validation status;
* certainty level;
* reader policy;
* runtime activation.

A signed artifact is not automatically true, validated, or recognized by every authority. A signature proves that a signer, key, or authority channel made or approved a declared artifact under a declared scope.

## Scope

In scope:

* key types and roles;
* supported signature algorithms;
* trust root pinning models;
* authority-channel trust roots;
* signature verification requirements for distributors and clients;
* signing targets for Exchange artifacts, Runtime Packs, Authority Registries, Validation Decisions, and Recognition artifacts;
* rotation, revocation, and compromise handling;
* minimum manifest fields for signer identity and key metadata;
* Runtime Pack signing scope;
* offline verification requirements.

Out of scope:

* network PKI / CA integration details, which may be deployment-specific;
* secrets storage implementation, such as HSM, KMS, or local secure enclaves;
* authority governance process outside the machine-readable trust model;
* semantic validation of claims;
* reader-policy selection.

## Normative keywords

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

---

# 1. Design goals

Kristal v5 key management has the following design goals:

* **Integrity enforcement:** when signatures, hashes, trust roots, or revocation requirements are declared, verifiers enforce them according to policy.
* **Authority pluralism:** different authority channels may use different trust roots and policies.
* **Scoped recognition:** recognition by one authority channel does not imply recognition by another.
* **Tenant isolation:** tenants may use independent trust roots and keys.
* **Offline viability:** verification should be possible without network access.
* **Operational safety:** rotation, rollback prevention, and compromise response are first-class.
* **Label preservation:** signature verification must not erase validation status, certainty level, scope, or authority-channel information.

---

# 2. Supported signature algorithms

## 2.1 Baseline

Verifiers MUST support:

* `ed25519`

Artifacts SHOULD prefer `ed25519` when available.

## 2.2 Compatibility

Verifiers MAY support:

* `rsa-pss-sha256`

Deployments MUST document which compatibility algorithms are enabled.

Compatibility algorithms MUST NOT silently weaken trust decisions. If a deployment restricts certain algorithms to specific authority channels, environments, or artifact types, those restrictions MUST be explicit in policy.

---

# 3. Key roles

## 3.1 Trust Root

A trust root is a long-lived key or root set that anchors trust for a tenant, environment, authority channel, or registry.

Requirements:

* Trust roots MUST be pin-able by distributors and clients.
* Trust roots SHOULD be offline or highly protected.
* Trust roots SHOULD NOT sign ordinary artifacts directly.
* Trust roots SHOULD sign intermediates, authority registry updates, revocation lists, or root-transition attestations.
* Trust roots MUST be scoped by tenant, environment, authority channel, or deployment policy.

## 3.2 Intermediate / Release Authority Key

An intermediate key is a medium-lived key used to sign artifact signing keys, release signing certificates, validation decision keys, or recognition attestations.

Requirements:

* Intermediates MUST be signed by a trust root or another valid intermediate under declared policy.
* Intermediates MUST include validity windows.
* Intermediates SHOULD be rotated on a scheduled basis.
* Intermediates MUST declare their permitted scope.

Permitted scope may include:

* tenant;
* environment;
* artifact type;
* authority channel;
* validation policy;
* recognition policy;
* Runtime Pack profile;
* publication channel.

## 3.3 Artifact Signing Key

An artifact signing key is a shorter-lived key used to sign Kristal artifacts.

Artifact signing keys MAY sign:

* Exchange artifacts;
* Runtime Pack manifests;
* Authority Registries;
* Validation Decisions;
* Authority Recognition artifacts;
* revocation lists;
* transparency log entries;
* release bundles.

Requirements:

* Signing keys MUST be scoped.
* Signing keys SHOULD be rotated regularly.
* Signing keys MUST be auditable.
* Signing keys MUST have stable `key_id` values.
* Signing keys MUST NOT be used outside their declared scope.

## 3.4 Authority Channel Signing Key

An authority channel signing key is a key authorized to sign on behalf of a declared authority channel.

It may sign:

* validation decisions;
* recognition decisions;
* authority-channel metadata;
* scope declarations;
* policy declarations;
* delegated authority attestations.

Requirements:

* The key MUST be linked to an `authority_channel_id`.
* The key MUST be included in or referenced by the Authority Registry.
* The key MUST only sign decisions within its declared scope.
* A verifier MUST NOT treat an authority-channel signature as universal recognition outside its scope.

## 3.5 Runtime Pack Signing Key

A Runtime Pack signing key signs deployable offline packages.

Requirements:

* The key MUST be scoped to Runtime Pack signing.
* The signing target MUST include the Runtime Pack manifest and referenced file integrity.
* The signature MUST preserve source artifact status.
* A Runtime Pack signature MUST NOT imply that a working artifact is a reference artifact.

---

# 4. Trust models

## 4.1 Tenant-pinned trust roots

Each tenant has its own trust root or root set. Clients pin the tenant’s root fingerprints.

Advantages:

* strong tenant isolation;
* offline verification;
* reduced blast radius.

This model is recommended for multi-tenant deployments.

## 4.2 Environment-pinned trust roots

A deployment pins roots by environment, such as development, staging, or production. Tenants are separated by access control and authority registry policy rather than by separate roots.

Advantages:

* simpler operation for small deployments;
* offline verification.

Risk:

* larger blast radius if the root is compromised.

## 4.3 Authority-channel trust roots

Each authority channel may declare its own trust roots.

Examples:

* `authority:wikidata-seed`;
* `authority:who`;
* `authority:unesco-global-reference`;
* `authority:microsoft-systems`;
* `authority:local-research-collective`.

Requirements:

* Authority-channel trust roots MUST be declared in or referenced by an Authority Registry.
* Recognition by an authority channel MUST be scoped.
* Recognition by one authority channel MUST NOT imply recognition by another authority channel.
* Delegated authority MUST be explicit.

## 4.4 Hybrid trust roots

A deployment MAY combine tenant, environment, and authority-channel roots.

If hybrid trust roots are used, the Authority Registry or deployment policy MUST make precedence and scope explicit.

---

# 5. Authority Registry

Deployments SHOULD maintain a pinned, versioned **Authority Registry** artifact.

An Authority Registry defines:

* active, deprecated, and blocked trust roots;
* authority channels;
* authority-channel scopes;
* allowed signing keys;
* validation policies;
* recognition policies;
* delegation rules;
* revocation list references;
* required profiles;
* minimum signature requirements.

When present, distributors and clients SHOULD treat the Authority Registry as the policy input for verification, validation recognition, and authority-channel trust decisions.

The Authority Registry does not make all contained claims true. It defines which authorities, keys, policies, and scopes are accepted for a particular verification or recognition decision.

---

# 6. Artifact signature requirements

## 6.1 When signatures are present

If an artifact declares signatures, verifiers MUST:

1. Validate the signature against the artifact’s declared signing target.
2. Validate the signing target against the artifact’s canonical hashing rules.
3. Validate signer identity.
4. Validate signer scope.
5. Validate the key chain to a pinned trust root or Authority Registry root.
6. Enforce validity windows.
7. Enforce revocation policy when applicable.
8. Enforce downgrade and rollback policy when applicable.
9. Preserve validation, certainty, scope, and authority-channel labels.

If any required step fails, the artifact MUST NOT be accepted for the requested trust decision.

A failed signature verification MAY still allow inspection of the artifact in a diagnostic, forensic, research, or untrusted view, provided the artifact is clearly marked as not accepted under the requested trust policy.

## 6.2 What a signature proves

A valid signature proves that the declared signer signed the declared signing target under a declared key and scope.

A valid signature does not, by itself, prove:

* that all assertions are true;
* that all assertions are high certainty;
* that an artifact is recognized by every authority;
* that a working artifact is a reference artifact;
* that a Runtime Pack contains the full source artifact;
* that a reader policy should include the artifact by default.

Those decisions require validation policy, recognition policy, scope, authority channel, and reader policy.

---

# 7. Signing targets

The signed payload MUST be the canonical hash of the artifact’s declared hash target, excluding signatures themselves.

The signing target MUST be unambiguous and recorded in the artifact or manifest.

## 7.1 Exchange artifacts

For Exchange artifacts:

* The signing target MUST be the canonical hash of the Exchange identity payload.
* The signing target MUST exclude `signatures`.
* The manifest MUST make it unambiguous how the payload hash was computed.
* The signature MUST preserve `artifact_status`, such as `working` or `reference`.

A signature over a `working_exchange` MUST NOT be interpreted as recognition of a `reference_exchange`.

## 7.2 Runtime Packs

For Runtime Packs, the signing target MUST cover:

1. the canonical hash of the Runtime Pack manifest, excluding signatures;
2. the integrity of all referenced payload files as recorded in the manifest;
3. the declared source artifact references;
4. the declared Runtime Pack policies;
5. the declared reader-policy materialization, if any;
6. the declared validation, certainty, or authority-channel materialization, if any.

A Runtime Pack manifest MUST include hashes for every payload file it references.

The pack signature MUST be computed over the manifest that includes those hashes.

Manifest-only signing MAY exist only as a deployment-specific profile. It MUST NOT be the default.

## 7.3 Authority Registry

For Authority Registries:

* The signing target MUST include trust roots.
* The signing target MUST include authority channels.
* The signing target MUST include validation policies.
* The signing target MUST include recognition policies.
* The signing target MUST include revocation list references.
* The signing target MUST exclude registry signatures.

A verifier MUST NOT apply an Authority Registry whose signature target is ambiguous.

## 7.4 Validation Decisions

For Validation Decisions:

* The signing target MUST include the target reference.
* The signing target MUST include target level.
* The signing target MUST include validation status.
* The signing target MUST include `validated_as`.
* The signing target MUST include certainty level.
* The signing target MUST include authority channel.
* The signing target MUST include validation policy reference.
* The signing target MUST include scope.
* The signing target MUST exclude signatures.

A Validation Decision MUST NOT be interpreted outside its declared scope.

## 7.5 Authority Recognition artifacts

For Authority Recognition artifacts:

* The signing target MUST include issuer authority channel.
* The signing target MUST include target reference.
* The signing target MUST include target level.
* The signing target MUST include recognition status.
* The signing target MUST include recognized-as status.
* The signing target MUST include scope.
* The signing target MUST include recognition or validation policy references.
* The signing target MUST exclude signatures.

Recognition by one authority channel MUST NOT be treated as recognition by another unless explicit delegation or recognition exists.

## 7.6 Revocation lists

For revocation lists:

* The signing target MUST include revoked key IDs or artifact IDs.
* The signing target MUST include reasons.
* The signing target MUST include effective timestamps.
* The signing target MUST include issuer identity.
* The signing target MUST exclude signatures.

Revocation lists SHOULD be signed by a trust root or authorized intermediate.

---

# 8. Recommended signature envelope fields

Signed artifacts SHOULD include a `signatures[]` section in a manifest-like structure with:

* `sig_id`;
* `alg`;
* `key_id`;
* `signer`;
* `signer_type`;
* `authority_channel_id`, if applicable;
* `created_at`;
* `expires_at`, if applicable;
* `scope`, if applicable;
* `payload_hash`;
* `signature`;
* `chain`, if applicable;
* `policy_refs`, if applicable.

Recommended shape:

```json
{
  "sig_id": "sig:example",
  "alg": "ed25519",
  "key_id": "key:example",
  "signer": "Example Authority",
  "signer_type": "authority_channel",
  "authority_channel_id": "authority:example",
  "created_at": "2026-01-01T00:00:00Z",
  "expires_at": "2027-01-01T00:00:00Z",
  "scope": {
    "domain": "science"
  },
  "payload_hash": {
    "alg": "sha256",
    "value": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "signature": "base64url-or-multibase-signature",
  "chain": [],
  "policy_refs": []
}
```

Exact envelope shape is implementation-defined, but all required semantic fields MUST be representable.

Fields used for signature verification MUST NOT be ambiguous.

---

# 9. Trust root pinning and distribution

## 9.1 Pins

A pin is a stable fingerprint of a trust root public key.

Requirements:

* Pins MUST be distributed to clients out-of-band or via a secure bootstrap channel.
* Pins MUST be stored and enforced locally for offline verification.
* Pins SHOULD support multiple active roots to enable rotation.
* Pins SHOULD be associated with tenant, environment, and authority-channel scope.

## 9.2 Pin sets

Clients and distributors SHOULD support pin sets:

* `active_roots[]`;
* `deprecated_roots[]`;
* `blocked_roots[]`.

Policies around acceptance of deprecated roots MUST be documented.

Blocked roots MUST NOT be accepted for new trust decisions.

## 9.3 Offline pinning

Clients that operate offline MUST have access to the required pins, Authority Registry, and revocation data needed by the active policy.

If the active policy requires a trust root or registry that is unavailable, the client MUST NOT represent the artifact as accepted under that policy.

---

# 10. Authority delegation

Authority channels MAY recognize other authority channels.

Examples:

* an international organization recognizes a domain-specific authority;
* a government recognizes a national statistical office;
* a university recognizes a laboratory;
* a standards body recognizes a working group;
* a company recognizes a product documentation signing authority.

Delegation requirements:

* Delegation MUST be explicit.
* Delegation MUST be scoped.
* Delegation MUST declare the delegating authority channel.
* Delegation MUST declare the delegated authority channel.
* Delegation MUST declare the target domain or subdomain.
* Delegation MUST declare whether delegation is transitive.
* Delegation MUST be revocable.

Recognition of an authority channel does not imply universal recognition of all artifacts published by that channel. The applicable validation and recognition policies still apply.

---

# 11. Key rotation

## 11.1 Planned rotation

Trust roots rotate rarely and require careful migration.

Intermediates rotate periodically.

Signing keys rotate frequently.

Rotation requirements:

* Rotation MUST support overlap windows.
* Clients MUST support multiple pinned roots or intermediates during overlap.
* Artifacts SHOULD record which `key_id` signed them.
* Rotation events SHOULD be recorded in operational logs.
* Authority Registries SHOULD reflect current key status.

## 11.2 Emergency rotation

On compromise:

* mark affected key IDs as revoked;
* stop issuing new artifacts signed by the compromised key;
* re-issue current artifacts or packs signed with new keys when needed;
* update Authority Registries;
* update revocation lists;
* apply downgrade and rollback protections;
* publish operational notice through the appropriate distribution channel.

If an artifact was signed by a compromised key, verifiers MUST apply the active revocation and rollback policy.

---

# 12. Revocation

Because clients may be offline, revocation must work without live OCSP or online CRLs.

## 12.1 Recommended approach

Maintain signed revocation list artifacts per tenant, environment, authority channel, or registry scope.

A revocation list SHOULD contain:

* revoked `key_id` values;
* revoked artifact IDs, if applicable;
* revoked authority-channel IDs, if applicable;
* reasons;
* effective timestamps;
* issuer;
* scope;
* signatures.

Revocation lists SHOULD be:

* content-addressed;
* signed;
* versioned;
* distributed alongside Runtime Packs or through Orgo/Konnaxion sync channels.

## 12.2 Client behavior

Clients MUST consult the latest available revocation list before accepting a signature when a revocation list is present and applicable.

If policy requires revocation checking and no revocation list is available, the client MUST NOT accept the artifact under that policy.

Deployments MUST define the revocation policy level per environment.

Example policy levels:

* `ignore`;
* `require_if_present`;
* `require_strict`.

## 12.3 Revocation effects

A revoked key MUST NOT be accepted for new trust decisions after the revocation effective time.

A revoked authority channel MUST NOT be treated as recognized after the revocation effective time.

A revoked artifact MUST NOT be presented as accepted under the affected authority channel or policy.

Revocation does not necessarily delete historical records. It changes their current trust status.

---

# 13. Downgrade and rollback protection

Kristal deployments MUST protect Runtime Pack activation from downgrade and rollback attacks.

Requirements:

* Runtime Packs SHOULD include monotonic version or sequence metadata.
* Activation policy MUST compare candidate packs against the currently active pack.
* A candidate pack signed by revoked keys MUST NOT replace a valid active pack.
* A candidate pack with an older sequence MUST NOT replace a newer pack unless an explicit rollback policy allows it.
* Rollbacks MUST preserve audit records.
* Rollbacks SHOULD require explicit authority or operator action.

A Runtime Pack that fails activation requirements MAY still be inspected as an inactive candidate if the reader clearly marks it as not active under the selected policy.

---

# 14. Verification responsibilities by component

## 14.1 Orgo — control plane

Orgo MUST record:

* build ID;
* artifact IDs;
* signer `key_id`;
* signature metadata;
* validation decision references;
* authority recognition references;
* release status;
* publication status;
* activation status when applicable.

Orgo SHOULD:

* enforce “no publish without required signatures” in environments where signatures are required;
* manage rotation schedules;
* manage revocation list publication;
* publish or update Authority Registries;
* record operational audit trails;
* preserve distinction between working artifacts and reference artifacts.

## 14.2 Konnaxion — distribution and client UX

Konnaxion MUST:

* verify signatures when present and required by policy before activating a Runtime Pack;
* pin trust roots per tenant, environment, or Authority Registry policy;
* enforce rollback and downgrade policy;
* preserve artifact status;
* expose validation, certainty, authority, and reader-policy labels where applicable.

Konnaxion MUST NOT present a Runtime Pack as accepted under an authority channel unless the applicable trust, validation, and recognition requirements are satisfied.

## 14.3 Architect — renderer

Architect SHOULD verify that inputs satisfy the active reader policy before rendering.

Architect MUST preserve:

* validation labels;
* certainty labels;
* authority labels;
* disputed status;
* fictional or mythological scope;
* provenance traceability.

Architect MUST NOT flatten scoped validation into universal truth.

Architect does not need to re-sign artifacts unless it produces distributable outputs.

## 14.4 SenTient — resolver

SenTient is not typically a signer.

SenTient MAY sign resolver outputs if the deployment treats resolver output as a distributable artifact.

If SenTient signs outputs, those signatures MUST declare scope and target.

## 14.5 Kristal compiler

The Kristal compiler MUST produce deterministic artifact identity and hashing outputs according to the declared canonicalization and reproducibility profiles.

The compiler MAY produce working artifacts before validation decisions are complete.

Compiler output signatures prove compiler output identity and integrity. They do not imply authority recognition unless a recognized authority channel signs or recognizes the artifact.

---

# 15. Minimum security acceptance criteria

A deployment meets minimum Kristal v5 security criteria if:

1. Signed artifacts are verified according to their declared signing target.
2. Trust roots are pinned and enforceable offline.
3. Authority channels are scoped and auditable.
4. Key rotation is supported.
5. Revocation list distribution exists for environments where revocation is required.
6. Downgrade and rollback protection is implemented for Runtime Pack activation.
7. Signature verification preserves artifact status, validation status, certainty level, scope, and authority-channel labels.
8. A valid signature is not treated as universal truth, universal validation, or universal recognition.
9. Runtime Packs do not erase whether they derive from working artifacts or reference artifacts.
10. Reader policies remain explicit and inspectable.

---

# 16. Optional profiles

Future optional profiles MAY define:

* transparency logs;
* append-only release ledgers;
* threshold signatures;
* multi-authority recognition;
* hardware-backed signing;
* remote attestation;
* authority-channel delegation graphs;
* policy-specific revocation models;
* audit bundle formats.

Transparency logs are recommended for environments that require strong auditability, compromise detection, or public accountability.

---

# 17. Summary

Kristal v5 key management protects artifact identity, signing authority, policy scope, and offline verification.

It does not create a universal truth authority.

A signed artifact means:

> This signer signed this target, under this key, within this declared scope.

A recognized artifact means:

> This authority channel accepts this target under this recognition policy and scope.

A validated assertion means:

> This authority channel accepts this assertion as a specific kind of claim, at a declared certainty level, under a declared validation policy and scope.

These meanings MUST remain separate.

Integrity protects artifacts. Authority is plural. Recognition is scoped. Certainty remains explicit.
