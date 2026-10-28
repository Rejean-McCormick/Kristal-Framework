"""Tests for the optional UNESCO taxonomy companion (no canonical schema mutations)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/v11"))
from check_unesco_classification import evaluate  # noqa: E402


class UnescoClassificationTests(unittest.TestCase):
    def test_pinned_counts_and_schema(self):
        ref=json.loads((ROOT/"spec/v7/reference-kos/unesco-thesaurus-profile.json").read_text(encoding="utf-8"))
        schema=json.loads((ROOT/"profiles/unesco/kristal-unesco-classification.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(len(ref["domains"]), 7)
        self.assertEqual(sum(len(d["microthesauri"]) for d in ref["domains"]), 88)
        self.assertEqual({d["notation"] for d in ref["domains"]}, set(schema["properties"]["domains"]["items"]["enum"]))
        self.assertNotIn("isced_f2013", schema["properties"])

    def test_reviewed_mapping(self):
        ex=json.loads((ROOT/"profiles/unesco/examples/classification.fragment.example.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluate(ex)["status"],"reviewed")

    def test_candidate_mismatch_and_legacy_not_inferred(self):
        self.assertEqual(evaluate({"classification":{"isced_f2013":{"codes":["06"]}}})["status"],"unmapped")
        example={"classification":{"unesco_thesaurus":{"kos_id":"kos:unesco-thesaurus","domains":["3"],"microthesauri":["3.20"],"mapping_status":"candidate"}}}
        self.assertEqual(evaluate(example)["status"],"review_required")
        example["classification"]["unesco_thesaurus"].update({"domains":["1"],"mapping_status":"reviewed"})
        self.assertEqual(evaluate(example)["status"],"invalid")

    def test_bad_notation(self):
        obj={"classification":{"unesco_thesaurus":{"kos_id":"kos:unesco-thesaurus","domains":["06"],"mapping_status":"reviewed"}}}
        self.assertEqual(evaluate(obj)["status"],"invalid")


if __name__ == "__main__":
    unittest.main()
