"""Unesco mt1.10 integration invariants. Does not approve publication."""
from pathlib import Path
import json
import unittest


class HandoffContractTest(unittest.TestCase):
    def test_single_branch_and_sealed_release(self):
        data=json.loads((Path(__file__).resolve().parents[1]/'integrations'/'unesco-mt1-10'/'handoff.json').read_text(encoding='utf8'))
        self.assertEqual(data['schema'],'koa.unesco-mt1-10-repo-handoff/1.0')
        self.assertEqual(data['branch'],'unesco-mt1-10')
        self.assertEqual(data['baseline_concept_count'],41)
        self.assertEqual(len(data['target_locales']),14)
        self.assertEqual(len(set(data['target_locales'])),14)
        self.assertTrue(data['semantic_grain']['one_branch_kristal'])
        self.assertTrue(data['semantic_grain']['articles_are_projections'])
        self.assertFalse(data['semantic_grain']['one_kristal_per_concept'])
        self.assertFalse(data['semantic_grain']['one_kristal_per_language'])
        self.assertTrue(data['wikidata_candidates_are_unreviewed'])
        self.assertFalse(data['automatic_exact_match'])
        self.assertFalse(data['automatic_canonical_write'])
        self.assertFalse(data['public_upload_authorized'])
        self.assertFalse(data['public_deployment_authorized'])
        self.assertFalse(data['wikipedia_source']['remote_wikipedia_required'])
        self.assertFalse(data['wikipedia_source']['xml_text_extracted'])
        self.assertEqual(data['current_gate'],'CANDIDATE_INTEGRATION_ONLY')

if __name__=='__main__':unittest.main()
