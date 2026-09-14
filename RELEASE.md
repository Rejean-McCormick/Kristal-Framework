# Kristal Framework release process

Kristal uses **Git as the release identity**. The release tag names the version and the resolved commit SHA pins the exact repository content. `contract-set.manifest.json` is only a curated index of public contract surfaces; it is not a file inventory and it carries no per-file hashes.

## Release gate

From a clean checkout:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_release.py
mkdocs build --strict
```

All commands MUST pass before tagging a stable release.

## Release metadata

When changing the release version, update together:

- `VERSION`
- `kristal-release.json`
- `contract-set.manifest.json` (`release` field only when the version changes)
- `CHANGELOG.md`
- the corresponding status report under `docs/status/`

`contract-set.manifest.json` lists contract **surfaces** (directories/files), not every file in the repository.

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

python ./tools/validate_release.py
if ($LASTEXITCODE -ne 0) {
    throw "Kristal release validation failed."
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
  "version": "5.0.0-rc.1",
  "git_tag": "v5.0.0-rc.1",
  "git_commit": "<full SHA resolved from tag>",
  "canonicalization_profile": "kristal.v5:jcs-rfc8785"
}
```

Floating dependencies (`main`, `latest`, `5.x`) are not valid release locks.
