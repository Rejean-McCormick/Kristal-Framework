import fs from 'node:fs';
import { canonicalize, cloneJson } from '../jcs.mjs';
import { sha256Hex } from '../hash.mjs';

export const V8_SCHEMA_VERSION = '8.0';
export const KQP_PROTOCOL = 'kristal-query/1.0';
export const LANGUAGE_PROTOCOL = 'kristal-language/1.0';
export const AI_COMPACT_PROFILE = 'kristal-ai-compact/1.0';
export const SEMANTIC_FINGERPRINT_PROFILE = 'kristal.reference:semantic-fingerprint/v1';
export const STABLE_ORDERING_PROFILE = 'kristal.query/stable-id-v1';

export const V8_ARTIFACT_TYPES = new Set([
  'kristall_lexicon',
  'kristall_lexicon_stack',
  'kristall_query_index',
  'kristall_query_request',
  'kristall_query_result',
  'kristall_ai_context_bundle',
  'kristall_v8_capabilities',
]);

export const V7_ARTIFACT_TYPES = new Set([
  'kristall_entity_registry',
  'kristall_property_registry',
  'kristall_assertion_registry',
  'kristall_source_registry',
  'kristall_mesh',
  'kristall_manifest',
  'kristall_kos_registry',
  'kristall_axis_registry',
  'kristall_axis_type_registry',
  'kristall_assertion_family_registry',
  'kristall_projection_recipe',
  'kristall_toc_registry',
  'kristall_crystallization_record',
  'semantic_resonance',
]);

export function isObject(value) {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

export function encodedBytes(value) {
  return Buffer.byteLength(JSON.stringify(value), 'utf8');
}

export function canonicalBytes(value) {
  return Buffer.from(canonicalize(value), 'utf8');
}

export function sha256IdOfJson(value) {
  return `sha256:${sha256Hex(canonicalBytes(value))}`;
}

export function byteFingerprintFromFile(file, ref = file, schemaVersion) {
  const digest = sha256Hex(fs.readFileSync(file));
  const out = { ref, byte_sha256: `sha256:${digest}` };
  if (schemaVersion) out.schema_version = schemaVersion;
  return out;
}

export function byteFingerprintFromJson(doc, ref = 'memory:json') {
  const bytes = canonicalBytes(doc);
  const out = { ref, byte_sha256: `sha256:${sha256Hex(bytes)}` };
  if (typeof doc?.schema_version === 'string') out.schema_version = doc.schema_version;
  return out;
}

export function normalizeLocale(tag) {
  if (typeof tag !== 'string' || !tag.trim()) throw new Error('locale must be a non-empty BCP 47 tag');
  try {
    return new Intl.Locale(tag).toString();
  } catch {
    throw new Error(`invalid BCP 47 locale: ${tag}`);
  }
}

export function localeMatches(lexiconLanguage, requestedLocale, fallbacks = []) {
  const language = normalizeLocale(lexiconLanguage);
  const requested = normalizeLocale(requestedLocale);
  const accepted = new Set([requested, ...fallbacks.map(normalizeLocale)]);
  accepted.add(new Intl.Locale(requested).language);
  return accepted.has(language) || new Intl.Locale(language).language === new Intl.Locale(requested).language;
}

export function semanticRefKey(ref) {
  if (!isObject(ref) || typeof ref.identity_space !== 'string' || typeof ref.id !== 'string') return null;
  return `${ref.identity_space}\u0000${ref.namespace ?? ''}\u0000${ref.id}`;
}

export function classifyIdentity(id, hint = null) {
  if (hint) return hint;
  if (typeof id !== 'string') return 'external';
  if (/^(?:KQ|KP|KA|KS)[1-9][0-9]*$/.test(id)) return 'kristall';
  return 'external';
}

export function collectSemanticRefs(value) {
  const out = [];
  const seen = new Set();
  function add(identity_space, id, namespace) {
    const ref = { identity_space, id };
    if (namespace) ref.namespace = namespace;
    const key = semanticRefKey(ref);
    if (key && !seen.has(key)) { seen.add(key); out.push(ref); }
  }
  function walk(x) {
    if (Array.isArray(x)) { for (const item of x) walk(item); return; }
    if (isObject(x)) {
      if (typeof x.identity_space === 'string' && typeof x.id === 'string') add(x.identity_space, x.id, x.namespace);
      for (const v of Object.values(x)) walk(v);
      return;
    }
    if (typeof x === 'string' && /^(?:KQ|KP|KA|KS)[1-9][0-9]*$/.test(x)) add('kristall', x);
  }
  walk(value);
  return out;
}

const PRESENTATION_KEYS = new Set([
  'preferred_label', 'label', 'labels', 'description', 'definition', 'definition_gloss',
  'usage_notes', 'alternate_terms', 'part_of_speech', 'grammatical_features', 'title',
]);
const DERIVED_KEYS = new Set([
  'state_id', 'content_hash', 'signatures', 'attestations', 'semantic_fingerprint',
]);

function semanticProjectionInner(value, { stripPresentation = true } = {}) {
  if (Array.isArray(value)) return value.map((x) => semanticProjectionInner(x, { stripPresentation }));
  if (!isObject(value)) return value;
  const out = {};
  const artifactType = value.artifact_type;
  const lexical = artifactType === 'kristall_lexicon' || artifactType === 'kristall_lexicon_stack';
  for (const [key, child] of Object.entries(value)) {
    if (DERIVED_KEYS.has(key)) continue;
    if (stripPresentation && !lexical && PRESENTATION_KEYS.has(key)) continue;
    out[key] = semanticProjectionInner(child, { stripPresentation: stripPresentation && !lexical });
  }
  return out;
}

export function semanticProjection(value) {
  return semanticProjectionInner(cloneJson(value));
}

export function semanticFingerprint(value, { profile = SEMANTIC_FINGERPRINT_PROFILE } = {}) {
  if (profile !== SEMANTIC_FINGERPRINT_PROFILE) throw new Error(`unsupported semantic fingerprint profile: ${profile}`);
  const projection = semanticProjection(value);
  const domain = `KRISTAL\u0000SEMANTIC-FINGERPRINT\u0000${profile}\u0000${value?.artifact_type ?? 'unknown'}\u0000`;
  const digest = sha256Hex(Buffer.concat([Buffer.from(domain, 'utf8'), canonicalBytes(projection)]));
  return { profile, digest: `sha256:${digest}` };
}

export function stableItemKey(value) {
  if (isObject(value)) {
    for (const key of ['entity_id','property_id','assertion_id','source_id','edge_id','id','atom_id']) {
      if (typeof value[key] === 'string') return `${key}:${value[key]}`;
    }
  }
  return canonicalize(value);
}

export function encodeCursor(payload) {
  return Buffer.from(JSON.stringify(payload), 'utf8').toString('base64url');
}

export function decodeCursor(cursor) {
  try {
    const value = JSON.parse(Buffer.from(cursor, 'base64url').toString('utf8'));
    if (!isObject(value)) throw new Error('not an object');
    return value;
  } catch (error) {
    throw new Error(`invalid continuation cursor: ${error.message}`);
  }
}

export function normalizedQueryHash(request) {
  const q = cloneJson(request);
  if (q.pagination) delete q.pagination.cursor;
  return sha256IdOfJson(q);
}

export function sourceSetHash(fingerprints) {
  const normalized = [...(fingerprints ?? [])].map((x) => {
    const out = { ref: x.ref, byte_sha256: x.byte_sha256 };
    if (x.semantic_fingerprint !== undefined) out.semantic_fingerprint = x.semantic_fingerprint;
    if (x.schema_version !== undefined) out.schema_version = x.schema_version;
    return out;
  }).sort((a,b) => String(a.ref).localeCompare(String(b.ref)));
  return sha256IdOfJson(normalized);
}

export function deepReplaceSemanticIds(value, symbolById) {
  if (Array.isArray(value)) return value.map((x) => deepReplaceSemanticIds(x, symbolById));
  if (isObject(value)) {
    const out = {};
    for (const [k,v] of Object.entries(value)) out[k] = deepReplaceSemanticIds(v, symbolById);
    return out;
  }
  if (typeof value === 'string' && symbolById.has(value)) return { '$k': symbolById.get(value) };
  return value;
}

export function deepExpandSemanticIds(value, symbolTable) {
  if (Array.isArray(value)) return value.map((x) => deepExpandSemanticIds(x, symbolTable));
  if (isObject(value)) {
    if (Object.keys(value).length === 1 && Number.isInteger(value.$k)) {
      const id = symbolTable[String(value.$k)];
      if (typeof id !== 'string') throw new Error(`missing symbol-table entry ${value.$k}`);
      return id;
    }
    const out = {};
    for (const [k,v] of Object.entries(value)) out[k] = deepExpandSemanticIds(v, symbolTable);
    return out;
  }
  return value;
}
