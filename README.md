# Kristal

[![Kristal Standard CI](https://github.com/Rejean-McCormick/Kristal-Framework/actions/workflows/ci.yml/badge.svg)](https://github.com/Rejean-McCormick/Kristal-Framework/actions/workflows/ci.yml)
[![KristalDiag](https://github.com/Rejean-McCormick/KristalDiag/actions/workflows/ci.yml/badge.svg)](https://github.com/Rejean-McCormick/KristalDiag/actions/workflows/ci.yml)
[![Release Reproducibility](https://github.com/Rejean-McCormick/Kristal-Framework/actions/workflows/release-qualification.yml/badge.svg)](https://github.com/Rejean-McCormick/Kristal-Framework/actions/workflows/release-qualification.yml)

**Current standard baseline:** `8.0.0`

Kristal is a portable, deterministic knowledge-state standard. v8 preserves the v6 portable state contract and the v7 semantic identity model, and adds two optional capability layers: **external composable language Kristals** and an **AI-native semantic query/context protocol**.

## v8 in one sentence

```text
v6 portable truth + v7 semantic identity + optional v8 language/query capabilities
```

v8 is additive. A valid v6 or v7 artifact does not need to be rewritten to participate in a v8 deployment.

## Repository boundaries

```text
spec/       normative prose and frozen compatibility specifications
schemas/    canonical active v6/v7/v8 JSON Schemas
tck/        normative conformance vectors and golden fixtures
examples/   non-normative examples
reference/  non-normative reference implementation(s)
tools/      repository, release, and non-normative v8 helper tooling
contracts/  release/contract manifests and compatibility locks
history/    status records and release history
compat/     frozen materialization needed only by legacy compatibility tests
```

The specification and TCK define behavior. Reference code demonstrates behavior.

## Architecture

```text
v6  kristal_state/6.0                         unchanged portable truth
        ↓
v7  KQ/KP/KA/KS + Mesh/KOS/axes/projections unchanged semantic baseline
        ↓
v8  Language Layer + AI Query Layer          additive optional capabilities
        ↓
    derived read models / AI contexts         never canonical authority
```

### Language Layer

Language is external to semantic identity. Lexical Kristals are composable by language, domain, education level, geography and project. A French deployment can resolve through `fr-core + fr-science + fr-chemistry + fr-CA + project-delta` without embedding 300 languages in the semantic Kristal.

### AI Query Layer

AI clients discover and resolve semantic identities, then query exact graph relations, assertions, evidence and provenance through the Kristal Query Protocol (KQP). Query indexes are rebuildable read models. Results explicitly declare completeness, truncation and continuation state. AI context bundles are bounded projections with provenance and trust metadata.

### Kristal Icon Code (presentation profile)

Kristal also defines an **informative, non-authoritative visual presentation profile** for desktop and UI identification. It encodes exactly three signals: domain band, knowledge-object nature pictogram and maturity `0..5`. The companion `kristal-desktop/1.0` convention standardizes a regenerable Windows `desktop.ini` binding with a compact `InfoTip` and machine-readable `[Kristal]` cache. Rendered icons and desktop metadata are derived views and never semantic authority. See [Kristal Icon Code](spec/v8/Kristal-Icon-Code.md).

## Final v8 invariants

```text
SEMANTICS != LANGUAGE
READ MODEL != CANONICAL STATE
MODEL OUTPUT != AUTHORITY
SCHEMA VALID != SEMANTICALLY VALID
SEMANTIC FINGERPRINT != BYTE HASH
PARTIAL RESULT != NEGATIVE RESULT
FUZZY DISCOVERY != SEMANTIC ANSWER
EXTENSION != CANONICAL MUTATION
```

See [v8 Home](spec/v8/Home.md) for the standard entry point and [Core Invariants](spec/v8/Core-Invariants.md) for the complete list.

## Compatibility

- valid v6 artifacts remain valid unchanged;
- valid v7 artifacts remain valid unchanged;
- v7 labels remain legal compatibility/display fallbacks;
- v8 lexicons, indexes, plans and AI contexts are external or derived;
- `contracts/v8-compatibility-lock.json` freezes inherited v6/v7 machine surfaces;
- downgrade may lose v8 capabilities but MUST NOT change semantic assertions to compensate.

## Public verification

Kristal is continuously validated on clean GitHub-hosted runners through separate normative and independent qualification layers.

- **Kristal Standard CI:** runs the Framework's native validation suite against the exact checked-out revision, including normative contracts, schemas, compatibility surfaces, TCK vectors, repository integrity checks and the v8 validation surface.
- **KristalDiag:** is maintained as a separate independent diagnostic and conformance framework. It self-tests independently and can qualify a pinned Kristal Framework revision against explicit semantic profiles.
- **Release reproducibility:** rebuilds the Kristal release independently and requires byte-identical archives before the release artifact is accepted.
- **Evidence artifacts:** GitHub Actions retains validation output, exact repository revisions, manifests and release hashes produced during qualification runs.

The separation is intentional:

```text
Kristal Framework = normative specification and reference contracts
KristalDiag        = independent examiner and qualification harness
GitHub Actions     = clean external execution environment
```

A green **Kristal Standard CI** demonstrates that the checked-out Framework revision satisfies its native normative validation suite.

A green **KristalDiag** qualification is a separate result against the explicitly pinned Standard revision and profile. The independent diagnostic does not redefine the Standard, and the Standard does not self-certify the independent diagnostic.

## Validate

```bash
python tools/validate_all.py
```

Build the deterministic release archive:

```bash
python tools/build_release.py
```