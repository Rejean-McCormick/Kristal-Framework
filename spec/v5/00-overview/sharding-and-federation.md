# Sharding and Federation

## Status

Draft — Kristal v5

## Purpose

This document defines the Kristal v5 model for **sharding** and **federation**.

Sharding lets large or scoped Kristal corpora be split into smaller, independently addressable artifacts.

Federation lets multiple shards, publishers, authority channels, validation decisions, and reader policies be composed without silently merging their claims or hiding disagreement.

The goal is to support portable, offline-usable, authority-aware knowledge composition across domains, institutions, communities, research groups, companies, governments, cultural bodies, and individual publishers.

---

## Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

---

## 1. Core model

Kristal v5 separates:

* artifact existence;
* artifact integrity;
* assertion status;
* certainty level;
* validation status;
* authority recognition;
* reader visibility;
* federation composition.

A shard may contain uncertain, disputed, fictional, mythological, speculative, incomplete, or erroneous assertions.

A federation may compose such shards.

The federation layer MUST preserve the status, provenance, authority channel, certainty, scope, and lineage of the shards and assertions it composes.

A federation MUST NOT make one authority channel appear to speak for another.

A federation MUST NOT silently merge conflicting claims.

A federation MUST NOT represent an assertion as validated, recognized, or reference-level outside the authority channel, scope, certainty level, and validation policy that support that status.

---

## 2. Shards

### 2.1 Definition

A **shard** is a scoped Kristal Exchange artifact.

A shard represents a coherent subset of a larger corpus, such as:

* a domain subset;
* a jurisdictional subset;
* a time-window subset;
* a language subset;
* a tenant subset;
* a publisher subset;
* a source-dataset subset;
* a research subset;
* a fictional or mythological corpus subset;
* a reference subset recognized by an authority channel.

A shard is not merely a file split. It carries identity, scope, provenance, status, and policy metadata.

### 2.2 Shard identity

Each shard MUST have a stable content-addressed identifier.

Recommended field:

```json
{
  "shard_id": "sha256:<hex>"
}
```

A shard MAY also carry a `kristal_id` if the shard is itself a complete Kristal Exchange artifact.

If both `shard_id` and `kristal_id` are present, the schema or manifest MUST define whether they are identical or whether `shard_id` identifies the shard wrapper while `kristal_id` identifies the contained Exchange.

### 2.3 Shard status

A shard MUST declare an artifact status.

Recommended values:

* `draft`
* `working`
* `under_review`
* `recognized`
* `reference`
* `deprecated`
* `superseded`
* `revoked`

A shard with `artifact_status = "working"` MAY be useful for review, research, diagnostics, collaboration, or creative exploration.

A shard with `artifact_status = "reference"` has been recognized as a reference under one or more declared authority channels and scopes.

`reference` MUST NOT be interpreted as universal truth.

### 2.4 Shard scope

A shard MUST declare scope.

Recommended shape:

```json
{
  "scope": {
    "domain": "heritage",
    "subdomain": "unesco",
    "jurisdiction": null,
    "time_window": "2020-01-01T00:00:00Z/2025-12-31T23:59:59Z",
    "tenant_id": "tenant_demo",
    "environment": "prod",
    "language": "en"
  }
}
```

`scope.domain` is REQUIRED.

Recommended domain values include:

* `general`
* `wikidata`
* `science`
* `health`
* `education`
* `heritage`
* `law`
* `policy`
* `technology`
* `environment`
* `culture`
* `mythology`
* `fiction`
* `research`
* `operations`
* `civic`
* `local_notes`

Implementations MAY extend the domain list if the extension is declared by profile or policy.

### 2.5 Shard provenance

A shard SHOULD preserve:

* source snapshot references;
* structured epistemic state references;
* dataset references;
* prior shard references;
* prior Exchange references;
* publisher identity;
* compiler identity;
* build configuration hash;
* validation decision references;
* authority recognition references;
* lineage.

A shard SHOULD NOT erase source identity when it is republished, copied, forked, transformed, or federated.

---

## 3. Federation

### 3.1 Definition

A **federation** is a deterministic composition of multiple Kristal shards, Exchanges, datasets, or references under an explicit composition policy.

A federation can present a unified query or navigation surface while preserving:

* who published each shard;
* who validated or recognized it;
* which authority channel applies;
* which scope applies;
* which reader policy is active;
* which claims are disputed;
* which claims conflict;
* which claims are excluded by policy;
* which claims remain visible only under broader views.

### 3.2 Federation is not silent merging

Federation MUST preserve source identities.

Federation MUST NOT rewrite shard identities.

Federation MUST NOT silently merge conflicting claims.

Federation MUST NOT treat recognition by one authority channel as recognition by another.

Federation MUST NOT hide that a reader policy filtered out disputed, fictional, mythological, rejected, revoked, or unrecognized material.

### 3.3 Federation can expose multiple views

A federation MAY expose multiple reader-policy views over the same composed corpus.

Examples:

* `reference_only`
* `validated_only`
* `high_certainty_only`
* `research`
* `creative`
* `all_with_labels`
* `custom`

Each view MUST declare which authority channels, validation statuses, certainty levels, scopes, and validated-as modes are included.

---

## 4. Federation Manifest

### 4.1 Purpose

A Federation Manifest describes the composition of shards and the policy used to interpret them.

Recommended artifact type:

```json
{
  "artifact_type": "exchange_federation_manifest"
}
```

### 4.2 Required fields

A Kristal v5 Federation Manifest SHOULD contain:

```json
{
  "schema_version": "5.0",
  "artifact_type": "exchange_federation_manifest",
  "federation_id": "sha256:<hex>",
  "created_at": "RFC3339",
  "artifact_status": "working|under_review|recognized|reference|deprecated|revoked",
  "scope": {},
  "authority_registry_ref": {},
  "shards": [],
  "composition_policy": {},
  "reader_policy_refs": [],
  "validation_refs": [],
  "authority_recognition_refs": [],
  "publisher": {},
  "content_hash": {},
  "signatures": [],
  "extensions": {}
}
```

### 4.3 Federation identity

A federation MUST have a stable identifier.

Recommended field:

```json
{
  "federation_id": "sha256:<hex>"
}
```

The hash target for `federation_id` MUST be defined by the applicable canonicalization and hashing rules.

The signatures array MUST NOT be included in the signed payload hash unless an explicit profile says otherwise.

Timestamp fields such as `created_at` MUST NOT affect content-addressed identifiers unless an explicit profile declares them part of the identity surface.

---

## 5. Shard references

A federation manifest contains shard references.

Recommended shape:

```json
{
  "shard_id": "sha256:<hex>",
  "artifact_type": "exchange_shard_manifest",
  "manifest_hash": {
    "alg": "sha256",
    "value": "<hex>"
  },
  "uri": "konnaxion://shards/<id>.json",
  "required": true,
  "scope": {
    "domain": "heritage",
    "subdomain": "unesco",
    "jurisdiction": null,
    "time_window": "2020-01-01T00:00:00Z/2025-12-31T23:59:59Z",
    "tenant_id": "tenant_demo",
    "environment": "prod",
    "language": "en"
  },
  "authority_channel": "authority:unesco-heritage",
  "artifact_status": "reference",
  "validation_refs": [],
  "authority_recognition_refs": []
}
```

### 5.1 Required versus optional shards

A shard reference SHOULD declare whether the shard is required.

If a required shard is unavailable, corrupted, revoked, or not accepted by policy, the federation view MUST report that the composed view is incomplete or unavailable under that policy.

If an optional shard is unavailable, the federation MAY still produce a view, provided the result clearly indicates that optional material was unavailable or excluded.

### 5.2 Shard order

Shard order MUST be deterministic.

Shard ordering MAY be based on:

* explicit order in the manifest;
* stable lexical order by `shard_id`;
* authority precedence;
* scope precedence;
* time-window precedence;
* declared composition policy.

The active ordering rule MUST be declared.

---

## 6. Composition policy

### 6.1 Purpose

The composition policy defines how a federation handles overlap, conflict, visibility, ordering, and authority selection.

Recommended shape:

```json
{
  "policy_id": "kristal.v5:composition-policy:<slug>",
  "policy_version": "1",
  "overlap_strategy": "authority_precedence",
  "conflict_strategy": "preserve_disagreement",
  "default_visibility": "reader_policy",
  "ordering": "stable",
  "parameters": {}
}
```

### 6.2 Overlap strategies

Recommended `overlap_strategy` values:

* `authority_precedence`
* `latest_time_window`
* `explicit_allow_deny`
* `preserve_all`
* `reader_policy_selected`

### 6.3 Conflict strategies

Recommended `conflict_strategy` values:

* `preserve_disagreement`
* `authority_precedence`
* `mark_disputed`
* `exclude_conflict`
* `require_reader_choice`

Default Kristal v5 behavior SHOULD be:

```text
conflict_strategy = "preserve_disagreement"
```

### 6.4 Preserve disagreement

When `conflict_strategy = "preserve_disagreement"`, the federation MUST:

* retain all conflicting assertions that are visible under the active reader policy;
* preserve source shard identity for each assertion;
* preserve authority channel identity for each assertion;
* preserve validation and recognition status;
* mark the conflict in the result surface or conflict index;
* allow downstream readers or interfaces to display the disagreement.

### 6.5 Authority precedence

When `overlap_strategy` or `conflict_strategy` uses authority precedence, the manifest MUST declare the relevant authority order or authority-selection rule.

Authority precedence MUST be scoped.

Example:

```json
{
  "authority_precedence": [
    {
      "scope": {
        "domain": "health"
      },
      "order": [
        "authority:who",
        "authority:national-health-agency",
        "authority:local-clinic"
      ]
    }
  ]
}
```

Authority precedence in one scope MUST NOT imply precedence in another scope.

### 6.6 Reader-policy-selected composition

When composition depends on reader policy, the result MUST expose or record the active reader policy.

A query or rendered view SHOULD make clear that results are policy-filtered.

---

## 7. Authority Registry

### 7.1 Purpose

An Authority Registry records authority channels, trust roots, validation policies, recognition policies, revocation references, and scope-bound rules.

The registry does not create universal truth. It declares which authorities are recognized for which scopes and under which policies.

### 7.2 Authority channel

Recommended authority channel shape:

```json
{
  "authority_channel_id": "authority:<slug>",
  "name": "string",
  "authority_type": "institution|government|association|company|research_collective|individual|ai_validator|community|standards_body|intergovernmental_organization|hybrid_collective",
  "scope": {},
  "recognized_by": [],
  "trust_roots": [],
  "validation_policies": [],
  "revocation_policy_ref": null
}
```

### 7.3 Authority recognition

Authority channels MAY recognize other authority channels.

Examples:

* an international organization recognizes a health authority for public-health reference material;
* a government recognizes a national statistics agency for demographic datasets;
* a standards body recognizes a technical working group for a technical specification;
* a company is recognized as the primary authority for its own declared system architecture.

Recognition MUST be explicit and scoped.

Recognition by one authority channel MUST NOT imply recognition by another.

### 7.4 Registry references

A federation manifest SHOULD reference an Authority Registry.

Recommended shape:

```json
{
  "authority_registry_ref": {
    "registry_id": "kristal:authority-registry:sha256:<hex>",
    "registry_hash": {
      "alg": "sha256",
      "value": "<hex>"
    },
    "uri": "konnaxion://authority-registries/<id>.json"
  }
}
```

Implementations MAY support registry identifiers in more than one form, such as:

* `sha256:<hex>`
* `kristal:authority-registry:sha256:<hex>`

The accepted forms MUST be documented.

---

## 8. Validation and recognition in federations

### 8.1 Validation is scoped

A validation decision MUST declare:

* target;
* target level;
* validation status;
* validated-as mode;
* certainty level where applicable;
* authority channel;
* validation policy reference;
* scope;
* findings or reason codes;
* timestamp;
* signatures where required.

A federation MUST NOT collapse validation decisions into a single boolean.

Invalid:

```json
{
  "validated": true
}
```

Recommended pattern:

```json
{
  "validation_status": "validated",
  "validated_as": "institutional_reference",
  "certainty_level": "high",
  "authority_channel": "authority:unesco-heritage",
  "validation_policy_ref": "policy:unesco-heritage-reference-validation@1",
  "scope": {
    "domain": "heritage",
    "subdomain": "unesco"
  }
}
```

### 8.2 Recognition is scoped

Authority recognition records whether an authority channel recognizes a target.

Targets MAY include:

* assertion;
* shard;
* Exchange;
* Runtime Pack;
* dataset;
* federation;
* authority channel;
* validation policy;
* reader policy.

Recognition MUST be scoped.

Recognition MUST NOT be inherited by a fork unless the recognizing authority explicitly recognizes the fork.

### 8.3 Federation-level recognition

A federation itself MAY be recognized as a reference artifact.

Federation-level recognition means that the federation manifest, composition policy, selected shards, reader policies, and authority assumptions are recognized under the declared scope.

It does not automatically mean that every assertion in every shard has maximum certainty.

---

## 9. Reader policies

### 9.1 Purpose

Reader policies determine which material is visible in a view.

They can be used by Runtime Packs, query wrappers, Konnaxion surfaces, Architect renderers, institutional deployments, research tools, or creative tools.

### 9.2 Recommended reader modes

Recommended reader modes:

* `reference_only`
* `validated_only`
* `high_certainty_only`
* `research`
* `creative`
* `all_with_labels`
* `custom`

### 9.3 Reader policy shape

Recommended shape:

```json
{
  "reader_policy_id": "reader_policy:<slug>",
  "mode": "validated_only",
  "allowed_authority_channels": [],
  "allowed_validation_statuses": [],
  "allowed_certainty_levels": [],
  "allowed_validated_as": [],
  "include_disputed": false,
  "include_fictional": false,
  "include_mythological": false,
  "show_labels": true,
  "fallback_behavior": "show_unavailable"
}
```

### 9.4 Validated-only view

A `validated_only` view means all visible assertions satisfy the active reader policy.

It does not mean:

* all assertions have maximum certainty;
* all assertions are physical-world facts;
* all authorities agree;
* all claims are universally true.

A validated-only view may include assertions validated as:

* hypotheses;
* sourced claims;
* institutional references;
* publisher declarations;
* technical specifications;
* legal or policy positions;
* mythological corpora;
* fictional corpora;
* disputed positions.

The validated-as mode, authority channel, certainty level, and scope MUST remain visible or recoverable.

---

## 10. Query behavior

Federation-aware query systems MUST preserve the distinction between:

* source shard;
* assertion status;
* certainty level;
* validation status;
* validated-as mode;
* authority channel;
* recognition status;
* scope;
* reader policy;
* conflict status.

A federation-aware query system SHOULD support filters for:

* `artifact_status`
* `assertion_status`
* `certainty_level`
* `validation_status`
* `validated_as`
* `authority_channel`
* `recognition_status`
* `scope.domain`
* `scope.subdomain`
* `scope.jurisdiction`
* `scope.language`
* `source_shard`
* `reader_policy`
* `include_disputed`
* `include_fictional`
* `include_mythological`
* `show_disagreement`

If query results are filtered by reader policy, responses SHOULD expose the active reader policy.

---

## 11. Integrity and offline behavior

### 11.1 Local verification

A federation may be used offline if all required manifests, shards, registries, policies, revocation records, and Runtime Packs needed by the active reader policy are locally available.

Implementations SHOULD verify:

* shard hashes;
* federation manifest hash;
* registry hash;
* policy hashes;
* signatures required by the active policy;
* revocation status where available;
* schema conformance.

### 11.2 Required verification

If a channel, reader policy, release policy, or activation policy requires a verification step, that step MUST be completed before the artifact is represented as trusted, recognized, reference-level, released, or active for that channel.

If a candidate shard or federation cannot satisfy the active policy, the implementation MUST preserve the current accepted view or clearly mark the candidate as unavailable, unrecognized, incomplete, or rejected under that policy.

This requirement does not prevent the candidate from being inspected in diagnostic, review, research, or creative contexts when policy allows it.

### 11.3 Revocation-aware behavior

Federation-aware systems SHOULD support revocation lists or revocation records.

If a shard, signing key, authority channel, recognition record, validation decision, or federation manifest is revoked under the active policy, the system MUST NOT present it as accepted for that policy.

The system MAY preserve it for audit, lineage, dispute review, or historical analysis if policy allows.

---

## 12. Forks and divergence

### 12.1 Forks are allowed

Kristal v5 allows forks.

A fork may be created by:

* a researcher;
* a community;
* a government;
* an association;
* a company;
* an expert group;
* a cultural institution;
* a religious or mythological community;
* a creative project;
* an individual.

Forking a shard or federation MUST preserve lineage.

### 12.2 Fork metadata

A fork SHOULD declare:

* source artifact reference;
* fork reason;
* publisher;
* authority channel;
* scope;
* validation status;
* recognition status;
* reader policies;
* conflict relationship to the source.

### 12.3 Recognition does not automatically transfer

A fork MUST NOT inherit recognition from the source artifact unless the recognizing authority explicitly recognizes the fork.

A fork MAY be valid under one authority channel and rejected, ignored, disputed, or excluded by another.

### 12.4 Divergent claims

Divergent claims MAY be represented if they preserve labels and authority.

Examples:

* a scientific reference shard and a fringe-position shard may coexist;
* a government policy shard and an activist critique shard may coexist;
* a mythology shard may be recognized as mythology;
* a fictional shard may be recognized as fiction;
* a company may publish a system-description shard while regulators publish safety or compliance shards.

Federation preserves these distinctions.

---

## 13. Examples

### 13.1 Heritage federation

A heritage federation may compose:

* a UNESCO heritage reference shard;
* national heritage datasets;
* local cultural inventories;
* disputed or pending nominations;
* language-specific label shards;
* historical revision shards.

A strict reader policy may show only material recognized by the UNESCO heritage authority channel.

A research reader policy may also show disputed, pending, or locally asserted material with labels.

### 13.2 Wikidata seed federation

A Wikidata Seed Kristal may be sharded by:

* entity ranges;
* property groups;
* language labels;
* statement type;
* domain;
* dump timestamp;
* source namespace.

The seed SHOULD preserve full statement structure where possible, including:

* entities;
* properties;
* statements;
* qualifiers;
* references;
* ranks;
* labels;
* aliases;
* descriptions.

A query layer may expose a best-rank or truthy-like projection, but the source federation SHOULD preserve the richer structure when available.

### 13.3 Medical authority federation

A health federation may compose:

* WHO-recognized guidance;
* national agency guidance;
* hospital policy;
* research evidence bundles;
* deprecated or revoked guidance;
* disputed recommendations.

A reader policy for clinical reference use may exclude drafts and disputed material.

A research policy may include lower-certainty material with clear labels.

### 13.4 Fiction and mythology federation

A mythology federation may be recognized as cultural or mythological material.

A fiction federation may be recognized as a fictional corpus.

Such recognition MUST NOT imply validation as physical-world fact.

---

## 14. Conformance

An implementation supporting Kristal v5 sharding and federation MUST:

* preserve shard identity;
* preserve source lineage;
* preserve publisher identity;
* preserve scope;
* preserve authority-channel metadata;
* preserve validation and recognition references;
* preserve assertion status and certainty metadata when present;
* implement deterministic composition policies;
* expose or record reader-policy filtering;
* avoid silent merging of conflicting claims;
* avoid presenting scoped recognition as universal recognition;
* verify required integrity material before representing artifacts as trusted under a policy;
* support revocation-aware behavior when revocation records are declared by policy;
* distinguish working artifacts from reference artifacts;
* support offline composition when all required local material is available.

---

## 15. Minimal mental model

A shard answers:

> “What does this scoped artifact assert, and under which provenance, status, and authority context?”

A federation answers:

> “How do multiple scoped artifacts coexist under an explicit composition policy?”

An authority channel answers:

> “Who recognizes what, under which rules, for which scope?”

A reader policy answers:

> “Which parts of this composed knowledge surface are visible right now?”

The core Kristal v5 rule is:

> Federation preserves disagreement without silent merging.
