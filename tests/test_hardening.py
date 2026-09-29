"""rc.2 regressions. Synthetic inputs only; local filesystem and HTTP boundaries."""
from test_runtime import Base
from omnxlib.core import *
from omnxlib import console as cs, projection as pj, migration as mg, tasks, project, audit, launcher
from omnxlib.decisions import Store, check
from omnxlib.privacy import redact
from omnxlib import previews
from unittest.mock import patch
import unittest, threading, urllib.request, urllib.error, http.cookiejar, time, copy, tempfile, os, json

class DecisionHardening(Base):
    def setUp(self):super().setUp();self.init()
    def make(self,**kw):return Store(self.fs).create({'type':'product','title':'Escolha humana','question':'A ou B?','options':[{'id':'a','label':'A','description':'Opção A'},{'id':'b','label':'B','description':'Opção B'}],**kw})
    def approve(self,x,option='a'):return Store(self.fs).update(x['decision']['id'],x['sha256'],status='approved',selected_option=option,authority_ref='user:synthetic')
    def test_R02_approved_choice_immutable(self):
        x=self.approve(self.make());before=self.fs.read('.omnx/decisions/'+x['decision']['id']+'.json')
        self.expect('decision_terminal',lambda:Store(self.fs).update(x['decision']['id'],x['sha256'],selected_option='b'))
        self.assertEqual(before,self.fs.read('.omnx/decisions/'+x['decision']['id']+'.json'))
    def test_R03_create_cannot_approve(self):self.expect('invalid_initial_state',lambda:self.make(status='approved'))
    def test_R03_create_cannot_forge_actor(self):self.expect('managed_decision_fields',lambda:self.make(authority_ref='human'))
    def test_create_cannot_forge_history(self):self.expect('managed_decision_fields',lambda:self.make(history=[]))
    def test_create_cannot_forge_selected_option(self):self.expect('managed_decision_fields',lambda:self.make(selected_option='b'))
    def test_create_duplicate_options(self):self.expect('duplicate_option',lambda:self.make(options=[{'id':'a','label':'A','description':'A'}]*2))
    def test_recommendation_must_exist(self):self.expect('invalid_option',lambda:self.make(recommended_option='c'))
    def test_approval_requires_explicit_choice(self):
        x=self.make();self.expect('missing_option',lambda:Store(self.fs).update(x['decision']['id'],x['sha256'],status='approved',authority_ref='user:test'))
    def test_choice_without_approval_rejected(self):
        x=self.make();self.expect('empty_update',lambda:Store(self.fs).update(x['decision']['id'],x['sha256'],selected_option='a'))
    def test_R04_missing_hash_is_captured(self):
        self.fs.write('docs/ux/proposals/UX-x/tela.html',b'<h1>old</h1>',None)
        x=self.make(type='ux',subject_ref='docs/ux/proposals/UX-x/tela.html')
        self.assertEqual(x['decision']['subject_sha256'],digest(b'<h1>old</h1>'))
        self.fs.write(x['decision']['subject_ref'],b'<h1>new</h1>',x['decision']['subject_sha256'])
        self.expect('stale_subject',lambda:self.approve(x))
    def test_asset_change_invalidates_binding(self):
        self.fs.write('docs/ux/proposals/UX-x/tela.html',b'<link rel="stylesheet" href="screen.css">',None)
        self.fs.write('docs/ux/proposals/UX-x/screen.css',b'p { color:red; }',None)
        x=self.make(type='ux',subject_ref='docs/ux/proposals/UX-x/tela.html')
        self.fs.write('docs/ux/proposals/UX-x/screen.css',b'p { color:blue; }',self.fs.hash('docs/ux/proposals/UX-x/screen.css'))
        self.expect('stale_subject',lambda:self.approve(x))
    def test_wrong_supplied_subject_hash(self):
        self.fs.write('docs/ux/proposals/UX-x/tela.html',b'new',None)
        self.expect('stale_subject',lambda:self.make(subject_ref='docs/ux/proposals/UX-x/tela.html',subject_sha256='f'*64))
    def test_subject_secret_ref_denied(self):self.expect('protected_subject',lambda:self.make(subject_ref='.env'))
    def test_missing_subject_not_silently_unbound(self):self.expect('missing_subject',lambda:self.make(subject_ref='docs/no.md'))
    def test_requested_changes_require_feedback(self):
        x=self.make();self.expect('missing_feedback',lambda:Store(self.fs).update(x['decision']['id'],x['sha256'],status='changes_requested'))
    def test_cannot_approve_before_revision(self):
        x=self.make();x=Store(self.fs).update(x['decision']['id'],x['sha256'],status='changes_requested',feedback='Mude a proposta.')
        self.expect('revision_required',lambda:self.approve(x))
    def test_revision_preserves_feedback_history(self):
        x=self.make();x=Store(self.fs).update(x['decision']['id'],x['sha256'],status='changes_requested',feedback='Mude a proposta.')
        x=Store(self.fs).revise(x['decision']['id'],x['sha256'],{'question':'Agora A ou B?'})
        x=self.approve(x);self.assertEqual(x['decision']['revision'],4)
        self.assertEqual(x['decision']['history'][1]['previous']['status'],'changes_requested')
        self.assertEqual(x['decision']['feedback'],['Mude a proposta.']);check(x['decision'])
    def test_history_tampering_rejected(self):
        x=self.approve(self.make());d=copy.deepcopy(x['decision']);d['history'][0]['previous']['question']='silent overwrite'
        self.expect('decision_history_invalid',lambda:check(d))
    def test_terminal_feedback_cannot_rewrite(self):
        x=self.approve(self.make());self.expect('decision_terminal',lambda:Store(self.fs).update(x['decision']['id'],x['sha256'],feedback='new'))
    def test_supersede_preserves_original_choice(self):
        x=self.approve(self.make());x=Store(self.fs).update(x['decision']['id'],x['sha256'],status='superseded',authority_ref='user:new-decision')
        self.assertEqual(x['decision']['history'][-1]['previous']['selected_option'],'a')
    def test_R12_hash_derived_from_displayed_bytes(self):
        x=self.make();did=x['decision']['id'];rel='.omnx/decisions/'+did+'.json';original=self.fs.read(rel)
        real_read=self.fs.read
        def racing_read(path,*args,**kwargs):
            raw=real_read(path,*args,**kwargs)
            if path==rel:
                other=load_data(raw);other['question']='A pergunta mudou';(self.fs.root/rel).write_bytes(json_bytes(other))
            return raw
        with patch.object(self.fs,'read',side_effect=racing_read):
            _,displayed,sha=Store(self.fs).read_record(did)
        self.assertEqual(displayed['question'],'A ou B?');self.assertEqual(sha,digest(original))
        self.expect('stale_state',lambda:Store(self.fs).update(did,sha,status='approved',selected_option='a',authority_ref='user:test'))
    def test_legacy_requires_reconfirmation(self):
        x=self.make();d=x['decision'];rel='.omnx/decisions/'+d['id']+'.json'
        legacy={k:v for k,v in d.items() if k not in ('history','subject_manifest','legacy_record')};legacy.update(schema_version=1,status='approved',selected_option='b')
        self.fs.write(rel,json_bytes(legacy),x['sha256']);sha=self.fs.hash(rel)
        self.expect('legacy_decision',lambda:Store(self.fs).update(d['id'],sha,feedback='a'))
        new=Store(self.fs).revise(d['id'],sha,{})
        self.assertEqual(new['decision']['status'],'pending');self.assertIsNone(new['decision']['authority_ref'])
        self.assertEqual(new['decision']['legacy_record']['data']['status'],'approved')
    def test_task_ref_must_exist(self):self.expect('missing_task',lambda:self.make(task_refs=['TASK-unknown']))

class ProjectionHardening(Base):
    def setUp(self):super().setUp();self.init();pj.clear_cache()
    def test_R05_one_bad_task_does_not_hide_valid(self):
        good=self.task();self.fs.write('.omnx/tasks/TASK-bad.md',b'---\ninvalid',None)
        p=pj.read_project(self.fs.root);self.assertEqual([t['id'] for t in p['tasks']],[good['task']['id']]);self.assertTrue(p['partial'])
    def test_invalid_decision_isolated(self):
        Store(self.fs).create({'title':'Boa','question':'Q?','type':'product'})
        self.fs.write('.omnx/decisions/DEC-bad.json',b'{"bad":',None)
        p=pj.read_project(self.fs.root);self.assertEqual(len(p['decisions']),1);self.assertTrue(p['partial'])
    def test_R08_blocked_in_counts_and_rows(self):
        x=self.task();x=tasks.Store(self.fs).update(x['task']['id'],{'blocked_reason':'Cliente precisa responder'},x['sha256'],transition='blocked')
        p=pj.read_project(self.fs.root);self.assertEqual(p['counts']['by_status']['blocked'],1);self.assertEqual(p['tasks'][0]['status'],'blocked')
    def test_R10_prompt_bounded_no_bodies(self):
        x=self.task();rel='.omnx/tasks/'+x['task']['id']+'.md';m,b=tasks.parse(self.fs.read(rel))
        self.fs.write(rel,tasks.dump(m,'API_SECRET="synthetic-long-value-0123456789"\n'+'a'*100000),self.fs.hash(rel))
        p=pj.read_project(self.fs.root);prompt=cs.prompt_for_task(p,x['task']['id'])
        self.assertLess(len(prompt),2400);self.assertNotIn('synthetic-long-value',prompt);self.assertIn(p['project_id'],prompt);self.assertIn(p['workspace_id'],prompt)
    def test_explain_prompt_is_read_only(self):
        x=self.task();prompt=cs.prompt_for_task(pj.read_project(self.fs.root),x['task']['id'],'explain');self.assertIn('SOMENTE LEITURA',prompt);self.assertIn('sem modificar',prompt)
    def test_R11_unchanged_refresh_no_metadata_read(self):
        self.task();pj.read_project(self.fs.root);before=pj.METRICS['metadata_reads'];pj.read_project(self.fs.root)
        self.assertEqual(before,pj.METRICS['metadata_reads']);self.assertGreater(pj.METRICS['cache_hits'],0)
    def test_R12_projection_does_not_call_separate_hash(self):
        x=self.task();Store(self.fs).create({'title':'Q','question':'Q?','type':'product'})
        with patch.object(RootFS,'hash',side_effect=AssertionError('No separate content/hash reads in projection')):
            p=pj.read_project(self.fs.root)
        self.assertEqual(len(p['tasks']),1);self.assertEqual(len(p['decisions']),1)
    def test_changes_requested_not_waiting_for_user(self):
        x=Store(self.fs).create({'title':'Q','question':'Q?','type':'product'})
        Store(self.fs).update(x['decision']['id'],x['sha256'],status='changes_requested',feedback='Ajuste')
        p=pj.read_project(self.fs.root);self.assertEqual(p['counts']['pending_decisions'],0);self.assertEqual(p['counts']['awaiting_agent'],1)
    def test_future_project_schema_read_only_no_mutation(self):
        rel='.omnx/project.yaml';p=self.fs.data(rel,yaml_ok=True);p['schema_version']=99;raw=json_bytes(p);self.fs.write(rel,raw,self.fs.hash(rel))
        out=pj.read_project(self.fs.root);self.assertTrue(out['read_only']);self.assertEqual(self.fs.read(rel),raw)
    def test_method_update_not_project_health_score(self):
        p=pj.read_project(self.fs.root);p['method_lock']['adopted_packages']['omnx-code']['version']='2.0.0'
        status=cs.version_status(p);self.assertEqual(status['status'],'outdated');self.assertEqual(status['basis'],'installed_bundle_not_remote_check')
    def test_redaction_happens_before_ui_payload(self):
        x=self.task();m,b=tasks.parse(self.fs.read('.omnx/tasks/'+x['task']['id']+'.md'))
        m['title']='ACCESS_TOKEN=syntheticabcdefg1234';self.fs.write('.omnx/tasks/'+m['id']+'.md',tasks.dump(m,b),self.fs.hash('.omnx/tasks/'+m['id']+'.md'))
        self.assertNotIn('syntheticabcdefg1234',json.dumps(pj.read_project(self.fs.root)))
    def test_oversize_item_isolated(self):
        self.task();self.fs.write('.omnx/tasks/TASK-large.md',b'a'*(pj.MAX_METADATA+1),None)
        p=pj.read_project(self.fs.root);self.assertEqual(len(p['tasks']),1);self.assertTrue(p['partial'])

class HTTPHardening(Base):
    def setUp(self):
        super().setUp();self.init();self.old=(cs.CATALOG_DIR,cs.CATALOG);self.cat=tempfile.TemporaryDirectory()
        cs.CATALOG_DIR=Path(self.cat.name)/'catalog';cs.CATALOG=cs.CATALOG_DIR/'projects.json';self.item=cs.register(self.fs.root)
        self.server=cs.ConsoleServer();self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.base=self.server.origin
        self.jar=http.cookiejar.CookieJar();self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(self.jar))
        url=self.server.issue_bootstrap();self.key=url.split('#key=')[1]
        self.csrf=self.send('/api/session',{},headers={'X-OMNX-Bootstrap':self.key},auth=False)['csrf']
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();cs.CATALOG_DIR,cs.CATALOG=self.old;self.cat.cleanup();super().tearDown()
    def send(self,path,body=None,headers=None,auth=True,raw=False):
        h={'Origin':self.base};h.update(headers or {})
        if body is not None:h['Content-Type']='application/json';h.setdefault('X-OMNX-CSRF',self.csrf if auth else '')
        r=urllib.request.Request(self.base+path,data=json_bytes(body) if body is not None else None,headers=h)
        with self.opener.open(r,timeout=5) as response:
            b=response.read();return (b,response.headers) if raw else json.loads(b)
    def fail(self,status,fn):
        with self.assertRaises(urllib.error.HTTPError) as c:fn()
        self.assertEqual(c.exception.code,status);return json.loads(c.exception.read())
    def decision(self,**kwargs):return Store(self.fs).create({'title':'Q','question':'Q?','type':'product',**kwargs})
    def update_body(self,x,**kw):return {'workspace_id':self.item['workspace_id'],'decision_id':x['decision']['id'],'expected_sha256':x['sha256'],'status':'approved','request_id':uuid.uuid4().hex,**kw}
    def test_R07_legacy_arbitrary_preview_route_removed(self):
        self.fs.write('.env',b'SYNTHETIC_SECRET',None);self.fail(404,lambda:self.send('/api/mockup?path=.env'))
    def test_R07_preview_id_cannot_read_env(self):
        self.fs.write('.env',b'SYNTHETIC_SECRET',None)
        self.fail(404,lambda:self.send('/api/preview',{'workspace_id':self.item['workspace_id'],'preview_id':'PRE-'+digest(b'.env')[:24]}))
    def test_preview_rejects_unknown_fields(self):self.fail(400,lambda:self.send('/api/preview',{'workspace_id':self.item['workspace_id'],'path':'.env'}))
    def test_preview_grant_bound_to_files(self):
        self.fs.write('docs/ux/proposals/UX-x/t.html',b'<h1>Preview</h1>',None)
        self.fs.write('.env',b'NO',None)
        r=self.send('/api/preview',{'workspace_id':self.item['workspace_id'],'preview_id':'PRE-'+digest(b'docs/ux/proposals/UX-x/t.html')[:24]})
        url=r['url'];parts=url.split('/',3);self.fail(403,lambda:self.send('/preview/'+parts[2]+'/.env',raw=True))
    def test_preview_changed_after_grant_denied(self):
        rel='docs/ux/proposals/UX-x/t.html';self.fs.write(rel,b'old',None)
        r=self.send('/api/preview',{'workspace_id':self.item['workspace_id'],'preview_id':'PRE-'+digest(rel.encode())[:24]})
        self.fs.write(rel,b'new',self.fs.hash(rel));self.fail(409,lambda:self.send(r['url'],raw=True))
    def test_preview_no_scripts_navigation_or_form_actions(self):
        rel='docs/ux/proposals/UX-x/t.html';self.fs.write(rel,b'<script>globalThis.BAD=1</script><meta http-equiv="refresh" content="0;url=https://evil.example"><form action="https://evil.example"><input><a href="https://evil.example">x</a></form>',None)
        r=self.send('/api/preview',{'workspace_id':self.item['workspace_id'],'preview_id':'PRE-'+digest(rel.encode())[:24]})
        raw,h=self.send(r['url'],raw=True);self.assertNotIn(b'globalThis.BAD',raw);self.assertNotIn(b'https://evil',raw);self.assertIn("script-src 'none'",h['Content-Security-Policy']);self.assertIn('sandbox;',h['Content-Security-Policy'])
    def test_css_network_removed(self):
        x=previews.sanitize_css('@import "https://evil/a.css"; a{background:url(https://evil/a)}','docs/x/a.css','docs/x',{},'g')
        self.assertNotIn('https://evil',x)
    def test_bootstrap_token_one_use(self):self.fail(403,lambda:self.send('/api/session',{},headers={'X-OMNX-Bootstrap':self.key}))
    def test_cookie_is_httponly_strict(self):
        key=self.server.issue_bootstrap().split('#key=')[1];_,h=self.send('/api/session',{},headers={'X-OMNX-Bootstrap':key},raw=True)
        self.assertIn('HttpOnly',h['Set-Cookie']);self.assertIn('SameSite=Strict',h['Set-Cookie'])
    def test_reopening_launcher_does_not_invalidate_first_tab_csrf(self):
        first=self.csrf;key=self.server.issue_bootstrap().split('#key=')[1]
        second=self.send('/api/session',{},headers={'X-OMNX-Bootstrap':key})['csrf']
        self.assertEqual(first,second)
        x=self.decision();r=self.send('/api/decision/update',self.update_body(x),headers={'X-OMNX-CSRF':first})
        self.assertEqual(Store(self.fs).get(x['decision']['id'])[1]['status'],'approved')
    def test_new_browser_session_does_not_share_other_identity(self):
        key=self.server.issue_bootstrap().split('#key=')[1]
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        r=urllib.request.Request(self.base+'/api/session',data=b'{}',headers={'Origin':self.base,'Content-Type':'application/json','X-OMNX-Bootstrap':key})
        with opener.open(r) as response:second=json.load(response)['csrf']
        self.assertNotEqual(self.csrf,second)
    def test_query_token_no_longer_authenticates(self):
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.fail(403,lambda:opener.open(self.base+'/api/projects?token='+self.key))
    def test_csrf_required(self):self.fail(403,lambda:self.send('/api/project/register',{'path':str(self.fs.root)},headers={'X-OMNX-CSRF':''}))
    def test_forged_origin_rejected(self):self.fail(403,lambda:self.send('/api/project/register',{'path':str(self.fs.root)},headers={'Origin':'https://evil.example'}))
    def test_forged_host_rejected(self):self.fail(403,lambda:self.send('/api/projects',headers={'Host':'evil.example'}))
    def test_null_origin_rejected(self):self.fail(403,lambda:self.send('/api/projects',headers={'Origin':'null'}))
    def test_main_csp_blocks_inline_handlers(self):
        raw,h=self.send('/',raw=True);self.assertIn("script-src 'self'",h['Content-Security-Policy']);self.assertNotIn("script-src 'unsafe-inline'",h['Content-Security-Policy'])
    def test_json_duplicate_key_rejected(self):
        r=urllib.request.Request(self.base+'/api/project/register',data=b'{"path":"a","path":"b"}',headers={'Content-Type':'application/json','X-OMNX-CSRF':self.csrf,'Origin':self.base})
        self.fail(400,lambda:self.opener.open(r))
    def test_api_does_not_accept_arbitrary_authority(self):
        x=self.decision();self.fail(400,lambda:self.send('/api/decision/update',self.update_body(x,authority_ref='CEO')))
    def test_critical_decisions_read_only(self):
        for typ in ['risk','operation','release','migration','architecture']:
            with self.subTest(type=typ):
                x=self.decision(type=typ);self.fail(403,lambda:self.send('/api/decision/update',self.update_body(x)))
    def test_stale_approval_through_http(self):
        x=self.decision();Store(self.fs).revise(x['decision']['id'],x['sha256'],{'question':'Nova pergunta'})
        self.fail(409,lambda:self.send('/api/decision/update',self.update_body(x)))
    def test_double_click_idempotent(self):
        x=self.decision();body=self.update_body(x);a=self.send('/api/decision/update',body);b=self.send('/api/decision/update',body)
        self.assertEqual(a['sha256'],b['sha256']);self.assertEqual(Store(self.fs).get(x['decision']['id'])[1]['revision'],2)
    def test_idempotency_key_cannot_change_payload(self):
        x=self.decision();body=self.update_body(x);self.send('/api/decision/update',body);body['status']='rejected'
        self.fail(409,lambda:self.send('/api/decision/update',body))
    def test_decision_not_execution_authorization(self):
        t=self.task('backlog');d=self.decision(task_refs=[t['task']['id']]);self.send('/api/decision/update',self.update_body(d))
        self.assertEqual(tasks.Store(self.fs).get(t['task']['id'])[1]['authorization']['status'],'proposed')
    def test_summary_contains_no_task_bodies(self):
        self.task();r=self.send('/api/projects');self.assertNotIn('tasks',r['projects'][0]);self.assertEqual(r['projects'][0]['counts']['tasks'],1)
    def test_pagination_honest(self):
        for _ in range(5):self.task()
        q=urllib.parse.urlencode({'workspace_id':self.item['workspace_id'],'collection':'tasks','limit':2,'offset':1})
        p=self.send('/api/project?'+q);self.assertEqual(p['total'],5);self.assertEqual(len(p['items']),2)
    def test_task_done_disallowed_on_console(self):
        t=self.task();self.fail(403,lambda:self.send('/api/task/transition',{'workspace_id':self.item['workspace_id'],'task_id':t['task']['id'],'expected_sha256':t['sha256'],'to':'done','request_id':uuid.uuid4().hex}))
    def test_no_arbitrary_asset_file(self):self.fail(403,lambda:self.send('/assets/../../scripts/omnx.py',headers={'Cookie':''}))
    def test_session_expiration(self):
        for s in self.server.sessions.values():s['expires']=0
        self.fail(403,lambda:self.send('/api/projects'))

class CatalogAndRecovery(Base):
    def setUp(self):
        super().setUp();self.init();self.old=(cs.CATALOG_DIR,cs.CATALOG);self.cat=tempfile.TemporaryDirectory();cs.CATALOG_DIR=Path(self.cat.name)/'catalog';cs.CATALOG=cs.CATALOG_DIR/'projects.json'
    def tearDown(self):cs.CATALOG_DIR,cs.CATALOG=self.old;self.cat.cleanup();super().tearDown()
    def test_R06_clones_remain_distinct(self):
        a=cs.register(self.fs.root)
        with tempfile.TemporaryDirectory() as b:
            fs=RootFS(b);fs.write('.omnx/project.yaml',self.fs.read('.omnx/project.yaml'),None);bb=cs.register(fs.root)
            rows=cs._catalog_read()['projects'];self.assertEqual(len(rows),2);self.assertEqual(a['project_id'],bb['project_id']);self.assertNotEqual(a['workspace_id'],bb['workspace_id'])
            self.expect('ambiguous_workspace',lambda:cs.find_workspace(a['project_id']))
    def test_register_repeat_no_duplicate(self):cs.register(self.fs.root);cs.register(self.fs.root);self.assertEqual(len(cs._catalog_read()['projects']),1)
    def test_unregister_does_not_remove_files(self):
        a=cs.register(self.fs.root);before=self.files();cs.unregister(a['workspace_id']);self.assertEqual(before,self.files())
    def test_catalog_malformed_not_overwritten(self):
        cs.CATALOG_DIR.mkdir();cs.CATALOG.write_bytes(b'bad')
        self.expect('invalid_document',lambda:cs.register(self.fs.root));self.assertEqual(cs.CATALOG.read_bytes(),b'bad')
    def test_register_does_not_mutate_project(self):
        before=self.files();cs.register(self.fs.root);self.assertEqual(before,self.files())
    def test_catalog_symlink_denied(self):
        cs.CATALOG_DIR.mkdir();target=Path(self.tmp.name)/'target';target.write_bytes(b'preserve');cs.CATALOG.symlink_to(target)
        self.expect('unsafe_link',lambda:cs.register(self.fs.root));self.assertEqual(target.read_bytes(),b'preserve')
    def test_launch_shortcut_uses_current_python_and_quotes(self):
        with tempfile.TemporaryDirectory(prefix='launcher with space ') as out:
            with patch('platform.system',return_value='Linux'):
                result=launcher.create(out)
                text=Path(result['changed_paths'][0]).read_text();self.assertIn('"'+sys.executable+'"',text);self.assertIn('Terminal=false',text)
                self.expect('stale_state',lambda:launcher.create(out))
    def test_macos_launcher_structure_generated_not_host_homologation(self):
        with tempfile.TemporaryDirectory() as out:
            with patch('platform.system',return_value='Darwin'):r=launcher.create(out)
            p=Path(r['changed_paths'][0]);self.assertTrue((p/'Contents/Info.plist').exists());self.assertIn(sys.executable,(p/'Contents/MacOS/omnx-console').read_text())
    def test_windows_launcher_structure_generated_not_host_homologation(self):
        with tempfile.TemporaryDirectory() as out:
            with patch('platform.system',return_value='Windows'):r=launcher.create(out)
            self.assertIn('DisableDelayedExpansion',Path(r['changed_paths'][0]).read_text())
    def test_launcher_name_injection_rejected(self):self.expect('invalid_launcher_name',lambda:launcher.create(self.tmp.name,'../../pwn'))
    def test_plan_saved_before_journal_can_resume(self):
        with tempfile.TemporaryDirectory() as root:
            fs=RootFS(root);p=mg.make_plan(fs,'user:test','explicit:read')
            def fault(point):
                if point=='plan_saved':raise RuntimeError('synthetic crash')
            with self.assertRaises(RuntimeError):mg.apply(fs,p,p['plan_digest'],fault=fault)
            mg.resume(fs,p['migration_id'],p['plan_digest']);self.assertEqual(mg.status(fs,p['migration_id'])['phase'],'applied')
    def test_rollback_preserves_new_decisions(self):
        with tempfile.TemporaryDirectory() as root:
            fs=RootFS(root);p=mg.make_plan(fs,'user:test','explicit:read');mg.apply(fs,p,p['plan_digest'])
            Store(fs).create({'title':'Q','question':'Q?','type':'product'})
            self.expect('rollback_dependents',lambda:mg.rollback(fs,p['migration_id'],p['plan_digest']))
    def test_gate_blocks_added_failed_control(self):
        r=self.request();a=self.passed(r)
        a['control_results'].append({'control_id':'SEC-OUTPUT-01','origin':'added','assessment':'evaluated','result':'fail','evidence_ids':[a['evidence'][0]['id']],'rationale':'Same response boundary exposes a field.','limitation_code':None})
        g=audit.gate(self.fs,r,a,'merge','local');self.assertEqual(g['decision'],'blocked');self.assertIn('ADDED_CONTROL_FAIL:SEC-OUTPUT-01',g['reasons'])
