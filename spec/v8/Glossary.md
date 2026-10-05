# v8 glossary

**AI context bundle** — bounded derived projection designed for model consumption. Not canonical state.

**BCP 47 locale** — standard language tag such as `fr`, `fr-CA` or `sr-Cyrl` used for lexical/rendering selection.

**canonical state** — inherited v6/v7 source-of-truth material under its own contract.

**completeness** — declared extent to which a result satisfied requested semantic, evidence and source scope.

**continuation** — opaque cursor/state used to resume a stable paginated query.

**discovery** — approximate or exact process that proposes semantic identity candidates before exact traversal.

**lexical Kristal** — external companion mapping semantic references to language-specific forms.

**lexicon stack** — ordered set of lexical Kristals plus deterministic resolution/fallback policy.

**KQP** — Kristal Query Protocol `kristal-query/1.0`.

**partial result** — useful result that did not fully cover requested scope. Not evidence that omitted facts do not exist.

**query index** — rebuildable derived structure used to accelerate query. Not semantic authority.

**semantic atom** — context unit containing enough identities, relation/assertion material and provenance to remain interpretable when selected independently.

**semantic fingerprint** — versioned derived digest over a declared semantic projection. Distinct from inherited byte/content hash.

**semantic universe** — federated language-neutral space using v7 identities, mappings and shards.

**symbol table** — local compact mapping used inside an AI bundle to reduce repeated IDs; never a persistent semantic identity.

**trust class** — metadata describing how context should be treated by a consuming AI/control plane; it does not itself establish factual truth.


**Kristal Icon Code** — informative presentation profile `kristal-icon/1.0` that encodes domain, dominant knowledge-object nature and maturity in a compact icon. Not semantic authority.

**icon nature** — one dominant presentation category (`REF`, `COL`, `MOD`, `PRT`, `TWN`, `INV`, `SRC`) describing what kind of knowledge object a Kristal primarily represents. Distinct from JSON `artifact_type` and storage/schema version.

**icon maturity** — presentation-level `0..5` assessment of how mature/stable the Kristal representation is. Not certainty, truth probability or problem-resolution status.

**Kristal desktop binding** — informative Windows folder-binding convention `kristal-desktop/1.0` that maps a generated Kristal icon and compact human `InfoTip` onto a folder while optionally exposing a machine-readable `[Kristal]` cache. It is regenerable and not semantic authority.

**Kristal InfoTip** — localized human tooltip derived from presentation metadata in the order name, nature, domains, maturity and optional volume. It is a display summary, not a machine identity.

