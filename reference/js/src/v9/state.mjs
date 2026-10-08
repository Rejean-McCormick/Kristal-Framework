import { cloneJson, canonicalize } from '../jcs.mjs';
import { LOGICAL_PROFILE, STATE_PROFILE, commitmentDigest, compareUtf8Lexicographic, isObject, sortArtifactRefs, sortStateRefs } from './common.mjs';

const SUPPORTED_LOGICAL_PROFILES = new Set([LOGICAL_PROFILE]);
const SUPPORTED_STATE_PROFILES = new Set([STATE_PROFILE]);
const DIGEST=/^sha256:[0-9a-f]{64}$/;

function issue(issues,path,message,code='INVALID_DOCUMENT'){issues.push({path,code,message});}
function commitmentOk(c){return isObject(c)&&typeof c.profile==='string'&&DIGEST.test(c.digest??'');}

export function artifactLogicalProjection(artifact) {
  const out = { payload: cloneJson(artifact.payload) };
  if (artifact.scope !== undefined) out.scope = cloneJson(artifact.scope);
  if (artifact.extensions !== undefined) out.extensions = cloneJson(artifact.extensions);
  if (Array.isArray(artifact.dependencies) && artifact.dependencies.length) out.dependencies = sortArtifactRefs(artifact.dependencies);
  return out;
}

export function logicalArtifactCommitment(artifact, { profile = LOGICAL_PROFILE } = {}) {
  if (!isObject(artifact?.logical_contract) || typeof artifact.logical_contract.id !== 'string' || typeof artifact.logical_contract.version !== 'string') throw new Error('logical_contract id/version required');
  if (!SUPPORTED_LOGICAL_PROFILES.has(profile)) throw new Error(`unsupported logical commitment profile: ${profile}`);
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
  refs.sort((a,b) => compareUtf8Lexicographic(canonicalize(a),canonicalize(b)));
  const out = { members, references: refs };
  if (state.scope !== undefined) out.scope = cloneJson(state.scope);
  return out;
}

export function stateCommitment(state, { profile = STATE_PROFILE } = {}) {
  if (!SUPPORTED_STATE_PROFILES.has(profile)) throw new Error(`unsupported state commitment profile: ${profile}`);
  const domain = `KRISTAL\u0000STATE-COMMITMENT\u0000${profile}\u0000`;
  return { profile, digest: commitmentDigest(domain, stateLogicalProjection(state)) };
}

export function verifyLogicalArtifact(artifact,{requireCommitment=true}={}){
  const issues=[];
  if(!isObject(artifact)) return {ok:false,issues:[{path:'$',code:'INVALID_TYPE',message:'artifact must be object'}]};
  if(artifact.schema_version!=='9.0')issue(issues,'$.schema_version','expected 9.0','SCHEMA_VERSION_MISMATCH');
  if(artifact.artifact_type!=='kristal_logical_artifact')issue(issues,'$.artifact_type','expected kristal_logical_artifact','ARTIFACT_TYPE_MISMATCH');
  if(typeof artifact.artifact_id!=='string'||!artifact.artifact_id)issue(issues,'$.artifact_id','artifact_id required','MISSING_FIELD');
  if(!isObject(artifact.logical_contract)||typeof artifact.logical_contract.id!=='string'||typeof artifact.logical_contract.version!=='string')issue(issues,'$.logical_contract','logical_contract id/version required','INVALID_CONTRACT');

  if(requireCommitment&&!commitmentOk(artifact.logical_commitment)) issue(issues,'$.logical_commitment','valid logical commitment required','INVALID_COMMITMENT');
  const declaredProfile=artifact.logical_commitment?.profile;
  if(declaredProfile && !SUPPORTED_LOGICAL_PROFILES.has(declaredProfile)) issue(issues,'$.logical_commitment.profile',`unsupported logical commitment profile: ${declaredProfile}`,'UNSUPPORTED_PROFILE');

  let calculated=null;
  if(!declaredProfile || SUPPORTED_LOGICAL_PROFILES.has(declaredProfile)) {
    try{calculated=logicalArtifactCommitment(artifact,{profile:declaredProfile??LOGICAL_PROFILE});}
    catch(e){issue(issues,'$.logical_commitment',e.message,'COMMITMENT_CALCULATION_FAILED');}
  }
  if(calculated&&commitmentOk(artifact.logical_commitment)&&artifact.logical_commitment.digest!==calculated.digest)
    issue(issues,'$.logical_commitment.digest','declared logical commitment does not match logical content','DIGEST_MISMATCH');
  return {ok:issues.length===0,issues,commitment:calculated};
}

export function verifyStateSnapshot(state,{requireCommitment=true}={}){
  const issues=[];
  if(!isObject(state)) return {ok:false,issues:[{path:'$',code:'INVALID_TYPE',message:'state must be object'}]};
  if(state.schema_version!=='9.0')issue(issues,'$.schema_version','expected 9.0','SCHEMA_VERSION_MISMATCH');
  if(state.artifact_type!=='kristal_state_snapshot')issue(issues,'$.artifact_type','expected kristal_state_snapshot','ARTIFACT_TYPE_MISMATCH');
  if(typeof state.state_ref!=='string'||!state.state_ref)issue(issues,'$.state_ref','state_ref required','MISSING_FIELD');
  if(!Array.isArray(state.members))issue(issues,'$.members','members must be array','INVALID_TYPE');
  if(!Array.isArray(state.references))issue(issues,'$.references','references must be array','INVALID_TYPE');
  const memberIds=new Set();
  if(Array.isArray(state.members)) for(const [i,m] of state.members.entries()){
    if(!isObject(m)||typeof m.artifact_id!=='string'||!isObject(m.logical_contract)||typeof m.logical_contract.id!=='string'||typeof m.logical_contract.version!=='string')issue(issues,`$.members[${i}]`,'artifact reference with logical_contract required','INVALID_REFERENCE');
    else if(memberIds.has(m.artifact_id))issue(issues,`$.members[${i}].artifact_id`,'duplicate owned artifact_id','DUPLICATE_ID');
    else memberIds.add(m.artifact_id);
    if(!commitmentOk(m?.logical_commitment))issue(issues,`$.members[${i}].logical_commitment`,'valid logical commitment required','INVALID_COMMITMENT');
  }

  if(requireCommitment&&!commitmentOk(state.logical_commitment)) issue(issues,'$.logical_commitment','valid state commitment required','INVALID_COMMITMENT');
  const declaredProfile=state.logical_commitment?.profile;
  if(declaredProfile && !SUPPORTED_STATE_PROFILES.has(declaredProfile)) issue(issues,'$.logical_commitment.profile',`unsupported state commitment profile: ${declaredProfile}`,'UNSUPPORTED_PROFILE');

  let calculated=null;
  if(!declaredProfile || SUPPORTED_STATE_PROFILES.has(declaredProfile)) {
    try{calculated=stateCommitment(state,{profile:declaredProfile??STATE_PROFILE});}
    catch(e){issue(issues,'$.logical_commitment',e.message,'COMMITMENT_CALCULATION_FAILED');}
  }
  if(calculated&&commitmentOk(state.logical_commitment)&&state.logical_commitment.digest!==calculated.digest)
    issue(issues,'$.logical_commitment.digest','declared state commitment does not match logical state','DIGEST_MISMATCH');
  return {ok:issues.length===0,issues,commitment:calculated};
}
