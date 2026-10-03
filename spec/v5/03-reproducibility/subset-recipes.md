# Subset recipes (Kristal v5 reproducibility)

## Status

Draft (normative for subset builder reproducibility)

## Purpose

A **subset recipe** is a declarative, reproducible input that defines how to derive a **deterministic subset** of a larger source snapshot so that the resulting Kristal artifacts are reproducible and comparable across toolchains.

Subset recipes are first-class in Kristal v5. They specify seeds, deterministic expansion rules, allow/deny constraints, depth limits, stopping criteria, reader-policy constraints, authority constraints, and snapshot identifiers.

A subset recipe may be used to produce:

* a Structured Epistemic State;
* a Working Exchange;
* a Reference Exchange;
* a Runtime Pack;
* a shard;
* a federation member;
* a reader-policy-specific package.

Subset recipes are part of the build input snapshot. If a recipe affects selected entities, statements, assertions, evidence, authority recognition records, validation decisions, or output bytes, it MUST be recorded in the relevant manifest or build record.

Normative keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.

---

## 1. Scope and non-goals

### 1.1 In scope

This document defines:

* recipe object model;
* recipe identity;
* deterministic subset selection;
* deterministic expansion rules;
* deterministic filtering by source, scope, status, certainty, validation, recognition, and authority channel;
* deterministic truncation and stopping criteria;
* how subset recipes participate in build determinism;
* how to record recipe references in Exchange, Runtime Pack, shard, federation, and build manifests.

### 1.2 Out of scope

This document does not define:

* full Wikidata subset research algorithms;
* ranking algorithms outside declared deterministic policies;
* runtime query behavior;
* reader UI behavior;
* Runtime Pack layout policies;
* authority governance procedures;
* validation policy semantics beyond deterministic filtering and recording.

For query/runtime behavior, see:

```text
04-query/query-contract.md
```

For Runtime Pack layout policies, see:

```text
03-reproducibility/allowed-runtime-pack-policies.md
```

For reader policy behavior, see:

```text
04-query/reader-policy-profiles.md
```

---

## 2. Determinism contract

### 2.1 Deterministic subset requirement

Given identical:

* source snapshot;
* subset recipe;
* compiler identity and version;
* declared source profiles;
* declared policies;
* declared authority registry;
* declared validation and recognition inputs;
* declared reader policy inputs;
* declared stopping and ordering rules;

the subset builder MUST produce identical selected sets.

Selected sets may include:

* selected entities;
* selected properties;
* selected statements;
* selected assertions;
* selected qualifiers;
* selected references;
* selected labels, aliases, and descriptions;
* selected evidence blobs;
* selected provenance records;
* selected validation decisions;
* selected authority recognition records;
* selected revocation records;
* selected reader policy records.

The selected sets MUST therefore be able to reproduce identical downstream artifacts when compiled under the same deterministic build rules.

### 2.2 Offline constraint

Subset evaluation MUST be executable without network access.

Any external dependency MUST be represented as a content-addressed input snapshot referenced by the recipe or by the build manifests.

Mutable live network state MUST NOT affect subset selection unless it has first been pinned into a content-addressed snapshot.

### 2.3 Selection does not imply validation

Selecting an assertion into a subset does not validate it.

Selecting a source, entity, claim, assertion, evidence reference, validation decision, or authority recognition record only means that it is included in the selected material.

Validation, certainty, and authority recognition remain explicit metadata and MUST NOT be inferred from inclusion alone.

---

## 3. Recipe identity

### 3.1 `recipe_id`

A subset recipe MUST have a stable content-addressed identifier:

```text
recipe_id = "sha256:" + hex(SHA-256(JCS(hash_target(recipe))))
```

Where:

* `JCS` is RFC 8785 JSON Canonicalization Scheme;
* `hash_target(recipe)` is the recipe object after applying required exclusions.

The v5 canonicalization values are:

```text
canonicalization_profile = "kristal.v5:jcs-rfc8785"
canonicalization_version = "1"
```

### 3.2 Hash target exclusions

The recipe hash target MUST exclude:

* `recipe_id`;
* `signatures`;
* signature envelopes;
* attestation overlays;
* proof overlays;
* any equivalent non-content verification wrapper.

`created_at` MAY appear on recipe objects, but it MUST NOT affect `recipe_id` unless a profile explicitly includes it in the hash target.

### 3.3 Canonical recipe representation

The normative recipe format is a JSON object.

If a producer stores recipes in another syntax, such as YAML or TOML, it MUST define a deterministic mapping into the normative JSON object prior to hashing.

The resulting JSON object MUST be the one used to compute `recipe_id`.

---

## 4. Recipe object model

A conforming recipe MUST be a JSON object with the following top-level fields.

### 4.1 Required fields

* `schema_version`

  * MUST be `"5.0"`.
* `artifact_type`

  * MUST be `"subset_recipe"`.
* `recipe_id`

  * MUST be present and MUST match the computed content-addressed ID.
* `canonicalization_profile`

  * MUST be `"kristal.v5:jcs-rfc8785"`.
* `canonicalization_version`

  * MUST be `"1"`.
* `source_snapshot_ref`

  * Content-addressed reference to the upstream dataset, corpus, Structured Epistemic State, Exchange, shard, federation, or other source snapshot.
* `seeds`

  * Seed sets that anchor the subset.
* `expansion`

  * Deterministic expansion rules.
* `constraints`

  * Allow/deny lists and other eligibility guards.
* `stopping`

  * Depth, budget, and termination rules.

### 4.2 Optional fields

* `recipe_version`

  * Human-managed semantic version for the recipe’s intent.
  * Does not replace `recipe_id`.
* `created_at`

  * Timestamp for recipe production.
  * MUST NOT affect `recipe_id` unless explicitly included by profile.
* `created_by`

  * Creator metadata.
* `description`

  * Human-readable description.
* `scope`

  * Declared recipe scope.
* `profiles_enabled`

  * Optional profiles that affect selection behavior.
* `reader_policy_ref`

  * Reader policy used as a selection constraint.
* `authority_registry_ref`

  * Authority registry used for authority-channel constraints.
* `validation_policy_refs`

  * Validation policies used for filtering or inclusion.
* `recognition_policy_refs`

  * Recognition policies used for filtering or inclusion.
* `signatures`

  * Optional signatures.
  * MUST NOT affect `recipe_id`.
* `extensions`

  * Implementation-specific fields that MUST NOT change core identity or deterministic selection semantics unless a profile explicitly defines them.

---

## 5. Source snapshot references

### 5.1 Source kinds

A subset recipe MAY target any source snapshot kind declared by Kristal v5, including:

* `wikidata_snapshot`;
* `wikibase_snapshot`;
* `structured_epistemic_state`;
* `working_exchange`;
* `reference_exchange`;
* `runtime_pack`;
* `exchange_shard`;
* `exchange_federation`;
* `dataset`;
* `evidence_bundle`;
* `authority_registry`;
* `validation_decision_set`;
* `authority_recognition_set`.

### 5.2 Source reference shape

A source snapshot reference SHOULD include:

```json
{
  "artifact_id": "sha256:<hex>",
  "artifact_type": "wikidata_snapshot",
  "ref": "snapshots/wikidata/full-2026-01.json",
  "content_hash": {
    "alg": "sha256",
    "value": "<64 lowercase hexadecimal characters>"
  }
}
```

### 5.3 Source stability

The source snapshot MUST be immutable for the purposes of recipe evaluation.

If the upstream source changes, a new source snapshot identifier MUST be used.

---

## 6. Seeds

### 6.1 Seed kinds

`seeds` MUST include at least one seed set.

Seed sets MAY include:

* `entity_ids`;
* `property_ids`;
* `statement_ids`;
* `assertion_ids`;
* `shard_ids`;
* `authority_channel_ids`;
* `validation_decision_ids`;
* `recognition_ids`;
* `dataset_ids`;
* `evidence_ids`;
* `scope_selectors`;
* `query_patterns`.

### 6.2 Entity, property, and statement seeds

For Wikidata/Wikibase-aligned sources:

* `entity_ids` SHOULD use stable entity identifiers, such as QID-like strings.
* `property_ids` SHOULD use stable property identifiers, such as PID-like strings.
* `statement_ids` SHOULD use stable statement identifiers where available.

### 6.3 Assertion seeds

For Kristal-native sources:

* `assertion_ids` SHOULD use stable content-addressed assertion IDs.
* Assertion seeds MUST NOT imply validation or recognition.
* Assertion status and certainty MUST be preserved during selection.

### 6.4 Scope selectors

Scope selectors MAY select material by:

* `domain`;
* `subdomain`;
* `jurisdiction`;
* `time_window`;
* `tenant_id`;
* `environment`;
* `language`.

### 6.5 Deterministic seed normalization

Before evaluation:

* seed arrays MUST be deduplicated;
* seed arrays MUST be sorted deterministically using stable byte-wise lexicographic order over their canonical string form;
* empty identifiers MUST be rejected;
* unknown identifiers MUST either be rejected or recorded as unresolved according to a declared policy;
* seed normalization MUST be independent of input file order.

---

## 7. Expansion rules

`expansion.rules` MUST be an array of rule objects.

Each rule object MUST have:

* `rule_id`

  * string, non-empty, unique within the recipe;
* `kind`

  * string enum or profile-defined rule kind;
* `params`

  * object containing parameters for the rule.

Rules are applied in a deterministic pipeline:

1. Seeds initialize the frontier at depth `0`.
2. For each depth `d` from `0` to `max_depth`, rules are applied in recipe order.
3. All sets produced at each step MUST be merged with deterministic deduplication and deterministic ordering.
4. Constraints are applied consistently.
5. Stopping criteria are applied deterministically.

### 7.1 Required portable baseline rule kinds

Implementations claiming conformance to the v5 subset-recipe baseline MUST implement the following rule kinds.

#### 7.1.1 `OUTGOING_EDGES`

Meaning:

For each entity or assertion in the frontier, include statements where the item is the subject, and optionally add referenced target entities to the next frontier.

Required params:

* `predicates`

  * array of property IDs, or `"*"`.
* `include_targets`

  * boolean.
* `include_qualifiers`

  * boolean.
* `include_references`

  * boolean.
* `include_assertion_metadata`

  * boolean.

#### 7.1.2 `INCOMING_EDGES`

Meaning:

For each entity in the frontier, include statements where the entity appears as an entity-valued object, and optionally add the statement subjects to the next frontier.

Required params:

* `predicates`

  * array of property IDs, or `"*"`.
* `include_subjects`

  * boolean.
* `include_qualifiers`

  * boolean.
* `include_references`

  * boolean.
* `include_assertion_metadata`

  * boolean.

#### 7.1.3 `TAXONOMY_CLOSURE`

Meaning:

Include closure over a declared taxonomy predicate set up to a bound.

Required params:

* `predicates`

  * array of property IDs.
* `direction`

  * `"up"`, `"down"`, or `"both"`.
* `max_hops`

  * integer greater than or equal to `1`.

#### 7.1.4 `LABELS_AND_DESCRIPTIONS`

Meaning:

Include label, alias, and description facts required for UX, query, or reader display.

Required params:

* `languages`

  * array of BCP-47 tags, or `"*"`.
* `include_aliases`

  * boolean.
* `include_descriptions`

  * boolean.

#### 7.1.5 `PROVENANCE_AND_EVIDENCE`

Meaning:

Include provenance and evidence records referenced by selected assertions or statements.

Required params:

* `include_provenance`

  * boolean.
* `include_evidence_refs`

  * boolean.
* `include_evidence_blobs`

  * boolean.
* `max_evidence_blobs`

  * integer greater than or equal to `0`, or `null`.

#### 7.1.6 `VALIDATION_DECISIONS`

Meaning:

Include validation decisions that target selected assertions, artifacts, shards, datasets, or authority channels.

Required params:

* `authority_channels`

  * array of authority channel IDs, or `"*"`.
* `validation_statuses`

  * array of validation statuses, or `"*"`.
* `validated_as`

  * array of validated-as modes, or `"*"`.
* `include_revoked`

  * boolean.

#### 7.1.7 `AUTHORITY_RECOGNITIONS`

Meaning:

Include authority recognition records that target selected assertions, artifacts, shards, datasets, runtime packs, or authority channels.

Required params:

* `authority_channels`

  * array of authority channel IDs, or `"*"`.
* `recognition_statuses`

  * array of recognition statuses, or `"*"`.
* `recognized_as`

  * array of recognized-as modes, or `"*"`.
* `include_revoked`

  * boolean.

#### 7.1.8 `READER_POLICY_CLOSURE`

Meaning:

Include metadata required to evaluate the declared reader policy offline.

Required params:

* `reader_policy_ref`

  * artifact reference or `"recipe.reader_policy_ref"`.
* `include_authority_registry`

  * boolean.
* `include_revocations`

  * boolean.
* `include_validation_policies`

  * boolean.
* `include_recognition_policies`

  * boolean.

### 7.2 Additional rule kinds

If an implementation supports additional rule kinds, they MUST be declared through `profiles_enabled`.

Additional rule kinds MUST remain:

* deterministic;
* testable;
* offline-evaluable;
* documented;
* portable within the declaring profile.

---

## 8. Constraints

`constraints` MUST include allow/deny fields.

### 8.1 Required constraint groups

A recipe MUST include:

* `allow_entities`;
* `deny_entities`;
* `allow_properties`;
* `deny_properties`.

Each field MUST be an array. Empty arrays are allowed.

### 8.2 Optional constraint groups

A recipe MAY include:

* `allow_assertions`;
* `deny_assertions`;
* `allow_authority_channels`;
* `deny_authority_channels`;
* `allow_validation_statuses`;
* `deny_validation_statuses`;
* `allow_recognition_statuses`;
* `deny_recognition_statuses`;
* `allow_certainty_levels`;
* `deny_certainty_levels`;
* `allow_validated_as`;
* `deny_validated_as`;
* `allow_domains`;
* `deny_domains`;
* `allow_scopes`;
* `deny_scopes`;
* `include_disputed`;
* `include_rejected`;
* `include_revoked`;
* `include_fictional`;
* `include_mythological`.

### 8.3 Constraint precedence

Deny lists MUST take precedence over allow lists.

If an allow list is non-empty, only identifiers or values present in it are eligible after applying deny precedence.

Constraints MUST apply consistently to:

* seed sets;
* expansion results;
* selected statements;
* selected assertions;
* next-frontier candidates;
* provenance records;
* evidence records;
* validation decisions;
* authority recognition records;
* reader policy closure records;
* truncation tie-breaking sets.

### 8.4 Reader policy constraints

If a recipe declares `reader_policy_ref`, the reader policy MAY constrain selection.

Reader policy constraints MUST be deterministic.

A reader policy MUST NOT silently convert scoped validation into universal truth.

A `validated_only` reader policy means all visible assertions satisfy the active reader policy. It does not mean all visible assertions are universally true, maximally certain, or accepted by all authorities.

---

## 9. Deterministic ordering and truncation

### 9.1 Stable ordering keys

All intermediate and final sets MUST be ordered deterministically.

The following ordering keys are normative unless a profile declares a different deterministic ordering policy.

#### Entity ordering key

Canonical string ID, byte-wise lexicographic.

#### Property ordering key

Canonical string ID, byte-wise lexicographic.

#### Statement ordering key

Preferred:

1. stable `statement_id`, if available;
2. otherwise deterministic surrogate key computed as JCS + SHA-256 over a canonical tuple of:

   * `subject_id`;
   * `predicate_id`;
   * `object_value`;
   * `qualifiers`;
   * `references`;
   * assertion metadata included in statement identity, if any.

#### Assertion ordering key

Preferred:

1. stable `assertion_id`, if available;
2. otherwise deterministic surrogate key computed as JCS + SHA-256 over the assertion hash target.

#### Evidence ordering key

Preferred:

1. stable `evidence_id`, if available;
2. otherwise content hash.

#### Validation decision ordering key

Preferred:

1. `validation_decision_id`;
2. otherwise deterministic surrogate key over target, authority channel, policy, status, scope, and created identity material.

#### Authority recognition ordering key

Preferred:

1. `recognition_id`;
2. otherwise deterministic surrogate key over issuer authority channel, target, recognition status, recognized-as mode, scope, and policy reference.

### 9.2 Budget limits and deterministic truncation

When a stopping or budget limit is reached, the subset builder MUST truncate deterministically.

It MUST:

* sort candidates by the relevant stable ordering key;
* select the first `N` items deterministically;
* record that truncation occurred;
* record which limit triggered truncation;
* record resulting counts.

Silent, undeclared truncation MUST NOT occur.

### 9.3 Truncation and epistemic status

Truncation MUST NOT imply rejection, low certainty, or invalidity.

If relevant material is omitted because of budget limits, the build metadata SHOULD make that visible to downstream consumers.

---

## 10. Stopping criteria

`stopping` MUST include:

* `max_depth`

  * integer greater than or equal to `0`;
* at least one global budget.

### 10.1 Required budget

At least one of the following MUST be present:

* `max_entities`;
* `max_statements`;
* `max_assertions`.

### 10.2 Optional budgets

A recipe MAY include:

* `max_properties`;
* `max_evidence_blobs`;
* `max_provenance_records`;
* `max_validation_decisions`;
* `max_authority_recognitions`;
* `max_frontier_per_depth`;
* `max_runtime_bytes_estimate`.

### 10.3 Stopping semantics

Depth is evaluated as BFS depth from seeds.

Budgets are global across the run unless a profile explicitly defines per-depth budgets.

When a frontier exceeds `max_frontier_per_depth`, the frontier MUST be truncated deterministically.

---

## 11. Recording subset recipes in manifests

Subset recipes participate in determinism as inputs.

### 11.1 Structured Epistemic State

If a Structured Epistemic State was produced using a subset recipe, the state SHOULD record the recipe reference.

Recommended location:

```text
source_refs[]
```

or:

```text
extensions.subset_recipe
```

The reference SHOULD include:

* `recipe_id`;
* `schema_version`;
* `source_snapshot_ref`;
* `content_hash`;
* `ref`, if available.

### 11.2 Working Exchange

If a subset recipe was used to produce a Working Exchange, the Exchange Manifest MUST record the recipe reference in a deterministic way.

Recommended location:

```text
inputs.subset_recipe
```

If the schema does not provide a dedicated field, producers SHOULD record:

```text
extensions.subset_recipe.recipe_id
extensions.subset_recipe.schema_version
extensions.subset_recipe.source_snapshot_ref
```

### 11.3 Reference Exchange

If a subset recipe affected the content of a Reference Exchange, the Reference Exchange MUST retain traceability to the recipe directly or through its source Working Exchange.

If the subset recipe affected authority recognition or validation inclusion, the relevant policy and recognition references MUST also be recorded.

### 11.4 Runtime Pack Manifest

If a Runtime Pack was compiled from an Exchange built via a subset recipe, the Runtime Pack Manifest SHOULD record the subset recipe reference directly or carry a deterministic pointer to the source Exchange Manifest.

If reader-policy filtering was applied during Runtime Pack compilation, the active reader policy MUST also be recorded.

### 11.5 Shard manifest

If a shard was produced using a subset recipe, the shard manifest MUST record the subset recipe reference.

The shard scope and recipe scope MUST be compatible, or the manifest MUST record the reason for the mismatch under a deterministic reason code.

### 11.6 Federation manifest

If a federation includes shards selected by subset recipes, the federation manifest SHOULD preserve recipe references through shard references.

If the federation itself was produced by a recipe, the federation manifest MUST record that recipe reference.

---

## 12. Conformance tests

Implementations SHOULD add subset recipe fixtures to the reproducibility test corpus.

### 12.1 Required test categories

Conformance tests SHOULD include:

* same toolchain reproducibility;
* cross-toolchain reproducibility;
* budget truncation;
* seed normalization;
* source snapshot pinning;
* stable `recipe_id` computation;
* deterministic evidence selection;
* deterministic validation-decision selection;
* deterministic authority-recognition selection;
* reader-policy-filtered selection;
* revoked target exclusion or inclusion according to policy;
* federation member selection.

### 12.2 Suggested fixtures

#### SR-1: Same toolchain

Same `source_snapshot_ref` and same recipe JSON produce identical selected sets.

#### SR-2: Cross toolchain

Published recipe fixture with expected `recipe_id` and expected selected-set hashes matches independent implementations.

#### SR-3: Budget truncation

Force truncation and verify deterministic truncation plus explicit truncation declaration.

#### SR-4: Reader policy

Apply a `validated_only` reader policy and verify that visible assertions satisfy the policy without changing underlying assertion meaning.

#### SR-5: Authority recognition

Select only assertions recognized by a specified authority channel and verify deterministic inclusion.

#### SR-6: Disagreement preservation

Select conflicting assertions from different shards and verify that disagreement is preserved unless a declared policy filters one side.

#### SR-7: Revocation behavior

Select authority recognition records and apply revocations according to declared policy.

---

## 13. Minimal example

The following example is non-normative.

```json
{
  "schema_version": "5.0",
  "artifact_type": "subset_recipe",
  "recipe_id": "sha256:<computed>",
  "canonicalization_profile": "kristal.v5:jcs-rfc8785",
  "canonicalization_version": "1",

  "source_snapshot_ref": {
    "artifact_id": "sha256:<snapshot>",
    "artifact_type": "wikidata_snapshot",
    "ref": "snapshots/wikidata/full.json",
    "content_hash": {
      "alg": "sha256",
      "value": "<64 lowercase hexadecimal characters>"
    }
  },

  "description": "Small deterministic subset for an offline education pack.",

  "scope": {
    "domain": "education",
    "subdomain": "general-reference",
    "language": "en"
  },

  "seeds": {
    "entity_ids": ["Q1", "Q42"],
    "property_ids": ["P31"],
    "statement_ids": [],
    "assertion_ids": []
  },

  "expansion": {
    "rules": [
      {
        "rule_id": "r1",
        "kind": "OUTGOING_EDGES",
        "params": {
          "predicates": "*",
          "include_targets": true,
          "include_qualifiers": true,
          "include_references": true,
          "include_assertion_metadata": true
        }
      },
      {
        "rule_id": "r2",
        "kind": "LABELS_AND_DESCRIPTIONS",
        "params": {
          "languages": ["en", "fr"],
          "include_aliases": true,
          "include_descriptions": true
        }
      },
      {
        "rule_id": "r3",
        "kind": "PROVENANCE_AND_EVIDENCE",
        "params": {
          "include_provenance": true,
          "include_evidence_refs": true,
          "include_evidence_blobs": false,
          "max_evidence_blobs": 0
        }
      }
    ]
  },

  "constraints": {
    "allow_entities": [],
    "deny_entities": [],
    "allow_properties": [],
    "deny_properties": [],

    "allow_assertions": [],
    "deny_assertions": [],

    "allow_authority_channels": [],
    "deny_authority_channels": [],

    "allow_validation_statuses": [],
    "deny_validation_statuses": [],

    "allow_recognition_statuses": [],
    "deny_recognition_statuses": [],

    "allow_certainty_levels": [],
    "deny_certainty_levels": [],

    "allow_validated_as": [],
    "deny_validated_as": [],

    "allow_domains": ["education", "wikidata"],
    "deny_domains": [],

    "allow_scopes": [],
    "deny_scopes": [],

    "include_disputed": true,
    "include_rejected": false,
    "include_revoked": false,
    "include_fictional": false,
    "include_mythological": false
  },

  "stopping": {
    "max_depth": 2,
    "max_entities": 50000,
    "max_statements": 200000,
    "max_assertions": 200000,
    "max_evidence_blobs": 0,
    "max_frontier_per_depth": 10000
  }
}
```
