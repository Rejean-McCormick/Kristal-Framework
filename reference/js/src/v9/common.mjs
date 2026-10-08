import { canonicalize, cloneJson } from '../jcs.mjs';
import { sha256Hex } from '../hash.mjs';

export const V9_SCHEMA_VERSION = '9.0';
export const LOGICAL_PROFILE = 'kristal.logical/jcs-sha256-v1';
export const STATE_PROFILE = 'kristal.state-commitment/jcs-sha256-v1';

export function isObject(value) { return !!value && typeof value === 'object' && !Array.isArray(value); }
export function canonicalBytes(value) { return Buffer.from(canonicalize(value), 'utf8'); }
export function commitmentDigest(domain, value) {
  return `sha256:${sha256Hex(Buffer.concat([Buffer.from(domain, 'utf8'), canonicalBytes(value)]))}`;
}

// IMPORTANT: commitment ordering must never depend on the process locale.
// v9's "lexicographic" ordering is implemented as unsigned UTF-8 byte order.
// This comparator is deterministic across hosts, locales and ICU versions.
export function compareUtf8Lexicographic(a, b) {
  return Buffer.compare(Buffer.from(String(a), 'utf8'), Buffer.from(String(b), 'utf8'));
}

export function normalizeLogicalRef(ref) {
  const out = { artifact_id: ref.artifact_id, logical_commitment: cloneJson(ref.logical_commitment) };
  if (ref.logical_contract) out.logical_contract = cloneJson(ref.logical_contract);
  return out;
}
export function sortArtifactRefs(refs = []) {
  return refs.map(normalizeLogicalRef).sort((a,b) => {
    const ak = `${a.artifact_id}\u0000${a.logical_commitment?.digest ?? ''}`;
    const bk = `${b.artifact_id}\u0000${b.logical_commitment?.digest ?? ''}`;
    return compareUtf8Lexicographic(ak,bk);
  });
}
export function sortStateRefs(refs = []) {
  return refs.map((ref) => ({ state_ref: ref.state_ref, logical_commitment: cloneJson(ref.logical_commitment) }))
    .sort((a,b) => compareUtf8Lexicographic(
      `${a.state_ref}\u0000${a.logical_commitment?.digest ?? ''}`,
      `${b.state_ref}\u0000${b.logical_commitment?.digest ?? ''}`
    ));
}
