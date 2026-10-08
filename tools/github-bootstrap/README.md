# Kristal GitHub Bootstrap 1.1.0-alpha.2

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
  └─ verifiable publication workflow
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

## Publication

The publication workflow treats `state_file` as untrusted data rather than executable shell text. It resolves the path inside `GITHUB_WORKSPACE`, verifies the v9 state, builds a `kristal.publication-bundle/1.0`, verifies every local payload, then creates a **draft** GitHub Release targeted at the exact source commit.

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
