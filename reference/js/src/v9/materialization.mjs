const DIGEST=/^sha256:[0-9a-f]{64}$/;
function isObject(v){return !!v&&typeof v==='object'&&!Array.isArray(v);}
function issue(issues,path,message){issues.push({path,message});}
function blobOk(b){return isObject(b)&&typeof b.media_type==='string'&&DIGEST.test(b.digest??'')&&Number.isInteger(b.size)&&b.size>=0;}
export function verifyMaterializationManifest(doc){
 const issues=[];
 if(!isObject(doc))return{ok:false,issues:[{path:'$',message:'manifest must be object'}]};
 if(doc.schema_version!=='9.0')issue(issues,'$.schema_version','expected 9.0');
 if(doc.artifact_type!=='kristal_materialization_manifest')issue(issues,'$.artifact_type','expected kristal_materialization_manifest');
 if(!isObject(doc.source)||typeof doc.source.artifact_id!=='string')issue(issues,'$.source','logical source required');
 if(typeof doc.profile!=='string'||!doc.profile)issue(issues,'$.profile','profile required');
 if(!Array.isArray(doc.segments)||!doc.segments.length)issue(issues,'$.segments','at least one segment required');
 for(const [i,s] of (doc.segments??[]).entries())if(!blobOk(s?.blob))issue(issues,`$.segments[${i}].blob`,'valid blob descriptor required');
 if(doc.reconstructability?.lossless!==true)issue(issues,'$.reconstructability.lossless','v9 reference verifier requires lossless=true');
 return{ok:issues.length===0,issues};
}
