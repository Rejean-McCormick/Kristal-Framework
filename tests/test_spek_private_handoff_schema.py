import json
from pathlib import Path
import pytest


def test_spek_profile_rejects_self_approved_handoff():
    jsonschema=pytest.importorskip('jsonschema')
    root=Path(__file__).resolve().parents[1]
    schema=json.loads((root/'profiles/spek/private-editorial-handoff.schema.json').read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    digest='sha256:'+'0'*64
    data={'format':'spek.private-editorial-handoff/1.0','status':'PRIVATE_UNQUALIFIED_NOT_PUBLISHABLE',
        'instance_id':'demo','instance_sha256':digest,'language':'fr',
        'source':{'kind':'not_supplied','sha256':None,'assertion_existence_checked':False},
        'template_locks':[{'template_ref':'rhetorical.definition@1.0.0','sha256':digest}],
        'fields':[{'realization_key':'term','request_file':'term.json','request_sha256':digest,
          'source_assertion_refs':['source:one'],'slot_kind':'concept','required_force':'PRESENT',
          'discourse_function':'','obligations_count':1,'allowed_block_kinds':['utterance']}],
        'selected_assertion_count':1,'relations_declared_unverified':[],
        'qualification':{'semantic_entailment_checked':False,'semantik_result_pairs_verified':False,
         'rhetorical_relations_approved':False,'c1_c2_c3_approved':False,'publication_authorized':False}}
    assert jsonschema.Draft202012Validator(schema).is_valid(data)
    data['qualification']['publication_authorized']=True
    assert not jsonschema.Draft202012Validator(schema).is_valid(data)
