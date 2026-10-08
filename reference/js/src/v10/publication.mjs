import fs from 'node:fs';
import path from 'node:path';
import { canonicalize } from '../jcs.mjs';
import { sha256Hex } from '../hash.mjs';
import { verifyStateSnapshot } from '../v9/state.mjs';
import { verifyNodeManifest, verifyGithubBinding, verifyPublication } from './contracts.mjs';

const sha256=(bytes)=>`sha256:${sha256Hex(bytes)}`;
const jsonBytes=(value)=>Buffer.from(JSON.stringify(value,null,2)+'\n','utf8');
function ensureOk(label,result){if(!result.ok)throw new Error(`${label}: `+result.issues.map(x=>`${x.code??'ERROR'} ${x.path}: ${x.message}`).join('; '));}
function safeRelative(p){return typeof p==='string'&&p.length>0&&!path.isAbsolute(p)&&!p.split(/[\\/]+/).includes('..');}

export function publicationIdentity({node_id,binding_id,state,bundle_manifest_digest}){
  const projection={node_id,binding_id,state,bundle_manifest_digest};
  return `urn:kristal:publication:sha256:${sha256Hex(Buffer.from(canonicalize(projection),'utf8'))}`;
}

export function buildPublicationBundleFromFiles(stateFile,nodeFile,bindingFile,outputDir,{sourceCommit=null}={}){
  const state=JSON.parse(fs.readFileSync(stateFile,'utf8'));
  const node=JSON.parse(fs.readFileSync(nodeFile,'utf8'));
  const binding=JSON.parse(fs.readFileSync(bindingFile,'utf8'));
  const stateCheck=verifyStateSnapshot(state); ensureOk('state',stateCheck);
  ensureOk('node',verifyNodeManifest(node)); ensureOk('binding',verifyGithubBinding(binding));
  if(binding.node_id!==node.node_id)throw new Error('binding node_id does not match node manifest');
  if(!node.bindings.some(b=>b.binding_id===binding.binding_id))throw new Error('binding is not declared by node manifest');

  fs.mkdirSync(outputDir,{recursive:true});
  const stateOut=path.join(outputDir,'state-snapshot.json');
  const stateBytes=fs.readFileSync(stateFile);
  fs.writeFileSync(stateOut,stateBytes);
  const payload={role:'state_snapshot',path:'state-snapshot.json',media_type:'application/json',size:stateBytes.length,blob_digest:sha256(stateBytes)};
  const manifest={
    schema_version:'1.0',artifact_type:'kristal_publication_bundle_manifest',profile:'kristal.publication-bundle/1.0',
    state:{state_ref:state.state_ref,logical_commitment:stateCheck.commitment},payloads:[payload]
  };
  if(sourceCommit)manifest.source={commit:sourceCommit};
  const manifestBytes=jsonBytes(manifest); const manifestDigest=sha256(manifestBytes);
  fs.writeFileSync(path.join(outputDir,'bundle-manifest.json'),manifestBytes);

  const publication={
    schema_version:'10.0',artifact_type:'kristal_publication',
    publication_id:publicationIdentity({node_id:node.node_id,binding_id:binding.binding_id,state:manifest.state,bundle_manifest_digest:manifestDigest}),
    node_id:node.node_id,binding_id:binding.binding_id,state:manifest.state,
    resources:[
      {role:'state_snapshot',locator:'bundle://state-snapshot.json',media_type:'application/json',size:stateBytes.length,blob_digest:payload.blob_digest},
      {role:'other',locator:'bundle://bundle-manifest.json',media_type:'application/vnd.kristal.publication-bundle+json',size:manifestBytes.length,blob_digest:manifestDigest}
    ],
    extensions:{bundle:{profile:manifest.profile,manifest_blob_digest:manifestDigest},...(sourceCommit?{source:{commit:sourceCommit}}:{})}
  };
  ensureOk('publication',verifyPublication(publication));
  const pubBytes=jsonBytes(publication); fs.writeFileSync(path.join(outputDir,'publication.json'),pubBytes);
  return {ok:true,publication_id:publication.publication_id,state:publication.state,bundle_manifest_digest:manifestDigest,files:['state-snapshot.json','bundle-manifest.json','publication.json']};
}

export function verifyPublicationBundle(bundleDir){
  const issues=[];const add=(path_,code,message)=>issues.push({path:path_,code,message});
  let pub,manifest;
  try{pub=JSON.parse(fs.readFileSync(path.join(bundleDir,'publication.json'),'utf8'));}catch(e){return{ok:false,issues:[{path:'publication.json',code:'MISSING_RESOURCE',message:e.message}]};}
  const check=verifyPublication(pub);issues.push(...check.issues.map(x=>({...x,path:`publication.json${x.path==='$'?'':x.path.slice(1)}`})));
  try{manifest=JSON.parse(fs.readFileSync(path.join(bundleDir,'bundle-manifest.json'),'utf8'));}catch(e){add('bundle-manifest.json','MISSING_RESOURCE',e.message);return{ok:false,issues};}
  if(manifest?.artifact_type!=='kristal_publication_bundle_manifest'||manifest?.profile!=='kristal.publication-bundle/1.0')add('bundle-manifest.json','UNSUPPORTED_PROFILE','unsupported bundle manifest');
  if(!Array.isArray(manifest?.payloads))add('bundle-manifest.json.payloads','INVALID_TYPE','payloads must be array');
  else for(const [i,r] of manifest.payloads.entries()){
    if(!safeRelative(r?.path)){add(`bundle-manifest.json.payloads[${i}].path`,'INVALID_PATH','payload path must be relative and contained');continue;}
    const file=path.resolve(bundleDir,r.path);const root=path.resolve(bundleDir)+path.sep;
    if(!file.startsWith(root)){add(`bundle-manifest.json.payloads[${i}].path`,'INVALID_PATH','payload escapes bundle');continue;}
    if(!fs.existsSync(file)){add(r.path,'MISSING_RESOURCE','payload missing');continue;}
    const bytes=fs.readFileSync(file);if(bytes.length!==r.size)add(r.path,'SIZE_MISMATCH',`expected ${r.size}, got ${bytes.length}`);const got=sha256(bytes);if(got!==r.blob_digest)add(r.path,'DIGEST_MISMATCH',`expected ${r.blob_digest}, got ${got}`);
  }
  const manifestBytes=fs.readFileSync(path.join(bundleDir,'bundle-manifest.json'));const md=sha256(manifestBytes);
  if(pub?.extensions?.bundle?.manifest_blob_digest!==md)add('publication.json.extensions.bundle.manifest_blob_digest','DIGEST_MISMATCH','publication does not bind exact bundle manifest bytes');
  const expectedId=publicationIdentity({node_id:pub?.node_id,binding_id:pub?.binding_id,state:pub?.state,bundle_manifest_digest:md});
  if(pub?.publication_id!==expectedId)add('publication.json.publication_id','DIGEST_MISMATCH','publication_id does not match publication identity projection');
  for(const [i,r] of (pub?.resources??[]).entries()){
    if(!r.locator?.startsWith('bundle://'))continue;const rel=r.locator.slice('bundle://'.length);if(!safeRelative(rel)){add(`publication.json.resources[${i}].locator`,'INVALID_PATH','bundle locator invalid');continue;}const f=path.join(bundleDir,rel);if(!fs.existsSync(f)){add(rel,'MISSING_RESOURCE','publication resource missing');continue;}const b=fs.readFileSync(f);if(r.size!==b.length)add(rel,'SIZE_MISMATCH',`expected ${r.size}, got ${b.length}`);const d=sha256(b);if(r.blob_digest!==d)add(rel,'DIGEST_MISMATCH',`expected ${r.blob_digest}, got ${d}`);
  }
  return{ok:issues.length===0,issues,publication_id:pub?.publication_id,state:pub?.state};
}
