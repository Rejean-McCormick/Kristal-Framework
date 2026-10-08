# Kristal

**Current standard baseline:** `10.0.0-draft.2`

Kristal is a portable, deterministic knowledge-state standard. **Kristal v10 — Hosted Kristal Network Architecture** preserves the frozen v6 portable epistemic state, v7 semantic identity model, v8 language/query layer, and v9 Semantic State Architecture while adding portable node discovery, host bindings, publication records, directories and host profiles.

## v10 in one sentence

```text
v6 epistemics + v7 identity + v8 language/query + v9 semantic state + v10 hosted network
```

## Core v10 rule

```text
SEMANTIC STATE != HOSTING != PUBLICATION LOCATION != DISCOVERY DIRECTORY
```

V10 deliberately keeps v9 logical artifacts, state snapshots and commitment profiles unchanged. GitHub is the first reference host profile (`kristal.host/github/1.0`), not a dependency of semantic identity.

## New v10 surfaces

```text
.kristal/node.json              -> node identity and roles
.kristal/bindings/*.json        -> replaceable host bindings
kristal_publication             -> exact state -> retrievable host resources
kristal_directory               -> discovery/routing across many nodes
```

A large deployment can therefore use many repositories/collections and a root directory without making repository layout part of the knowledge commitment.

## Validate

```bash
python tools/validate_all.py
cd reference/js && npm test
node bin/kristal-ref.mjs v10-capabilities
```

Start with [v10 Home](spec/v10/Home.md), the [Core Specification](spec/v10/01-core-spec/kristal-v10-core-spec.md), and the [GitHub Reference Profile](spec/v10/GitHub-Reference-Profile.md).

## GitHub bootstrap

The companion one-time account/repository bootstrap is bundled under [`tools/github-bootstrap/`](tools/github-bootstrap/README.md). It manages account-wide GitHub integration, a private root directory, initial public/private Kristal collections, and later one-time initialization of additional Kristal repositories.
