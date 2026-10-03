import crypto from 'node:crypto';

function asDate(value, label) {
  const ms = Date.parse(value);
  if (!Number.isFinite(ms)) throw new Error(`invalid ${label}: ${value}`);
  return ms;
}

export function verifySignatureFixture(fixture) {
  const algorithm = String(fixture.algorithm ?? fixture.signature?.alg ?? '').toLowerCase();
  if (algorithm !== 'ed25519') return { ok: false, issues: [`unsupported algorithm:${algorithm || '<missing>'}`] };
  try {
    const publicKey = crypto.createPublicKey(fixture.public_key_pem);
    const message = Buffer.from(fixture.message_base64 ?? '', 'base64');
    const signature = Buffer.from(fixture.signature_base64 ?? fixture.signature?.signature ?? '', 'base64');
    const ok = crypto.verify(null, message, publicKey, signature);
    return { ok, issues: ok ? [] : ['signature_invalid'] };
  } catch (error) {
    return { ok: false, issues: [`signature_error:${error.message}`] };
  }
}

export function verifyTrustFixture(fixture) {
  const issues = [];
  const at = asDate(fixture.at, 'at');
  const keyId = fixture.key_id ?? fixture.signature?.key_id;
  const root = (fixture.trust_roots ?? []).find((item) => item.key_id === keyId);
  if (!root) return { ok: false, issues: ['trust_root_missing'] };

  if (root.not_before && at < asDate(root.not_before, 'not_before')) issues.push('key_not_yet_valid');
  if (root.not_after && at > asDate(root.not_after, 'not_after')) issues.push('key_expired');

  for (const revocation of fixture.revocations ?? []) {
    if (revocation.key_id !== keyId) continue;
    const effective = asDate(revocation.effective_at ?? revocation.revoked_at, 'revocation effective_at');
    if (effective <= at) issues.push('key_revoked');
  }

  const sigResult = verifySignatureFixture({
    algorithm: fixture.algorithm ?? fixture.signature?.alg ?? 'ed25519',
    public_key_pem: root.public_key_pem,
    message_base64: fixture.message_base64,
    signature_base64: fixture.signature_base64 ?? fixture.signature?.signature,
  });
  issues.push(...sigResult.issues);
  return { ok: issues.length === 0, issues };
}
