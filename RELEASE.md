# Kristal Framework release process

Kristal uses **Git as the release identity**. The release tag names the version and the resolved commit SHA pins the exact repository content. `contract-set.manifest.json` is only a curated index of public contract surfaces; it is not a file inventory and it carries no per-file hashes.

## Release gate

From a clean checkout:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_all.py
```

The complete validation command MUST pass before tagging any release candidate or stable release.

This command validates **framework/release integrity**, executable framework-vector conformance, and the strict documentation build. They do not, by themselves, establish that an Exchange compiler, Runtime Pack builder/verifier, Da’at implementation, or ecosystem integration is implementation-conformant. Any implementation conformance claimed for a release MUST also satisfy the applicable executable acceptance tests and the current status report under `docs/status/`.

## Release metadata

When changing the release version, update together:

- `VERSION`
- `kristal-release.json`
- `contract-set.manifest.json` (`release` field only when the version changes)
- `release-lock.example.json`
- `CHANGELOG.md`
- the corresponding status report under `docs/status/`

`contract-set.manifest.json` lists contract **surfaces** (directories/files), not every file in the repository.

Deprecated generated manifest artifacts MUST be absent before release:

- `schema-set.manifest.json`;
- `tools/build_manifests.py`.

They belong to the retired per-file-hash release model and MUST NOT be regenerated. Schema bytes are pinned by the Git tag + commit SHA, while `contract-set.manifest.json` remains a curated surface index.

## Tagging

The release manifest does not self-embed the Git commit SHA. After the release commit exists, create an annotated tag and resolve it to the immutable commit.

### PowerShell 7

Run this as one block from the authoritative repository root:

```powershell
$ErrorActionPreference = "Stop"
$Version = (Get-Content ./VERSION -Raw).Trim()
$Tag = "v$Version"

if (-not (Test-Path .git)) {
    throw "Run this from the root of the Kristal Git repository."
}

python ./tools/validate_all.py
if ($LASTEXITCODE -ne 0) {
    throw "Kristal complete validation suite failed."
}

$Dirty = git status --porcelain
if ($Dirty) {
    throw "Working tree is not clean. Commit the release changes first."
}

if (git tag --list $Tag) {
    throw "Tag $Tag already exists locally."
}

git tag -a $Tag -m "Kristal Framework $Version"
if ($LASTEXITCODE -ne 0) {
    throw "Tag creation failed."
}

$Commit = (git rev-list -n 1 $Tag).Trim()
if (-not $Commit) {
    throw "Unable to resolve $Tag to a commit."
}

Write-Host "Kristal release ready"
Write-Host "Version : $Version"
Write-Host "Tag     : $Tag"
Write-Host "Commit  : $Commit"

git push origin HEAD
if ($LASTEXITCODE -ne 0) {
    throw "Branch push failed."
}

git push origin $Tag
if ($LASTEXITCODE -ne 0) {
    throw "Tag push failed."
}
```

### Optional signed tag

If Git signing is configured and you specifically want a cryptographically signed Git tag, replace:

```powershell
git tag -a $Tag -m "Kristal Framework $Version"
```

with:

```powershell
git tag -s $Tag -m "Kristal Framework $Version"
git tag --verify $Tag
```

A signed tag is optional for the framework release process. Do not block a release candidate merely because local GPG signing is not configured.

## Downstream lock

Consumers SHOULD record the small release identity:

```json
{
  "version": "5.0.0-rc.2",
  "git_tag": "v5.0.0-rc.2",
  "git_commit": "<full SHA resolved from tag>",
  "canonicalization_profile": "kristal.v5:jcs-rfc8785",
  "canonicalization_version": "1"
}
```

Floating dependencies (`main`, `latest`, `5.x`) are not valid release locks.

## Source archive hygiene

`tools/build_release_archive.py` builds release archives from **Git-tracked files only**. Untracked diagnostics, local notes, `.levelupdiag/`, virtual environments, build output, and other workstation state MUST NOT affect release bytes. `CODE_SNAPSHOT_MANIFEST.md` is a local/export snapshot aid and is intentionally excluded from framework release archives.

The archive builder MUST refuse to run outside a Git work tree. For a release build, the working tree SHOULD be clean and the release tag MUST ultimately resolve to the committed bytes being archived.
