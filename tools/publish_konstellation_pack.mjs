#!/usr/bin/env node
// Explicit application profile; core Kristal v5 contracts remain unchanged.
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
export const canonical=x=>Array.isArray(x)?'['+x.map(canonical).join(',')+']':x&&typeof x==='object'?'{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')+'}':JSON.stringify(x);
export const sha=x=>createHash('sha256').update(x).digest('hex');
const need=(ok,message)=>{if(!ok)throw Error(message);};
function admit(kind,value){
 const validator=fileURLToPath(new URL('./validate_konstellation_document.py',import.meta.url));
 const r=spawnSync(process.env.PYTHON || 'python',[validator,kind],{input:JSON.stringify(value),encoding:'utf8',maxBuffer:1024*1024});
 need(r.status===0,'Schema admission failed (Python + jsonschema required): '+(r.stderr||r.error?.message||''));
}
export function publish({catalog,assertions,policy,exchangeId,artifactStatus,createdAt,output}){
 need(/^sha256:[a-f0-9]{64}$/.test(exchangeId),'Explicit source Exchange hash required');
 need(['draft','working','under_review','recognized','reference','deprecated','superseded','revoked'].includes(artifactStatus),'Explicit artifact status required');
 need(typeof createdAt==='string'&&!Number.isNaN(Date.parse(createdAt)),'Explicit creation timestamp required');
 need(catalog&&typeof catalog.synthetic==='boolean'&&typeof catalog.title==='string'&&typeof catalog.description==='string','Catalogue provenance and description required');
 need(Array.isArray(assertions)&&assertions.length<=100000,'Assertion array required, at most 100000 rows');
 need(policy?.schema_version==='5.0'&&policy.artifact_type==='reader_policy'&&/^reader_policy:[a-z0-9][a-z0-9.*:-]*$/.test(policy.reader_policy_id)&&policy.policy,'ReaderPolicy v5 document required');
 admit('policy',policy);
 const entities=new Map(catalog.entities?.map(e=>[e.id,e])),sources=new Set(catalog.sources?.map(s=>s.id)),relations=new Map(catalog.registry?.relations?.map(r=>[r.id,r]));
 need(entities.size===catalog.entities?.length&&sources.size===catalog.sources?.length&&relations.size===catalog.registry?.relations?.length,'Invalid catalogue or duplicate identities');
 const required=['id','subject','relation','value','status','certainty','validationStatus','validatedAs','authority','recognitionStatus','scope','sourceRefs'];
 const ids=new Set();
 for(const a of assertions){
  need(required.every(k=>a[k]!==undefined&&a[k]!==null),'Missing epistemic column in assertion '+a.id);
  need(typeof a.id==='string'&&!ids.has(a.id),'Duplicate assertion identity');ids.add(a.id);
  need(['hypothesis','claimed','sourced','disputed','reviewed','validated','rejected','retracted','superseded'].includes(a.status),'Unknown assertion status');
  for(const k of ['certainty','validationStatus','validatedAs','authority','recognitionStatus'])need(typeof a[k]==='string'&&a[k].length,'Invalid '+k);
  need(typeof a.scope.domain==='string'&&Array.isArray(a.sourceRefs)&&a.sourceRefs.every(id=>sources.has(id)),'Unknown source or missing scope');
  const r=relations.get(a.relation),subject=entities.get(a.subject);
  need(r&&subject&&r.domain.includes(subject.type),'Assertion domain mismatch');
  if(r.valueKind==='entity')need(entities.get(a.value)?.type===r.range,'Assertion range mismatch');
  if(r.valueKind==='interval')need(a.ruleRef&&Array.isArray(a.derivedFrom),'Interval requires derivation evidence');
 }
 const root=path.resolve(output);need(!fs.existsSync(root),'Refusing to overwrite an existing pack');
 const parent=path.dirname(root);fs.mkdirSync(parent,{recursive:true});const stage=fs.mkdtempSync(path.join(parent,'.konstellation-pack-'));
 try{
  const write=(name,data,role)=>{const bytes=Buffer.from(canonical(data)+'\n');fs.writeFileSync(path.join(stage,name),bytes);return {path:name,role,sha256:sha(bytes),size_bytes:bytes.length};};
  const {assertions:ignored,policies:ignoredPolicies,integration:ignoredIntegration,...safeCatalog}=catalog;
  const rows=[...assertions].sort((a,b)=>{for(const key of ['subject','relation','value','id']){const x=canonical(a[key]),y=canonical(b[key]);if(x!==y)return x<y?-1:1;}return 0;});
  const files=[write('catalog.json',safeCatalog,'metadata'),write('assertions.json',rows,'metadata'),write('reader-policy.json',policy,'reader_policy')];
  const digest=x=>'sha256:'+sha(canonical(x));
  const manifest={schema_version:'5.0',artifact_type:'runtime_pack_manifest',runtime_pack_id:digest({files,exchangeId,artifactStatus}),runtime_pack_version:'5.0.0',created_at:createdAt,profiles:['konstellation:reader-json-v1'],source_exchange_ref:{exchange_id:exchangeId,artifact_type:'working_exchange'},source_artifact_status:artifactStatus,compiler:{name:'kristal-konstellation-publisher',version:'1.0.0'},build:{build_id:digest(files),deterministic:true,canonicalization_profile:'kristal.v5:jcs-rfc8785',canonicalization_version:'1',config_hash:digest({profile:'konstellation:reader-json-v1'}),compile_status:'succeeded'},policies:{data_ordering:{policy:'subject_predicate_object_statement_id_asc',notes:'Canonical JSON values, ECMAScript string order.'},row_grouping:{policy:'fixed_rows_100k',notes:'Single complete JSON table, at most 100000 rows.'},membership_filter:{kind:'none'},bitmap:{format:'roaring',run_optimize:false,notes:'No bitmap files emitted; reader builds in-memory indexes.'}},reader_policy_refs:[{id:'sha256:'+files[2].sha256,artifact_type:'reader_policy',hash:'sha256:'+files[2].sha256}],query_contract_ref:{contract_id:'kristal.v5:query-contract:offline-core',contract_version:'1'},files,integrity:{hash_alg:'sha256'}};
  admit('manifest',manifest);
  const m=write('manifest.json',manifest,'metadata');
  const keys=[...new Set([...required,...rows.flatMap(Object.keys)])];
  write('konstellation.json',{adapter:'kristal-runtime-pack-v1',directory:'.',manifest:'manifest.json',manifestSha256:m.sha256,catalog:'catalog.json',rows:[{file:'assertions.json',format:'json',columns:Object.fromEntries(keys.map(k=>[k,k])),qualifiersPreserved:true}],relationMappings:Object.fromEntries([...new Set(rows.map(a=>a.relation))].map(id=>[id,id]))},'metadata');
  // No generated signature, validation status or historical truth claim.
  fs.renameSync(stage,root);return {directory:root,config:path.join(root,'konstellation.json'),assertions:rows.length};
 }catch(e){fs.rmSync(stage,{recursive:true,force:true});throw e;}
}
if(process.argv[1]&&fileURLToPath(import.meta.url)===path.resolve(process.argv[1])){
 try{const args={};for(let i=2;i<process.argv.length;i+=2){need(process.argv[i].startsWith('--')&&process.argv[i+1],'Expected --name value');args[process.argv[i].slice(2)]=process.argv[i+1];}
 const read=name=>JSON.parse(fs.readFileSync(args[name],'utf8'));
 console.log(JSON.stringify(publish({catalog:read('catalog'),assertions:read('assertions'),policy:read('policy'),exchangeId:args['exchange-id'],artifactStatus:args['artifact-status'],createdAt:args['created-at'],output:args.output})));}
 catch(e){console.error(e.message);process.exitCode=1;}
}
