# diK interoperability profile — Kristal Framework v11 draft.3

**Status:** additive draft contract, not certification of a shipped diK application.

## Vocabulary

- **Identifiant de référent sémantique (IRS)** / **semantic referent identifier**: general conceptual name for an opaque identifier designating a person, object, event, or concept. In the canonical Kristal namespace, the entity/reference identifier is `KQ…`.
- **Semantic property identifier:** `KP…`. Statement and source identifiers are `KA…`, `KS…` respectively.
- **Wikidata QID**: Wikidata's `Q…` item identifier; **Wikidata PID**: `P…` property identifier. These are *external identifiers* in Kristal, never substitutes for KQ/KP without a typed, accepted exact crosswalk and explicit projection.
- **IRI** (Internationalized Resource Identifier) is an addressing standard and is not synonymous with KQ or Wikidata QID.

## The normative boundary

Kristal Framework owns file schemas and semantic integrity rules. **diK is a prospective implementation/client**, not an alternative authority or a new identity namespace. A diK-generated report or migration plan MUST cite the graph, lexicon catalog, registry namespace and any used crosswalk snapshot. A derived cache or live service MUST be reproducible from the versioned inputs.

## Two independent dictionaries

1. Lexical dictionaries: `({namespace}, KQ/KP, locale, optional domain)` -> labels/aliases, source, precedence, review.
2. Alignment crosswalk: `({namespace}, KQ/KP) ↔ (system, Q/P)`, relation (`exactMatch` etc.), status, evidence and review.

One does not imply the other. The same term may label distinct KQ IDs. A `closeMatch` MUST NOT be used as an exact-mapping bridge to import a label as verified. No new Wikidata Q/P identifiers are minted internally. When an external Q/P appears later, add a reviewed crosswalk revision while preserving internal IDs and historical commitments.

## Coverage contract

`schemas/v11/kristal-dik-coverage-report.schema.json` specifies a machine-readable summary for a canonical `kristal_semantic_graph` and a `kristal_dictionary_catalog`.

- Denominator: **distinct KQ IDs** referenced as entities; independently **distinct KP IDs** referenced as properties including qualifiers. KA/KS are separately checked for referential integrity, not implicitly counted as untranslated KQ items.
- Every requested locale has four mutually exclusive statuses: `direct`, `fallback` (explicitly declared locale fallback only), `missing`, `conflicted`.
- `complete_direct` means every KQ **and** KP has a direct label in that locale. `complete_usable` additionally accepts explicit fallback labels. These MUST NOT be conflated.
- An empty selected locale set is invalid. Every requested locale MUST be declared in the chosen catalog. No unreviewed/generated translation counts as direct.
- `all_locales_direct` / `all_locales_usable` count the KQ/KP covered **in every selected locale**; they are not percentages over all Wikidata.
- Source catalog and semantic graph SHA-256, graph ID and namespace MUST be included so the report is reproducible. Detailed missing lists MAY be separated into hashed JSONL shards by future profiles; the reference implementation includes a deterministic bounded sample and truncation flag.
- This report applies to **v11 canonical input**. A legacy Kristal with unresolved words MUST undergo semantic inventory first; its denominator is unknown and no 100% completeness may be claimed.
- Crosswalk completeness is a **separate report/metric**, never counted as lexical completeness.

## Conversion plan contract

`schemas/v11/kristal-dik-conversion-plan.schema.json` describes a proposed migration from a versioned historical artifact. Every operation is attached to an exact source path, original value, KQ/KP target, decision and evidence.

- Plans are **not** execution authorization. A producer (e.g. Authoring Kit) MUST independently verify source digests and that every operation is explicitly reviewed and approved before emitting a new semantic revision.
- A label match produces a **candidate**, not automatic proof of identity. Scores are advisory only; ambiguity MUST stop automatic application.
- Non-identity text, quotations and literal content MUST NOT be target paths. A global string replace is nonconforming.
- Applied migrations MUST preserve old source bytes and cryptographic commitments, create a new logical revision and an auditable reversal/crosswalk record.
- The Framework currently validates plans structurally and provides an offline coverage reference; it **does not execute migration**. Authoring Kit or diK would implement an approved, transactional producer flow in a later release.

## Local workflow / read-only example

```sh
python tools/v11/dik_coverage.py \
  --graph examples/v11/semantic-graph.example.json \
  --registry examples/v11/identity-registry.example.json \
  --crosswalk examples/v11/external-crosswalk.example.json \
  --catalog examples/v11/dictionaries/catalog.json \
  --locales fr,en,fr-CA \
  --output /tmp/dik-coverage.json
```

The reference command refuses stale catalog hashes, missing registry identities, unknown locales and conflicting layers. It does not mutate graphs, dictionaries or the external Wikidata dump. It is a bounded local reference implementation; large-dump download/synchronization, 300-language performance certification, bulk reverse lookup, curator UI and migration execution remain application-level work.

## Validation expectations

A conforming diK implementation SHALL test: mixed-case locale normalization under a separate IANA/CLDR registry (not falsely claimed by draft tools), namespace isolation, crosswalk versioning, 300+ sparse locales, duplicate term/disputed sources, conflict audit, fallback count separation, prospective QIDs not taking precedence over KQ identities, no silent replacement of literals, snapshot and migration immutability, and correction-layer preservation.
