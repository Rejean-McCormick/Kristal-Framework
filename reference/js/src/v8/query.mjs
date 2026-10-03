import { cloneJson, canonicalize } from '../jcs.mjs';
import {
  isObject, encodedBytes, classifyIdentity, stableItemKey, semanticRefKey,
  normalizedQueryHash, sourceSetHash, encodeCursor, decodeCursor, STABLE_ORDERING_PROFILE,
} from './common.mjs';
import { createQueryIndex } from './query_index.mjs';

export const SUPPORTED_QUERY_MODES = new Set([
  'identity_lookup','neighborhood','semantic_traversal','evidence_closure','semantic_slice','unknowns'
]);

const ALL_QUERY_MODES = new Set([
  'identity_lookup','neighborhood','semantic_traversal','evidence_closure','authority_resolution',
  'temporal','diff','capability','constraints','cross_kristal','lexical','unknowns','semantic_slice'
]);
const DISCOVERY_MODES = new Set(['exact','lexical','semantic_similarity','hybrid']);
const DIRECTIONS = new Set(['out','in','both']);

function issue(issues,path,message){ issues.push({path,message}); }

export function verifyQueryRequest(doc) {
  const issues=[];
  if (!isObject(doc)) return {ok:false,issues:[{path:'$',message:'request must be object'}]};
  if (doc.schema_version!=='8.0') issue(issues,'$.schema_version','expected 8.0');
  if (doc.artifact_type!=='kristall_query_request') issue(issues,'$.artifact_type','expected kristall_query_request');
  if (doc.protocol!=='kristal-query/1.0') issue(issues,'$.protocol','expected kristal-query/1.0');
  if (typeof doc.query_id!=='string'||!doc.query_id) issue(issues,'$.query_id','query_id required');
  if (!ALL_QUERY_MODES.has(doc.mode)) issue(issues,'$.mode','unsupported query mode');
  if (!Array.isArray(doc.roots)||doc.roots.length===0) issue(issues,'$.roots','at least one root required');
  for (const [i,r] of (doc.roots??[]).entries()) {
    if (!isObject(r)||!['kristall','kristal_v6','external'].includes(r.identity_space)||typeof r.id!=='string'||!r.id) issue(issues,`$.roots[${i}]`,'invalid semantic root');
  }
  const discovery=doc.discovery?.mode ?? 'exact';
  if (!DISCOVERY_MODES.has(discovery)) issue(issues,'$.discovery.mode','unsupported discovery mode');
  if (discovery!=='exact' && !doc.discovery?.query_text) issue(issues,'$.discovery.query_text','non-exact discovery requires query_text');
  if (doc.traversal?.direction!==undefined && !DIRECTIONS.has(doc.traversal.direction)) issue(issues,'$.traversal.direction','unsupported direction');
  if (doc.traversal?.max_depth!==undefined && (!Number.isInteger(doc.traversal.max_depth)||doc.traversal.max_depth<0||doc.traversal.max_depth>64)) issue(issues,'$.traversal.max_depth','max_depth must be 0..64');
  if (!isObject(doc.budget)) issue(issues,'$.budget','budget required');
  else {
    for (const key of ['deadline_ms','max_items','max_bytes']) if (!Number.isInteger(doc.budget[key])||doc.budget[key]<1) issue(issues,`$.budget.${key}`,`${key} must be positive integer`);
    if (doc.budget.max_bytes!==undefined && doc.budget.max_bytes<256) issue(issues,'$.budget.max_bytes','max_bytes must be >=256');
    if (doc.budget.max_tokens!==undefined && (!Number.isInteger(doc.budget.max_tokens)||doc.budget.max_tokens<128)) issue(issues,'$.budget.max_tokens','max_tokens must be >=128');
    if (doc.budget.max_tokens!==undefined && (typeof doc.budget.tokenizer_id!=='string'||!doc.budget.tokenizer_id)) issue(issues,'$.budget.tokenizer_id','tokenizer_id required when max_tokens is used');
  }
  if (doc.pagination?.page_size!==undefined && (!Number.isInteger(doc.pagination.page_size)||doc.pagination.page_size<1||doc.pagination.page_size>10000)) issue(issues,'$.pagination.page_size','page_size must be 1..10000');
  return {ok:issues.length===0,issues,supported:SUPPORTED_QUERY_MODES.has(doc.mode)};
}

function graphKey(space,id){return `${space}\u0000${id}`;}
function endpointId(v){return isObject(v)?v.id:(typeof v==='string'?v:null);}
function endpointSpace(v){
  if (isObject(v) && typeof v.identity_space==='string') return v.identity_space;
  return classifyIdentity(endpointId(v));
}
function nodeRef(node){return {identity_space:node.identity_space,id:node.id,...(node.namespace?{namespace:node.namespace}:{})};}

function normalizedNode(node) {
  return {
    id:node.id,
    identity_space:node.identity_space,
    kind:node.kind,
    ...(node.record!==null&&node.record!==undefined?{record:node.record}:{}),
    ...(node.source_ref?{source_ref:node.source_ref}:{}),
  };
}

function edgePasses(edge, request) {
  const propSet=new Set([...(request.traversal?.properties??[]),...(request.filters?.property_ids??[])]);
  if (propSet.size && !propSet.has(edge.relation)) return false;
  const sem=new Set(request.traversal?.edge_semantics??[]);
  if (sem.size && !sem.has(edge.edge_semantics)) return false;
  return true;
}

function assertionPasses(item, request) {
  const a=item.record??item;
  const statuses=new Set(request.filters?.assertion_status??[]);
  if (statuses.size && !statuses.has(a.assertion_status??a.status)) return false;
  const roles=new Set(request.filters?.record_role??[]);
  if (roles.size && !roles.has(a.record_role)) return false;
  const sources=new Set(request.filters?.source_refs??[]);
  if (sources.size) {
    const src=item.source_ref??a.source_binding?.source_kristal_id;
    if (!sources.has(src)) return false;
  }
  return true;
}

function flattenResult(result) {
  const order=['nodes','edges','assertions','evidence'];
  const flat=[];
  for (const bucket of order) {
    const items=[...(result[bucket]??[])].sort((a,b)=>stableItemKey(a).localeCompare(stableItemKey(b)));
    for (const value of items) flat.push({bucket,value});
  }
  return flat;
}

function inflateResult(items) {
  const result={nodes:[],edges:[],assertions:[],evidence:[]};
  for (const item of items) result[item.bucket].push(item.value);
  return result;
}

function continuationBinding(request, sourceFingerprints) {
  return {q:normalizedQueryHash(request),s:sourceSetHash(sourceFingerprints)};
}

function pageResult(fullResult, request, sourceFingerprints) {
  const flat=flattenResult(fullResult);
  const binding=continuationBinding(request,sourceFingerprints);
  let offset=0;
  if (request.pagination?.cursor) {
    const cursor=decodeCursor(request.pagination.cursor);
    if (cursor.v!==1||cursor.q!==binding.q||cursor.s!==binding.s||!Number.isInteger(cursor.o)||cursor.o<0) throw new Error('continuation cursor does not match normalized query/source snapshot');
    offset=cursor.o;
  }
  const pageSize=Math.min(request.pagination?.page_size??Number.MAX_SAFE_INTEGER,request.budget.max_items??Number.MAX_SAFE_INTEGER);
  let selected=flat.slice(offset,offset+pageSize);
  let nextOffset=offset+selected.length;

  // max_bytes is a hard wire-payload ceiling. Reserve room for result metadata; trim until the complete result fits.
  function provisional(items, hasMore) {
    return {
      schema_version:'8.0',artifact_type:'kristall_query_result',protocol:'kristal-query/1.0',query_id:request.query_id,mode:request.mode,
      status:hasMore?'partial':'complete',source_fingerprints:sourceFingerprints,resolved_roots:[],resolution_candidates:[],result:inflateResult(items),
      completeness:{semantic_closure:hasMore?'partial':'complete',evidence_closure:'not_requested',source_coverage:'complete',truncated:hasMore,reasons:hasMore?['pagination_or_budget']:[]},
      continuation:{has_more:hasMore,...(hasMore?{cursor:'X'.repeat(220)}:{}),ordering_profile:STABLE_ORDERING_PROFILE},unresolved:[],conflicts:[],omissions:[],query_plan:{discovery:'exact',strategy:'identity_graph'}
    };
  }
  while (selected.length && encodedBytes(provisional(selected,nextOffset<flat.length)) > request.budget.max_bytes) {
    selected.pop(); nextOffset--;
  }
  if (!selected.length && offset<flat.length && encodedBytes(provisional([],true))>request.budget.max_bytes) throw new Error('max_bytes too small for KQP result metadata');
  const hasMore=nextOffset<flat.length;
  const continuation={has_more:hasMore,ordering_profile:STABLE_ORDERING_PROFILE};
  if (hasMore) continuation.cursor=encodeCursor({v:1,...binding,o:nextOffset});
  return {result:inflateResult(selected),continuation,omittedCount:flat.length-selected.length-offset,offset,total:flat.length,hasMore};
}

function gatherDirectEvidence(assertions,index) {
  const evidence=[]; const seen=new Set();
  for (const item of assertions) {
    const id=item.id??item.assertion_id??item.record?.assertion_id;
    for (const e of index.evidenceByAssertion.get(id)??[]) {
      const key=canonicalize(e); if(!seen.has(key)){seen.add(key);evidence.push(e);}
    }
  }
  return evidence;
}

function resolveRoots(request,index) {
  const resolved=[]; const unresolved=[];
  for (const ref of request.roots) {
    const key=graphKey(ref.identity_space,ref.id);
    const node=index.identity.get(key);
    if (node) resolved.push(node);
    else unresolved.push({...ref,reason:'root_not_found'});
  }
  return {resolved,unresolved};
}

function traverse(request,index,resolvedRoots,deadlineAt) {
  const direction=request.mode==='neighborhood' ? (request.traversal?.direction??'both') : (request.traversal?.direction??'both');
  const maxDepth=request.mode==='identity_lookup'?0:(request.mode==='neighborhood'?1:(request.traversal?.max_depth??2));
  const maxNodes=Math.min(request.traversal?.max_nodes??request.budget.max_items,request.budget.max_items);
  const maxEdges=Math.min(request.traversal?.max_edges??request.budget.max_items,request.budget.max_items);
  const seen=new Set(); const nodes=[]; const edges=[]; const edgeSeen=new Set(); const queue=resolvedRoots.map((x)=>[x,0]);
  const reasons=[];
  while(queue.length){
    if(Date.now()>deadlineAt){reasons.push('deadline_ms');break;}
    const [node,depth]=queue.shift(); const key=graphKey(node.identity_space,node.id);
    if(seen.has(key))continue;
    if(nodes.length>=maxNodes){reasons.push('max_nodes');break;}
    seen.add(key); nodes.push(normalizedNode(node));
    if(depth>=maxDepth)continue;
    const candidates=[];
    if(direction==='out'||direction==='both') for(const edge of index.outgoing.get(key)??[]) candidates.push({edge,next:endpointId(edge.to),space:endpointSpace(edge.to)});
    if(direction==='in'||direction==='both') for(const edge of index.incoming.get(key)??[]) candidates.push({edge,next:endpointId(edge.from),space:endpointSpace(edge.from)});
    candidates.sort((a,b)=>stableItemKey(a.edge).localeCompare(stableItemKey(b.edge)));
    for(const c of candidates){
      if(!edgePasses(c.edge,request))continue;
      if(edges.length>=maxEdges){reasons.push('max_edges');queue.length=0;break;}
      const eid=c.edge.edge_id??canonicalize(c.edge);
      if(!edgeSeen.has(eid)){edgeSeen.add(eid);edges.push(c.edge);}
      if(c.next){const n=index.identity.get(graphKey(c.space,c.next));if(n&&!seen.has(graphKey(c.space,c.next)))queue.push([n,depth+1]);}
    }
  }
  return {nodes,edges,reasons:[...new Set(reasons)]};
}

export function executeQuery(request,dataset,{index=createQueryIndex(dataset)}={}) {
  const verified=verifyQueryRequest(request);
  if(!verified.ok) return errorResult(request,dataset,verified.issues.map(x=>`${x.path}: ${x.message}`),'invalid_request');
  if(!SUPPORTED_QUERY_MODES.has(request.mode)) return errorResult(request,dataset,[`query mode ${request.mode} is valid in KQP but not implemented by this reference engine`],'unsupported_mode');
  const discovery=request.discovery?.mode??'exact';
  if(discovery!=='exact') return errorResult(request,dataset,[`reference engine requires exact discovery; ${discovery} is a discovery-stage capability, not an exact semantic answer`],'unsupported_discovery');
  const deadlineAt=Date.now()+request.budget.deadline_ms;
  let rootState=resolveRoots(request,index);
  const full={nodes:[],edges:[],assertions:[],evidence:[]};
  let reasons=[];

  if(request.mode==='unknowns') {
    // Unknowns query returns resolved root cards plus explicit unresolved roots; it does not invent missing identities.
    full.nodes=rootState.resolved.map(normalizedNode);
  } else if(request.mode==='evidence_closure') {
    full.nodes=rootState.resolved.map(normalizedNode);
    const assertions=[];
    for(const root of rootState.resolved){for(const a of index.assertionsByEntity.get(graphKey(root.identity_space,root.id))??[]) if(assertionPasses(a,request)) assertions.push(a.record??a);}
    full.assertions=assertions;
    full.evidence=gatherDirectEvidence(assertions,index);
  } else {
    const traversed=traverse(request,index,rootState.resolved,deadlineAt);
    full.nodes=traversed.nodes;full.edges=traversed.edges;reasons.push(...traversed.reasons);
    const assertions=[]; const aSeen=new Set();
    for(const node of full.nodes){
      const key=graphKey(node.identity_space,node.id);
      for(const a of index.assertionsByEntity.get(key)??[]){
        if(!assertionPasses(a,request))continue;
        const id=a.id??a.record?.assertion_id??stableItemKey(a.record??a);
        if(!aSeen.has(id)){aSeen.add(id);assertions.push(a.record??a);}
      }
    }
    full.assertions=assertions;
    if(request.evidence?.include) full.evidence=gatherDirectEvidence(assertions,index);
  }

  let paged;
  try { paged=pageResult(full,request,dataset.source_fingerprints??[]); }
  catch(error){return errorResult(request,dataset,[error.message],'cursor_or_budget_error');}
  if(paged.hasMore) reasons.push('pagination_or_budget');
  if(rootState.unresolved.length) reasons.push('unresolved_roots');
  reasons=[...new Set(reasons)].sort();
  const partial=reasons.length>0;
  const evidenceRequested=!!request.evidence?.include || request.mode==='evidence_closure';
  const plan={
    discovery:'exact',strategy:'identity_graph',...(request.intent?{intent:request.intent}:{}),
    traversal_direction:['identity_lookup','evidence_closure','unknowns'].includes(request.mode)?'none':(request.traversal?.direction??'both'),
    max_depth:request.mode==='identity_lookup'?0:(request.mode==='neighborhood'?1:(request.traversal?.max_depth??2)),
    max_nodes:request.traversal?.max_nodes??request.budget.max_items,max_edges:request.traversal?.max_edges??request.budget.max_items,
    properties:[...(request.traversal?.properties??[])],indexes_used:['identity_lookup','incoming_edges','outgoing_edges','assertions_by_entity'],shards_contacted:[],
  };
  const omissions=[];
  if(paged.hasMore) omissions.push({kind:'pagination_or_budget',remaining_items:paged.total-(paged.offset+flattenResult(paged.result).length)});
  let out = {
    schema_version:'8.0',artifact_type:'kristall_query_result',protocol:'kristal-query/1.0',query_id:request.query_id,mode:request.mode,status:partial?'partial':'complete',
    source_fingerprints:dataset.source_fingerprints??[],resolved_roots:rootState.resolved.map(nodeRef),resolution_candidates:[],result:paged.result,
    completeness:{semantic_closure:partial?'partial':'complete',evidence_closure:evidenceRequested?(partial?'partial':'complete'):'not_requested',source_coverage:'complete',truncated:paged.hasMore||reasons.some(x=>['max_nodes','max_edges','deadline_ms'].includes(x)),reasons},
    continuation:paged.continuation,unresolved:rootState.unresolved,conflicts:[],omissions,query_plan:plan,
  };

  // Enforce max_bytes against the actual complete wire result, not only item payloads.
  let emitted=flattenResult(out.result);
  while(encodedBytes(out)>request.budget.max_bytes && emitted.length){
    emitted.pop();
    out.result=inflateResult(emitted);
    const nextOffset=paged.offset+emitted.length;
    const hasMore=nextOffset<paged.total;
    out.status='partial';
    out.completeness.semantic_closure='partial';
    if(evidenceRequested)out.completeness.evidence_closure='partial';
    out.completeness.truncated=true;
    out.completeness.reasons=[...new Set([...(out.completeness.reasons??[]),'max_bytes'])].sort();
    out.continuation={has_more:hasMore,ordering_profile:STABLE_ORDERING_PROFILE};
    if(hasMore){const binding=continuationBinding(request,dataset.source_fingerprints??[]);out.continuation.cursor=encodeCursor({v:1,...binding,o:nextOffset});}
    out.omissions=[{kind:'pagination_or_budget',remaining_items:Math.max(0,paged.total-nextOffset),reason:'max_bytes'}];
  }
  if(encodedBytes(out)>request.budget.max_bytes){
    return errorResult(request,dataset,[`max_bytes ${request.budget.max_bytes} is too small for mandatory KQP result metadata`],'wire_budget_too_small');
  }
  return out;
}

function errorResult(request,dataset,messages,reason) {
  return {
    schema_version:'8.0',artifact_type:'kristall_query_result',protocol:'kristal-query/1.0',query_id:request?.query_id??'invalid-query',mode:ALL_QUERY_MODES.has(request?.mode)?request.mode:'semantic_slice',status:'error',
    source_fingerprints:dataset?.source_fingerprints??[],resolved_roots:[],resolution_candidates:[],result:{nodes:[],edges:[],assertions:[],evidence:[]},
    completeness:{semantic_closure:'unknown',evidence_closure:'unknown',source_coverage:'unknown',truncated:false,reasons:[reason]},continuation:{has_more:false,ordering_profile:STABLE_ORDERING_PROFILE},
    unresolved:[],conflicts:[],omissions:[{kind:reason,messages}],query_plan:{discovery:request?.discovery?.mode??'exact',strategy:'rejected'},
  };
}
