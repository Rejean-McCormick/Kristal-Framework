import fs from 'node:fs';
import path from 'node:path';
import { canonicalize } from '../jcs.mjs';
import { verifyStateSnapshot } from './state.mjs';
import { verifyActivation } from './contracts.mjs';

function atomicWriteJson(file, value){
 const abs=path.resolve(file); fs.mkdirSync(path.dirname(abs),{recursive:true});
 const tmp=`${abs}.tmp-${process.pid}`; fs.writeFileSync(tmp,JSON.stringify(value,null,2)+'\n','utf8'); fs.renameSync(tmp,abs);
}
export function publishStateSnapshot(state, storeDir){
 const result=verifyStateSnapshot(state); if(!result.ok)throw new Error(result.issues.map(x=>`${x.path}: ${x.message}`).join('; '));
 const digest=result.commitment.digest.slice('sha256:'.length); const dir=path.join(storeDir,'states'); fs.mkdirSync(dir,{recursive:true});
 const target=path.join(dir,`${digest}.json`); const bytes=JSON.stringify(state,null,2)+'\n';
 if(fs.existsSync(target)){ const current=fs.readFileSync(target,'utf8'); if(canonicalize(JSON.parse(current))!==canonicalize(state))throw new Error('immutable state path collision'); }
 else fs.writeFileSync(target,bytes,'utf8');
 return {state_ref:state.state_ref,logical_commitment:result.commitment,path:target};
}
export function activateChannel(activation, pointerFile){
 const check=verifyActivation(activation); if(!check.ok)throw new Error(check.issues.map(x=>`${x.path}: ${x.message}`).join('; '));
 let current=null; if(fs.existsSync(pointerFile))current=JSON.parse(fs.readFileSync(pointerFile,'utf8'));
 if(activation.expected_previous){
   const got=current?.active_state?.logical_commitment?.digest??null;
   const expected=activation.expected_previous.logical_commitment.digest;
   if(got!==expected)throw new Error(`activation compare-and-swap failed: expected ${expected}, found ${got}`);
 }
 atomicWriteJson(pointerFile,activation); return {ok:true,channel_id:activation.channel_id,active_state:activation.active_state,sequence:activation.sequence};
}
