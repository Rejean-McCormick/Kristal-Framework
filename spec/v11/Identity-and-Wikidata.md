# Identity, minting and Wikidata crosswalk

## Scope and allocation

Use the existing v7 identifiers: `KQ…` items, `KP…` properties, `KA…` assertions, `KS…` sources. Their scope is `(namespace_id, id)`; allocators MUST prevent reuse **within** their namespace, persist issuance and expose a collision check. A future allocation service may be distributed, but this draft supplies **no global allocator**. The examples are illustrative and do not reserve production KQ IDs.

Before minting a new KQ/KP an authoring implementation SHOULD consult its local identity registry and, when available, the local Wikidata mirror to find identity candidates. If an existing local identity represents the intended concept, reuse it. If no verified match exists, mint a **new KQ/KP**, never a synthetic `Q…`/`P…`. Candidate matches do not block local minting when justified, but MUST remain reviewable.

## Independent crosswalk

`kristal_external_crosswalk` is separate from the graph. A mapping records local namespaced identity, exact external system and id, mapping relation, status and, when accepted, evidence-backed review. `exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch`, `relatedMatch` are **not interchangeable**. Wikidata Q maps only to KQ and Wikidata P maps only to KP. `candidate`, `rejected`, `superseded` entries MUST NOT be used as exact substitutes.

An accepted exact mapping MUST have an explicit decision id, method and `KS` evidence reference; validators MUST reject multiple accepted `exactMatch` records for the same KQ/KP *or* Wikidata Q/P **within the same namespace and crosswalk view** unless a reconciliation decision explicitly supersedes old records and the active view is unique. The supplied validator requires simple uniqueness in a single document.

## Future Wikidata alignment

On a later Wikidata dump:

1. discover possible corresponding Q/P using multilingual lexicon, type and structured context;
2. record each as candidate rather than exact;
3. verify scope and meaning; accept/reject with provenance;
4. publish a new crosswalk version/record, keeping historical mapping decisions auditable;
5. leave the internal KQ/KP, graph and existing commitment unchanged.

External redirects, splits, merges and Wikidata reuse of labels MUST NOT trigger local silent merges. When external meaning changes, record a superseding decision. A failed or offline mirror does not affect the internal graph.

## Terminology for diK (draft.3)

Use *semantic referent identifier* (French: **identifiant de référent sémantique**) as the generic term for an opaque KQ-style entity/concept identifier. This is not a Wikidata QID, and it does not cover KP property IDs or KA/KS assertion/source IDs. The precise key is the tuple `(namespace_id, KQ_id)`. An IRI is an addressing construct rather than a synonym for a QID. The distinction is normative in diK reports and conversion plans.
