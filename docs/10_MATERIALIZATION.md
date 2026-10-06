# Materialization

## 1. Definition

A **materialization** is a physical representation of a logical artifact.

```text
Logical Artifact
      ↓
Materialization Profile
      ↓
Physical Representation
```

The purpose of v9 materialization is to allow storage and access optimization without changing logical identity.

## 2. Explicit profile

Every non-trivial materialization must identify the profile that explains how its bytes reconstruct logical content.

Examples of possible profiles:

```text
kristal.materialization/inline-json/1
kristal.materialization/native-blob/1
kristal.materialization/segmented-jsonl/1
kristal.materialization/kristal-state-v6/1
```

Additional profiles can be added independently from the core Standard.

## 3. Inline materialization

Small artifacts should normally remain simple.

An inline profile stores one artifact in one directly readable representation.

It is appropriate for:

- small epistemic corpora;
- contracts;
- small registries;
- procedure graphs of modest size;
- manifests and metadata.

V9 must not require segmentation because segmentation exists.

## 4. Segmented materialization

Large artifacts may be divided into immutable physical segments.

Segments can improve:

- partial reads;
- parallel validation;
- incremental rebuilds;
- cache reuse;
- partial distribution;
- localized corruption recovery.

Segment boundaries are physical and must not redefine semantic identity.

## 5. Factorization

Factorization stores shared logical information once while preserving its effective presence for each member.

For example, if 600,000 claims share:

```text
record_role = reference_knowledge
assertion_status = sourced
actionability = not_applicable
provenance = source X
```

a materialization may store that envelope once and associate member records with it.

The reconstructed logical records must still expose those values.

```text
DEFAULTED METADATA != LOST METADATA
```

## 6. Dictionaries

Repeated semantic identifiers may be represented by local ordinals inside a physical segment.

Example:

```text
421 → urn:kristal:pokemon:pokemon:1
```

The local value `421` must never become an externally stable semantic identity.

```text
LOCAL ORDINAL != SEMANTIC IDENTITY
```

## 7. Columnar representation

A homogeneous relation may be represented column-wise when that improves compression and query access.

This is especially suitable when many records share shape and only a few fields vary.

Columnar storage is a profile-level optimization. It is not a core semantic requirement.

## 8. Native graph/AST materialization

A graph or AST may remain physically graph-/tree-oriented.

V9 must not convert a mathematical AST, diagnostic multiplex graph or procedural DAG into rows merely because relational storage is available.

## 9. Compression

Compression is orthogonal to logical materialization.

A profile may permit codecs such as gzip or Zstandard, but changing codec alone must not change logical commitment.

## 10. Encryption

Encryption is also a physical envelope unless the logical contract makes ciphertext itself the knowledge object.

Re-encryption can change blob bytes while preserving logical commitment when the security profile allows logical comparison.

## 11. Materialization manifest

A manifest links a logical artifact commitment to one or more physical blobs.

Conceptual example:

```json
{
  "contract": "kristal.materialization/9.0",
  "source": {
    "artifact_id": "urn:kristal:pokemon:learnsets",
    "logical_commitment": "sha256:..."
  },
  "profile": "kristal.materialization/segmented-jsonl/1",
  "segments": [
    {
      "segment_key": "subject-bucket:00",
      "blob": {
        "media_type": "application/vnd.kristal.segment+jsonl",
        "digest": "sha256:...",
        "size": 182732
      }
    }
  ]
}
```

## 12. Hidden physical partitioning

Clients should query logical keys, not physical bucket names.

A materialization may change from 256 to 1024 buckets without changing the logical contract.

```text
LOGICAL QUERY != PHYSICAL PARTITION
```

## 13. Planner boundary

The Standard defines valid materialization contracts, not a mandatory optimizer.

A tool may recommend a materialization after examining:

- cardinality;
- repetition;
- update locality;
- query locality;
- entropy;
- structure type.

The selected profile remains explicit in the produced artifact.
