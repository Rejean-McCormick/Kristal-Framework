import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { canonicalize, cloneJson, removePointer } from '../src/jcs.mjs';
import { sha256Hex } from '../src/hash.mjs';
import { exchangeIdentity, verifyExchange } from '../src/exchange.mjs';
import { buildRuntimePackFromRequest, runtimePackIdentity, verifyRuntimePack } from '../src/runtime_pack.mjs';
import { verifySignatureFixture, verifyTrustFixture } from '../src/security.mjs';
import { verifyPortableVector } from '../src/runtime_pack_portable.mjs';
import { verifyReferentRegistry } from '../src/referent_registry.mjs';
import { verifyKnowledgeModelContract } from '../src/knowledge_model_contract.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..');
const kristalRoot = process.env.KRISTAL_ROOT ? path.resolve(process.env.KRISTAL_ROOT) : path.resolve(repo, '..', '..');
const vectorsRoot = path.join(kristalRoot, 'spec', 'v5', '09-test-vectors');

let failed = 0;
function pass(name) { console.log(`PASS ${name}`); }
function fail(name, message) { failed++; console.error(`FAIL ${name} — ${message}`); }
function assert(name, condition, message='assertion failed') { condition ? pass(name) : fail(name, message); }
function readJson(p) { return JSON.parse(fs.readFileSync(p, 'utf8')); }

if (!fs.existsSync(vectorsRoot)) {
  console.error(`Framework vectors not found: ${vectorsRoot}`);
  process.exit(2);
}

// Independent execution of the official JCS vectors.
const jcsDoc = readJson(path.join(vectorsRoot, 'jcs', 'vectors.json'));
for (const v of jcsDoc.vectors) {
  const input = cloneJson(v.input);
  for (const ptr of v.content_boundary?.exclude_json_pointers ?? []) removePointer(input, ptr);
  const canonical = canonicalize(input);
  const digest = sha256Hex(Buffer.from(canonical, 'utf8'));
  assert(`JCS ${v.id}`, canonical === v.expected_canonical && digest === v.expected_sha256_hex,
    `canonical/hash mismatch expected=${v.expected_sha256_hex} actual=${digest}`);
}

const exchangeDoc = readJson(path.join(vectorsRoot, 'exchange', 'vectors.json'));
for (const v of exchangeDoc.vectors) {
  const id = exchangeIdentity(v.input);
  const idOk = id.canonical === v.expected_canonical && id.kristal_id === v.expected_kristal_id;
  assert(`Exchange identity ${v.id}`, idOk, `expected=${v.expected_kristal_id} actual=${id.kristal_id}`);
  const verify = verifyExchange(v.input);
  const shouldPass = (v.expect_declared_hash_integrity ?? 'pass') === 'pass';
  assert(`Exchange verify ${v.id}`, verify.ok === shouldPass, `expected ok=${shouldPass} issues=${verify.issues.join(',')}`);
}

const rpDoc = readJson(path.join(vectorsRoot, 'runtime-pack', 'vectors.json'));
for (const v of rpDoc.vectors) {
  const id = runtimePackIdentity(v.input);
  assert(`Runtime Pack identity ${v.id}`, id.canonical === v.expected_canonical && id.runtime_pack_id === v.expected_runtime_pack_id,
    `expected=${v.expected_runtime_pack_id} actual=${id.runtime_pack_id}`);

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), `kristal-rp-${v.id}-`));
  try {
    const built = buildRuntimePackFromRequest(v, tmp);
    const verification = verifyRuntimePack(built.manifest, tmp);
    if ((v.expect_payload_integrity ?? 'pass') === 'pass') {
      assert(`Runtime Pack verify ${v.id}`, verification.ok, verification.issues.join(','));
    } else {
      // Build rewrites inventory from payload bytes, so test the supplied tampered vector against its declared manifest separately.
      for (const [rel, encoded] of Object.entries(v.payloads ?? {})) {
        const full = path.join(tmp, ...rel.split('/'));
        fs.mkdirSync(path.dirname(full), { recursive: true });
        fs.writeFileSync(full, Buffer.from(encoded, 'base64'));
      }
      const supplied = verifyRuntimePack(v.input, tmp);
      assert(`Runtime Pack reject ${v.id}`, !supplied.ok, 'tampered vector unexpectedly accepted');
    }
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

// Portable RP-2..RP-5 byte-profile vectors.
const portableDoc = readJson(path.join(vectorsRoot, 'runtime-pack', 'portable-vectors.json'));
assert('Runtime Pack portable profile id', portableDoc.profile === 'kristal.v5:runtime-pack-portable-conformance@1', portableDoc.profile);
for (const v of portableDoc.vectors ?? []) {
  const result = verifyPortableVector(v);
  assert(`Runtime Pack portable ${v.id}`, result.ok, result.issues.join(','));
}

// Referent Registry 1.0.0 conformance adapter.
const referentExample = readJson(path.join(kristalRoot, 'spec', 'v5', '10-examples', 'referent-registry.example.json'));
const referentResult = verifyReferentRegistry(referentExample);
assert('Referent Registry example accepted', referentResult.ok, referentResult.issues.join(','));
const invalidReferent = cloneJson(referentExample);
invalidReferent.referents[0].kind = 'organization';
assert('Referent Registry rejects non-core kind', !verifyReferentRegistry(invalidReferent).ok);
const wikidataAsIdentity = cloneJson(referentExample);
wikidataAsIdentity.referents[0].ref = 'Q8018';
assert('Referent Registry requires stable namespaced ref', !verifyReferentRegistry(wikidataAsIdentity).ok);

// Frozen knowledge-model contract pin used by downstream consumers such as kOA.
const knowledgeContractPath = path.join(kristalRoot, 'contracts', 'legacy', 'knowledge-model-contract.v1.json');
const knowledgeContract = readJson(knowledgeContractPath);
// The supplied snapshots do not contain the exact historical contract-set payload pinned by v1.
// Preserve and verify the v1 bundle identity without fabricating that missing historical payload.
const knowledgeResult = verifyKnowledgeModelContract(knowledgeContract);
assert('Knowledge-model contract bundle verified', knowledgeResult.ok, knowledgeResult.issues.join(','));
assert('Knowledge-model bundle pin', knowledgeResult.bundle_sha256 === 'sha256:07fe0527ab29a4b40870efdd0c9e0c67c91de919e5428047245b2a2c04f8ea98', knowledgeResult.bundle_sha256);

// Security adapter tests.
const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
const { publicKey: wrongPublicKey } = crypto.generateKeyPairSync('ed25519');
const message = Buffer.from('Kristal signed fixture', 'utf8');
const signature = crypto.sign(null, message, privateKey);
const baseFixture = {
  algorithm: 'ed25519',
  public_key_pem: publicKey.export({ type: 'spki', format: 'pem' }),
  message_base64: message.toString('base64'),
  signature_base64: signature.toString('base64'),
};
assert('Ed25519 valid signature', verifySignatureFixture(baseFixture).ok);
assert('Ed25519 wrong key rejected', !verifySignatureFixture({ ...baseFixture, public_key_pem: wrongPublicKey.export({ type: 'spki', format: 'pem' }) }).ok);
const tampered = Buffer.from('Kristal signed fixturE', 'utf8');
assert('Ed25519 tampered payload rejected', !verifySignatureFixture({ ...baseFixture, message_base64: tampered.toString('base64') }).ok);

const root = {
  key_id: 'test-root-v1',
  public_key_pem: baseFixture.public_key_pem,
  not_before: '2026-01-01T00:00:00Z',
  not_after: '2027-01-01T00:00:00Z',
};
const trustFixture = {
  at: '2026-09-16T00:00:00Z',
  key_id: root.key_id,
  algorithm: 'ed25519',
  message_base64: baseFixture.message_base64,
  signature_base64: baseFixture.signature_base64,
  trust_roots: [root],
  revocations: [],
};
assert('Trust valid root', verifyTrustFixture(trustFixture).ok);
assert('Trust revoked key rejected', !verifyTrustFixture({ ...trustFixture, revocations: [{ key_id: root.key_id, effective_at: '2026-09-15T00:00:00Z' }] }).ok);
assert('Trust future revocation not active', verifyTrustFixture({ ...trustFixture, revocations: [{ key_id: root.key_id, effective_at: '2026-09-17T00:00:00Z' }] }).ok);
assert('Trust expired key rejected', !verifyTrustFixture({ ...trustFixture, at: '2027-02-01T00:00:00Z' }).ok);

if (failed) process.exit(1);
console.log('Kristal reference implementation tests: PASS');
