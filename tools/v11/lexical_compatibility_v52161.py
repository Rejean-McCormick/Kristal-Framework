"""Private graph reader; original V11 lexicon validity is never inferred from a rehearsal."""
from __future__ import annotations
import hashlib,importlib.util,json
from contextlib import closing
from pathlib import Path

def neighbor():
    p=Path(__file__).with_name('operational_native_v5216.py');s=importlib.util.spec_from_file_location('kristal_operational_v5216_reader',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
op=neighbor();u=op.u;f=op.f
STATUS='LEXICAL_COMPATIBILITY_REVIEWED_CANONICAL_REPAIR_PENDING'
STRICT='QUALIFIED_ACTIVE_GRAPH'
PRIVATE={'PRIVATE_GRAPH_ONLY_LEXICAL_BLOCKED','PRIVATE_LEXICAL_COMPATIBILITY_GRAPH'}

def graph_access(status,purpose):
    f.require(purpose in ('active-only','private-review'),'Unknown purpose')
    f.require(status==STRICT or (status in PRIVATE and purpose=='private-review'),'Graph unavailable in requested purpose; lexical qualification or source checks incomplete')
    return {'qualification_status':status,'original_canonical_lexical_qualified':status==STRICT,'lexical_content_served':False,'canonical_repair_authorized':False,'historical_restoration_authorized':False}

class Reader:
    db=u.Reader.db
    one=u.Reader.one
    def __init__(self,generation,expected_report_sha256,purpose='active-only'):
        self.generation=Path(generation).absolute();self.private=self.generation.parent;self.purpose=purpose;f.require(purpose in ('active-only','private-review'),'Unknown purpose')
        r=json.loads(u.verified(self.generation,'report.json',expected_report_sha256));f.require(r['status']==STATUS,'Wrong report status');self.dbpath=f.safe(self.generation,'active.sqlite');self.db_sha=r['database_sha256'];h=hashlib.sha256()
        with self.dbpath.open('rb') as inp:
            for b in iter(lambda:inp.read(1048576),b''):h.update(b)
        f.require(h.hexdigest()==self.db_sha,'Database digest mismatch');self.prior=op.Reader(f.safe(self.private,r['prior_generation_name']),r['source_report_sha256'],purpose)
    def graph_report(self,namespace):
        row=self.one('SELECT g.* FROM v52161_active_graph g JOIN workspace w USING(slug) WHERE w.active=1 AND w.namespace_id=? AND g.namespace_id=w.namespace_id',(namespace,));r=json.loads(row['report_json']);f.require(r['namespace_id']==namespace and r['slug']==row['slug'] and r['status']==row['status'],'Graph report scope mismatch');return r
    def active_graph(self,namespace):
        r=self.graph_report(namespace);gate=graph_access(r['status'],self.purpose);raw=u.verified(self.generation,r['graph_path'],r['graph_sha256']);doc=f.decode(raw);f.require(doc['namespace_id']==namespace,'Graph namespace mismatch')
        return op.envelope('active',{'namespace_id':namespace},{'graph':doc,'graph_sha256':r['graph_sha256'],'profile_sha256':r['profile_sha256'],'state_sha256':r['state_sha256'],'projection_sha256':r['projection_sha256'],**gate},self.purpose)
    def active_assertion(self,namespace,semantic_id):
        g=self.active_graph(namespace);row=self.one('SELECT * FROM v52161_active_assertion WHERE namespace_id=? AND semantic_id=?',(namespace,semantic_id));a=u.pointer(g['payload']['graph'],row['json_pointer']);f.require(a['id']==semantic_id,'Assertion pointer mismatch');ident=self.one("SELECT i.* FROM identity i JOIN workspace w ON w.slug=i.owner_slug AND w.namespace_id=i.namespace_id WHERE w.active=1 AND i.namespace_id=? AND i.semantic_id=? AND i.kind='assertion'",(namespace,semantic_id))
        return op.envelope('active',{'namespace_id':namespace,'semantic_id':semantic_id},{'assertion':a,'identity':ident,'original_pointer':row['json_pointer'],'graph_sha256':g['payload']['graph_sha256'],**graph_access(g['payload']['qualification_status'],self.purpose)},self.purpose)
    def history(self,namespace,semantic_id):
        f.require(self.purpose=='private-review','Historical audit requires private-review');row=self.one('SELECT * FROM v52161_ka_history WHERE namespace_id=? AND semantic_id=?',(namespace,semantic_id));return {'format':'kristal.experimental.ka-history-review/0.1','scope':{'namespace_id':namespace,'semantic_id':semantic_id},'authority':'HISTORICAL_OBSERVATION_NOT_ACTIVE_ASSERTION','activation_authorized':False,'payload':json.loads(row['record_json'])}
    def read(self,layer,*args):
        if layer=='active':
            r=self.graph_report(args[0]);graph_access(r['status'],self.purpose)
            if r['status']!=STRICT:
                row=self.one('SELECT * FROM identity WHERE namespace_id=? AND semantic_id=?',(args[0],args[1]));return op.envelope('active',{'namespace_id':args[0],'semantic_id':args[1]},{'identity':row,'labels':None,**graph_access(r['status'],self.purpose)},self.purpose)
        return self.prior.read(layer,*args)
