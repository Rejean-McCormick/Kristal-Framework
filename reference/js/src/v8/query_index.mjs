import { classifyIdentity, stableItemKey, sha256IdOfJson } from './common.mjs';

function endpointId(value) {
  if (value && typeof value === 'object') return value.id;
  return typeof value === 'string' ? value : null;
}

function endpointSpace(id) {
  return classifyIdentity(id);
}

function graphKey(space,id) { return `${space}\u0000${id}`; }

export function createQueryIndex(dataset) {
  const identity = new Map();
  const outgoing = new Map();
  const incoming = new Map();
  const predicateUsage = new Map();
  const assertionsByEntity = new Map();
  const evidenceByAssertion = new Map();

  function addIdentity(space,id,kind,record,meta={}) {
    if (!id) return;
    const key=graphKey(space,id);
    if (!identity.has(key)) identity.set(key,{id,identity_space:space,kind,record,...meta});
  }
  function addAdj(map,key,edge) {
    if (!map.has(key)) map.set(key,[]);
    map.get(key).push(edge);
  }

  for (const x of dataset.entities ?? []) addIdentity('kristall',x.entity_id,'entity',x);
  for (const x of dataset.properties ?? []) addIdentity('kristall',x.property_id,'property',x);
  for (const x of dataset.assertions ?? []) addIdentity('kristall',x.assertion_id,'assertion',x);
  for (const x of dataset.sources ?? []) addIdentity('kristall',x.source_id,'source',x);

  for (const edge of dataset.edges ?? []) {
    const from=endpointId(edge.from), to=endpointId(edge.to);
    const fs=endpointSpace(from), ts=endpointSpace(to);
    if (from) addIdentity(fs,from,fs==='kristall'?'entity':'external_or_source_local',null);
    if (to) addIdentity(ts,to,ts==='kristall'?'entity':'external_or_source_local',null);
    if (from) addAdj(outgoing,graphKey(fs,from),edge);
    if (to) addAdj(incoming,graphKey(ts,to),edge);
    if (edge.relation) addAdj(predicateUsage,edge.relation,edge);
  }

  for (const {ref,doc} of dataset.v6_states ?? []) {
    for (const [i,a] of (doc.assertions ?? []).entries()) {
      const s=a.statement?.subject, o=a.statement?.object, p=a.statement?.predicate;
      const sid=s?.id, oid=o?.id;
      if (sid) addIdentity('kristal_v6',sid,s?.kind ?? 'referent',s,{source_ref:ref});
      if (oid) addIdentity('kristal_v6',oid,o?.kind ?? 'referent',o,{source_ref:ref});
      if (p) addIdentity('kristal_v6',p,'property',{id:p},{source_ref:ref});
      const aid=`${ref}#assertion:${i}`;
      addIdentity('kristal_v6',aid,'assertion',a,{source_ref:ref});
      if (sid) {
        const edge={edge_id:`v6:${sha256IdOfJson({ref,i,sid,p,oid:o?.id ?? o?.value})}`,'from':{kind:s?.kind ?? 'referent',id:sid},relation:p,'to':o,edge_semantics:'v6_statement',status:a.assertion_status ?? 'unknown',source_ref:ref,assertion_ref:aid};
        addAdj(outgoing,graphKey('kristal_v6',sid),edge);
        if (oid) addAdj(incoming,graphKey('kristal_v6',oid),edge);
        if (p) addAdj(predicateUsage,p,edge);
        assertionsByEntity.set(graphKey('kristal_v6',sid),[...(assertionsByEntity.get(graphKey('kristal_v6',sid)) ?? []),{id:aid,record:a,source_ref:ref}]);
        if (oid) assertionsByEntity.set(graphKey('kristal_v6',oid),[...(assertionsByEntity.get(graphKey('kristal_v6',oid)) ?? []),{id:aid,record:a,source_ref:ref}]);
        if (Array.isArray(a.evidence_refs)) evidenceByAssertion.set(aid,a.evidence_refs.map((x)=>({source_ref:x})));
      }
    }
  }

  // v7 source binding offers a deterministic direct association even when the underlying source assertion lives outside v7.
  for (const a of dataset.assertions ?? []) {
    const local=a.source_binding?.source_kristal_id;
    if (!local) continue;
    const key=graphKey(classifyIdentity(local),local);
    assertionsByEntity.set(key,[...(assertionsByEntity.get(key) ?? []),{id:a.assertion_id,record:a}]);
  }

  for (const map of [outgoing,incoming,predicateUsage,assertionsByEntity,evidenceByAssertion]) {
    for (const [key,values] of map.entries()) map.set(key,[...values].sort((a,b)=>stableItemKey(a).localeCompare(stableItemKey(b))));
  }
  return { identity,outgoing,incoming,predicateUsage,assertionsByEntity,evidenceByAssertion };
}

export function exportQueryIndex(index, dataset, { indexId='KQI-reference' }={}) {
  const toObj=(map)=>Object.fromEntries([...map.entries()].sort(([a],[b])=>a.localeCompare(b)));
  const payloads={
    'identity.json':toObj(index.identity),
    'outgoing.json':toObj(index.outgoing),
    'incoming.json':toObj(index.incoming),
    'predicate-usage.json':toObj(index.predicateUsage),
    'assertions-by-entity.json':toObj(index.assertionsByEntity),
    'evidence-by-assertion.json':toObj(index.evidenceByAssertion),
  };
  const kinds={
    'identity.json':'identity_lookup','outgoing.json':'outgoing_edges','incoming.json':'incoming_edges',
    'predicate-usage.json':'predicate_usage','assertions-by-entity.json':'assertions_by_entity','evidence-by-assertion.json':'evidence_by_assertion',
  };
  const manifest={
    schema_version:'8.0',artifact_type:'kristall_query_index',index_id:indexId,authoritative:false,rebuildable:true,
    built_from:dataset.source_fingerprints,
    indexes:Object.entries(payloads).map(([location,payload])=>({kind:kinds[location],location,content_hash:sha256IdOfJson(payload),profile:`kristal.query-index/${kinds[location]}/v1`})),
  };
  return {manifest,payloads};
}
