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

At repository/node level it installs `.kristal/node.json`, `.kristal/bindings/github.json`, `.kristal/capabilities.json`, `.kristal/bootstrap-state.json`, qualification workflow/receipt support, publication workflow, topics and supported GitHub features.

The UI never stores a GitHub token. Authentication remains owned by GitHub CLI.
