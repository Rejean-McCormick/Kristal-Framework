import fs from 'node:fs';
import path from 'node:path';
import { canonicalize } from '../jcs.mjs';
import { verifyStateSnapshot } from './state.mjs';
import { verifyActivation } from './contracts.mjs';

function atomicWriteJson(file, value){
 const abs=path.resolve(file); fs.mkdirSync(path.dirname(abs),{recursive:true});
 const tmp=`${abs}.tmp-${process.pid}-${Date.now()}`;
 const fd=fs.openSync(tmp,'wx');
 try { fs.writeFileSync(fd,JSON.stringify(value,null,2)+'\n','utf8'); fs.fsyncSync(fd); }
 finally { fs.closeSync(fd); }
 fs.renameSync(tmp,abs);
 // Best-effort directory sync for crash durability on POSIX.
 try { const dfd=fs.openSync(path.dirname(abs),'r'); try{fs.fsyncSync(dfd);}finally{fs.closeSync(dfd);} } catch {}
}
function sameStateRef(a,b){
 return !!a&&!!b&&a.state_ref===b.state_ref&&a.logical_commitment?.profile===b.logical_commitment?.profile&&a.logical_commitment?.digest===b.logical_commitment?.digest;
}
function withInterprocessLock(target, fn){
 const lock=`${path.resolve(target)}.lock`;
 fs.mkdirSync(path.dirname(lock),{recursive:true});
 let fd;
 try { fd=fs.openSync(lock,'wx'); }
 catch(e){ if(e?.code==='EEXIST') throw new Error(`activation lock busy: ${lock}`); throw e; }
 try { return fn(); }
 finally { try{fs.closeSync(fd);}finally{try{fs.unlinkSync(lock);}catch{}} }
}

export function publishStateSnapshot(state, storeDir){
 const result=verifyStateSnapshot(state); if(!result.ok)throw new Error(result.issues.map(x=>`${x.code??'ERROR'} ${x.path}: ${x.message}`).join('; '));
 const digest=result.commitment.digest.slice('sha256:'.length); const dir=path.join(storeDir,'states'); fs.mkdirSync(dir,{recursive:true});
 const target=path.join(dir,`${digest}.json`); const bytes=JSON.stringify(state,null,2)+'\n';
 if(fs.existsSync(target)){ const current=fs.readFileSync(target,'utf8'); if(canonicalize(JSON.parse(current))!==canonicalize(state))throw new Error('immutable state path collision'); }
 else fs.writeFileSync(target,bytes,'utf8');
 return {state_ref:state.state_ref,logical_commitment:result.commitment,path:target};
}
export function activateChannel(activation, pointerFile){
 const check=verifyActivation(activation); if(!check.ok)throw new Error(check.issues.map(x=>`${x.path}: ${x.message}`).join('; '));
 return withInterprocessLock(pointerFile,()=>{
   let current=null; if(fs.existsSync(pointerFile))current=JSON.parse(fs.readFileSync(pointerFile,'utf8'));
   if(current){
     if(current.channel_id!==activation.channel_id) throw new Error(`activation channel mismatch: existing ${current.channel_id}, requested ${activation.channel_id}`);
     if(!activation.expected_previous) throw new Error('activation expected_previous is required when a channel already exists');
     if(!sameStateRef(current.active_state,activation.expected_previous)) throw new Error('activation compare-and-swap failed: expected_previous does not match current active state');
     if(activation.sequence!==current.sequence+1) throw new Error(`activation sequence must advance exactly by one: current ${current.sequence}, requested ${activation.sequence}`);
     if(activation.previous_state!==undefined&&!sameStateRef(current.active_state,activation.previous_state)) throw new Error('activation previous_state does not match current active state');
   }
   atomicWriteJson(pointerFile,activation);
   return {ok:true,channel_id:activation.channel_id,active_state:activation.active_state,sequence:activation.sequence};
 });
}
