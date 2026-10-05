# GitHub qualification model

Kristal separates normative authority from implementation diagnostics.

## Native authority

`Kristal Standard CI` runs the repository's own normative validation surface:

- `tools/validate_standard.py`
- contract-set validation
- documentation link/navigation validation
- the JavaScript reference implementation tests

The workflow stores the exact Git commit, Standard version and tool versions as
an artifact with the validation log.

## Independent examiner

KristalDiag remains a separate examiner. Its GitHub workflow should test the
frozen v6/v7 semantic substrate independently. It must **not** be described as
the authority for v8 language/query semantics until KristalDiag itself gains
explicit v8 profiles.

## Release reproducibility

`Kristal Release Reproducibility` is manual. It validates the Standard, verifies
the committed `REPO_MANIFEST.json`, builds the release twice and requires the
two archives to be byte-identical before uploading the release evidence.

## Current independent-diagnostic finding

Against the 2026-10-04 snapshots, the native v8 validation passes, while
KristalDiag 0.7.0 `V7-Projection` reports K02 FAIL on the two
`v6-compatible-projection.example.json` files. Their declared v6 state/content
hash equals the base v6 state hash, while KristalDiag's v6 hash target includes
`extensions.kristal_v7` because the v6 core excludes only `state_id`,
`content_hash`, and `signatures`.

Do not suppress this finding in CI. Resolve the semantic/hash rule explicitly
in either the Standard vectors/specification or KristalDiag, then keep a
regression test for the chosen rule.
