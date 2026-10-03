export function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

export function canonicalize(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string' || typeof value === 'number') {
    if (typeof value === 'number' && !Number.isFinite(value)) {
      throw new Error('non-finite number is not valid I-JSON');
    }
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return '[' + value.map(canonicalize).join(',') + ']';
  }
  if (typeof value === 'object') {
    const keys = Object.keys(value).sort();
    return '{' + keys.map((key) => JSON.stringify(key) + ':' + canonicalize(value[key])).join(',') + '}';
  }
  throw new Error(`unsupported JSON value: ${typeof value}`);
}

export function pointerParts(pointer) {
  if (pointer === '') return [];
  if (!pointer.startsWith('/')) throw new Error(`invalid JSON Pointer: ${pointer}`);
  return pointer.slice(1).split('/').map((x) => x.replaceAll('~1', '/').replaceAll('~0', '~'));
}

export function removePointer(doc, pointer) {
  const parts = pointerParts(pointer);
  if (!parts.length) throw new Error('root exclusion unsupported');
  let parent = doc;
  for (let i = 0; i < parts.length - 1; i++) {
    if (parent === null || typeof parent !== 'object' || !(parts[i] in parent)) return;
    parent = parent[parts[i]];
  }
  const last = parts.at(-1);
  if (Array.isArray(parent)) {
    const idx = Number(last);
    if (Number.isInteger(idx) && idx >= 0 && idx < parent.length) parent.splice(idx, 1);
  } else if (parent && typeof parent === 'object') {
    delete parent[last];
  }
}

export function removeSignatureMaterial(value) {
  if (Array.isArray(value)) {
    for (const item of value) removeSignatureMaterial(item);
    return;
  }
  if (!value || typeof value !== 'object') return;
  delete value.signatures;
  delete value.attestations;
  for (const nested of Object.values(value)) removeSignatureMaterial(nested);
}
