import base64, copy, json, unittest

from kristal_github_bootstrap.core import (
    BootstrapError, RepoSpec, desired_repos, validate_config, stable_node_id,
    node_manifest, github_binding, directory_doc, qualify_workflow, publish_workflow,
    apply_account, apply_single_repo, plan_account, repo_readme,
    ACTION_CHECKOUT, ACTION_SETUP_NODE, ACTION_ATTEST,
)

SHA='0123456789abcdef0123456789abcdef01234567'

def cfg(kind='organization', features='best_effort'):
    return {
        'account': {'owner':'acme','kind':kind},
        'network': {'id':'urn:kristal:network:test'},
        'framework': {'repository':'acme/KristalV10','ref':SHA},
        'global': {'create_dotgithub':True,'create_private_profile':True,'create_profile_repository':True},
        'hub': {'repository':'kristal-hub','visibility':'private','identity_key':'root-directory'},
        'policy': {'default_branch':'main'},
        'features': {'immutable_releases':features,'environments':features,'custom_properties':'off','attestations':features},
        'collections': [
            {'name':'kristal-public','identity_key':'public-primary','visibility':'public','role':'collection','collection':'public'},
            {'name':'kristal-private','identity_key':'private-primary','visibility':'private','role':'collection','collection':'private'},
        ],
    }

class FakeClient:
    def __init__(self, login='acme'):
        self.login=login
        self.repos={('acme','KristalV10'):{'id':99,'name':'KristalV10','owner':{'login':'acme'},'visibility':'public','default_branch':'main'}}
        self.files={}; self.calls=[]; self.topics={}; self.immutable=set(); self.envs=set(); self.next_id=100
    def repo(self,owner,name): return self.repos.get((owner,name))
    def create_repo(self,owner,kind,spec):
        self.next_id+=1; d={'id':self.next_id,'name':spec.name,'owner':{'login':owner},'visibility':spec.visibility,'default_branch':'main'}; self.repos[(owner,spec.name)]=d; self.calls.append(('MUTATE','create_repo',spec.name)); return d
    def get_text_file(self,owner,repo,path):
        k=(owner,repo,path)
        if k not in self.files:return None
        return self.files[k], 'sha-'+str(abs(hash(k)))
    def put_text_file(self,owner,repo,path,content,message,branch='main',overwrite_managed=False):
        k=(owner,repo,path); existed=k in self.files
        if existed and not overwrite_managed:return 'kept'
        self.files[k]=content; self.calls.append(('MUTATE','file',repo,path)); return 'updated' if existed else 'created'
    def api(self,method,endpoint,body=None,optional=False):
        self.calls.append((method,endpoint,body))
        if method=='GET' and endpoint=='/user': return {'login':self.login}
        if method=='GET' and '/commits/' in endpoint: return {'sha':endpoint.rsplit('/',1)[-1]}
        if '/contents/' in endpoint:
            owner,repo=endpoint.split('/')[2],endpoint.split('/')[3]; path=endpoint.split('/contents/',1)[1]; k=(owner,repo,path)
            if method=='GET':
                if k not in self.files:return None
                return {'content':base64.b64encode(self.files[k].encode()).decode(),'sha':'abc'}
            if method=='PUT': self.files[k]=base64.b64decode(body['content']).decode(); self.calls.append(('MUTATE','api-file',repo,path)); return {'ok':True}
        if endpoint.endswith('/topics'):
            owner,repo=endpoint.split('/')[2],endpoint.split('/')[3]; k=(owner,repo)
            if method=='GET': return {'names':self.topics.get(k,[])}
            if method=='PUT': self.topics[k]=list(body['names']); self.calls.append(('MUTATE','topics',repo)); return {'names':self.topics[k]}
        if endpoint.endswith('/immutable-releases'):
            owner,repo=endpoint.split('/')[2],endpoint.split('/')[3]; k=(owner,repo)
            if method=='GET': return {'enabled':True} if k in self.immutable else None
            if method=='PUT': self.immutable.add(k); self.calls.append(('MUTATE','immutable',repo)); return None
        if '/environments/production' in endpoint:
            owner,repo=endpoint.split('/')[2],endpoint.split('/')[3]; k=(owner,repo)
            if method=='GET': return {'name':'production'} if k in self.envs else None
            if method=='PUT': self.envs.add(k); self.calls.append(('MUTATE','environment',repo)); return {'name':'production'}
        if method=='GET' and endpoint.startswith('/repos/'):
            owner,repo=endpoint.split('/')[2],endpoint.split('/')[3]; return self.repos.get((owner,repo))
        return {'ok':True}

class Tests(unittest.TestCase):
    def test_requires_public_and_private(self):
        c=cfg(); c['collections']=c['collections'][:1]
        with self.assertRaises(BootstrapError): validate_config(c)
    def test_refuses_public_hub_with_private_nodes(self):
        c=cfg(); c['hub']['visibility']='public'
        with self.assertRaises(BootstrapError): validate_config(c)
    def test_rejects_floating_framework_ref(self):
        c=cfg(); c['framework']['ref']='main'
        with self.assertRaises(BootstrapError): validate_config(c)
    def test_rejects_repository_name_collisions(self):
        c=cfg(); c['collections'][0]['name']='kristal-hub'
        with self.assertRaises(BootstrapError): validate_config(c)
    def test_internal_visibility_rejected_for_user(self):
        c=cfg('user'); c['collections'][0]['visibility']='internal'
        with self.assertRaises(BootstrapError): validate_config(c)
    def test_stable_identity_uses_identity_key_not_repo_name(self):
        c=cfg(); a=next(x for x in desired_repos(c) if x.name=='kristal-public')
        c2=copy.deepcopy(c); c2['collections'][0]['name']='renamed-public'; b=next(x for x in desired_repos(c2) if x.name=='renamed-public')
        self.assertEqual(a.node_id,b.node_id)
    def test_binding_has_no_credentials_and_only_effective_surfaces(self):
        s=RepoSpec('x','private','collection','urn:uuid:1')
        b=github_binding('acme','organization',s,effective={})
        text=json.dumps(b).lower()
        for forbidden in ('token','password','private_key','secret'): self.assertNotIn(forbidden,text)
        self.assertNotIn('activation',b['surfaces']); self.assertNotIn('attestation',b['surfaces']); self.assertNotIn('materialization',b['surfaces'])
        b2=github_binding('acme','organization',s,effective={'environment':'present','attestations':'required'})
        self.assertIn('activation',b2['surfaces']); self.assertIn('attestation',b2['surfaces'])
    def test_public_readme_does_not_name_private_hub(self):
        s=RepoSpec('x','public','collection','urn:uuid:1')
        self.assertNotIn('kristal-hub',repo_readme(s,'kristal-hub'))
    def test_workflows_pin_every_external_action_and_framework(self):
        w=qualify_workflow(cfg()); p=publish_workflow(cfg())
        self.assertIn(ACTION_CHECKOUT,w); self.assertIn(ACTION_SETUP_NODE,w); self.assertIn(f'ref: {SHA}',w)
        self.assertIn(ACTION_ATTEST,p); self.assertNotIn('actions/checkout@v4',w+p); self.assertNotIn('actions/setup-node@v4',w+p)
    def test_publish_workflow_uses_env_for_input_and_draft_targeted_release(self):
        w=publish_workflow(cfg())
        self.assertIn('STATE_FILE: ${{ inputs.state_file }}',w)
        self.assertNotIn('verify-state-v9 "${{ inputs.state_file }}"',w)
        self.assertIn('build-publication-bundle-v10',w); self.assertIn('--draft --target "$GITHUB_SHA"',w); self.assertIn('verify-publication-bundle-v10',w)
        self.assertIn('validate-read-surface.py validate-root', w)
        self.assertIn('state-only compatibility validation', w)
        self.assertNotIn('    environment: production',w)  # best-effort feature is not a claimed gate
        c=cfg(); c['features']['environments']='required'; self.assertIn('    environment: production',publish_workflow(c))
    def test_user_account_owner_mismatch_is_blocked(self):
        c=cfg('user'); f=FakeClient(login='other')
        with self.assertRaises(BootstrapError): apply_account(f,c)
    def test_account_apply_is_convergent_for_managed_files_and_features(self):
        c=cfg(features='best_effort'); f=FakeClient(); apply_account(f,c); before=len([x for x in f.calls if x and x[0]=='MUTATE']); apply_account(f,c); after=len([x for x in f.calls if x and x[0]=='MUTATE'])
        # custom properties are off; all observed repo features/files/topics are already converged.
        self.assertEqual(before,after)
    def test_human_edit_of_managed_file_is_conflict_not_overwrite(self):
        c=cfg(features='off'); f=FakeClient(); apply_account(f,c)
        k=('acme','kristal-public','.kristal/node.json'); f.files[k]=f.files[k].replace('"collection"','"gateway"',1)
        with self.assertRaises(BootstrapError): apply_account(f,c)
    def test_topics_are_merged_not_replaced(self):
        c=cfg(features='off'); f=FakeClient(); f.topics[('acme','kristal-public')]=['human-topic']; apply_account(f,c)
        self.assertIn('human-topic',f.topics[('acme','kristal-public')]); self.assertIn('kristal',f.topics[('acme','kristal-public')])
    def test_dynamic_repo_survives_later_account_reconcile(self):
        c=cfg(features='off'); f=FakeClient(); apply_account(f,c); out=apply_single_repo(f,c,'kristal-chemistry','public','collection','science',True); nid=out['node_id']; apply_account(f,c)
        doc=json.loads(f.files[('acme','kristal-hub','.kristal/directory.json')]); self.assertIn(nid,{e['node_id'] for e in doc['entries']})
    def test_existing_node_identity_is_preserved(self):
        c=cfg(features='off'); f=FakeClient(); apply_account(f,c); k=('acme','kristal-public','.kristal/node.json'); d=json.loads(f.files[k]); d['node_id']='urn:uuid:preserved'; f.files[k]=json.dumps(d,indent=2)+'\n'
        # update bootstrap ledger to represent an intentional prior identity, not a human file conflict
        bs=json.loads(f.files[('acme','kristal-public','.kristal/bootstrap-state.json')]); import hashlib; bs['managed_files']['.kristal/node.json']=hashlib.sha256(f.files[k].encode()).hexdigest(); f.files[('acme','kristal-public','.kristal/bootstrap-state.json')]=json.dumps(bs,indent=2)+'\n'
        apply_account(f,c); root=json.loads(f.files[('acme','kristal-hub','.kristal/directory.json')]); entry=next(e for e in root['entries'] if e['metadata']['repository']=='kristal-public'); self.assertEqual(entry['node_id'],'urn:uuid:preserved')
    def test_plan_can_be_bound_to_observed_state(self):
        c=cfg(features='off'); f=FakeClient(); plan=plan_account(f,c); f.repos[('acme','external-drift')]={'id':999,'visibility':'private'}
        # unrelated repos do not invalidate a plan; desired topology changes do.
        f.repos[('acme','kristal-public')]={'id':123,'visibility':'public','default_branch':'dev'}
        with self.assertRaises(BootstrapError): apply_account(f,c,expected_observed_fingerprint=plan['observed_fingerprint'])


class GuiConfigTests(unittest.TestCase):
    def test_gui_render_roundtrip(self):
        from kristal_github_bootstrap.gui import render_config, validate_gui_values
        from kristal_github_bootstrap.core import load_config
        import tempfile
        from pathlib import Path
        vals={
            'owner':'acme','kind':'organization','network_id':'urn:kristal:network:acme',
            'framework_repo':'acme/KristalV10','framework_ref':'a'*40,
            'hub_repo':'kristal-hub','public_repo':'kristal-public','private_repo':'kristal-private',
            'immutable_releases':'best_effort','environments':'best_effort','custom_properties':'best_effort','attestations':'best_effort',
            'create_private_profile':'true',
        }
        validate_gui_values(vals)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'network.toml'; p.write_text(render_config(vals))
            cfg=load_config(p)
            self.assertEqual(cfg['account']['owner'],'acme')
            self.assertEqual(cfg['framework']['ref'],'a'*40)
            self.assertEqual({c['visibility'] for c in cfg['collections']},{'public','private'})

    def test_gui_rejects_duplicate_repo_names_and_floating_ref(self):
        from kristal_github_bootstrap.gui import validate_gui_values
        vals={
            'owner':'acme','kind':'organization','framework_ref':'main',
            'hub_repo':'same','public_repo':'same','private_repo':'private',
        }
        with self.assertRaises(BootstrapError):
            validate_gui_values(vals)

    def test_gui_operator_defaults(self):
        from kristal_github_bootstrap.gui import (
            DEFAULT_FRAMEWORK_REPO, DEFAULT_FRAMEWORK_SHA, DEFAULT_WINDOWS_CONFIG
        )
        self.assertEqual(DEFAULT_FRAMEWORK_REPO, "Rejean-McCormick/KristalV10")
        self.assertEqual(DEFAULT_FRAMEWORK_SHA, "27c0c7db3d79a4597c1c964fe8281fa35b5f858a")
        self.assertEqual(DEFAULT_WINDOWS_CONFIG, r"C:\mycode\Kristal\network.toml")


class FrameworkPreflightTests(unittest.TestCase):
    def test_framework_preflight_prefers_exact_git_commit_and_reports_resolution(self):
        from kristal_github_bootstrap.core import framework_preflight
        c=cfg(features='off'); f=FakeClient()
        out=framework_preflight(f,c)
        self.assertEqual(out['status'],'ok')
        self.assertTrue(out['ref_resolved'])
        self.assertEqual(out['resolved_sha'],SHA)
        self.assertIn('/git/commits/',out['verification_attempts'][0]['endpoint'])

    def test_plan_exposes_framework_preflight_diagnostics(self):
        c=cfg(features='off'); f=FakeClient()
        plan=plan_account(f,c)
        action=next(a for a in plan['actions'] if a.get('feature')=='framework')
        self.assertEqual(action['status'],'ok')
        self.assertEqual(action['ref'],SHA)
        self.assertTrue(action['ref_resolved'])
        self.assertIn('verification_attempts',action)


if __name__=='__main__': unittest.main()

class LifecycleTests(unittest.TestCase):
    def test_extract_run_id_from_gh_output(self):
        from kristal_github_bootstrap.lifecycle import extract_run_id
        text='✓ Created workflow_dispatch event\nhttps://github.com/acme/repo/actions/runs/37677255910\n'
        self.assertEqual(extract_run_id(text),'37677255910')

    def test_genesis_state_shape(self):
        from kristal_github_bootstrap.lifecycle import build_genesis_state
        s=build_genesis_state('urn:kristal:state:test','public','2026-10-07T00:00:00Z')
        self.assertEqual(s['schema_version'],'9.0')
        self.assertEqual(s['artifact_type'],'kristal_state_snapshot')
        self.assertEqual(s['members'],[])
        self.assertEqual(s['references'],[])
        self.assertEqual(s['logical_commitment']['profile'],'kristal.state-commitment/jcs-sha256-v1')
        self.assertEqual(s['logical_commitment']['digest'],'sha256:'+'0'*64)
        self.assertEqual(s['created_at'],'2026-10-07T00:00:00Z')

    def test_lifecycle_default_workspace(self):
        from kristal_github_bootstrap.gui import DEFAULT_WINDOWS_WORKSPACE
        self.assertEqual(DEFAULT_WINDOWS_WORKSPACE, r'C:\mycode\Kristal')

class ActivationLifecycleTests(unittest.TestCase):
    def test_activation_ref_is_deterministic_and_git_safe(self):
        from kristal_github_bootstrap.lifecycle import activation_ref_name
        a = activation_ref_name('public/stable')
        b = activation_ref_name('public/stable')
        self.assertEqual(a, b)
        self.assertTrue(a.startswith('kristal-activation/public-stable-'))
        self.assertNotIn(' ', a)

    def test_activation_ref_changes_with_channel(self):
        from kristal_github_bootstrap.lifecycle import activation_ref_name
        self.assertNotEqual(activation_ref_name('public/stable'), activation_ref_name('public/canary'))

    def test_same_state_ref_ignores_host_metadata_but_requires_commitment(self):
        from kristal_github_bootstrap.lifecycle import _same_state_ref
        a = {
            'state_ref': 'urn:kristal:state:x',
            'logical_commitment': {'profile': 'kristal.state-commitment/jcs-sha256-v1', 'digest': 'sha256:'+'1'*64},
            'authority_ref': 'urn:a',
        }
        b = {
            'state_ref': 'urn:kristal:state:x',
            'logical_commitment': {'profile': 'kristal.state-commitment/jcs-sha256-v1', 'digest': 'sha256:'+'1'*64},
        }
        c = dict(b)
        c['logical_commitment'] = dict(b['logical_commitment'])
        c['logical_commitment']['digest'] = 'sha256:'+'2'*64
        self.assertTrue(_same_state_ref(a, b))
        self.assertFalse(_same_state_ref(a, c))

class MultiKristalLifecycleTests(unittest.TestCase):
    def test_manager_catalog_local_state_and_collection_path(self):
        import tempfile
        from pathlib import Path
        from kristal_github_bootstrap.lifecycle import (
            manager_entries, inspect_local_kristal, collection_state_relative, default_channel_id,
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            local = root / "My Kristal"
            (local / "build/v9").mkdir(parents=True)
            (local / "kristal.workspace.json").write_text(json.dumps({
                "format":"kristal.local-workspace/3.2.0", "title":"My Kristal", "slug":"my-kristal"
            }), encoding="utf-8")
            state = {
                "schema_version":"9.0", "artifact_type":"kristal_state_snapshot",
                "state_ref":"urn:kristal:state:my-kristal",
                "logical_commitment":{"profile":"kristal.state-commitment/jcs-sha256-v1","digest":"sha256:"+"1"*64},
                "members":[], "references":[], "parents":[]
            }
            (local / "build/v9/state-snapshot.json").write_text(json.dumps(state), encoding="utf-8")
            catalog = root / "kristal-manager.json"
            catalog.write_text(json.dumps({
                "format":"kristal-local-registry/2.0",
                "entries":[{"path":str(local),"title":"My Kristal","slug":"my-kristal","publication_target":"private"}]
            }), encoding="utf-8")
            rows = manager_entries(catalog)
            self.assertEqual(len(rows), 1)
            info = inspect_local_kristal(local, manager_entry=rows[0])
            self.assertEqual(info["state_ref"], "urn:kristal:state:my-kristal")
            self.assertTrue(info["state_path"].endswith("build/v9/state-snapshot.json"))
            self.assertEqual(collection_state_relative(info["slug"]), "kristals/my-kristal/state/state-snapshot.json")
            self.assertEqual(default_channel_id("private", info["slug"]), "private/my-kristal/stable")

    def test_release_selection_is_by_state_ref_not_repo_latest(self):
        from unittest.mock import patch
        from kristal_github_bootstrap.lifecycle import find_release_for_state_ref
        releases = [
            {"tag_name":"kristal-pub-newer","draft":False,"target_commitish":"b"*40},
            {"tag_name":"kristal-pub-wanted","draft":False,"target_commitish":"a"*40},
        ]
        records = {
            "kristal-pub-newer":{"state":{"state_ref":"urn:kristal:state:other"}},
            "kristal-pub-wanted":{"state":{"state_ref":"urn:kristal:state:wanted"}},
        }
        with patch("kristal_github_bootstrap.lifecycle._releases", return_value=releases), \
             patch("kristal_github_bootstrap.lifecycle._release_publication_record", side_effect=lambda o,r,t: records[t]):
            selected = find_release_for_state_ref("acme","collection","urn:kristal:state:wanted")
            self.assertEqual(selected["tag_name"], "kristal-pub-wanted")
            selected_commit = find_release_for_state_ref("acme","collection","urn:kristal:state:wanted",target_commit="a"*40)
            self.assertEqual(selected_commit["tag_name"], "kristal-pub-wanted")

    def test_render_config_defaults_to_kristal_v10(self):
        from kristal_github_bootstrap.gui import render_config
        text = render_config({
            "owner":"acme", "kind":"user", "network_id":"urn:kristal:network:acme",
            "framework_repo":"", "framework_ref":"a"*40,
            "hub_repo":"kristal-hub", "public_repo":"kristal-public", "private_repo":"kristal-private",
            "immutable_releases":"off", "environments":"off", "custom_properties":"off", "attestations":"off",
            "create_private_profile":"false",
        })
        self.assertIn('repository = "acme/KristalV10"', text)

class LocalStateStagingTests(unittest.TestCase):
    def test_stage_local_state_preserves_exact_bytes(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from kristal_github_bootstrap.lifecycle import stage_local_state
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.json"
            collection = root / "collection"; collection.mkdir()
            raw = b'{\n  "schema_version": "9.0",\n  "artifact_type": "kristal_state_snapshot",\n  "state_ref": "urn:kristal:state:x",\n  "logical_commitment": {"profile":"p","digest":"sha256:' + b'1'*64 + b'"}\n}\n'
            source.write_bytes(raw)
            with patch("kristal_github_bootstrap.lifecycle._json_command", return_value={"ok":True,"commitment":{"profile":"p","digest":"sha256:"+"1"*64}}):
                out = stage_local_state(collection, source, "kristals/x/state/state-snapshot.json", Path("cli.mjs"))
            target = collection / "kristals/x/state/state-snapshot.json"
            self.assertEqual(target.read_bytes(), raw)
            self.assertTrue(out["changed"])
            self.assertEqual(out["state_ref"], "urn:kristal:state:x")

class CollectionIngestTests(unittest.TestCase):
    def test_collection_workflow_is_path_scoped_sharded_and_pinned(self):
        from kristal_github_bootstrap.core import collection_ingest_workflow
        w = collection_ingest_workflow(cfg())
        self.assertIn("'kristals/**'", w)
        self.assertIn('validate-read-surface.py validate-index', w)
        self.assertIn('validate-read-surface.py discover', w)
        self.assertIn('validate-read-surface.py validate-shard', w)
        self.assertIn('max-parallel: 8', w)
        self.assertIn('fetch-depth: 0', w)
        self.assertIn(ACTION_CHECKOUT, w)
        self.assertIn(ACTION_SETUP_NODE, w)
        self.assertIn(f'ref: {SHA}', w)

    def test_node_qualification_is_not_triggered_by_every_kristal_sync(self):
        w = qualify_workflow(cfg())
        self.assertIn("- '.kristal/**'", w)
        self.assertIn("- '.github/workflows/kristal-qualify.yml'", w)
        self.assertNotIn("- 'kristals/**'", w)
        self.assertIn('workflow_dispatch:', w)

    def test_collection_apply_installs_ingest_workflow_and_validator_only_on_collections(self):
        from kristal_github_bootstrap.core import seed_node_repo
        c = cfg(features='off'); f = FakeClient()
        # Seed enough fake repositories for direct node seeding.
        for spec in desired_repos(c):
            f.repos[('acme', spec.name)] = {'id':1000, 'name':spec.name, 'owner':{'login':'acme'}, 'visibility':spec.visibility, 'default_branch':'main'}
        public = next(x for x in desired_repos(c) if x.name == 'kristal-public')
        hub = next(x for x in desired_repos(c) if x.name == 'kristal-hub')
        seed_node_repo(f, c, public)
        self.assertIn(('acme','kristal-public','.github/workflows/kristal-ingest.yml'), f.files)
        self.assertIn(('acme','kristal-public','.kristal/tools/validate-read-surface.py'), f.files)
        seed_node_repo(f, c, hub, is_hub=True, all_specs=desired_repos(c))
        self.assertNotIn(('acme','kristal-hub','.github/workflows/kristal-ingest.yml'), f.files)

    def test_collection_validator_accepts_exact_surface_and_rejects_drift(self):
        import hashlib, tempfile
        from pathlib import Path
        from kristal_github_bootstrap import collection_ingest as ci
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            root = repo / 'kristals' / 'zoology'
            (root / 'ai').mkdir(parents=True)
            (root / 'state').mkdir(parents=True)
            (root / '.kristal').mkdir(parents=True)
            (repo / '.kristal-framework' / 'reference/js/bin').mkdir(parents=True)
            fake_cli = repo / '.kristal-framework/reference/js/bin/kristal-ref.mjs'
            fake_cli.write_text("process.exit(0);\n", encoding='utf-8')
            state_commitment = {'profile':'kristal.state-commitment/jcs-sha256-v1','digest':'sha256:'+'1'*64}
            state = {'schema_version':'9.0','artifact_type':'kristal_state_snapshot','state_ref':'urn:kristal:state:zoology','logical_commitment':state_commitment,'members':[],'references':[],'parents':[]}
            (root/'state/state-snapshot.json').write_text(json.dumps(state, separators=(',',':'))+'\n', encoding='utf-8')
            ai_manifest = {'state_ref':state['state_ref'],'state_logical_commitment':state_commitment}
            (root/'AI_MANIFEST.json').write_text(json.dumps(ai_manifest)+'\n', encoding='utf-8')
            (root/'AI_START_HERE.md').write_text('# start\n', encoding='utf-8')
            (root/'README.md').write_text('# Zoology\n', encoding='utf-8')
            # ai/INDEX is itself hosted, but its file list points only to content files.
            indexed = []
            for rel, role in [('README.md','overview'),('state/state-snapshot.json','state_snapshot')]:
                p = root / rel
                indexed.append({'path':rel,'role':role,'size':p.stat().st_size,'sha256':'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()})
            ai_index = {'files':indexed,'materialization_blobs':[]}
            (root/'ai/INDEX.json').write_text(json.dumps(ai_index, separators=(',',':'))+'\n', encoding='utf-8')
            roles = {
                'README.md':'overview','AI_START_HERE.md':'ai_entrypoint','AI_MANIFEST.json':'ai_manifest',
                'ai/INDEX.json':'ai_index','state/state-snapshot.json':'state_snapshot'
            }
            files=[]
            for rel in sorted(roles, key=lambda x: x.encode('utf-8')):
                p=root/rel
                files.append({'path':rel,'role':roles[rel],'size':p.stat().st_size,'sha256':'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()})
            projection = {'format':ci.READ_SURFACE_FORMAT,'slug':'zoology','state_ref':state['state_ref'],'state_logical_commitment':state_commitment,'entrypoint':'AI_START_HERE.md','files':files,'materialization_objects':[]}
            surface_digest='sha256:'+hashlib.sha256(ci._canonicalize(projection).encode()).hexdigest()
            manifest={'format':ci.SYNC_MANIFEST_FORMAT,'read_surface_format':ci.READ_SURFACE_FORMAT,'slug':'zoology','target_root':'kristals/zoology','entrypoint':'AI_START_HERE.md','state_ref':state['state_ref'],'state_logical_commitment':state_commitment,'surface_digest':surface_digest,'file_count':len(files),'total_bytes':sum(x['size'] for x in files),'materialization_object_count':0,'files':files}
            (root/'.kristal/sync-manifest.json').write_text(json.dumps(manifest)+'\n', encoding='utf-8')
            out=ci.validate_surface(repo,'kristals/zoology',fake_cli)
            self.assertEqual(out['result'],'PASS')
            (root/'README.md').write_text('# drift\n', encoding='utf-8')
            with self.assertRaises(ci.ValidationError):
                ci.validate_surface(repo,'kristals/zoology',fake_cli)

    def test_collection_index_digest_matches_manager_contract(self):
        import hashlib, tempfile
        from pathlib import Path
        from kristal_github_bootstrap import collection_ingest as ci
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td); root=repo/'kristals/zoology/.kristal'; root.mkdir(parents=True)
            commitment={'profile':'kristal.state-commitment/jcs-sha256-v1','digest':'sha256:'+'2'*64}
            manifest={'format':ci.SYNC_MANIFEST_FORMAT,'state_ref':'urn:kristal:state:zoology','state_logical_commitment':commitment,'surface_digest':'sha256:'+'3'*64,'entrypoint':'AI_START_HERE.md','file_count':5,'total_bytes':123}
            (root/'sync-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            row={'slug':'zoology','title':'Zoology','path':'kristals/zoology','entrypoint':'kristals/zoology/AI_START_HERE.md','state_ref':manifest['state_ref'],'state_logical_commitment':commitment,'surface_digest':manifest['surface_digest'],'file_count':5,'total_bytes':123,'materialization_object_count':0}
            projection={'format':ci.COLLECTION_INDEX_FORMAT,'kristals':[row]}
            digest='sha256:'+hashlib.sha256(json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(',',':')).encode()).hexdigest()
            index={**projection,'count':1,'index_digest':digest,'note':'derived'}
            (repo/'kristals/index.json').write_text(json.dumps(index), encoding='utf-8')
            self.assertEqual(ci.validate_index(repo)['result'],'PASS')


class CollectionIngestDiscoveryTests(unittest.TestCase):
    def test_validator_or_workflow_change_revalidates_all_indexed_surfaces(self):
        import os, tempfile
        from pathlib import Path
        from unittest.mock import patch
        from kristal_github_bootstrap import collection_ingest as ci
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td); (repo/'kristals').mkdir()
            index={
                'format':ci.COLLECTION_INDEX_FORMAT,
                'count':2,
                'index_digest':'sha256:'+'0'*64,
                'kristals':[
                    {'path':'kristals/a'},
                    {'path':'kristals/b'},
                ],
            }
            # discover_roots only needs the rows; index integrity is checked by the workflow's prior step.
            (repo/'kristals/index.json').write_text(json.dumps(index), encoding='utf-8')
            old=os.environ.get('GITHUB_EVENT_NAME')
            os.environ['GITHUB_EVENT_NAME']='push'
            try:
                with patch('kristal_github_bootstrap.collection_ingest._git_changed_paths', return_value=['.github/workflows/kristal-ingest.yml']):
                    self.assertEqual(ci.discover_roots(repo), ['kristals/a','kristals/b'])
            finally:
                if old is None: os.environ.pop('GITHUB_EVENT_NAME',None)
                else: os.environ['GITHUB_EVENT_NAME']=old
