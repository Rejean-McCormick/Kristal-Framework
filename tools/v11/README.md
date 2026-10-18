# v11 Framework reference tools

`validate_v11.py` validates examples, schema pairs and cross-document identity integrity. `resolve_legacy.py` proposes non-destructive conversions of explicitly supplied legacy identity paths using v11 dictionaries and accepted/exact Wikidata crosswalk mappings. It does not modify a Kristal or mint any KQ/KP.

These are Framework reference tools, not an Authoring Kit release. `pip install -r requirements-dev.txt` provides the required `jsonschema` dependency.


## Draft.2 dictionary management reference

`dictionaries.py` is an **offline** file-based importer/auditor/renderer; it does not fetch remote data or alter existing Kristals:

```bash
python tools/v11/dictionaries.py import-local \
  --dump examples/v11/wikidata-small.sample.jsonl \
  --crosswalk examples/v11/external-crosswalk.example.json \
  --namespace example.org/kristal-demo --snapshot my-new-snapshot \
  --languages fr,en --output /tmp/kristal-dictionaries
python tools/v11/dictionaries.py audit \
  --catalog examples/v11/dictionaries/catalog.json \
  --crosswalk examples/v11/external-crosswalk.example.json \
  --registry examples/v11/identity-registry.example.json
python tools/v11/dictionaries.py resolve \
  --catalog examples/v11/dictionaries/catalog.json --id KQ1001 --locale fr-CA
```

The input dump can be official line-per-entity JSON array, JSONL, `.gz` or `.bz2`. The importer streams input once, uses a temporary SQLite index for deterministic ordering, and imports only accepted `exactMatch` Q/P entities into immutable source files. It **does not** mint identities, merge lexical ambiguity, invent terms, overwrite earlier snapshots or overwrite reviewed curation.

To update, import into a **new** directory and compare versioned catalog files; reviewed curation is a separate layer. The reference lookup scans layers and is not optimized for full Wikidata-sized indexes. For 300 languages at scale, an external index/caching layer can be generated from the exact source files without becoming canonical. The RFC defines a future HTTP downloader; no live bulk download, incremental-change watcher or IANA/CLDR locale registry validation is shipped in this draft.


## diK profile — draft.3 (read only)

```bash
python tools/v11/dik_coverage.py --graph examples/v11/semantic-graph.example.json --registry examples/v11/identity-registry.example.json --crosswalk examples/v11/external-crosswalk.example.json --catalog examples/v11/dictionaries/catalog.json --locales fr,en,fr-CA
python tools/v11/dik_conversion_plan.py --plan examples/v11/dik-conversion-plan.example.json --registry examples/v11/identity-registry.example.json --source examples/v11/dik-legacy-sample.json
```

The Framework now accepts reviewed third-party dictionary sources with source identity, version and license. The planned diK application will manage multi-dictionary reconciliation and migration workflows; the supplied tool checks plans and coverage but **does not rewrite legacy artifacts**, connect to online Wikidata, or certify 300-language throughput.


## Draft.4 read-only diK/Kit preflight

`interop_preflight.py` validates an incoming catalog against the exact Framework v11 draft.3 schemas, SHA-256 layers, the authoritative registry and reviewed crosswalk. Use `--kit-import-candidate` for Wikidata-only incoming layers; curated and external layers must not be promoted by that path. For a graph, add `--graph ... --locales fr,en,fr-CA` to check KQ/KP coverage. This is **not** Kit registration, catalog selection, semantic promotion, signed approval, network access, or general diK application qualification. See `docs/30_DIK_AUTHORING_KIT_HANDOFF.md`.
