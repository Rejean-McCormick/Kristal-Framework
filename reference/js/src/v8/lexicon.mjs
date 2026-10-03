import { isObject, normalizeLocale, localeMatches, semanticRefKey } from './common.mjs';

const IDENTITY_SPACES = new Set(['kristall','kristal_v6','external']);
const LEXICAL_STATUSES = new Set(['resolved','missing','deprecated','conflicted']);

function issue(issues, path, message) { issues.push({ path, message }); }

export function verifySemanticRef(ref, path = '$') {
  const issues = [];
  if (!isObject(ref)) { issue(issues, path, 'semantic_ref must be object'); return issues; }
  if (!IDENTITY_SPACES.has(ref.identity_space)) issue(issues, `${path}.identity_space`, 'unsupported identity space');
  if (typeof ref.id !== 'string' || !ref.id) issue(issues, `${path}.id`, 'id is required');
  if (ref.namespace !== undefined && (typeof ref.namespace !== 'string' || !ref.namespace)) issue(issues, `${path}.namespace`, 'namespace must be non-empty string');
  return issues;
}

export function verifyLexicon(doc) {
  const issues = [];
  if (!isObject(doc)) return { ok:false, issues:[{path:'$',message:'lexicon must be object'}] };
  if (doc.schema_version !== '8.0') issue(issues,'$.schema_version','expected 8.0');
  if (doc.artifact_type !== 'kristall_lexicon') issue(issues,'$.artifact_type','expected kristall_lexicon');
  if (typeof doc.lexicon_id !== 'string' || !doc.lexicon_id) issue(issues,'$.lexicon_id','lexicon_id required');
  try { normalizeLocale(doc.language); } catch (e) { issue(issues,'$.language',e.message); }
  if (!isObject(doc.scope) || typeof doc.scope.kind !== 'string') issue(issues,'$.scope','scope.kind required');
  if (!Array.isArray(doc.entries)) issue(issues,'$.entries','entries must be array');
  const seen = new Map();
  for (const [i, entry] of (doc.entries ?? []).entries()) {
    const p = `$.entries[${i}]`;
    if (!isObject(entry)) { issue(issues,p,'entry must be object'); continue; }
    issues.push(...verifySemanticRef(entry.semantic_ref, `${p}.semantic_ref`));
    if (!LEXICAL_STATUSES.has(entry.lexical_status)) issue(issues,`${p}.lexical_status`,'unsupported lexical status');
    if (entry.lexical_status === 'resolved' && (typeof entry.preferred_term !== 'string' || !entry.preferred_term)) issue(issues,`${p}.preferred_term`,'resolved entry requires preferred_term');
    const key = semanticRefKey(entry.semantic_ref);
    if (key) {
      if (seen.has(key)) issue(issues,p,`duplicate semantic_ref also present at ${seen.get(key)}`);
      else seen.set(key,p);
    }
  }
  return { ok:issues.length===0, issues, normalized_language: issues.some(x=>x.path==='$.language') ? null : normalizeLocale(doc.language) };
}

export function verifyLexiconStack(doc) {
  const issues = [];
  if (!isObject(doc)) return { ok:false, issues:[{path:'$',message:'stack must be object'}] };
  if (doc.schema_version !== '8.0') issue(issues,'$.schema_version','expected 8.0');
  if (doc.artifact_type !== 'kristall_lexicon_stack') issue(issues,'$.artifact_type','expected kristall_lexicon_stack');
  if (typeof doc.stack_id !== 'string' || !doc.stack_id) issue(issues,'$.stack_id','stack_id required');
  try { normalizeLocale(doc.requested_locale); } catch(e) { issue(issues,'$.requested_locale',e.message); }
  const policy = doc.resolution_policy;
  if (!isObject(policy)) issue(issues,'$.resolution_policy','resolution_policy required');
  else {
    if (policy.precedence !== 'highest_numeric_wins') issue(issues,'$.resolution_policy.precedence','expected highest_numeric_wins');
    if (!['preserve_semantic_id','error'].includes(policy.on_missing)) issue(issues,'$.resolution_policy.on_missing','unsupported missing policy');
    if (!['return_conflict','error'].includes(policy.on_conflict)) issue(issues,'$.resolution_policy.on_conflict','unsupported conflict policy');
    for (const [i, locale] of (policy.locale_fallback ?? []).entries()) {
      try { normalizeLocale(locale); } catch(e) { issue(issues,`$.resolution_policy.locale_fallback[${i}]`,e.message); }
    }
  }
  if (!Array.isArray(doc.layers) || doc.layers.length===0) issue(issues,'$.layers','at least one layer required');
  if (Array.isArray(doc.layers) && doc.layers.length>64) issue(issues,'$.layers','reference runtime supports at most 64 layers');
  const refs = new Set();
  for (const [i, layer] of (doc.layers ?? []).entries()) {
    const p=`$.layers[${i}]`;
    if (!isObject(layer) || typeof layer.lexicon_ref !== 'string' || !layer.lexicon_ref) issue(issues,p,'layer lexicon_ref required');
    else if (refs.has(layer.lexicon_ref)) issue(issues,p,'duplicate lexicon_ref');
    else refs.add(layer.lexicon_ref);
    if (!Number.isInteger(layer?.precedence)) issue(issues,`${p}.precedence`,'integer precedence required');
  }
  return { ok:issues.length===0, issues };
}

export function lexiconMap(lexicons) {
  const map = new Map();
  for (const doc of lexicons ?? []) {
    const verified = verifyLexicon(doc);
    if (!verified.ok) throw new Error(`invalid lexicon ${doc?.lexicon_id ?? '<unknown>'}: ${verified.issues.map(x=>`${x.path} ${x.message}`).join('; ')}`);
    if (map.has(doc.lexicon_id)) throw new Error(`duplicate lexicon_id: ${doc.lexicon_id}`);
    map.set(doc.lexicon_id, doc);
  }
  return map;
}

export function resolveLexicalization(ref, stack, lexicons, { requestedLocale } = {}) {
  const stackCheck = verifyLexiconStack(stack);
  if (!stackCheck.ok) throw new Error(`invalid lexicon stack: ${stackCheck.issues.map(x=>`${x.path} ${x.message}`).join('; ')}`);
  const refIssues = verifySemanticRef(ref);
  if (refIssues.length) throw new Error(`invalid semantic reference: ${refIssues.map(x=>x.message).join('; ')}`);
  const map = lexicons instanceof Map ? lexicons : lexiconMap(lexicons);
  const locale = normalizeLocale(requestedLocale ?? stack.requested_locale);
  const fallbacks = stack.resolution_policy.locale_fallback ?? [];
  const key = semanticRefKey(ref);
  const candidates = [];
  const unavailableLayers = [];

  for (const layer of stack.layers) {
    const lexicon = map.get(layer.lexicon_ref);
    if (!lexicon) {
      if (!layer.optional) unavailableLayers.push(layer.lexicon_ref);
      continue;
    }
    if (!localeMatches(lexicon.language, locale, fallbacks)) continue;
    const entry = lexicon.entries.find((x) => semanticRefKey(x.semantic_ref) === key);
    if (!entry || entry.lexical_status !== 'resolved') continue;
    candidates.push({
      precedence: layer.precedence,
      lexicon_id: lexicon.lexicon_id,
      language: normalizeLocale(lexicon.language),
      preferred_term: entry.preferred_term,
      entry,
    });
  }

  if (unavailableLayers.length) {
    return { semantic_ref:ref, lexical_status:'unavailable', locale, missing_layers:unavailableLayers, render:ref.id };
  }
  if (!candidates.length) {
    if (stack.resolution_policy.on_missing === 'error') throw new Error(`missing lexicalization for ${ref.id}`);
    return { semantic_ref:ref, lexical_status:'missing', locale, render:ref.id };
  }
  const highest = Math.max(...candidates.map((x)=>x.precedence));
  const top = candidates.filter((x)=>x.precedence===highest).sort((a,b)=>a.lexicon_id.localeCompare(b.lexicon_id));
  const terms = [...new Set(top.map((x)=>x.preferred_term))];
  if (terms.length > 1) {
    if (stack.resolution_policy.on_conflict === 'error') throw new Error(`conflicting lexicalizations for ${ref.id}: ${terms.join(', ')}`);
    return { semantic_ref:ref, lexical_status:'conflicted', locale, precedence:highest, candidates:top, render:ref.id };
  }
  const winner = top[0];
  return {
    semantic_ref:ref,
    lexical_status:'resolved',
    locale,
    term:winner.preferred_term,
    render:winner.preferred_term,
    lexicon:winner.lexicon_id,
    precedence:highest,
    entry:winner.entry,
  };
}

export function resolveMany(refs, stack, lexicons, options = {}) {
  const resolved = [];
  const missing = [];
  const conflicts = [];
  for (const ref of refs) {
    const result = resolveLexicalization(ref, stack, lexicons, options);
    resolved.push(result);
    if (result.lexical_status === 'missing' || result.lexical_status === 'unavailable') missing.push(ref.id);
    if (result.lexical_status === 'conflicted') conflicts.push(ref.id);
  }
  return { resolved, missing, conflicts };
}
