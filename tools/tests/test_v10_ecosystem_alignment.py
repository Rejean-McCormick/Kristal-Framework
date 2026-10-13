"""Offline checks for draft v10 reference profile consistency."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from check_v10_ecosystem_alignment import PROFILES, inspect


class AlignmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        paths = ["VERSION", "contracts/release.json", "contracts/contract-set.json",
                 "contracts/v9-compatibility-lock.json", "contracts/v10-compatibility-lock.json"]
        paths += [path for path, _ in PROFILES.values()]
        for item in paths:
            target = self.root / item
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item, target)

    def tearDown(self):
        self.temp.cleanup()

    def change(self, name, mutate):
        target = self.root / name
        payload = json.loads(target.read_text(encoding="utf-8"))
        mutate(payload)
        target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_matching_reference_is_local_only(self):
        status = inspect(self.root)
        self.assertEqual(status["status"], "PASS", status["issues"])
        self.assertEqual(status["external_consumers"], "NOT_EVALUATED")
        self.assertEqual(status["hosting_publication_activation"], "NOT_AUTHORIZED")

    def test_release_version_drift_fails(self):
        self.change("contracts/release.json", lambda d: d.update(version="10.0.0-draft.99"))
        self.assertEqual(inspect(self.root)["status"], "FAIL")

    def test_v9_semantic_baseline_drift_fails(self):
        self.change("contracts/release.json", lambda d: d["v10"].update(semantic_state_baseline="kristal.state/10.0"))
        self.assertEqual(inspect(self.root)["status"], "FAIL")

    def test_missing_normative_profile_fails(self):
        self.change("contracts/contract-set.json", lambda d: d["normative"]["schemas"].remove(PROFILES["github_collection_index_profile"][0]))
        self.assertEqual(inspect(self.root)["status"], "FAIL")

    def test_schema_format_mismatch_fails(self):
        self.change(PROFILES["github_sync_manifest_profile"][0], lambda d: d["properties"]["format"].update(const="invalid"))
        self.assertEqual(inspect(self.root)["status"], "FAIL")

    def test_missing_lock_fails(self):
        (self.root / "contracts/v9-compatibility-lock.json").unlink()
        self.assertEqual(inspect(self.root)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
