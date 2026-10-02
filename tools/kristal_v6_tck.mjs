#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const fixturePath = path.join(root,'docs','Technical-Reference','kristal-docs-v6','09-test-vectors','kristal-state','kristal-state.example.json');
const state = JSON.parse(fs.readFileSync(fixturePath,'utf8'));

const VALUE_SEMANTICS = new Set(['boolean','categorical','set','ordinal','scalar','interval','probability','distribution','vector','partial_order','state','temporal']);
const VALUE_STATES = new Set(['known','unknown','not_applicable','indeterminate','not_measured']);
const RECORD_ROLES = new Set(['authoritative_constraint','observed_state','organizational_rule','reference_knowledge','derived_state','decision','action','structural_record']);
const ACTIONABILITY = new Set(['automatic','human_review','human_decision','manual','prohibited','insufficient_information','not_applicable']);

function canonicalize(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string' || typeof value === 'number') {
    if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('non-finite number is not I-JSON');
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return '[' + value.map(canonicalize).join(',') + ']';
  if (typeof value === 'object') {
    const keys=Object.keys(value).sort();
    return '{'+keys.map(k=>JSON.stringify(k)+':'+canonicalize(value[k])).join(',')+'}';
  }
  throw new Error(`unsupported JSON value: ${typeof value}`);
}
function clone(v){ return JSON.parse(JSON.stringify(v)); }
function stateIdentity(s){
  const target=clone(s); delete target.state_id; delete target.content_hash; delete target.signatures;
  const canonical=canonicalize(target);
  const hex=crypto.createHash('sha256').update(Buffer.from(canonical,'utf8')).digest('hex');
  return {state_id:`sha256:${hex}`,content_hash:{alg:'sha256',value:hex}};
}
function checkValuation(v){
  if (!v || typeof v !== 'object' || Array.isArray(v)) return false;
  if (typeof v.dimension !== 'string' || !v.dimension) return false;
  if (!VALUE_SEMANTICS.has(v.value_semantics) || !VALUE_STATES.has(v.value_state)) return false;
  if (v.value_state === 'known' && !Object.hasOwn(v,'value')) return false;
  if (v.value_state !== 'known' && Object.hasOwn(v,'value')) return false;
  if (v.value_state === 'known' && v.value_semantics === 'probability' && (typeof v.value !== 'number' || v.value < 0 || v.value > 1)) return false;
  if (v.value_state === 'known' && v.value_semantics === 'boolean' && typeof v.value !== 'boolean') return false;
  if (v.value_state === 'known' && v.value_semantics === 'scalar' && typeof v.value !== 'number') return false;
  return true;
}
function verify(s){
  if (s.schema_version !== '6.0' || s.artifact_type !== 'kristal_state' || !Array.isArray(s.assertions)) return false;
  for (const a of s.assertions){
    if (!a.statement || typeof a.statement !== 'object') return false;
    if (a.record_role !== undefined && !RECORD_ROLES.has(a.record_role)) return false;
    if (a.valuations !== undefined && (!Array.isArray(a.valuations) || !a.valuations.every(checkValuation))) return false;
    if (a.actionability !== undefined && (!a.actionability || !ACTIONABILITY.has(a.actionability.mode))) return false;
  }
  const id=stateIdentity(s);
  if (s.state_id !== undefined && s.state_id !== id.state_id) return false;
  if (s.content_hash !== undefined && (s.content_hash.alg !== 'sha256' || s.content_hash.value !== id.content_hash.value)) return false;
  return true;
}

let failures=0;
function expect(name, condition){
  if(condition) console.log(`PASS ${name}`); else {console.error(`FAIL ${name}`); failures++;}
}
expect('positive v6 fixture', verify(state));
expect('fixture canonical state identity', stateIdentity(state).state_id === state.state_id);

const badUnknown=clone(state); badUnknown.assertions[1].valuations[0].value='low'; delete badUnknown.state_id; delete badUnknown.content_hash;
expect('non-known value state cannot carry value', !verify(badUnknown));
const badProb=clone(state); badProb.assertions[0].valuations.push({dimension:'p',value_semantics:'probability',value_state:'known',value:1.2}); delete badProb.state_id; delete badProb.content_hash;
expect('probability is bounded', !verify(badProb));
const badRole=clone(state); badRole.assertions[0].record_role='law_because_i_said_so'; delete badRole.state_id; delete badRole.content_hash;
expect('record_role vocabulary', !verify(badRole));
const badAction=clone(state); badAction.assertions[0].actionability.mode='execute_everything'; delete badAction.state_id; delete badAction.content_hash;
expect('actionability vocabulary', !verify(badAction));

if(failures) process.exit(1);
console.log('Kristal v6 TCK: PASS');
