function isObject(v){return v!==null&&typeof v==='object'&&!Array.isArray(v);}
const DIGEST=/^sha256:[0-9a-f]{64}$/;
const ROLES=new Set(['collection','directory','publisher','gateway']);
const ACCOUNT_KINDS=new Set(['user','organization','enterprise','other']);
const VISIBILITIES=new Set(['public','private','internal','host-defined']);
const RESOURCE_ROLES=new Set(['state_snapshot','materialization_manifest','exchange','runtime_pack','query_index','lexicon','other']);
function issue(issues,path,message,code='INVALID_DOCUMENT'){issues.push({path,code,message});}
function nonEmpty(v){return typeof v==='string'&&v.length>0;}
function commitmentOk(c){return isObject(c)&&nonEmpty(c.profile)&&DIGEST.test(c.digest??'');}
function stateRefOk(s){return isObject(s)&&nonEmpty(s.state_ref)&&commitmentOk(s.logical_commitment);}
function base(doc,type){const issues=[];if(!isObject(doc))return{issues:[{path:'$',code:'INVALID_TYPE',message:'document must be object'}]};if(doc.schema_version!=='10.0')issue(issues,'$.schema_version','expected 10.0','SCHEMA_VERSION_MISMATCH');if(doc.artifact_type!==type)issue(issues,'$.artifact_type',`expected ${type}`,'ARTIFACT_TYPE_MISMATCH');return{issues};}
function bindingRefOk(v){return isObject(v)&&nonEmpty(v.binding_id)&&nonEmpty(v.profile)&&nonEmpty(v.descriptor);}
function verifySurface(issues,path,s){if(!isObject(s)){issue(issues,path,'surface must be object','INVALID_TYPE');return;}if(!nonEmpty(s.kind))issue(issues,`${path}.kind`,'surface kind required','MISSING_FIELD');if(s.locator!==undefined&&!nonEmpty(s.locator))issue(issues,`${path}.locator`,'locator must be non-empty when present','INVALID_VALUE');}

export function verifyNodeManifest(doc){
 const {issues}=base(doc,'kristal_node_manifest');
 if(!isObject(doc))return{ok:false,issues};
 if(!nonEmpty(doc.node_id))issue(issues,'$.node_id','node_id required','MISSING_FIELD');
 if(!Array.isArray(doc.roles)||!doc.roles.length)issue(issues,'$.roles','at least one role required','INVALID_TYPE');
 else {const seen=new Set();for(const [i,r] of doc.roles.entries()){if(!ROLES.has(r))issue(issues,`$.roles[${i}]`,`unsupported role: ${r}`,'UNSUPPORTED_ROLE');if(seen.has(r))issue(issues,`$.roles[${i}]`,'duplicate role','DUPLICATE_VALUE');seen.add(r);}}
 if(!Array.isArray(doc.semantic_state_contracts)||!doc.semantic_state_contracts.length)issue(issues,'$.semantic_state_contracts','at least one semantic state contract required','INVALID_TYPE');
 else for(const [i,c] of doc.semantic_state_contracts.entries())if(!nonEmpty(c))issue(issues,`$.semantic_state_contracts[${i}]`,'contract id required','INVALID_VALUE');
 if(!Array.isArray(doc.bindings))issue(issues,'$.bindings','bindings must be array','INVALID_TYPE');
 else {const ids=new Set();for(const [i,b] of doc.bindings.entries()){if(!bindingRefOk(b))issue(issues,`$.bindings[${i}]`,'binding_id/profile/descriptor required','INVALID_BINDING');else if(ids.has(b.binding_id))issue(issues,`$.bindings[${i}].binding_id`,'duplicate binding_id','DUPLICATE_ID');else ids.add(b.binding_id);}}
 if(doc.directories!==undefined&&!Array.isArray(doc.directories))issue(issues,'$.directories','directories must be array','INVALID_TYPE');
 return{ok:issues.length===0,issues};
}

export function verifyHostBinding(doc){
 const {issues}=base(doc,'kristal_host_binding');
 if(!isObject(doc))return{ok:false,issues};
 for(const k of ['binding_id','node_id'])if(!nonEmpty(doc[k]))issue(issues,`$.${k}`,`${k} required`,'MISSING_FIELD');
 if(!isObject(doc.profile)||!nonEmpty(doc.profile.id)||!nonEmpty(doc.profile.version))issue(issues,'$.profile','profile id/version required','INVALID_PROFILE');
 if(!isObject(doc.host)){issue(issues,'$.host','host object required','INVALID_TYPE');}
 else {if(!nonEmpty(doc.host.provider))issue(issues,'$.host.provider','provider required','MISSING_FIELD');if(!isObject(doc.host.account_scope))issue(issues,'$.host.account_scope','account_scope required','INVALID_TYPE');else{if(!ACCOUNT_KINDS.has(doc.host.account_scope.kind))issue(issues,'$.host.account_scope.kind','unsupported account kind','INVALID_VALUE');if(!nonEmpty(doc.host.account_scope.owner))issue(issues,'$.host.account_scope.owner','owner required','MISSING_FIELD');}}
 if(!isObject(doc.resource)){issue(issues,'$.resource','resource object required','INVALID_TYPE');}
 else {if(!nonEmpty(doc.resource.kind))issue(issues,'$.resource.kind','resource kind required','MISSING_FIELD');if(!nonEmpty(doc.resource.locator))issue(issues,'$.resource.locator','resource locator required','MISSING_FIELD');if(doc.resource.visibility!==undefined&&!VISIBILITIES.has(doc.resource.visibility))issue(issues,'$.resource.visibility','unsupported visibility','INVALID_VALUE');}
 if(!isObject(doc.surfaces))issue(issues,'$.surfaces','surfaces object required','INVALID_TYPE');
 else for(const [name,s] of Object.entries(doc.surfaces))verifySurface(issues,`$.surfaces.${name}`,s);
 return{ok:issues.length===0,issues};
}

export function verifyPublication(doc){
 const {issues}=base(doc,'kristal_publication');
 if(!isObject(doc))return{ok:false,issues};
 for(const k of ['publication_id','node_id','binding_id'])if(!nonEmpty(doc[k]))issue(issues,`$.${k}`,`${k} required`,'MISSING_FIELD');
 if(!stateRefOk(doc.state))issue(issues,'$.state','exact state reference required','INVALID_STATE_REFERENCE');
 if(!Array.isArray(doc.resources)||!doc.resources.length)issue(issues,'$.resources','at least one resource required','INVALID_TYPE');
 else for(const [i,r] of doc.resources.entries()){
   const path=`$.resources[${i}]`;
   if(!isObject(r)){issue(issues,path,'resource must be object','INVALID_TYPE');continue;}
   if(!RESOURCE_ROLES.has(r.role))issue(issues,`${path}.role`,'supported resource role required','INVALID_VALUE');
   if(!nonEmpty(r.locator))issue(issues,`${path}.locator`,'locator required','MISSING_FIELD');
   if(!nonEmpty(r.media_type))issue(issues,`${path}.media_type`,'media_type required for verifiable publication','MISSING_FIELD');
   if(!Number.isInteger(r.size)||r.size<0)issue(issues,`${path}.size`,'non-negative integer size required for verifiable publication','INVALID_SIZE');
   if(!DIGEST.test(r.blob_digest??''))issue(issues,`${path}.blob_digest`,'sha256 blob_digest required for verifiable publication','INVALID_DIGEST');
   if(r.logical_commitment!==undefined&&!commitmentOk(r.logical_commitment))issue(issues,`${path}.logical_commitment`,'invalid logical commitment','INVALID_COMMITMENT');
 }
 if(doc.attestations!==undefined&&!Array.isArray(doc.attestations))issue(issues,'$.attestations','attestations must be array','INVALID_TYPE');
 return{ok:issues.length===0,issues};
}

export function verifyDirectory(doc){
 const {issues}=base(doc,'kristal_directory');
 if(!isObject(doc))return{ok:false,issues};
 for(const k of ['directory_id','node_id'])if(!nonEmpty(doc[k]))issue(issues,`$.${k}`,`${k} required`,'MISSING_FIELD');
 if(!Array.isArray(doc.entries)){issue(issues,'$.entries','entries must be array','INVALID_TYPE');return{ok:false,issues};}
 const nodes=new Set();
 for(const [i,e] of doc.entries.entries()){
   const path=`$.entries[${i}]`;
   if(!isObject(e)){issue(issues,path,'directory entry must be object','INVALID_TYPE');continue;}
   if(!nonEmpty(e.node_id))issue(issues,`${path}.node_id`,'node_id required','MISSING_FIELD');
   else if(nodes.has(e.node_id))issue(issues,`${path}.node_id`,'duplicate node_id','DUPLICATE_ID');else nodes.add(e.node_id);
   if(e.roles!==undefined){if(!Array.isArray(e.roles))issue(issues,`${path}.roles`,'roles must be array','INVALID_TYPE');else for(const [j,r] of e.roles.entries())if(!ROLES.has(r))issue(issues,`${path}.roles[${j}]`,`unsupported role: ${r}`,'UNSUPPORTED_ROLE');}
   if(!Array.isArray(e.bindings)||!e.bindings.length)issue(issues,`${path}.bindings`,'at least one binding required','INVALID_BINDING');
   else for(const [j,b] of e.bindings.entries())if(!bindingRefOk(b))issue(issues,`${path}.bindings[${j}]`,'binding_id/profile/descriptor required','INVALID_BINDING');
   if(e.advertised_states!==undefined){if(!Array.isArray(e.advertised_states))issue(issues,`${path}.advertised_states`,'advertised_states must be array','INVALID_TYPE');else for(const [j,s] of e.advertised_states.entries())if(!stateRefOk(s))issue(issues,`${path}.advertised_states[${j}]`,'exact state reference required','INVALID_STATE_REFERENCE');}
   if(e.channels!==undefined){if(!isObject(e.channels))issue(issues,`${path}.channels`,'channels must be object','INVALID_TYPE');else for(const [name,s] of Object.entries(e.channels))if(!stateRefOk(s))issue(issues,`${path}.channels.${name}`,'exact state reference required','INVALID_STATE_REFERENCE');}
 }
 return{ok:issues.length===0,issues};
}

export function verifyGithubBinding(doc){
 const result=verifyHostBinding(doc);const issues=[...result.issues];
 if(doc?.profile?.id!=='kristal.host/github'||doc?.profile?.version!=='1.0')issue(issues,'$.profile','expected kristal.host/github 1.0','UNSUPPORTED_PROFILE');
 if(doc?.host?.provider!=='github.com')issue(issues,'$.host.provider','expected github.com','PROFILE_MISMATCH');
 if(doc?.resource?.kind!=='repository')issue(issues,'$.resource.kind','expected repository','PROFILE_MISMATCH');
 if(!isObject(doc?.profile_configuration)||!nonEmpty(doc.profile_configuration.repository)||!nonEmpty(doc.profile_configuration.default_branch))issue(issues,'$.profile_configuration','repository/default_branch required','INVALID_PROFILE_CONFIGURATION');
 if(isObject(doc?.profile_configuration)&&doc.profile_configuration.repository&&doc?.resource?.locator){const suffix=`/${doc.profile_configuration.repository}`;if(!doc.resource.locator.endsWith(suffix))issue(issues,'$.profile_configuration.repository','repository does not match resource locator','RELATION_MISMATCH');}
 return{ok:issues.length===0,issues};
}
