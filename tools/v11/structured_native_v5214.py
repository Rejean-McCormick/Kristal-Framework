"""Experimental lossless companion contract; never a V11 graph or authority grant."""
from __future__ import annotations
import hashlib, json, re, stat
from decimal import Decimal
from pathlib import Path, PurePosixPath
from jsonschema import Draft202012Validator
FORMAT='kristal.experimental.native-structured/0.1'
STATUS='PRIVATE_REPRESENTATION_ONLY'
SCHEMA=Path(__file__).resolve().parents[2]/'schemas/experimental/native-structured-0.1.schema.json'

def require(ok,msg):
    if not ok: raise ValueError(msg)
def safe(root,rel):
    p=PurePosixPath(rel);require(isinstance(rel,str) and rel and not p.is_absolute() and '..' not in p.parts and '\\' not in rel and ':' not in rel and p.as_posix()==rel,'Unsafe path')
    dst=Path(root).absolute().joinpath(*p.parts)
    for x in [*reversed(dst.parents),dst]:
        try: st=x.lstat()
        except FileNotFoundError: continue
        require(not stat.S_ISLNK(st.st_mode) and not getattr(st,'st_file_attributes',0)&0x400,'Link/reparse refused')
    return dst
def sha(b):return hashlib.sha256(b).hexdigest()
def pairs(items):
    d={}
    for k,v in items:
        require(k not in d,'Duplicate JSON key: '+k);d[k]=v
    return d
def reject_constant(x):raise ValueError('Non-finite JSON number: '+x)
def decode(b):return json.loads(b,object_pairs_hook=pairs,parse_float=Decimal,parse_constant=reject_constant)
def encode(v):
    # Decimal preserves base-10 value without binary float conversion. Original bytes remain authoritative.
    if isinstance(v,Decimal):require(v.is_finite(),'Nonfinite decimal');return str(v)
    if isinstance(v,dict):return '{'+','.join(json.dumps(k,ensure_ascii=True)+':'+encode(x) for k,x in v.items())+'}'
    if isinstance(v,list):return '['+','.join(encode(x) for x in v)+']'
    require(type(v) in (str,int,bool,type(None)),'Unsupported JSON runtime value');return json.dumps(v,ensure_ascii=True,allow_nan=False)
def shape(v):
    return {dict:'object',list:'array',str:'string',bool:'boolean',int:'integer',Decimal:'decimal',type(None):'null'}[type(v)]
def ref(x):
    require(isinstance(x,dict),'Reference envelope expected')
    if set(x)=={'external_id','label'}:
        require(isinstance(x['external_id'],str) and x['external_id'].strip() and isinstance(x['label'],str),'Invalid embedded reference');return x['external_id']
    require(set(x)=={'kind','id'} and all(isinstance(x[k],str) and x[k].strip() for k in x),'Invalid native reference');return x['id']
def pred(x):
    if isinstance(x,str):require(x.strip(),'Empty predicate');return x
    return ref(x)
def describe(o,ptr,*,aging_exception=False):
    require(isinstance(o,dict) and isinstance(o.get('kind'),str),'Missing native kind')
    k=o['kind'];val=o.get('value');s=shape(val) if 'value' in o else 'absent';form=None;anomaly=None
    if k in ('referent','concept','pattern','item'):
        if set(o)=={'kind','value'} and k=='item':ref(val);form='embedded_reference'
        else:
            require(set(o) in ({'kind','id'},{'kind','id','value'}) and isinstance(o['id'],str) and o['id'].strip(),'Unsupported reference')
            require('value' not in o or isinstance(val,str),'Invalid enriched reference');form='enriched_reference' if 'value' in o else 'reference'
    elif k=='monolingual_text':
        require(set(o)=={'kind','value'} and isinstance(val,dict) and set(val)=={'text','lang'} and all(isinstance(val[t],str) for t in val) and val['lang'].strip(),'Invalid monolingual text');form='monolingual_text'
    elif k=='json':require(set(o)=={'kind','value'} and s in ('object','array'),'Invalid JSON structured value');form='json_'+s
    elif k=='set':require(set(o)<={'kind','value','language'} and s=='array','Invalid set');form='native_set_sequence'
    elif k in ('string','boolean'):
        require(set(o)<={'kind','value','language'} and 'value' in o,'Invalid scalar envelope')
        if k=='string' and s=='array' and aging_exception:
            require(all(isinstance(x,str) for x in val),'Invalid anomalous list');form='declared_string_array';anomaly='DECLARED_STRING_ACTUAL_ARRAY'
        else:require(s==k,'Native scalar kind mismatch');form='scalar_'+k
    else:raise ValueError('Unsupported native kind: '+k)
    if 'language' in o:require(isinstance(o['language'],str) and o['language'].strip(),'Invalid language')
    return {'pointer':ptr,'native_kind':k,'shape':s,'form':form,'anomaly':anomaly}
def records(slug,source_path,source_bytes):
    state=decode(source_bytes);require(isinstance(state,dict) and (state.get('schema_version'),state.get('artifact_type')) in (('5.0','structured_epistemic_state'),('6.0','kristal_state')),'Unexpected source contract')
    aa=state['assertions'];require(isinstance(aa,list),'Missing assertions');h=sha(source_bytes);out=[]
    for i,a in enumerate(aa):
        p=f'/assertions/{i}';st=a['statement'];require(set(st) in ({'subject','predicate','object'},{'subject','predicate','object','qualifiers'}),'Unsupported statement fields')
        aid=a['assertion_id'];status=a['assertion_status'];require(isinstance(aid,str) and aid and isinstance(status,str) and status,'Invalid assertion identity/status')
        su=ref(st['subject']);pr=pred(st['predicate']);ex=slug=='aging' and h=='59167e2a836b8e3a00dc74b487c29ebb7517819187479748e32458b9f92a6554' and i==16 and aid=='urn:aging:assertion:mechanisms_hallmarks/twelve'
        ob=describe(st['object'],p+'/statement/object',aging_exception=ex);qs=[]
        for j,q in enumerate(st.get('qualifiers',[])):
            require(set(q)=={'predicate','object'},'Unsupported qualifier');qs.append({'predicate_ref':pred(q['predicate']),'object':describe(q['object'],p+f'/statement/qualifiers/{j}/object')})
        out.append({'occurrence_id':'sha256:'+sha(encode([slug,source_path,h,p]).encode('ascii')),'native_assertion_id':aid,'pointer':p,'native_status':status,'subject_ref':su,'predicate_ref':pr,'object':ob,'qualifiers':qs})
    return state,out
def validate_packet(root,packet,*,schema=SCHEMA):
    Draft202012Validator(json.loads(Path(schema).read_bytes())).validate(packet)
    originals=root/'originals'
    for rel,h in packet['files'].items():require(sha(safe(originals,rel).read_bytes())==h,'Original digest mismatch: '+rel)
    ws=decode(safe(originals,'kristal.workspace.json').read_bytes());require(ws['slug']==packet['slug'],'Workspace owner mismatch')
    index=decode(safe(originals,'canon/state.index.json').read_bytes());registered=index['canonical_artifacts'];require(isinstance(registered,list),'Missing registered artifacts')
    expected=[{'path':x['path'],'artifact_id':x['artifact_id'],'contract_id':x['logical_contract']['id'],'contract_version':x['logical_contract']['version']} for x in registered]
    require(packet['registered_artifacts']==expected and all(x['path'] in packet['files'] for x in expected),'Registered artifact coverage mismatch')
    if packet['source_path'] is None:require(packet['records']==[],'Discovery must not invent occurrences');return None,[]
    require(packet['source_path'] in packet['files'],'Unbound source path');raw=safe(originals,packet['source_path']).read_bytes();state,rr=records(packet['slug'],packet['source_path'],raw)
    require(rr==packet['records'],'Occurrence index differs from original');require(len({r['occurrence_id'] for r in rr})==len(rr),'Occurrence collision');return state,rr

def read_occurrence(root,packet,occurrence_id):
    state,rr=validate_packet(root,packet);r=next((x for x in rr if x['occurrence_id']==occurrence_id),None);require(r is not None,'Unknown occurrence')
    a=state['assertions'][int(r['pointer'].split('/')[-1])]
    return {'format':FORMAT,'status':STATUS,'slug':packet['slug'],'source_path':packet['source_path'],'source_sha256':packet['files'][packet['source_path']],'record':r,'native_assertion':a,'authority':'NONE_GRANTED_BY_REPRESENTATION'}
