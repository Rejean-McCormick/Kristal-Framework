# Framework v11 draft.4 — diK alpha.7 / Authoring Kit draft.3 handoff

**Scope:** additive *tooling and explanation*, **not** a new semantic format. Framework's strict v11 normative schemas and TCK vectors still have the exact `11.0.0-draft.3` contract bytes and identities. The historical v6–v10 compatibility locks are unchanged. No installation, remote write, migration, approval or publication happens by reading this document.

## Responsibilities and trust boundaries

| Producer | Owned authority | Exchange | Forbidden shortcut |
|---|---|---|---|
| Kristal Framework v11 | Types, KQ/KP/KA/KS integrity, schemas, lexical layers and accepted crosswalk rules | Read-only preflight, coverage | Treat a passing preflight as authoring or identity approval |
| diK alpha.7 | Read-side dictionaries, source imports, candidate reviews, compact projections, coverage | `catalog.json` + hashed shards; candidate plans/reports | Allocate a KQ from matching terms or replace a canon |
| Authoring Kit 4.0.0-draft.3 | Canonical graph/registry, registered Logical Artifacts, explicit catalog selection, authorized migration producer | Imports **Wikidata-only** diK candidate, retains curated preferences | Adopt diK input without checking namespace, hashes or registration |
| Integration Pack v11 | Read-only consumer and projections | v11 verified payloads | Mutate KQ/KP through a lexical projection |

**Never use Wikidata `Q` as Kristal `KQ`, nor `P` as `KP`.** The immutable crosswalk requires an accepted `exactMatch` with registered KS evidence. Labels are stored in locales/candidate layers; they are not identities.

## Preflight reference command

`tools/v11/interop_preflight.py` is a **read-only candidate preflight**. Given an Authoring Kit workspace, supply its registered registry/crosswalk and the incoming external diK catalog. It checks schema, source hashes, acceptance, namespace and types against Framework v11 draft.3 rules. `--kit-import-candidate` rejects curated/external incoming layers because the Kit draft.3 adoption path only imports the newly downloaded Wikidata layers (reviewed curated layers are preserved independently).

```bash
python tools/v11/interop_preflight.py \
  --catalog /immutable/dik/output/catalog.json \
  --registry /authoring/project/canon/domain/v11/registry.json \
  --crosswalk /authoring/project/canon/domain/v11/crosswalk.json \
  --kit-import-candidate \
  --output /tmp/dik-kit-preflight.json
```

For the included Foundation fixture (with **curated** layers), use a *general dictionary* preflight **without** `--kit-import-candidate`:

```bash
python tools/v11/interop_preflight.py \
  --catalog examples/v11/dictionaries/catalog.json \
  --registry examples/v11/identity-registry.example.json \
  --crosswalk examples/v11/external-crosswalk.example.json \
  --graph examples/v11/semantic-graph.example.json \
  --locales fr,en,fr-CA
```

Preflight output is **derived**, includes input file SHA-256, catalog ID, namespace and coverage, and cannot overwrite a previous report. `complete_direct` and usable fallback remain distinct; an undeclared locale causes rejection. Preflight **does not** verify the source authority of a user-supplied hash, or automatically attest to meaning.

## Kit promotion remains distinct

On an independent *copy* of an Authoring Kit 4.0.0-draft.3 project, after preflight:

```bash
python tools/kristal.py import-dik-catalog ./MyKristal \
  --catalog /immutable/dik/output/catalog.json \
  --revision wd-review-001 --register \
  --artifact-id urn:project:dik:wd-review-001 \
  --contract-id project.v11.lexical-catalog
python tools/kristal.py select-v11-catalog ./MyKristal \
  --catalog canon/domain/v11/dictionaries/dik-revisions/wd-review-001/catalog.json
python tools/kristal.py check-v11 ./MyKristal
python tools/kristal.py coverage-v11 ./MyKristal --locales fr,en
```

The above is a *separate project CLI*, not a Framework CLI. Selecting a catalog is an explicit action after registration; it is not equivalent to a GitHub publication or a state activation. Kit recovery (`recover-v11`) handles some interruption phases; power-loss, multi-writer and network filesystem durability remain to be qualified.

## Current evidence and limits

The Framework's local regression suite exercises positive/negative preflight, file hash integrity, registration evidence, locale fallback and preservation of canon. The Authoring Kit draft.3 separately tested local import/selection. **The Framework release does not bundle an executable diK alpha.7 or the entire Authoring Kit source**: the preflight is not proof that every shipped diK alpha.7 import has passed against every Kit workspace. The diK alpha.7 importer is still an alpha; the user-supplied real Wikidata mirror, deltas, and hundreds of densely populated locales are not production-qualified.

For reproducibility, keep the exact `11.0.0-draft.3` semantic schema bytes pinned while draft.4 tooling and wiki evolve. Any *future* normative change requires its own schema/TCK/version negotiation and ratification; do not silently extend official schema fields to match diK candidate fields.
