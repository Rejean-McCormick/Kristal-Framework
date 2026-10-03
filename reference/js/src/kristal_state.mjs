import { cloneJson, canonicalize } from './jcs.mjs';
import { sha256Hex, sha256Id } from './hash.mjs';

export const KRISTAL_STANDARD_VERSION = '6.0.0';
export const KRISTAL_CANONICALIZATION_PROFILE = 'kristal.v6:jcs-rfc8785';

export const VALUE_SEMANTICS = new Set([
  'boolean','categorical','set','ordinal','scalar','interval','probability',
  'distribution','vector','partial_order','state','temporal'
]);

export const VALUE_STATES = new Set([
  'known','unknown','not_applicable','indeterminate','not_measured'
]);

export const RECORD_ROLES = new Set([
  'authoritative_constraint','observed_state','organizational_rule',
  'reference_knowledge','derived_state','decision','action','structural_record'
]);

export const ACTIONABILITY_MODES = new Set([
  'automatic','human_review','human_decision','manual','prohibited',
  'insufficient_information','not_applicable'
]);

export function stateHashTarget(state) {
  const out = cloneJson(state);
  delete out.state_id;
  delete out.content_hash;
  delete out.signatures;
  return out;
}

export function stateIdentity(state) {
  const target = stateHashTarget(state);
  const canonical = canonicalize(target);
  const digest = sha256Hex(Buffer.from(canonical, 'utf8'));
  return {
    canonicalization_profile: KRISTAL_CANONICALIZATION_PROFILE,
    canonical,
    sha256_hex: digest,
    state_id: `sha256:${digest}`,
    content_hash: { alg: 'sha256', value: digest },
  };
}

function issue(issues, path, message) {
  issues.push({ path, message });
}

function validateKnownValue(v, path, issues) {
  const sem = v.value_semantics;
  const value = v.value;
  if (!('value' in v)) {
    issue(issues, path + '.value', 'known valuation requires value');
    return;
  }
  if (sem === 'boolean' && typeof value !== 'boolean') issue(issues, path + '.value', 'boolean valuation requires boolean');
  if (sem === 'categorical' && !['string','number','boolean'].includes(typeof value)) issue(issues, path + '.value', 'categorical valuation requires scalar category');
  if (sem === 'set' && !Array.isArray(value)) issue(issues, path + '.value', 'set valuation requires array');
  if (sem === 'scalar' && typeof value !== 'number') issue(issues, path + '.value', 'scalar valuation requires number');
  if (sem === 'probability' && (typeof value !== 'number' || value < 0 || value > 1)) issue(issues, path + '.value', 'probability must be between 0 and 1');
  if (sem === 'distribution' && !(Array.isArray(value) || (value && typeof value === 'object'))) issue(issues, path + '.value', 'distribution requires array/object');
  if (sem === 'vector' && !(Array.isArray(value) || (value && typeof value === 'object'))) issue(issues, path + '.value', 'vector requires array/object');
  if (sem === 'state' && typeof value !== 'string') issue(issues, path + '.value', 'state valuation requires string state');
  if (sem === 'temporal' && !(typeof value === 'string' || (value && typeof value === 'object'))) issue(issues, path + '.value', 'temporal valuation requires string/object');
  if (sem === 'interval') {
    const ok = (Array.isArray(value) && value.length === 2) || (value && typeof value === 'object');
    if (!ok) issue(issues, path + '.value', 'interval valuation requires pair/object');
  }
}

export function validateValuation(v, path='valuation') {
  const issues = [];
  if (!v || typeof v !== 'object' || Array.isArray(v)) {
    issue(issues, path, 'valuation must be object');
    return issues;
  }
  if (typeof v.dimension !== 'string' || !v.dimension.trim()) issue(issues, path + '.dimension', 'dimension is required');
  if (!VALUE_SEMANTICS.has(v.value_semantics)) issue(issues, path + '.value_semantics', 'unsupported value semantics');
  if (!VALUE_STATES.has(v.value_state)) issue(issues, path + '.value_state', 'unsupported value state');
  if (v.value_state === 'known' && VALUE_SEMANTICS.has(v.value_semantics)) validateKnownValue(v, path, issues);
  if (v.value_state && v.value_state !== 'known' && 'value' in v) issue(issues, path + '.value', 'non-known value state must not masquerade as a value');
  return issues;
}

export function verifyKristalState(state, { requireIdentity=false }={}) {
  const issues = [];
  if (!state || typeof state !== 'object' || Array.isArray(state)) {
    return { ok:false, issues:[{path:'$',message:'state must be object'}] };
  }
  if (state.schema_version !== '6.0') issue(issues, '$.schema_version', 'expected 6.0');
  if (state.artifact_type !== 'kristal_state') issue(issues, '$.artifact_type', 'expected kristal_state');
  if (!Array.isArray(state.assertions)) issue(issues, '$.assertions', 'assertions must be array');
  if (state.applicability !== undefined && (!state.applicability || typeof state.applicability !== 'object' || Array.isArray(state.applicability))) issue(issues, '$.applicability', 'applicability must be object');

  for (const [i,a] of (Array.isArray(state.assertions) ? state.assertions : []).entries()) {
    const p = `$.assertions[${i}]`;
    if (!a || typeof a !== 'object' || Array.isArray(a)) { issue(issues,p,'assertion must be object'); continue; }
    if (!a.statement || typeof a.statement !== 'object') issue(issues,p+'.statement','statement is required');
    if (a.record_role !== undefined && !RECORD_ROLES.has(a.record_role)) issue(issues,p+'.record_role','unsupported record role');
    if (a.coordinates !== undefined && !(Array.isArray(a.coordinates) || (a.coordinates && typeof a.coordinates === 'object'))) issue(issues,p+'.coordinates','coordinates must be array/object');
    if (a.applicability !== undefined && (!a.applicability || typeof a.applicability !== 'object' || Array.isArray(a.applicability))) issue(issues,p+'.applicability','applicability must be object');
    for (const [j,v] of (Array.isArray(a.valuations) ? a.valuations : []).entries()) issues.push(...validateValuation(v, `${p}.valuations[${j}]`));
    if (a.valuations !== undefined && !Array.isArray(a.valuations)) issue(issues,p+'.valuations','valuations must be array');
    if (a.actionability !== undefined) {
      if (!a.actionability || typeof a.actionability !== 'object' || Array.isArray(a.actionability)) issue(issues,p+'.actionability','actionability must be object');
      else if (!ACTIONABILITY_MODES.has(a.actionability.mode)) issue(issues,p+'.actionability.mode','unsupported actionability mode');
    }
  }

  const id = stateIdentity(state);
  if (state.state_id !== undefined && state.state_id !== id.state_id) issue(issues,'$.state_id','declared state_id does not match canonical content');
  if (state.content_hash !== undefined) {
    const ch=state.content_hash;
    if (!ch || ch.alg !== 'sha256' || ch.value !== id.sha256_hex) issue(issues,'$.content_hash','declared content_hash does not match canonical content');
  }
  if (requireIdentity && state.state_id === undefined) issue(issues,'$.state_id','state_id required');
  if (requireIdentity && state.content_hash === undefined) issue(issues,'$.content_hash','content_hash required');
  return { ok: issues.length === 0, issues, identity: id };
}

export function summarizeKristalState(state) {
  const roleCounts = {};
  const actionabilityCounts = {};
  const valuationSemantics = {};
  const valuationDimensions = {};
  for (const a of state.assertions ?? []) {
    if (a.record_role) roleCounts[a.record_role]=(roleCounts[a.record_role]??0)+1;
    if (a.actionability?.mode) actionabilityCounts[a.actionability.mode]=(actionabilityCounts[a.actionability.mode]??0)+1;
    for (const v of a.valuations ?? []) {
      valuationSemantics[v.value_semantics]=(valuationSemantics[v.value_semantics]??0)+1;
      valuationDimensions[v.dimension]=(valuationDimensions[v.dimension]??0)+1;
    }
  }
  return {
    schema_version: state.schema_version,
    artifact_type: state.artifact_type,
    assertion_count: Array.isArray(state.assertions) ? state.assertions.length : 0,
    record_roles: roleCounts,
    actionability_modes: actionabilityCounts,
    valuation_semantics: valuationSemantics,
    valuation_dimensions: valuationDimensions,
  };
}
