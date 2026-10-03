import { verifyKristalState } from '../kristal_state.mjs';
import { isObject, V7_ARTIFACT_TYPES, V8_ARTIFACT_TYPES, byteFingerprintFromJson } from './common.mjs';
import { verifyLexicon, verifyLexiconStack } from './lexicon.mjs';

const V7_ARRAY_REQUIREMENTS = new Map([
  ['kristall_entity_registry','entities'],
  ['kristall_property_registry','properties'],
  ['kristall_assertion_registry','assertions'],
  ['kristall_source_registry','sources'],
  ['kristall_mesh','edges'],
  ['kristall_kos_registry','systems'],
  ['kristall_axis_registry','axes'],
  ['kristall_axis_type_registry','axis_types'],
  ['kristall_assertion_family_registry','families'],
  ['kristall_toc_registry','entries'],
]);

function basicV7Verify(doc) {
  const issues=[];
  if (!isObject(doc)) return {ok:false,issues:[{path:'$',message:'artifact must be object'}]};
  if (doc.schema_version !== '7.0') issues.push({path:'$.schema_version',message:'expected 7.0'});
  if (!V7_ARTIFACT_TYPES.has(doc.artifact_type)) issues.push({path:'$.artifact_type',message:'unrecognized v7 artifact type'});
  const requiredArray = V7_ARRAY_REQUIREMENTS.get(doc.artifact_type);
  if (requiredArray && !Array.isArray(doc[requiredArray])) issues.push({path:`$.${requiredArray}`,message:'expected array'});
  return {ok:issues.length===0,issues};
}

function basicV8Verify(doc) {
  if (doc?.artifact_type === 'kristall_lexicon') return verifyLexicon(doc);
  if (doc?.artifact_type === 'kristall_lexicon_stack') return verifyLexiconStack(doc);
  const issues=[];
  if (!isObject(doc)) return {ok:false,issues:[{path:'$',message:'artifact must be object'}]};
  if (doc.schema_version !== '8.0') issues.push({path:'$.schema_version',message:'expected 8.0'});
  if (!V8_ARTIFACT_TYPES.has(doc.artifact_type)) issues.push({path:'$.artifact_type',message:'unrecognized v8 artifact type'});
  return {ok:issues.length===0,issues};
}

export function inspectArtifact(doc) {
  if (doc?.schema_version === '6.0' && doc?.artifact_type === 'kristal_state') {
    const verification = verifyKristalState(doc);
    return { ok:verification.ok, family:'v6', schema_version:'6.0', artifact_type:'kristal_state', issues:verification.issues };
  }
  if (doc?.schema_version === '7.0') {
    const verification=basicV7Verify(doc);
    return { ok:verification.ok, family:'v7', schema_version:'7.0', artifact_type:doc?.artifact_type, issues:verification.issues };
  }
  if (doc?.schema_version === '8.0') {
    const verification=basicV8Verify(doc);
    return { ok:verification.ok, family:'v8', schema_version:'8.0', artifact_type:doc?.artifact_type, issues:verification.issues };
  }
  return { ok:false, family:'unknown', schema_version:doc?.schema_version, artifact_type:doc?.artifact_type, issues:[{path:'$',message:'unsupported Kristal artifact'}] };
}

export function buildDataset(artifacts) {
  const dataset = {
    entities:[], properties:[], assertions:[], sources:[], edges:[],
    v6_states:[], lexicons:[], lexicon_stacks:[], query_indexes:[], capabilities:[],
    artifacts:[], source_fingerprints:[],
  };
  for (const item of artifacts ?? []) {
    const doc = item?.doc ?? item;
    const ref = item?.ref ?? `memory:${dataset.artifacts.length}`;
    const inspection=inspectArtifact(doc);
    if (!inspection.ok) throw new Error(`invalid/unsupported artifact ${ref}: ${inspection.issues.map(x=>`${x.path} ${x.message}`).join('; ')}`);
    const fingerprint=item?.fingerprint ?? byteFingerprintFromJson(doc,ref);
    dataset.artifacts.push({ref,doc,family:inspection.family,artifact_type:doc.artifact_type,fingerprint});
    dataset.source_fingerprints.push(fingerprint);
    switch (doc.artifact_type) {
      case 'kristal_state': dataset.v6_states.push({ref,doc}); break;
      case 'kristall_entity_registry': dataset.entities.push(...(doc.entities ?? [])); break;
      case 'kristall_property_registry': dataset.properties.push(...(doc.properties ?? [])); break;
      case 'kristall_assertion_registry': dataset.assertions.push(...(doc.assertions ?? [])); break;
      case 'kristall_source_registry': dataset.sources.push(...(doc.sources ?? [])); break;
      case 'kristall_mesh': dataset.edges.push(...(doc.edges ?? [])); break;
      case 'kristall_lexicon': dataset.lexicons.push(doc); break;
      case 'kristall_lexicon_stack': dataset.lexicon_stacks.push(doc); break;
      case 'kristall_query_index': dataset.query_indexes.push(doc); break;
      case 'kristall_v8_capabilities': dataset.capabilities.push(doc); break;
      default: break;
    }
  }
  return dataset;
}
