import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { cloneJson } from '../src/jcs.mjs';
import { stateIdentity, verifyKristalState, summarizeKristalState } from '../src/kristal_state.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const fixture=JSON.parse(fs.readFileSync(path.resolve(here,'../../../examples/v6/kristal-state.example.json'),'utf8'));
let failed=0;
function test(name, cond, detail='') { if(cond) console.log(`PASS ${name}`); else { failed++; console.error(`FAIL ${name} ${detail}`); } }

let r=verifyKristalState(fixture,{requireIdentity:true});
test('v6 fixture verifies',r.ok,JSON.stringify(r.issues));
test('state id stable',stateIdentity(fixture).state_id===fixture.state_id);
const summary=summarizeKristalState(fixture);
test('role summary',summary.record_roles.derived_state===1 && summary.record_roles.structural_record===1);
test('actionability summary',summary.actionability_modes.human_review===1 && summary.actionability_modes.not_applicable===1);
test('valuation dimensions',summary.valuation_dimensions.intervention_necessity===1 && summary.valuation_dimensions.risk_score===1);

const unknown=cloneJson(fixture);
delete unknown.state_id; delete unknown.content_hash;
unknown.assertions[0].valuations.push({dimension:'diagnostic_support',value_semantics:'ordinal',value_state:'unknown',value:0});
r=verifyKristalState(unknown);
test('unknown cannot masquerade as zero',!r.ok);

const badProb=cloneJson(fixture); delete badProb.state_id; delete badProb.content_hash;
badProb.assertions[0].valuations.push({dimension:'cause_probability',value_semantics:'probability',value_state:'known',value:1.4});
test('invalid probability rejected',!verifyKristalState(badProb).ok);

const highAuto=cloneJson(fixture); delete highAuto.state_id; delete highAuto.content_hash;
highAuto.assertions[0].valuations[0].value='established';
highAuto.assertions[0].actionability={mode:'human_decision',requires_human_validation:true};
r=verifyKristalState(highAuto);
test('high valuation does not force automatic',r.ok && highAuto.assertions[0].actionability.mode==='human_decision');

const tampered=cloneJson(fixture); tampered.assertions[0].statement.predicate='maintenance.requires_replacement';
test('tamper breaks declared identity',!verifyKristalState(tampered,{requireIdentity:true}).ok);

if(failed) process.exit(1);
console.log('Kristal v6 reference tests: PASS');
