# Language Layer

## Purpose

The Language Layer separates stable semantic identity from human language. It supports many languages, specialist vocabularies, education levels, regional terminology and project-specific lexical choices without embedding every translation in every semantic Kristal.

## Lexical Kristal

A `kristall_lexicon` is an external companion artifact. Each lexical entry points to a semantic reference and provides language-specific lexical material.

Default identity spaces are:

- `kristall` — v7/v8 `KQ`, `KP`, `KA`, `KS` identities;
- `kristal_v6` — stable v6 namespaced referents when no v7 mapping is required;
- `external` — an explicitly declared external identity space.

A lexicon MAY be incomplete. `lexical_status: missing` records a known gap and MUST NOT be rendered as an invented translation.

## Locale and script

`language` and requested locales use BCP 47 syntax (for example `fr`, `fr-CA`, `sr-Cyrl`). Lexicons MAY declare a default script and writing direction. Locale tags describe lexical/rendering context; they do not create semantic identity.

## Composition

Lexicons SHOULD be small, composable and scoped. Typical layers include:

- language core (`fr-core`);
- domain (`fr-chemistry`);
- educational level (`fr-science-college`);
- geography (`fr-CA`, `fr-botany-north-america`);
- organization/project deltas.

Domain, education and geographic scope SHOULD point to semantic identities rather than rely only on free text when such identities exist.

## Morphology

Language-specific morphology is optional lexical metadata. Part of speech, gender, number, inflection classes or other grammatical features MAY be stored in lexical entries. These features assist rendering but do not alter semantic assertions.

## Non-authority

Definitions, glosses and usage notes in a lexical artifact are explanatory lexical material. They MUST NOT override semantic assertions, ontology constraints, provenance or authority rules in the canonical semantic layer.
