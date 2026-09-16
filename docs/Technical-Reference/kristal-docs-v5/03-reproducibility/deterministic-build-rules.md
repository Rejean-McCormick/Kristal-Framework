# Deterministic build rules (Kristal v5)

## Status

Normative (v5 core)

## Purpose

This document defines the **deterministic build requirements** for producing Kristal v5 artifacts, specifically:

* **Working Exchange**
* **Reference Exchange**
* **Kristal Runtime Pack**
* **Exchange Shard Manifest**
* **Exchange Federation Manifest**
* derived manifests, indexes, inventories, and content-addressed outputs

The goal is **interoperability and reproducibility**: independent implementations MUST be able to rebuild artifacts with **bit-identical outputs** when given identical inputs, identical compiler versions, and the same recorded policies and parameters.

Kristal v5 separates compilation from validation and authority recognition. A deterministic build may produce a Working Exchange before all assertions are validated or recognized. Validation and recognition decisions are recorded separately and may affect reference status, publication, distribution, activation, reader visibility, or downstream use.

## Scope

These rules apply to:

* compilation stages that produce Working Exchanges, Reference Exchanges, Runtime Packs, shard manifests, and federation manifests;
* all content-addressed IDs associated with these artifacts;
* manifests and files that claim deterministic outputs;
* build-affecting reader policies, validation policies, authority registries, query policies, and runtime-pack policies;
* signatures, hashes, inventories, and artifact references used to verify identity and integrity.

These rules do **not** mandate a specific runtime performance strategy. They mandate that whatever strategy is used must be selected from **portable, enumerated policies** and must be **fully recorded** to enable reproducibility.

These rules do **not** require every compiled artifact to be validated, recognized, or reference-approved. Compilation proves that an artifact was built deterministically from declared inputs. It does not prove that the artifact’s assertions are true, validated, high-certainty, or recognized by any authority channel.

## Definitions

* **Deterministic build:** given the same input snapshot, compiler identity, configuration, policies, and parameters, the compiler produces identical outputs.
* **Reproducible build:** a third party can rerun the compiler using only the recorded manifests, referenced inputs, compiler version, and policy declarations and reproduce the exact outputs.
* **Input snapshot:** the complete set of inputs used for compilation.
* **Structured Epistemic State:** the normative input unit for Kristal v5 compilation. It contains assertions, provenance, evidence references, scope, certainty, status, lineage, and policy references.
* **Claim-IR:** an extractor proposal profile. Claim-IR MAY be part of an input snapshot, but it is not the universal required input format.
* **Working Exchange:** a compiled, content-addressed artifact representing a Structured Epistemic State that may or may not be validated or recognized.
* **Reference Exchange:** a compiled artifact recognized under one or more authority channels for a declared scope.
* **Authority recognition:** a scoped record by which an authority channel recognizes an artifact, shard, assertion, dataset, runtime pack, or another authority channel.
* **Validation decision:** a scoped record describing the validation status of an artifact, shard, assertion, authority channel, dataset, or runtime pack.
* **Reader policy:** a machine-readable policy defining which validation states, authority channels, certainty levels, and epistemic modes are visible to a reader or application.
* **Portable policy:** an allowed, enumerated policy defined in `03-reproducibility/allowed-runtime-pack-policies.md`.
* **Hash target:** the JSON object or declared projection that is canonicalized and hashed to produce a content-addressed ID, after applying required exclusions.

Normative keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.

## Normative requirements

### 1) Determinism declaration

1.1 Any Runtime Pack claiming v5 core conformance MUST declare whether it is deterministic.

1.2 Kristal v5 Runtime Packs claiming v5 core conformance MUST set:

```json
{
  "build": {
    "deterministic": true
  }
}
```

1.3 If an implementation cannot guarantee determinism for a given build, it MUST either:

* refuse to emit a v5 core-conformant pack; or
* emit a pack under a non-core profile that explicitly states non-deterministic behavior.

1.4 Working Exchanges, Reference Exchanges, shard manifests, and federation manifests that claim deterministic identity MUST record enough build-affecting information to reproduce their content-addressed IDs.

1.5 Determinism applies to output bytes and identity material. It does not imply validation, authority recognition, high certainty, publication approval, or reader visibility.

### 2) Canonicalization and hashing dependencies

2.1 Any JSON object or JSON projection used for content-addressed IDs MUST be canonicalized using the declared canonicalization profile.

2.2 v5 core requires:

```text
canonicalization_profile = "kristal.v5:jcs-rfc8785"
canonicalization_version = "1"
```

2.3 These values MUST be recorded by:

* every Working Exchange;
* every Reference Exchange;
* every Runtime Pack Manifest;
* every Exchange Shard Manifest;
* every Exchange Federation Manifest;
* every Authority Registry;
* every Validation Decision when content-addressed;
* every Authority Recognition when content-addressed;
* every Revocations artifact.

2.4 For any content-addressed ID computation, the hashed material MUST:

* exclude the output ID field itself, such as `kristal_id`, `exchange_id`, `runtime_pack_id`, `shard_id`, `federation_id`, `state_id`, `recognition_id`, `validation_decision_id`, or `revocations_id`;
* exclude `signatures` fields wherever they appear;
* exclude equivalent signature, attestation, or proof overlays unless a profile explicitly defines them as part of a separate proof hash;
* follow the relevant hashed-material projection for the artifact type.

2.5 `created_at` MAY reflect build time, but it MUST NOT affect content-addressed IDs unless a profile explicitly includes it in a declared hash target.

2.6 Hash objects MUST use the field name `alg`, not `algo`.

2.7 v5 core hash objects MUST use the following shape:

```json
{
  "alg": "sha256",
  "value": "<64 lowercase hexadecimal characters>"
}
```

2.8 When an artifact declares hashes, signatures, trust roots, compatibility constraints, revocation policy, or authority registry requirements, consumers MUST verify those requirements before treating the artifact as satisfying the corresponding policy.

### 3) Input snapshot is part of determinism

3.1 A deterministic build MUST be parameterized by an explicit input snapshot.

3.2 The input snapshot MAY include:

* Structured Epistemic State artifacts;
* Claim-IR artifacts when extractor workflows are used;
* Resolved Claim-IR artifacts when resolution workflows are used;
* source datasets;
* Wikidata/Wikibase snapshots;
* source documents or evidence blobs;
* validation rulesets;
* validation decisions;
* authority recognition records;
* authority registries;
* revocation lists;
* reader policies;
* subset recipes;
* query profiles;
* runtime-pack policies;
* federation manifests or shard manifests;
* compiler configuration.

3.3 The compiler configuration that affects output bytes MUST be hashed and recorded as `build.config_hash`.

3.4 Any implicit inputs that affect output bytes MUST be eliminated or explicitly recorded. This includes:

* default configuration;
* environment variables;
* locale;
* timezone;
* system time;
* dependency versions;
* compiler feature flags;
* nondeterministic random seeds;
* host-specific filesystem ordering;
* platform-specific path handling.

3.5 If an implementation uses external resources during compilation, the exact resource identity, version, and content hash MUST be recorded.

3.6 A build MUST NOT depend on mutable network state unless that state has been pinned into the input snapshot.

### 4) Ordering determinism

4.1 The compiler MUST NOT rely on non-deterministic iteration order.

4.2 All collections that affect output bytes MUST be processed in a deterministic order defined by an allowed ordering policy.

4.3 If an ordering policy is used, it MUST be recorded under the relevant manifest policy section.

4.4 Stable ordering MUST apply to all build-affecting collections, including:

* assertions;
* provenance records;
* evidence references;
* validation references;
* authority recognition references;
* file inventories;
* shard lists;
* federation composition rules;
* reader policy references;
* manifest references;
* dictionary encodings;
* index rows;
* generated lookup tables;
* membership-filter inputs;
* bitmap inputs.

4.5 Deterministic ordering MUST NOT silently erase disagreement. If two assertions conflict, ordering MAY determine presentation or precedence under a declared policy, but conflict handling MUST remain explicit.

### 5) Portable, enumerated policies

5.1 Build-affecting behaviors MUST be chosen from the allowed policy set defined in:

```text
03-reproducibility/allowed-runtime-pack-policies.md
```

5.2 If a required behavior is not covered by an allowed policy, the implementation MUST either:

* propose a new policy for standardization; or
* emit a non-core profile artifact that does not claim v5 core conformance.

5.3 This requirement exists to prevent builds that are technically reproducible but practically incomparable.

5.4 Policy declarations MUST include enough information to reproduce output bytes.

5.5 Policy declarations MUST distinguish at least:

* compilation policies;
* canonicalization policies;
* data ordering policies;
* query policies;
* reader policies;
* validation policies;
* authority recognition policies;
* runtime-pack policies;
* federation composition policies;
* integrity policies.

### 6) Structured Epistemic State determinism

6.1 A Structured Epistemic State used as a build input MUST be schema-valid under the declared schema version.

6.2 A Structured Epistemic State MUST be content-addressable or have a declared canonical hash target.

6.3 If a Structured Epistemic State contains assertions, their order in the source file MUST NOT affect compiled output unless an explicit ordering policy says otherwise.

6.4 Assertions MUST carry stable identifiers or be deterministically assigned identifiers from declared hash targets.

6.5 Assertion identity derivation MUST exclude fields that are not part of assertion meaning or declared identity, including signatures and output ID fields.

6.6 A Structured Epistemic State MAY include uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions. The compiler MUST preserve their declared status and certainty metadata.

6.7 The compiler MUST NOT convert assertion uncertainty into validation or recognition status.

### 7) Validation and recognition are not universal compile gates

7.1 Compilation MAY produce a Working Exchange from a schema-valid Structured Epistemic State even when validation has not been completed.

7.2 Validation MAY affect:

* assertion status;
* certainty level;
* validation status;
* authority recognition eligibility;
* reference status;
* publication status;
* runtime-pack activation status;
* reader visibility;
* downstream query behavior.

7.3 Validation MUST NOT be treated as a universal compilation blocker.

7.4 Validation MAY block creation of a Reference Exchange if the applicable authority channel or validation policy requires it.

7.5 Validation MAY block publication, distribution, activation, or reader visibility on selected channels.

7.6 Authority recognition MAY be required for reference status, but lack of recognition MUST NOT prevent a Working Exchange from existing unless a local workflow policy explicitly requires that behavior.

7.7 A build manifest MUST distinguish compilation status from validation status, recognition status, publication status, and activation status.

### 8) Working Exchange and Reference Exchange derivation

8.1 A Working Exchange MUST declare:

* `schema_version`;
* `artifact_type`;
* content-addressed ID;
* source state references;
* compiler identity;
* configuration hash;
* canonicalization profile and version;
* build policies;
* scope;
* assertion status and certainty metadata or summaries;
* validation references when present;
* authority recognition references when present.

8.2 A Reference Exchange MUST additionally declare the authority recognition records, validation decisions, policy references, and scope under which reference status is granted.

8.3 Reference status MUST be scoped. A Reference Exchange recognized by one authority channel MUST NOT be treated as recognized by another authority channel unless such recognition is explicitly recorded.

8.4 A Reference Exchange MUST retain traceability to the Working Exchange or Structured Epistemic State from which it was derived.

8.5 Compilers MUST NOT collapse assertion certainty, validation status, and authority recognition into a single boolean field.

8.6 A field such as:

```json
{ "validated": true }
```

MUST NOT be used as the only representation of validation.

8.7 Validation status MUST be qualified by target, authority channel, validation policy, scope, certainty level, and validated-as mode.

### 9) Runtime Pack source status

9.1 A Runtime Pack MUST reference the Exchange or federation source it was compiled from.

9.2 A Runtime Pack MUST declare the source artifact status, such as:

```text
working
reference
deprecated
superseded
revoked
```

9.3 A Runtime Pack derived from a Working Exchange is not equivalent to a Runtime Pack derived from a Reference Exchange.

9.4 A Runtime Pack MUST include enough metadata for consumers to apply reader policies.

9.5 A Runtime Pack MUST NOT present unrecognized or unvalidated assertions as recognized reference material unless the active reader policy explicitly allows that interpretation.

9.6 Runtime Pack tables, indexes, dictionaries, columnar files, search structures, and profile-defined database-like files are derived materializations, not independent authorities.

9.7 For a declared Runtime Pack build identity, every materialization that affects query results MUST be immutable and bound to the declared source artifact, compiler/configuration identity, and applicable materialization policies.

9.8 A conforming materialization MUST be deterministically rebuildable from the declared Kristal source artifact and build inputs. Deleting and rebuilding the materialization MUST NOT change the authoritative epistemic state.

9.9 Runtime Pack payloads MUST NOT be used as writable operational databases whose mutations are expected to flow back into the source Exchange or a product database. Changes originate as new source artifacts/epistemic inputs and produce new artifact/build identities.

9.10 Core v5 does not define a general-purpose writable SQLite profile. A database-like representation is an optional profile extension and MUST remain read-only/derived unless a future normative Kristal contract explicitly defines otherwise.

### 10) Reader policy determinism

10.1 If a Runtime Pack or query surface applies a reader policy during compilation, the reader policy MUST be included in the input snapshot.

10.2 Reader policies that affect output bytes MUST be content-addressed or referenced by content hash.

10.3 Reader policies MAY filter by:

* artifact status;
* assertion status;
* validation status;
* recognition status;
* authority channel;
* certainty level;
* validated-as mode;
* scope;
* domain;
* subdomain;
* jurisdiction;
* time window;
* fictional mode;
* mythological mode;
* disputed status.

10.4 A reader policy MUST NOT silently convert scoped validation into universal truth.

10.5 A “validated-only” reader policy means all visible assertions satisfy the active reader policy. It does not mean all visible assertions are universally true, maximally certain, or accepted by all authorities.

### 11) Federation and sharding determinism

11.1 A shard is a scoped Exchange artifact and MUST have deterministic identity.

11.2 A federation manifest MUST have deterministic identity.

11.3 A federation manifest MUST NOT rewrite shard bytes, shard identities, source hashes, or recognition records.

11.4 A federation manifest MUST declare deterministic composition policy, including:

* shard ordering;
* overlap handling;
* conflict handling;
* authority precedence, if used;
* reader policy defaults, if used;
* optional vs required shard behavior;
* treatment of revoked or deprecated shards.

11.5 Federation MUST preserve disagreement unless the declared composition policy explicitly filters or selects among conflicting assertions.

11.6 If two shards assert incompatible claims, the compiler MUST NOT silently merge them as though they agree.

11.7 If authority precedence is used, the applicable authority registry and recognition policy MUST be included in the input snapshot.

### 12) Parquet determinism

12.1 If Parquet is used, deterministic builds MUST:

* use a portable `data_ordering` policy;
* use a portable `row_grouping` policy;
* record Parquet encoding settings that affect file bytes;
* record compression settings;
* record dictionary encoding settings;
* record statistics settings;
* record bloom-filter settings if enabled.

12.2 The exact Parquet-related settings MUST be recorded under the relevant manifest policy section.

12.3 If bloom filters are enabled, they MUST be treated as profile-bound unless explicitly included in v5 core allowed policies.

12.4 Parquet output MUST be stable across supported toolchains claiming the same conformance profile.

### 13) Membership filters and bitmap determinism

13.1 If a pack includes membership filters, the kind and all parameters that affect bytes MUST be recorded, including as applicable:

* filter type;
* seed or seed derivation rule;
* bits per key;
* false-positive probability target;
* fingerprint size;
* load factor;
* hash function family;
* hash count;
* builder variant identifiers.

13.2 If a pack includes bitmaps, the bitmap format and any optimization steps that affect bytes MUST be recorded, including whether run optimization was applied.

13.3 Implementations MUST ensure membership-filter and bitmap construction is deterministic.

13.4 Random seeds MUST NOT be used unless explicitly recorded or deterministically derived from declared input material.

### 14) File inventory and integrity

14.1 The Runtime Pack Manifest MUST enumerate all files included in the pack under `files[]`, including:

* `path`;
* `role`;
* `sha256`;
* `size_bytes`.

14.2 The set of files and their hashes MUST be sufficient for consumers to verify pack contents and integrity.

14.3 The file inventory MUST be deterministic.

14.4 `files[]` entries MUST have stable deterministic ordering, such as lexical ordering by normalized path.

14.5 Path values MUST be normalized and MUST NOT depend on platform-specific path separators.

14.6 The inventory MUST include all files required for the declared query contract, reader policy behavior, integrity verification, and runtime execution.

### 15) Runtime Pack ID derivation

15.1 The `runtime_pack_id` MUST be derived from a canonical deterministic representation of the pack’s hashed material.

15.2 The hashed material MUST exclude:

* `runtime_pack_id` itself;
* `signatures` fields;
* equivalent signature or attestation overlays;
* non-identity timestamps unless explicitly included by a profile.

15.3 The hashed material MUST include, at minimum, a canonical projection covering:

* referenced source Exchange, federation, or shard identity;
* source artifact status;
* source content hash;
* deterministic build identity inputs;
* compiler identity;
* `build.config_hash`;
* `build.deterministic`;
* declared canonicalization profile and version;
* recorded portable policy selections;
* reader policy references that affect output bytes;
* validation or authority recognition references that affect output bytes;
* file inventory entries;
* query contract reference;
* runtime layout policy.

15.4 Each file inventory entry included in the hash target MUST include:

* `path`;
* `sha256`;
* `size_bytes`;
* `role`.

15.5 The exact hashed-material projection, including field set, ordering, exclusions, and path normalization, MUST be documented and test-vectorized.

### 16) Exchange ID derivation

16.1 Exchange IDs MUST be derived from a canonical deterministic representation of the Exchange hashed material.

16.2 Exchange hashed material MUST exclude:

* the output ID field itself;
* signatures;
* equivalent attestation overlays;
* non-identity timestamps unless explicitly included by a profile.

16.3 Working Exchange hashed material MUST include the declared source state references, scope, compilation policy, compiler identity, config hash, and compiled payload.

16.4 Reference Exchange hashed material MUST include the recognition and validation references that are part of its reference status.

16.5 A Reference Exchange with different authority recognition records MUST have a different content-addressed identity unless the recognition records are deliberately stored outside the hashed material by a declared profile.

### 17) Time, randomness, and environment constraints

17.1 The build MUST NOT incorporate non-deterministic sources into bytes that are hashed or part of deterministic outputs.

17.2 Non-deterministic sources include:

* system time;
* nondeterministic PRNG;
* thread scheduling;
* filesystem enumeration order;
* locale defaults;
* timezone defaults;
* host-specific path handling;
* unpinned dependency behavior;
* network response timing;
* mutable external resources.

17.3 `created_at` MAY reflect build time but MUST NOT affect content-addressed IDs unless a profile explicitly includes it.

17.4 If parallel compilation is used, the output MUST be equivalent to a deterministic serial order.

17.5 Any randomness required for a data structure MUST be replaced by deterministic seed derivation or explicitly recorded seed values.

### 18) Build record requirements

18.1 A v5 build record SHOULD distinguish at least:

* `compile_status`;
* `validation_status`;
* `review_status`;
* `recognition_status`;
* `publication_status`;
* `activation_status`;
* `working_outputs`;
* `reference_outputs`;
* `runtime_pack_outputs`;
* `reason_codes`.

18.2 `compile_status` MUST NOT be overloaded to mean validation status.

18.3 `validation_status` MUST NOT be overloaded to mean authority recognition.

18.4 `recognition_status` MUST NOT be treated as global unless the recognition scope explicitly says so.

18.5 Build records belong to operational metadata. They MAY be referenced by Kristal artifacts but SHOULD remain distinct from the epistemic content itself.

### 19) Signatures and verification

19.1 Signatures MUST be excluded from the primary content-addressed hash target unless a profile defines a separate proof hash.

19.2 Signature objects SHOULD use the minimal v5 shape:

```json
{
  "key_id": "string",
  "alg": "ed25519",
  "signature": "string",
  "created_at": "RFC3339"
}
```

19.3 Consumers MUST verify signatures required by the applicable artifact, authority registry, runtime policy, reader policy, or activation policy before treating the artifact as satisfying that policy.

19.4 Signature verification failure affects the policy that depends on that signature. It does not imply that the artifact bytes cannot exist or be inspected.

19.5 Revoked keys MUST NOT be accepted for policies whose scope and effective time are covered by the revocation.

### 20) Reproducibility acceptance criteria

20.1 A v5 core-conformant build MUST pass the acceptance tests defined in:

```text
03-reproducibility/reproducibility-acceptance-tests.md
```

20.2 At minimum, acceptance testing MUST verify:

* identical inputs and policies produce identical output bytes;
* identical inputs and policies produce identical content-addressed IDs;
* independent implementations produce stable IDs;
* file inventories are stable;
* hashed-material exclusions are applied consistently;
* signatures are excluded from primary hash targets;
* output ID fields are excluded from their own hash targets;
* `created_at` does not affect content-addressed IDs unless explicitly profile-bound;
* reader-policy-filtered outputs are reproducible;
* federation composition is deterministic;
* disagreement is preserved or handled according to declared policy;
* runtime-pack query outputs are stable under the declared query contract.

20.3 Acceptance tests SHOULD include examples for:

* Working Exchange compilation;
* Reference Exchange derivation;
* Structured Epistemic State compilation;
* authority recognition;
* validation decisions;
* reader policy filtering;
* Runtime Pack generation;
* shard compilation;
* federation composition;
* revoked keys;
* revoked targets.

## Non-normative notes

* Keeping the policy surface area small is intentional. It encourages comparable builds and reduces ecosystem fragmentation.
* Advanced optimizations, such as Parquet bloom filters, should typically be gated behind explicit profiles unless they are proven portable and deterministic across toolchains.
* Operational resilience patterns such as circuit breakers, DLQs, blue/green deployment, canary releases, retries, structured logs, and correlation IDs are described in `08-ops/` and are not part of artifact conformance unless explicitly referenced by a profile.
* A deterministic build can faithfully reproduce a bad, disputed, fictional, mythological, low-certainty, or rejected assertion. Determinism only means the artifact was built reproducibly.
* Validation, certainty, authority recognition, and reader policy determine how the resulting artifact should be interpreted.
