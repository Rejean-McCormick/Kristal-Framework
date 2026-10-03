const TOP_KEYS = new Set([
  'schema_version', 'artifact_type', 'profile_version', 'registry_id', 'scope',
  'referents', 'external_sources', 'extensions',
]);
const REFERENT_KEYS = new Set([
  'ref', 'kind', 'labels', 'description', 'external_ids', 'classifications', 'attributes',
]);
const LABEL_KEYS = new Set(['text', 'lang']);
const EXTERNAL_ID_KEYS = new Set(['system', 'id', 'url']);
const EXTERNAL_SOURCE_KEYS = new Set(['system', 'id', 'url', 'revision', 'content_hash']);

export const REFERENT_KINDS = new Set([
  'person', 'collective', 'work', 'edition', 'manifestation', 'document', 'concept',
  'place', 'installation', 'activity', 'process', 'event', 'physical_object', 'system', 'other',
]);

const REF_RE = /^[a-z][a-z0-9._-]*:\S+$/;
const SHA256_RE = /^sha256:[0-9a-fA-F]{64}$/;
const LANG_RE = /^[a-zA-Z]{2,3}(-[a-zA-Z0-9]{2,8})*$/;

function isObject(v) {
  return v !== null && typeof v === 'object' && !Array.isArray(v);
}

function unknownKeys(obj, allowed, prefix, issues) {
  if (!isObject(obj)) return;
  for (const key of Object.keys(obj)) {
    if (!allowed.has(key)) issues.push(`${prefix}: unsupported property ${key}`);
  }
}

function nonEmptyString(value) {
  return typeof value === 'string' && value.length > 0;
}

function validUri(value) {
  if (typeof value !== 'string') return false;
  try {
    const url = new URL(value);
    return Boolean(url.protocol);
  } catch {
    return false;
  }
}

function verifyLabel(label, prefix, issues) {
  if (!isObject(label)) {
    issues.push(`${prefix}: label must be an object`);
    return;
  }
  unknownKeys(label, LABEL_KEYS, prefix, issues);
  if (!nonEmptyString(label.text)) issues.push(`${prefix}: text must be a non-empty string`);
  if ('lang' in label && (typeof label.lang !== 'string' || !LANG_RE.test(label.lang))) {
    issues.push(`${prefix}: invalid language tag`);
  }
}

function verifyExternalId(value, prefix, issues) {
  if (!isObject(value)) {
    issues.push(`${prefix}: external identifier must be an object`);
    return;
  }
  unknownKeys(value, EXTERNAL_ID_KEYS, prefix, issues);
  if (!nonEmptyString(value.system)) issues.push(`${prefix}: system must be a non-empty string`);
  if (!nonEmptyString(value.id)) issues.push(`${prefix}: id must be a non-empty string`);
  if ('url' in value && !validUri(value.url)) issues.push(`${prefix}: url must be an absolute URI`);
}

function verifyReferent(value, index, issues) {
  const prefix = `referents[${index}]`;
  if (!isObject(value)) {
    issues.push(`${prefix}: referent must be an object`);
    return;
  }
  unknownKeys(value, REFERENT_KEYS, prefix, issues);
  if (!nonEmptyString(value.ref) || !REF_RE.test(value.ref)) issues.push(`${prefix}: invalid ref`);
  if (!REFERENT_KINDS.has(value.kind)) issues.push(`${prefix}: unsupported kind ${String(value.kind)}`);
  if (!Array.isArray(value.labels) || value.labels.length < 1) {
    issues.push(`${prefix}: labels must contain at least one label`);
  } else {
    value.labels.forEach((label, i) => verifyLabel(label, `${prefix}.labels[${i}]`, issues));
  }
  if ('description' in value && typeof value.description !== 'string') issues.push(`${prefix}: description must be a string`);
  if ('external_ids' in value) {
    if (!Array.isArray(value.external_ids)) issues.push(`${prefix}: external_ids must be an array`);
    else value.external_ids.forEach((x, i) => verifyExternalId(x, `${prefix}.external_ids[${i}]`, issues));
  }
  if ('classifications' in value) {
    if (!Array.isArray(value.classifications) || value.classifications.some((x) => !nonEmptyString(x))) {
      issues.push(`${prefix}: classifications must be an array of non-empty strings`);
    }
  }
  if ('attributes' in value && !isObject(value.attributes)) issues.push(`${prefix}: attributes must be an object`);
}

function verifyExternalSource(value, index, issues) {
  const prefix = `external_sources[${index}]`;
  if (!isObject(value)) {
    issues.push(`${prefix}: external source must be an object`);
    return;
  }
  unknownKeys(value, EXTERNAL_SOURCE_KEYS, prefix, issues);
  if (!nonEmptyString(value.system)) issues.push(`${prefix}: system must be a non-empty string`);
  if (!nonEmptyString(value.id)) issues.push(`${prefix}: id must be a non-empty string`);
  if ('url' in value && !validUri(value.url)) issues.push(`${prefix}: url must be an absolute URI`);
  if ('revision' in value && typeof value.revision !== 'string') issues.push(`${prefix}: revision must be a string`);
  if ('content_hash' in value && typeof value.content_hash !== 'string') issues.push(`${prefix}: content_hash must be a string`);
}

export function verifyReferentRegistry(doc) {
  const issues = [];
  if (!isObject(doc)) return { ok: false, profile: 'kristal.referent-registry/1.0.0', issues: ['registry must be an object'] };

  unknownKeys(doc, TOP_KEYS, 'registry', issues);
  if (doc.schema_version !== '5.0') issues.push('schema_version must be 5.0');
  if (doc.artifact_type !== 'referent_registry') issues.push('artifact_type must be referent_registry');
  if ('profile_version' in doc && doc.profile_version !== '1.0.0') issues.push('profile_version must be 1.0.0 when present');
  if (typeof doc.registry_id !== 'string' || !SHA256_RE.test(doc.registry_id)) issues.push('registry_id must be sha256:<64 hex>');

  if (!isObject(doc.scope) || !nonEmptyString(doc.scope.domain)) issues.push('scope.domain must be a non-empty string');
  if (!Array.isArray(doc.referents)) issues.push('referents must be an array');
  else doc.referents.forEach((x, i) => verifyReferent(x, i, issues));

  if ('external_sources' in doc) {
    if (!Array.isArray(doc.external_sources)) issues.push('external_sources must be an array');
    else doc.external_sources.forEach((x, i) => verifyExternalSource(x, i, issues));
  }
  if ('extensions' in doc && !isObject(doc.extensions)) issues.push('extensions must be an object');

  return {
    ok: issues.length === 0,
    profile: 'kristal.referent-registry/1.0.0',
    referent_count: Array.isArray(doc.referents) ? doc.referents.length : 0,
    issues,
  };
}
