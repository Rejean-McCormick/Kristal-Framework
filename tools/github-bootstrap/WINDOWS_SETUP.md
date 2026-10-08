# Windows setup — Kristal GitHub Bootstrap

`Kristal-GitHub-Setup.pyw` is the graphical installer/reconciler for the initial GitHub integration.
It uses the same bootstrap engine as the `kristal-github` CLI; it does not maintain a second configuration model.

## Prerequisites

1. Python 3.11 or newer.
2. GitHub CLI (`gh`) installed.
3. Authenticate once with `gh auth login`, then verify with `gh auth status`.
4. Publish the Kristal Framework repository first and obtain the exact 40-character commit SHA that the hosted nodes will pin.

For a public network node, the framework repository should be publicly readable unless you deliberately provide another credential path.

## Install and launch

From PowerShell in this directory:

```powershell
py -3.11 -m pip install .
pyw -3.11 .\Kristal-GitHub-Setup.pyw
```

If the Windows Python launcher does not expose `pyw`, run:

```powershell
pythonw .\Kristal-GitHub-Setup.pyw
```

## Wizard workflow

1. Enter the GitHub owner and account type (`organization` or `user`).
2. Keep a stable network ID. Do not change it when repositories are renamed.
3. Enter the framework repository and click **Detect main SHA**, or paste the exact immutable commit SHA.
4. Choose the private hub plus the initial public and private collection repository names.
5. Leave optional GitHub features on `best_effort` for the first pilot unless you specifically require the guarantee.
6. Click **Doctor**. Fix authentication/permission/framework errors first.
7. Click **Plan** and review the proposed repositories/actions.
8. Click **Apply**. The tool rechecks observed state before mutation.
9. Use the **Add repository** tab later for additional collections/directories. New nodes are registered in the private hub.

The generated `network.toml` remains the desired configuration source. Keep it under private version control or in your administrative backup.

## What Apply installs

At account/organization level it can establish the `.github` integration/profile, an optional private organization profile, and the private Kristal hub/directory.

At repository/node level it installs `.kristal/node.json`, `.kristal/bindings/github.json`, `.kristal/capabilities.json`, `.kristal/bootstrap-state.json`, qualification workflow/receipt support, publication workflow, topics and supported GitHub features. Collection nodes additionally receive the sharded `kristal-ingest.yml` workflow and `.kristal/tools/validate-read-surface.py` validator for Manager-synchronized AI/GitHub read surfaces.

The UI never stores a GitHub token. Authentication remains owned by GitHub CLI.

### Current prefilled host

- Owner: `Rejean-McCormick`
- Account type: `user`
- Framework: `Rejean-McCormick/KristalV10`
- Stable network ID: `urn:kristal:network:rejean-mccormick`
- Local framework working tree: `C:\mycode\Kristal\KristalV10` (informational; the wizard operates on GitHub, not directly on this path)

The config and plan files now default beside the launcher instead of the process working directory.

## Lifecycle tab (alpha.10)

Open `Kristal-GitHub-Setup.pyw` and select **Lifecycle**. The default workspace is `C:\mycode\Kristal`, and the default Manager catalog is `C:\mycode\Kristal\kristal-manager.json`.

1. Click **Refresh** beside **Manager Local Kristal** and select the Local Kristal you want. You may also choose **Folder** and browse directly.
2. Confirm the **Publication target** (`public` or `private`). If the Manager entry already declares `publication_target`, Setup requires the same target instead of silently overriding it.
3. **Qualify collections** verifies the public/private host repositories and qualification receipts. Routine content synchronization is validated separately by the collection ingest workflow.
4. **Publish selected Local** verifies the Local v9 State Snapshot, stages its exact bytes at `kristals/<slug>/state/state-snapshot.json` when needed, validates an existing Manager read surface when present, qualifies the exact commit, publishes the v10 bundle and independently verifies the Release.
5. **Verify selected publication** resolves the Release by the selected `state_ref`, not by "latest Release".
6. **Activate selected** uses a per-Kristal channel such as `public/bateaux/stable` or `private/finances/stable`.
7. **Verify active channel** re-downloads the Release referenced by the activation and verifies that the active state is the selected Local Kristal state.

Routine GitHub synchronization/hosting is not owned by Setup. Kristal Manager owns the dynamic read surface consumed by downstream systems; Setup owns qualification, formal publication and activation.

No `.ps1` file is part of this workflow. The `.pyw` invokes `gh`, `git` and `node` directly, and Windows subprocesses are started without transient console windows.
