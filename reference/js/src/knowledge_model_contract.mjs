import fs from 'node:fs';
import path from 'node:path';
import { canonicalize } from './jcs.mjs';
import { sha256Id } from './hash.mjs';

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function knowledgeModelBundleIdentity(contract) {
  const core = clone(contract);
  delete core.bundle_sha256;
  return sha256Id(Buffer.from(canonicalize(core), 'utf8'));
}

export function verifyKnowledgeModelContract(contract, frameworkRoot) {
  const issues = [];
  if (!contract || typeof contract !== 'object' || Array.isArray(contract)) {
    return { ok: false, issues: ['contract must be an object'] };
  }
  if (contract.format !== 'kristal.knowledge-model-contract/v1') issues.push('unsupported contract format');
  if (contract.release !== '5.0.0-rc.3') issues.push(`unexpected release ${String(contract.release)}`);
  if (contract.referent_profile !== 'kristal.referent-registry/1.0.0') issues.push('unexpected referent profile');
  if (contract.structured_epistemic_state !== '5.0') issues.push('unexpected Structured Epistemic State version');

  const computed = knowledgeModelBundleIdentity(contract);
  if (contract.bundle_sha256 !== computed) {
    issues.push(`bundle_sha256 mismatch: expected ${computed}, declared ${String(contract.bundle_sha256)}`);
  }

  if (!Array.isArray(contract.files) || contract.files.length < 1) {
    issues.push('files must be a non-empty array');
  } else if (frameworkRoot) {
    for (const [i, entry] of contract.files.entries()) {
      if (!entry || typeof entry !== 'object') {
        issues.push(`files[${i}] must be an object`);
        continue;
      }
      const full = path.resolve(frameworkRoot, String(entry.path ?? ''));
      if (!fs.existsSync(full) || !fs.statSync(full).isFile()) {
        issues.push(`missing contract file: ${String(entry.path)}`);
        continue;
      }
      const bytes = fs.readFileSync(full);
      const digest = sha256Id(bytes);
      if (digest !== entry.sha256) issues.push(`file hash mismatch: ${entry.path}`);
      if (bytes.length !== entry.bytes) issues.push(`file size mismatch: ${entry.path}`);
    }
  }

  return {
    ok: issues.length === 0,
    profile: 'kristal.knowledge-model-contract/v1',
    bundle_sha256: computed,
    files_verified: frameworkRoot && Array.isArray(contract.files) ? contract.files.length : 0,
    issues,
  };
}
