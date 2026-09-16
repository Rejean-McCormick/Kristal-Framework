# 01-core-spec/ids-canonicalization-hashing.md

## Status

Draft (v5)

## Purpose

This document specifies the **normative** rules for:

* `canonical_json` — how Kristal objects are canonicalized
* `content_hash` — how stable digest material is recorded
* `kristal_id` — how Exchange-level content-addressed IDs are computed
* `state_id` — how Structured Epistemic State IDs are computed
* `assertion_id` — how assertion-level IDs are computed
* manifest IDs — how sidecar manifests are content-addressed
* optional `rdf_hash` — RDF-level hash for deterministic RDF exports

Kristal v5 requires that two independent implementations produce identical IDs for identical hash targets under the same canonicalization profile.

Canonicalization and hashing protect artifact identity, reproducibility, and integrity. They do not decide truth, certainty, recognition, or authority.

---

## 0. Scope note: payloads vs manifests (normative)

This document defines ID computation for Kristal v5 content-addressed objects, including:

* Structured Epistemic States
* Exchange payloads
* assertions
* shard manifests
* federation manifests
* runtime pack manifests
* authority registries
* validation decisions
* authority recognition records
* revocation records
* reader policies, where content-addressed

The **Exchange payload** is the structured Kristal artifact used for reference, federation, querying, and runtime packaging.

**Manifests** are sidecar or package-level objects that record build inputs, parameters, profiles, dependency references, integrity material, timestamps, publication status, runtime packaging details, or operational metadata.

A manifest MAY have its own content-addressed ID, but it is **not part of the Exchange payload hash target** unless a profile explicitly says otherwise.

**Core conformance implication:**

* Wall-clock timestamps and volatile compilation telemetry MUST NOT appear inside the Exchange payload hashed region unless they are intended to be part of the stable content identity.
* Operational timestamps, logs, environment telemetry, and build-run metadata SHOULD be recorded in sidecar manifests or operational logs.
* Validation, recognition, certainty, and reader-policy metadata MAY be part of a payload hash target when they are part of the stable artifact content. They MUST NOT be silently excluded.

---

## 1. Terminology

* **Kristal object**: any JSON object governed by this specification and intended to be canonicalized, hashed, signed, referenced, or distributed.
* **Structured Epistemic State**: the normative v5 input unit for structured claims, sources, provenance, certainty, review, and validation metadata.
* **Exchange payload**: a Kristal Exchange JSON object containing structured content, references, validation metadata, recognition metadata, queryable material, and artifact identity fields.
* **Reference Exchange**: an Exchange payload recognized under one or more authority channels for a declared scope.
* **Working Exchange**: an Exchange payload that is materialized and usable but not necessarily recognized as a reference by any authority channel.
* **Exchange Manifest**: a sidecar manifest that records reproducibility, build, integrity, policy, and dependency declarations for an Exchange.
* **Runtime Pack Manifest**: the sidecar manifest for a compiled offline Runtime Pack.
* **canonical_json**: the canonical byte representation of an object after applying this specification’s canonicalization rules.
* **Hash target**: the exact JSON object that is canonicalized and hashed to produce an ID or digest.
* **JCS**: JSON Canonicalization Scheme, RFC 8785, used as the mandatory canonicalization method for the v5 core profile.
* **content_hash**: a recorded digest object identifying the hash algorithm and digest value.
* **signature**: a cryptographic signature over a canonicalized hash target or digest according to the signing profile.
* **attestation**: a signed or recorded claim about validation, recognition, publication, review, runtime packaging, or operational status.

Normative keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.

---

## 2. Normative `canonical_json` profile

### 2.1 Canonicalization method

`canonical_json` MUST be produced using **RFC 8785 JSON Canonicalization Scheme (JCS)** under the v5 core profile.

### 2.2 Canonicalization profile recording

Every content-addressed Kristal object MUST record:

* `schema_version`
* `canonicalization_profile`
* `canonicalization_version`

The default v5 core values are:

```json
{
  "schema_version": "5.0",
  "canonicalization_profile": "kristal.v5:jcs-rfc8785",
  "canonicalization_version": "1"
}
```

Implementations MAY introduce additional canonicalization profiles, but they MUST make them explicit.

An implementation MUST NOT claim v5 core conformance for an object whose canonicalization profile is missing, ambiguous, or incompatible with this document.

### 2.3 Canonicalization boundaries

Canonicalization applies to the selected hash target object.

It does not imply that every adjacent file, manifest, signature, runtime package, or operational log is part of the same hash target.

Where multiple objects are bundled together, each content-addressed object MUST declare or inherit the hash target rules that apply to it.

---

## 3. Hash algorithms and digest representation

### 3.1 Mandatory hash algorithm

The mandatory v5 core hash algorithm is:

```text
sha256
```

### 3.2 Digest encoding

SHA-256 digests MUST be encoded as lowercase hexadecimal.

A content-addressed identifier MUST use the form:

```text
sha256:<lowercase-hex>
```

### 3.3 `content_hash` object shape

When a digest is stored as a field rather than as the object ID itself, it MUST use:

```json
{
  "alg": "sha256",
  "value": "<lowercase-hex>"
}
```

The key name MUST be `alg`, not `algo`.

### 3.4 Hash stability

A hash target MUST contain only the fields intended to define the stable identity of the object.

Volatile fields such as compilation wall-clock time, local filesystem path, machine hostname, CI job ID, or transient runtime telemetry MUST NOT be included in a hash target unless a profile explicitly defines them as stable identity material.

---

## 4. General hash target selection

### 4.1 Mandatory exclusions

To compute an ID for a Kristal object, implementations MUST derive a hash target object by removing:

1. the output ID field being computed;
2. `content_hash`, when it stores the digest being computed;
3. top-level `signatures`, when present;
4. top-level `attestations`, when present;
5. any nested field whose key is exactly `signatures` or `attestations`, for defensive compatibility.

The output ID field depends on the object type. Examples include:

```text
kristal_id
state_id
assertion_id
shard_id
federation_id
runtime_pack_id
validation_decision_id
recognition_id
registry_id
revocation_id
reader_policy_id
```

### 4.2 Signature placement rule

Signatures MUST be carried in a top-level `signatures` array when present.

Attestations SHOULD be carried in a top-level `attestations` array when the object embeds attestations directly.

Profiles MAY store attestations as separate signed records referenced by ID. That form is preferred when attestations may change independently of the object being attested.

### 4.3 No implicit exclusions

Except for the exclusions in Section 4.1, implementations MUST NOT silently exclude additional fields from the hash target.

If a profile needs a different stable-content boundary, that boundary MUST be declared through an explicit profile identifier and version.

### 4.4 Hash target determinism

For a given object, canonicalization profile, canonicalization version, and hash target rule, implementations MUST derive the same hash target.

If two implementations disagree about the hash target, the object is not portable under this specification until the disagreement is resolved by profile clarification or conformance correction.

---

## 5. `kristal_id` computation

### 5.1 Definition

An Exchange payload uses content-addressing:

```text
kristal_id = "sha256:" + hex(SHA-256(JCS(hash_target(E))))
```

Where:

* `E` is the Exchange payload JSON object;
* `hash_target(E)` is derived using Section 4;
* `JCS(...)` is RFC 8785 canonicalization;
* `hex(...)` is lowercase hexadecimal encoding.

### 5.2 Algorithm

Given an Exchange JSON object `E`:

1. Produce `T = hash_target(E)` by applying Section 4.
2. Serialize `T` to bytes `B = JCS(T)`.
3. Compute `H = SHA-256(B)`.
4. Encode `H` as lowercase hex.
5. Set:

```text
kristal_id = "sha256:" + hex(H)
```

### 5.3 Acceptance criteria

Two independent implementations MUST produce identical `kristal_id` values for the same Exchange payload under the same:

* `schema_version`
* `canonicalization_profile`
* `canonicalization_version`
* hash target rule

### 5.4 Exchange status is part of identity when present

If `artifact_status`, `validation_refs`, `authority_recognition_refs`, `certainty_summary`, `reader_policy_refs`, or equivalent status fields are present inside the Exchange payload, they are part of the hash target unless a profile explicitly excludes them.

This means that a Working Exchange and a Reference Exchange MAY have different `kristal_id` values even when they share the same underlying assertions.

That difference is intentional when recognition, validation, or status metadata is part of the artifact’s stable identity.

### 5.5 Core Exchange identity boundary

The v5 core Exchange identity profile is:

```text
kristal.v5:exchange-id-core@1
```

`kristal_id` identifies the **stable Exchange payload**. It does not identify the compiler process or the Exchange Manifest as a whole.

An `exchange-manifest.schema.json` object may record `created_at`, `manifest_id`, `build`, `inputs`, human-facing references, signatures, and other reproducibility or package metadata around the Exchange. Those manifest/build fields MUST NOT be added to the Exchange payload hash target merely because they coexist in the same package or implementation envelope.

In particular, the following are build/provenance metadata rather than Exchange payload identity material unless a future explicit identity profile says otherwise:

* compiler name, version, source revision, or host platform;
* build correlation IDs;
* wall-clock timestamps;
* `build.config_hash`;
* CI/job/host telemetry;
* manifest-only integrity or publication metadata.

A compiler MUST record build-affecting metadata needed for reproducibility in the Exchange Manifest/build record, while keeping `kristal_id` a content identity for the stable Exchange payload. Therefore two independent conforming compilers that emit the same stable Exchange payload MUST compute the same `kristal_id` even when compiler identities or build-run metadata differ.

The framework TCK Exchange vectors are **payload/hash-target fixtures**, not complete `exchange-manifest.schema.json` instances. Full compiler/verifier conformance remains a separate claim until a concrete implementation adapter is exercised.

---

## 6. `state_id` computation

### 6.1 Purpose

A `state_id` identifies a Structured Epistemic State.

Structured Epistemic States are used to represent claims, hypotheses, evidence, provenance, certainty, scope, and review or validation references before or outside Exchange packaging.

### 6.2 Definition

```text
state_id = "sha256:" + hex(SHA-256(JCS(hash_target(S))))
```

Where `S` is the Structured Epistemic State object.

### 6.3 Hash target

The `state_id` hash target MUST exclude:

* `state_id`
* `content_hash`, when it stores the digest being computed
* `signatures`
* `attestations`

It MUST NOT exclude assertions, provenance, evidence, certainty, validation, scope, lineage, or policy references unless a profile explicitly defines a different state identity boundary.

### 6.4 Acceptance criteria

Two Structured Epistemic States with identical stable content MUST produce the same `state_id`.

If a certainty level, assertion status, validation reference, recognition reference, scope, or provenance entry changes, the `state_id` SHOULD change unless the profile explicitly stores that change outside the state hash target.

---

## 7. `assertion_id` computation

### 7.1 Purpose

A stable `assertion_id` enables:

* deduplication
* merge operations
* provenance tracking
* validation decisions at assertion level
* authority recognition at assertion level
* dispute preservation across federation
* query filtering by assertion status, certainty, scope, and authority channel

### 7.2 Definition

If `assertion_id` is present, the producer MUST compute it deterministically from an assertion hash target.

```text
assertion_id = "sha256:" + hex(SHA-256(JCS(hash_target(A))))
```

Where `A` is the assertion object or normalized assertion target.

### 7.3 Minimum assertion hash target

The assertion hash target SHOULD include, when applicable:

* normalized subject
* normalized predicate or property
* normalized value
* assertion scope
* qualifiers
* references or evidence pointers
* provenance pointers
* assertion status
* certainty level
* `validated_as`, when present
* authority recognition references, when present and intended to be part of assertion identity
* validation decision references, when present and intended to be part of assertion identity

Profiles MAY define a narrower assertion identity if they need to distinguish the claim core from review, validation, certainty, or recognition metadata.

If a profile uses a narrower identity, it MUST define separate IDs or references for status-bearing assertion versions.

### 7.4 Wikidata-compatible statement material

For Wikidata-compatible statements, the assertion hash target SHOULD preserve the relevant statement structure, including:

* entity ID or subject reference
* property ID or predicate
* value
* qualifiers
* references
* rank, when present
* statement-level metadata needed to preserve source meaning

A Kristal profile MAY expose a Wikidata-compatible `statement_id` as an alias or source identifier, but `assertion_id` is the v5 normative field for Kristal assertion identity.

### 7.5 Ordering rules

Where assertion substructures are semantically sets, implementations MUST sort deterministically before hashing.

Recommended ordering:

1. primary sort key: predicate/property identifier ascending lexicographically;
2. secondary sort key: canonicalized value representation, compared lexicographically over `canonical_json` bytes;
3. tertiary sort key: canonicalized representation of the full substructure.

This applies to qualifiers, references, evidence pointers, provenance references, and equivalent set-like structures.

---

## 8. Manifest ID computation

### 8.1 Scope

Manifests MAY be content-addressed independently from the payloads or packages they describe.

This applies to:

* Exchange Manifest
* Runtime Pack Manifest
* Exchange Shard Manifest
* Exchange Federation Manifest
* Authority Registry
* Validation Decision
* Authority Recognition
* Revocation Record
* Reader Policy
* Transparency Log Entry

### 8.2 Definition

A manifest ID MUST be computed using the same core rule:

```text
<object_id> = "sha256:" + hex(SHA-256(JCS(hash_target(M))))
```

Where `M` is the manifest or record object.

### 8.3 Manifest hash target

The manifest hash target MUST exclude:

* the output ID field being computed;
* `content_hash`, when it stores the digest being computed;
* `signatures`;
* `attestations`.

The manifest hash target MUST include declared stable manifest content, including dependency references, policy references, source artifact references, scope, profile identifiers, and integrity declarations.

Operationally volatile fields SHOULD be placed outside the manifest hash target or in a separate operational log.

### 8.4 Manifests do not mutate referenced artifacts

A manifest that references an Exchange, Runtime Pack, shard, or authority record MUST NOT change the identity of that referenced object.

If a manifest records new validation, recognition, publication, or runtime information, that information belongs to the manifest or related signed record unless the artifact itself is intentionally reissued with new status-bearing content.

---

## 9. Optional RDF-level hashing: `rdf_hash`

Kristal v5 supports optional RDF integrity mode for RDF exports.

When enabled, `rdf_hash` is computed using **RDF Dataset Canonicalization (RDFC-1.0)** from canonical N-Quads.

This mode is optional and enabled only under an explicit profile, such as:

```text
05-profiles/profile-rdf-integrity-rdfc.md
```

When enabled, implementations SHOULD use conformance tests for RDFC behavior and SHOULD define resource limits for canonicalization.

The RDF hash does not replace `kristal_id` unless a profile explicitly defines that behavior.

---

## 10. Optional human-verifiable ID representations

Profiles MAY define human-verifiable or URI-compatible representations of:

* `kristal_id`
* `state_id`
* `assertion_id`
* `content_hash`
* `rdf_hash`

Examples may include ni-URI-style or Trusty URI-style representations.

Such representations MUST be derived from the normative digest and MUST NOT change the underlying content-addressed ID.

---

## 11. Signing workflow dependency

The signing and verification workflow is:

```text
remove signatures
-> derive hash target
-> canonicalize
-> hash or verify digest
-> sign or verify signature
```

Declared hashes and signatures are verified according to:

```text
01-core-spec/signatures-trust.md
```

This file defines the ID, hash target, and canonicalization prerequisites that signing depends on.

Failure to verify a declared hash or signature is an integrity result. It does not, by itself, decide assertion certainty, authority recognition, reader visibility, or truth status.

---

## 12. Conformance requirements

A v5 conforming implementation MUST:

1. support RFC 8785 JCS for `canonical_json`;
2. record `schema_version = "5.0"` on v5 objects;
3. record `canonicalization_profile = "kristal.v5:jcs-rfc8785"` under the v5 core profile;
4. record `canonicalization_version = "1"` under the v5 core profile;
5. compute SHA-256 digests as lowercase hexadecimal;
6. use `sha256:<hex>` for content-addressed IDs;
7. exclude the output ID field from its own hash target;
8. exclude `signatures` and `attestations` from hash targets;
9. exclude `content_hash` when it stores the digest being computed;
10. avoid volatile operational telemetry in stable hash targets unless explicitly profiled;
11. preserve deterministic ordering for set-like substructures before hashing;
12. distinguish artifact identity from validation, recognition, certainty, and reader policy.

A v5 conforming implementation MUST NOT:

1. silently exclude undeclared fields from a hash target;
2. use `algo` instead of `alg`;
3. include signatures in the bytes being signed unless an explicit signature profile requires it;
4. treat `kristal_id` as proof of truth;
5. treat hash verification as authority recognition;
6. treat a Runtime Pack hash as replacing the identity of its source Exchange;
7. claim v5 core conformance under an unspecified canonicalization profile.

---

## 13. Non-goals

This document does not define:

* which claims are true;
* which authority channels are recognized;
* which certainty levels are acceptable for a reader;
* which validation policies are authoritative;
* which artifacts should be visible by default;
* how Orgo workflows approve or reject submissions;
* how Konnaxion chooses runtime activation policies;
* how Architect renders user-facing labels;
* how SenTient resolves ambiguous source material.

Those concerns are defined by separate Kristal v5 documents and ecosystem contracts.

This document defines only the stable identity, canonicalization, and hashing rules that those layers depend on.
