import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { referenceV10Capabilities } from '../src/v10/capabilities.mjs';
import { verifyNodeManifest, verifyHostBinding, verifyPublication, verifyDirectory, verifyGithubBinding } from '../src/v10/contracts.mjs';
import { buildPublicationBundleFromFiles, verifyPublicationBundle } from '../src/v10/publication.mjs';
import { verifyGithubReadSurface, verifyGithubSyncManifest, verifyGithubCollectionIndex, verifyHostedGithubReadSurface, verifyHostedGithubCollection, githubReadSurfaceDigest, githubCollectionIndexDigest } from '../src/v10/github_read_surface.mjs';
import { stateCommitment } from '../src/v9/state.mjs';
import { sha256Hex } from '../src/hash.mjs';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const load=(p)=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
let failed=0; function test(name,ok,detail=''){if(!ok){failed++;console.error('FAIL',name,detail);}else console.log('PASS',name);}
const node=load('tck/v10/vectors/node-manifest.example.json');
const binding=load('tck/v10/vectors/github-binding.example.json');
const publication=load('tck/v10/vectors/publication.example.json');
const directory=load('tck/v10/vectors/directory.example.json');
const v9state=load('tck/v9/vectors/state-snapshot.example.json');
test('node manifest verifies',verifyNodeManifest(node).ok);
test('generic host binding verifies',verifyHostBinding(binding).ok);
test('github profile binding verifies',verifyGithubBinding(binding).ok);
test('publication verifies',verifyPublication(publication).ok,JSON.stringify(verifyPublication(publication).issues));
test('directory verifies',verifyDirectory(directory).ok);

const readSurface=load('profiles/github/examples/github-read-surface.example.json');
const syncManifest=load('profiles/github/examples/github-sync-manifest.example.json');
const collectionIndex=load('profiles/github/examples/github-collection-index.example.json');
test('GitHub read-surface verifies',verifyGithubReadSurface(readSurface).ok,JSON.stringify(verifyGithubReadSurface(readSurface).issues));
test('GitHub sync manifest verifies',verifyGithubSyncManifest(syncManifest).ok,JSON.stringify(verifyGithubSyncManifest(syncManifest).issues));
test('GitHub collection index verifies',verifyGithubCollectionIndex(collectionIndex).ok,JSON.stringify(verifyGithubCollectionIndex(collectionIndex).issues));
const badSurface=JSON.parse(JSON.stringify(readSurface));badSurface.surface_digest='sha256:'+'0'.repeat(64);
test('read-surface digest tampering is rejected',!verifyGithubReadSurface(badSurface).ok&&verifyGithubReadSurface(badSurface).issues.some(i=>i.code==='DIGEST_MISMATCH'));

const badNode=JSON.parse(JSON.stringify(node));badNode.roles=['not-a-role'];badNode.bindings=[null];
const badNodeResult=verifyNodeManifest(badNode);
test('invalid role and null binding are rejected',!badNodeResult.ok&&badNodeResult.issues.some(i=>i.code==='UNSUPPORTED_ROLE')&&badNodeResult.issues.some(i=>i.code==='INVALID_BINDING'));
const badPub=JSON.parse(JSON.stringify(publication));badPub.resources=[{}];
test('empty publication resource is rejected',!verifyPublication(badPub).ok);
const badDirectory=JSON.parse(JSON.stringify(directory));badDirectory.entries={};
let directoryStructured=false;try{const r=verifyDirectory(badDirectory);directoryStructured=!r.ok&&r.issues.some(i=>i.code==='INVALID_TYPE');}catch{};
test('malformed directory returns structured validation result',directoryStructured);

test('v10 preserves v9 state commitment',stateCommitment(v9state).digest===v9state.logical_commitment.digest);
const moved=JSON.parse(JSON.stringify(binding));moved.resource.locator='github://other-owner/renamed-repo';moved.profile_configuration.repository='renamed-repo';
test('host move does not touch semantic state commitment',stateCommitment(v9state).digest===v9state.logical_commitment.digest);
const caps=referenceV10Capabilities();
test('v10 capabilities inherit v9 state',caps.compatibility.semantic_state_baseline==='kristal.state/9.0'&&caps.capabilities.semantic_state.v9_unchanged===true);
test('v10 capabilities advertise GitHub read surfaces',caps.capabilities.hosting.github_read_surfaces===true&&caps.capabilities.hosting.github_collection_indexes===true&&caps.capabilities.hosting.hosted_surface_verification===true);

const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'kristal-v10-bundle-'));
try{
  const built=buildPublicationBundleFromFiles(path.join(ROOT,'tck/v9/vectors/state-snapshot.example.json'),path.join(ROOT,'tck/v10/vectors/node-manifest.example.json'),path.join(ROOT,'tck/v10/vectors/github-binding.example.json'),tmp,{sourceCommit:'0123456789abcdef0123456789abcdef01234567'});
  test('publication bundle builds',built.ok&&built.files.length===3);
  test('publication bundle verifies',verifyPublicationBundle(tmp).ok,JSON.stringify(verifyPublicationBundle(tmp).issues));
  fs.appendFileSync(path.join(tmp,'state-snapshot.json'),' ');
  const tampered=verifyPublicationBundle(tmp);
  test('publication bundle detects tampered payload bytes',!tampered.ok&&tampered.issues.some(i=>i.code==='DIGEST_MISMATCH'||i.code==='SIZE_MISMATCH'));
} finally {fs.rmSync(tmp,{recursive:true,force:true});}

const hostedTmp=fs.mkdtempSync(path.join(os.tmpdir(),'kristal-v10-hosted-'));
try{
  const hostedRoot=path.join(hostedTmp,'kristals','demo');fs.mkdirSync(path.join(hostedRoot,'ai'),{recursive:true});fs.mkdirSync(path.join(hostedRoot,'state'),{recursive:true});fs.mkdirSync(path.join(hostedRoot,'.kristal'),{recursive:true});
  const stateBytes=fs.readFileSync(path.join(ROOT,'tck/v9/vectors/state-snapshot.example.json'));fs.writeFileSync(path.join(hostedRoot,'state','state-snapshot.json'),stateBytes);
  const stateDoc=JSON.parse(stateBytes.toString('utf8'));
  fs.writeFileSync(path.join(hostedRoot,'AI_START_HERE.md'),'# Demo\nRead AI_MANIFEST.json then ai/INDEX.json.\n','utf8');
  fs.writeFileSync(path.join(hostedRoot,'AI_MANIFEST.json'),JSON.stringify({format:'kristal.portable-ai/1.0',state_ref:stateDoc.state_ref,state_logical_commitment:stateDoc.logical_commitment,entrypoint:'AI_START_HERE.md'},null,2)+'\n','utf8');
  const fileInfo=(rel,role)=>{const b=fs.readFileSync(path.join(hostedRoot,...rel.split('/')));return{path:rel,role,size:b.length,sha256:`sha256:${sha256Hex(b)}`};};
  let files=[fileInfo('AI_MANIFEST.json','ai_manifest'),fileInfo('AI_START_HERE.md','ai_entrypoint'),fileInfo('state/state-snapshot.json','state_snapshot')];
  const aiIndex={format:'kristal.ai-index/1.0',state_ref:stateDoc.state_ref,state_logical_commitment:stateDoc.logical_commitment,files:[{...files.find(x=>x.path==='state/state-snapshot.json'),media_type:'application/json'}],materialization_blobs:[]};
  fs.writeFileSync(path.join(hostedRoot,'ai','INDEX.json'),JSON.stringify(aiIndex,null,2)+'\n','utf8');files.push(fileInfo('ai/INDEX.json','ai_index'));files.sort((a,b)=>Buffer.compare(Buffer.from(a.path,'utf8'),Buffer.from(b.path,'utf8')));
  const surface={format:'kristal.github-read-surface/1.0',kit_version:'test',slug:'demo',target_root:'kristals/demo',entrypoint:'AI_START_HERE.md',state_ref:stateDoc.state_ref,state_logical_commitment:stateDoc.logical_commitment,ready:true,errors:[],surface_digest:'',file_count:files.length,total_bytes:files.reduce((n,x)=>n+x.size,0),files:files.map(x=>({...x,media_type:'application/octet-stream'})),materialization_object_count:0,materialization_objects:[]};surface.surface_digest=githubReadSurfaceDigest(surface);
  const manifest={format:'kristal.github-sync-manifest/1.0',manager_version:'test',read_surface_format:surface.format,local_kit_version:'test',slug:'demo',title:'Demo',target_root:'kristals/demo',entrypoint:'AI_START_HERE.md',state_ref:stateDoc.state_ref,state_logical_commitment:stateDoc.logical_commitment,surface_digest:surface.surface_digest,file_count:files.length,total_bytes:surface.total_bytes,materialization_object_count:0,files,policy:{derived_read_surface:true,sync_is_not_publication:true,activation_is_separate:true,materialization_blobs_are_not_implicitly_copied:true}};
  fs.writeFileSync(path.join(hostedRoot,'.kristal','sync-manifest.json'),JSON.stringify(manifest,null,2)+'\n','utf8');
  const row={slug:'demo',title:'Demo',path:'kristals/demo',entrypoint:'kristals/demo/AI_START_HERE.md',state_ref:stateDoc.state_ref,state_logical_commitment:stateDoc.logical_commitment,surface_digest:surface.surface_digest,file_count:files.length,total_bytes:surface.total_bytes,materialization_object_count:0};
  const idx={format:'kristal.github-collection-index/1.0',kristals:[row],count:1,index_digest:githubCollectionIndexDigest([row]),note:'Derived navigation index for GitHub/AI discovery; not semantic authority.'};fs.writeFileSync(path.join(hostedTmp,'kristals','index.json'),JSON.stringify(idx,null,2)+'\n','utf8');
  test('hosted GitHub Kristal verifies',verifyHostedGithubReadSurface(hostedTmp,'kristals/demo').ok,JSON.stringify(verifyHostedGithubReadSurface(hostedTmp,'kristals/demo').issues));
  test('hosted GitHub collection verifies',verifyHostedGithubCollection(hostedTmp).ok,JSON.stringify(verifyHostedGithubCollection(hostedTmp).issues));
  fs.appendFileSync(path.join(hostedRoot,'AI_START_HERE.md'),'tamper');const tamperedHosted=verifyHostedGithubReadSurface(hostedTmp,'kristals/demo');test('hosted verifier detects byte tampering',!tamperedHosted.ok&&tamperedHosted.issues.some(i=>i.code==='DIGEST_MISMATCH'||i.code==='SIZE_MISMATCH'));
} finally {fs.rmSync(hostedTmp,{recursive:true,force:true});}

if(failed)process.exit(1);console.log('Kristal v10 reference tests: PASS');
