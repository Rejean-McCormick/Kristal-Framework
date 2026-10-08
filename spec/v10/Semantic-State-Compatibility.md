# Semantic State Compatibility

V10 deliberately reuses the v9 semantic-state contracts instead of inventing `10.0` variants that only rename `schema_version`.

This means the same `kristal_state_snapshot` and the same `logical_commitment` can be published through GitHub, another forge, object storage, a local filesystem, or several mirrors without semantic mutation.

V10 implementations MUST treat the following as non-semantic unless a domain contract explicitly says otherwise:

- repository owner/name;
- branch or tag;
- release ID;
- URL or API endpoint;
- workflow or job identity;
- deployment/environment ID;
- package registry locator;
- host account visibility;
- host-generated timestamps and attestations.


## Draft.2 reference hardening

Draft.2 does not change the frozen v9 schema or commitment profile identifiers. The JavaScript reference implementation removes locale-sensitive comparison from commitment normalization and rejects an unsupported declared commitment profile instead of reporting successful verification. This is treated as an implementation conformance correction, not a redefinition of published v9 contracts.

Operators that previously produced v9 commitments with a non-conforming locale-sensitive implementation MUST preserve the original bytes and identify affected objects before migration. They MUST NOT silently rewrite historical commitments to make them verify.
