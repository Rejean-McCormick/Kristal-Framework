# v11 conformance — draft.3

- **V11-Reader**: validates v11 artifact schemas, identity scope and graph referential integrity. Reads v6–v10 artifacts according to original versions.
- **V11-Lexical**: keeps words out of canonical graph fields, resolves KQ/KP presentation separately, surfaces ambiguity/missing lexemes.
- **V11-Crosswalk**: distinguishes internal vs Wikidata namespaces, validates Q↔KQ and P↔KP pairing, provenance, active exact uniqueness, candidate and superseded states.
- **V11-Dictionary-Manager (draft.2)**: catalogs every locale and ordered source/curated layer, records source snapshot and hashes, imports only accepted-exact Wikidata Q/P mappings, makes curated changes separately reviewable, rejects stale/corrupted data, and requires explicit fallbacks. This local reference profile does not certify 300-language live performance.
- **V11-diK-Coverage (draft.3)**: canonical KQ and KP inventories per graph and locale; direct vs explicit fallback vs missing vs conflicts; report digests and deterministic examples. Does not claim legacy coverage where referents remain unresolved.
- **V11-diK-Plan (draft.3)**: bounded, reviewable conversion plan, source digest/JSON Pointer verification, approved evidence refs; no silent mutation or execution.
- **V11-External-Dictionary (draft.3)**: imported third-party lexical records require source provenance, source license and reviewed identity alignment supported by KS evidence.
- **V11-Legacy-Resolver**: emits a non-mutating structured report, never silently rewrites ambiguous input or treats lexical equality as identity certainty.
- **V11-Full**: satisfies all previous version full profiles plus the five v11 profiles, including real producer/consumer integration tests. **Not claimed by the supplied draft implementation**.

The reference schema validator (`tools/v11/validate_v11.py`) and test vectors demonstrate v11 structural/reference integrity at the Framework level. They do not certify the Authoring Kit, hosted nodes, migrated Kristals or a live Wikidata installation.

Required negative TCK cases: raw Wikidata Q used as canonical KQ, text as predicate, extra language label on graph, unresolved graph endpoint, mistaken KQ/Q ↔ KP/P mapping, accepted exact without decision/evidence, duplicate active exact crosswalk, ambiguous same-language term, candidate-only Wikidata mapping, and literal text not mistaken for an identity.
