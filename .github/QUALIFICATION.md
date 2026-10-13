# GitHub qualification model

Kristal separates normative authority from implementation diagnostics.

## Native authority

`Kristal Standard CI` runs the repository's native validation surface:

- `tools/validate_standard.py` across inherited v6-v9 and proposed v10 contracts;
- contract-set and knowledge-model bundle validation;
- documentation link/navigation validation;
- the JavaScript reference implementation tests, including v9 commitments, v10 hosting profiles and local lifecycle behavior.

The workflow stores the exact Git commit, Standard version and tool versions as validation evidence. It also runs a **read-only v10 profile consistency check** and negative tests. This validates the local Framework only; no real Manager, C1/C2, GitHub collection or reader deployment is qualified.

## Independent examiner

KristalDiag remains a separate examiner. The Framework does not treat KristalDiag as normative authority. Independent KristalDiag qualification remains separate and must be verified against a pinned exact Framework revision and the specific profiles it actually implements. Native Framework CI is not independent C1 qualification or evidence of permission to synchronize, publish or activate a Kristal.

## Release reproducibility

`Kristal Release Reproducibility` is manual. It validates the Standard, verifies the committed `REPO_MANIFEST.json`, builds the release twice and requires byte-identical archives before uploading release evidence.

## Compatibility posture

V9 uses `contracts/v9-compatibility-lock.json` to freeze inherited v6/v7/v8 normative and TCK surfaces. A v9 change that mutates a frozen inherited file must fail qualification rather than silently redefining compatibility.

Independent diagnostic disagreements must remain visible until the Standard and diagnostic agree on an explicit rule; CI must not suppress them merely to obtain a green result.

## GitHub host boundary

A public sync is already a disclosure, even when it is not a normative immutable publication. Scope, visibility and authorization must therefore be checked before the remote write. A structurally valid collection index does not establish independent C1/C2 trust. See [`docs/28_V10_ECOSYSTEM_ALIGNMENT.md`](../docs/28_V10_ECOSYSTEM_ALIGNMENT.md).
