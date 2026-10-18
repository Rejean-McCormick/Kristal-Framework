# Kristal v11 — Canonical Semantic Identity & Lexical Separation

**Status:** `11.0.0-draft.4` — proposed standard; **not** published as final conformance.

Kristal v11 *adds* a strict semantic identity profile to the frozen v6–v10 foundation. Its graphs carry only Kristal semantic identities for nodes, properties, assertions and sources. Language is resolved through lexical dictionaries; Wikidata is an external mapping, never an alternative master namespace.

```text
v6 epistemic state + v7 KQ/KP/KA/KS + v8 lexical/query + v9 commitments + v10 hosting + v11 strict semantic identity
```

- [Core specification](01-core-spec/kristal-v11-core-spec.md)
- [Identity and Wikidata crosswalk](Identity-and-Wikidata.md)
- [Lexical boundaries](Lexical-Boundary.md)
- [Dictionary management: 300+ languages, imported/curated layers](Dictionary-Management.md)
- [Legacy resolution and migration](Legacy-Resolution.md)
- [diK dictionary-app interoperability](diK-Interoperability.md)
- [diK alpha.7 / Authoring Kit draft.3 exchange companion](diK-Toolkit-Exchange.md)
- [Conformance](Conformance.md)

This draft **does not rewrite** frozen v7 registry schemas with `preferred_label`, existing v8 lexicons with compatibility identity spaces, v9 commitments, v10 host contracts, or old state commitments. Its `schemas/v11` contracts opt into a stricter profile; legacy formats remain readable under their own declared versions.
