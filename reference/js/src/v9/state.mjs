import { cloneJson, canonicalize } from '../jcs.mjs';
import { LOGICAL_PROFILE, STATE_PROFILE, commitmentDigest, isObject, sortArtifactRefs, sortStateRefs } from './common.mjs';

export function artifactLogicalProjection(artifact) {
  const out = { payload: cloneJson(artifact.payload) };
  if (artifact.scope !== undefined) out.scope = cloneJson(artifact.scope);
  if (artifact.extensions !== undefined) out.extensions = cloneJson(artifact.extensions);
  if (Array.isArray(artifact.dependencies) && artifact.dependencies.length) out.dependencies = sortArtifactRefs(artifact.dependencies);
  return out;
}

export function logicalArtifactCommitment(artifact, { profile = LOGICAL_PROFILE } = {}) {
  if (!isObject(artifact?.logical_contract) || typeof artifact.logical_contract.id !== 'string' || typeof artifact.logical_contract.version !== 'string') throw new Error('logical_contract id/version required');
  if (profile !== LOGICAL_PROFILE) throw new Error(`unsupported logical commitment profile: ${profile}`);
  const domain = `KRISTAL\u0000LOGICAL-COMMITMENT\u0000${profile}\u0000${artifact.logical_contract.id}\u0000${artifact.logical_contract.version}\u0000`;
  return { profile, digest: commitmentDigest(domain, artifactLogicalProjection(artifact)) };
}

export function stateLogicalProjection(state) {
  const members = sortArtifactRefs(state.members ?? []);
  const refs = [];
  for (const ref of state.references ?? []) {
    if (ref.artifact_id) refs.push({ kind:'artifact', value: sortArtifactRefs([ref])[0] });
    else if (ref.state_ref) refs.push({ kind:'state', value: sortStateRefs([ref])[0] });
  }
  refs.sort((a,b) => canonicalize(a).localeCompare(canonicalize(b)));
  const out = { members, references: refs };
  if (state.scope !== undefined) out.scope = cloneJson(state.scope);
  return out;
}

export function stateCommitment(state, { profile = STATE_PROFILE } = {}) {
  if (profile !== STATE_PROFILE) throw new Error(`unsupported state commitment profile: ${profile}`);
  const domain = `KRISTAL\u0000STATE-COMMITMENT\u0000${profile}\u0000`;
  return { profile, digest: commitmentDigest(domain, stateLogicalProjection(state)) };
}

function issue(issues,path,message){issues.push({path,message});}
const DIGEST=/^sha256:[0-9a-f]{64}$/;
function commitmentOk(c){return isObject(c)&&typeof c.profile==='string'&&DIGEST.test(c.digest??'');}

export function verifyLogicalArtifact(artifact,{requireCommitment=true}={}){
  const issues=[];
  if(!isObject(artifact)) return {ok:false,issues:[{path:'$',message:'artifact must be object'}]};
  if(artifact.schema_version!=='9.0')issue(issues,'$.schema_version','expected 9.0');
  if(artifact.artifact_type!=='kristal_logical_artifact')issue(issues,'$.artifact_type','expected kristal_logical_artifact');
  if(typeof artifact.artifact_id!=='string'||!artifact.artifact_id)issue(issues,'$.artifact_id','artifact_id required');
  if(!isObject(artifact.logical_contract)||typeof artifact.logical_contract.id!=='string'||typeof artifact.logical_contract.version!=='string')issue(issues,'$.logical_contract','logical_contract id/version required');
  let calculated=null;
  try{calculated=logicalArtifactCommitment(artifact);}catch(e){issue(issues,'$.logical_commitment',e.message);}
  if(requireCommitment&&!commitmentOk(artifact.logical_commitment))issue(issues,'$.logical_commitment','valid logical commitment required');
  if(calculated&&artifact.logical_commitment&&artifact.logical_commitment.profile===calculated.profile&&artifact.logical_commitment.digest!==calculated.digest)issue(issues,'$.logical_commitment.digest','declared logical commitment does not match logical content');
  return {ok:issues.length===0,issues,commitment:calculated};
}

export function verifyStateSnapshot(state,{requireCommitment=true}={}){
  const issues=[];
  if(!isObject(state)) return {ok:false,issues:[{path:'$',message:'state must be object'}]};
  if(state.schema_version!=='9.0')issue(issues,'$.schema_version','expected 9.0');
  if(state.artifact_type!=='kristal_state_snapshot')issue(issues,'$.artifact_type','expected kristal_state_snapshot');
  if(typeof state.state_ref!=='string'||!state.state_ref)issue(issues,'$.state_ref','state_ref required');
  if(!Array.isArray(state.members))issue(issues,'$.members','members must be array');
  if(!Array.isArray(state.references))issue(issues,'$.references','references must be array');
  const memberIds=new Set();
  for(const [i,m] of (state.members??[]).entries()){
    if(!isObject(m)||typeof m.artifact_id!=='string'||!isObject(m.logical_contract)||typeof m.logical_contract.id!=='string'||typeof m.logical_contract.version!=='string')issue(issues,`$.members[${i}]`,'artifact reference with logical_contract required');
    else if(memberIds.has(m.artifact_id))issue(issues,`$.members[${i}].artifact_id`,'duplicate owned artifact_id');
    else memberIds.add(m.artifact_id);
    if(!commitmentOk(m?.logical_commitment))issue(issues,`$.members[${i}].logical_commitment`,'valid logical commitment required');
  }
  let calculated=null;
  try{calculated=stateCommitment(state);}catch(e){issue(issues,'$.logical_commitment',e.message);}
  if(requireCommitment&&!commitmentOk(state.logical_commitment))issue(issues,'$.logical_commitment','valid state commitment required');
  if(calculated&&state.logical_commitment&&state.logical_commitment.profile===calculated.profile&&state.logical_commitment.digest!==calculated.digest)issue(issues,'$.logical_commitment.digest','declared state commitment does not match logical state');
  return {ok:issues.length===0,issues,commitment:calculated};
}
