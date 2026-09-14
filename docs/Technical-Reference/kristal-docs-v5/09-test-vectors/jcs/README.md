# JCS Test Vectors (Kristal v5)

## Status

Draft (normative test-vector guidance)

## Purpose

This folder contains golden test vectors for Kristal v5 canonicalization and content-addressed identity rules.

Kristal v5 requires that:

* `canonical_json` uses RFC 8785 JSON Canonicalization Scheme (JCS);
* content-addressed IDs are computed from canonicalized JSON bytes;
* signatures are excluded from content-addressed identity;
* tenant-local metadata, access-control metadata, workflow state, distribution state, and runtime activation state are excluded from global content identity;
* validation status, certainty metadata, authority recognition references, and reader-policy metadata are included or excluded according to the artifact’s declared content boundary.

For an artifact whose global identity is content-derived, the default rule is:

```text id="8e3zfh"
sha256(JCS(json_object_without_signatures_and_non_content_control_metadata))
```

These vectors ensure that independent implementations in different languages compute identical canonical bytes and identical hashes for the same declared artifact boundary.

## Files in this folder

* `vectors.json`
  A collection of JCS input cases and expected canonical outputs.

* `expected-hashes.txt`
  Expected SHA-256 hashes for each vector’s canonical output.

## Vector format

Each entry in `vectors.json` SHOULD use the following shape:

```json id="nmg708"
{
  "id": "jcs-0001",
  "description": "Brief description of the case",
  "profile": "kristal.v5:jcs-rfc8785",
  "artifact_type": "generic_json",
  "content_boundary": {
    "exclude_json_pointers": []
  },
  "input": {
    "...": "original JSON object"
  },
  "expected_canonical": "{\"a\":1,\"b\":2}",
  "expected_sha256_hex": "..."
}
```

Notes:

* `profile` SHOULD be `kristal.v5:jcs-rfc8785`.
* `expected_canonical` MUST be the exact UTF-8 string output of JCS.
* `expected_sha256_hex` MUST be the SHA-256 digest of `expected_canonical` bytes, represented as lower-case hexadecimal.
* `content_boundary.exclude_json_pointers` SHOULD declare excluded JSON Pointers, such as signatures or tenant-local control metadata.
* Vectors MUST embed `expected_sha256_hex` and `expected-hashes.txt` MUST repeat the same digest keyed by stable vector `id`.

## Required coverage

The normative release vector set MUST include cases covering the following areas. The release validator checks the committed vectors with the ECMAScript reference serialization used by RFC 8785.

### 1. Object key ordering

The vector set MUST include:

* keys out of order in input;
* nested objects;
* repeated ordering checks across different object depths;
* objects containing arrays and nested objects.

### 2. Arrays

The vector set MUST include:

* arrays preserving order;
* nested arrays;
* arrays containing objects;
* arrays containing mixed JSON scalar values.

### 3. Numbers

The vector set MUST include:

* integers;
* floating-point values;
* negative values;
* zero;
* exponent notation;
* values that must not be represented in a non-canonical form.

Implementations MUST NOT apply language-specific or platform-specific numeric formatting beyond RFC 8785 requirements.

### 4. Strings and escaping

The vector set MUST include:

* quotes;
* backslashes;
* unicode characters;
* unicode escape equivalence;
* control characters;
* strings containing visually similar but byte-distinct characters where relevant.

### 5. Booleans and null

The vector set MUST include:

* `true`;
* `false`;
* `null`.

### 6. Signature exclusion fixture

The vector set MUST include at least one fixture where:

* the input contains a signature envelope section or mock signature fields;
* the canonicalization/hash input explicitly excludes those fields;
* the expected canonical output corresponds to the object after signature exclusion.

This ensures implementations match Kristal’s rule:

```text id="9xhncg"
remove signatures -> canonicalize -> hash
```

The following field names SHOULD be treated as signature fields when the artifact profile declares them outside the content boundary:

* `signatures`
* `signature`
* `proof`
* `proofs`
* `jws`
* `detached_signatures`

The exact excluded fields MUST be declared by the artifact profile or vector metadata.

### 7. Tenant metadata exclusion fixture

The vector set MUST include at least one fixture where:

* the input contains tenant-local metadata;
* the global content identity excludes that tenant-local metadata;
* two inputs with identical content and different tenant metadata produce the same canonical output and hash.

Examples of tenant-local metadata include:

* `tenant_id`
* `tenant_artifact_handle`
* `acl`
* `access_control`
* `workflow_state`
* `approval_state`
* `distribution_status`
* `activation_status`
* `cache_state`
* `reader_session`

These fields MUST NOT influence global content IDs unless a specific derived artifact profile explicitly declares them inside its content boundary.

### 8. Validation and certainty boundary fixture

The vector set MUST include at least one fixture demonstrating whether validation and certainty metadata are inside or outside the content boundary for a given artifact type.

For Kristal v5:

* validation references may be part of an Exchange content boundary when the Exchange declares them as content;
* authority recognition references may be part of an Exchange content boundary when the Exchange declares them as content;
* reader-policy selections are usually control-plane or view-plane metadata unless a derived reader-policy artifact declares them as content;
* workflow state is not part of the global Exchange content boundary.

The vector metadata MUST make the boundary explicit.

### 9. Derived view fixture

The vector set SHOULD include a fixture for a derived reader-policy view where the view itself has a declared content boundary.

Example:

* source Exchange remains unchanged;
* reader-policy-filtered output is represented as a derived artifact;
* the derived artifact receives its own hash based on its declared content boundary.

This prevents implementations from accidentally reusing the source Exchange identity for a filtered or transformed view.

## How to use these vectors

### Step 1: Determine the content boundary

For each vector:

1. Read the vector metadata.
2. Determine which fields are inside the declared content boundary.
3. Remove excluded fields before canonicalization.
4. Do not remove fields that are explicitly part of the declared artifact content.

### Step 2: Canonicalization

For each vector:

1. Parse `input` into an in-memory JSON object.
2. Apply the declared content-boundary exclusions.
3. Serialize the resulting object using RFC 8785 JCS.
4. Compare the resulting UTF-8 bytes to `expected_canonical`.

### Step 3: Hashing

For each vector:

1. Compute SHA-256 over the canonical bytes.
2. Compare the result to `expected_sha256_hex` or to the corresponding line in `expected-hashes.txt`.

Any mismatch indicates that:

* the implementation is not RFC 8785 compliant;
* the implementation is applying additional transformations;
* excluded fields were not removed correctly;
* required content fields were incorrectly removed;
* the declared content boundary was misapplied;
* the vector’s expected value is incorrect and must be corrected through the test-vector update process.

## Conformance requirement

A Kristal v5 core implementation MUST:

* ship or reference a JCS vector set;
* pass the required JCS canonicalization vectors in CI;
* pass the required signature-exclusion vectors in CI;
* pass the required tenant-metadata exclusion vectors in CI;
* apply declared content boundaries consistently;
* compute SHA-256 over the exact canonical UTF-8 bytes.

If an implementation claims Kristal v5 core conformance but fails these vectors, its content-addressed IDs are not interoperable.

## Updating the vectors

### Versioning

If vectors change materially:

* increment the vector set version;
* preserve old vectors where possible;
* add a changelog entry outside the normative test data;
* avoid changing expected output for existing vector IDs unless correcting a documented vector error.

`vectors.json` SHOULD include root-level metadata similar to:

```json id="9etgcs"
{
  "vector_set_id": "kristal.v5:jcs-test-vectors",
  "vector_set_version": "5.0.0",
  "canonicalization_profile": "kristal.v5:jcs-rfc8785",
  "hash_alg": "sha256",
  "vectors": []
}
```

### Adding new vectors

Prefer adding new IDs rather than modifying existing ones.

Recommended ID format:

```text id="21der8"
jcs-v5-0001
jcs-v5-0002
jcs-v5-0003
```

Vector IDs MUST remain stable after publication.

## Suggested commands

The exact runner is language-specific, but a test runner should perform the equivalent of:

```text id="kb0efn"
load vectors.json
for each vector:
  boundary_input = apply_content_boundary(input, content_boundary)
  canonical = JCS(boundary_input)
  hash = sha256(canonical)
  assert canonical == expected_canonical
  assert hash == expected_sha256_hex
```

For vectors stored with `expected-hashes.txt`, the runner must also verify that each vector ID maps unambiguously to its expected hash.

## Interaction with Kristal v5 artifacts

### Exchange

Exchange identity uses the content boundary declared by the Exchange schema and profile.

Signatures MUST be excluded.

Tenant-local metadata MUST be excluded.

Validation references, certainty summaries, and authority recognition references are included only when declared as part of the Exchange content boundary.

### Runtime Pack

Runtime Pack identity uses the content boundary declared by the Runtime Pack manifest.

Runtime Pack signatures MUST be excluded from Runtime Pack content hashes.

Tenant-local cache state, installation state, activation state, and distribution state MUST be excluded unless explicitly declared in a separate tenant-scoped packaging profile.

### Authority Recognition

Authority recognition artifacts may be content-addressed.

Their signatures MUST be excluded from the recognition content hash.

The recognition decision itself, issuer authority channel, target reference, scope, recognized status, reason codes, and evidence references SHOULD be included in the content boundary.

### Validation Decision

Validation decision artifacts may be content-addressed.

Their signatures MUST be excluded from the validation decision content hash.

The validation status, validated-as status, certainty level, authority channel, target reference, findings, reason codes, and evidence references SHOULD be included in the content boundary.

### Reader Policy

Reader policy artifacts may be content-addressed when represented as portable artifacts.

If content-addressed, their selected authority channels, allowed statuses, certainty levels, included scopes, and fallback behavior SHOULD be included in the content boundary.

A reader session, UI state, user identity, or tenant-local access grant MUST NOT be included in the global reader-policy artifact hash.

## Non-goals

These vectors do not validate:

* epistemic truth;
* authority recognition;
* assertion correctness;
* certainty level accuracy;
* reader-policy appropriateness;
* RDF canonicalization;
* Runtime Pack query behavior.

They only verify JSON canonicalization, declared field exclusion, and SHA-256 hashing over the declared content boundary.

## Summary

The JCS test vectors ensure that Kristal v5 implementations compute the same canonical JSON bytes and the same content-addressed IDs for the same declared artifact boundary.

The core rule is:

```text id="kmure7"
declare content boundary
remove excluded fields
canonicalize using RFC 8785 JCS
hash canonical UTF-8 bytes with SHA-256
```

This preserves deterministic identity while allowing Kristal v5 to separate artifact content from signatures, tenant-local metadata, workflow state, distribution state, activation state, and reader-session state.
