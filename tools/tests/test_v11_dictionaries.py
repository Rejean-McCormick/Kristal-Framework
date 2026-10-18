"""Reference dictionary-manager tests: import, layers, drift and failures."""
from __future__ import annotations
import bz2
from copy import deepcopy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/v11'))
from dictionaries import (DictionaryError, accepted_exact, audit, check_schema,
                          import_local, read_json, resolve, sha256)

class DictionaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.crosswalk=read_json(ROOT/'examples/v11/external-crosswalk.example.json')
        self.registry=read_json(ROOT/'examples/v11/identity-registry.example.json')
        self.ns=self.registry['namespace_id']
        self.cwpath=self.root/'crosswalk.json'
        self.regpath=self.root/'registry.json'
        self.cwpath.write_text(json.dumps(self.crosswalk),encoding='utf-8')
        self.regpath.write_text(json.dumps(self.registry),encoding='utf-8')
        self.dump=self.root/'dump.json.bz2'
        entities=[
          {'id':'Q8018','lastrevid':12345,
           'labels':{'fr':{'language':'fr','value':"Augustin d'Hippone"},'en':{'language':'en','value':'Augustine of Hippo'}},
           'aliases':{'fr':[{'language':'fr','value':'saint Augustin'}]},
           'descriptions':{'fr':{'language':'fr','value':'philosophe et théologien'}}},
          {'id':'Q999999','labels':{'fr':{'language':'fr','value':'Unmatched'}}},
        ]
        with bz2.open(self.dump,'wt',encoding='utf-8') as f:
            f.write('[\n')
            f.write(json.dumps(entities[0],ensure_ascii=False)+',\n')
            f.write(json.dumps(entities[1],ensure_ascii=False)+'\n]\n')
        self.out=self.root/'dictionary'

    def do_import(self,languages='fr,en'):
        return import_local(SimpleNamespace(dump=str(self.dump),crosswalk=str(self.cwpath),
                        namespace=self.ns,snapshot='2026-10-16',languages=languages,output=str(self.out)))

    def test_import_streaming_crosswalk_and_locales(self):
        result=self.do_import()
        self.assertEqual(result['entities_scanned'],2)
        self.assertEqual(result['accepted_exact_entities_seen'],1)
        self.assertEqual(result['labels_by_locale'],{'fr':1,'en':1})
        self.assertEqual(audit(self.out/'catalog.json',self.cwpath,self.regpath)['locales'],2)
        self.assertEqual(resolve(self.out/'catalog.json','KQ1001','fr')['term'],"Augustin d'Hippone")
        self.assertEqual(resolve(self.out/'catalog.json','KQ1001','en')['term'],'Augustine of Hippo')
        self.assertEqual(resolve(self.out/'catalog.json','KQ1002','fr')['status'],'missing')
        entry=json.loads((self.out/'imported/wikidata/2026-10-16/fr.jsonl').read_text().strip())
        self.assertEqual(entry['aliases'],['saint Augustin'])
        self.assertEqual(entry['source_revision'],12345)
        self.assertEqual(entry['external_id'],'Q8018')

    def test_curated_priority_no_mutation_of_source(self):
        self.do_import()
        catalogpath=self.out/'catalog.json'
        c=read_json(catalogpath)
        curated={
            'schema_version':'11.0','artifact_type':'kristal_curated_dictionary',
            'namespace_id':self.ns,'language':'fr',
            'entries':[{'semantic_id':'KQ1001','preferred_term':'Saint Augustin',
                        'review':{'decision_id':'review-1','reviewer':'curator',
                                  'reason':'Preferred display term in this domain'}}]}
        target=self.out/'curated/fr.json';target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(curated,ensure_ascii=False)+'\n',encoding='utf-8')
        original=(self.out/'imported/wikidata/2026-10-16/fr.jsonl').read_bytes()
        c['languages'][0]['layers'].append({
           'layer_id':'fr-local','kind':'curated','priority':200,
           'path':'curated/fr.json','sha256':sha256(target)})
        catalogpath.write_text(json.dumps(c),encoding='utf-8')
        audit(catalogpath,self.cwpath,self.regpath)
        resolved=resolve(catalogpath,'KQ1001','fr')
        self.assertEqual(resolved['term'],'Saint Augustin')
        self.assertEqual((self.out/'imported/wikidata/2026-10-16/fr.jsonl').read_bytes(),original)

    def test_fallback_is_explicit(self):
        self.do_import()
        p=self.out/'catalog.json';catalog=read_json(p)
        self.assertEqual(resolve(p,'KQ1001','fr-CA')['status'],'missing')
        catalog['languages'].append({'tag':'fr-CA','fallbacks':['fr'],'layers':[]})
        p.write_text(json.dumps(catalog),encoding='utf-8')
        audit(p)
        rendered=resolve(p,'KQ1001','fr-CA')
        self.assertTrue(rendered['fallback'])
        self.assertEqual(rendered['effective_locale'],'fr')

    def test_corrupted_source_detected(self):
        self.do_import()
        with (self.out/'imported/wikidata/2026-10-16/fr.jsonl').open('a',encoding='utf-8') as f:
            f.write('corrupted\n')
        with self.assertRaisesRegex(DictionaryError,'digest mismatch'):
            audit(self.out/'catalog.json')

    def test_import_does_not_overwrite_snapshot(self):
        self.do_import()
        with self.assertRaisesRegex(DictionaryError,'already exists'):
            self.do_import()

    def test_accepted_exact_duplicates_rejected(self):
        cw=deepcopy(self.crosswalk)
        duplicate=deepcopy(cw['mappings'][0]);duplicate['mapping_id']='second'
        cw['mappings'].append(duplicate)
        with self.assertRaises(DictionaryError):
            accepted_exact(cw,self.ns)

    def test_301_declared_locales_possible(self):
        # The protocol has no arbitrary 300-language ceiling and can represent sparse locales.
        tags=[f'qaa-{i:03d}' for i in range(301)]
        catalog={'schema_version':'11.0','artifact_type':'kristal_dictionary_catalog',
                 'catalog_id':'large','namespace_id':self.ns,
                 'languages':[{'tag':t,'fallbacks':[],'layers':[]} for t in tags]}
        check_schema(catalog,'kristal-dictionary-catalog.schema.json')
        p=self.root/'empty-catalog.json';p.write_text(json.dumps(catalog),encoding='utf-8')
        self.assertEqual(audit(p)['locales'],301)

    def test_cyclic_fallback_rejected(self):
        self.do_import()
        p=self.out/'catalog.json';c=read_json(p)
        c['languages'][0]['fallbacks']=['en']
        c['languages'][1]['fallbacks']=['fr']
        p.write_text(json.dumps(c),encoding='utf-8')
        with self.assertRaisesRegex(DictionaryError,'cyclic locale fallback'):
            audit(p)

    def test_same_priority_conflict_rejected(self):
        self.do_import()
        p=self.out/'catalog.json';c=read_json(p)
        curated={'schema_version':'11.0','artifact_type':'kristal_curated_dictionary',
                 'namespace_id':self.ns,'language':'fr',
                 'entries':[{'semantic_id':'KQ1001','preferred_term':'Different label',
                             'review':{'decision_id':'d1','reviewer':'c','reason':'test'}}]}
        target=self.out/'curated.json';target.write_text(json.dumps(curated),encoding='utf-8')
        c['languages'][0]['layers'].append({'layer_id':'same-tier','kind':'curated',
            'priority':100,'path':'curated.json','sha256':sha256(target)})
        p.write_text(json.dumps(c),encoding='utf-8')
        with self.assertRaisesRegex(DictionaryError,'conflicting same-priority'):
            audit(p)

    def test_unsafe_source_layer_path_rejected(self):
        self.do_import()
        p=self.out/'catalog.json';c=read_json(p)
        c['languages'][0]['layers'][0]['path']='../../outside.jsonl'
        p.write_text(json.dumps(c),encoding='utf-8')
        with self.assertRaises(DictionaryError):audit(p)

    def test_alias_not_a_new_identity(self):
        self.do_import()
        data=(self.out/'imported/wikidata/2026-10-16/fr.jsonl').read_text()
        self.assertNotIn('KQ999999',data)
        self.assertIn('saint Augustin',data)

if __name__=='__main__':unittest.main()
