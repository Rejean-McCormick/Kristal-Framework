# Migration from v7 to v8

Migration is optional because v8 is additive.

A valid v7 Kristall may be used unchanged by a v8 processor. Recommended adoption steps are:

1. keep v7 registries and Mesh unchanged;
2. declare v8 capability metadata;
3. create external lexical Kristals for desired languages/domains;
4. create a deterministic lexical stack policy;
5. build rebuildable query indexes from canonical artifacts;
6. expose typed KQP query with pagination/completeness;
7. add AI context compilation and optional compact encoding;
8. add semantic fingerprint profiles only where they provide value.

Existing v7 labels MAY seed a lexical worklist or fallback lexicon. Their extraction is a convenience operation, not a semantic migration.

## No forced rewrite

Do not convert every v7 label into a language artifact before using v8. Do not mint new semantic IDs for existing v7 identities. Do not replace inherited hashes with v8 semantic fingerprints.

## Production adoption

Deployments SHOULD introduce derived indexes and AI query paths as read-side capabilities first. Canonical mutation/admission workflows remain governed by existing source contracts until explicitly upgraded under a separate write protocol.
