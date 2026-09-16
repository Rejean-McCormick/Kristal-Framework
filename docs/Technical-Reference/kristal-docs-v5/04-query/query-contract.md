# Query Contract

## Status

Draft — Kristal v5

## Purpose

This document defines the **offline query contract** for Kristal v5 **Runtime Packs** and any local wrapper service that exposes them.

The goal is a **portable, deterministic, offline-usable** query surface that supports common retrieval needs: search/navigation primitives, constrained graph lookups, assertion-status filters, validation filters, certainty filters, authority-channel filters, and reader-policy views.

This contract is intentionally constrained to preserve offline predictability, reproducibility, and local execution. It does not attempt to implement full SPARQL.

---

## 1. Scope and non-goals

### 1.1 In scope

This contract covers:

* a triple-pattern query model over `(s, p, o)` with any subset bound or unbound;
* deterministic result ordering derived from recorded Runtime Pack policies;
* deterministic paging by cursor or offset;
* deterministic behavior for declared resource limits;
* optional constrained joins;
* optional cardinality metadata;
* explicit support for reader-policy filtering;
* explicit support for validation, certainty, scope, authority-channel, and recognition filters;
* offline query behavior over a local Runtime Pack.

### 1.2 Out of scope

This contract does not require:

* full SPARQL 1.1 semantics;
* `OPTIONAL`;
* `UNION`;
* arbitrary `FILTER` expressions;
* property paths;
* subqueries;
* federated network queries;
* runtime dependence on live Wikidata, live SPARQL endpoints, LLM calls, or remote authority services;
* non-deterministic query behavior;
* adaptive sampling unless declared by a profile.

A Runtime Pack may be derived from Wikidata, Wikibase, RDF, JSON-LD, internal datasets, institutional corpora, fictional corpora, mythological corpora, or research submissions. The query contract only defines how local query behavior must be exposed once the pack exists.

---

## 2. Core model

A Kristal Runtime Pack exposes structured epistemic data.

A query result may include facts, claims, hypotheses, disputed statements, fictional statements, mythological statements, institutional declarations, or high-confidence reference assertions. The query layer must not hide the status of those assertions when the pack contains that metadata.

Kristal v5 separates:

* artifact existence;
* artifact integrity;
* assertion status;
* certainty level;
* validation status;
* authority recognition;
* reader visibility.

Query implementations must preserve that separation.

A query result being returned does not mean the claim is universally true. It means the claim exists in the pack and is visible under the active query parameters and reader policy.

---

## 3. Terminology

* **Term**: a subject, property, object identifier, or literal.
* **Triple**: `(s, p, o)` where `s` and `p` are identifiers and `o` is an identifier or literal.
* **Triple pattern**: a triple where any of `s`, `p`, or `o` may be unbound.
* **Binding**: a concrete value for an unbound position.
* **Result set**: ordered list of matching triples, bindings, statements, or assertion views.
* **Statement**: a claim-like unit that may include qualifiers, references, rank, provenance, status, certainty, and authority metadata.
* **Assertion**: an epistemic statement with status, certainty, provenance, and scope.
* **Assertion status**: status such as `hypothesis`, `claimed`, `sourced`, `disputed`, `reviewed`, `validated`, `rejected`, `retracted`, or `superseded`.
* **Certainty level**: strength of the assertion within its scope, such as `unknown`, `speculative`, `low`, `medium`, `high`, `established`, or `not_applicable`.
* **Validation status**: decision status such as `not_evaluated`, `in_review`, `validated`, `conditionally_validated`, `disputed`, `rejected`, or `revoked`.
* **Validated as**: the epistemic mode under which an assertion was validated, such as `hypothesis`, `institutional_reference`, `publisher_declaration`, `mythological_corpus`, or `fictional_corpus`.
* **Authority channel**: declared authority under which a claim, artifact, shard, or pack is validated, recognized, rejected, or disputed.
* **Recognition status**: authority-recognition state such as `recognized`, `conditionally_recognized`, `under_review`, `disputed`, `rejected`, `deprecated`, or `revoked`.
* **Reader policy**: a declared visibility policy that determines which authority channels, validation statuses, certainty levels, and epistemic modes are included.
* **Paging mode**: either `CURSOR` or `OFFSET`, as recorded in pack policies.
* **Cursor**: opaque paging token that resumes iteration deterministically.
* **Offset paging**: deterministic paging by `(offset, limit)` against a deterministic ordering.
* **Page size**: number of results requested per page. This is `limit` in the core contract. Profiles may name it `page_size`.
* **join1**: constrained two-stage lookup pattern with a declared cap and strictness mode.

Normative keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.

---

## 4. Query model

### 4.1 Required query primitive

An implementation MUST support querying a single triple pattern.

Inputs:

* `s` — bound or unbound;
* `p` — bound or unbound;
* `o` — bound or unbound;
* `limit` — positive integer page size;
* paging parameters according to the pack’s declared paging mode.

Output:

* an ordered sequence of results, each result containing either:

  * matching triples `(s, p, o)`;
  * bindings for unbound positions;
  * statement objects;
  * assertion objects;
  * or a declared stable combination of the above.

Implementations MUST document which output shape they use and MUST keep it stable within a declared `contract_id`.

### 4.2 Required metadata preservation

If the Runtime Pack contains the following metadata, the query layer MUST be able to expose it either inline or through an explicitly declared expansion/profile:

* assertion identifier;
* assertion status;
* certainty level;
* validation status;
* validated-as mode;
* authority channel;
* recognition status;
* provenance references;
* evidence references;
* scope;
* source shard;
* source artifact;
* lineage reference;
* dispute/conflict marker.

A query surface MAY offer compact results by default, but it MUST document how clients can request or resolve the status-bearing form when supported by the pack.

### 4.3 Determinism

Given:

* identical Runtime Pack bytes;
* identical recorded portable policy selections;
* identical query inputs;
* identical reader policy;
* identical wrapper configuration;

the implementation MUST return:

* identical result ordering;
* identical paging behavior;
* identical cap behavior;
* identical error behavior.

---

## 5. Data model constraints

### 5.1 Identifiers and literals

Subjects and properties MUST be represented in a stable identifier space, such as QID/PID-like strings or an equivalent stable encoding.

Literal normalization rules for numbers, dates, time zones, language tags, units, and datatypes MUST be deterministic and MUST be consistent with the Runtime Pack manifest or a referenced normalization profile.

### 5.2 Statement projections

Runtime Packs MUST define whether the runtime query surface returns:

* the full statement set;
* a best-rank or truthy-like projection;
* a reader-policy-filtered projection;
* a scope-filtered projection;
* or multiple named projections.

If a truthy-like projection is supported, mapping rules MUST be deterministic and documented.

If only export profiles define truthy-like behavior and the runtime does not, the runtime MUST state that clearly.

### 5.3 Assertion-status projection

A Runtime Pack MAY expose statement triples without assertion metadata for compact query use. However, if the pack supports v5 assertion metadata, the query contract SHOULD expose at least one projection that preserves:

* assertion status;
* certainty level;
* validation status;
* authority channel;
* recognition status;
* scope.

Recommended projection names:

* `triples`;
* `statements`;
* `assertions`;
* `reference_view`;
* `validated_view`;
* `reader_policy_view`.

---

## 6. Reader-policy filtering

### 6.1 Purpose

Reader policies allow people and applications to choose what they want to see.

Examples:

* `reference_only`;
* `validated_only`;
* `high_certainty_only`;
* `research`;
* `creative`;
* `all_with_labels`;
* `custom`.

A reader policy is not a truth engine. It is a visibility rule.

### 6.2 Required reader-policy declaration

If a Runtime Pack supports reader-policy filtering, the manifest SHOULD reference one or more reader policies through `reader_policy_refs`.

The query contract SHOULD expose the active reader policy in responses, either by ID or resolved metadata.

### 6.3 Reader-policy inputs

A query MAY include:

* `reader_policy_id`;
* `reader_mode`;
* `allowed_authority_channels`;
* `allowed_validation_statuses`;
* `allowed_certainty_levels`;
* `allowed_validated_as`;
* `include_disputed`;
* `include_fictional`;
* `include_mythological`;
* `include_rejected`;
* `show_labels`.

If the query surface does not allow arbitrary inline reader-policy parameters, it MUST document the supported named reader policies.

### 6.4 Validated-only behavior

`validated_only` means:

* all visible assertions satisfy the active validation policy;
* validation is scoped by authority, policy, and domain;
* visible assertions may still have different certainty levels;
* visible assertions may be validated as hypotheses, institutional records, publisher declarations, mythological corpora, fictional corpora, disputed positions, or high-confidence facts.

`validated_only` MUST NOT be interpreted as:

* all visible assertions have maximum certainty;
* all authorities agree;
* every assertion is universally true;
* every assertion is a physical-world factual claim.

---

## 7. Filters

### 7.1 Core triple filters

The query primitive MUST support:

* `s`;
* `p`;
* `o`.

### 7.2 Recommended v5 epistemic filters

If the pack contains the relevant metadata, implementations SHOULD support filters for:

* `artifact_status`;
* `assertion_status`;
* `certainty_level`;
* `validation_status`;
* `validated_as`;
* `authority_channel`;
* `recognition_status`;
* `scope.domain`;
* `scope.subdomain`;
* `scope.jurisdiction`;
* `scope.language`;
* `source_shard`;
* `source_artifact`;
* `reader_policy`.

### 7.3 Disagreement filters

If the pack supports federation or conflict metadata, implementations SHOULD support:

* `include_disputed`;
* `include_conflicts`;
* `conflict_strategy`;
* `authority_precedence`;
* `show_disagreement`.

Default behavior SHOULD be determined by the active reader policy.

### 7.4 Fiction, mythology, and symbolic scopes

If a pack contains fictional, mythological, symbolic, or speculative material, implementations SHOULD preserve those labels and SHOULD support filtering them through:

* `include_fictional`;
* `include_mythological`;
* `include_symbolic`;
* `include_speculative`;
* `validated_as`.

A query implementation MUST NOT silently present fictional or mythological assertions as validated physical-world truth.

---

## 8. Result ordering

### 8.1 Ordering policy

Result ordering MUST be derived from the Runtime Pack’s recorded ordering policy, such as `policies.data_ordering`.

Implementations MUST NOT use implementation-dependent iteration order.

### 8.2 Stable tie-breakers

If multiple rows compare equal under the primary ordering keys, implementations MUST define stable tie-breakers so ordering is total and deterministic.

Possible tie-breakers:

* statement ID;
* assertion ID;
* shard ID;
* source row ID;
* content hash;
* stable lexical ordering.

### 8.3 Ordering disclosure

Implementations MUST document:

* primary ordering keys;
* tie-breakers;
* whether ordering is over triples, statements, assertions, or bindings;
* whether filtering happens before or after ordering;
* whether paging happens before or after policy filtering.

Recommended rule:

* filtering SHOULD happen before paging;
* ordering SHOULD happen after filtering;
* paging SHOULD apply to the ordered, filtered result set.

---

## 9. Resource limits and join caps

### 9.1 Required limits

Implementations MUST declare, at minimum:

* maximum allowed page size: `limit_max`;
* timeout policy, if any;
* memory/resource cap policy, if any;
* join cap policy if `join1` is supported:

  * `join1_cap.default`;
  * `join1_cap.mode`.

These MUST be surfaced in either:

* the Runtime Pack manifest;
* the query contract;
* or the local wrapper configuration if the wrapper is the enforcement point.

They MUST remain deterministic for a given pack and configuration.

### 9.2 join1

If the runtime supports a constrained two-stage lookup, it MUST define `join1` explicitly.

Example:

1. Evaluate pattern A to produce intermediate bindings.
2. Bound intermediate bindings by `join1_cap.default`.
3. Use each binding to evaluate pattern B.
4. Combine results deterministically.
5. Apply declared ordering, filtering, and paging rules.

If `join1` is not supported, the implementation MUST reject such requests deterministically with a stable error code.

### 9.3 Cap breach behavior

When a cap is exceeded, behavior MUST be determined by the declared `join1_cap.mode`:

* `STRICT`: return an error response with a stable error code.
* `TRUNCATE`: truncate intermediate results deterministically and return `truncated=true` plus deterministic counts where feasible.

Silently truncating without a flag MUST NOT occur.

### 9.4 Recommended strictness

For correctness-sensitive views such as `reference_only`, `validated_only`, legal, health, scientific, or institutional reference contexts, `STRICT` is recommended.

For exploratory views such as `research`, `creative`, or `all_with_labels`, `TRUNCATE` MAY be acceptable when visibly declared.

---

## 10. Paging contract

An implementation MUST support exactly one declared paging mode per contract identifier:

* `CURSOR`; or
* `OFFSET`.

A Runtime Pack or wrapper MAY expose multiple query contracts if it supports multiple paging modes.

### 10.1 Cursor paging

If cursor paging is supported:

* the cursor MUST be opaque to callers;
* the cursor MUST resume iteration deterministically for the same pack, query inputs, reader policy, and wrapper configuration;
* the cursor MUST become invalid if the pack changes;
* the cursor MUST become invalid if query parameters change, unless explicitly supported;
* the cursor SHOULD encode or bind to the active reader policy.

Core response fields:

* `next_cursor`;
* `has_more`.

### 10.2 Offset paging

If offset paging is supported:

* ordering MUST be deterministic;
* `(offset, limit)` MUST be deterministic over the filtered and ordered result set;
* responses SHOULD include:

  * `offset`;
  * `limit`;
  * `total`, if cheap or declared by a profile.

### 10.3 Pagination profile

If the pack claims `profile-query-tpf-pagination@v5`, the normative request/response envelope, stable-order requirements, and optional cardinality fields are defined by:

* `05-profiles/profile-query-tpf-pagination.md`.

This contract does not define a transport. A local wrapper MAY expose HTTP endpoints, file APIs, embedded APIs, WASM calls, or device-local APIs, but MUST preserve the profile’s normative behaviors and remain usable offline.

---

## 11. Error model

### 11.1 Stable error codes

Implementations MUST return stable, machine-readable error codes.

At minimum:

* `invalid_query_schema`;
* `invalid_parameter_type`;
* `unsupported_query_shape`;
* `unsupported_projection`;
* `unsupported_filter`;
* `unsupported_reader_policy`;
* `reader_policy_not_available`;
* `cap_exceeded`;
* `cursor_invalid`;
* `cursor_expired`;
* `pack_not_found`;
* `pack_integrity_failed`;
* `pack_signature_invalid`;
* `pack_not_accepted_by_policy`;
* `query_contract_mismatch`;
* `resource_limit_exceeded`;
* `internal_corruption`;
* `unsupported_profile`.

### 11.2 Deterministic error behavior

Errors MUST be deterministic for a given:

* pack;
* query input;
* reader policy;
* recorded policies;
* wrapper configuration.

### 11.3 Integrity-related errors

If a pack fails required integrity verification under the active query, reader, or activation policy, the implementation MUST NOT return results as trusted.

It SHOULD return a stable error such as:

* `pack_integrity_failed`;
* `pack_signature_invalid`;
* `pack_not_accepted_by_policy`.

An implementation MAY expose limited diagnostic metadata if allowed by policy, but it MUST clearly mark the pack as unavailable for trusted query use.

---

## 12. Optional cardinality metadata

If the pack declares cardinality estimates as supported, responses MAY include a `cardinality` object:

```json
{
  "type": "exact",
  "value": 42,
  "scope": "pattern"
}
```

Allowed fields:

* `type`: `exact` or `approx`;
* `value`: integer;
* `bounds`: optional `{ "lower": int, "upper": int }`;
* `confidence`: optional float in `[0,1]`;
* `scope`: for example `pattern`, `pattern+projection`, `pattern+reader_policy`, or `pattern+filters`.

Rules:

* If `type = "exact"`, `value` MUST be correct.
* If `type = "approx"`, the implementation MUST document the approximation method.
* Cardinality MUST specify whether it is counted before or after reader-policy filtering.
* Cardinality MUST specify whether it is counted before or after authority, validation, and certainty filters.

---

## 13. Query request shape

This contract does not require one transport, but implementations SHOULD expose an equivalent request shape.

Example:

```json
{
  "contract_id": "kristal.v5:query:triple-pattern@1",
  "projection": "assertions",
  "pattern": {
    "s": "Q42",
    "p": null,
    "o": null
  },
  "filters": {
    "reader_policy_id": "reader_policy:validated-only-global-reference",
    "authority_channel": ["authority:unesco-global-reference"],
    "validation_status": ["validated", "conditionally_validated"],
    "certainty_level": ["medium", "high", "established"],
    "include_disputed": false,
    "include_fictional": false,
    "include_mythological": false
  },
  "paging": {
    "mode": "CURSOR",
    "limit": 100,
    "cursor": null
  },
  "include": {
    "labels": true,
    "provenance": true,
    "validation": true,
    "recognition": true,
    "certainty": true,
    "scope": true
  }
}
```

---

## 14. Query response shape

Implementations SHOULD expose an equivalent response shape.

Example:

```json
{
  "contract_id": "kristal.v5:query:triple-pattern@1",
  "runtime_pack_id": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "source_exchange_id": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "projection": "assertions",
  "reader_policy_id": "reader_policy:validated-only-global-reference",
  "results": [
    {
      "s": "Q42",
      "p": "P31",
      "o": "Q5",
      "assertion_id": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      "assertion_status": "validated",
      "validation_status": "validated",
      "validated_as": "high_confidence_fact",
      "certainty_level": "established",
      "authority_channel": "authority:wikidata-seed",
      "recognition_status": "recognized",
      "scope": {
        "domain": "wikidata",
        "subdomain": null,
        "jurisdiction": null,
        "time_window": null,
        "tenant_id": null,
        "environment": null,
        "language": "en"
      },
      "provenance_refs": [],
      "evidence_refs": []
    }
  ],
  "paging": {
    "next_cursor": null,
    "has_more": false
  },
  "diagnostics": {
    "truncated": false,
    "filters_applied_before_paging": true,
    "ordering_policy": "qid_pid_statement_id_asc"
  }
}
```

---

## 15. Manifest requirements

### 15.1 Contract declaration

A Runtime Pack that claims conformance to this query contract SHOULD declare `query_contract_ref` in the Runtime Pack Manifest.

Recommended fields:

* `query_contract_ref.contract_id`;
* `query_contract_ref.contract_hash`;
* `query_contract_ref.contract_version`.

If the pack claims a pagination profile, it MUST also declare pagination support in `query_capabilities`.

If the pack supports cardinality metadata, it SHOULD declare that in `query_capabilities`.

### 15.2 Policy linkage

To interpret query behavior deterministically, the Runtime Pack Manifest MUST record or reference the portable policy selections that govern:

* ordering;
* paging mode;
* join caps;
* strictness mode;
* projections;
* reader-policy availability;
* authority-channel filters;
* validation-status filters;
* certainty-level filters;
* scope filters.

These may be declared directly in the Runtime Pack Manifest or through referenced policies.

### 15.3 Reader-policy linkage

If reader-policy filtering is supported, the Runtime Pack Manifest SHOULD include `reader_policy_refs`.

Each referenced reader policy SHOULD declare:

* allowed authority channels;
* allowed validation statuses;
* allowed certainty levels;
* allowed validated-as modes;
* whether disputed material is included;
* whether fictional material is included;
* whether mythological material is included;
* whether labels must be shown;
* fallback behavior.

---

## 16. Conformance tests

A Kristal v5 implementation MUST ship fixtures or tests that validate:

* deterministic ordering for a known pack;
* stable paging across repeated runs;
* cap breach behavior matching declared strictness mode;
* stable error codes;
* projection behavior;
* reader-policy filtering;
* authority-channel filtering;
* validation-status filtering;
* certainty-level filtering;
* disputed-claim visibility;
* fictional/mythological scope visibility;
* integrity-error behavior;
* pagination profile behavior if enabled;
* cardinality behavior if enabled.

Test fixtures SHOULD include at least:

* a Wikidata-like factual statement;
* a sourced but not validated claim;
* a validated hypothesis;
* a high-certainty reference assertion;
* a disputed assertion;
* a fictional or mythological assertion;
* two authority channels that disagree;
* a reader policy that excludes one assertion and includes another.

---

## 17. Non-normative implementation notes

* Query engines may use Parquet, deterministic indexes, or a profile-defined read-only database-like materialization internally, provided observable query semantics remain conformant.
* Treat all Runtime Pack query stores as derived from the declared source artifact; do not accept local write-back as a mutation of Kristal knowledge.
* Prefer cursor paging over offset for large packs.
* Enforce resource limits early to protect offline devices.
* Keep query wrappers small and deterministic.
* Avoid implementation-dependent iteration order.
* Do not hide assertion labels in user-facing views.
* Do not let reader-policy filtering silently remove disagreement without exposing that a filter is active.
* If a pack declares signatures or integrity hashes, verify according to the active reader, trust-root, or activation policy before returning trusted results.
* For strict institutional deployments, use `reference_only`, `validated_only`, or `high_certainty_only` reader policies.
* For research and creative deployments, use broader policies with labels visible.
* For mythology and fiction, use `validated_as` and `certainty_level = "not_applicable"` where physical-world certainty is not the right metric.
