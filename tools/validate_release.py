#!/usr/bin/env python3
"""Kristal Standard v6 release integrity gate."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT / "docs" / "Technical-Reference" / "kristal-docs-v6"
V5 = ROOT / "docs" / "Technical-Reference" / "kristal-docs-v5"
V6_SCHEMA = ROOT / "schemas" / "kristal-state.schema.json"
V6_DOC_SCHEMA = V6 / "02-schemas" / "kristal-state.schema.json"
V6_EXAMPLE = V6 / "10-examples" / "kristal-state.example.json"


def fail(msg: str) -> None:
    raise AssertionError(msg)


def canonical_bundle_hash(contract: dict) -> str:
    core = dict(contract)
    core.pop("bundle_sha256", None)
    payload = json.dumps(core, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def check_required_files() -> None:
    required = [
        "VERSION", "README.md", "CHANGELOG.md", "RELEASE.md", "kristal-release.json",
        "contract-set.manifest.json", "knowledge-model-contract.v1.json",
        "knowledge-model-contract.v2.json", "release-lock.example.json",
        "docs/Technical-Reference/kristal-docs-v6/01-core-spec/kristal-v6-core-spec.md",
        "schemas/kristal-state.schema.json",
        "docs/Technical-Reference/kristal-docs-v6/02-schemas/kristal-state.schema.json",
        "docs/Technical-Reference/kristal-docs-v6/10-examples/kristal-state.example.json",
        "docs/Technical-Reference/kristal-docs-v5/02-schemas/structured-epistemic-state.schema.json",
    ]
    for rel in required:
        if not (ROOT / rel).is_file(): fail(f"missing required file: {rel}")


def check_json_and_schemas() -> None:
    for p in ROOT.rglob("*.json"):
        if any(part in {"dist", "site"} for part in p.relative_to(ROOT).parts): continue
        json.loads(p.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(json.loads(V6_SCHEMA.read_text(encoding="utf-8")))
    if V6_SCHEMA.read_bytes() != V6_DOC_SCHEMA.read_bytes(): fail("root v6 schema and documentation schema copy drifted")
    for p in (V5 / "02-schemas").glob("*.json"):
        Draft202012Validator.check_schema(json.loads(p.read_text(encoding="utf-8")))


def check_v6_example() -> None:
    schema = json.loads(V6_SCHEMA.read_text(encoding="utf-8"))
    data = json.loads(V6_EXAMPLE.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data), key=lambda e:list(e.path))
    if errors:
        e=errors[0]; fail(f"v6 example violates schema: {e.message} @ /{'/'.join(map(str,e.path))}")
    if data.get("schema_version") != "6.0" or data.get("artifact_type") != "kristal_state":
        fail("v6 fixture must be schema_version 6.0 / artifact_type kristal_state")


def check_release_metadata() -> None:
    version=(ROOT/"VERSION").read_text(encoding="utf-8").strip()
    if version != "6.0.0": fail(f"unexpected VERSION {version}")
    release=json.loads((ROOT/"kristal-release.json").read_text(encoding="utf-8"))
    if release.get("version") != version: fail("VERSION != kristal-release.json version")
    if release.get("core_version") != "6.0": fail("core_version must be 6.0")
    if release.get("canonical_artifact") != "kristal_state": fail("canonical_artifact must be kristal_state")
    if release.get("canonicalization_profile") != "kristal.v6:jcs-rfc8785": fail("canonicalization profile mismatch")
    if release.get("canonicalization_version") != "1": fail("canonicalization version mismatch")
    if release.get("git",{}).get("tag") != "v6.0.0": fail("release tag mismatch")
    if release.get("git",{}).get("commit") is not None: fail("release manifest must not self-embed commit")
    lock=json.loads((ROOT/"release-lock.example.json").read_text(encoding="utf-8"))
    if lock.get("version") != version or lock.get("git_tag") != "v6.0.0": fail("release lock mismatch")


def check_contract_surfaces() -> None:
    doc=json.loads((ROOT/"contract-set.manifest.json").read_text(encoding="utf-8"))
    if doc.get("release") != "6.0.0" or doc.get("core_schema_line") != "6.0": fail("contract manifest version mismatch")
    if doc.get("canonical_artifact") != "kristal_state": fail("contract manifest canonical artifact mismatch")
    seen=set()
    for section in ("normative_surfaces","profile_surfaces","conformance_surfaces","informative_surfaces"):
        vals=doc.get(section)
        if not isinstance(vals,list): fail(f"missing contract section {section}")
        for e in vals:
            path=e.get("path") if isinstance(e,dict) else None
            if not path or path in seen: fail(f"invalid/duplicate contract path: {path}")
            seen.add(path)
            if not (ROOT/path).exists(): fail(f"contract surface missing: {path}")


def check_knowledge_bundle() -> None:
    doc=json.loads((ROOT/"knowledge-model-contract.v2.json").read_text(encoding="utf-8"))
    if doc.get("format") != "kristal.knowledge-model-contract/v2": fail("unexpected v2 knowledge contract format")
    if doc.get("release") != "6.0.0" or doc.get("kristal_state") != "6.0": fail("v2 knowledge contract version mismatch")
    if doc.get("canonicalization_profile") != "kristal.v6:jcs-rfc8785": fail("v2 knowledge contract canonicalization mismatch")
    if doc.get("bundle_sha256") != canonical_bundle_hash(doc): fail("v2 bundle_sha256 mismatch")
    for e in doc.get("files",[]):
        p=ROOT/e["path"]
        if not p.is_file(): fail(f"v2 contract file missing: {e['path']}")
        b=p.read_bytes(); h="sha256:"+hashlib.sha256(b).hexdigest()
        if h != e.get("sha256") or len(b) != e.get("bytes"): fail(f"v2 contract file drift: {e['path']}")


def check_v5_bundle_frozen() -> None:
    # Frozen hash from the supplied 5.0.0-rc.3 tree.
    expected="a1efd65644106b83b05e9ce3718f50db31cb9953118edc573d84f9606e39a6ce"
    actual=hashlib.sha256((ROOT/"knowledge-model-contract.v1.json").read_bytes()).hexdigest()
    if actual != expected: fail("legacy knowledge-model-contract.v1.json changed; v5 compatibility bundle must remain frozen")


def check_docs() -> None:
    rc=subprocess.run([sys.executable,str(ROOT/"tools/check_docs.py")],cwd=ROOT)
    if rc.returncode: fail("documentation link/navigation validation failed")


def main() -> int:
    checks=[
      ("required files",check_required_files),
      ("JSON + schemas",check_json_and_schemas),
      ("v6 fixture",check_v6_example),
      ("release metadata",check_release_metadata),
      ("contract surfaces",check_contract_surfaces),
      ("v6 knowledge-model bundle",check_knowledge_bundle),
      ("frozen v5 bundle",check_v5_bundle_frozen),
      ("documentation",check_docs),
    ]
    for label,fn in checks:
        fn(); print(f"PASS: {label}")
    print("Kristal v6 release integrity: PASS")
    return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}",file=sys.stderr); raise SystemExit(1)
