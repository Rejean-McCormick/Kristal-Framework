# GitHub qualification model

Kristal separates normative authority from implementation diagnostics.

## Native authority

`Kristal Standard CI` runs the repository's native validation surface:

- `tools/validate_standard.py` across frozen v6-v8 and active v9 draft contracts;
- contract-set and knowledge-model bundle validation;
- documentation link/navigation validation;
- the JavaScript reference implementation tests, including v9 commitments and local lifecycle behavior.

The workflow stores the exact Git commit, Standard version and tool versions as validation evidence.

## Independent examiner

KristalDiag remains a separate examiner. The Framework does not treat KristalDiag as normative authority. Until KristalDiag gains explicit v9 profiles, native Framework CI is the executable v9 draft qualification surface and KristalDiag continues to qualify only the profiles it explicitly implements.

## Release reproducibility

`Kristal Release Reproducibility` is manual. It validates the Standard, verifies the committed `REPO_MANIFEST.json`, builds the release twice and requires byte-identical archives before uploading release evidence.

## Compatibility posture

V9 uses `contracts/v9-compatibility-lock.json` to freeze inherited v6/v7/v8 normative and TCK surfaces. A v9 change that mutates a frozen inherited file must fail qualification rather than silently redefining compatibility.

Independent diagnostic disagreements must remain visible until the Standard and diagnostic agree on an explicit rule; CI must not suppress them merely to obtain a green result.
