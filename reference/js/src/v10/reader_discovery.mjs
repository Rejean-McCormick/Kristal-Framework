/** Optional Local Kit 3.3.0 reader discovery profile; NOT a v9 commitment or access grant. */
import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';

const ID = /^sha256:[a-f0-9]{64}$/;
const DISCOVERY = 'kristal.discovery/1.0';
const INVENTORY = 'kristal.reader-inventory/1.0';
const PROFILE = 'kristal.reader-profile/1.0';
const CLASSES = new Set(['tiny','small','medium','large','massive']);
const ALLOWED_READERS = new Set([
  'kristal.reader/generic-v1','kristal.reader/causal-graph-v1',
  'kristal.reader/federated-resolution-v1','kristal.reader/proof-navigation-v1',
  'kristal.reader/procedure-v1','kristal.reader/temporal-record-v1',
  'kristal.reader/semantic-reference-v1','kristal.reader/collection-comparison-v1',
  'kristal.reader/social-system-v1','kristal.reader/learning-path-v1',
  'kristal.reader/medical-federation-v1', 'kristal.reader/graph-v1',
]);
function object(x){return x!==null&&typeof x==='object'&&!Array.isArray(x);}
function issue(list,where,message,code='INVALID_METADATA'){list.push({path:where,code,message});}
function relativeSafe(s){return typeof s==='string'&&s.length>0&&s.length<=1024&&!s.includes('\\')&&!s.startsWith('/')&&!s.includes('\0')&&!s.includes(':')&&s.split('/').every(x=>x&&x!=='.'&&x!=='..');}
function number0(n){return Number.isSafeInteger(n)&&n>=0;}
function recordErrors(d,i,p){
 const out=[];
 if(!object(d)||!object(i)||!object(p))return[{path:'$',code:'INVALID_TYPE',message:'all three documents must be objects'}];
 if(d.format!==DISCOVERY)issue(out,'discovery.format','unsupported discovery version','UNSUPPORTED_PROFILE');
 if(i.format!==INVENTORY)issue(out,'inventory.format','unsupported inventory version','UNSUPPORTED_PROFILE');
 if(p.format!==PROFILE)issue(out,'reader.format','unsupported reader version','UNSUPPORTED_PROFILE');
 if(typeof d.state_ref!=='string'||!d.state_ref.trim())issue(out,'discovery.state_ref','missing state reference');
 if(d.state_ref!==i.state_ref||d.state_ref!==p.state_ref)issue(out,'state_ref','state references differ','RELATION_MISMATCH');
 if(!ID.test(d.source_fingerprint??'')||d.source_fingerprint!==i.source_fingerprint||d.source_fingerprint!==p.source_fingerprint)issue(out,'source_fingerprint','fingerprints absent, invalid or inconsistent','RELATION_MISMATCH');
 if(d.authority!=='noncanonical_derived_metadata_not_access_or_publication_authority')issue(out,'discovery.authority','discovery does not grant authority');
 if(!object(d.classification))issue(out,'discovery.classification','missing classification');
 if(!object(d.data_layout)||d.data_layout.inventory_ref!=='derived/reader-inventory.json')issue(out,'discovery.data_layout','wrong inventory reference');
 if(!object(d.reader)||d.reader.hints_ref!=='derived/reader-profile.json'||d.reader.profile!==p.specialization)issue(out,'discovery.reader','reader reference or specialization differs','RELATION_MISMATCH');
 if(!object(d.size)||!CLASSES.has(d.size.class)||d.size.class!==i.size_class||!number0(d.size.tracked_local_bytes))issue(out,'discovery.size','invalid or inconsistent size class','RELATION_MISMATCH');
 if(!object(i.measurement)||!['partial','measured_referenced_local_files'].includes(i.measurement.status)||i.measurement.status!==d.size?.completeness)issue(out,'inventory.measurement','measurement status mismatch','RELATION_MISMATCH');
 if(!object(i.storage)||!number0(i.storage.tracked_local_bytes)||!number0(i.storage.tracked_file_count)||!number0(i.storage.max_tracked_file_bytes))issue(out,'inventory.storage','invalid storage counters');
 if(d.size?.tracked_local_bytes!==i.storage?.tracked_local_bytes)issue(out,'size.tracked_local_bytes','total bytes mismatch','RELATION_MISMATCH');
 if(!Array.isArray(i.files)||!Array.isArray(i.segments)||!Array.isArray(p.artifact_strategies))issue(out,'files','file inventory/segments/strategies must be arrays');
 if(p.configuration_status!=='advisory_only'||!Array.isArray(p.constraints))issue(out,'reader','reader must be advisory only');
 const files=new Map(); let total=0,max=0;
 for(const [n,row] of (Array.isArray(i.files)?i.files:[]).entries()){
  const key=`inventory.files[${n}]`;
  if(!object(row)||!relativeSafe(row.path)){issue(out,key,'unsafe file path','INVALID_PATH');continue;}
  if(files.has(row.path))issue(out,key,'duplicate path','DUPLICATE_PATH');
  if(!number0(row.size_bytes)||!ID.test(row.sha256??'')||typeof row.media_type!=='string'||!row.media_type){issue(out,key,'invalid file metadata');continue;}
  files.set(row.path,row);total+=row.size_bytes;max=Math.max(max,row.size_bytes);
  if(!Number.isSafeInteger(total))issue(out,key,'tracked bytes overflow');
 }
 if(total!==i.storage?.tracked_local_bytes||files.size!==i.storage?.tracked_file_count||max!==i.storage?.max_tracked_file_bytes)issue(out,'inventory.storage','file entries do not match aggregate counters','RELATION_MISMATCH');
 const strategies=new Set();
 for(const [n,row] of (Array.isArray(p.artifact_strategies)?p.artifact_strategies:[]).entries()){
  const key=`reader.artifact_strategies[${n}]`;
  if(!object(row)||!relativeSafe(row.path)){issue(out,key,'unsafe strategy path','INVALID_PATH');continue;}
  const f=files.get(row.path);
  if(!f||strategies.has(row.path))issue(out,key,'missing inventory row or duplicate strategy','RELATION_MISMATCH');
  else if(row.size_bytes_measured!==f.size_bytes||row.must_verify_digest!==f.sha256||row.media_type_observed!==f.media_type)issue(out,key,'strategy conflicts with measured bytes','RELATION_MISMATCH');
  if(row.authorization_required!==true)issue(out,key,'authorization flag missing');
  strategies.add(row.path);
 }
 if(strategies.size!==files.size)issue(out,'reader.artifact_strategies','one strategy per inventory file required','RELATION_MISMATCH');
 for(const [n,s] of (Array.isArray(i.segments)?i.segments:[]).entries()){
  if(!object(s)){issue(out,`inventory.segments[${n}]`,'segment must be object');continue;}
  if(s.path!==null && s.path!==undefined && (!relativeSafe(s.path)||!files.has(s.path)))issue(out,`inventory.segments[${n}].path`,'unknown or unsafe segment path','INVALID_PATH');
 }
 return out;
}
export function verifyReaderDocuments(discovery, inventory, profile){const issues=recordErrors(discovery,inventory,profile);return{ok:issues.length===0,issues,source_fingerprint:discovery?.source_fingerprint??null};}
export function readerPlan(discovery, inventory, profile, {maxJsonBytes=32_000_000}={}){
 const verified=verifyReaderDocuments(discovery,inventory,profile);
 if(!verified.ok)return{ok:false,issues:verified.issues,plan:[]};
 const specialty=ALLOWED_READERS.has(profile.specialization)?profile.specialization:'kristal.reader/generic-v1';
 const specialized=ALLOWED_READERS.has(profile.specialization);
 const byPath=new Map(profile.artifact_strategies.map(r=>[r.path,r]));
 const localSegments=new Map(inventory.segments.filter(s=>s.path).map(s=>[s.path,s]));
 const plan=inventory.files.map(f=>{
  const s=byPath.get(f.path);const segment=localSegments.get(f.path);
  const compression=segment?.compression_declared??s.compression_declared;
  const encrypted=segment?.encrypted_declared===true||s.encrypted_declared===true;
  let mode='opaque_or_format_specific',candidate=null,preconditions=['authorize access','verify bytes and media type'];
  if(encrypted){mode='decrypt_with_authorized_adapter_first';preconditions.push('verify decryption and payload bounds');}
  else if(compression&&!['none','identity'].includes(compression)){mode='decompress_with_bounded_adapter_first';preconditions.push('verify decompressed size and payload type');}
  else if(f.media_type==='application/json'){
   candidate='simdjson';mode=f.size_bytes<=maxJsonBytes?'ondemand_or_dom':'selective_ondemand_capacity_guard';
   preconditions.push('enforce parser capacity and memory limit');
  }else if(['application/x-ndjson','application/jsonl','application/ndjson'].includes(f.media_type)){
   candidate='simdjson';mode='document_stream_requires_record_bound';
   preconditions.push('measure maximum record bytes before choosing batch size');
  }
  return{path:f.path,size_bytes:f.size_bytes,sha256:f.sha256,media_type:f.media_type,mode,parser_candidate:candidate,
   authorization_required:true,execution_ready:false,preconditions};
 });
 return{ok:true,profile:specialty,specialization_recognized:specialized,advisory_only:true,source_fingerprint:discovery.source_fingerprint,
   total_tracked_bytes:inventory.storage.tracked_local_bytes,completeness:inventory.measurement.status,
   origin_fingerprint_independently_verified:false,plan};
}
async function readBounded(file,maxBytes){const st=await fsp.lstat(file);if(!st.isFile()||st.isSymbolicLink()||st.size>maxBytes)throw new Error('unsafe or oversized metadata file');return JSON.parse(await fsp.readFile(file,'utf8'));}
async function safeLocalFile(root,rel){
 if(!relativeSafe(rel))throw new Error('unsafe relative path');
 let cursor=root;for(const segment of rel.split('/')){cursor=path.join(cursor,segment);const stat=await fsp.lstat(cursor);if(stat.isSymbolicLink())throw new Error('symbolic link forbidden');}
 const stat=await fsp.stat(cursor);if(!stat.isFile())throw new Error('not a regular file');return{file:cursor,stat};
}
async function digestFile(file){const hash=createHash('sha256');for await(const chunk of createReadStream(file))hash.update(chunk);return 'sha256:'+hash.digest('hex');}
/** Verify the three small metadata files and optionally check every registered file's bytes.
 *  A consumer MUST separately authorize opening each file; verification is not authorization.
 */
export async function inspectReaderRoot(folder,{verifyFiles=false,maxMetadataBytes=2_000_000,maxFiles=100_000}={}){
 const issues=[];let root;
 try{root=await fsp.realpath(folder);}catch(e){return{ok:false,issues:[{path:'.',code:'READ_ERROR',message:e.message}]};}
 const rels=['kristal.discovery.json','derived/reader-inventory.json','derived/reader-profile.json'];
 const docs=[];
 for(const rel of rels){try{const {file}=await safeLocalFile(root,rel);docs.push(await readBounded(file,maxMetadataBytes));}
  catch(e){issue(issues,rel,e.message,'READ_ERROR');}}
 if(issues.length)return{ok:false,issues};
 const [discovery,inventory,profile]=docs;const checked=verifyReaderDocuments(discovery,inventory,profile);
 issues.push(...checked.issues);
 if(Array.isArray(inventory.files)&&inventory.files.length>maxFiles)issue(issues,'inventory.files','inventory file count exceeds local policy','RESOURCE_LIMIT');
 if(!issues.length&&verifyFiles){
  for(const entry of inventory.files){
   try{
    const {file,stat}=await safeLocalFile(root,entry.path);
    if(stat.size!==entry.size_bytes){issue(issues,entry.path,'file size changed','SIZE_MISMATCH');continue;}
    if(await digestFile(file)!==entry.sha256)issue(issues,entry.path,'file digest changed','DIGEST_MISMATCH');
   }catch(e){issue(issues,entry.path,e.message,'READ_ERROR');}
  }
 }
 const ok=issues.length===0;
 return{ok,issues,discovery:ok?discovery:undefined,inventory:ok?inventory:undefined,
  profile:ok?profile:undefined,reader_plan:ok?readerPlan(discovery,inventory,profile):undefined,
  files_verified:verifyFiles&&ok,origin_fingerprint_independently_verified:false};
}
