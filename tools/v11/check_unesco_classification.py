#!/usr/bin/env python3
"""Inspect a local workspace UNESCO classification. Read-only, non-normative companion profile."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "profiles/unesco/kristal-unesco-classification.schema.json"
REFERENCE = ROOT / "spec/v7/reference-kos/unesco-thesaurus-profile.json"


def evaluate(workspace: dict) -> dict:
    """Return domain/microthesaurus validation; never infer from ISCED, names or icons."""
    classification = workspace.get("classification", {})
    if not isinstance(classification, dict):
        return {"status": "invalid", "issues": ["classification must be an object"]}
    mapping = classification.get("unesco_thesaurus")
    if mapping is None:
        return {"status": "unmapped", "issues": ["no explicit UNESCO classification"]}
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(mapping), key=lambda e: str(e.path))
    if errors:
        return {"status": "invalid", "issues": [f"{list(e.path)}: {e.message}" for e in errors]}
    profile = json.loads(REFERENCE.read_text(encoding="utf-8"))
    domains = {d["notation"] for d in profile["domains"]}
    micros = {mt["notation"]: d["notation"] for d in profile["domains"] for mt in d["microthesauri"]}
    if len(domains) != 7 or len(micros) != 88:
        return {"status": "invalid", "issues": ["pinned UNESCO profile has wrong 7/88 counts"]}
    declared = set(mapping.get("domains", []))
    implied = {micros[x] for x in mapping.get("microthesauri", [])}
    if declared and not implied.issubset(declared):
        return {"status": "invalid", "issues": ["declared microthesaurus belongs to another UNESCO domain"]}
    # Concept URIs are kept intact; inspecting their live availability is out of scope.
    if mapping.get("mapping_status") != "reviewed":
        return {"status": "review_required", "issues": ["UNESCO mapping requires an explicit reviewed status"]}
    return {"status": "reviewed", "issues": [], "domains": sorted(declared or implied), "microthesauri": mapping.get("microthesauri", [])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path, help="Path to kristal.workspace.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.workspace.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        result = {"status": "invalid", "issues": [str(exc)]}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"UNESCO classification: {result['status']}" + (" | " + "; ".join(result.get("issues", [])) if result.get("issues") else ""))
    return {"reviewed": 0, "unmapped": 2, "review_required": 2, "invalid": 1}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
