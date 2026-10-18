# Lexical boundary

The canonical graph **does not contain `label`, `name`, `preferred_label`, translated properties or human-language identity slugs**. Those belong to external `kristal_lexical_dictionary` artifacts keyed by KQ/KP + `namespace_id` + locale. Dict entries MAY include synonyms and contextual domain KQ IDs. Dictionary labels and definitions are presentation/search data, never semantic identity or epistemic authority.

The v8 layered lexicon remains a valid historical reader format; the new v11 dictionary profile is strict and language-specific. A future adapter MAY import compatible v8 entries after explicit normalization into namespace-scoped KQ/KP; `kristal_v6`, `external`, and unresolved source referents MUST NOT masquerade as v11 canonical IDs.

Render: resolve semantic ref → select dictionaries by locale + declared fallback/precedence → select visible term; missing translation leaves the KQ/KP visible as a missing lexicalization, **not missing meaning**.

Resolve legacy words: locale and expected identity kind are mandatory, contextual domain KQ can filter candidates, duplicate/ambiguous matches are reported and never auto-merged. A word appearing in a quotation or an explicitly typed literal **does not require conversion**: only places previously used as identity or predicate need to be migrated.

For operational import/curation, use [Dictionary management](Dictionary-Management.md): source/curated layers, per-locale audit and explicit provenance. v11 lexical dictionary artifacts remain supported; the draft.2 catalog profile adds managed imported and curated layers.
