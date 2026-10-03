import fs from 'node:fs';
import path from 'node:path';
import { canonicalize, cloneJson, removePointer, removeSignatureMaterial } from './jcs.mjs';
import { sha256Hex } from './hash.mjs';

export const RUNTIME_PACK_ID_PROFILE = 'kristal.v5:runtime-pack-id-core@1';
export const RUNTIME_PACK_EXCLUSIONS = [
  '/runtime_pack_id',
  '/created_at',
  '/build/build_id',
  '/compiler/build_platform',
  '/integrity/pack_hash',
  '/integrity/manifest_hash',
];

export function runtimePackHashTarget(input) {
  const target = cloneJson(input);
  removeSignatureMaterial(target);
  for (const pointer of RUNTIME_PACK_EXCLUSIONS) removePointer(target, pointer);
  return target;
}

export function runtimePackIdentity(input) {
  const target = runtimePackHashTarget(input);
  const canonical = canonicalize(target);
  const hex = sha256Hex(Buffer.from(canonical, 'utf8'));
  return {
    profile: RUNTIME_PACK_ID_PROFILE,
    canonical,
    sha256_hex: hex,
    runtime_pack_id: `sha256:${hex}`,
  };
}

export function verifyPayloadInventory(manifest, payloadDir) {
  const issues = [];
  const declared = new Set();
  for (const entry of manifest.files ?? []) {
    declared.add(entry.path);
    const full = path.join(payloadDir, ...entry.path.split('/'));
    if (!fs.existsSync(full) || !fs.statSync(full).isFile()) {
      issues.push(`missing payload:${entry.path}`);
      continue;
    }
    const bytes = fs.readFileSync(full);
    const digest = sha256Hex(bytes);
    if (digest !== entry.sha256) issues.push(`hash mismatch:${entry.path}`);
    if (bytes.length !== entry.size_bytes) issues.push(`size mismatch:${entry.path}`);
  }
  return issues;
}

export function verifyRuntimePack(manifest, payloadDir) {
  const identity = runtimePackIdentity(manifest);
  const issues = [];
  if (manifest?.runtime_pack_id !== identity.runtime_pack_id) {
    issues.push(`runtime_pack_id mismatch: expected ${identity.runtime_pack_id}, declared ${manifest?.runtime_pack_id ?? '<missing>'}`);
  }
  issues.push(...verifyPayloadInventory(manifest, payloadDir));
  return { ok: issues.length === 0, issues, ...identity };
}

export function buildRuntimePackFromRequest(request, outputDir) {
  const manifest = cloneJson(request.manifest ?? request.input ?? request);
  const payloads = request.payloads ?? {};
  fs.mkdirSync(outputDir, { recursive: true });

  const byPath = new Map((manifest.files ?? []).map((entry) => [entry.path, entry]));
  for (const [rel, encoded] of Object.entries(payloads)) {
    const bytes = Buffer.from(encoded, 'base64');
    const full = path.join(outputDir, ...rel.split('/'));
    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, bytes);
    const entry = byPath.get(rel);
    if (entry) {
      entry.sha256 = sha256Hex(bytes);
      entry.size_bytes = bytes.length;
    }
  }

  const identity = runtimePackIdentity(manifest);
  manifest.runtime_pack_id = identity.runtime_pack_id;
  const manifestPath = path.join(outputDir, 'runtime-pack.manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n', 'utf8');
  return { manifest, manifest_path: manifestPath, ...identity };
}
