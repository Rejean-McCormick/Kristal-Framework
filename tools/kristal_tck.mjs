#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { verifyPortableVector } from './runtime_pack_portable_tck.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const vectorsRoot = path.join(root, 'docs', 'Technical-Reference', 'kristal-docs-v5', '09-test-vectors');

function clone(v) { return JSON.parse(JSON.stringify(v)); }
function canonicalize(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string' || typeof value === 'number') {
    if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('non-finite number is not I-JSON');
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return '[' + value.map(canonicalize).join(',') + ']';
  if (typeof value === 'object') {
    const keys = Object.keys(value).sort();
    return '{' + keys.map(k => JSON.stringify(k) + ':' + canonicalize(value[k])).join(',') + '}';
  }
  throw new Error(`unsupported JSON value: ${typeof value}`);
}
function sha256Hex(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }
function pointerParts(pointer) {
  if (pointer === '') return [];
  if (!pointer.startsWith('/')) throw new Error(`invalid JSON Pointer: ${pointer}`);
  return pointer.slice(1).split('/').map(x => x.replaceAll('~1','/').replaceAll('~0','~'));
}
function removePointer(doc, pointer) {
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
function removeSignatureMaterial(value) {
  if (Array.isArray(value)) {
    for (const item of value) removeSignatureMaterial(item);
    return;
  }
  if (!value || typeof value !== 'object') return;
  delete value.signatures;
  delete value.attestations;
  for (const v of Object.values(value)) removeSignatureMaterial(v);
}
function exchangeTarget(input) {
  const target = clone(input);
  delete target.kristal_id;
  delete target.content_hash;
  removeSignatureMaterial(target);
  return target;
}
function runtimePackTarget(input, exclusions) {
  const target = clone(input);
  removeSignatureMaterial(target);
  for (const p of exclusions) removePointer(target, p);
  return target;
}
function digestTarget(target) {
  const canonical = canonicalize(target);
  const hex = sha256Hex(Buffer.from(canonical, 'utf8'));
  return { canonical, hex, id: `sha256:${hex}` };
}
function readJson(rel) { return JSON.parse(fs.readFileSync(path.join(vectorsRoot, rel), 'utf8')); }

let failed = 0;
function pass(id, msg='') { console.log(`PASS ${id}${msg ? ` — ${msg}` : ''}`); }
function fail(id, msg) { failed++; console.error(`FAIL ${id} — ${msg}`); }

function runExchangeVectors() {
  const doc = readJson('exchange/vectors.json');
  const results = new Map();
  for (const v of doc.vectors) {
    const actual = digestTarget(exchangeTarget(v.input));
    results.set(v.id, actual);
    const problems = [];
    if (actual.canonical !== v.expected_canonical) problems.push('canonical target mismatch');
    if (actual.hex !== v.expected_sha256_hex) problems.push(`sha mismatch expected=${v.expected_sha256_hex} actual=${actual.hex}`);
    if (actual.id !== v.expected_kristal_id) problems.push(`id mismatch expected=${v.expected_kristal_id} actual=${actual.id}`);
    const declaredHashOk = v.input?.kristal_id === actual.id && v.input?.content_hash?.alg === 'sha256' && v.input?.content_hash?.value === actual.hex;
    if ((v.expect_declared_hash_integrity ?? 'pass') === 'pass' && !declaredHashOk) problems.push('declared Exchange hash/ID mismatch');
    if (v.expect_declared_hash_integrity === 'fail' && declaredHashOk) problems.push('tampered Exchange unexpectedly passes declared hash/ID verification');
    problems.length ? fail(v.id, problems.join('; ')) : pass(v.id, v.name);
  }
  for (const rel of doc.relations ?? []) {
    const a = results.get(rel.left), b = results.get(rel.right);
    if (!a || !b) { fail(rel.id, 'unknown relation vector'); continue; }
    const ok = rel.expect === 'same_id' ? a.id === b.id : a.id !== b.id;
    ok ? pass(rel.id, rel.expect) : fail(rel.id, `${rel.left}=${a.id}, ${rel.right}=${b.id}`);
  }
}

function verifyRuntimePackPayloads(vector) {
  const manifest = vector.input;
  const payloads = vector.payloads ?? {};
  const issues = [];
  for (const entry of manifest.files ?? []) {
    if (!(entry.path in payloads)) { issues.push(`missing payload:${entry.path}`); continue; }
    const bytes = Buffer.from(payloads[entry.path], 'base64');
    const digest = sha256Hex(bytes);
    if (digest !== entry.sha256) issues.push(`hash mismatch:${entry.path}`);
    if (bytes.length !== entry.size_bytes) issues.push(`size mismatch:${entry.path}`);
  }
  return issues;
}

function runRuntimePackVectors() {
  const doc = readJson('runtime-pack/vectors.json');
  for (const v of doc.vectors) {
    const actual = digestTarget(runtimePackTarget(v.input, doc.id_profile.exclude_json_pointers));
    const problems = [];
    if (actual.canonical !== v.expected_canonical) problems.push('canonical target mismatch');
    if (actual.hex !== v.expected_sha256_hex) problems.push(`sha mismatch expected=${v.expected_sha256_hex} actual=${actual.hex}`);
    if (actual.id !== v.expected_runtime_pack_id) problems.push(`id mismatch expected=${v.expected_runtime_pack_id} actual=${actual.id}`);
    const integrity = verifyRuntimePackPayloads(v);
    if ((v.expect_payload_integrity ?? 'pass') === 'pass' && integrity.length) problems.push(...integrity);
    if (v.expect_payload_integrity === 'fail' && !integrity.length) problems.push('tampered payload unexpectedly accepted');
    problems.length ? fail(v.id, problems.join('; ')) : pass(v.id, v.name);
  }
}


function runRuntimePackPortableVectors() {
  const doc = readJson('runtime-pack/portable-vectors.json');
  if (doc.profile !== 'kristal.v5:runtime-pack-portable-conformance@1') {
    fail('RP-PROFILE', `unexpected portable profile ${doc.profile}`);
    return;
  }
  for (const v of doc.vectors ?? []) {
    const result = verifyPortableVector(v);
    result.ok ? pass(v.id, v.name) : fail(v.id, result.issues.join('; '));
  }
}

runExchangeVectors();
runRuntimePackVectors();
runRuntimePackPortableVectors();
if (failed) process.exit(1);
console.log('Kristal TCK framework vectors: PASS');
