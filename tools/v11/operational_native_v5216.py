"""Explicit private read session with scoped graph content. No publishing or activation."""
import importlib.util,json
from pathlib import Path

def neighbor():
    p=Path(__file__).with_name('unified_native_v5215.py');s=importlib.util.spec_from_file_location('kristal_v5215_reader',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
u=neighbor();f=u.f
FORMAT='kristal.experimental.operational-read/0.1'
STATUS='ACTIVE_GRAPH_READINESS_REVIEWED_ACTIVATION_PENDING'

def envelope(layer,scope,payload,purpose):
    f.require(purpose in ('private-review','active-only'),'Unknown purpose')
    f.require(layer=='active' or purpose=='private-review','Nonactive content forbidden for active-only purpose')
    return {'format':FORMAT,'layer':layer,'scope':scope,'purpose':purpose,'authority':'EXISTING_ACTIVE_RECORD_NOT_NEW_TRUTH' if layer=='active' else 'NO_NEW_AUTHORITY_GRANTED','activation_authorized':False,'publication_authorized':False,'production_integrated':False,'epistemic_policy':'Native status is not new approval; no inference or promotion; active graph is a registered representation, not verification of truth.','payload':payload}

class Reader:
    db=u.Reader.db
    one=u.Reader.one
    def __init__(self,generation,expected_report_sha256,purpose='active-only'):
        self.generation=Path(generation).absolute();self.private=self.generation.parent;self.purpose=purpose
        f.require(purpose in ('active-only','private-review'),'Unknown purpose')
        r=json.loads(u.verified(self.generation,'report.json',expected_report_sha256));f.require(r['status']==STATUS,'Wrong report status');self.dbpath=f.safe(self.generation,'active.sqlite');self.db_sha=r['database_sha256']
        import hashlib
        h=hashlib.sha256()
        with self.dbpath.open('rb') as file:
            for block in iter(lambda:file.read(1048576),b''):h.update(block)
        f.require(h.hexdigest()==self.db_sha,'Database digest mismatch');self.prior=u.Reader(f.safe(self.private,r['prior_generation_name']),r['source_report_sha256'])
    def active_graph(self,namespace):
        row=self.one("SELECT g.* FROM v5216_active_graph g JOIN workspace w USING(slug) WHERE w.active=1 AND w.namespace_id=? AND g.namespace_id=w.namespace_id AND g.status='QUALIFIED_ACTIVE_GRAPH'",(namespace,));raw=u.verified(self.generation,row['graph_path'],row['graph_sha256']);doc=f.decode(raw);f.require(doc['namespace_id']==namespace,'Graph namespace mismatch')
        return envelope('active',{'namespace_id':namespace},{'graph':doc,'graph_sha256':row['graph_sha256'],'profile_sha256':row['profile_sha256'],'state_sha256':row['state_sha256'],'projection_sha256':row['projection_sha256'],'content_availability':'PINNED_PRIVATE_GRAPH_SNAPSHOT'},self.purpose)
    def active_assertion(self,namespace,semantic_id):
        row=self.one('SELECT * FROM v5216_active_assertion WHERE namespace_id=? AND semantic_id=?',(namespace,semantic_id));g=self.active_graph(namespace);a=u.pointer(g['payload']['graph'],row['json_pointer']);f.require(a['id']==semantic_id,'Assertion pointer mismatch')
        return envelope('active',{'namespace_id':namespace,'semantic_id':semantic_id},{'assertion':a,'graph_sha256':g['payload']['graph_sha256'],'original_pointer':row['json_pointer'],'identity':self.prior.active(namespace,semantic_id)['payload']['identity'],'native_epistemic_status':'NOT_DECLARED_BY_V11_GRAPH'},self.purpose)
    def read(self,layer,*args):
        f.require(layer in ('active','candidate','structured','native-artifact','native-record'),'Unknown layer')
        f.require(layer=='active' or self.purpose=='private-review','Explicit private-review required for nonactive content')
        method={'active':self.prior.active,'candidate':self.prior.candidate,'structured':self.prior.structured,'native-artifact':self.prior.artifact,'native-record':self.prior.native_record}[layer]
        result=method(*args)
        return envelope(result['layer'],result['scope'],result,self.purpose)
