# Kristal

[![Kristal Standard CI](https://github.com/Rejean-McCormick/Kristal-Framework/actions/workflows/ci.yml/badge.svg)](https://github.com/Rejean-McCormick/Kristal-Framework/actions/workflows/ci.yml)
[![KristalDiag](https://github.com/Rejean-McCormick/KristalDiag/actions/workflows/ci.yml/badge.svg)](https://github.com/Rejean-McCormick/KristalDiag/actions/workflows/ci.yml)
[![Release Reproducibility](https://github.com/Rejean-McCormick/Kristal-Framework/actions/workflows/release-qualification.yml/badge.svg)](https://github.com/Rejean-McCormick/Kristal-Framework/actions/workflows/release-qualification.yml)

**Current standard baseline:** `9.0.0-draft.1`

Kristal is a portable, deterministic knowledge-state standard. **Kristal v9 — Semantic State Architecture** preserves the frozen v6 portable epistemic state, v7 semantic identity model, and v8 language/query layers while adding representation-independent logical artifacts, immutable state snapshots, declared derivations, polymorphic materialization, and a Build → Publish → Activate lifecycle.

## v9 in one sentence

```text
v6 portable epistemics + v7 semantic identity + v8 language/query + v9 semantic-state architecture
```

## Core v9 rule

```text
KNOWLEDGE != BUILD != MATERIALIZATION != READ MODEL
```

V9 does **not** force graphs, DAGs, ASTs, relations, event ledgers, documents or federations into one universal shape. A `Logical Artifact` keeps its domain-native contract; a `State Snapshot` composes immutable logical commitments; physical representations can be changed or optimized without silently changing the logical state.

## Repository boundaries

```text
spec/       normative prose and compatibility specifications
schemas/    canonical JSON Schemas (v6-v9)
tck/        normative conformance vectors and golden fixtures
examples/   non-normative examples
reference/  non-normative reference implementation(s)
tools/      repository, release, and helper tooling
contracts/  release/contract manifests and compatibility locks
docs/       v9 architecture/authoring documentation
history/    status records and release history
compat/     frozen legacy compatibility material
```

## Architecture

```text
State Snapshot
  ├─ Logical Artifact(s) — domain-native shape
  └─ pinned external reference(s)
           │
           ▼
     Derivation Graph
           │
           ▼
     Materialization
       ┌───┴───┐
    Exchange  Runtime
```

## Compatibility

- valid v6 artifacts remain valid unchanged;
- valid v7 identity surfaces remain unchanged;
- v8 language/query semantics remain unchanged;
- `contracts/v9-compatibility-lock.json` freezes inherited v6-v8 machine/TCK surfaces;
- v9 domain-native artifacts may project to v6 without making the projection canonical by default.

## Validate

```bash
python tools/validate_all.py
```

Reference implementation:

```bash
cd reference/js
npm test
node bin/kristal-ref.mjs v9-capabilities
```

Build the deterministic release archive:

```bash
python tools/build_release.py
```

Start with [v9 Home](spec/v9/Home.md), the [Core Specification](spec/v9/01-core-spec/kristal-v9-core-spec.md), and the extended design documentation in [`docs/`](docs/README.md).
