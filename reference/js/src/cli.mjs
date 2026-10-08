import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { exchangeIdentity, verifyExchange } from './exchange.mjs';
import { buildRuntimePackFromRequest, verifyRuntimePack } from './runtime_pack.mjs';
import { verifySignatureFixture, verifyTrustFixture } from './security.mjs';
import { verifyPortableVector } from './runtime_pack_portable.mjs';
import { verifyReferentRegistry } from './referent_registry.mjs';
import { verifyKnowledgeModelContract } from './knowledge_model_contract.mjs';
import { stateIdentity, verifyKristalState, summarizeKristalState } from './kristal_state.mjs';
import { readJson, printJson, unwrapVector } from './io.mjs';
import { byteFingerprintFromFile, semanticFingerprint } from './v8/common.mjs';
import { inspectArtifact, buildDataset } from './v8/reader.mjs';
import { resolveLexicalization, lexiconMap } from './v8/lexicon.mjs';
import { executeQuery, verifyQueryRequest } from './v8/query.mjs';
import { createQueryIndex, exportQueryIndex } from './v8/query_index.mjs';
import { compileAIContext } from './v8/ai_context.mjs';
import { referenceV8Capabilities } from './v8/capabilities.mjs';
import { logicalArtifactCommitment, stateCommitment, verifyLogicalArtifact, verifyStateSnapshot } from './v9/state.mjs';
import { verifyMaterializationManifest } from './v9/materialization.mjs';
import { referenceV9Capabilities } from './v9/capabilities.mjs';
import { verifyDerivation, verifyExchangeV9, verifyActivation } from './v9/contracts.mjs';
import { publishStateSnapshot, activateChannel } from './v9/lifecycle.mjs';
import { referenceV10Capabilities } from './v10/capabilities.mjs';
import { verifyNodeManifest, verifyHostBinding, verifyPublication, verifyDirectory, verifyGithubBinding } from './v10/contracts.mjs';
import { buildPublicationBundleFromFiles, verifyPublicationBundle } from './v10/publication.mjs';

function die(message, code = 2) {
  process.stderr.write(message + '\n');
  process.exit(code);
}

function requireArg(args, index, label) {
  if (!args[index]) die(`missing ${label}`);
  return args[index];
}

function resultExit(result) {
  printJson(result);
  process.exit(result.ok === false ? 1 : 0);
}

function optionValues(args, flag) {
  const values=[];
  for(let i=0;i<args.length;i++) if(args[i]===flag){ if(!args[i+1])die(`missing value for ${flag}`); values.push(args[i+1]); i++; }
  return values;
}
function optionValue(args, flag, fallback=null) {
  const vals=optionValues(args,flag);return vals.length?vals.at(-1):fallback;
}
function intOption(args,flag,fallback=null){const v=optionValue(args,flag);if(v===null)return fallback;const n=Number(v);if(!Number.isInteger(n))die(`${flag} must be an integer`);return n;}
function writeOrPrint(value,file){if(file){fs.mkdirSync(path.dirname(path.resolve(file)),{recursive:true});fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n','utf8');}else printJson(value);}
function loadArtifacts(paths){return paths.map((file)=>{const doc=readJson(file);return{doc,ref:file,fingerprint:byteFingerprintFromFile(file,file,doc.schema_version)};});}

export async function main(argv = process.argv.slice(2)) {
  const [command, ...args] = argv;
  switch (command) {
    case 'state-id': {
      const file = requireArg(args, 0, 'Kristal State JSON');
      printJson(stateIdentity(readJson(file)));
      return;
    }
    case 'verify-state': {
      const file = requireArg(args, 0, 'Kristal State JSON');
      return resultExit(verifyKristalState(readJson(file), { requireIdentity: args.includes('--require-identity') }));
    }
    case 'summarize-state': {
      const file = requireArg(args, 0, 'Kristal State JSON');
      printJson(summarizeKristalState(readJson(file)));
      return;
    }
    case 'inspect-artifact': {
      const file=requireArg(args,0,'Kristal artifact JSON');
      const result=inspectArtifact(readJson(file));
      printJson({...result,source_fingerprint:byteFingerprintFromFile(file,file)});
      return;
    }
    case 'v8-capabilities': {
      printJson(referenceV8Capabilities());return;
    }
    case 'v9-capabilities': {
      printJson(referenceV9Capabilities());return;
    }
    case 'v10-capabilities': {
      printJson(referenceV10Capabilities());return;
    }
    case 'verify-node-v10': {
      const file=requireArg(args,0,'v10 Node Manifest JSON');return resultExit(verifyNodeManifest(readJson(file)));
    }
    case 'verify-host-binding-v10': {
      const file=requireArg(args,0,'v10 Host Binding JSON');return resultExit(verifyHostBinding(readJson(file)));
    }
    case 'verify-publication-v10': {
      const file=requireArg(args,0,'v10 Publication JSON');return resultExit(verifyPublication(readJson(file)));
    }
    case 'verify-directory-v10': {
      const file=requireArg(args,0,'v10 Directory JSON');return resultExit(verifyDirectory(readJson(file)));
    }
    case 'verify-github-binding-v10': {
      const file=requireArg(args,0,'v10 GitHub Binding JSON');return resultExit(verifyGithubBinding(readJson(file)));
    }
    case 'build-publication-bundle-v10': {
      const stateFile=requireArg(args,0,'v9 State Snapshot JSON');
      const nodeFile=requireArg(args,1,'v10 Node Manifest JSON');
      const bindingFile=requireArg(args,2,'v10 GitHub Binding JSON');
      const outputDir=requireArg(args,3,'output directory');
      printJson(buildPublicationBundleFromFiles(stateFile,nodeFile,bindingFile,outputDir,{sourceCommit:optionValue(args,'--source-commit')}));return;
    }
    case 'verify-publication-bundle-v10': {
      const bundleDir=requireArg(args,0,'publication bundle directory');return resultExit(verifyPublicationBundle(bundleDir));
    }
    case 'logical-commitment-v9': {
      const file=requireArg(args,0,'v9 Logical Artifact JSON');printJson(logicalArtifactCommitment(readJson(file)));return;
    }
    case 'verify-logical-artifact-v9': {
      const file=requireArg(args,0,'v9 Logical Artifact JSON');return resultExit(verifyLogicalArtifact(readJson(file)));
    }
    case 'state-commitment-v9': {
      const file=requireArg(args,0,'v9 State Snapshot JSON');printJson(stateCommitment(readJson(file)));return;
    }
    case 'verify-state-v9': {
      const file=requireArg(args,0,'v9 State Snapshot JSON');return resultExit(verifyStateSnapshot(readJson(file)));
    }
    case 'verify-materialization-v9': {
      const file=requireArg(args,0,'v9 Materialization Manifest JSON');return resultExit(verifyMaterializationManifest(readJson(file)));
    }
    case 'verify-derivation-v9': {
      const file=requireArg(args,0,'v9 Derivation JSON');return resultExit(verifyDerivation(readJson(file)));
    }
    case 'verify-exchange-v9': {
      const file=requireArg(args,0,'v9 Exchange JSON');return resultExit(verifyExchangeV9(readJson(file)));
    }
    case 'verify-activation-v9': {
      const file=requireArg(args,0,'v9 Activation JSON');return resultExit(verifyActivation(readJson(file)));
    }
    case 'publish-state-v9': {
      const file=requireArg(args,0,'v9 State Snapshot JSON');const store=requireArg(args,1,'store directory');printJson(publishStateSnapshot(readJson(file),store));return;
    }
    case 'activate-state-v9': {
      const file=requireArg(args,0,'v9 Activation JSON');const pointer=requireArg(args,1,'activation pointer file');printJson(activateChannel(readJson(file),pointer));return;
    }

    case 'semantic-fingerprint': {
      const file=requireArg(args,0,'Kristal artifact JSON');printJson(semanticFingerprint(readJson(file)));return;
    }
    case 'verify-query-request': {
      const file=requireArg(args,0,'KQP request JSON');return resultExit(verifyQueryRequest(readJson(file)));
    }
    case 'resolve-lexicon': {
      const semanticId=requireArg(args,0,'semantic id');
      const stackFile=requireArg(args,1,'lexicon stack JSON');
      const identitySpace=optionValue(args,'--identity-space','kristall');
      const namespace=optionValue(args,'--namespace');
      const locale=optionValue(args,'--locale');
      const lexiconFiles=optionValues(args,'--lexicon');
      if(!lexiconFiles.length)die('at least one --lexicon <file> is required');
      const ref={identity_space:identitySpace,id:semanticId,...(namespace?{namespace}:{})};
      const result=resolveLexicalization(ref,readJson(stackFile),lexiconMap(lexiconFiles.map(readJson)),{requestedLocale:locale??undefined});
      printJson(result);return;
    }
    case 'query-v8': {
      const requestFile=requireArg(args,0,'KQP request JSON');
      const artifacts=optionValues(args,'--artifact');if(!artifacts.length)die('at least one --artifact <file> is required');
      const dataset=buildDataset(loadArtifacts(artifacts));
      const result=executeQuery(readJson(requestFile),dataset);
      writeOrPrint(result,optionValue(args,'--output'));return;
    }
    case 'build-query-index': {
      const artifacts=optionValues(args,'--artifact');if(!artifacts.length)die('at least one --artifact <file> is required');
      const outputDir=optionValue(args,'--output-dir');if(!outputDir)die('--output-dir is required');
      const dataset=buildDataset(loadArtifacts(artifacts));const exported=exportQueryIndex(createQueryIndex(dataset),dataset,{indexId:optionValue(args,'--index-id','KQI-reference')});
      fs.mkdirSync(outputDir,{recursive:true});
      for(const [name,payload] of Object.entries(exported.payloads))fs.writeFileSync(path.join(outputDir,name),JSON.stringify(payload,null,2)+'\n','utf8');
      fs.writeFileSync(path.join(outputDir,'manifest.json'),JSON.stringify(exported.manifest,null,2)+'\n','utf8');
      printJson({ok:true,manifest:path.join(outputDir,'manifest.json'),index_count:exported.manifest.indexes.length});return;
    }
    case 'compile-ai-context': {
      const resultFile=requireArg(args,0,'KQP result JSON');
      const maxBytes=intOption(args,'--max-bytes',131072);const maxTokens=intOption(args,'--max-tokens');
      const tokenizerId=optionValue(args,'--tokenizer-id',maxTokens!==null?'heuristic-chars-per-token/4':null);
      const encoding=optionValue(args,'--encoding','expanded_json');
      if(!['expanded_json','symbol_table_v1'].includes(encoding))die('--encoding must be expanded_json or symbol_table_v1');
      const bundle=compileAIContext(readJson(resultFile),{maxBytes,maxTokens,tokenizerId,encoding});
      writeOrPrint(bundle,optionValue(args,'--output'));return;
    }
    case 'exchange-id': {
      const file = requireArg(args, 0, 'input JSON');
      const doc = unwrapVector(readJson(file));
      printJson(exchangeIdentity(doc));
      return;
    }
    case 'verify-exchange': {
      const file = requireArg(args, 0, 'input JSON');
      const doc = unwrapVector(readJson(file));
      return resultExit(verifyExchange(doc));
    }
    case 'build-runtime-pack': {
      const file = requireArg(args, 0, 'input JSON');
      const outputDir = requireArg(args, 1, 'output directory');
      const result = buildRuntimePackFromRequest(readJson(file), outputDir);
      printJson(result);
      return;
    }
    case 'verify-runtime-pack': {
      const manifestPath = requireArg(args, 0, 'manifest JSON');
      const payloadDir = requireArg(args, 1, 'payload directory');
      return resultExit(verifyRuntimePack(readJson(manifestPath), payloadDir));
    }
    case 'verify-runtime-profile': {
      const file = requireArg(args, 0, 'portable vector JSON');
      const doc = readJson(file);
      const results = (doc.vectors ?? []).map((vector) => ({ id: vector.id, ...verifyPortableVector(vector) }));
      const out = {
        ok: doc.profile === 'kristal.v5:runtime-pack-portable-conformance@1' && results.every((r) => r.ok),
        profile: doc.profile,
        results,
      };
      return resultExit(out);
    }
    case 'verify-signature': {
      const file = requireArg(args, 0, 'signature fixture JSON');
      return resultExit(verifySignatureFixture(readJson(file)));
    }
    case 'verify-trust': {
      const file = requireArg(args, 0, 'trust fixture JSON');
      return resultExit(verifyTrustFixture(readJson(file)));
    }
    case 'verify-referent-registry': {
      const file = requireArg(args, 0, 'Referent Registry JSON');
      return resultExit(verifyReferentRegistry(readJson(file)));
    }
    case 'verify-knowledge-model-contract': {
      const file = requireArg(args, 0, 'knowledge-model contract JSON');
      const frameworkRoot = args[1] ? path.resolve(args[1]) : path.resolve(path.dirname(file));
      return resultExit(verifyKnowledgeModelContract(readJson(file), frameworkRoot));
    }
    case 'self-test': {
      const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'kristal-ref-selftest-'));
      try {
        const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
        const message = Buffer.from('kristal-reference-self-test', 'utf8');
        const signature = crypto.sign(null, message, privateKey);
        const fixture = {
          algorithm: 'ed25519',
          public_key_pem: publicKey.export({ type: 'spki', format: 'pem' }),
          message_base64: message.toString('base64'),
          signature_base64: signature.toString('base64'),
        };
        const result = verifySignatureFixture(fixture);
        if (!result.ok) throw new Error(result.issues.join('; '));
        const caps=referenceV8Capabilities();
        if(caps.schema_version!=='8.0')throw new Error('v8 capabilities self-test failed');
        const caps9=referenceV9Capabilities();
        if(caps9.schema_version!=='9.0')throw new Error('v9 capabilities self-test failed');
        printJson({ ok: true, self_test: 'PASS', v8:true, v9:true });
      } finally {
        fs.rmSync(tmp, { recursive: true, force: true });
      }
      return;
    }
    default:
      die('usage: kristal-ref <state-id|verify-state|summarize-state|inspect-artifact|v8-capabilities|v9-capabilities|logical-commitment-v9|verify-logical-artifact-v9|state-commitment-v9|verify-state-v9|verify-materialization-v9|verify-derivation-v9|verify-exchange-v9|verify-activation-v9|publish-state-v9|activate-state-v9|semantic-fingerprint|verify-query-request|resolve-lexicon|query-v8|build-query-index|compile-ai-context|exchange-id|verify-exchange|build-runtime-pack|verify-runtime-pack|verify-runtime-profile|verify-signature|verify-trust|verify-referent-registry|verify-knowledge-model-contract|self-test> ...');
  }
}
