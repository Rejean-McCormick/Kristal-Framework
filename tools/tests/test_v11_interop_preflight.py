"""Framework draft.4 additive diK ↔ Authoring Kit local preflight tests."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/v11'))
from interop_preflight import preflight, _write_new
from dictionaries import DictionaryError, read_json, sha256

EX=ROOT/'examples/v11'

class InteropPreflightTests(unittest.TestCase):
    def values(self, **args):
        v={'catalog':EX/'dictionaries/catalog.json','registry':EX/'identity-registry.example.json',
           'crosswalk':EX/'external-crosswalk.example.json','graph':EX/'semantic-graph.example.json',
           'locales':['fr','en','fr-CA']}
        v.update(args);return v

    def test_coverage_uses_direct_and_fallback_separately(self):
        a=preflight(**self.values())
        b=preflight(**self.values())
        self.assertEqual(a,b)
        self.assertEqual(a['status'],'preflight_pass')
        self.assertEqual(a['graph']['coverage_by_locale'][2]['KQ']['fallback'],1)
        self.assertEqual(a['graph']['coverage_by_locale'][2]['KQ']['direct'],0)
        self.assertFalse(a['canonical_graph_modified'])
        self.assertFalse(a['catalog_activated'])

    def test_kit_import_is_restricted_to_external_wikidata_layers(self):
        with self.assertRaisesRegex(DictionaryError,'cannot contain curated/external'):
            preflight(**self.values(),kit_import_candidate=True)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(EX/'dictionaries',root/'dictionaries')
            cat=root/'dictionaries/catalog.json';data=read_json(cat)
            data['languages'][0]['layers']=[e for e in data['languages'][0]['layers'] if e['kind']=='wikidata']
            cat.write_text(json.dumps(data),encoding='utf-8')
            result=preflight(**self.values(catalog=cat),kit_import_candidate=True)
            self.assertTrue(result['kit_import_candidate'])

    def test_wrong_hash_never_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(EX/'dictionaries',root/'dictionary')
            f=root/'dictionary/imported/wikidata/demo-snapshot/fr.jsonl'
            f.write_text(f.read_text()+' ',encoding='utf-8')
            with self.assertRaisesRegex(DictionaryError,'digest mismatch'):
                preflight(**self.values(catalog=root/'dictionary/catalog.json'))

    def test_unapproved_wikidata_mapping_never_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(EX/'dictionaries',root/'dictionary')
            cat=root/'dictionary/catalog.json'
            f=root/'dictionary/imported/wikidata/demo-snapshot/fr.jsonl'
            text=f.read_text().replace('"external_id":"Q8018"','"external_id":"Q999999"')
            self.assertNotEqual(text,f.read_text())
            f.write_text(text,encoding='utf-8')
            data=read_json(cat)
            data['languages'][0]['layers'][0]['sha256']=sha256(f)
            cat.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaisesRegex(DictionaryError,'unaccepted or stale'):
                preflight(**self.values(catalog=cat))

    def test_no_registry_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'registry.json'
            data=read_json(EX/'identity-registry.example.json')
            data['namespace_id']='other-namespace'
            p.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaisesRegex(DictionaryError,'namespace mismatch'):
                preflight(**self.values(registry=p))

    def test_reports_are_new_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'preflight.json'
            _write_new(p,'FIRST')
            with self.assertRaises(FileExistsError):_write_new(p,'OVERWRITE')
            self.assertEqual(p.read_text(),'FIRST')

    def test_read_only_inputs(self):
        sources=[self.values()[x] for x in ('graph','catalog','registry','crosswalk')]
        fingerprints=[sha256(p) for p in sources]
        preflight(**self.values())
        self.assertEqual(fingerprints,[sha256(p) for p in sources])

if __name__=='__main__':unittest.main()
