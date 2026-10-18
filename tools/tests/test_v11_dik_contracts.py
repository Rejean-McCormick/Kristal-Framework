"""diK v11 draft.3 compatibility, coverage and read-only conversion tests."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/v11'))
from dictionaries import DictionaryError, audit, check_schema, read_json, sha256
from dik_coverage import make_report, validate_counts
from dik_conversion_plan import verify_plan

CAT = ROOT/'examples/v11/dictionaries/catalog.json'
GRAPH = ROOT/'examples/v11/semantic-graph.example.json'
REG = ROOT/'examples/v11/identity-registry.example.json'
CW = ROOT/'examples/v11/external-crosswalk.example.json'
SRC = ROOT/'examples/v11/dik-legacy-sample.json'
PLAN = ROOT/'examples/v11/dik-conversion-plan.example.json'

class DiKContracts(unittest.TestCase):
    def cover(self, **kwargs):
        return make_report(graph_path=GRAPH, catalog_path=CAT, registry_path=REG,
                           crosswalk_path=CW, locales=['fr','en','fr-CA'], **kwargs)

    def test_report_example_is_deterministic_and_schema_valid(self):
        report=self.cover()
        check_schema(report,'kristal-dik-coverage-report.schema.json')
        self.assertEqual(report,read_json(ROOT/'examples/v11/dik-coverage.example.json'))
        self.assertEqual((ROOT/'examples/v11/dik-coverage.example.json').read_bytes(),
                         (ROOT/'tck/v11/vectors/dik-coverage.example.json').read_bytes())
        self.assertEqual(report['semantic_reference_count'], {'KQ':2, 'KP':1})
        self.assertEqual(report['locales'][0]['KQ']['direct'],1)
        self.assertEqual(report['locales'][0]['KP']['missing'],1)
        self.assertEqual(report['locales'][2]['KQ']['fallback'],1)
        self.assertEqual(report['locales'][2]['KQ']['direct'],0)
        self.assertEqual(report['all_locales']['usable']['KQ'],1)
        self.assertEqual(report['all_locales']['direct']['KQ'],0)

    def test_missing_sample_zero_is_reported_as_truncated(self):
        r=self.cover(missing_sample_limit=0)
        self.assertEqual(r['locales'][0]['KQ']['missing_ids_sample'], [])
        self.assertTrue(r['locales'][0]['KQ']['sample_truncated'])

    def test_undeclared_locale_and_duplicates_rejected(self):
        with self.assertRaisesRegex(DictionaryError, 'undeclared'):
            self.cover_again(['pt'])
        with self.assertRaisesRegex(DictionaryError, 'unique'):
            self.cover_again(['fr','fr'])

    def cover_again(self, locales):
        return make_report(graph_path=GRAPH, catalog_path=CAT, registry_path=REG,
                           crosswalk_path=CW, locales=locales)

    def test_incorrect_counts_rejected_even_if_schema_valid(self):
        bad=self.cover()
        bad['locales'][0]['KQ']['direct']=2
        with self.assertRaisesRegex(DictionaryError, 'categories do not add'):
            validate_counts(bad)

    def test_missing_registry_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg=read_json(REG)
            reg['identities']=[x for x in reg['identities'] if x['id']!='KQ1002']
            p=Path(tmp)/'registry.json';p.write_text(json.dumps(reg),encoding='utf-8')
            with self.assertRaisesRegex(DictionaryError,'unregistered'):
                make_report(graph_path=GRAPH,catalog_path=CAT,registry_path=p,crosswalk_path=CW,locales=['fr'])

    def test_301_sparse_locales_are_measured_without_invention(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog=read_json(CAT)
            catalog['languages']=[{'tag':f'qaa-{i:03d}','fallbacks':[],'layers':[]} for i in range(301)]
            p=Path(tmp)/'catalog.json'
            p.write_text(json.dumps(catalog),encoding='utf-8')
            report=make_report(graph_path=GRAPH,catalog_path=p,registry_path=REG,crosswalk_path=CW)
            self.assertEqual(len(report['locales']),301)
            self.assertEqual(report['locales'][0]['KQ']['missing'],2)
            self.assertEqual(report['locales'][300]['KP']['missing'],1)
            self.assertFalse(report['locales'][0]['complete_usable'])

    def test_external_dictionary_alignments_and_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            (base/'external').mkdir()
            record={
                'namespace_id':'example.org/kristal-demo', 'semantic_id':'KQ1002',
                'language':'en','preferred_term':'Grace (domain label)',
                'source_system':'local-reviewed-terminology','source_snapshot':'2026-10-16',
                'source_record_id':'entry-12','license':'internal-curated',
                'alignment':{'decision_id':'a-123','reviewer':'reviewer-demo','evidence_refs':['KS4001']}}
            source=base/'external/en.jsonl'
            source.write_text(json.dumps(record,ensure_ascii=False)+'\n',encoding='utf8')
            original=read_json(CAT)
            original['languages'][0]['layers']=[]
            original['languages'][1]['layers']=[{
                'layer_id':'external-en','kind':'external','priority':200,
                'path':'external/en.jsonl','sha256':sha256(source),
                'source_system':'local-reviewed-terminology',
                'source_snapshot':'2026-10-16','license':'internal-curated'}]
            original['languages'][2]['layers']=[]
            p=base/'catalog.json';p.write_text(json.dumps(original),encoding='utf8')
            audit(p,CW,REG)
            r=make_report(graph_path=GRAPH,catalog_path=p,registry_path=REG,crosswalk_path=CW,locales=['en'])
            self.assertEqual(r['locales'][0]['KQ']['direct'],1)
            self.assertEqual(r['locales'][0]['KQ']['missing'],1)
            record['alignment']['evidence_refs']=['KS999999']
            source.write_text(json.dumps(record,ensure_ascii=False)+'\n',encoding='utf8')
            original['languages'][1]['layers'][0]['sha256']=sha256(source)
            p.write_text(json.dumps(original),encoding='utf8')
            with self.assertRaisesRegex(DictionaryError,'evidence KS absent'):
                audit(p,CW,REG)

    def test_plan_example_is_not_applied_and_source_digest_checked(self):
        plan=read_json(PLAN)
        self.assertEqual((PLAN).read_bytes(), (ROOT/'tck/v11/vectors/dik-conversion-plan.example.json').read_bytes())
        result=verify_plan(plan,registry=read_json(REG),source_path=SRC)
        self.assertEqual(result['decisions']['pending'],3)
        self.assertEqual(result['status'],'structural_check_only_no_execution_permission')
        with self.assertRaisesRegex(DictionaryError,'unapproved'):
            verify_plan(plan,registry=read_json(REG),source_path=SRC,require_all_approved=True)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'changed.json';path.write_text('{}',encoding='utf8')
            with self.assertRaisesRegex(DictionaryError,'source digest mismatch'):
                verify_plan(plan,registry=read_json(REG),source_path=path)

    def test_plan_wrong_target_kind_and_duplicate_paths_rejected(self):
        plan=read_json(PLAN)
        plan['operations'][1]['target_id']='KQ1001'
        with self.assertRaisesRegex(Exception,'kristal-dik-conversion-plan'):
            verify_plan(plan,registry=read_json(REG))
        plan=read_json(PLAN)
        plan['operations'][1]['source_path']=plan['operations'][0]['source_path']
        with self.assertRaisesRegex(DictionaryError,'duplicate'):
            verify_plan(plan,registry=read_json(REG))

    def test_approved_plan_requires_evidence_and_registered_source(self):
        plan=read_json(PLAN)
        plan['operations'][0]['decision']={'status':'approved'}
        with self.assertRaisesRegex(DictionaryError,'kristal-dik-conversion-plan'):
            verify_plan(plan,registry=read_json(REG))
        plan['operations'][0]['decision']={
            'status':'approved','decision_id':'d1','reviewer':'r1',
            'reason':'demo reviewed','evidence_refs':['KS9999']}
        with self.assertRaisesRegex(DictionaryError,'unknown KS evidence'):
            verify_plan(plan,registry=read_json(REG))
        plan['operations'][0]['decision']['evidence_refs']=['KS4001']
        self.assertEqual(verify_plan(plan,registry=read_json(REG))['decisions']['approved'],1)

if __name__=='__main__':
    unittest.main()
