"""Opt-in read-only federation of distinct authority/representation layers."""
from __future__ import annotations
import importlib.util, json, re, sqlite3
from pathlib import Path
from contextlib import closing
from jsonschema import Draft202012Validator

def load_neighbor():
    p=Path(__file__).with_name('structured_native_v5214.py')
    s=importlib.util.spec_from_file_location('kristal_structured_v5214_reader',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
f=load_neighbor()
FORMAT='kristal.experimental.unified-read/0.1'
STATUS='UNIFIED_PRIVATE_READER_QUALIFIED_ACTIVATION_PENDING'
SCHEMA=Path(__file__).resolve().parents[2]/'schemas/experimental/unified-read-0.1.schema.json'

def verified(root,rel,expected):
    f.require(isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected),'Missing valid digest')
    raw=f.safe(root,rel).read_bytes();f.require(f.sha(raw)==expected,'Digest mismatch: '+rel);return raw

def pointer(doc,ptr):
    f.require(isinstance(ptr,str) and (ptr=='' or ptr.startswith('/')),'Invalid JSON pointer')
    if not ptr:return doc
    for token in ptr.split('/')[1:]:
        f.require(not re.search(r'~(?![01])',token),'Invalid pointer escape')
        token=token.replace('~1','/').replace('~0','~')
        if isinstance(doc,list):
            f.require(re.fullmatch(r'0|[1-9][0-9]*',token) is not None and int(token)<len(doc),'Invalid array index');doc=doc[int(token)]
        elif isinstance(doc,dict):
            f.require(token in doc,'Pointer not found');doc=doc[token]
        else:raise ValueError('Pointer traverses scalar')
    return doc

def envelope(layer,scope,payload):
    status={'active':'ACTIVE_INDEX_METADATA_ONLY','candidate':'PRIVATE_V11_CANDIDATE_NOT_ACTIVE','structured':'PRIVATE_STRUCTURED_NOT_V11','native_artifact':'REGISTERED_NATIVE_NOT_V11','native_record':'REGISTERED_NATIVE_NOT_V11'}[layer]
    result={'format':FORMAT,'layer':layer,'status':status,'scope':scope,'authority':'NO_NEW_AUTHORITY_GRANTED','activation_authorized':False,'production_integrated':False,'payload':payload}
    Draft202012Validator(json.loads(SCHEMA.read_bytes())).validate(result);return result

class Reader:
    """Read-only snapshot session. Caller supplies trusted report SHA, not a discovered hash."""
    def __init__(self,generation,expected_report_sha256):
        self.generation=Path(generation).absolute();self.private=self.generation.parent
        r=json.loads(verified(self.generation,'report.json',expected_report_sha256));f.require(r['status']==STATUS,'Wrong generation status')
        self.dbpath=f.safe(self.generation,'active.sqlite');self.db_sha=r['database_sha256']
        # Streaming hash; the database is never opened writable.
        import hashlib
        h=hashlib.sha256()
        with self.dbpath.open('rb') as inp:
            for block in iter(lambda:inp.read(1048576),b''):h.update(block)
        f.require(h.hexdigest()==self.db_sha,'Database digest mismatch')
    def db(self):
        c=sqlite3.connect(self.dbpath.as_uri()+'?mode=ro&immutable=1',uri=True);c.row_factory=sqlite3.Row;return c
    def one(self,sql,args):
        with closing(self.db()) as c:rows=c.execute(sql,args).fetchall()
        f.require(len(rows)==1,'Unknown or ambiguous scoped record');return dict(rows[0])
    def active(self,namespace,semantic_id):
        row=self.one('SELECT i.* FROM identity i JOIN workspace w ON w.slug=i.owner_slug AND w.namespace_id=i.namespace_id WHERE w.active=1 AND i.namespace_id=? AND i.semantic_id=?',(namespace,semantic_id))
        with closing(self.db()) as c:labels=[dict(x) for x in c.execute('SELECT * FROM lexical WHERE namespace_id=? AND semantic_id=? ORDER BY language_tag',(namespace,semantic_id))]
        return envelope('active',{'namespace_id':namespace,'semantic_id':semantic_id},{'identity':row,'labels':labels,'content_availability':'INDEX_METADATA_ONLY','source_database_sha256':self.db_sha})
    def candidate(self,namespace,semantic_id):
        row=self.one('SELECT * FROM v5215_candidate_identity WHERE namespace_id=? AND semantic_id=?',(namespace,semantic_id));profile=self.one("SELECT * FROM v5215_profile WHERE slug=? AND layer='candidate'",(row['slug'],));root=f.safe(self.private,profile['generation']+'/candidates/'+row['slug']);inv=json.loads(profile['inventory_json']);bridge=f.decode(verified(root,'bridge.json',inv['bridge.json']));entries=[x for x in bridge['entries'] if x['semantic_id']==semantic_id];f.require(len(entries)==1 and bridge['namespace_id']==namespace,'Bridge scope mismatch');entry=entries[0]
        f.require(all(entry[k]==row[k] for k in ('kind','native_ref','json_pointer','source_sha256')),'Bridge/index disagreement')
        with closing(self.db()) as c:labels=[dict(x) for x in c.execute('SELECT language_tag,preferred_term FROM v5215_candidate_lexical WHERE namespace_id=? AND semantic_id=? ORDER BY language_tag',(namespace,semantic_id))]
        payload={'identity':row,'labels':labels,'bridge_entry':entry,'native_record':None,'projection':None,'source_path':bridge['source_paths'].get(entry['source']),'source_sha256':entry['source_sha256'],'original_pointer':entry['json_pointer'],'epistemic_status':None}
        if row['kind']=='assertion':
            a=f.decode(verified(root,'native-originals/state.json',entry['source_sha256']));original=pointer(a,entry['json_pointer']);f.require(original['assertion_id']==entry['native_ref'],'Assertion ID mismatch')
            graph=f.decode(verified(root,'canon/domain/v11/graph.json',inv['canon/domain/v11/graph.json']));pr=[x for x in graph['assertions'] if x['id']==semantic_id];f.require(len(pr)==1,'Projection missing');payload.update(native_record=original,projection=pr[0],epistemic_status=original.get('assertion_status'))
        return envelope('candidate',{'namespace_id':namespace,'semantic_id':semantic_id},payload)
    def packet(self,slug):
        profile=self.one("SELECT * FROM v5215_profile WHERE slug=? AND layer IN ('structured','discovery')",(slug,));root=f.safe(self.private,profile['generation']+'/structured/'+slug);packet=f.decode(verified(root,'packet.json',profile['packet_sha256']));f.require(packet['slug']==slug,'Packet scope mismatch');return root,packet,profile
    def structured(self,slug,occurrence_id):
        row=self.one('SELECT * FROM v5214_occurrence WHERE slug=? AND occurrence_id=?',(slug,occurrence_id));root,packet,profile=self.packet(slug);f.require(profile['layer']=='structured','Not a structured assertion packet')
        rec=f.read_occurrence(root,packet,occurrence_id);f.require(rec['record']['pointer']==row['json_pointer'] and rec['record']['native_assertion_id']==row['native_assertion_id'] and rec['record']['native_status']==row['native_status'],'Occurrence mismatch')
        return envelope('structured',{'slug':slug,'occurrence_id':occurrence_id},rec)
    def artifact(self,slug,path,ptr=None):
        row=self.one('SELECT * FROM v5215_native_artifact WHERE slug=? AND path=?',(slug,path));root,packet,profile=self.packet(slug);f.require(profile['layer']=='discovery','Not a discovery profile');f.require(packet['files'].get(path)==row['sha256'],'Artifact digest not in packet');f.require(any(x['path']==path and x['contract_id']==row['contract_id'] and x['contract_version']==row['contract_version'] and x['artifact_id']==row['artifact_id'] for x in packet['registered_artifacts']),'Artifact registration mismatch');raw=verified(root/'originals',path,row['sha256']);out={'registration':row,'script_executed':False,'document':None,'selected_pointer':ptr,'selected_value':None}
        if row['media_kind']=='json':
            doc=f.decode(raw);out['document']=doc
            if ptr is not None:out['selected_value']=pointer(doc,ptr)
        else:f.require(ptr is None,'Non-JSON artifact is metadata only')
        return envelope('native_artifact',{'slug':slug,'path':path},out)
    def native_record(self,slug,path,collection,native_id):
        row=self.one('SELECT * FROM v5215_native_record WHERE slug=? AND path=? AND collection=? AND native_id=?',(slug,path,collection,native_id));doc=self.artifact(slug,path,row['json_pointer']);value=doc['payload']['selected_value'];f.require(isinstance(value,dict) and value.get(row['id_field'])==native_id,'Native record identity mismatch')
        return envelope('native_record',{'slug':slug,'path':path,'collection':collection,'native_id':native_id},{'record_index':row,'native_record':value,'document_context':doc['payload']['document'],'registration':doc['payload']['registration']})
