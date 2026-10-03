# Profile: RDF Integrity (RDFC) (Kristal v5)

## Status

Draft

## Purpose

Provide an optional, standardized integrity mechanism for Kristal v5 RDF exports by computing a deterministic `rdf_hash` over a declared RDF projection using an RDF Dataset Canonicalization method and CI conformance gating.

This profile is designed for deployments that need **semantic-web grade export integrity**. Independent verifiers can confirm that exported RDF content matches the declared hash, while Kristal v5 keeps its normative core focused on portable epistemic artifacts, structured references, provenance, authority recognition, validation status, certainty metadata, and query semantics.

This profile does not decide whether an assertion is true, validated, recognized, disputed, fictional, mythological, or high-certainty. It only verifies that a declared RDF export projection is byte-stable after RDF dataset canonicalization and that its declared hash matches the exported RDF content.

## Scope

In scope:

* Canonicalization and hashing of RDF datasets for selected export projections
* CI conformance gating using an RDFC test suite subset or declared equivalent
* Explicit coverage declaration for hashed RDF projections
* Resource limits for RDF canonicalization and hashing
* Structured reporting when integrity production or verification cannot be completed
* Export-level integrity verification independent of Kristal core JSON identity

Out of scope:

* Kristal core JSON canonicalization and `kristal_id`, which are handled by the Kristal v5 core using JCS-based canonicalization
* Runtime Pack hashing, which is handled by Runtime Pack manifests
* Authority recognition, validation decisions, certainty levels, or reader-policy filtering
* Any requirement that this profile is enabled by default
* Any claim that RDF export integrity implies epistemic validation

## Dependencies

This profile depends on at least one deterministic RDF export profile, typically:

* `profile-rdf-wdqs-export` using a declared projection such as `full` or `truthy`

The export MUST be deterministic and byte-stable according to its export profile before this integrity profile is applied.

If the underlying RDF export profile is non-deterministic, incomplete, underspecified, or projection-ambiguous, this RDF integrity profile MUST report that it cannot produce or verify a reliable `rdf_hash` for that projection.

## Normative keywords

MUST, SHOULD, and MAY are used as in RFC 2119.

## Profile activation

An implementation enables this profile by declaring, in its export manifest:

* `profile.id = "rdf-integrity-rdfc"`
* `profile.version = "5.0"`
* `rdfc.algorithm = "RDFC-1.0"` or a later explicitly supported algorithm
* `rdf_hash.alg = "sha256"`
* `rdf_hash.coverage` with explicitly enumerated projections covered by the hash

Profile activation means only that RDF export integrity is being computed or verified for the declared projection(s). It does not mean that the exported assertions are validated, recognized, high-certainty, or visible under any particular reader policy.

## Covered projections

When enabled, the implementation MUST declare exactly which RDF projection or projections are hash-covered.

At minimum, the manifest MUST include:

* `coverage.projection`: `"full"`, `"truthy"`, or another declared export projection
* `coverage.export_profile_id`: for example, `"rdf-wdqs"`
* `coverage.graphs`: which named graphs are included in the hash
* `coverage.exclusions`: which graphs, triples, metadata fields, timestamps, signatures, or generated artifacts are excluded
* `coverage.scope`: the Kristal scope covered by the export, when applicable
* `coverage.source_artifact_ref`: the Exchange, shard, dataset, or export artifact from which the RDF projection was produced

Coverage MUST be explicit enough that an independent verifier can reconstruct the same RDF dataset boundary.

## Projection equivalence rules

Differences between projections, such as `full` versus `truthy`, MUST NOT be treated as integrity failures unless the export profile explicitly requires projection equivalence.

Each projection’s `rdf_hash` is independently meaningful.

For example:

* a `full` projection hash verifies the declared full RDF projection;
* a `truthy` projection hash verifies the declared truthy RDF projection;
* a mismatch between `full` and `truthy` is not an integrity problem unless a profile incorrectly declared them equivalent.

## Canonicalization method

The canonicalization algorithm MUST be an RDF Dataset Canonicalization method compatible with RDFC-1.0 style conformance, such as a method producing canonical N-Quads output.

Requirements:

* The input MUST be an RDF dataset.
* A single RDF graph MUST be represented as a dataset before canonicalization.
* The canonicalization method MUST produce a deterministic canonical byte stream.
* Blank nodes MUST be deterministically canonicalized, or deterministically skolemized before canonicalization if the selected algorithm and export profile explicitly allow and document that behavior.
* The selected canonicalization method and version MUST be recorded in the manifest.
* The canonicalization implementation identifier and version MUST be recorded in the manifest.

The term “canonicalization” in this profile refers only to deterministic RDF dataset normalization for hashing. It does not imply canonical truth, universal authority, or epistemic finality.

## Hash computation

`rdf_hash.value` MUST be computed as:

```text
SHA-256(canonical_rdf_bytes)
```

Where:

* `canonical_rdf_bytes` is the canonical output produced by the selected RDFC algorithm;
* canonical bytes MUST be treated as a raw byte sequence;
* no platform-dependent newline, Unicode, path, locale, or serialization normalization may be applied after canonicalization unless the selected algorithm explicitly defines it.

The manifest MUST include:

* RDF canonicalization algorithm identifier
* RDF canonicalization algorithm version
* canonicalization implementation identifier and version
* hash algorithm identifier
* exact export artifact or artifacts hashed
* exact projection coverage
* any declared exclusions

## Resource limits

Because RDF dataset canonicalization can exhibit worst-case behavior, implementations MUST support resource limits and MUST declare them in the manifest.

Minimum required limit fields:

* `limits.timeout_ms`
* `limits.max_triples` or equivalent dataset size cap
* `limits.max_blank_nodes` or equivalent blank-node complexity cap
* `limits.max_memory_mb`

Recommended additional limit fields:

* `limits.max_named_graphs`
* `limits.max_output_bytes`
* `limits.max_cpu_ms`
* `limits.max_recursion_depth`, when relevant to the implementation

## Limit exceed behavior

If declared resource limits are exceeded during canonicalization or hashing:

* the implementation MUST NOT emit a partial `rdf_hash`;
* the implementation MUST emit a structured issue in the export report;
* the implementation MUST preserve enough diagnostic information for reproducibility and review;
* the export manifest MUST NOT present the missing hash as successfully produced.

If a consuming policy declares `rdf_hash` as required for a given artifact, projection, authority channel, or assurance level, then a missing or unverified `rdf_hash` means the artifact is **not accepted under that policy**.

This is a policy outcome, not a statement about the underlying truth or falsity of the exported assertions.

## CI gating

If this profile is enabled in a build:

* CI MUST gate the canonicalization implementation against a selected subset of the W3C RDFC-1.0 test suite or an equivalent conformance suite declared by the implementation.
* The selected subset MUST be documented.
* The selected subset MUST be versioned.
* The rationale for subset selection SHOULD be documented when the full suite is not used.
* CI results SHOULD be linked from the export report or build record.

A build that cannot demonstrate conformance to the declared test subset MUST NOT claim conformance to this profile.

## Verification procedure

A verifier checks:

1. The export manifest declares `rdf-integrity-rdfc` profile activation, coverage, algorithms, implementation versions, and resource limits.
2. The verifier regenerates or loads the RDF export for the declared projection.
3. The verifier confirms that the declared coverage boundary is reproducible.
4. The verifier canonicalizes the RDF dataset using the declared algorithm.
5. The verifier hashes the canonical bytes with SHA-256.
6. The verifier compares the computed value to `rdf_hash.value`.
7. The verifier reports verification status for the declared projection.

Verification statuses SHOULD include:

* `verified`
* `hash_mismatch`
* `verification_not_possible`
* `coverage_ambiguous`
* `algorithm_unsupported`
* `limits_exceeded`
* `source_artifact_unavailable`

If the computed hash does not match `rdf_hash.value`, verification fails for that RDF projection.

If resource limits prevent verification, the verifier MUST report `verification_not_possible` or `limits_exceeded` with structured details.

If the active reader policy, export policy, authority channel, or assurance context requires RDF hash verification, then a projection that cannot be verified MUST NOT be treated as accepted under that policy.

## Manifest fields

Implementations SHOULD represent profile activation in the export manifest with fields similar to:

```json
{
  "profiles": [
    {
      "id": "rdf-integrity-rdfc",
      "version": "5.0",
      "enabled": true,
      "params": {
        "rdfc": {
          "algorithm": "RDFC-1.0",
          "version": "1.0",
          "implementation": {
            "name": "string",
            "version": "string"
          }
        },
        "coverage": {
          "projection": "full",
          "export_profile_id": "rdf-wdqs",
          "graphs": [],
          "exclusions": [],
          "scope": {},
          "source_artifact_ref": {}
        },
        "limits": {
          "timeout_ms": 30000,
          "max_triples": 1000000,
          "max_blank_nodes": 100000,
          "max_memory_mb": 4096
        },
        "rdf_hash": {
          "alg": "sha256",
          "value": "string",
          "artifact_ref": "string"
        }
      }
    }
  ]
}
```

The exact manifest schema MAY differ, but it MUST preserve the same semantics: profile identity, profile version, algorithm declaration, coverage declaration, limits, and hash value.

## Error and warning reporting

When enabled, the exporter MUST emit structured issues.

Errors:

* `RDFC_CANONICALIZATION_FAILED`
* `RDFC_LIMIT_EXCEEDED`
* `RDFC_UNSUPPORTED_DATASET_FEATURE`
* `RDFC_HASH_MISMATCH`
* `RDFC_COVERAGE_AMBIGUOUS`
* `RDFC_EXPORT_NON_DETERMINISTIC`
* `RDFC_ALGORITHM_UNSUPPORTED`
* `RDFC_SOURCE_ARTIFACT_UNAVAILABLE`

Warnings:

* `RDFC_SUBSET_TEST_SUITE`
* `RDFC_LIMITS_TIGHT`
* `RDFC_SKOLEMIZED_BLANK_NODES`
* `RDFC_METADATA_GRAPH_EXCLUDED`
* `RDFC_PROJECTION_NOT_EQUIVALENT`
* `RDFC_OPTIONAL_PROFILE_NOT_ENABLED`

Each issue SHOULD include:

* `code`
* `severity`
* `message`
* `path` or `artifact_ref`
* `projection`
* `details`

Recommended issue shape:

```json
{
  "code": "RDFC_LIMIT_EXCEEDED",
  "severity": "error",
  "message": "RDF canonicalization exceeded the declared blank-node limit.",
  "artifact_ref": "exports/wdqs-full.nq",
  "projection": "full",
  "details": {
    "limit": "max_blank_nodes",
    "declared_value": 100000,
    "observed_value": 145392
  }
}
```

## Determinism requirements

If the underlying export is deterministic according to its export profile, and the canonicalization algorithm passes CI gating, then `rdf_hash` MUST be stable across runs given identical inputs.

If determinism is violated and the hash changes across identical rebuilds:

* the build MUST be treated as non-conformant under this profile;
* the export report MUST include a structured error;
* the manifest MUST NOT claim a verified stable RDF hash for that projection.

Determinism requirements apply to the declared RDF projection only. They do not imply that other projections, exports, reader-policy views, or runtime packs are identical.

## Conformance

A build is conformant to this profile if:

* profile activation is declared with `profile.id = "rdf-integrity-rdfc"`;
* `profile.version = "5.0"` is declared;
* coverage boundaries are explicitly declared;
* canonicalization and hashing follow the declared algorithms;
* resource limits are enforced and recorded;
* CI gating is applied when the profile is enabled;
* structured errors are emitted when hash production or verification cannot complete;
* no partial `rdf_hash` is emitted;
* deterministic rebuilds produce stable hashes for identical inputs;
* verification procedures can be independently reproduced within declared limits.

A build is not conformant to this profile if:

* the RDF projection boundary is ambiguous;
* the hash algorithm or canonicalization algorithm is not declared;
* profile activation is claimed without a verifiable hash;
* a partial hash is emitted after canonicalization failure;
* failures are hidden or downgraded into successful verification;
* the manifest presents export integrity as epistemic validation.

## Interactions with other profiles

* **RDF WDQS Export** provides the RDF dataset this profile hashes.
* **Provenance (Nanopub + PROV-O)** may package related graphs, attribution, and provenance structures, but does not substitute for canonical RDF dataset hashing.
* **Validation SHACL** and **Validation ShEx** may validate RDF shape conformance, but shape validity does not substitute for RDF export integrity.
* **Reader Policy** may require or ignore this profile depending on assurance needs.
* **Authority Recognition** may require RDF integrity evidence before recognizing an export, but RDF integrity alone does not imply recognition.
* **Runtime Pack Manifest** handles runtime distribution integrity separately.
* **Kristal Core Identity** remains defined by the core manifest and JSON canonicalization rules; this profile MUST NOT redefine `kristal_id`.

## Security and trust considerations

This profile protects RDF export integrity, not epistemic truth.

A successful RDF hash verification means:

* the declared RDF projection was reproduced;
* the canonicalized RDF bytes match the declared hash;
* the export boundary, algorithm, and limits were sufficient for verification.

It does not mean:

* every exported assertion is true;
* every assertion is validated;
* the export is recognized by an authority channel;
* the export is visible under a strict reader policy;
* the export has high certainty.

Implementations and user interfaces SHOULD keep these distinctions visible.

## Summary

This profile adds optional RDF export integrity to Kristal v5.

It provides a deterministic way to verify RDF projections using RDF Dataset Canonicalization and SHA-256 hashing. It does not define truth, validation, recognition, certainty, or reader visibility.

The profile’s responsibility is narrow and technical:

> A declared RDF projection can be independently canonicalized, hashed, and compared against the manifest.

All epistemic status remains governed by Kristal v5 validation, certainty, authority recognition, federation, and reader-policy rules.
