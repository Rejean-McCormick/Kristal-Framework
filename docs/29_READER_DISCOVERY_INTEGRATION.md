# Reader discovery, Arketype and size-aware parser integration

This optional v10 draft.3.2 companion profile interoperates with Local Authoring Kit 3.3.0 and Arketype 1.4.0.

**Division of responsibilities**

- **Arketype:** design-time `ARK-xx` structures, `PRF-xx` use cases, domains, classifications. An unclassified or legacy Kristal remains valid.
- **Authoring Kit:** classification in `kristal.workspace.json`, physical inventory, input fingerprint, noncanonical discovery/profile generation, local freshness check. Derivations stay outside canonical v9 state.
- **Framework:** schemas, compatibility contract, validator and guarded reader-plan example.
- **Runtime/adapter (e.g. simdjson):** independent authorization, safe file open, actual format and digest verification, parser installation, sizing and resource limits, codec selection. The Framework does **not** ship a simdjson binary binding.

The reader plan can highlight different access patterns for UCKK, proof/navigation Kristals, longitudinal person records, procedure graphs, automotive diagnosis and knowledge federations without imposing a different v9 schema for each. Large JSONL and external compressed/remote segments must not be processed as raw JSON without extra checks.

**Procedure for a local Kit workspace**

```bash
python tools/kristal.py classify ./MyKristal --arketype-dir ../Arketype-v1.4.0 --usage PRF-15
python tools/kristal.py build-discovery ./MyKristal
python tools/kristal.py check ./MyKristal
node reference/js/bin/kristal-ref.mjs inspect-reader-discovery ./MyKristal --verify-files
```

Commands 1–3 belong to the **Authoring Kit repository**; the last belongs to the **Framework repository**. Paths must be adapted accordingly. No command publishes, activates or authorizes access to data. Readers lacking these files fall back to guarded generic behavior.

**Migration strategy**: no rewriting of v6/v7/v8/v9 logical contracts or v10 hosting contracts. Existing built states keep their commitments. Regenerate discovery metadata after changing registered source bytes, manifest declarations or Arketype classification; do not manually invent measurement values. A `large` label does not replace per-file sizing. A `federated` label is organization, not size.
