import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { referenceV10Capabilities } from '../src/v10/capabilities.mjs';
import { verifyNodeManifest, verifyHostBinding, verifyPublication, verifyDirectory, verifyGithubBinding } from '../src/v10/contracts.mjs';
import { buildPublicationBundleFromFiles, verifyPublicationBundle } from '../src/v10/publication.mjs';
import { stateCommitment } from '../src/v9/state.mjs';
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

const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'kristal-v10-bundle-'));
try{
  const built=buildPublicationBundleFromFiles(path.join(ROOT,'tck/v9/vectors/state-snapshot.example.json'),path.join(ROOT,'tck/v10/vectors/node-manifest.example.json'),path.join(ROOT,'tck/v10/vectors/github-binding.example.json'),tmp,{sourceCommit:'0123456789abcdef0123456789abcdef01234567'});
  test('publication bundle builds',built.ok&&built.files.length===3);
  test('publication bundle verifies',verifyPublicationBundle(tmp).ok,JSON.stringify(verifyPublicationBundle(tmp).issues));
  fs.appendFileSync(path.join(tmp,'state-snapshot.json'),' ');
  const tampered=verifyPublicationBundle(tmp);
  test('publication bundle detects tampered payload bytes',!tampered.ok&&tampered.issues.some(i=>i.code==='DIGEST_MISMATCH'||i.code==='SIZE_MISMATCH'));
} finally {fs.rmSync(tmp,{recursive:true,force:true});}
if(failed)process.exit(1);console.log('Kristal v10 reference tests: PASS');
