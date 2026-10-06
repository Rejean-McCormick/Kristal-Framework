function isObject(v){return !!v&&typeof v==='object'&&!Array.isArray(v);}
const DIGEST=/^sha256:[0-9a-f]{64}$/;
function issue(issues,path,message){issues.push({path,message});}
function commitmentOk(c){return isObject(c)&&typeof c.profile==='string'&&DIGEST.test(c.digest??'');}
function blobOk(b){return isObject(b)&&typeof b.media_type==='string'&&DIGEST.test(b.digest??'')&&Number.isInteger(b.size)&&b.size>=0;}
function artifactRefOk(r){return isObject(r)&&typeof r.artifact_id==='string'&&isObject(r.logical_contract)&&typeof r.logical_contract.id==='string'&&typeof r.logical_contract.version==='string'&&commitmentOk(r.logical_commitment);}
function stateRefOk(r){return isObject(r)&&typeof r.state_ref==='string'&&commitmentOk(r.logical_commitment);}

export function verifyDerivation(doc){
 const issues=[];
 if(!isObject(doc))return{ok:false,issues:[{path:'$',message:'derivation must be object'}]};
 if(doc.schema_version!=='9.0')issue(issues,'$.schema_version','expected 9.0');
 if(doc.artifact_type!=='kristal_derivation')issue(issues,'$.artifact_type','expected kristal_derivation');
 if(!isObject(doc.transform)||typeof doc.transform.id!=='string'||typeof doc.transform.version!=='string')issue(issues,'$.transform','transform id/version required');
 if(!Array.isArray(doc.inputs))issue(issues,'$.inputs','inputs must be array');
 for(const [i,r] of (doc.inputs??[]).entries())if(!(artifactRefOk(r)||stateRefOk(r)))issue(issues,`$.inputs[${i}]`,'artifact or state logical reference required');
 if(!Array.isArray(doc.outputs)||!doc.outputs.length)issue(issues,'$.outputs','at least one output required');
 for(const [i,r] of (doc.outputs??[]).entries())if(!artifactRefOk(r))issue(issues,`$.outputs[${i}]`,'artifact logical reference required');
 if(doc.determinism?.claimed!==true&&doc.determinism?.claimed!==false)issue(issues,'$.determinism.claimed','boolean determinism claim required');
 return{ok:issues.length===0,issues};
}

export function verifyExchangeV9(doc){
 const issues=[];
 if(!isObject(doc))return{ok:false,issues:[{path:'$',message:'exchange must be object'}]};
 if(doc.schema_version!=='9.0')issue(issues,'$.schema_version','expected 9.0');
 if(doc.artifact_type!=='kristal_exchange')issue(issues,'$.artifact_type','expected kristal_exchange');
 if(!stateRefOk(doc.state))issue(issues,'$.state','valid state reference required');
 if(!blobOk(doc.state_blob))issue(issues,'$.state_blob','valid state blob descriptor required');
 if(!Array.isArray(doc.materializations))issue(issues,'$.materializations','materializations must be array');
 for(const [i,m] of (doc.materializations??[]).entries())if(!isObject(m)||typeof m.artifact_id!=='string'||!blobOk(m.manifest_blob))issue(issues,`$.materializations[${i}]`,'artifact_id and manifest blob required');
 return{ok:issues.length===0,issues};
}

export function verifyActivation(doc){
 const issues=[];
 if(!isObject(doc))return{ok:false,issues:[{path:'$',message:'activation must be object'}]};
 if(doc.schema_version!=='9.0')issue(issues,'$.schema_version','expected 9.0');
 if(doc.artifact_type!=='kristal_activation')issue(issues,'$.artifact_type','expected kristal_activation');
 if(typeof doc.channel_id!=='string'||!doc.channel_id)issue(issues,'$.channel_id','channel_id required');
 if(!stateRefOk(doc.active_state))issue(issues,'$.active_state','valid active state reference required');
 if(!Number.isInteger(doc.sequence)||doc.sequence<0)issue(issues,'$.sequence','non-negative integer sequence required');
 if(doc.previous_state!==undefined&&!stateRefOk(doc.previous_state))issue(issues,'$.previous_state','valid previous state reference required');
 if(doc.expected_previous!==undefined&&!stateRefOk(doc.expected_previous))issue(issues,'$.expected_previous','valid expected previous state reference required');
 return{ok:issues.length===0,issues};
}
