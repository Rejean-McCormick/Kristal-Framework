# Reader Discovery — optional v10 companion profile (`1.0`)

This profile accepts **exactly the three noncanonical JSON formats produced by Local Authoring Kit 3.3.0**:

| Path in a Local Kristal | Format |
|---|---|
| `kristal.discovery.json` | `kristal.discovery/1.0` |
| `derived/reader-inventory.json` | `kristal.reader-inventory/1.0` |
| `derived/reader-profile.json` | `kristal.reader-profile/1.0` |

The schemas in `schemas/` are **byte-identical to the Authoring Kit 3.3.0 source schemas** at the time of this profile release. The `examples/demo-kristal` fixture was produced by that Kit and includes two registered artifacts (JSON and JSONL) and Arketype `PRF-15` classification.

Reader metadata is **advisory**. It is not v9 state, not an identity, not a semantic commitment, not a network discovery directory, not a publication, and not an authorization token. Its measured local bytes exclude unregistered and remote objects. Reader-specific optimization MUST be chosen from **verified physical format and size** under local policies, not from Arketype IDs alone. If a legacy Kristal has no discovery files, use a guarded generic reader. Incomplete triples must not be accepted as complete.

Example (Node 22+):

```bash
cd reference/js
node bin/kristal-ref.mjs inspect-reader-discovery ../../profiles/reader-discovery/examples/demo-kristal --verify-files
```

`--verify-files` verifies the exact local referenced file sizes and SHA-256. Without it, the command only checks metadata integrity and relationships. Neither mode independently reconstructs the Kit's source fingerprint from workspace/catalogue inputs, validates JSON content, proves authorization, decrypts, decompresses, invokes simdjson or guarantees full-project size. Run `python tools/kristal.py check` in the Kit to assess local staleness, plus appropriate v9/conformance checks separately.

A consumer may use `reader_plan` to set up its own **optional** simdjson adapter; JSONL streaming requires an independently measured record bound before batch sizing. Hints are never executable configuration by themselves. See [the Framework profile specification](../../spec/v10/Reader-Discovery-Profile.md).
