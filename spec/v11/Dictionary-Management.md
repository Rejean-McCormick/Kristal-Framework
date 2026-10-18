# Dictionary management — v11 draft.3

## Scope and non-goals

The semantic graph's source of truth is the namespaced KQ/KP/KA/KS registry, **not** a label, a language, a Wikidata Q/P, or an automatic translation. This profile makes lexical data manageable for hundreds of locales without requiring a dictionary server. It does **not** claim 300 fully populated translations: each locale has independently measured, potentially sparse coverage.

A directory of versioned, hash-verified files is sufficient as the authoritative interchange/storage format. A local SQLite/search index, caching service or UI MAY be *derived* from those files; it MUST be reproducible and MUST NOT become a competing semantic identity registry.

## Separation of concerns

1. **Crosswalk:** accepted, evidence-backed `exactMatch` KQ↔Wikidata Q and KP↔Wikidata P, versioned independently. Other matching relations and candidate mappings cannot automatically supply canonical lexical entries.
2. **Imported source:** immutable-per-snapshot `kristal_wikidata_lexical_record` JSONL shards, generated from downloaded Wikidata JSON data. An imported term has the exact source external Q/P, language, labels/aliases/descriptions, snapshot ID and optional revision. This is neither a verified Kristal definition nor an internal identity.
3. **Curated source:** reviewed local corrections, specialist terminology and additions, indexed by *namespaced* KQ/KP and locale. Human-curated overrides are never overwritten by fresh Wikidata imports.
4. **Catalog/manifest:** declares supported BCP 47 language tags, explicit per-locale fallbacks and ordered lexical layers, with SHA-256 for each on-disk file. Its paths are relative to the catalog directory and may reference many shards. The catalog, not an undeclared filesystem glob, determines precedence.

Every `(namespace_id, semantic_id, locale)` MAY have entries from several layers. An explicitly reviewed curated layer can supersede a source label **for display only**. Equal-precedence contradictory resolved terms are an error, not a random pick. An absent translation MUST be reported as missing; no guessed, machine-generated or fallback term may be written as verified translation automatically.

## Scale and language semantics

- Locale tags SHOULD follow IETF BCP 47 / Unicode CLDR (`fr`, `fr-CA`, `zh-Hant`, `sr-Latn`, etc.), with canonicalization and aliases carried in an external locale registry. A simple regex alone does not verify that a tag exists. Preserve Unicode text faithfully (NFC normalization for comparisons; never ASCII-only transliteration by default).
- No limit of 300 in the protocol: 300+ locales can be declared; each can have zero or more lexical shards. Coverage MUST be calculated separately for KQ and KP, per locale and domain, from the actual semantic references, not the number of language files.
- Sparse storage: no placeholders for every `KQ × locale`. File sharding and compressed JSONL are permitted when volumes demand it. For large imports, a temporary SQLite index is a **derived processing artifact**, not the semantic canon.
- Directionality and script-specific display (right-to-left, distinct scripts) are presentation concerns; locale fallback MUST be explicit and MUST NOT silently equate scripts or languages.
- Same spelling can validly name different KQ concepts: reverse lookup returns candidates with context. Aliases are not guaranteed translations.

## Wikidata update workflow

Wikidata publishes JSON entity dumps with Q/P labels, aliases and descriptions per language. An operator may use a local mirror or download the official dump; separate downloads for 300 languages are **not required**. Its Wikibase lexeme namespace (L identifiers and senses/forms) is distinct from Q/P labels and SHOULD only be imported through a future explicitly typed lexical extension.

1. Record source URI or local mirror ID, snapshot date/revision and content digest.
2. Stream the dump *once*, joining only accepted exact KQ↔Q / KP↔P crosswalk entries. Extract requested locales; do not invent missing labels. Reject inconsistent or duplicate mappings.
3. Build sorted source JSONL shards, catalog hashes and per-language statistics. Never modify curated entries.
4. Compare the new source snapshot against the previous one and review changed/vanished labels, redirects, deleted entities or crosswalk changes. Mark these for audit rather than editing semantic identities.
5. Review local spelling, term and meaning changes in curated files. Published semantic graphs, identities and past content commitments remain unchanged.
6. Validate catalog paths, hashes, locale selection, references, layer conflicts, source provenance and verified crosswalks. Publish a new lexicon/catalog version only after validation.

## Strict rendering / resolution rules

For `(namespace_id, KQ/KP, locale)`: load the catalog's declared locale and *only* its declared fallback chain, evaluate valid layers by precedence, reject ties with different terms, return the selected term plus origin, effective locale and fallback flag. Missing lexicalization returns the KQ/KP and a missing status, without changing the concept. Reverse lookups use language+expected KQ/KP kind+domain; ambiguous words remain candidate sets.

Wikidata Q/P must not be used directly as graph endpoints or property identifiers, and an external source candidate, closeMatch, relatedMatch, or fuzzy lexical similarity MUST NOT become an accepted exact mapping. Curated display preferences are not epistemic evidence of a concept's identity.

## Repository / package structure (illustrative)

```text
dictionaries/
  catalog.json                 # language tags, namespaces, layers, SHA-256s, fallbacks
  imported/wikidata/<snapshot>/fr.jsonl
  imported/wikidata/<snapshot>/en.jsonl
  curated/fr.json             # versioned local terminology, reviewed overrides
  curated/fr-CA.json
  curated/ar.json
```

At larger scale, split source files into hashed, content-addressed or stable ID-range shards under each locale. Do not commit a complete raw Wikidata mirror or generated multi-gigabyte search indexes into each Kristal repository. They can be independently hosted via the v10 publication and discovery mechanisms.

## Conformance status

The draft.2 Framework ships schema contracts and a deterministic, **offline** reference importer, catalog auditor and renderer for a bounded accepted-exact subset of a local JSON/JSONL Wikidata dump. It does not currently provide a production distributed dictionary service, live Wikidata downloading/resume, language-tag registry integration, full-dump performance certification or translation review UI; those may be implemented in Authoring Kit / specialized services against this contract.

## Addendum draft.3 — conciliation de plusieurs dictionnaires (diK)

The catalog layer kind `external` allows third-party terminology sets, in addition to `wikidata` and `curated`. Each external JSONL entry MUST cite its source system, source snapshot, source record ID, license/usage conditions, target KQ/KP and an **explicit reviewed alignment decision** with at least one `KS` evidence reference. Its layer MUST declare `source_system`, `source_snapshot`, `license`, path, priority and SHA-256. The validator checks provenance and source-reference integrity; it does **not** claim that reviewed alignment is objectively correct.

Sources may disagree on labels without changing KQ identity. Curated preferences never rewrite imported snapshot data. Equal-priority contradictory labels are rejected by audit. A diK user may propose a new preferred term or an external-to-internal alignment, but MUST record the reviewer and evidence in a new versioned layer. Unsupported, unreviewed or rights-incompatible imports MUST NOT be installed as trusted lexical sources.

The [diK interoperability profile](diK-Interoperability.md) defines graph-specific coverage and non-executable conversion plans. diK may construct additional derived indexes but may not turn imported words, Wikidata QIDs or source-local dictionary IDs into Kristal identity keys.
