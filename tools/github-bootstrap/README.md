# Kristal GitHub Bootstrap 1.1.0-alpha.10


Windows preset: `Rejean-McCormick/KristalV10` at commit `27c0c7db3d79a4597c1c964fe8281fa35b5f858a`, with config `C:\mycode\Kristal\network.toml`. Existing config at that path is auto-loaded.
Declarative bootstrap and reconciliation engine for a **Kristal v10 Hosted Kristal Network** on GitHub.

This prerelease hardens the 1.0 bootstrap around four rules:

1. desired configuration and observed GitHub state are compared before mutation;
2. managed files are updated only when their last managed fingerprint still matches, otherwise the tool reports a conflict;
3. node identity is persistent and independent from the GitHub repository locator;
4. generated workflows pin the Kristal Framework and external Actions to immutable commit SHAs.

## Two configuration levels

```text
ACCOUNT / ORGANIZATION
  ├─ public .github integration
  ├─ optional private organization profile
  ├─ private root directory + network registry
  └─ optional GitHub account-level metadata

REPOSITORY / NODE
  ├─ .kristal/node.json
  ├─ .kristal/bindings/github.json
  ├─ .kristal/capabilities.json
  ├─ .kristal/bootstrap-state.json
  ├─ qualification workflow + receipt
  ├─ verifiable publication workflow
  └─ collection nodes: sharded read-surface ingest workflow
```

The default topology remains a private root hub plus at least one public and one private collection. A repository is a permissions/lifecycle boundary, not necessarily one Kristal: one collection repository may host many Kristals.

## Identity and privacy

`[network].id` and each collection `identity_key` are operational identity inputs. Keep them stable if a repository is renamed or moved. Existing `.kristal/node.json` identifiers are preserved when the bootstrap adopts an already initialized node.

Public README/profile content does **not** name the private hub. The private registry may know all nodes; public discovery surfaces are intentionally filtered.

## Requirements

- Python 3.11+
- GitHub CLI (`gh`) authenticated with the permissions required by the selected features
- a public Kristal Framework repository when public nodes consume it without an extra credential
- `[framework].ref` set to a full **40-character commit SHA**

The tool persists no token, PAT or reusable credential.

## Windows graphical setup

`Kristal-GitHub-Setup.pyw` provides a Tk-based initial installer and maintenance UI on Windows. It writes the same `network.toml` consumed by the CLI and invokes the same `doctor → plan → apply` reconciliation engine; there is no parallel GUI-only state. After `pip install .`, launch the `.pyw` directly or use the installed `kristal-github-setup` GUI entry point. See `WINDOWS_SETUP.md`.

## Workflow

```bash
cp examples/kristal-github.toml ./network.toml
# edit owner, network id, framework repository and pinned SHA

kristal-github doctor --config network.toml
kristal-github plan network.toml --out plan.json
kristal-github apply network.toml --plan plan.json --yes
kristal-github status network.toml
```

`apply --plan` refuses a stale plan when the observed desired-repository topology has changed. `reconcile` runs the same convergent engine without requiring a saved plan.

To add a repository later:

```bash
kristal-github repo network.toml \
  --name kristal-chemistry \
  --visibility public \
  --collection science \
  --yes
```

The new node receives an opaque persistent `urn:uuid:` identity and is added to `.kristal/network-registry.json` in the private hub. Subsequent account reconciliation projects the directory from both the declarative initial topology and this registry, so dynamic nodes are not lost.

## Managed-file safety

`.kristal/bootstrap-state.json` records the last applied hash of each managed node file. On reconciliation:

- missing managed file → create;
- exact desired content → no mutation;
- current content still equals the last managed value → safe update;
- current content differs from both → **conflict**, no overwrite.

`--adopt-managed` is an explicit repair/adoption operation. README files are create-only and topics are merged with existing user topics rather than replaced.

## Qualification

Generated qualification workflows:

- use read-only repository permissions;
- pin `actions/checkout`, `actions/setup-node` and `actions/upload-artifact` to exact commits;
- pin the Kristal Framework to the configured commit;
- validate the node/binding/directory descriptors;
- emit a qualification receipt tied to the candidate commit and framework commit.

Node qualification is path-scoped to `.kristal/**` and its own workflow, so a large Manager synchronization under `kristals/**` does not rerun node qualification for every content update. Formal publication can still dispatch qualification explicitly for the exact candidate commit.

## Collection ingest validation

Collection repositories additionally receive `.github/workflows/kristal-ingest.yml` and the managed validator `.kristal/tools/validate-read-surface.py`. This is the GitHub-side verifier for the read surface emitted by Local Kit 3.2.4+ and synchronized by Manager alpha.11+.

On changes under `kristals/**` it:

- validates the derived `kristals/index.json`;
- discovers only changed `kristals/<slug>/` roots;
- dynamically shards large batches while keeping the matrix below GitHub's practical job-count limit;
- validates shards in parallel (`max-parallel: 8`);
- verifies every hosted file size and SHA-256 from `.kristal/sync-manifest.json`;
- independently recomputes the Local Kit `surface_digest`;
- checks `AI_MANIFEST.json`, `ai/INDEX.json`, the AI entrypoint, state identity/commitment and materialization metadata;
- runs the pinned Framework `verify-state-v9` on the hosted State Snapshot;
- rejects unmanaged extra files inside an exact hosted read surface.

This validation is operational/derived. It does not turn the GitHub index or read surface into semantic authority.

## Publication

The publication workflow treats `state_file` as untrusted data rather than executable shell text. It resolves the path inside `GITHUB_WORKSPACE`, verifies the v9 state, builds a `kristal.publication-bundle/1.0`, verifies every local payload, then creates a **draft** GitHub Release targeted at the exact source commit.

When the selected state belongs to a Manager alpha.11+ hosted read surface, publication first validates that exact surface with the same managed collection validator. Old state-only collection entries remain supported as a compatibility path; publication still verifies their v9 state directly.

Before finalizing the Release it downloads the remote assets and verifies the bundle again. A retry against an existing publication succeeds only when the downloaded Publication Record and bundle match; otherwise it fails as a conflict.

`best_effort` Environments are not presented as an approval guarantee. Only `features.environments = "required"` makes the publication job depend on the `production` Environment.

## Feature modes

`immutable_releases`, `environments`, `custom_properties`, and `attestations` accept:

- `off` — not configured or claimed;
- `best_effort` — use when available but do not elevate it to a required guarantee;
- `required` — bootstrap/workflow fails when the guarantee cannot be supplied.

Host bindings only advertise optional activation/attestation surfaces when the bootstrap has an effective corresponding capability.

## Current scope

This alpha implements the draft.2 hardening/convergence milestone. It does not yet install a GitHub App, GHCR as a mandatory storage layer, or a central service, and it does not let AI write canonical knowledge directly.

## Ready defaults for Rejean-McCormick

The Windows setup wizard is prefilled for `Rejean-McCormick/KristalV10`, personal-account mode, stable network ID `urn:kristal:network:rejean-mccormick`, and the minimal topology `kristal-hub` (private), `kristal-public` (public), `kristal-private` (private). Personal-account mode intentionally does not create or modify the GitHub profile repository or a global `.github` repository. Push the framework to `main`, then use **Detect main SHA** before Doctor/Plan/Apply.


## Alpha.5 Windows preflight fix

Framework SHA verification now checks the exact Git commit object first and falls back to the repository commit endpoint. Doctor/Plan exposes the attempted endpoints and diagnostic reason instead of returning an opaque `blocked` status.

## alpha.10: GitHub read-surface ingest + multi-Kristal lifecycle

The Windows GUI has a **Lifecycle** tab and does not require PowerShell scripts for the operator flow.

The lifecycle is now centered on a **selected Local Kristal** rather than a repo-global `state/state-snapshot.json`:

```text
Local Kristal
  -> Manager synchronizes optimized AI/GitHub read surface
  -> GitHub Collection Ingest validates changed surfaces in shards
  -> Setup selects exact v9 State Snapshot for formal publication
  -> exact-commit qualification
  -> v10 publication Release
  -> independent bundle verification
  -> per-Kristal activation channel
```

### Kristal Manager bridge

The GUI reads `C:\mycode\Kristal\kristal-manager.json` (`kristal-local-registry/2.0`) when available. A selected entry contributes only operator metadata such as local path, slug and `publication_target`. It does **not** become semantic authority.

GitHub hosting/synchronization visibility and formal publication target remain independent. Kristal Manager owns the dynamic hosted read surface used by downstream systems and AI readers; Setup owns qualification/publication/activation. Neither hosting location nor visibility changes the semantic commitment.

You can also browse a Local Kristal folder directly if no Manager catalog is available.

### Multi-Kristal collection layout

A collection repository may host thousands of Kristals. Manager alpha.11+ uses a derived navigation index plus one optimized read surface per Kristal:

```text
kristals/
├── index.json
├── bateaux/
│   ├── AI_START_HERE.md
│   ├── AI_MANIFEST.json
│   ├── ai/
│   ├── canon/
│   ├── docs/
│   ├── sources/
│   ├── state/state-snapshot.json
│   └── .kristal/sync-manifest.json
├── cuisine/
└── finances/
```

The exact file projection is owned by Local Kit's `kristal.github-read-surface/1.0` contract. Manager transports that projection and updates `kristals/index.json`; Bootstrap validates it on GitHub. Large materialization bytes are not implicitly forced into Git.

### Publication selection

alpha.10 no longer treats the repo-global newest Release as the selected Kristal publication. Publication lookup is by exact `state_ref`, with independent bundle verification. Immediately after publish, the Release must also target the exact qualified collection commit.

This avoids selecting the wrong Release when several Kristals coexist in one collection.

### Activation

Activation remains separate from publication. The default channel is now per Kristal:

```text
public/<slug>/stable
private/<slug>/stable
```

The GUI validates the v9 activation transition with the pinned Framework, then advances a dedicated Git ref through a non-force fast-forward update. Existing channels preserve `previous_state`, `expected_previous`, and monotonic `sequence`. Re-activating the same state is idempotent.

When GitHub Environments are `best_effort`, the GUI also attempts to record a `production` Deployment for observability. `environments = "required"` is deliberately refused by the local activation path because a mandatory approval gate should be workflow-mediated.

### Local state discovery

For a selected Local Kristal the GUI recognizes, in order:

- `build/v9/state-snapshot.json`
- `state/state-snapshot.json`
- `.kristal/v9/state-snapshot.json`
- `state-snapshot.json`
- newest `release/v9/states/*.json`

The chosen file is always verified by the pinned `KristalV10` reference CLI before formal publication staging. Routine GitHub read-surface synchronization is owned by Kristal Manager, not Setup.

### Framework default

The current default/fallback framework repository name is `OWNER/KristalV10`; the active Windows preset remains `Rejean-McCormick/KristalV10` pinned to commit `27c0c7db3d79a4597c1c964fe8281fa35b5f858a`.
