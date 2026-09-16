# Runtime Pack identity and integrity vectors

These vectors define the first executable Runtime Pack identity profile for the Kristal v5 TCK:

`kristal.v5:runtime-pack-id-core@1`

Runtime Pack format version used by these core vectors is `5.0.0`; it is not coupled to the framework release-candidate suffix.

The profile applies RFC 8785 / JCS to a Runtime Pack Manifest after removing only the explicitly non-identity fields below plus all `signatures` / `attestations` fields:

- `/runtime_pack_id`
- `/created_at`
- `/build/build_id`
- `/compiler/build_platform`
- `/integrity/pack_hash`
- `/integrity/manifest_hash`

All remaining fields are identity-bearing for this profile. In particular, the source Exchange reference, source status, compiler name/version/revision, deterministic config, policies, reader-policy references, query-contract reference, and deterministic file inventory remain in the hash target.

This closes the test-vector gap required by deterministic-build rule 15.5 without making local wall-clock time or host platform part of pack identity.

The payload-integrity vectors also verify that every declared file hash and size is checked fail-closed.

This TCK does **not** yet claim byte-level conformance for Roaring encoding, membership-filter construction, Parquet row-group bytes, or a complete Runtime Pack compiler. Those require implementation adapters and/or more narrowly pinned byte-format profiles.
