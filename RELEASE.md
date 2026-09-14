# Kristal Framework release process

## Release gate

From a clean checkout:

```bash
python -m pip install -r requirements-dev.txt
python tools/build_manifests.py --check
python tools/validate_release.py
mkdocs build --strict
```

All commands MUST pass before tagging a stable release.

Build the deterministic distributable archive after validation:

```bash
python tools/build_release_archive.py
```

The generated `.zip.sha256` sidecar authenticates the exact distributed archive. The archive digest is intentionally not embedded inside the archive.

## Create or refresh manifests

When an intentional contract change is made:

```bash
python tools/build_manifests.py
python tools/validate_release.py
```

Commit the changed contracts and generated manifests together.

## Tagging

The release manifest does not self-embed the Git commit SHA. After the release commit exists, create a signed annotated tag:

```bash
git tag -s v5.0.0-rc.1 -m "Kristal Framework v5.0.0-rc.1"
git push origin v5.0.0-rc.1
```

For stable `v5.0.0`, repeat after updating `VERSION`, `kristal-release.json`, and the changelog and after all release gates pass.

## Downstream lock

Consumers SHOULD record:

```json
{
  "version": "5.0.0",
  "git_tag": "v5.0.0",
  "git_commit": "<full SHA resolved from signed tag>",
  "contract_set_digest": "sha256:<from kristal-release.json>",
  "schema_set_digest": "sha256:<from kristal-release.json>",
  "canonicalization_profile": "kristal.v5:jcs-rfc8785",
  "canonicalization_version": "1"
}
```

Floating pins (`main`, `latest`, `5.x`) are not valid release locks.
