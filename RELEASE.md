# Kristal Standard 6.0.0 release

Kristal 6.0.0 is the first release whose canonical structured artifact is `kristal_state`.

## Release identity

```text
version: 6.0.0
git tag: v6.0.0 (pending until the release commit/tag exists)
canonicalization: kristal.v6:jcs-rfc8785 / 1
canonical artifact: kristal_state
```

`kristal-release.json` records release metadata. `contract-set.manifest.json` identifies public contract surfaces. Git tag + resolved commit SHA pin the repository bytes after publication.

## Main semantic changes

- typed `valuations[]` replace the assumption of one universal certainty dimension;
- `coordinates` expose domain geometry;
- `applicability` exposes applicability boundaries;
- `record_role` distinguishes constraints, observations, local rules, derived state, decisions, actions and structural records;
- `actionability` exposes human/automation boundaries without granting execution authority;
- `kristal_state` replaces v5 SES as the conceptual center for new models.

## Compatibility

The complete v5 technical reference remains under `docs/Technical-Reference/kristal-docs-v5/`.

`knowledge-model-contract.v1.json` is retained unchanged for legacy consumers. The active v6 bundle is `knowledge-model-contract.v2.json`.

Existing v5 Exchange/Runtime Pack/shard/federation consumers may continue through compatibility adapters. New v6 models should not use those materializations as a second canonical truth layer.

## Validation

Before tagging:

```bash
python tools/validate_all.py
```

A release tag must be created only after the tree passes the v6 release gate, v6 conformance checks, retained v5 compatibility vectors and strict docs build.
