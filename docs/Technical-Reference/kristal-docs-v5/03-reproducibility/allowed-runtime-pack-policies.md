# Allowed Runtime Pack Policies (Kristal v5)

## Status

Draft — normative for Kristal v5 portability

## Purpose

Kristal v5 keeps the **determinism surface area small** while enabling high-performance offline execution, filtered reader views, and portable Runtime Packs.

A Runtime Pack is a deployable offline package derived from a Kristal Exchange or shard set. It may support strict reference use, validated-only use, research use, creative use, or custom reader policies. The pack must make its construction policies explicit so another implementation can compare, reproduce, or reject it under the same declared constraints.

Runtime Pack storage structures are query/execution materializations. They are not a second source of epistemic truth and are not mutable application databases. A profile MAY define additional read-oriented physical representations (for example a database-like file) only when the manifest/schema/profile can declare them, bind them to the build/source identity, and preserve deterministic rebuildability. Core v5 does not currently define a writable SQLite profile.

A Kristal v5 Runtime Pack MUST:

1. Select policy values from the allowed sets below.
2. Record those selections in the Runtime Pack manifest under `policies`.
3. Declare any reader-policy materialization, source filtering, authority-channel filtering, or validation/certainty filtering that affects included data or indexes.
4. Preserve validation labels, certainty labels, authority labels, and source lineage.

Anything outside these policies is either:

* a **non-normative implementation detail**, or
* an **optional profile extension** that MUST be explicitly declared and MUST NOT change core IDs unless included in the declared reproducibility surface.

A physical storage representation that can influence query bytes/results, integrity verification, or portability is not merely an invisible implementation detail: the applicable profile and reproducibility surface MUST make the relevant representation/version/configuration constraints explicit.

## Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

---

# 1. Policy recording requirements

## 1.1 Manifest structure — minimum

The Runtime Pack manifest MUST include a `policies` object with, at minimum:

* `policies.data_ordering`
* `policies.row_grouping`
* `policies.membership_filter`
* `policies.bitmap`

The manifest MAY also include:

* `policies.parquet`
* `policies.source_materialization`
* `policies.reader_policy_materialization`
* `policies.validation_materialization`
* `policies.authority_materialization`

Implementations MAY include additional policy keys only if the Runtime Pack manifest schema permits them. Implementations MUST NOT omit the required policy keys above.

## 1.2 Manifest linkage

A Runtime Pack manifest SHOULD declare:

* `source_exchange_ref`
* `source_artifact_status`
* `reader_policy_refs`
* `query_contract_ref`

If the pack is derived from a working artifact, `source_artifact_status` SHOULD be `working`.

If the pack is derived from a reference artifact, `source_artifact_status` SHOULD be `reference`.

A Runtime Pack MUST NOT imply that a working artifact is a reference artifact. It MUST preserve the source artifact status.

## 1.3 Determinism requirement

Given identical:

* inputs,
* source snapshots,
* compiler version,
* compiler config hash,
* selected reader policies,
* selected authority channels,
* selected validation/certainty filters,
* and the same recorded Runtime Pack policies,

the resulting Runtime Pack MUST be reproducible according to `03-reproducibility/reproducibility-acceptance-tests.md`.

## 1.4 Label preservation requirement

Runtime Pack construction MUST preserve, expose, or faithfully index the following Kristal v5 labels when they exist in the source artifact:

* `artifact_status`
* `assertion_status`
* `validation_status`
* `certainty_level`
* `validated_as`
* `authority_channel`
* `recognition_status`
* `scope`
* `provenance_refs`
* `evidence_refs`
* `lineage`

A Runtime Pack MUST NOT flatten scoped validation into universal truth.

A Runtime Pack MUST NOT remove the fact that an assertion is hypothetical, disputed, fictional, mythological, rejected, revoked, or validated only under a specific authority channel.

---

# 2. Data ordering policies

Ordering is treated as an index. Runtime Pack builders MUST pick from the following ordering policies for the primary assertion or triples store.

## 2.1 Allowed ordering policies

Exactly one of the following MUST be selected in `policies.data_ordering.policy`:

* `qid_pid_statement_id_asc`
* `subject_predicate_object_statement_id_asc`
* `lexicographic_sop_asc`
* `lexicographic_spo_asc`
* `none`

## 2.2 Semantics

* `qid_pid_statement_id_asc` MUST define a total order where the primary sort is by subject identifier, then predicate identifier, then a stable statement identifier.
* `subject_predicate_object_statement_id_asc` MUST define a total order by subject, predicate, object, then stable statement identifier.
* `lexicographic_sop_asc` MUST define a total order by stable byte-wise lexicographic comparison of a deterministic triple key encoding whose fields are `(s, o, p)` in that order.
* `lexicographic_spo_asc` MUST define a total order by stable byte-wise lexicographic comparison of a deterministic triple key encoding whose fields are `(s, p, o)` in that order.
* `none` indicates that the pack does not declare a portable total order.

Packs that claim stable pagination profiles SHOULD NOT use `none`.

## 2.3 Tie-breakers

If the chosen ordering can produce ties under its primary keys, implementations MUST apply a deterministic tie-breaker chain that produces a total order:

1. The ordering policy’s primary keys.
2. A stable statement identifier when available.
3. Stable byte comparison of a deterministic serialized key.
4. Stable byte comparison of the content-addressed assertion or row identifier.

---

# 3. Row-group sizing policies

Row-group policy impacts scan behavior, Parquet block indexes, pagination behavior, and reproducibility.

## 3.1 Allowed row-group modes

Exactly one of the following MUST be selected in `policies.row_grouping.policy`:

* `fixed_rows_100k`
* `fixed_rows_1m`
* `fixed_bytes_128mb`
* `fixed_bytes_512mb`

## 3.2 Determinism constraints

* The selected policy MUST be applied deterministically.
* Implementations MUST NOT vary row groups based on unstable runtime factors such as CPU count, memory pressure, wall-clock time, thread scheduling, or host-specific file-system behavior.
* If `fixed_bytes_*` policies are used, byte-size computation MUST be defined by the pack profile or manifest schema.

---

# 4. Membership filter policies

Membership filters accelerate scans by quickly rejecting “not present” membership queries.

They are probabilistic. Kristal v5 therefore makes determinism and semantic safety requirements explicit.

## 4.1 Allowed filter kinds

Exactly one of the following MUST be selected in `policies.membership_filter.kind`:

* `none`
* `bloom`
* `cuckoo`
* `xor8`
* `xor16`

## 4.2 Required parameters

For `kind = none`, no additional parameters are required.

For `kind != none`, the manifest MUST record all required parameters for that kind.

For `bloom`:

* `seed`
* `bits_per_key`
* `hash_functions`

For `cuckoo`:

* `seed`
* `fingerprint_bits`
* `load_factor`

For `xor8` or `xor16`:

* `seed`
* `bits_per_key`

## 4.3 False positives

Membership filters MAY return false positives.

Therefore:

* A membership hit MUST NOT be treated as proof of membership.
* Implementations MUST deterministically prune false positives by validating against the source store or declared authoritative index inside the pack.
* No probabilistic acceptance is permitted at the semantic layer.
* Query results MUST NOT change assertion status, certainty level, validation status, or authority recognition because of a membership filter hit.

---

# 5. Bitmap index policies

Bitmaps accelerate joins, multi-value lookups, authority-channel filters, validation-status filters, certainty filters, and reader-policy views.

## 5.1 Allowed bitmap formats

Exactly one of the following MUST be selected in `policies.bitmap.format`:

* `roaring`
* `roaring_run_optimized`

## 5.2 Run optimization

If run optimization is enabled, it MUST be recorded as:

```json
{
  "policies": {
    "bitmap": {
      "run_optimize": true
    }
  }
}
```

If run optimization is not enabled, it MUST be recorded as:

```json
{
  "policies": {
    "bitmap": {
      "run_optimize": false
    }
  }
}
```

## 5.3 Required bitmap label indexes

A Runtime Pack intended for v5 reader-policy filtering SHOULD provide bitmap or equivalent deterministic indexes for:

* `artifact_status`
* `assertion_status`
* `validation_status`
* `certainty_level`
* `validated_as`
* `authority_channel`
* `recognition_status`
* `scope.domain`

If those indexes are omitted, the manifest SHOULD declare which filters require scan-based evaluation.

## 5.4 Container statistics

Recording bitmap container statistics for cost modeling is an OPTIONAL profile extension.

If enabled, it MUST be declared as a profile and MUST NOT affect core identity unless included in the declared reproducibility surface.

---

# 6. Parquet-level policies

## 6.1 Parquet schema invariants

If a Runtime Pack uses Parquet:

* Column names and logical types MUST follow the v5 runtime schema definition or a declared v5-compatible profile.
* Sorting declarations MUST match the chosen data ordering policy, if applicable.
* Validation, certainty, authority, provenance, and lineage fields MUST NOT be silently dropped if they are required by the declared reader policy or query contract.

## 6.2 Allowed Parquet policy fields

If `policies.parquet` is present, it MUST use only allowed enumerations:

* `compression` in `{zstd, snappy, gzip, none}`
* `dictionary_encoding` in `{true, false}`
* `statistics` in `{none, page, rowgroup}`

## 6.3 Parquet Bloom filters

Parquet Bloom filters MAY be enabled as an optional performance profile, recorded as:

```json
{
  "policies": {
    "parquet": {
      "bloom_filters": {
        "enabled": true
      }
    }
  }
}
```

If enabled and the manifest schema permits additional details, the pack SHOULD record:

* which columns have Bloom filters;
* sizing parameters;
* hash parameters;
* seed parameters needed to reproduce them.

Bloom filters MUST NOT be required for core conformance.

---

# 7. Source materialization policies

A Runtime Pack may represent the full source artifact or a filtered materialization.

## 7.1 Allowed source materialization policies

If `policies.source_materialization` is present, exactly one of the following MUST be selected in `policies.source_materialization.policy`:

* `full_source`
* `reader_policy_view`
* `authority_channel_view`
* `validation_status_view`
* `certainty_view`
* `custom_profile`

## 7.2 Semantics

* `full_source` means the pack contains the full selected source artifact or shard set.
* `reader_policy_view` means the pack materializes only the data visible under one or more declared reader policies.
* `authority_channel_view` means the pack materializes only data associated with selected authority channels.
* `validation_status_view` means the pack materializes only data matching selected validation statuses.
* `certainty_view` means the pack materializes only data matching selected certainty levels.
* `custom_profile` means the pack uses a declared profile-specific filtering rule.

## 7.3 Required declarations

If the source is filtered during pack construction, the Runtime Pack manifest MUST declare:

* source artifact references;
* source artifact status;
* selected shards or datasets;
* selected authority channels, if any;
* selected reader policies, if any;
* selected validation statuses, if any;
* selected certainty levels, if any;
* selected `validated_as` values, if any;
* selected scopes, if any;
* profile IDs, if `custom_profile` is used.

A filtered Runtime Pack MUST NOT present itself as containing the full source artifact.

Regardless of source materialization policy, the materialized store is non-authoritative relative to its declared source artifact. Consumers MUST NOT treat local mutations to Runtime Pack storage as edits to the Exchange. A changed knowledge state requires a new source/epistemic input and a new derived build.

---

# 8. Reader-policy materialization

People and applications may choose strict or broad reading surfaces. Runtime Packs may support or materialize those choices.

## 8.1 Allowed reader-policy materialization modes

If `policies.reader_policy_materialization` is present, exactly one of the following MUST be selected in `policies.reader_policy_materialization.mode`:

* `none`
* `index_only`
* `filtered_materialization`

## 8.2 Semantics

* `none` means the Runtime Pack does not provide reader-policy-specific materialization.
* `index_only` means the Runtime Pack contains the source data but provides deterministic indexes for reader-policy filtering.
* `filtered_materialization` means the Runtime Pack contains only the subset visible under declared reader policies.

## 8.3 Reader-policy references

If `index_only` or `filtered_materialization` is used, the manifest MUST declare `reader_policy_refs`.

A Runtime Pack MAY support reader modes such as:

* `reference_only`
* `validated_only`
* `high_certainty_only`
* `research`
* `creative`
* `all_with_labels`
* `custom`

A `validated_only` reader policy means that all visible assertions satisfy the active validation policy. It does not mean all visible assertions have maximum certainty or universal agreement.

---

# 9. Validation and certainty materialization

Validation and certainty are separate dimensions.

Validation answers:

```text
Who accepts this claim or artifact, under which rules, for which scope?
```

Certainty answers:

```text
How strong is the assertion within that scope?
```

## 9.1 Allowed validation materialization modes

If `policies.validation_materialization` is present, exactly one of the following MUST be selected in `policies.validation_materialization.mode`:

* `none`
* `index_only`
* `filtered_materialization`

## 9.2 Required fields

If `index_only` or `filtered_materialization` is used, the manifest SHOULD record:

* `included_validation_statuses`
* `included_certainty_levels`
* `included_validated_as`
* `included_authority_channels`
* `included_recognition_statuses`

## 9.3 Label constraints

Runtime Pack construction MUST NOT convert:

* `hypothesis` into `high_confidence_fact`;
* `fictional_corpus` into physical-world fact;
* `mythological_corpus` into physical-world fact;
* `disputed_position` into recognized reference;
* authority-scoped validation into universal validation.

A Runtime Pack may contain only validated data if the active reader policy requires it. That validated data may still include multiple certainty levels, provided the certainty level and `validated_as` status remain explicit.

---

# 10. Authority materialization

Authority channels are plural and scoped.

A Runtime Pack MAY be built for one or more authority channels.

## 10.1 Allowed authority materialization modes

If `policies.authority_materialization` is present, exactly one of the following MUST be selected in `policies.authority_materialization.mode`:

* `none`
* `index_only`
* `filtered_materialization`

## 10.2 Required fields

If `index_only` or `filtered_materialization` is used, the manifest SHOULD record:

* `included_authority_channels`
* `included_authority_types`
* `included_recognition_statuses`
* `authority_registry_ref`

## 10.3 Authority constraints

Recognition by one authority channel MUST NOT be represented as recognition by another authority channel unless the second authority channel explicitly recognizes it.

A Runtime Pack built for a selected authority channel MUST preserve the fact that the selection occurred.

---

# 11. Query contract linkage

This document specifies build-affecting Runtime Pack construction policies.

Runtime query semantics are specified by `04-query/query-contract.md` and any declared query profiles.

A Runtime Pack SHOULD declare `query_contract` in the manifest, including:

* `contract_id`;
* capability flags;
* supported reader modes;
* supported filters;
* supported pagination behavior;
* supported authority-channel filters;
* supported validation-status filters;
* supported certainty-level filters.

Any declared pagination behavior MUST derive its stable order from `policies.data_ordering`.

Any declared filtered view MUST derive its inclusion rules from declared reader, validation, certainty, source, or authority materialization policies.

---

# 12. Unknown policy handling

Implementations MUST reject unknown policy values and unknown schema/profile versions unless explicitly configured to allow them.

If an implementation is configured to allow unknown values, it MUST mark the Runtime Pack as using implementation-specific behavior.

Unknown policy acceptance MUST NOT silently change:

* content-addressed identity;
* validation status;
* certainty level;
* authority recognition;
* reader-policy visibility;
* query semantics.

---

# 13. Versioning

Policy enumerations are versioned by the Runtime Pack manifest schema version.

For Kristal v5:

```text
schema_version = 5.0
runtime_pack_version = 5.0
```

Any change to enumerations or semantics MUST bump the relevant schema or profile version.

Patch-level documentation edits that do not change Runtime Pack semantics MAY leave the schema/profile version unchanged.

---

# 14. Summary — portable minimum

A Kristal v5 Runtime Pack MUST record, at minimum:

* `policies.data_ordering`
* `policies.row_grouping`
* `policies.membership_filter`
* `policies.bitmap`

A Kristal v5 Runtime Pack SHOULD also declare:

* `source_exchange_ref`
* `source_artifact_status`
* `reader_policy_refs`
* `query_contract_ref`

A Runtime Pack that filters, materializes, or indexes a subset SHOULD also record, when applicable:

* `policies.source_materialization`
* `policies.reader_policy_materialization`
* `policies.validation_materialization`
* `policies.authority_materialization`
* `policies.parquet`

These policies define the **portable comparability surface** for Runtime Packs in Kristal v5.

The purpose is not to guarantee that all data is final, universally true, or maximally certain. The purpose is to make Runtime Packs reproducible, inspectable, filterable, and honest about their source, validation status, certainty level, authority channel, and reader policy.
