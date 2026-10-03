# 01-core-spec/signatures-trust.md

## Status

Draft (v5)

## Purpose

This document specifies the **normative** rules for:

* signature and attestation structures used in Kristal v5 artifacts
* what is signed and how signing inputs are constructed
* required verification semantics for signatures, content identity, and trust roots
* trust-root and key identity (`key_id` / KID), including offline verification expectations
* minimum interoperability requirements for mandatory-to-implement algorithms
* the relationship between signatures, authority recognition, validation status, and reader policy

This document applies to:

* **Structured Epistemic State** artifacts
* **Kristal Exchange** artifacts
* **Runtime Pack** manifests
* **Exchange Shard** manifests
* **Exchange Federation** manifests
* **Authority Registry** artifacts
* **Authority Recognition** artifacts
* **Validation Decision** artifacts
* **Revocation** artifacts
* other derived Kristal artifacts that explicitly declare conformance to this signature model

---

## 1. Terminology

* **Artifact**: a JSON object that declares a Kristal v5 `artifact_type`.
* **Content identity**: the artifact’s content-addressed identifier, computed per `01-core-spec/ids-canonicalization-hashing.md`.
* **Hash target**: the JSON object that is canonicalized and hashed to produce content identity, with signature overlays and any excluded self-identifying fields removed according to the ID and canonicalization rules.
* **Signature**: a cryptographic proof that binds an issuer key to an artifact’s content identity.
* **Attestation**: a signature produced by a third party, such as an auditor, publisher, validator, distributor, authority channel, or review body, over the same content identity.
* **Trust root**: a pinned set of public keys, certificates, or equivalent verifier-recognized trust material used for a given scope, tenant, authority channel, environment, or reader policy.
* **Authority channel**: a declared source of recognition or validation within a specific scope and policy.
* **Validation decision**: a scoped decision asserting that an artifact, shard, assertion, runtime pack, or authority channel has a particular validation status under a declared policy.
* **Recognition**: a scoped acceptance by an authority channel that a target is trusted, reference-worthy, conditionally accepted, rejected, revoked, or otherwise classified under that channel.
* **Reader policy**: a policy used by a reader, runtime, application, or user interface to decide which artifacts, assertions, validation statuses, certainty levels, and authority channels are visible or trusted in a given view.
* **Unsigned artifact**: an artifact with no `signatures` field, or with an empty `signatures` array.
* **Required signature**: a signature whose `required` field is `true` or omitted.

Normative keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.

---

## 2. Core principles

1. **Content IDs are not signatures.**
   Content identity proves content equivalence. Signatures prove issuer authenticity, issuer continuity, or issuer authorization relative to a trust store or authority channel.

2. **Signatures MUST NOT be included in the content-hash target.**
   Signatures are overlays. The content identity is computed over the artifact with signature fields excluded.

3. **Output identity fields MUST NOT hash themselves.**
   Any field that stores the artifact’s own content identity, such as `kristal_id`, `state_id`, `runtime_pack_id`, `federation_id`, `shard_id`, `recognition_id`, or `validation_decision_id`, MUST be excluded from the hash target used to produce that same identity.

4. **Verification MUST be offline-capable.**
   A verifier MUST be able to verify a signed artifact with no network access, given the artifact, its declared signature material, and the relevant trust roots.

5. **Integrity verification protects artifact identity.**
   Signature verification determines whether a key recognized by the verifier signed the artifact’s content identity. It does not, by itself, prove that the artifact is universally true, globally valid, high-certainty, or recognized by every authority channel.

6. **Validation, certainty, and recognition are separate from signatures.**
   A signature MAY support publication, distribution, recognition, validation, or audit, but those statuses MUST be expressed through explicit validation decisions, authority recognition records, manifests, or reader policies.

7. **Verification failure is a status, not a metaphysical judgment.**
   If a required signature cannot be verified, the artifact MUST NOT be treated as signature-verified or accepted by any policy requiring that signature. The artifact MAY still be stored, inspected, rendered with warning labels, used in research contexts, or processed under a policy that allows unverified material.

---

## 3. Signature envelope

### 3.1 Where signatures live

Artifacts that support signatures MUST include signatures only in the top-level field:

* `signatures`: an array of signature objects

If `signatures` is absent or empty, the artifact is considered **unsigned**.

Signature objects MUST be carried only in the top-level `signatures` field. If signature-like fields appear elsewhere, verifiers MUST exclude them from the hash target and SHOULD mark the artifact as non-conformant unless the relevant artifact profile explicitly defines those fields.

### 3.2 Signature object schema

Each entry in `signatures[]` MUST be an object with:

* `key_id` (string): key identifier used to locate the issuer public key in a trust store
* `alg` (string): signing algorithm identifier
* `signature` (string): signature bytes encoded as base64url without padding
* `created_at` (string, optional): ISO 8601 / RFC 3339 timestamp
* `required` (boolean, optional): defaults to `true`

Optional fields:

* `purpose` (string): signature purpose, such as `"publisher"`, `"validator"`, `"authority"`, `"auditor"`, `"distributor"`, or `"reviewer"`
* `signer` (object): human-readable signer metadata, such as `{ "name": "...", "org": "..." }`
* `authority_channel` (string): authority channel under which the signature is issued or interpreted
* `scope` (object): optional scope for which the signature is intended
* `validation_policy_ref` (object): optional reference to the policy that interprets this signature
* `expires_at` (string): ISO 8601 / RFC 3339 timestamp
* `notes` (string)
* `x5c` (array of strings): X.509 certificate chain, encoded as base64 DER, if a profile enables certificate-chain verification
* `extensions` (object): implementation-specific extension fields

A signature object MUST NOT be interpreted as a validation decision unless a profile or policy explicitly maps that signature to a validation decision or authority recognition record.

### 3.3 Mandatory-to-implement algorithms

To ensure interoperability, Kristal v5 implementations MUST support verification for:

* `alg = "ed25519"`
* content identity hash algorithm `sha256`
* canonicalization profile `kristal.v5:jcs-rfc8785`

Implementations MAY support additional algorithms, but MUST NOT claim Kristal v5 signature conformance if they cannot verify Ed25519 signatures over Kristal v5 SHA-256 content identities.

---

## 4. Signing input construction

### 4.1 Goals

The signing input MUST:

* bind the issuer to the artifact’s content identity
* prevent ambiguous “what exactly was signed” situations
* be reconstructable deterministically by verifiers from the artifact alone
* remain stable when signatures are added, removed, reordered, or replaced

### 4.2 Signing input

For each signature object `S` in `A.signatures[]`, the signing input MUST be the raw digest bytes of the artifact’s content identity.

For a content identity encoded as:

```text
sha256:<hex>
```

the signing input is the 32 raw bytes represented by `<hex>`.

For artifacts whose identity field stores only the hex digest, the signing input is the 32 raw bytes represented by that hex value.

The following artifact identity fields are recognized by this document:

* `state_id`
* `kristal_id`
* `runtime_pack_id`
* `shard_id`
* `federation_id`
* `registry_id`
* `recognition_id`
* `validation_decision_id`
* `revocation_id`
* any profile-defined identity field that explicitly declares conformance to the Kristal v5 content identity model

### 4.3 Identity recomputation requirement

Before verifying any signatures, verifiers MUST recompute the artifact’s content identity from the artifact itself, according to `01-core-spec/ids-canonicalization-hashing.md`.

The recomputation MUST exclude:

* the top-level `signatures` field
* the artifact’s own identity field
* any profile-declared signature overlays
* any profile-declared non-hash fields

If the recomputed identity does not match the declared identity field, the artifact’s identity verification fails.

An artifact whose identity verification fails MUST NOT be treated as content-identity-verified. Any reader, runtime, publisher, or validator that requires verified identity MUST reject it for that policy.

The artifact MAY still be preserved, inspected, analyzed, or displayed as unverified if the active reader policy allows that behavior.

### 4.4 Signature computation

For `alg = "ed25519"`:

* signature input MUST be the raw digest bytes described in Section 4.2
* `signature` MUST be the base64url-encoded Ed25519 signature bytes, without padding

---

## 5. Verification rules

### 5.1 Verification procedure

Given an artifact `A`:

1. If `A.signatures` is absent or empty, the artifact is **unsigned**.
2. If `A.signatures` is present:

   1. Recompute `A`’s content identity from `A`, excluding signatures and other declared non-hash fields.
   2. Compare the recomputed identity to the declared identity.
   3. For each signature object `S` in `A.signatures`:

      * validate that required fields exist and are well-formed;
      * resolve the public key for `S.key_id` from the verifier’s trust store;
      * verify that `S.alg` is supported;
      * verify `S.signature` over the signing input defined in Section 4.2;
      * evaluate optional fields such as `expires_at`, `purpose`, `authority_channel`, and `scope` if required by the active policy.
3. Apply required and optional signature semantics:

   * if `S.required` is true or missing, it is required;
   * if `S.required` is false, the signature is optional;
   * required signatures affect whether the artifact satisfies policies that require verified signatures;
   * optional signature failures MUST be reported but do not by themselves invalidate other successfully verified signatures.

### 5.2 Required verification semantics

If an artifact contains a required signature, and that required signature cannot be verified, then:

* the artifact MUST NOT be treated as signed by that key;
* the artifact MUST NOT satisfy any policy that requires that signature, key, authority channel, purpose, or trust root;
* the artifact MUST NOT be published, distributed, activated, rendered as verified, or recognized under a policy that requires successful verification of that signature;
* the failure MUST be visible to validation, distribution, runtime, or reader systems that evaluate the artifact.

The artifact MAY still exist as an unsigned, partially verified, unverified, disputed, research, archival, or diagnostic object if a policy explicitly allows that status.

### 5.3 Partial verification

Verifiers MUST NOT silently skip signatures they cannot process if those signatures are required.

If a verifier does not support the algorithm referenced by a required signature, verification for that signature MUST fail for that verifier.

If a verifier cannot resolve the key referenced by a required signature, verification for that signature MUST fail for that verifier.

If a verifier can verify some signatures but not others, the verifier MUST report signature status per signature.

### 5.4 Signature status values

Implementations SHOULD expose signature verification results using the following statuses:

```text
signature_status:
  - not_present
  - verified
  - failed
  - unsupported_alg
  - missing_key
  - expired
  - malformed
  - identity_mismatch
  - policy_not_satisfied
  - not_evaluated
```

A single artifact MAY contain signatures with different statuses.

### 5.5 Artifact verification status

Implementations SHOULD expose artifact-level verification status using the following values:

```text
artifact_verification_status:
  - unsigned
  - identity_verified
  - identity_mismatch
  - signature_verified
  - partially_verified
  - signature_failed
  - policy_satisfied
  - policy_not_satisfied
  - not_evaluated
```

Artifact verification status MUST NOT be confused with assertion validation status, authority recognition, or certainty level.

---

## 6. Trust roots, key identity, and multi-tenancy

### 6.1 Trust roots

Each verifier MUST maintain or receive a trust store containing:

* trusted public keys, certificates, or equivalent trust material keyed by `key_id`
* the scope, tenant, environment, authority channel, or policy for which each key is trusted
* optional validity windows
* optional revocation metadata
* optional allowed purposes

Trust stores MAY be:

* tenant-scoped
* environment-scoped
* device-scoped
* authority-channel-scoped
* reader-policy-scoped
* runtime-pack-scoped
* offline-bundled

### 6.2 `key_id` format

Recommended `key_id` formats include:

* stable string key IDs, such as `"orgo-prod-ed25519-2026-01"`
* key fingerprints using a stable encoding
* URI-like identifiers controlled by an authority channel
* certificate-bound identifiers when an X.509 profile is enabled

A `key_id` MUST be stable enough for deterministic offline verification.

A `key_id` MUST NOT rely on network lookup as the only way to resolve the key.

### 6.3 Key rotation

Implementations SHOULD support key rotation by:

* allowing overlapping validity windows where old and new keys are trusted;
* preserving historical trust material needed to verify older artifacts;
* using short-lived signing keys under longer-lived root keys where appropriate;
* publishing revocations or trust-store updates through explicit revocation artifacts or transparency-log profiles;
* ensuring that offline verifiers can determine whether a key was valid for the artifact and policy being evaluated.

### 6.4 Multi-tenancy

The same signature MAY have different policy effects in different tenants, environments, or authority channels.

For example, a signature may be recognized by one reader policy but ignored by another. A company’s signature may be sufficient for its own technical documentation, but insufficient for an independent safety validation.

Verifiers MUST NOT assume that a valid cryptographic signature implies universal recognition.

---

## 7. What signatures authorize

This specification binds signatures to content identity.

Whether a signature is enough to:

* publish an Exchange into a registry;
* recognize an artifact as a reference;
* distribute a Runtime Pack;
* activate a Runtime Pack;
* display a “verified” label;
* satisfy a validation policy;
* satisfy an authority recognition policy;
* include material in a reader policy view;

is governed by explicit policy.

Recommended minimum policy separation:

* **Kristal** defines artifact identity, canonicalization, hashing, signatures, manifests, query contracts, and verification semantics.
* **Orgo** manages workflows, review routing, approvals, audit records, release records, and operational lifecycle.
* **Konnaxion** distributes Kristals, applies reader policies, manages runtime access, and surfaces validation, authority, and certainty labels.
* **Architect** renders artifacts and summaries without hiding validation labels, authority labels, certainty levels, or disputed status.
* **SenTient** may support extraction, normalization, disambiguation, and Claim-IR profile processing, but Claim-IR is not the universal required input to Kristal v5.

A signature proves that a key signed a content identity. It does not prove that:

* the artifact is globally true;
* every assertion inside the artifact is true;
* every assertion has high certainty;
* the artifact is recognized by all authority channels;
* the artifact is suitable for every reader policy;
* the artifact is validated outside its declared scope.

---

## 8. Relationship to validation, certainty, and recognition

### 8.1 Signatures and validation

A signed artifact MAY be used as evidence in a validation decision.

A signature MAY be required by a validation policy.

A signature MAY be produced by an authority channel as part of a validation decision.

However, signature verification alone MUST NOT be represented as validation unless a validation decision or policy explicitly says so.

### 8.2 Signatures and certainty

A signature does not set certainty level.

Certainty MUST be expressed through fields such as:

```text
certainty_level
validated_as
assertion_status
validation_status
recognition_status
```

An artifact may be signed and still contain low-certainty, disputed, speculative, mythological, fictional, or rejected assertions.

An artifact may be unsigned and still be useful as research material, provided the active reader policy allows it and the status is visible.

### 8.3 Signatures and authority recognition

Authority recognition MUST be represented explicitly through an authority recognition artifact, validation decision, registry entry, or policy-defined equivalent.

A signature may support recognition, but it does not replace the recognition record unless a profile explicitly defines that behavior.

### 8.4 Signatures and reader policy

Reader policies decide which materials are visible or trusted in a particular view.

A reader policy MAY require:

* signed artifacts only;
* signatures from specific authority channels;
* signatures with specific `purpose` values;
* validation decisions signed by recognized validators;
* runtime packs signed by recognized distributors;
* unsigned or partially verified artifacts to remain hidden by default.

A reader policy MAY also allow unsigned, unverified, disputed, fictional, mythological, or low-certainty material in research, creative, archival, or diagnostic modes.

---

## 9. Optional attestation layers

Implementations MAY support multiple signatures in `signatures[]`.

Common signature purposes include:

* `publisher`: the entity that released the artifact
* `validator`: the entity that issued a validation decision
* `authority`: the authority channel recognizing or classifying the artifact
* `auditor`: a third party that reviewed the artifact
* `distributor`: the entity that served or packaged the artifact
* `reviewer`: a person, group, or system that participated in review
* `compiler`: the system that compiled the artifact
* `registry`: the registry that accepted or indexed the artifact

A deployment MAY require:

* at least one valid required signature;
* a specific `purpose` signature;
* a signature from a specific authority channel;
* multiple independent signatures;
* a signature chain;
* a signature plus a validation decision;
* a signature plus a transparency-log entry.

Such requirements MUST be expressed in a validation policy, authority policy, deployment policy, or reader policy.

---

## 10. Revocation and expiry

### 10.1 Expiry

If a signature includes `expires_at`, verifiers SHOULD evaluate it when the active policy requires time validity.

If a signature is expired under the active policy, the signature status SHOULD be `expired`.

Expired signatures MUST NOT satisfy policies requiring currently valid signatures.

A policy MAY still allow expired signatures for archival, historical, or reproducibility purposes.

### 10.2 Revocation

If a key, signature, authority recognition, validation decision, or artifact is revoked, the revocation MUST be represented through a revocation artifact or an authority-channel-specific revocation mechanism.

Revocation evaluation is policy-dependent. Implementations SHOULD expose whether revocation status was checked, unavailable, not applicable, or satisfied.

Recommended revocation statuses:

```text
revocation_status:
  - not_checked
  - not_revoked
  - revoked
  - unknown
  - unavailable_offline
  - not_applicable
```

Offline verifiers SHOULD use the revocation material bundled with the artifact, runtime pack, trust store, registry snapshot, or transparency-log profile.

---

## 11. Transparency log profile

A transparency log is optional but recommended for ecosystems that need public auditability of publication, validation, recognition, revocation, and distribution events.

A transparency log entry MAY record:

* artifact identity
* artifact type
* publisher
* authority channel
* validation decision
* recognition decision
* revocation event
* runtime pack publication
* signature metadata
* timestamp
* inclusion proof
* previous entry or log checkpoint
* signatures over the log entry

A transparency log MUST NOT be required for basic Kristal v5 signature conformance unless a deployment profile explicitly requires it.

---

## 12. Conformance tests

A Kristal v5 implementation MUST provide test vectors that cover:

* positive verification cases with valid identity and valid signature;
* negative cases where artifact tampering causes identity mismatch;
* wrong key;
* missing key;
* malformed signature;
* unsupported algorithm on a required signature;
* expired signature when expiry is policy-enforced;
* required and optional signature mixes;
* multiple signatures with mixed results;
* unsigned artifacts;
* artifacts allowed by research or diagnostic policy despite missing signatures;
* artifacts rejected by a strict reader or activation policy because required verification is not satisfied.

Test vectors SHOULD include:

* Structured Epistemic State artifacts
* Exchange artifacts
* Runtime Pack manifests
* Exchange Shard manifests
* Exchange Federation manifests
* Authority Recognition artifacts
* Validation Decision artifacts
* Revocation artifacts
* multiple `key_id` resolutions
* multiple trust stores
* tenant-scoped and authority-channel-scoped trust roots

A conformant implementation MUST clearly distinguish:

* identity verification;
* signature verification;
* policy acceptance;
* validation status;
* authority recognition;
* certainty level;
* reader visibility.

---

## 13. Interoperability requirements

A Kristal v5 implementation claiming signature conformance MUST:

1. support `ed25519`;
2. support `sha256` content identities;
3. support `kristal.v5:jcs-rfc8785` canonicalization;
4. exclude signatures from hash targets;
5. exclude self-identity fields from their own hash targets;
6. expose per-signature verification status;
7. expose artifact-level verification status;
8. support unsigned artifacts as a distinct status;
9. avoid treating signature verification as universal validation;
10. support offline verification with supplied trust roots.

---

## 14. Security considerations

Implementations SHOULD defend against:

* signature wrapping attacks;
* signature fields embedded outside the top-level `signatures` array;
* hash target ambiguity;
* self-referential identity hashing;
* unsupported algorithm downgrade;
* key substitution;
* stale trust roots;
* revoked keys;
* expired signatures;
* tenant/environment trust confusion;
* authority-channel confusion;
* validation laundering;
* rendering verified signatures as universal truth;
* hiding failed or missing verification status from users or downstream systems.

User interfaces and APIs SHOULD avoid ambiguous labels such as:

```text
trusted
true
canonical
official
safe
```

unless the label is scoped by authority channel, reader policy, validation decision, and certainty level.

Preferred labels include:

```text
signed
identity-verified
signature-verified
recognized by <authority channel>
validated as <status>
reference under <reader policy>
not verified
verification failed
unsigned
```

---

## 15. Open questions

The following profile decisions remain open:

* Should `expires_at` become required for some authority-channel signatures?
* Should `key_id` use a required fingerprint format instead of allowing stable strings?
* Should the transparency log profile be mandatory for public authority recognition?
* Should signatures bind only content identity, or also selected policy metadata?
* Should runtime-pack signatures include additional pack-level integrity surfaces beyond the content identity of the manifest?
* Should validation decisions require separate signatures from both validator and authority channel?
* Should reader policies be signed when distributed in Runtime Packs?
