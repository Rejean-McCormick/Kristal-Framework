# Framework v11 / diK — owner and schema boundary

**Documentation of a downstream compatibility check, 24 November 2026.**
The Framework checkout reports `11.0.0-draft.4`. The 11 schema JSON files
under `schemas/v11` match the diK vendored copies byte-for-byte in the
supplied SmartDump. This observation does **not** establish complete TCK
or runtime compatibility with other repositories.

Framework remains normative for KQ/KP/KA/KS, namespace binding, lexical
catalogs and external Wikidata mapping formats. A bare `KQ1001` is not
globally unique: consumers must retain `namespace_id`. Neither a label nor
a Wikidata Q/P is a local Kristal identity. The history of v6–v10 and the
current v11 reference schemas/tools remain unchanged.

diK's `dik.canonical-selection-decisions/0.2` is a **non-normative** local
review format requiring five source SHA-256 digests, including the graph.
It does not revise any Framework schema, claim a Framework-active revision,
or make an editorial approval. The read-only cross-check is owned by C0:
`scripts/check_semantic_schema_parity.py` in kOA Digital Ecosystem.
