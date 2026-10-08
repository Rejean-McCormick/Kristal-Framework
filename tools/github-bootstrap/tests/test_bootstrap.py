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
        'framework': {'repository':'acme/Kristal-Framework','ref':SHA},
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
        self.repos={('acme','Kristal-Framework'):{'id':99,'name':'Kristal-Framework','owner':{'login':'acme'},'visibility':'public','default_branch':'main'}}
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

if __name__=='__main__': unittest.main()

class GuiConfigTests(unittest.TestCase):
    def test_gui_render_roundtrip(self):
        from kristal_github_bootstrap.gui import render_config, validate_gui_values
        from kristal_github_bootstrap.core import load_config
        import tempfile
        from pathlib import Path
        vals={
            'owner':'acme','kind':'organization','network_id':'urn:kristal:network:acme',
            'framework_repo':'acme/Kristal-Framework','framework_ref':'a'*40,
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
