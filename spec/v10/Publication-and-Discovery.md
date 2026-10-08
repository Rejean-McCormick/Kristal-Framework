# Publication and Discovery

A `kristal_publication` is an immutable operational record that binds an exact v9 state identity and commitment to retrievable bytes on a host. Publication is distinct from activation.

## Verifiable publication baseline

For the v10 verifiable publication baseline, every `resources[]` entry MUST carry:

- a role;
- a locator;
- a media type;
- an exact byte size;
- a SHA-256 blob digest.

A content commitment alone is insufficient to identify a publication. `state_ref`, the state commitment profile/digest, the publishing node/binding, and the exact publication bundle are bound by the publication identity. Repacking or mirroring therefore does not mutate semantic state, while distinct bundles cannot silently collide.

The reference implementation defines a non-normative `kristal.publication-bundle/1.0` tool format. Its payload manifest excludes its own envelope and attestations, avoiding self-digest cycles. The Publication Record may bind that manifest by blob digest.

Publication resources may include a state snapshot, materialization manifest, exchange package, runtime pack, query index, lexicon or other derived representation. A publisher MUST verify the local bundle before upload and SHOULD verify the remotely retrieved bytes before finalizing an immutable publication. An already-finalized publication is idempotent only when the retrieved bundle verifies and its Publication Record is identical; otherwise the operation is a conflict.

Publication records MAY reference host attestations. Host attestations prove facts about build/publication execution; they do not establish epistemic authority over the knowledge itself.

A `kristal_directory` is a mutable discovery surface. It advertises nodes, bindings and optionally currently advertised states/channels. Directory entries are hints for location and routing. A directory implementation MUST treat malformed collections as validation failures rather than process exceptions and SHOULD expose stable pagination/generation metadata when paging is implemented.

```text
DIRECTORY != AUTHORITY
DISCOVERY != FEDERATION MEMBERSHIP
```

Exact semantic federation remains expressed through pinned v9 `state_snapshot.references[]`.
