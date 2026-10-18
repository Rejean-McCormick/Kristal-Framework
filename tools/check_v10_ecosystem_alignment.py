#!/usr/bin/env python3
"""Read-only Framework-local v10 contract consistency report.

No remote I/O, hosting mutation, release, or cross-repository qualification.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    "github_read_surface_profile": ("profiles/github/schemas/kristal-github-read-surface.schema.json", "kristal.github-read-surface/1.0"),
    "github_sync_manifest_profile": ("profiles/github/schemas/kristal-github-sync-manifest.schema.json", "kristal.github-sync-manifest/1.0"),
    "reader_discovery_profile": ("profiles/reader-discovery/schemas/kristal-discovery.schema.json", "kristal.discovery/1.0"),
    "github_collection_index_profile": ("profiles/github/schemas/kristal-github-collection-index.schema.json", "kristal.github-collection-index/1.0"),
}


def inspect(root: Path = ROOT) -> dict:
    issues: list[str] = []
    def read(path: str) -> dict:
        try:
            value = json.loads((root / path).read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("expected JSON object")
            return value
        except (OSError, ValueError) as exc:
            issues.append(f"{path}: {exc}")
            return {}

    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
    except OSError as exc:
        issues.append(f"VERSION: {exc}")
        version = ""
    release = read("contracts/release.json")
    contract_set = read("contracts/contract-set.json")
    if release.get("version") != version or contract_set.get("version") != version:
        issues.append("VERSION, release.json and contract-set.json must agree")
    if release.get("status") != "draft" or not (version.startswith("10.0.0-draft.") or version.startswith("11.0.0-draft.")):
        issues.append("v10 baseline checker requires an active v10 or additive v11 draft")
    v10 = release.get("v10") if isinstance(release.get("v10"), dict) else {}
    if v10.get("semantic_state_baseline") != "kristal.state/9.0":
        issues.append("v9 semantic state must remain the v10 baseline")
    if v10.get("hosted_network_baseline") != "kristal.hosting/10.0":
        issues.append("Expected hosted network baseline kristal.hosting/10.0")
    if v10.get("reference_host_profile") != "kristal.host/github/1.0":
        issues.append("Expected GitHub reference host profile kristal.host/github/1.0")
    if (v10.get("compatibility_lock", release.get("compatibility_lock")) != "contracts/v10-compatibility-lock.json"):
        issues.append("v10 compatibility lock reference mismatch")
    normalized = contract_set.get("normative") if isinstance(contract_set.get("normative"), dict) else {}
    schemas = normalized.get("schemas") if isinstance(normalized.get("schemas"), list) else []
    for key, (path, fmt) in PROFILES.items():
        if v10.get(key) != fmt:
            issues.append(f"contracts/release.json v10.{key} must equal {fmt}")
        if path not in schemas:
            issues.append(f"Missing {path} in normative schema list")
        schema = read(path)
        actual = (schema.get("properties") or {}).get("format", {})
        if not isinstance(actual, dict) or actual.get("const") != fmt:
            issues.append(f"{path} format.const must equal {fmt}")
    for file in ["contracts/v10-compatibility-lock.json", "contracts/v9-compatibility-lock.json"]:
        if not (root / file).is_file():
            issues.append(f"Missing historical compatibility lock: {file}")
    return {
        "status": "PASS" if not issues else "FAIL",
        "scope": "framework-local-contract-consistency-only",
        "version": version,
        "release_status": release.get("status"),
        "semantic_state_baseline": v10.get("semantic_state_baseline"),
        "host_profile": v10.get("reference_host_profile"),
        "profiles": {key: fmt for key, (_, fmt) in PROFILES.items()},
        "external_consumers": "NOT_EVALUATED",
        "hosting_publication_activation": "NOT_AUTHORIZED",
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print structured local evidence")
    args = parser.parse_args()
    result = inspect()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Kristal v10 local contract alignment: {result['status']}")
        for issue in result["issues"]:
            print(f"- {issue}")
        print("External consumers: NOT_EVALUATED; no deployment or authorization")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
