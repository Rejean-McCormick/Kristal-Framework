# Profile: Query — TPF-like Pagination (Kristal v5)

## Status

Optional standardized profile — Kristal v5

## Purpose

This profile defines an **offline-friendly, TPF-like pagination contract** for querying Kristal Runtime Packs.

The intent is to provide:

* predictable, cacheable, low-bandwidth query behavior;
* stable pagination semantics across implementations;
* reproducible cursor behavior over immutable Runtime Pack snapshots;
* optional cardinality metadata to support planning and user interfaces;
* pagination over reader-policy, validation-status, certainty-level, and authority-channel views.

This profile does **not** attempt to replicate full SPARQL semantics. Runtime Packs remain intentionally constrained, offline-executable, and governed by their declared query contract.

## Scope

This profile specifies:

* request and response envelopes for paginated queries;
* cursor-token pagination semantics;
* cursor stability guarantees;
* ordering requirements for correct pagination;
* optional cardinality metadata;
* declared-capability behavior;
* interaction with reader policies, authority channels, validation status, and certainty levels.

This profile does not specify:

* the full query language, which is defined by `04-query/query-contract.md`;
* network transport, such as HTTP versus local API;
* how Runtime Packs are built, which is defined by Runtime Pack construction policies;
* how authority channels validate or recognize claims, which is defined by authority and validation contracts.

Normative behaviors in this profile MUST hold regardless of transport.

---

## Conformance

An implementation claims this profile by including the following profile identifier in the Runtime Pack Manifest `profiles[]`:

```text
kristal.v5:profile-query-tpf-pagination@1
```

The Runtime Pack Manifest MUST also declare `query_contract` with:

* `query_contract.contract_id`, non-empty;
* `query_contract.supports_pagination = true`.

If the implementation supports cardinality estimates, it MUST also declare:

* `query_contract.supports_cardinality_estimates = true`.

If the implementation supports reader-policy filtering, authority-channel filtering, validation-status filtering, certainty-level filtering, or `validated_as` filtering, it MUST declare those capabilities in `query_contract.supported_filters` or an equivalent v5-compatible capability field.

If this profile is claimed, the implementation MUST meet the requirements below.

---

## Terminology

* **Page**: a bounded subset of results from a query.
* **Cursor token**: an opaque token allowing the client to fetch the next page.
* **Stable order**: a total order over the result set that does not change during pagination.
* **Reader policy**: a declared policy that determines which assertions, artifacts, authorities, validation statuses, certainty levels, or scopes are visible to a reader.
* **Filtered view**: a query view restricted by reader policy, authority channel, validation status, certainty level, scope, or profile-specific filters.
* **Snapshot**: the immutable Runtime Pack content addressed by `runtime_pack_id`.

---

# 1. Capability declaration

## 1.1 Required manifest fields

A Runtime Pack that claims this profile MUST declare the query contract in the Runtime Pack Manifest:

* `query_contract.contract_id`;
* `query_contract.supports_pagination = true`.

The Runtime Pack SHOULD also declare:

* `query_contract.supported_filters`;
* `query_contract.supported_reader_modes`;
* `query_contract.supported_ordering`;
* `query_contract.max_page_size`, if a maximum is enforced;
* `query_contract.capabilities_ref`, if capabilities are stored in a separate file.

## 1.2 Declared capabilities

If a Runtime Pack claims this profile and a consumer requests pagination within the declared capability set, the implementation MUST provide pagination behavior as specified here.

If a request asks for a capability not declared by the Runtime Pack, the implementation MUST return a structured error rather than returning partial or misleading results.

## 1.3 Capability labels

If the Runtime Pack supports filtering by Kristal v5 epistemic labels, the capabilities object SHOULD indicate support for:

* `artifact_status`;
* `assertion_status`;
* `validation_status`;
* `certainty_level`;
* `validated_as`;
* `authority_channel`;
* `recognition_status`;
* `scope.domain`;
* `scope.subdomain`;
* `reader_policy`.

---

# 2. Stable ordering is mandatory for pagination

## 2.1 Stable total order

Paginated queries MUST have a stable total order over results.

The order MUST be derived from one of:

* the Runtime Pack’s recorded `policies.data_ordering`;
* a query-contract-declared stable ordering profile;
* an explicit ordering parameter allowed by the base query contract.

Implementations MUST NOT paginate over an unstable or implementation-dependent ordering.

## 2.2 Ordering and filtered views

If the query is evaluated over a filtered view, the stable order MUST be applied after the filter is resolved.

Examples of filtered views include:

* `reader_policy = validated_only`;
* selected authority channels;
* selected validation statuses;
* selected certainty levels;
* selected scopes;
* selected `validated_as` values.

The filter MUST NOT change the meaning of the ordering policy. It only changes the visible result set.

## 2.3 Unorderable queries

If a query’s semantics do not produce a stable order, or if the Runtime Pack cannot derive one from declared policies, the implementation MUST reject pagination for that query with a structured error.

---

# 3. Page size

## 3.1 Required parameter

Implementations MUST support a `page_size` parameter.

`page_size` MUST be an integer greater than zero.

## 3.2 Maximum page size

Implementations SHOULD enforce a maximum page size to protect offline devices.

If enforced, the maximum MUST be documented and discoverable via capabilities.

## 3.3 Mapping to base query contract

The base query contract uses `limit`.

When this pagination profile is used:

* the effective `limit` MUST equal `page_size`;
* clients SHOULD omit `limit` inside the `query` object;
* if `query.limit` is present and differs from `page_size`, the implementation MUST return `INVALID_QUERY`.

---

# 4. Cursor tokens

## 4.1 Opaque tokens

Cursor tokens MUST be opaque to clients.

Clients MUST NOT depend on cursor token structure.

## 4.2 Determinism

Cursor tokens MUST be deterministic for the same:

* `runtime_pack_id`;
* `query_hash`;
* `page_size`;
* `cursor_position`;
* selected reader policy;
* selected filters;
* stable ordering policy.

Cursor tokens MUST NOT depend on wall-clock time.

## 4.3 Runtime Pack binding

Cursor tokens MUST be bound to the specific Runtime Pack identified by `runtime_pack_id`.

A token from one Runtime Pack MUST NOT be valid on another Runtime Pack.

## 4.4 Query binding

Cursor tokens MUST be bound to the query payload used to produce them.

A cursor token produced for one query MUST NOT be accepted for another query.

## 4.5 Resume behavior

Cursor tokens MUST include sufficient information, directly or indirectly, to resume iteration without changing the result sequence.

The internal mechanism is implementation-defined, but the externally visible behavior MUST be stable.

---

# 5. Pagination API — logical contract

Regardless of transport, the logical interface MUST accept:

* `query`: a query object defined in `04-query/query-contract.md`;
* `page_size`: integer greater than zero;
* `cursor`: optional opaque token;
* `reader_policy`: optional reader policy identifier or inline reader policy object, if supported;
* `filters`: optional object containing declared filter dimensions, if supported.

The query object MUST omit `limit` or set it equal to `page_size`.

The response MUST return:

* `runtime_pack_id`;
* `query_hash`;
* `page_size`;
* `results`;
* `next_cursor`;
* `page_info`.

If supported and declared, the response MAY also return:

* `cardinality`;
* `applied_reader_policy`;
* `applied_filters`;
* `result_labels`;
* `warnings`.

---

# 6. Response envelope

A conformant response MUST include:

* `runtime_pack_id`: Runtime Pack identifier;
* `query_hash`: hash of the canonical query payload;
* `page_size`: integer;
* `results`: array;
* `next_cursor`: string or null;
* `page_info`: object.

`page_info` MUST include:

* `returned`: integer count of results returned;
* `has_more`: boolean.

If the implementation supports cardinality estimates and declares that support in the manifest, responses MUST also include `cardinality`.

## 6.1 Result labels

If the query contract supports epistemic labels, results SHOULD preserve or expose relevant labels, including:

* `assertion_status`;
* `validation_status`;
* `certainty_level`;
* `validated_as`;
* `authority_channel`;
* `recognition_status`;
* `scope`;
* `provenance_refs`;
* `evidence_refs`.

If labels are omitted from individual rows for performance reasons, the response MUST provide a declared mechanism for retrieving them.

A response MUST NOT flatten authority-scoped validation into universal validation.

A response MUST NOT hide that a result is hypothetical, disputed, fictional, mythological, rejected, revoked, or validated only by a specific authority channel when that information is part of the source artifact and relevant to the active reader policy.

---

# 7. Query hashing

## 7.1 Query hash computation

Implementations MUST compute:

```text
query_hash = sha256(JCS(query_payload))
```

where `query_payload` includes:

* the query object;
* `page_size`;
* any explicit ordering parameters allowed by the base query contract;
* selected reader policy identifiers or inline reader policy content;
* selected authority-channel filters;
* selected validation-status filters;
* selected certainty-level filters;
* selected `validated_as` filters;
* selected scope filters;
* any other declared query-affecting filters.

`query_payload` MUST NOT include:

* `cursor`.

## 7.2 Limit normalization

For query hashing, `limit` MUST be normalized according to this profile:

* if `query.limit` is omitted, the normalized query payload uses `limit = page_size`;
* if `query.limit` is present and equals `page_size`, it MAY remain present or be normalized to the same canonical representation;
* if `query.limit` differs from `page_size`, the request is invalid and no query hash needs to be returned.

## 7.3 Canonicalization

Canonicalization for `query_hash` MUST use RFC 8785 JCS under the Kristal v5 canonicalization identifiers:

```text
canonicalization_profile = "kristal.v5:jcs-rfc8785"
canonicalization_version = "1"
```

---

# 8. Capabilities discovery

Implementations MUST provide a capabilities object discoverable via one of:

* an explicit API call;
* a static file in the Runtime Pack, for example `query/capabilities.json`;
* a manifest-declared `query_contract.capabilities_ref`.

Capabilities MUST include at least:

* supported query contract IDs;
* supported query profile IDs;
* maximum page size, if enforced;
* whether cardinality estimates are supported;
* supported ordering modes;
* supported reader modes;
* supported filters.

Capabilities SHOULD include support declarations for:

* `reader_policy`;
* `artifact_status`;
* `assertion_status`;
* `validation_status`;
* `certainty_level`;
* `validated_as`;
* `authority_channel`;
* `recognition_status`;
* `scope.domain`;
* `scope.subdomain`.

---

# 9. Cardinality metadata

Cardinality metadata is optional but standardized.

If the implementation supports cardinality estimates, it MUST:

* set `query_contract.supports_cardinality_estimates = true` in the Runtime Pack manifest;
* include `cardinality` in paginated responses.

## 9.1 Cardinality object

```json
{
  "cardinality": {
    "type": "estimate",
    "value": 12345,
    "confidence": "medium"
  }
}
```

## 9.2 Cardinality rules

* `value` MUST be a non-negative integer.
* `type` MUST be either `estimate` or `exact`.
* If exact cardinality is available, the implementation MAY use `"type": "exact"` and omit `confidence`.
* If cardinality is not supported, responses MUST NOT include `cardinality`.

## 9.3 Cardinality over filtered views

If the query uses reader-policy or epistemic filters, cardinality MUST refer to the filtered result set, not the unfiltered source artifact.

---

# 10. Error handling

Errors MUST be structured and MUST include:

* `code`: stable string identifier;
* `message`: human-readable message;
* `details`: optional object.

Required error codes:

* `UNSUPPORTED_PAGINATION`: query type cannot be paginated;
* `INVALID_CURSOR`: token is invalid or not bound to this pack/query;
* `PAGE_SIZE_TOO_LARGE`: requested page size exceeds the supported maximum;
* `INVALID_QUERY`: query does not conform to the base query contract or this profile;
* `UNSUPPORTED_FILTER`: requested filter is not supported by the declared query contract;
* `UNSUPPORTED_READER_POLICY`: requested reader policy is not supported;
* `UNSTABLE_ORDERING`: query cannot be paginated with stable ordering;
* `PACK_MISMATCH`: cursor or query is bound to another Runtime Pack;
* `INTERNAL_ERROR`: unexpected implementation error.

An implementation MUST NOT return partial or incorrect results when a request cannot be satisfied under declared capabilities.

---

# 11. Determinism and snapshot guarantees

## 11.1 Repeated calls

For a given Runtime Pack, pagination MUST be consistent across repeated calls:

* using the same cursor token MUST yield the same subsequent results;
* using the same query, page size, reader policy, filters, and cursor MUST yield the same page;
* tokens MUST remain valid for the lifetime of the Runtime Pack.

## 11.2 Immutable snapshots

Implementations MUST treat Runtime Packs as immutable snapshots.

If the underlying data changes, it MUST be represented as a new Runtime Pack with a new `runtime_pack_id`.

## 11.3 Filtered snapshots

If a Runtime Pack materializes a filtered view, the filter set is part of the snapshot identity.

A filtered Runtime Pack MUST NOT present itself as containing the full source artifact.

---

# 12. Declared-capability correctness

If a Runtime Pack Manifest claims this profile but the implementation cannot provide correct pagination behavior for a request that falls within the declared capability set, it MUST return a structured error.

It MUST NOT return partial, unstable, unlabeled, or misleading results.

This rule applies especially when:

* ordering cannot be made stable;
* cursor state is invalid;
* a requested reader policy is unsupported;
* a requested validation or certainty filter is unsupported;
* a requested authority-channel filter is unsupported;
* the implementation cannot preserve required result labels.

---

# 13. Non-normative guidance

Implementers SHOULD prefer cursor designs that can resume without full scans, such as:

* last-seen key;
* index position;
* stable row group position;
* bitmap-backed filter position;
* deterministic shard cursor.

Cursor tokens should remain opaque even when they encode deterministic state.

Implementers SHOULD keep default page sizes small for offline or low-memory environments.

Offline clients may use the following as a primary cache key strategy:

```text
(runtime_pack_id, query_hash, cursor)
```

If reader policies or filters are used, they are already included in `query_hash`.

---

# 14. Example request and response

## 14.1 Example request

```json
{
  "query": {
    "type": "spo",
    "s": "Q42",
    "p": "P31"
  },
  "page_size": 50,
  "reader_policy": "reader_policy:validated-only",
  "filters": {
    "authority_channel": ["authority:wikidata-seed"],
    "validation_status": ["validated"],
    "certainty_level": ["medium", "high", "established"]
  }
}
```

## 14.2 Example response

```json
{
  "runtime_pack_id": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "query_hash": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "page_size": 50,
  "results": [
    {
      "s": "Q42",
      "p": "P31",
      "o": "Q5",
      "assertion_status": "validated",
      "validation_status": "validated",
      "certainty_level": "established",
      "validated_as": "institutional_reference",
      "authority_channel": "authority:wikidata-seed",
      "scope": {
        "domain": "wikidata"
      }
    }
  ],
  "next_cursor": "opaque-token",
  "page_info": {
    "returned": 1,
    "has_more": true
  },
  "cardinality": {
    "type": "estimate",
    "value": 12345,
    "confidence": "medium"
  },
  "applied_reader_policy": "reader_policy:validated-only",
  "applied_filters": {
    "authority_channel": ["authority:wikidata-seed"],
    "validation_status": ["validated"],
    "certainty_level": ["medium", "high", "established"]
  }
}
```

---

# 15. Summary

A Kristal v5 Runtime Pack that claims this profile provides stable, deterministic pagination over immutable Runtime Pack snapshots.

The profile guarantees:

* stable ordering;
* deterministic cursor behavior;
* query hashing for cacheability and comparability;
* structured errors;
* optional cardinality metadata;
* declared support for reader policies and epistemic filters;
* preservation of validation, certainty, authority, and scope labels.

This profile does not claim that all visible data is universally true or maximally certain.

It guarantees that paginated query behavior is stable, explicit, inspectable, and aligned with the Runtime Pack’s declared policies.
