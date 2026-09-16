#!/usr/bin/env python3
"""Kristal Framework release-candidate validation gate."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs" / "Technical-Reference" / "kristal-docs-v5"
SCHEMAS = BASE / "02-schemas"
EXAMPLES = BASE / "10-examples"
JCS = BASE / "09-test-vectors" / "jcs"

EXAMPLE_SCHEMA = {
    "authority-registry.example.json": "authority-registry.schema.json",
    "claim-ir.example.json": "claim-ir.schema.json",
    "exchange-federation-manifest.example.json": "exchange-federation-manifest.schema.json",
    "exchange-shard-manifest.example.json": "exchange-shard-manifest.schema.json",
    "exchange.example.json": "exchange-manifest.schema.json",
    "medical-authority-recognition.example.json": "authority-recognition.schema.json",
    "plural-authority-federation.example.json": "exchange-federation-manifest.schema.json",
    "reader-policy-validated-only.example.json": "reader-policy.schema.json",
    "resolved-claim-ir.example.json": "resolved-claim-ir.schema.json",
    "revocations.example.json": "revocations.schema.json",
    "runtime-pack-manifest.example.json": "runtime-pack-manifest.schema.json",
    "structured-epistemic-state.example.json": "structured-epistemic-state.schema.json",
    "validation-report.example.json": "validation-report.schema.json",
    "divergent-fork.example.json": "structured-epistemic-state.schema.json",
    "independent-research-evidence-bundle.example.json": "structured-epistemic-state.schema.json",
    "mythology-corpus-kristal.example.json": "structured-epistemic-state.schema.json",
    "publisher-declared-system-kristal.example.json": "structured-epistemic-state.schema.json",
    "wikidata-seed-kristal.example.json": "structured-epistemic-state.schema.json",
}

RETIRED_RELEASE_ARTIFACTS = (
    "schema-set.manifest.json",
    "tools/build_manifests.py",
)


def fail(msg: str) -> None:
    raise AssertionError(msg)


def check_required_files() -> None:
    required = [
        "VERSION",
        "CHANGELOG.md",
        "RELEASE.md",
        ".gitattributes",
        "kristal-release.json",
        "contract-set.manifest.json",
        "release-lock.example.json",
        "docs/Technical-Reference/kristal-docs-v5/00-overview/specification-status.md",
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            fail(f"missing required release file: {rel}")


def check_retired_release_artifacts() -> None:
    present = [rel for rel in RETIRED_RELEASE_ARTIFACTS if (ROOT / rel).exists()]
    if present:
        fail(
            "retired per-file release artifacts are still present: "
            + ", ".join(present)
            + "; remove them instead of regenerating them"
        )


def check_json_and_schemas() -> None:
    for p in ROOT.rglob("*.json"):
        # Generated build output is never part of the source validation surface.
        if "dist" in p.relative_to(ROOT).parts or "site" in p.relative_to(ROOT).parts:
            continue
        json.loads(p.read_text(encoding="utf-8"))
    for p in SCHEMAS.glob("*.json"):
        Draft202012Validator.check_schema(json.loads(p.read_text(encoding="utf-8")))


def check_format_checker_enforcement() -> None:
    """Fail closed when optional JSON Schema format validators are unavailable.

    jsonschema intentionally treats unknown/unavailable format checks as valid.
    Kristal release validation requires date-time and URI checks to be active,
    so probe both invalid and valid values before validating repository examples.
    """
    checker = FormatChecker()
    probes = [
        ("date-time", "not-a-date-time", "2026-09-16T12:34:56Z"),
        ("uri", "not a uri", "https://kristal.org/validation-probe"),
    ]
    for format_name, invalid_value, valid_value in probes:
        schema = {"type": "string", "format": format_name}
        validator = Draft202012Validator(schema, format_checker=checker)
        if not list(validator.iter_errors(invalid_value)):
            fail(
                f"JSON Schema format checker is not enforcing {format_name}; "
                "install development dependencies from requirements-dev.txt"
            )
        valid_errors = list(validator.iter_errors(valid_value))
        if valid_errors:
            fail(
                f"JSON Schema format checker rejects the valid {format_name} "
                f"probe: {valid_errors[0].message}"
            )

def check_examples() -> None:
    format_checker = FormatChecker()
    for ex_name, schema_name in EXAMPLE_SCHEMA.items():
        data = json.loads((EXAMPLES / ex_name).read_text(encoding="utf-8"))
        schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
        errors = sorted(
            Draft202012Validator(schema, format_checker=format_checker).iter_errors(data),
            key=lambda e: list(e.path),
        )
        if errors:
            e = errors[0]
            fail(f"{ex_name} !~ {schema_name}: {e.message} @ /{'/'.join(map(str, e.path))}")
        if str(data.get("schema_version")) != "5.0":
            fail(f"{ex_name}: schema_version must be 5.0")


def check_jcs_vectors() -> None:
    rc = subprocess.run(["node", str(ROOT / "tools/check_jcs_vectors.mjs")], cwd=ROOT)
    if rc.returncode:
        fail("JCS golden-vector conformance failed")


def check_schema_ids() -> None:
    seen = set()
    for p in SCHEMAS.glob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        sid = d.get("$id")
        if not isinstance(sid, str) or not sid.startswith("https://kristal.org/schemas/v5/"):
            fail(f"{p.name}: invalid or missing v5 $id")
        if sid in seen:
            fail(f"duplicate schema $id: {sid}")
        seen.add(sid)


def check_release_metadata() -> None:
    release = json.loads((ROOT / "kristal-release.json").read_text(encoding="utf-8"))
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if release.get("version") != version:
        fail("VERSION != kristal-release.json version")
    if release.get("git", {}).get("tag") != f"v{version}":
        fail("release tag does not match VERSION")
    if release.get("git", {}).get("commit") is not None:
        fail("release manifest must not self-embed a Git commit")
    if release.get("canonicalization_profile") != "kristal.v5:jcs-rfc8785":
        fail("release canonicalization_profile must be kristal.v5:jcs-rfc8785")
    if release.get("canonicalization_version") != "1":
        fail("release canonicalization_version must be 1")

    lock = json.loads((ROOT / "release-lock.example.json").read_text(encoding="utf-8"))
    if lock.get("version") != version or lock.get("git_tag") != f"v{version}":
        fail("release-lock.example.json version/tag does not match VERSION")
    if lock.get("canonicalization_profile") != release.get("canonicalization_profile"):
        fail("release lock canonicalization_profile mismatch")
    if lock.get("canonicalization_version") != release.get("canonicalization_version"):
        fail("release lock canonicalization_version mismatch")

    surfaces = json.loads((ROOT / "contract-set.manifest.json").read_text(encoding="utf-8"))
    if surfaces.get("format") != "kristal.contract-surfaces/v1":
        fail("unexpected contract-set.manifest.json format")
    if surfaces.get("release") != version:
        fail("contract-set.manifest.json release does not match VERSION")

    seen = set()
    for section in (
        "normative_surfaces",
        "profile_surfaces",
        "conformance_surfaces",
        "informative_surfaces",
    ):
        values = surfaces.get(section)
        if not isinstance(values, list):
            fail(f"contract-set.manifest.json missing list: {section}")
        for entry in values:
            path = entry.get("path") if isinstance(entry, dict) else None
            name = entry.get("name") if isinstance(entry, dict) else None
            if not isinstance(path, str) or not path:
                fail(f"invalid contract surface path in {section}")
            if not isinstance(name, str) or not name:
                fail(f"invalid contract surface name in {section}")
            if path in seen:
                fail(f"duplicate contract surface path: {path}")
            seen.add(path)
            if not (ROOT / path).exists():
                fail(f"contract surface does not exist: {path}")


def check_cross_document_invariants() -> None:
    """Guard a few high-value invariants that previously drifted across docs/schema/TCK."""
    runtime_docs = [
        BASE / "01-core-spec" / "kristal-v5-core-spec.md",
        BASE / "00-overview" / "conformance-and-alignment.md",
        BASE / "03-reproducibility" / "allowed-runtime-pack-policies.md",
    ]
    stale_runtime_version = re.compile(r'runtime_pack_version(?:"\s*:\s*"|\s*=\s*)5\.0(?!\.)')
    for p in runtime_docs:
        text = p.read_text(encoding="utf-8")
        if stale_runtime_version.search(text):
            fail(f"{p.relative_to(ROOT)} still uses runtime_pack_version 5.0; use 5.0.0")

    konnaxion = (BASE / "06-integration" / "konnaxion-distribution-contract.md").read_text(encoding="utf-8")
    if 'artifact_type = "runtime_pack"' in konnaxion:
        fail("Konnaxion distribution contract must use artifact_type = runtime_pack_manifest")

    exchange_schema = json.loads((SCHEMAS / "exchange-manifest.schema.json").read_text(encoding="utf-8"))
    rules = exchange_schema.get("allOf", [])

    def rule_for(artifact_type: str) -> dict:
        for rule in rules:
            if_const = (rule.get("if", {}).get("properties", {}).get("artifact_type", {}).get("const"))
            if if_const == artifact_type:
                return rule.get("then", {})
        fail(f"exchange schema missing conditional rule for {artifact_type}")
        return {}

    reference_rule = rule_for("reference_exchange")
    if reference_rule.get("anyOf"):
        fail("reference_exchange must require authority_recognition_refs; validation_refs alone cannot qualify it")
    if "authority_recognition_refs" not in reference_rule.get("required", []):
        fail("reference_exchange schema does not require authority_recognition_refs")
    reference_statuses = set(reference_rule.get("properties", {}).get("artifact_status", {}).get("enum", []))
    if "recognized" in reference_statuses or "reference" not in reference_statuses:
        fail("reference_exchange lifecycle statuses are not aligned")

    working_rule = rule_for("working_exchange")
    working_statuses = set(working_rule.get("properties", {}).get("artifact_status", {}).get("enum", []))
    if "recognized" not in working_statuses or "reference" in working_statuses:
        fail("working_exchange lifecycle statuses are not aligned")


def check_alignment() -> None:
    rc = subprocess.run([sys.executable, str(ROOT / "tools/check_version_alignment.py")], cwd=ROOT)
    if rc.returncode:
        fail("version alignment check failed")


def check_docs() -> None:
    rc = subprocess.run([sys.executable, str(ROOT / "tools/check_docs.py")], cwd=ROOT)
    if rc.returncode:
        fail("documentation navigation/link validation failed")


def main() -> int:
    checks = [
        ("required release files", check_required_files),
        ("retired release artifacts absent", check_retired_release_artifacts),
        ("JSON parsing and schema metaschema", check_json_and_schemas),
        ("schema IDs", check_schema_ids),
        ("JSON Schema format checker enforcement", check_format_checker_enforcement),
        ("examples against schemas + formats", check_examples),
        ("JCS golden hashes", check_jcs_vectors),
        ("version alignment", check_alignment),
        ("documentation navigation and links", check_docs),
        ("release metadata and contract surfaces", check_release_metadata),
        ("cross-document contract invariants", check_cross_document_invariants),
    ]
    for name, fn in checks:
        fn()
        print(f"PASS: {name}")
    print("Kristal framework/release integrity validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
