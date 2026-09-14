#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const jcsDir = path.join(root, 'docs', 'Technical-Reference', 'kristal-docs-v5', '09-test-vectors', 'jcs');

function clone(value) { return JSON.parse(JSON.stringify(value)); }

function pointerParts(pointer) {
  if (pointer === '') return [];
  if (!pointer.startsWith('/')) throw new Error(`invalid JSON Pointer: ${pointer}`);
  return pointer.slice(1).split('/').map(x => x.replaceAll('~1','/').replaceAll('~0','~'));
}

function removePointer(doc, pointer) {
  const parts = pointerParts(pointer);
  if (!parts.length) throw new Error('root exclusion is not supported by Kristal vectors');
  let parent = doc;
  for (let i=0; i<parts.length-1; i++) {
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

// RFC 8785 uses ECMAScript primitive serialization and UTF-16 code-unit key ordering.
// JSON.stringify supplies the primitive/number/string serialization; Array.sort() on
// strings supplies UTF-16 lexicographic ordering in JavaScript.
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

const doc = JSON.parse(fs.readFileSync(path.join(jcsDir, 'vectors.json'), 'utf8'));
const expectedLines = fs.readFileSync(path.join(jcsDir, 'expected-hashes.txt'), 'utf8')
  .split(/\r?\n/).map(s=>s.trim()).filter(s=>s && !s.startsWith('#'));
const expected = new Map(expectedLines.map(line => line.split(/\s+/)));

let failures = 0;
for (const v of doc.vectors) {
  const input = clone(v.input);
  for (const ptr of (v.content_boundary?.exclude_json_pointers ?? [])) removePointer(input, ptr);
  const actual = canonicalize(input);
  const digest = crypto.createHash('sha256').update(Buffer.from(actual, 'utf8')).digest('hex');
  const problems = [];
  if (actual !== v.expected_canonical) problems.push(`canonical mismatch\n expected=${v.expected_canonical}\n actual  =${actual}`);
  if (digest !== v.expected_sha256_hex) problems.push(`embedded hash mismatch expected=${v.expected_sha256_hex} actual=${digest}`);
  if (expected.get(v.id) !== digest) problems.push(`expected-hashes mismatch expected=${expected.get(v.id)} actual=${digest}`);
  if (problems.length) {
    failures++;
    console.error(`FAIL ${v.id} (${v.name}): ${problems.join('; ')}`);
  } else {
    console.log(`PASS ${v.id} (${v.name})`);
  }
}
if (expected.size !== doc.vectors.length) {
  console.error(`FAIL expected-hashes entries=${expected.size}, vectors=${doc.vectors.length}`);
  failures++;
}
if (failures) process.exit(1);
console.log('JCS vectors: PASS');
