import { sha256Hex } from '../hash.mjs';
import {
  encodedBytes, collectSemanticRefs, deepReplaceSemanticIds, deepExpandSemanticIds,
  isObject, AI_COMPACT_PROFILE,
} from './common.mjs';

function priority(kind,isRoot=false){
  if(isRoot)return 130;
  return ({assertion:120,evidence_ref:115,conflict:110,edge:100,property:90,entity:80,source:75,unresolved:70})[kind]??60;
}

function atom(kind,payload,index,queryResult,rootIds){
  const refs=collectSemanticRefs(payload);
  const ids=new Set(refs.map(x=>x.id));
  const isRoot=[...rootIds].some(id=>ids.has(id) || payload?.id===id);
  return {
    atom_id:`atom:${kind}:${String(index).padStart(6,'0')}`,kind,semantic_refs:refs,payload,
    provenance:(queryResult.source_fingerprints??[]).map(x=>({source_ref:x.ref,fingerprint_ref:x.byte_sha256,retrieval_reason:'ai_context_compilation'})),
    trust_class:'derived',priority:priority(kind,isRoot),
  };
}

function buildCandidates(q){
  const roots=new Set((q.resolved_roots??[]).map(x=>x.id)); const out=[];
  for(const [i,x] of (q.result?.assertions??[]).entries())out.push(atom('assertion',x,i,q,roots));
  for(const [i,x] of (q.result?.evidence??[]).entries())out.push(atom('evidence_ref',x,i,q,roots));
  for(const [i,x] of (q.result?.edges??[]).entries())out.push(atom('edge',x,i,q,roots));
  for(const [i,x] of (q.result?.nodes??[]).entries()){
    const kind=x.kind==='property'?'property':x.kind==='source'?'source':'entity';out.push(atom(kind,x,i,q,roots));
  }
  for(const [i,x] of (q.conflicts??[]).entries())out.push(atom('conflict',x,i,q,roots));
  for(const [i,x] of (q.unresolved??[]).entries())out.push(atom('unresolved',x,i,q,roots));
  return out.sort((a,b)=>(b.priority-a.priority)||a.atom_id.localeCompare(b.atom_id));
}

function heuristicTokens(value){return Math.max(1,Math.ceil(encodedBytes(value)/4));}

function compactAtoms(atoms){
  const ids=[]; const seen=new Set();
  for(const a of atoms)for(const r of a.semantic_refs??[])if(!seen.has(r.id)){seen.add(r.id);ids.push(r.id);}
  const symbolById=new Map(ids.map((id,i)=>[id,i]));
  const symbol_table=Object.fromEntries(ids.map((id,i)=>[String(i),id]));
  const compacted=atoms.map(a=>({...a,payload:deepReplaceSemanticIds(a.payload,symbolById)}));
  return {atoms:compacted,symbol_table};
}

export function expandCompactContext(bundle){
  if(bundle.encoding!=='symbol_table_v1')return bundle;
  const out=structuredClone(bundle);
  const table=out.context?.symbol_table??{};
  out.context.atoms=(out.context?.atoms??[]).map(a=>({...a,payload:deepExpandSemanticIds(a.payload,table)}));
  out.encoding='expanded_json';delete out.context.symbol_table;delete out.context.compact_profile;
  return out;
}

export function compileAIContext(queryResult,{
  maxBytes=131072,maxTokens=null,tokenizerId=null,tokenCounter=null,encoding='expanded_json',intent=null,
}={}){
  if(!isObject(queryResult)||queryResult.artifact_type!=='kristall_query_result')throw new Error('compileAIContext requires kristall_query_result');
  if(!Number.isInteger(maxBytes)||maxBytes<256)throw new Error('maxBytes must be integer >=256');
  if(maxTokens!==null&&(!Number.isInteger(maxTokens)||maxTokens<128))throw new Error('maxTokens must be null or integer >=128');
  if(maxTokens!==null&&!tokenizerId)throw new Error('tokenizerId required with maxTokens');
  const candidates=buildCandidates(queryResult); const chosen=[]; const dropped=[];
  const root=queryResult.resolved_roots??[];
  const tokenFn=tokenCounter??heuristicTokens;
  const estimateKind=tokenCounter?'exact':'heuristic';

  function draft(atoms,bundleId='AICB-'+('0'.repeat(16))){
    const ctx=encoding==='symbol_table_v1'?compactAtoms(atoms):{atoms};
    return {
      schema_version:'8.0',artifact_type:'kristall_ai_context_bundle',bundle_id:bundleId,query_id:queryResult.query_id,
      source_fingerprints:queryResult.source_fingerprints??[],roots:root,encoding,
      budget:{max_bytes:maxBytes,used_bytes:0,...(maxTokens!==null?{max_tokens:maxTokens,estimated_tokens:0,tokenizer_id:tokenizerId,token_estimate_kind:estimateKind}:{})},
      selection:{policy:'semantic_atom_priority',intent:intent??queryResult.query_plan?.intent??queryResult.mode,atom_ordering:'priority_then_stable_id'},
      completeness:structuredClone(queryResult.completeness??{semantic_closure:'unknown',evidence_closure:'unknown',source_coverage:'unknown',truncated:false,reasons:[]}),
      context:ctx,unresolved:queryResult.unresolved??[],omissions:[...(queryResult.omissions??[])],
    };
  }

  for(const candidate of candidates){
    const test=draft([...chosen,candidate]);
    const bytes=encodedBytes(test);const tokens=maxTokens!==null?tokenFn(test):0;
    if(bytes<=maxBytes&&(maxTokens===null||tokens<=maxTokens))chosen.push(candidate);else dropped.push(candidate);
  }
  let doc=draft(chosen);
  if(dropped.length){
    doc.completeness.truncated=true;
    if(doc.completeness.semantic_closure==='complete')doc.completeness.semantic_closure='partial';
    doc.completeness.reasons=[...new Set([...(doc.completeness.reasons??[]),'ai_context_budget'])].sort();
    doc.omissions.push({kind:'ai_context_budget',count:dropped.length,atom_ids:dropped.map(x=>x.atom_id)});
  }
  const identityCore=structuredClone(doc); identityCore.bundle_id='';identityCore.budget.used_bytes=0;if('estimated_tokens'in identityCore.budget)identityCore.budget.estimated_tokens=0;
  doc.bundle_id=`AICB-${sha256Hex(Buffer.from(JSON.stringify(identityCore),'utf8')).slice(0,16)}`;
  doc.budget.used_bytes=encodedBytes(doc);
  if(maxTokens!==null)doc.budget.estimated_tokens=tokenFn(doc);
  // Fixed-point guard: accounting fields can increase the payload by a few bytes.
  while((doc.budget.used_bytes>maxBytes)||(maxTokens!==null&&doc.budget.estimated_tokens>maxTokens)){
    const atoms=doc.context.atoms??[];if(!atoms.length)throw new Error('AI context metadata exceeds requested budget');
    const removed=chosen.pop();dropped.unshift(removed);doc=draft(chosen,doc.bundle_id);
    doc.completeness.truncated=true;if(doc.completeness.semantic_closure==='complete')doc.completeness.semantic_closure='partial';
    doc.completeness.reasons=[...new Set([...(doc.completeness.reasons??[]),'ai_context_budget'])].sort();
    doc.omissions.push({kind:'ai_context_budget',count:dropped.length,atom_ids:dropped.map(x=>x.atom_id)});
    doc.budget.used_bytes=encodedBytes(doc);if(maxTokens!==null)doc.budget.estimated_tokens=tokenFn(doc);
  }
  return doc;
}
