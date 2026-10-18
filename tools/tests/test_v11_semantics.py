"""Negative TCK for v11 canonical graph, crosswalk and word resolver."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/v11'))
from validate_v11 import (IntegrityError, fixture_documents, validate_documents,
                          validate_schema, check_fixtures)
from resolve_legacy import resolve_requests

class V11SemanticTests(unittest.TestCase):
    def setUp(self):self.fixtures=fixture_documents()
    def validate(self,**kw):
        fixture=deepcopy(self.fixtures);fixture.update(kw)
        validate_documents(**fixture)

    def test_positive_and_mirrored_examples(self):
        check_fixtures()
    def test_wikidata_q_cannot_be_canonical_entity(self):
        graph=deepcopy(self.fixtures['graph']);graph['entities']=['Q8018','KQ1002']
        with self.assertRaises(IntegrityError):self.validate(graph=graph)
    def test_text_predicate_cannot_be_canonical_property(self):
        graph=deepcopy(self.fixtures['graph']);graph['assertions'][0]['predicate']='influence'
        with self.assertRaises(IntegrityError):self.validate(graph=graph)
    def test_graph_rejects_label_field(self):
        graph=deepcopy(self.fixtures['graph']);graph['label']='Augustin'
        with self.assertRaises(IntegrityError):self.validate(graph=graph)
    def test_undeclared_assertion_endpoint(self):
        graph=deepcopy(self.fixtures['graph']);graph['assertions'][0]['object']['id']='KQ9999'
        with self.assertRaises(IntegrityError):self.validate(graph=graph)
    def test_graph_allows_typed_text_value_not_as_identity(self):
        graph=deepcopy(self.fixtures['graph'])
        graph['assertions'][0]['object']={'kind':'literal','datatype':'string','value':'Texte en français','language':'fr'}
        self.validate(graph=graph)
    def test_registry_mismatched_kind(self):
        r=deepcopy(self.fixtures['registry']);r['identities'][0]['kind']='property'
        with self.assertRaises(IntegrityError):self.validate(registry=r)
    def test_crosswalk_kq_to_wikidata_p_rejected(self):
        crosswalk=deepcopy(self.fixtures['crosswalk']);crosswalk['mappings'][0]['external_ref']['id']='P1234'
        with self.assertRaises(IntegrityError):self.validate(crosswalk=crosswalk)
    def test_crosswalk_kp_to_wikidata_q_rejected(self):
        crosswalk=deepcopy(self.fixtures['crosswalk']);crosswalk['mappings'][0]['local_ref']['id']='KP2001'
        with self.assertRaises(IntegrityError):self.validate(crosswalk=crosswalk)
    def test_accepted_without_review_rejected(self):
        crosswalk=deepcopy(self.fixtures['crosswalk']);crosswalk['mappings'][0].pop('review')
        with self.assertRaises(IntegrityError):self.validate(crosswalk=crosswalk)
    def test_crosswalk_conflicting_active_exact_rejected(self):
        crosswalk=deepcopy(self.fixtures['crosswalk']);m=deepcopy(crosswalk['mappings'][0])
        m['mapping_id']='dup';m['local_ref']['id']='KQ1002';crosswalk['mappings'].append(m)
        with self.assertRaises(IntegrityError):self.validate(crosswalk=crosswalk)
    def test_crosswalk_candidate_does_not_resolve_wikidata(self):
        crosswalk=deepcopy(self.fixtures['crosswalk']);crosswalk['mappings'][0]['status']='candidate'
        report=resolve_requests(self.fixtures['requests'],self.fixtures['lexicons'],crosswalk)
        self.assertEqual(report['results'][1]['status'],'unresolved')
    def test_text_ambiguity_is_reported(self):
        lexicons=deepcopy(self.fixtures['lexicons'])
        lexicons[0]['entries'][1]['alternate_terms']=["Augustin d'Hippone"]
        report=resolve_requests(self.fixtures['requests'],lexicons,self.fixtures['crosswalk'])
        self.assertEqual(report['results'][0]['status'],'ambiguous')
        self.assertEqual({r['id'] for r in report['results'][0]['candidates']},{'KQ1001','KQ1002'})
        self.assertFalse(report['canonical_graph_modified'])
        self.assertFalse(report['authoritative_identity_decisions'])
    def test_casefolded_lexical_resolution_preserves_identity(self):
        requests=deepcopy(self.fixtures['requests'])
        requests['requests'][0]['lookup']['term']="AUGUSTIN D'HIPPONE"
        report=resolve_requests(requests,self.fixtures['lexicons'],self.fixtures['crosswalk'])
        self.assertEqual(report['results'][0]['candidates'][0]['id'],'KQ1001')
    def test_unknown_word_unresolved_not_minted(self):
        requests=deepcopy(self.fixtures['requests']);requests['requests'][0]['lookup']['term']='Concept inconnu'
        report=resolve_requests(requests,self.fixtures['lexicons'],self.fixtures['crosswalk'])
        self.assertEqual(report['results'][0]['status'],'unresolved')
    def test_cross_namespace_not_silently_equal(self):
        crosswalk=deepcopy(self.fixtures['crosswalk']);crosswalk['mappings'][0]['local_ref']['namespace_id']='other'
        with self.assertRaises(IntegrityError):self.validate(crosswalk=crosswalk)

if __name__=='__main__':unittest.main()
