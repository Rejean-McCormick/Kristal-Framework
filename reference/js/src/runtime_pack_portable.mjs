import crypto from 'node:crypto';
import { canonicalize } from './jcs.mjs';
import { sha256Hex } from './hash.mjs';

export const PORTABLE_PROFILE = 'kristal.v5:runtime-pack-portable-conformance@1';
const UTF8 = new TextEncoder();

function cmpBytes(a, b) {
  return Buffer.compare(Buffer.from(a), Buffer.from(b));
}
function utf8Bytes(value) { return Buffer.from(String(value), 'utf8'); }
function cmpUtf8(a, b) { return cmpBytes(utf8Bytes(a), utf8Bytes(b)); }

export function sortPortableRows(rows, policy = 'qid_pid_statement_id_asc') {
  const out = rows.map((row) => JSON.parse(JSON.stringify(row)));
  const jcsBytes = (row) => Buffer.from(canonicalize(row), 'utf8');
  const tuples = {
    qid_pid_statement_id_asc: (r) => [r.subject, r.predicate, r.statement_id],
    subject_predicate_object_statement_id_asc: (r) => [r.subject, r.predicate, r.object, r.statement_id],
  };
  const tuple = tuples[policy];
  if (!tuple) throw new Error(`portable ordering policy not supported by reference profile: ${policy}`);
  out.sort((a, b) => {
    const aa = tuple(a), bb = tuple(b);
    for (let i = 0; i < aa.length; i++) {
      const c = cmpUtf8(aa[i], bb[i]);
      if (c) return c;
    }
    return cmpBytes(jcsBytes(a), jcsBytes(b));
  });
  return out;
}

export function encodeOrderedRows(rows, policy = 'qid_pid_statement_id_asc') {
  const ordered = sortPortableRows(rows, policy);
  const text = ordered.map((row) => canonicalize(row)).join('\n') + (ordered.length ? '\n' : '');
  return { ordered, bytes: Buffer.from(text, 'utf8') };
}

export function fixedRowGroups(rowCount, policy = 'fixed_rows_100k') {
  const sizes = { fixed_rows_100k: 100000, fixed_rows_1m: 1000000 };
  const groupSize = sizes[policy];
  if (!groupSize) throw new Error(`portable row grouping policy not supported by reference profile: ${policy}`);
  if (!Number.isSafeInteger(rowCount) || rowCount < 0) throw new Error('rowCount must be a non-negative safe integer');
  const groups = [];
  for (let start = 0, index = 0; start < rowCount; start += groupSize, index++) {
    groups.push({ index, start_row: start, row_count: Math.min(groupSize, rowCount - start) });
  }
  return groups;
}

export function encodeRowGroups(rowCount, policy = 'fixed_rows_100k') {
  const value = { policy, row_count: rowCount, groups: fixedRowGroups(rowCount, policy) };
  return { value, bytes: Buffer.from(canonicalize(value) + '\n', 'utf8') };
}

function u32le(n) { const b = Buffer.alloc(4); b.writeUInt32LE(n >>> 0); return b; }
function u16le(n) { const b = Buffer.alloc(2); b.writeUInt16LE(n & 0xffff); return b; }

function bloomDigest(seed, keyBytes) {
  const domain = Buffer.from('kristal-bloom-v1\0', 'utf8');
  return crypto.createHash('sha256')
    .update(domain)
    .update(u32le(seed))
    .update(u32le(keyBytes.length))
    .update(keyBytes)
    .digest();
}

function readU64LE(buf, offset) { return buf.readBigUInt64LE(offset); }
function setBit(bitset, position) { bitset[Math.floor(position / 8)] |= (1 << (position % 8)); }
function hasBit(bitset, position) { return (bitset[Math.floor(position / 8)] & (1 << (position % 8))) !== 0; }

function uniqueSortedKeys(keys) {
  const map = new Map();
  for (const key of keys) {
    const bytes = utf8Bytes(key);
    map.set(bytes.toString('hex'), { key: String(key), bytes });
  }
  return [...map.values()].sort((a, b) => cmpBytes(a.bytes, b.bytes));
}

function bloomPositions(seed, keyBytes, bitCount, hashFunctions) {
  const digest = bloomDigest(seed, keyBytes);
  const h1 = readU64LE(digest, 0);
  let h2 = readU64LE(digest, 8);
  if (h2 === 0n) h2 = 1n;
  const mod = BigInt(bitCount);
  const out = [];
  for (let i = 0; i < hashFunctions; i++) out.push(Number((h1 + BigInt(i) * h2) % mod));
  return out;
}

export function buildKbf1({ keys, seed, bits_per_key, hash_functions }) {
  if (!Number.isInteger(seed) || seed < 0 || seed > 0xffffffff) throw new Error('seed must be uint32');
  if (!Number.isInteger(bits_per_key) || bits_per_key < 1) throw new Error('bits_per_key must be >=1');
  if (!Number.isInteger(hash_functions) || hash_functions < 1 || hash_functions > 0xffff) throw new Error('hash_functions must be 1..65535');
  const unique = uniqueSortedKeys(keys);
  const bitCount = Math.max(8, Math.ceil((unique.length * bits_per_key) / 8) * 8);
  const bitset = Buffer.alloc(bitCount / 8);
  for (const { bytes } of unique) {
    for (const position of bloomPositions(seed, bytes, bitCount, hash_functions)) setBit(bitset, position);
  }
  const header = Buffer.alloc(24);
  header.write('KBF1', 0, 4, 'ascii');
  header.writeUInt8(1, 4);
  header.writeUInt8(1, 5);
  header.writeUInt16LE(0, 6);
  header.writeUInt32LE(seed >>> 0, 8);
  header.writeUInt32LE(bitCount >>> 0, 12);
  header.writeUInt16LE(hash_functions, 16);
  header.writeUInt16LE(0, 18);
  header.writeUInt32LE(unique.length >>> 0, 20);
  return { bytes: Buffer.concat([header, bitset]), bit_count: bitCount, key_count: unique.length, bitset };
}

export function bloomMaybeContains(kbf1Bytes, key) {
  const buf = Buffer.from(kbf1Bytes);
  if (buf.length < 25 || buf.subarray(0, 4).toString('ascii') !== 'KBF1') throw new Error('invalid KBF1 filter');
  if (buf.readUInt8(4) !== 1 || buf.readUInt8(5) !== 1) throw new Error('unsupported KBF1 version/hash method');
  const seed = buf.readUInt32LE(8);
  const bitCount = buf.readUInt32LE(12);
  const hashFunctions = buf.readUInt16LE(16);
  const bitset = buf.subarray(24);
  if (bitset.length !== Math.ceil(bitCount / 8)) throw new Error('invalid KBF1 bitset length');
  return bloomPositions(seed, utf8Bytes(key), bitCount, hashFunctions).every((p) => hasBit(bitset, p));
}

export function prunedMembership(kbf1Bytes, authoritativeKeys, key) {
  const maybe = bloomMaybeContains(kbf1Bytes, key);
  const authoritative = new Set(authoritativeKeys.map(String)).has(String(key));
  return { filter_maybe: maybe, authoritative, result: maybe && authoritative };
}

function normalizeU32Values(values) {
  const set = new Set();
  for (const value of values) {
    if (!Number.isInteger(value) || value < 0 || value > 0xffffffff) throw new Error(`bitmap value is not uint32: ${value}`);
    set.add(value >>> 0);
  }
  return [...set].sort((a, b) => a - b);
}

function runsFor(lows) {
  const runs = [];
  if (!lows.length) return runs;
  let start = lows[0], prev = lows[0];
  for (let i = 1; i < lows.length; i++) {
    const v = lows[i];
    if (v === prev + 1) { prev = v; continue; }
    runs.push([start, prev - start]);
    start = prev = v;
  }
  runs.push([start, prev - start]);
  return runs;
}

function arrayContainer(lows) {
  const b = Buffer.alloc(lows.length * 2);
  lows.forEach((v, i) => b.writeUInt16LE(v, i * 2));
  return b;
}
function bitsetContainer(lows) {
  const words = Array.from({ length: 1024 }, () => 0n);
  for (const v of lows) words[Math.floor(v / 64)] |= 1n << BigInt(v % 64);
  const b = Buffer.alloc(8192);
  words.forEach((w, i) => b.writeBigUInt64LE(w, i * 8));
  return b;
}
function runContainer(runs) {
  const b = Buffer.alloc(2 + runs.length * 4);
  b.writeUInt16LE(runs.length, 0);
  runs.forEach(([start, lenMinus1], i) => {
    b.writeUInt16LE(start, 2 + i * 4);
    b.writeUInt16LE(lenMinus1, 4 + i * 4);
  });
  return b;
}

export function serializeRoaring32(values, { run_optimize = false } = {}) {
  const sorted = normalizeU32Values(values);
  const buckets = new Map();
  for (const value of sorted) {
    const high = value >>> 16;
    const low = value & 0xffff;
    if (!buckets.has(high)) buckets.set(high, []);
    buckets.get(high).push(low);
  }
  const containers = [...buckets.entries()].sort((a, b) => a[0] - b[0]).map(([key, lows]) => {
    const cardinality = lows.length;
    const baseType = cardinality <= 4096 ? 'array' : 'bitset';
    const baseBytes = baseType === 'array' ? arrayContainer(lows) : bitsetContainer(lows);
    const runs = runsFor(lows);
    const runBytes = runContainer(runs);
    const useRun = Boolean(run_optimize && runBytes.length < baseBytes.length);
    return { key, lows, cardinality, type: useRun ? 'run' : baseType, bytes: useRun ? runBytes : baseBytes };
  });

  const hasRun = containers.some((c) => c.type === 'run');
  const size = containers.length;
  const parts = [];
  if (!hasRun) {
    const cookie = Buffer.alloc(8);
    cookie.writeUInt32LE(12346, 0);
    cookie.writeUInt32LE(size, 4);
    parts.push(cookie);
  } else {
    if (size < 1 || size > 0x10000) throw new Error('invalid Roaring container count');
    const cookie = Buffer.alloc(4);
    cookie.writeUInt32LE((12347 | ((size - 1) << 16)) >>> 0, 0);
    parts.push(cookie);
    const runBitmap = Buffer.alloc(Math.ceil(size / 8));
    containers.forEach((c, i) => { if (c.type === 'run') runBitmap[Math.floor(i / 8)] |= (1 << (i % 8)); });
    parts.push(runBitmap);
  }

  const descriptive = Buffer.alloc(size * 4);
  containers.forEach((c, i) => {
    descriptive.writeUInt16LE(c.key, i * 4);
    descriptive.writeUInt16LE(c.cardinality - 1, i * 4 + 2);
  });
  parts.push(descriptive);

  const needsOffsets = !hasRun || size >= 4;
  if (needsOffsets) {
    const prefixLen = parts.reduce((n, p) => n + p.length, 0) + size * 4;
    const offsets = Buffer.alloc(size * 4);
    let offset = prefixLen;
    containers.forEach((c, i) => {
      offsets.writeUInt32LE(offset >>> 0, i * 4);
      offset += c.bytes.length;
    });
    parts.push(offsets);
  }
  for (const c of containers) parts.push(c.bytes);
  return { bytes: Buffer.concat(parts), containers: containers.map((c) => ({ key: c.key, cardinality: c.cardinality, type: c.type, size_bytes: c.bytes.length })) };
}

export function executePortableVector(vector) {
  const kind = vector.case;
  if (kind === 'ordering') {
    const result = encodeOrderedRows(vector.input.rows, vector.input.policy);
    return { bytes: result.bytes, semantic: { ordered_statement_ids: result.ordered.map((r) => r.statement_id) } };
  }
  if (kind === 'row_grouping') {
    const result = encodeRowGroups(vector.input.row_count, vector.input.policy);
    return { bytes: result.bytes, semantic: result.value };
  }
  if (kind === 'membership_filter') {
    const result = buildKbf1(vector.input);
    const queries = (vector.queries ?? []).map((q) => ({ key: q.key, ...prunedMembership(result.bytes, vector.input.keys, q.key) }));
    return { bytes: result.bytes, semantic: { bit_count: result.bit_count, key_count: result.key_count, queries } };
  }
  if (kind === 'bitmap') {
    const result = serializeRoaring32(vector.input.values, { run_optimize: vector.input.run_optimize });
    return { bytes: result.bytes, semantic: { containers: result.containers } };
  }
  throw new Error(`unknown portable vector case: ${kind}`);
}

export function verifyPortableVector(vector) {
  const result = executePortableVector(vector);
  const actualBase64 = result.bytes.toString('base64');
  const actualSha = sha256Hex(result.bytes);
  const issues = [];
  if (actualBase64 !== vector.expected_payload_base64) issues.push('payload bytes mismatch');
  if (actualSha !== vector.expected_sha256_hex) issues.push(`sha256 mismatch expected=${vector.expected_sha256_hex} actual=${actualSha}`);
  if (vector.expected_semantic && canonicalize(result.semantic) !== canonicalize(vector.expected_semantic)) issues.push('semantic result mismatch');
  return { ok: issues.length === 0, issues, sha256_hex: actualSha, payload_base64: actualBase64, semantic: result.semantic };
}
