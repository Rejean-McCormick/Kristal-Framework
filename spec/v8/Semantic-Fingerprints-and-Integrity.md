# Semantic fingerprints and integrity

## Byte identity and semantic fingerprint are different

v6/v7 content hashes identify canonical bytes under their declared canonicalization boundaries. v8 does not change those rules.

A **semantic fingerprint** is an optional derived digest over a versioned semantic projection. It is useful for caching, deduplication and query continuation when irrelevant presentation differences should not change the semantic key.

```text
SEMANTIC FINGERPRINT != BYTE HASH
```

## Profile

A semantic fingerprint MUST declare its profile, for example:

```text
kristal.semantic-fingerprint/v1
```

The profile defines:

- included semantic fields;
- excluded presentation/derived fields;
- canonical ordering;
- canonical scalar encoding;
- hash algorithm and domain separator.

Processors MUST NOT invent local exclusion lists while claiming the same profile.

## Language exclusion

A semantic fingerprint profile for canonical semantic state SHOULD exclude external lexical labels when those labels do not alter meaning. Lexical artifacts can have their own independent content/fingerprint identities.

## Query use

Indexes and continuations MAY bind to semantic fingerprints in addition to byte hashes. When exact source bytes matter, the byte/content hash remains authoritative for identity.

## Tamper evidence

A local hash chain or Merkle root is useful but not an independent proof if an attacker can rewrite both data and chain head. High-assurance deployments SHOULD anchor release/snapshot roots in an independently governed system and define restore/fork reconciliation rules.

## Authority

A valid digest proves identity/integrity under a profile. It does not prove factual correctness or epistemic authority.
