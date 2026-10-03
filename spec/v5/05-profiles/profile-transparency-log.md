# Profile: Transparency Log (Kristal v5)

## Status

Optional standardized profile — Kristal v5.

## Purpose

This profile defines a transparency log pattern for Kristal v5 artifacts, validation decisions, authority recognitions, revocations, Runtime Pack releases, and trust-root changes.

A transparency log provides an append-oriented audit surface that makes it possible to inspect:

* what was published;
* who signed or recognized it;
* under which authority channel;
* under which scope;
* under which validation or recognition policy;
* when it was recorded;
* whether it was later superseded, revoked, disputed, or deprecated.

This profile does **not** create a universal truth authority.

A transparency log records events and signed statements. It does not, by itself, prove that every logged assertion is true, high-certainty, globally recognized, or visible under every reader policy.

---

## Scope

This profile specifies:

* transparency log entry structure;
* event types;
* append-only sequencing;
* hash-chain requirements;
* signature requirements;
* authority-channel linkage;
* validation and recognition event linkage;
* revocation and correction linkage;
* Runtime Pack release linkage;
* query and audit expectations;
* offline verification expectations.

This profile does not specify:

* a single network transport;
* a required storage backend;
* a global log operator;
* governance rules for every authority channel;
* semantic validation of claims;
* reader-policy inclusion rules.

---

## Normative keywords

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

---

# 1. Conformance

An implementation claims this profile by declaring the following profile identifier:

```text
kristal.v5:profile-transparency-log@1
```

A conformant transparency log MUST provide:

* append-oriented log entries;
* stable entry identifiers;
* deterministic entry hashing;
* monotonic sequence numbers within a log;
* previous-entry linkage;
* signed log checkpoints or signed entries;
* event type classification;
* target artifact references;
* authority-channel references when applicable;
* scope references when applicable;
* revocation or supersession linkage when applicable.

A Runtime Pack, Authority Registry, Exchange, Federation Manifest, Validation Decision, or Authority Recognition MAY reference one or more transparency logs.

---

# 2. Conceptual model

A transparency log records claims about artifact events.

Examples:

```text
artifact X was published
artifact X was signed by key Y
artifact X was recognized by authority channel Z
assertion A was validated as a hypothesis
runtime pack P was released to channel C
key K was revoked
authority channel Y delegated scope S to authority channel Z
```

A transparency log entry is not the same thing as the target artifact.

A transparency log entry records an event about a target.

The target remains governed by its own schema, signatures, content hash, authority channel, validation status, certainty level, and reader policy.

---

# 3. Design goals

Transparency logs in Kristal v5 support:

* auditability;
* compromise detection;
* release traceability;
* validation traceability;
* authority-recognition traceability;
* offline verification;
* public accountability where desired;
* correction and revocation visibility;
* federation without hidden authority laundering.

Transparency logs SHOULD make it difficult to silently rewrite the history of published artifacts, recognition decisions, revocations, or releases.

---

# 4. Log identity

A transparency log MUST have a stable `log_id`.

Recommended shape:

```json
{
  "log_id": "kristal:transparency-log:sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "schema_version": "5.0",
  "profile": "kristal.v5:profile-transparency-log@1"
}
```

A log SHOULD declare:

* operator identity;
* authority channel, if operated by an authority;
* scope;
* trust roots;
* signing policy;
* retention policy;
* public or private visibility status;
* checkpoint policy.

---

# 5. Entry identity

Each transparency log entry MUST have a stable `entry_id`.

Recommended shape:

```text
sha256:<64 lowercase hex characters>
```

The `entry_id` MUST be derived from the canonicalized log entry hash target.

The entry hash target MUST exclude signatures.

The entry hash target SHOULD exclude `entry_id` itself.

Hashing MUST use:

```text
canonicalization_profile = "kristal.v5:jcs-rfc8785"
canonicalization_version = "1"
hash_alg = "sha256"
```

---

# 6. Entry structure

A conformant transparency log entry SHOULD use the following structure:

```json
{
  "schema_version": "5.0",
  "artifact_type": "transparency_log_entry",
  "profile": "kristal.v5:profile-transparency-log@1",
  "log_id": "kristal:transparency-log:sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "entry_id": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "sequence": 1,
  "created_at": "2026-01-01T00:00:00Z",
  "event_type": "artifact_published",
  "target_ref": {
    "artifact_type": "reference_exchange",
    "artifact_id": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    "content_hash": {
      "alg": "sha256",
      "value": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    }
  },
  "target_level": "artifact",
  "issuer": {
    "authority_channel_id": "authority:example",
    "key_id": "key:example"
  },
  "scope": {
    "domain": "science"
  },
  "policy_refs": [],
  "previous_entry_id": null,
  "entry_hash": {
    "alg": "sha256",
    "value": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
  },
  "signatures": [],
  "extensions": {}
}
```

---

# 7. Required entry fields

A transparency log entry MUST include:

* `schema_version`;
* `artifact_type`;
* `profile`;
* `log_id`;
* `entry_id`;
* `sequence`;
* `created_at`;
* `event_type`;
* `target_ref`;
* `target_level`;
* `entry_hash`.

It SHOULD include:

* `issuer`;
* `scope`;
* `policy_refs`;
* `previous_entry_id`;
* `signatures`.

If the event involves validation, recognition, authority, release, revocation, or delegation, the entry MUST include enough references to identify the relevant authority channel and policy.

---

# 8. Event types

Allowed `event_type` values SHOULD include:

```text
artifact_submitted
artifact_compiled
artifact_published
artifact_deprecated
artifact_superseded
artifact_revoked
validation_decision_recorded
validation_decision_revoked
authority_recognition_recorded
authority_recognition_revoked
authority_channel_registered
authority_channel_deprecated
authority_channel_revoked
authority_delegation_recorded
authority_delegation_revoked
runtime_pack_built
runtime_pack_released
runtime_pack_activated
runtime_pack_revoked
reader_policy_registered
reader_policy_deprecated
trust_root_added
trust_root_deprecated
trust_root_blocked
revocation_list_published
federation_manifest_published
correction_recorded
dispute_recorded
checkpoint_published
```

Implementations MAY define additional event types through profile extensions.

Extension event types MUST be namespaced or otherwise clearly distinguishable from core event types.

---

# 9. Target levels

Allowed `target_level` values SHOULD include:

```text
artifact
shard
assertion
authority_channel
dataset
runtime_pack
validation_decision
authority_recognition
reader_policy
trust_root
revocation_list
federation_manifest
release
checkpoint
```

Rules:

* `target_level = assertion` MUST include a target reference to the assertion ID or containing artifact and assertion path.
* `target_level = runtime_pack` MUST include the Runtime Pack ID.
* `target_level = authority_channel` MUST include the authority channel ID.
* `target_level = validation_decision` MUST include the validation decision ID.
* `target_level = authority_recognition` MUST include the recognition ID.

---

# 10. Append-only sequencing

Within a log, entries MUST have monotonic sequence numbers.

Sequence numbers MUST NOT be reused.

If an entry is invalid, corrected, superseded, or revoked, the log MUST NOT mutate or delete the prior entry. It SHOULD append a new entry recording the correction, supersession, or revocation.

A transparency log MAY be segmented into epochs, shards, or checkpoints. If segmented, the segment identity and ordering rules MUST be declared.

---

# 11. Hash-chain linkage

A transparency log SHOULD provide hash-chain linkage.

Each entry SHOULD include:

```json
{
  "previous_entry_id": "sha256:<previous-entry-id-or-null>"
}
```

The first entry in a log or segment SHOULD use:

```json
{
  "previous_entry_id": null
}
```

If the log is sharded or checkpointed, each shard or checkpoint MUST declare how previous-entry linkage is preserved or summarized.

Implementations SHOULD provide a way to verify that no entries are missing between two known sequence numbers or checkpoints.

---

# 12. Checkpoints

A transparency log MAY publish checkpoints.

A checkpoint summarizes a known log state.

Recommended checkpoint structure:

```json
{
  "schema_version": "5.0",
  "artifact_type": "transparency_log_checkpoint",
  "profile": "kristal.v5:profile-transparency-log@1",
  "log_id": "kristal:transparency-log:sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "checkpoint_id": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
  "created_at": "2026-01-01T00:00:00Z",
  "sequence_min": 1,
  "sequence_max": 1000,
  "entry_count": 1000,
  "root_hash": {
    "alg": "sha256",
    "value": "1111111111111111111111111111111111111111111111111111111111111111"
  },
  "previous_checkpoint_id": null,
  "signatures": []
}
```

A checkpoint SHOULD be signed.

A checkpoint MAY use:

* linear hash-chain root;
* Merkle root;
* shard root;
* implementation-specific accumulator root.

The accumulator method MUST be declared.

---

# 13. Signatures

A transparency log MAY sign each entry individually.

A transparency log SHOULD sign checkpoints.

A transparency log operated by an authority channel MUST declare the signing authority or signing policy.

Signatures MUST use the common Kristal v5 signature semantics:

```json
{
  "key_id": "key:example",
  "alg": "ed25519",
  "payload_hash": {
    "alg": "sha256",
    "value": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "signature": "base64url-or-multibase-signature",
  "created_at": "2026-01-01T00:00:00Z"
}
```

A signature over a log entry proves that the signer signed that log entry.

It does not prove that the target artifact is universally true, globally validated, or recognized by every authority channel.

---

# 14. Authority-channel linkage

If a log entry records an authority action, it MUST identify the authority channel.

Examples of authority actions include:

* validation decision recorded;
* authority recognition recorded;
* authority delegation recorded;
* trust root added;
* revocation list published;
* reference artifact accepted;
* runtime pack released by authority channel.

Recommended shape:

```json
{
  "issuer": {
    "authority_channel_id": "authority:example",
    "key_id": "key:example"
  }
}
```

Recognition by one authority channel MUST NOT be represented as recognition by another authority channel unless the second authority explicitly records or delegates that recognition.

---

# 15. Validation decision linkage

A `validation_decision_recorded` event SHOULD reference a Validation Decision artifact.

Recommended target:

```json
{
  "event_type": "validation_decision_recorded",
  "target_level": "validation_decision",
  "target_ref": {
    "validation_decision_id": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "target_ref": {
      "artifact_id": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    }
  }
}
```

The log entry SHOULD preserve or reference:

* validation status;
* `validated_as`;
* certainty level;
* authority channel;
* validation policy;
* scope;
* target level.

A transparency log MUST NOT flatten scoped validation into universal truth.

---

# 16. Authority recognition linkage

An `authority_recognition_recorded` event SHOULD reference an Authority Recognition artifact.

The log entry SHOULD preserve or reference:

* issuer authority channel;
* target reference;
* target level;
* recognition status;
* recognized-as status;
* scope;
* policy references;
* evidence references.

Recognition MUST remain scoped.

Recognition by one authority channel MUST NOT imply recognition by another.

---

# 17. Runtime Pack release linkage

A `runtime_pack_released` event SHOULD reference:

* Runtime Pack ID;
* Runtime Pack manifest hash;
* source Exchange reference;
* source artifact status;
* release channel;
* pack version;
* reader policy references;
* authority registry reference;
* release record reference;
* signer key ID;
* timestamp.

Recommended shape:

```json
{
  "event_type": "runtime_pack_released",
  "target_level": "runtime_pack",
  "target_ref": {
    "runtime_pack_id": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "source_exchange_ref": {
      "artifact_id": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    },
    "source_artifact_status": "reference",
    "pack_version": "5.0.0"
  },
  "release": {
    "channel_id": "channel:prod",
    "reader_policy_refs": ["reader_policy:validated-only"],
    "authority_registry_ref": {
      "registry_id": "kristal:authority-registry:sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    }
  }
}
```

A Runtime Pack release entry MUST NOT imply that the pack is valid for every channel or reader policy.

---

# 18. Revocation linkage

A revocation event SHOULD identify:

* revoked target;
* revocation issuer;
* effective timestamp;
* revocation reason;
* affected authority channel;
* affected scope;
* policy reference;
* replacement target, if any.

Recommended reason codes:

```text
key_compromise
artifact_corruption
manifest_invalid
payload_hash_mismatch
signature_invalid
authority_channel_revoked
validation_decision_revoked
recognition_revoked
policy_withdrawn
scope_error
publisher_error
evidence_retracted
superseded_by_replacement
```

Revocation does not necessarily delete historical records.

It changes current trust, recognition, validation, release, or activation status under a declared policy.

---

# 19. Corrections and disputes

A correction event records that a previous artifact, decision, entry, or assertion has been corrected.

A dispute event records that an authority channel, reviewer, user group, or process contests a prior assertion, validation decision, recognition, or publication.

Correction and dispute entries SHOULD include:

* target reference;
* prior entry reference;
* issuer;
* reason;
* scope;
* policy reference;
* replacement reference, if any.

A dispute entry does not automatically revoke the target. It records contestation.

Reader policies decide how disputes affect visibility.

---

# 20. Offline verification

A transparency log SHOULD support offline verification.

Offline verification may use:

* signed checkpoints;
* bundled log entry ranges;
* Merkle proofs;
* hash-chain proofs;
* signed release bundles;
* Authority Registry references.

A Runtime Pack MAY include a transparency log subset sufficient to verify its release history, validation decisions, recognition decisions, or revocation status.

If an active policy requires transparency-log verification and the required log data is unavailable, the implementation MUST NOT represent the target as accepted under that policy.

It MAY still expose the target as unavailable, unverified, diagnostic, or untrusted material depending on reader policy.

---

# 21. Query expectations

A transparency log SHOULD be queryable by:

* `log_id`;
* `entry_id`;
* `sequence`;
* `event_type`;
* `target_level`;
* `target_ref`;
* `authority_channel_id`;
* `scope.domain`;
* `validation_status`;
* `recognition_status`;
* `runtime_pack_id`;
* `release channel`;
* `created_at`;
* `revocation reason`.

Query responses MUST preserve authority, scope, and status labels when those labels exist.

A query response MUST NOT imply universal truth from log presence alone.

---

# 22. Privacy and access control

Transparency logs may be public, private, tenant-scoped, authority-scoped, or deployment-scoped.

A private or restricted transparency log SHOULD still provide auditability to authorized verifiers.

If logs contain sensitive metadata, implementations SHOULD minimize exposure while preserving verifiability.

Possible strategies include:

* redacted entries;
* hashed target references;
* scoped access;
* encrypted payloads with public hashes;
* split public/private logs;
* aggregate checkpoints.

Privacy controls MUST NOT allow silent mutation of already-audited public claims.

---

# 23. Retention

Transparency log retention policy SHOULD be explicit.

Retention policy SHOULD declare:

* how long entries are retained;
* whether old checkpoints remain available;
* whether old entries may be archived;
* how archived entries are verified;
* whether revocation and correction entries remain available indefinitely.

If entries are removed from online service but remain part of a signed historical checkpoint, the system SHOULD provide a way to distinguish:

* missing data;
* archived data;
* intentionally redacted data;
* unavailable data;
* invalid data.

---

# 24. Federation

A federation may reference multiple transparency logs.

Federated logs MUST preserve:

* log identity;
* authority-channel boundaries;
* target references;
* event scope;
* event status;
* sequence or checkpoint verification.

Federation MUST NOT silently merge events from different authority channels as though they were issued by one authority.

If two transparency logs disagree, the federation layer SHOULD preserve the disagreement or apply an explicit composition policy.

---

# 25. Example: Authority recognition entry

```json
{
  "schema_version": "5.0",
  "artifact_type": "transparency_log_entry",
  "profile": "kristal.v5:profile-transparency-log@1",
  "log_id": "kristal:transparency-log:sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "entry_id": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "sequence": 42,
  "created_at": "2026-01-01T00:00:00Z",
  "event_type": "authority_recognition_recorded",
  "target_level": "authority_recognition",
  "target_ref": {
    "recognition_id": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    "target_ref": {
      "artifact_id": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    }
  },
  "issuer": {
    "authority_channel_id": "authority:unesco-global-reference",
    "key_id": "key:unesco-example"
  },
  "scope": {
    "domain": "education",
    "jurisdiction": "global"
  },
  "policy_refs": [
    {
      "policy_id": "kristal.v5:recognition-policy:global-education-reference"
    }
  ],
  "previous_entry_id": "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "entry_hash": {
    "alg": "sha256",
    "value": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
  },
  "signatures": [
    {
      "key_id": "key:unesco-example",
      "alg": "ed25519",
      "payload_hash": {
        "alg": "sha256",
        "value": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
      },
      "signature": "base64url-or-multibase-signature",
      "created_at": "2026-01-01T00:00:01Z"
    }
  ],
  "extensions": {}
}
```

---

# 26. Example: Runtime Pack release entry

```json
{
  "schema_version": "5.0",
  "artifact_type": "transparency_log_entry",
  "profile": "kristal.v5:profile-transparency-log@1",
  "log_id": "kristal:transparency-log:sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "entry_id": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "sequence": 87,
  "created_at": "2026-01-01T00:00:00Z",
  "event_type": "runtime_pack_released",
  "target_level": "runtime_pack",
  "target_ref": {
    "runtime_pack_id": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
    "source_exchange_ref": {
      "artifact_id": "sha256:4444444444444444444444444444444444444444444444444444444444444444"
    },
    "source_artifact_status": "reference",
    "pack_version": "5.0.0"
  },
  "issuer": {
    "authority_channel_id": "authority:wikidata-seed",
    "key_id": "key:wikidata-seed-release"
  },
  "scope": {
    "domain": "wikidata"
  },
  "release": {
    "channel_id": "channel:public-reference",
    "reader_policy_refs": ["reader_policy:validated-only"],
    "authority_registry_ref": {
      "registry_id": "kristal:authority-registry:sha256:5555555555555555555555555555555555555555555555555555555555555555"
    }
  },
  "previous_entry_id": "sha256:6666666666666666666666666666666666666666666666666666666666666666",
  "entry_hash": {
    "alg": "sha256",
    "value": "7777777777777777777777777777777777777777777777777777777777777777"
  },
  "signatures": [
    {
      "key_id": "key:wikidata-seed-release",
      "alg": "ed25519",
      "payload_hash": {
        "alg": "sha256",
        "value": "7777777777777777777777777777777777777777777777777777777777777777"
      },
      "signature": "base64url-or-multibase-signature",
      "created_at": "2026-01-01T00:00:01Z"
    }
  ],
  "extensions": {}
}
```

---

# 27. Nonconformance

A transparency log implementation is nonconforming if it:

* mutates previous entries without preserving an audit trail;
* reuses sequence numbers;
* omits target references;
* omits authority channel references for authority events;
* represents log inclusion as universal truth;
* represents one authority’s recognition as another’s recognition;
* hides revocation or correction events required by active policy;
* uses ambiguous signing targets;
* includes signatures in entry hashes without a declared profile;
* fails to preserve scope;
* fails to distinguish validation from recognition;
* fails to distinguish certainty from validation.

---

# 28. Summary

A Kristal v5 transparency log records auditable events about artifacts, validation decisions, authority recognitions, revocations, releases, trust roots, and corrections.

It does not create a universal truth layer.

The core rules are:

```text
Log entries are append-oriented.
Entry identity is content-addressed.
Checkpoints should be signed.
Authority is scoped.
Recognition is scoped.
Validation is scoped.
Revocation changes current trust status.
Corrections do not erase history.
Reader policies decide visibility.
Log inclusion does not equal truth.
```

Transparency logs make Kristal ecosystems more inspectable, accountable, and resilient without collapsing plural authority into a single truth monopoly.
