import { canonicalize, cloneJson, removeSignatureMaterial } from './jcs.mjs';
import { sha256Hex } from './hash.mjs';

export const EXCHANGE_ID_PROFILE = 'kristal.v5:exchange-id-core@1';

export function exchangeHashTarget(input) {
  const target = cloneJson(input);
  delete target.kristal_id;
  delete target.content_hash;
  removeSignatureMaterial(target);
  return target;
}

export function exchangeIdentity(input) {
  const target = exchangeHashTarget(input);
  const canonical = canonicalize(target);
  const hex = sha256Hex(Buffer.from(canonical, 'utf8'));
  return {
    profile: EXCHANGE_ID_PROFILE,
    canonical,
    sha256_hex: hex,
    kristal_id: `sha256:${hex}`,
  };
}

export function verifyExchange(input) {
  const identity = exchangeIdentity(input);
  const issues = [];
  if (input?.kristal_id !== identity.kristal_id) {
    issues.push(`kristal_id mismatch: expected ${identity.kristal_id}, declared ${input?.kristal_id ?? '<missing>'}`);
  }
  if (input?.content_hash?.alg !== 'sha256') {
    issues.push('content_hash.alg must be sha256');
  }
  if (input?.content_hash?.value !== identity.sha256_hex) {
    issues.push(`content_hash.value mismatch: expected ${identity.sha256_hex}, declared ${input?.content_hash?.value ?? '<missing>'}`);
  }
  return { ok: issues.length === 0, issues, ...identity };
}
