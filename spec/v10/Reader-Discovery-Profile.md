# Reader Discovery Companion Profile — v10 draft.3.2

**Status:** optional additive operational profile, version 1.0; intended for Local Authoring Kit 3.3.0 and future compatible producers. The v9 semantic-state commitment algorithms and frozen v6–v9 contracts are unchanged.

## Purpose and surfaces

A Kristal reader can discover the *shape* of a state before opening large physical payloads. The Local Kit produces three noncanonical files with corresponding schemas in [`profiles/reader-discovery/schemas/`](../../profiles/reader-discovery/schemas/):

1. `kristal.discovery.json` (`kristal.discovery/1.0`) — state reference, declared Arketype classification (`ARK-xx`, `PRF-xx` when known), physical organization, scale class, links to derived metadata, and input fingerprint.
2. `derived/reader-inventory.json` (`kristal.reader-inventory/1.0`) — actual registered local bytes, SHA-256, media types, materialization segment declarations and missing/external status. It is **not** total disk usage or a complete measure of external federations.
3. `derived/reader-profile.json` (`kristal.reader-profile/1.0`) — an advisory reader specialization and per-artifact parser suggestions. It is **not** a runnable command.

Producers **SHOULD** preserve exact filenames within the Local workspace and **MUST** write matching `state_ref` and `source_fingerprint` across the triple. Consumers **MUST NOT** assume Arketype declarations are independently verified facts. The inventory may be partial even when its tracked byte measurements are accurate. Null values such as `max_record_bytes` are unknown, not zero.

## Scope boundaries

```text
v9 semantic identity and logical commitments  !=  operational reader discovery
v10 hosted directory and publication          !=  local reader discovery
Arketype use-case profile                     !=  JSON codec or memory policy
measured registered local files               !=  total/federated corpus size
metadata verification                        !=  file access authorization
```

The discovery triple **MUST NOT** be registered as a canonical Logical Artifact merely to enable reader optimization. Discovery is independent of v10 GitHub hosting: copying a discovery file to a public read surface is a separate disclosure and sync policy decision. In particular, a read surface MUST NOT expose private file inventories by default.

## Selection protocol

1. Check if all three files exist. If absent, use a guarded generic reader; if partially present, signal incomplete discovery and use the generic path rather than trust partial hints.
2. Validate each file against the versioned schema and cross-check `state_ref`, `source_fingerprint`, reader/inventory links, size class and file/strategy correspondence.
3. Independently enforce authorization. Before consuming a payload, verify its safe relative path, availability, byte size, digest, actual format, limits and any encryption/compression envelope. The producer's source fingerprint binds observed inputs but is not a substitute for the consumer's own content verification.
4. Use architecture/usage only to prioritize indices and access patterns. Use physical type, per-file size, materialization segmentation and runtime capabilities to choose parser mode and capacities. Unknown reader profile IDs MUST fall back to a guarded generic strategy.
5. JSONL / NDJSON readers MUST establish an independent record-length bound before choosing a `simdjson` batch size. Decompression MUST be bounded before decoding; encrypted data requires separately authorized decryption. Do not treat declared labels as verified bytes.
6. Invalidate cached plans on missing, mismatched, or stale metadata. The Local Kit `check` operation verifies whether its generated metadata still matches workspace inputs; the Framework reference checker validates the triple and can verify listed file SHA-256 but does not reproduce Kit input fingerprints.

## Implementation and conformance

The Framework JS reference (`reference/js/src/v10/reader_discovery.mjs`) exposes `verifyReaderDocuments`, `readerPlan` and `inspectReaderRoot`; the CLI accepts:

```bash
node reference/js/bin/kristal-ref.mjs inspect-reader-discovery <local-kristal-dir> [--verify-files]
```

The output is an **advisory plan**, not execution by simdjson. `--verify-files` streams SHA-256 checks for registered local files, rejects traversal and symlinks and uses a metadata file-size cap. No external bytes are retrieved.

These are **profile-level** checks. They do not establish v9 conformance, upstream derivation freshness, real-world diagnosis accuracy, medical validity, access policy satisfaction or publication readiness.

For a producer example and exact schema mirror see [`profiles/reader-discovery/README.md`](../../profiles/reader-discovery/README.md). For the earlier conceptual distinction between polymorphic workloads and logical shapes see [v9 polymorphism](../v9/Architecture.md).
