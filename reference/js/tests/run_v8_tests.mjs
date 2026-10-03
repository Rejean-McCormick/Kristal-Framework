import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { inspectArtifact, buildDataset } from '../src/v8/reader.mjs';
import { semanticFingerprint } from '../src/v8/common.mjs';
import { lexiconMap, resolveLexicalization, verifyLexicon, verifyLexiconStack } from '../src/v8/lexicon.mjs';
import { executeQuery, verifyQueryRequest } from '../src/v8/query.mjs';
import { createQueryIndex, exportQueryIndex } from '../src/v8/query_index.mjs';
import { compileAIContext, expandCompactContext } from '../src/v8/ai_context.mjs';
import { referenceV8Capabilities } from '../src/v8/capabilities.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../../..');
const read=(p)=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
let failed=0;
function test(name, cond, detail=''){if(cond)console.log(`PASS ${name}`);else{failed++;console.error(`FAIL ${name}${detail?' — '+detail:''}`);}}
function clone(v){return JSON.parse(JSON.stringify(v));}

const v6=read('examples/v6/kristal-state.example.json');
const entity=read('examples/v7/entity-registry.example.json');
const prop=read('examples/v7/property-registry.example.json');
const ass=read('examples/v7/assertion-registry.example.json');
const src=read('examples/v7/source-registry.example.json');
const mesh=read('examples/v7/mesh.example.json');
const lexCore=read('examples/v8/lexicon-fr-core.example.json');
const lexChem=read('examples/v8/lexicon-fr-chemistry.example.json');
const stack=read('examples/v8/lexicon-stack.example.json');
const request=read('examples/v8/query-request.example.json');

test('v8 reader accepts v6',inspectArtifact(v6).ok&&inspectArtifact(v6).family==='v6');
test('v8 reader accepts v7',inspectArtifact(entity).ok&&inspectArtifact(entity).family==='v7');
test('v8 reader accepts v8',inspectArtifact(lexCore).ok&&inspectArtifact(lexCore).family==='v8');
test('lexicon verifies',verifyLexicon(lexCore).ok);
test('lexicon stack verifies',verifyLexiconStack(stack).ok);

const map=lexiconMap([lexCore,lexChem]);
let r=resolveLexicalization({identity_space:'kristall',id:'KQ1001'},stack,map);
test('fr lexical resolution',r.lexical_status==='resolved'&&r.term==='ministre',JSON.stringify(r));
r=resolveLexicalization({identity_space:'kristall',id:'KQ847291'},stack,map);
test('domain lexicon precedence',r.lexical_status==='resolved'&&r.term==='oxygène',JSON.stringify(r));
r=resolveLexicalization({identity_space:'kristall',id:'KQ9999'},stack,map);
test('missing lexicalization preserves semantic id',r.lexical_status==='missing'&&r.render==='KQ9999',JSON.stringify(r));

const changedLabel=clone(entity);changedLabel.entities[0].preferred_label='Minister';
const changedKind=clone(entity);changedKind.entities[0].entity_kind='person';
test('semantic fingerprint ignores presentation label',semanticFingerprint(entity).digest===semanticFingerprint(changedLabel).digest);
test('semantic fingerprint changes on semantic field',semanticFingerprint(entity).digest!==semanticFingerprint(changedKind).digest);

const dataset=buildDataset([entity,prop,ass,src,mesh,v6].map((doc,i)=>({doc,ref:`mem:${i}`})));
test('dataset contains v6 and v7',dataset.v6_states.length===1&&dataset.entities.length===3&&dataset.edges.length===1);
const index=createQueryIndex(dataset);
test('query index identity lookup',index.identity.has('kristall\u0000KQ1001'));
const exported=exportQueryIndex(index,dataset);
test('query index is derived',exported.manifest.authoritative===false&&exported.manifest.rebuildable===true&&exported.manifest.indexes.length>=4);

test('KQP request validates',verifyQueryRequest(request).ok);
let result=executeQuery(request,dataset,{index});
test('semantic slice completes',result.status==='complete',JSON.stringify(result.completeness));
test('semantic slice returns root',result.result.nodes.some(x=>x.id==='KQ1001'));
test('semantic slice traverses matching edge',result.result.edges.some(x=>x.relation==='KP1001'));
test('query plan exact',result.query_plan.discovery==='exact'&&result.query_plan.strategy==='identity_graph');

const pagedReq=clone(request);pagedReq.query_id='Q-page';pagedReq.pagination={page_size:1};pagedReq.budget.max_items=20;
const page1=executeQuery(pagedReq,dataset,{index});
test('pagination exposes continuation',page1.status==='partial'&&page1.continuation.has_more&&typeof page1.continuation.cursor==='string');
const page2Req=clone(pagedReq);page2Req.pagination.cursor=page1.continuation.cursor;
const page2=executeQuery(page2Req,dataset,{index});
test('continuation advances',JSON.stringify(page1.result)!==JSON.stringify(page2.result));
const badCursorReq=clone(page2Req);badCursorReq.roots=[{identity_space:'kristall',id:'KQ2001'}];
const badCursor=executeQuery(badCursorReq,dataset,{index});
test('cursor bound to query/snapshot',badCursor.status==='error'&&badCursor.completeness.reasons.includes('cursor_or_budget_error'));


const v6Request=clone(request);v6Request.query_id='Q-v6-adapter';v6Request.roots=[{identity_space:'kristal_v6',id:'urn:asset:pump-17'}];v6Request.traversal.properties=[];v6Request.language=undefined;v6Request.budget.max_bytes=200000;
const v6Result=executeQuery(v6Request,dataset,{index});
test('v8 query adapter traverses v6 without KQ invention',v6Result.status==='complete'&&v6Result.result.nodes.some(x=>x.identity_space==='kristal_v6'&&x.id==='urn:asset:pump-17')&&v6Result.result.edges.some(x=>x.relation==='maintenance.indicates_inspection'));

const byteBudgetReq=clone(request);byteBudgetReq.query_id='Q-byte-budget';byteBudgetReq.budget.max_bytes=2000;byteBudgetReq.pagination={page_size:300};
const byteBudgetResult=executeQuery(byteBudgetReq,dataset,{index});
test('KQP hard byte budget respected',Buffer.byteLength(JSON.stringify(byteBudgetResult),'utf8')<=byteBudgetReq.budget.max_bytes&&['partial','error'].includes(byteBudgetResult.status),String(Buffer.byteLength(JSON.stringify(byteBudgetResult),'utf8')));

const compact=compileAIContext(result,{maxBytes:200000,maxTokens:6000,tokenizerId:'heuristic-chars-per-token/4',encoding:'symbol_table_v1'});
test('AI context compact emitted',compact.encoding==='symbol_table_v1'&&compact.context.symbol_table&&compact.context.atoms.length>0);
test('AI context stays in byte budget',compact.budget.used_bytes<=compact.budget.max_bytes,`${compact.budget.used_bytes}`);
const expanded=expandCompactContext(compact);
test('compact payload expands',expanded.encoding==='expanded_json'&&!expanded.context.symbol_table);

const tiny=compileAIContext(result,{maxBytes:1800,encoding:'expanded_json'});
test('AI compiler reports budget truncation',tiny.completeness.truncated===true&&tiny.omissions.some(x=>x.kind==='ai_context_budget'));

const caps=referenceV8Capabilities();
test('v8 capabilities preserve v6/v7',caps.compatibility.reads.includes('kristal_state/6.0')&&caps.compatibility.reads.includes('kristall/7.0'));
test('v8 capabilities advertise exact query',caps.capabilities.ai_query.modes.includes('semantic_slice')&&caps.capabilities.ai_query.pagination===true);

if(failed)process.exit(1);
console.log('Kristal v8 reference tests: PASS');
