# Exchange identity vectors

These vectors test the Kristal v5 core Exchange identity profile `kristal.v5:exchange-id-core@1` from `01-core-spec/ids-canonicalization-hashing.md`.


These are deliberately **Exchange payload/hash-target fixtures**, not complete Exchange Manifest instances. Manifest-only fields such as compiler/build-run metadata are outside `kristal_id`; the manifest records them separately for reproducibility and audit.

For these Exchange **payload** fixtures, the hash target is produced by:

1. removing the output `kristal_id` field;
2. removing top-level `content_hash` when it stores the digest being computed;
3. removing every field named `signatures` or `attestations`, including nested defensive-compatibility occurrences;
4. applying no other implicit exclusions;
5. canonicalizing with RFC 8785 / `kristal.v5:jcs-rfc8785@1`;
6. hashing the canonical UTF-8 bytes with SHA-256.

The vectors deliberately omit volatile operational fields. `EX-003` adds a signature envelope to the same stable payload and MUST preserve the ID. `EX-004` changes status-bearing stable content and MUST change the ID.

Run:

```bash
node tools/kristal_tck.mjs
```
