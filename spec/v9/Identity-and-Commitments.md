# Identity and Commitments

Kristal v9 distinguishes three independent identities:

- **Semantic ID** — which logical object is being referenced;
- **Logical Commitment** — the exact normalized logical content under a named profile;
- **Blob Digest** — the exact bytes of one physical representation.

```text
SEMANTIC IDENTITY != CONTENT IDENTITY
LOGICAL COMMITMENT != BLOB DIGEST
```

## Baseline artifact profile

The normative baseline profile is:

```text
kristal.logical/jcs-sha256-v1
```

Before applying this profile, the domain `logical_contract` MUST have produced its canonical logical payload. In particular, the domain contract is responsible for declaring and normalizing set-like collections. Arrays are otherwise order-significant.

For a `kristal_logical_artifact`, construct the projection in this exact shape:

```json
{
  "payload": "<artifact.payload>",
  "scope": "<artifact.scope, when present>",
  "extensions": "<artifact.extensions, when present>",
  "dependencies": "<normalized dependencies, when non-empty>"
}
```

`artifact_id`, `authority_ref`, `identity_profile`, `logical_commitment`, signatures, physical representations and build metadata are not members of the artifact-content projection.

A dependency is normalized to:

```json
{
  "artifact_id": "...",
  "logical_contract": {"id":"...","version":"..."},
  "logical_commitment": {"profile":"...","digest":"sha256:..."}
}
```

`logical_contract` is omitted when absent. `authority_ref` is deliberately excluded from the content projection. Dependencies are sorted lexicographically by the concatenation:

```text
artifact_id + U+0000 + logical_commitment.digest
```

The UTF-8 domain separator is:

```text
KRISTAL U+0000 LOGICAL-COMMITMENT U+0000
kristal.logical/jcs-sha256-v1 U+0000
logical_contract.id U+0000
logical_contract.version U+0000
```

The final digest is:

```text
sha256( UTF8(domain_separator) || UTF8(JCS(projection)) )
```

and is serialized as lowercase:

```text
sha256:<64 hexadecimal characters>
```

## Baseline state profile

The normative baseline state profile is:

```text
kristal.state-commitment/jcs-sha256-v1
```

The state projection contains:

```json
{
  "members": [],
  "references": [],
  "scope": {}
}
```

`scope` is omitted when absent.

Owned members are normalized as artifact logical references and sorted using the artifact-reference rule above.

External references are normalized as either:

```json
{"kind":"artifact","value":{...normalized artifact reference...}}
```

or:

```json
{
  "kind":"state",
  "value": {
    "state_ref":"...",
    "logical_commitment":{"profile":"...","digest":"sha256:..."}
  }
}
```

State references are sorted by:

```text
state_ref + U+0000 + logical_commitment.digest
```

The combined external reference list is then sorted lexicographically by the JCS serialization of each `{kind,value}` entry.

The following fields are deliberately excluded from the state-content projection:

- `state_ref`;
- `parents`;
- `authority_ref`;
- `created_at`;
- signatures and attestations;
- activation/publication metadata;
- materialization and blob metadata.

The UTF-8 domain separator is:

```text
KRISTAL U+0000 STATE-COMMITMENT U+0000
kristal.state-commitment/jcs-sha256-v1 U+0000
```

The digest is SHA-256 over the domain separator followed by JCS bytes of the normalized state projection.

## Why semantic IDs are excluded

Two independently named artifacts can carry byte-for-byte and logically identical content. The logical commitment is a content commitment; it is not the semantic identifier. Conversely, one stable semantic identifier may have multiple revisions with different logical commitments.

## Why authority is excluded

Authority, signature, recognition and publication are governance/trust facts surrounding logical content. Re-signing or changing a distribution authority MUST NOT silently change the content commitment. A state may still record and sign authority metadata independently.

## Profile evolution

A change to any projection field, exclusion, collection-normalization rule, domain separator, canonicalization algorithm or hash algorithm MUST use a new commitment profile identifier. Existing profiles are immutable.

The normative golden values are under `tck/v9/vectors/logical-commitment-vectors.json`.
