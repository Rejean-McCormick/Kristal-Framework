#!/usr/bin/env python3
"""Build deterministic Kristal v5 contract and schema manifests."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "Technical-Reference" / "kristal-docs-v5"
CONTRACT_MANIFEST = ROOT / "contract-set.manifest.json"
SCHEMA_MANIFEST = ROOT / "schema-set.manifest.json"
RELEASE_MANIFEST = ROOT / "kristal-release.json"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def set_digest(entries: list[dict[str, str]]) -> str:
    # Deliberately simple, language-neutral digest input. Paths are repository-relative
    # UTF-8 text and hashes are lowercase SHA-256 hex.
    payload = "".join(f"{e['path']}\0{e['sha256']}\n" for e in sorted(entries, key=lambda x: x['path']))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def role_for(rel: str) -> str:
    p = rel.replace("\\", "/")
    if "/01-core-spec/" in p:
        return "core-normative"
    if "/02-schemas/" in p:
        return "schema-normative"
    if "/03-reproducibility/" in p:
        return "reproducibility-normative"
    if p.endswith("/04-query/query-contract.md"):
        return "query-normative"
    if "/04-query/" in p or "/05-profiles/" in p:
        return "profile-normative"
    if "/06-integration/" in p:
        return "integration-normative"
    if "/07-security/" in p:
        return "security-normative"
    if "/09-test-vectors/" in p:
        return "test-vector-normative"
    return "informative"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict, dict]:
    contract_entries = []
    for path in sorted(DOCS.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        contract_entries.append({"path": rel, "sha256": sha256_file(path), "role": role_for(rel)})

    schema_entries = [e for e in contract_entries if e["role"] == "schema-normative"]
    contract_digest = set_digest(contract_entries)
    schema_digest = set_digest(schema_entries)

    contract = {
        "format": "kristal.contract-set-manifest/v1",
        "release": VERSION,
        "digest_algorithm": "sha256",
        "set_digest_algorithm": "sha256(path + NUL + sha256 + LF, sorted by path)",
        "contract_set_digest": f"sha256:{contract_digest}",
        "entries": contract_entries,
    }
    schema = {
        "format": "kristal.schema-set-manifest/v1",
        "release": VERSION,
        "schema_line": "5.0",
        "digest_algorithm": "sha256",
        "set_digest_algorithm": "sha256(path + NUL + sha256 + LF, sorted by path)",
        "schema_set_digest": f"sha256:{schema_digest}",
        "entries": schema_entries,
    }
    release = {
        "format": "kristal.release/v1",
        "framework": "kristal",
        "version": VERSION,
        "status": "release-candidate" if "-rc." in VERSION else "stable",
        "core_version": "5.0",
        "canonicalization": {
            "profile": "kristal.v5:jcs-rfc8785",
            "version": "1",
            "hash_algorithm": "sha256",
        },
        "contract_set_digest": contract["contract_set_digest"],
        "schema_set_digest": schema["schema_set_digest"],
        "git": {
            "tag": f"v{VERSION}",
            "commit": None,
            "commit_resolution": "Resolve the signed Git tag to its full immutable commit SHA; consumers record that SHA in their own lock file.",
        },
    }
    return contract, schema, release


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Fail if generated manifests differ from committed files")
    args = ap.parse_args()
    contract, schema, release = build()
    expected = [(CONTRACT_MANIFEST, contract), (SCHEMA_MANIFEST, schema), (RELEASE_MANIFEST, release)]
    if args.check:
        failed = False
        for path, value in expected:
            text = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                print(f"OUT OF DATE: {path.relative_to(ROOT)}")
                failed = True
        return 1 if failed else 0
    for path, value in expected:
        write_json(path, value)
        print(f"wrote {path.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
