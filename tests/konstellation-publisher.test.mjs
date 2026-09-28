import {test} from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {publish,sha} from '../tools/publish_konstellation_pack.mjs';
const read=n=>JSON.parse(fs.readFileSync(new URL('../examples/konstellation/'+n+'.json',import.meta.url)));
const options=output=>({catalog:read('catalog'),assertions:read('assertions'),policy:read('policy'),exchangeId:'sha256:'+'a'.repeat(64),artifactStatus:'working',createdAt:'2026-09-27T00:00:00Z',output});
test('publisher preserves metadata and pins every file reproducibly',t=>{const root=fs.mkdtempSync(path.resolve('.publisher-test-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
const a=publish(options(path.join(root,'a'))),b=publish(options(path.join(root,'b')));assert.deepEqual(fs.readFileSync(a.directory+'/manifest.json'),fs.readFileSync(b.directory+'/manifest.json'));
const m=JSON.parse(fs.readFileSync(a.directory+'/manifest.json'));for(const f of m.files){const bytes=fs.readFileSync(a.directory+'/'+f.path);assert.equal(bytes.length,f.size_bytes);assert.equal(sha(bytes),f.sha256);}assert.throws(()=>publish(options(a.directory)),/overwrite/);
});
test('publisher refuses missing recognition, missing trace source and duplicates without output',t=>{const root=fs.mkdtempSync(path.resolve('.publisher-test-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
for(const modify of [o=>delete o.assertions[0].recognitionStatus,o=>o.assertions[0].sourceRefs=['unknown'],o=>o.assertions.push(o.assertions[0])]){const o=options(path.join(root,'invalid'));modify(o);assert.throws(()=>publish(o));assert(!fs.existsSync(o.output));}});
