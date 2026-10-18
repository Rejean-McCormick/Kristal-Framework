# Kristal v11 Core Specification

Version `11.0.0-draft.4` (normative rules unchanged from draft.3). Draft profile `kristal.semantic-identity/11.0`.

## Normative principle

**SEMANTIC IDENTITY != LEXICAL LABEL != EXTERNAL IDENTIFIER**

A conforming new canonical *v11 semantic graph* MUST use a namespace-scoped opaque `KQ` item/entity, `KP` property, `KA` assertion and `KS` source identifiers in their structural roles. A label, natural-language predicate, legacy URN, Wikidata `Q` or `P`, or a generated English/French slug MUST NOT be an identity in a v11 canonical graph. A string-valued, typed **literal datum** is permitted as the *object value* of a property, but MUST NOT serve as a subject, predicate, source or identity key.

The profile introduces additive artifacts:

- `kristal_identity_registry`: issued identities, scoped by `namespace_id`, without canonical labels;
- `kristal_semantic_graph`: language-neutral canonical edges, provenance and typed literal values;
- `kristal_lexical_dictionary`: `KQ`/`KP` → language-specific labels and aliases;
- `kristal_external_crosswalk`: evidence-backed `KQ`↔Wikidata `Q`, `KP`↔Wikidata `P` records;
- `kristal_legacy_resolution_requests`: explicit requests for non-destructive legacy interpretation.
- `kristal_dictionary_catalog`, `kristal_wikidata_lexical_record` and `kristal_curated_dictionary`: versioned lexical source and human-reviewed layers, with scoped KQ/KP references, per-locale precedence, snapshot provenance and file digests. These are not a second canonical graph.

- `kristal_external_lexical_record` (JSONL) supplies source-stamped, reviewed third-party dictionary entries; `kristal_dik_coverage_report` and `kristal_dik_conversion_plan` supply interoperable, non-executable application outputs.

All new artifacts MUST validate their schema **and** the v11 semantic integrity rules, including referential integrity, ID uniqueness and crosswalk collision checks. JSON Schema alone is insufficient. Duplicated names MAY refer to distinct concepts; identical labels MUST NOT imply equivalence.

## Compatibility

v11 SHALL preserve v6–v10 byte commitments and all historic locks. Existing `kristal_v6` referents and text properties remain legitimate **inside legacy artifacts**. They are not promoted into the v11 graph without an explicit, reviewable resolution record. Identity migrations create new logical revisions under existing v9 rules, not silent mutation of committed history.

The identity registry's `namespace_id` is part of identity scope. `KQ1001` in two namespaces is **not** automatically the same entity; identity comparisons MUST include namespace. A Wikidata `Q1001` is always distinct from either. No local minting algorithm may issue real Wikidata QIDs or PIDs.

## Boundaries

- A local Wikidata dump MAY assist candidate retrieval; network access to Wikidata MUST NOT be required to read or verify a Kristal graph.
- `exactMatch` requires an accepted, evidenced decision; resemblance or string equality is never sufficient.
- Reconciliation NEVER renumbers the stable local KQ/KP. A later Wikidata entry only adds an external correspondence revision.
- No AI output, lexical match, or graph similarity alone gives identity authority.
- v11 semantic conformance is not a blanket claim that all historical Kristals are migrated.
