#!/usr/bin/env python3
"""Kristal Framework release-candidate validation gate."""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

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


def fail(msg: str) -> None:
    raise AssertionError(msg)


def check_required_files() -> None:
    required = [
        "VERSION", "CHANGELOG.md", "RELEASE.md", ".gitattributes", "kristal-release.json",
        "contract-set.manifest.json",
        "docs/Technical-Reference/kristal-docs-v5/00-overview/specification-status.md",
    ]
    for rel in required:
        if not (ROOT / rel).is_file(): fail(f"missing required release file: {rel}")


def check_json_and_schemas() -> None:
    for p in ROOT.rglob("*.json"):
        json.loads(p.read_text(encoding="utf-8"))
    for p in SCHEMAS.glob("*.json"):
        Draft202012Validator.check_schema(json.loads(p.read_text(encoding="utf-8")))


def check_examples() -> None:
    for ex_name, schema_name in EXAMPLE_SCHEMA.items():
        data = json.loads((EXAMPLES / ex_name).read_text(encoding="utf-8"))
        schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            e = errors[0]
            fail(f"{ex_name} !~ {schema_name}: {e.message} @ /{'/'.join(map(str,e.path))}")
        if str(data.get("schema_version")) != "5.0":
            fail(f"{ex_name}: schema_version must be 5.0")


def check_jcs_vectors() -> None:
    rc = subprocess.run(["node", str(ROOT / "tools/check_jcs_vectors.mjs")], cwd=ROOT)
    if rc.returncode:
        fail("JCS golden-vector conformance failed")


def check_schema_ids() -> None:
    seen=set()
    for p in SCHEMAS.glob("*.json"):
        d=json.loads(p.read_text(encoding="utf-8"))
        sid=d.get("$id")
        if not isinstance(sid,str) or not sid.startswith("https://kristal.org/schemas/v5/"):
            fail(f"{p.name}: invalid or missing v5 $id")
        if sid in seen: fail(f"duplicate schema $id: {sid}")
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

    surfaces = json.loads((ROOT / "contract-set.manifest.json").read_text(encoding="utf-8"))
    if surfaces.get("release") != version:
        fail("contract-set.manifest.json release does not match VERSION")

    seen = set()
    for section in ("normative_surfaces", "profile_surfaces", "conformance_surfaces", "informative_surfaces"):
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


def check_alignment() -> None:
    rc=subprocess.run([sys.executable, str(ROOT/'tools/check_version_alignment.py')], cwd=ROOT)
    if rc.returncode: fail("version alignment check failed")


def check_docs() -> None:
    rc=subprocess.run([sys.executable, str(ROOT/'tools/check_docs.py')], cwd=ROOT)
    if rc.returncode: fail("documentation navigation/link validation failed")


def main() -> int:
    checks=[
        ("required release files", check_required_files),
        ("JSON parsing and schema metaschema", check_json_and_schemas),
        ("schema IDs", check_schema_ids),
        ("examples against schemas", check_examples),
        ("JCS golden hashes", check_jcs_vectors),
        ("version alignment", check_alignment),
        ("documentation navigation and links", check_docs),
        ("release metadata and contract surfaces", check_release_metadata),
    ]
    for name, fn in checks:
        fn(); print(f"PASS: {name}")
    print("Kristal release validation: PASS")
    return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
