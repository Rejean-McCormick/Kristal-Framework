#!/usr/bin/env python3
"""Kristal v5 framework-vector conformance gate.

This validates the TCK corpus itself. It deliberately does not claim that an
external Kristal compiler/verifier is conformant unless such an implementation
is tested separately.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs" / "Technical-Reference" / "kristal-docs-v5"
VECTORS = BASE / "09-test-vectors"
SCHEMAS = BASE / "02-schemas"


def fail(msg: str) -> None:
    raise AssertionError(msg)


def run_node_tck() -> None:
    rc = subprocess.run(["node", str(ROOT / "tools" / "kristal_tck.mjs")], cwd=ROOT)
    if rc.returncode:
        fail("Kristal TCK framework vectors failed")


def validate_runtime_pack_vectors() -> None:
    doc = json.loads((VECTORS / "runtime-pack" / "vectors.json").read_text(encoding="utf-8"))
    schema = json.loads((SCHEMAS / "runtime-pack-manifest.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for vector in doc.get("vectors", []):
        errors = sorted(validator.iter_errors(vector["input"]), key=lambda e: list(e.path))
        if errors:
            e = errors[0]
            fail(
                f"{vector.get('id')}: Runtime Pack fixture violates schema: "
                f"{e.message} @ /{'/'.join(map(str, e.path))}"
            )
        if vector["input"].get("runtime_pack_version") != "5.0.0":
            fail(f"{vector.get('id')}: core TCK runtime_pack_version must be 5.0.0")


def validate_exchange_vectors() -> None:
    doc = json.loads((VECTORS / "exchange" / "vectors.json").read_text(encoding="utf-8"))
    if doc.get("id_profile") != "kristal.v5:exchange-id-core@1":
        fail("unexpected Exchange TCK identity profile")

    ids = set()
    for vector in doc.get("vectors", []):
        vid = vector.get("id")
        if not isinstance(vid, str) or not vid:
            fail("Exchange vector missing id")
        if vid in ids:
            fail(f"duplicate Exchange vector id: {vid}")
        ids.add(vid)
        obj = vector.get("input")
        if not isinstance(obj, dict):
            fail(f"{vid}: input must be an object")
        if obj.get("schema_version") != "5.0":
            fail(f"{vid}: schema_version must be 5.0")
        if obj.get("canonicalization_profile") != "kristal.v5:jcs-rfc8785":
            fail(f"{vid}: canonicalization_profile mismatch")
        if obj.get("canonicalization_version") != "1":
            fail(f"{vid}: canonicalization_version mismatch")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", vector.get("expected_kristal_id", "")):
            fail(f"{vid}: expected_kristal_id malformed")

        artifact_type = obj.get("artifact_type")
        artifact_status = obj.get("artifact_status")
        if artifact_type == "reference_exchange":
            if artifact_status not in {"reference", "deprecated", "superseded", "revoked"}:
                fail(f"{vid}: reference_exchange has invalid lifecycle status {artifact_status!r}")
            if not obj.get("authority_recognition_refs"):
                fail(f"{vid}: reference_exchange requires authority_recognition_refs")
        elif artifact_type == "working_exchange":
            if artifact_status == "reference":
                fail(f"{vid}: working_exchange cannot have reference lifecycle status")
        else:
            fail(f"{vid}: unsupported Exchange artifact_type {artifact_type!r}")


def validate_runtime_pack_profile() -> None:
    doc = json.loads((VECTORS / "runtime-pack" / "vectors.json").read_text(encoding="utf-8"))
    profile = doc.get("id_profile", {})
    if profile.get("id") != "kristal.v5:runtime-pack-id-core@1":
        fail("unexpected Runtime Pack TCK identity profile")
    required_exclusions = {
        "/runtime_pack_id",
        "/created_at",
        "/build/build_id",
        "/compiler/build_platform",
        "/integrity/pack_hash",
        "/integrity/manifest_hash",
    }
    actual = set(profile.get("exclude_json_pointers", []))
    if actual != required_exclusions:
        fail(f"Runtime Pack TCK identity exclusions drifted: {sorted(actual)}")


def validate_acceptance_doc_version() -> None:
    p = BASE / "03-reproducibility" / "reproducibility-acceptance-tests.md"
    text = p.read_text(encoding="utf-8")
    if re.search(r"\bv3\b", text):
        fail("v5 reproducibility acceptance tests still contain stale v3 normative wording")


def main() -> int:
    checks = [
        ("Exchange vector declarations", validate_exchange_vectors),
        ("Runtime Pack vector schema + format conformance", validate_runtime_pack_vectors),
        ("Runtime Pack identity profile lock", validate_runtime_pack_profile),
        ("v5 acceptance-test version alignment", validate_acceptance_doc_version),
        ("executable TCK golden vectors", run_node_tck),
    ]
    for name, fn in checks:
        fn()
        print(f"PASS: {name}")
    print("Kristal framework-vector conformance: PASS")
    print("Kristal implementation conformance: NOT TESTED (no compiler/verifier adapter supplied)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
