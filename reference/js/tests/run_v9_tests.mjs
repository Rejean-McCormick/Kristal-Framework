import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { logicalArtifactCommitment, stateCommitment, verifyLogicalArtifact, verifyStateSnapshot } from '../src/v9/state.mjs';
import { verifyMaterializationManifest } from '../src/v9/materialization.mjs';
import { referenceV9Capabilities } from '../src/v9/capabilities.mjs';
import { inspectArtifact } from '../src/v8/reader.mjs';
import { verifyKnowledgeModelContract } from '../src/knowledge_model_contract.mjs';
import { verifyDerivation, verifyExchangeV9, verifyActivation } from '../src/v9/contracts.mjs';
import { publishStateSnapshot, activateChannel } from '../src/v9/lifecycle.mjs';
import os from 'node:os';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const load=(rel)=>JSON.parse(fs.readFileSync(path.join(ROOT,rel),'utf8'));
let failed=false;function test(name,ok,detail=''){if(!ok){failed=true;console.error('FAIL:',name,detail);}else console.log('PASS:',name);}
const artifact=load('examples/v9/logical-artifact.example.json');
const state=load('examples/v9/state-snapshot.example.json');
const mat=load('examples/v9/materialization-manifest.example.json');
const deriv=load('examples/v9/derivation.example.json');
const exchange=load('examples/v9/exchange.example.json');
const activation=load('examples/v9/activation.example.json');
test('logical artifact verifies',verifyLogicalArtifact(artifact).ok,JSON.stringify(verifyLogicalArtifact(artifact).issues));
test('generic reader recognizes v9',inspectArtifact(artifact).family==='v9'&&inspectArtifact(artifact).ok);
test('state snapshot verifies',verifyStateSnapshot(state).ok,JSON.stringify(verifyStateSnapshot(state).issues));
test('materialization verifies',verifyMaterializationManifest(mat).ok,JSON.stringify(verifyMaterializationManifest(mat).issues));
test('derivation verifies',verifyDerivation(deriv).ok,JSON.stringify(verifyDerivation(deriv).issues));
test('exchange verifies',verifyExchangeV9(exchange).ok,JSON.stringify(verifyExchangeV9(exchange).issues));
test('activation verifies',verifyActivation(activation).ok,JSON.stringify(verifyActivation(activation).issues));
const renamed=JSON.parse(JSON.stringify(artifact)); renamed.artifact_id='urn:kristal:example:recipe:alternate-id';
test('artifact commitment is independent of semantic identifier',logicalArtifactCommitment(artifact).digest===logicalArtifactCommitment(renamed).digest);
const extended=JSON.parse(JSON.stringify(artifact)); extended.extensions={domain_semantics:{difficulty:'advanced'}};
test('artifact commitment includes logical extensions',logicalArtifactCommitment(artifact).digest!==logicalArtifactCommitment(extended).digest);
const changed=JSON.parse(JSON.stringify(artifact)); changed.payload.steps[1].action='serve_pasta';
test('artifact commitment changes with logical payload',logicalArtifactCommitment(artifact).digest!==logicalArtifactCommitment(changed).digest);
const reordered=JSON.parse(JSON.stringify(state)); reordered.members=[...reordered.members].reverse();
test('state commitment normalizes member ordering',stateCommitment(state).digest===stateCommitment(reordered).digest);
const changedPhysical=JSON.parse(JSON.stringify(state)); changedPhysical.created_at='2030-01-01T00:00:00Z';
test('state commitment ignores publication timestamp',stateCommitment(state).digest===stateCommitment(changedPhysical).digest);

const unicodeA=JSON.parse(JSON.stringify(state));
unicodeA.members=[
  {artifact_id:'urn:test:ä',logical_contract:{id:'x',version:'1'},logical_commitment:{profile:'p',digest:'sha256:'+'1'.repeat(64)}},
  {artifact_id:'urn:test:z',logical_contract:{id:'x',version:'1'},logical_commitment:{profile:'p',digest:'sha256:'+'2'.repeat(64)}}
];
const unicodeB=JSON.parse(JSON.stringify(unicodeA)); unicodeB.members=[...unicodeB.members].reverse();
test('state commitment ordering is locale-independent and deterministic',stateCommitment(unicodeA).digest===stateCommitment(unicodeB).digest);
const unknownProfile=JSON.parse(JSON.stringify(state));unknownProfile.logical_commitment={profile:'unsupported-profile',digest:'sha256:'+'0'.repeat(64)};
const unknownCheck=verifyStateSnapshot(unknownProfile);
test('unknown state commitment profile is never verified',!unknownCheck.ok&&unknownCheck.issues.some(i=>i.code==='UNSUPPORTED_PROFILE'));
const wrongDigest=JSON.parse(JSON.stringify(state));wrongDigest.logical_commitment={...wrongDigest.logical_commitment,digest:'sha256:'+'0'.repeat(64)};
const wrongCheck=verifyStateSnapshot(wrongDigest);
test('wrong state commitment digest is rejected',!wrongCheck.ok&&wrongCheck.issues.some(i=>i.code==='DIGEST_MISMATCH'));

const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'kristal-v9-'));
const published=publishStateSnapshot(state,tmp);
test('state publish uses logical commitment',published.logical_commitment.digest===state.logical_commitment.digest);
const pointer=path.join(tmp,'channels','production.json');
const active=activateChannel(activation,pointer);
test('activation pointer written atomically',active.ok&&JSON.parse(fs.readFileSync(pointer,'utf8')).active_state.logical_commitment.digest===state.logical_commitment.digest);
let staleRejected=false;try{activateChannel({...activation,sequence:0},pointer);}catch(e){staleRejected=/expected_previous|required|sequence/.test(e.message);}test('existing activation requires compare-and-swap precondition',staleRejected);
const next={...activation,sequence:2,expected_previous:activation.active_state,previous_state:activation.active_state};
const nextActive=activateChannel(next,pointer);test('activation sequence advances under lock and CAS',nextActive.sequence===2);
let regressionRejected=false;try{activateChannel({...next,sequence:1},pointer);}catch(e){regressionRejected=true;}test('activation sequence regression rejected',regressionRejected);
fs.rmSync(tmp,{recursive:true,force:true});
const kmc=load('contracts/knowledge-model-contract.v5.json');
test('active knowledge-model contract v5 verifies',verifyKnowledgeModelContract(kmc,ROOT).ok);
const caps=referenceV9Capabilities();
test('v9 capabilities preserve v6-v8 reads',caps.compatibility.reads.includes('kristal_state/6.0')&&caps.compatibility.reads.includes('kristall/8.0'));
if(failed)process.exit(1);console.log('Kristal v9 reference tests: PASS');
