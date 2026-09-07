"""Console tests: local projection, decisions, prompts and safe preview discovery."""
import os, sys, tempfile, unittest, threading, urllib.request, urllib.error, json
from pathlib import Path
PACKAGE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PACKAGE/'scripts'));sys.dont_write_bytecode=True
from omnxlib.core import *
from omnxlib import migration as mg, tasks, console
from http.server import ThreadingHTTPServer
from omnxlib.decisions import Store as DecisionStore

class ConsoleBase(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.fs=RootFS(self.tmp.name)
        p=mg.make_plan(self.fs,'user:test','explicit-skill:test');mg.apply(self.fs,p,p['plan_digest'])
    def tearDown(self):self.tmp.cleanup()
    def task(self):
        return tasks.Store(self.fs).create({'title':'Fila inteligente','status':'backlog','authorization':{'status':'proposed','basis_ref':None},'acceptance':['Fila respeita a prioridade.'],'priority':'high'},'Implementar somente a fila desta fixture.')
    def decision(self,task_id=None):
        return DecisionStore(self.fs).create({'type':'ux','title':'Aprovar fila','question':'Aprovar a nova organização visual?','task_refs':[task_id] if task_id else [],'options':[{'id':'a','label':'Aprovar layout','description':'Usar a proposta atual.'}],'recommended_option':'a'})

class DecisionTests(ConsoleBase):
    def test_create_pending(self):self.assertEqual(self.decision()['decision']['status'],'pending')
    def test_approval_requires_authority(self):
        x=self.decision();s=DecisionStore(self.fs)
        with self.assertRaises(MethodError) as c:s.update(x['decision']['id'],x['sha256'],status='approved')
        self.assertEqual(c.exception.code,'missing_authority')
    def test_stale_approval_rejected(self):
        x=self.decision();s=DecisionStore(self.fs);s.update(x['decision']['id'],x['sha256'],feedback='Mude o título.')
        with self.assertRaises(MethodError) as c:s.update(x['decision']['id'],x['sha256'],status='approved',selected_option='a',authority_ref='product-owner:test')
        self.assertEqual(c.exception.code,'stale_state')
    def test_approval_does_not_change_task(self):
        t=self.task();d=self.decision(t['task']['id']);DecisionStore(self.fs).update(d['decision']['id'],d['sha256'],status='approved',selected_option='a',authority_ref='product-owner:test')
        _,m,_=tasks.Store(self.fs).get(t['task']['id']);self.assertEqual(m['status'],'backlog');self.assertEqual(m['authorization']['status'],'proposed')
    def test_subject_change_blocks_approval(self):
        self.fs.write('docs/ux/proposals/UX-x/screen.html',b'<h1>v1</h1>',None)
        x=DecisionStore(self.fs).create({'type':'ux','title':'Aprovar tela','question':'Aprovar?', 'subject_ref':'docs/ux/proposals/UX-x/screen.html','subject_sha256':self.fs.hash('docs/ux/proposals/UX-x/screen.html')})
        self.fs.write('docs/ux/proposals/UX-x/screen.html',b'<h1>v2</h1>',self.fs.hash('docs/ux/proposals/UX-x/screen.html'))
        with self.assertRaises(MethodError) as c:DecisionStore(self.fs).update(x['decision']['id'],x['sha256'],status='approved',selected_option='a',authority_ref='product-owner:test')
        self.assertEqual(c.exception.code,'stale_subject')

    def test_terminal_not_reopened(self):
        x=self.decision();s=DecisionStore(self.fs);x=s.update(x['decision']['id'],x['sha256'],status='approved',selected_option='a',authority_ref='product-owner:test')
        with self.assertRaises(MethodError) as c:s.update(x['decision']['id'],x['sha256'],status='pending')
        self.assertEqual(c.exception.code,'decision_terminal')

class ProjectionTests(ConsoleBase):
    def test_project_projection(self):
        t=self.task();self.decision(t['task']['id']);p=console._read_project(Path(self.tmp.name));self.assertEqual(len(p['tasks']),1);self.assertEqual(len(p['decisions']),1)
    def test_prompt_is_deterministic_and_no_deploy(self):
        t=self.task();self.decision(t['task']['id']);p=console._read_project(Path(self.tmp.name));a=console.prompt_for_task(p,t['task']['id']);b=console.prompt_for_task(p,t['task']['id']);self.assertEqual(a,b);self.assertIn('Não faça deploy',a);self.assertNotIn('Fila respeita a prioridade',a);self.assertIn(p['project_id'],a);self.assertIn('NÃO IMPLEMENTAR',a)
    def test_mockup_image_discovered(self):
        self.fs.write('docs/ux/proposals/UX-fixture/screen.png',b'PNG',None);p=console._read_project(Path(self.tmp.name));self.assertEqual(p['mockups'][0]['path'],'docs/ux/proposals/UX-fixture/screen.png')
    def test_outside_symlink_not_discovered(self):
        outside=Path(self.tmp.name).parent/'omnx-outside-mockup.txt';outside.write_text('x')
        base=self.fs.root/'docs'/'ux'/'proposals'/'UX-x';base.mkdir(parents=True,exist_ok=True);(base/'bad.png').symlink_to(outside)
        p=console._read_project(Path(self.tmp.name));self.assertFalse(any(m['name']=='bad.png' for m in p['mockups']))
        outside.unlink()
    def test_overview_version_difference(self):
        p=console._read_project(Path(self.tmp.name));p['method_lock']={'adopted_packages':{'omnx-code':{'version':'0.0.1'}}};o=console.overview([p]);self.assertEqual(o['outdated_projects'],1)

class CatalogTests(unittest.TestCase):
    def test_catalog_can_register_disjoint_paths(self):
        # Isolate HOME so this test never touches the real user catalog.
        old_dir,old_cat=console.CATALOG_DIR,console.CATALOG
        with tempfile.TemporaryDirectory() as h,tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            try:
                console.CATALOG_DIR=Path(h)/'.omnx-console';console.CATALOG=console.CATALOG_DIR/'projects.json'
                ia=console.register(Path(a));ib=console.register(Path(b));rows=console._catalog_read()['projects']
                self.assertEqual({x['path'] for x in rows},{str(Path(a).resolve()),str(Path(b).resolve())});self.assertNotEqual(ia['project_id'],ib['project_id'])
            finally:console.CATALOG_DIR,console.CATALOG=old_dir,old_cat

class HTTPTests(ConsoleBase):
    def setUp(self):
        super().setUp()
        self.old_dir,self.old_cat=console.CATALOG_DIR,console.CATALOG
        self.cat=tempfile.TemporaryDirectory();console.CATALOG_DIR=Path(self.cat.name)/'.omnx-console';console.CATALOG=console.CATALOG_DIR/'projects.json'
        console.register(Path(self.tmp.name))
        self.server=console.ConsoleServer(('127.0.0.1',0))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'
        import http.cookiejar
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        key=self.server.issue_bootstrap().split('#key=')[1]
        req=urllib.request.Request(self.base+'/api/session',data=b'{}',headers={'Content-Type':'application/json','X-OMNX-Bootstrap':key,'Origin':self.base})
        self.csrf=json.loads(self.opener.open(req).read())['csrf']
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)
        console.CATALOG_DIR,console.CATALOG=self.old_dir,self.old_cat;self.cat.cleanup();super().tearDown()
    def test_api_requires_token(self):
        with self.assertRaises(urllib.error.HTTPError) as c:urllib.request.urlopen(self.base+'/api/projects')
        self.assertEqual(c.exception.code,403)
    def test_api_projects_with_token(self):
        r=urllib.request.Request(self.base+'/api/projects');d=json.loads(self.opener.open(r).read());self.assertEqual(d['overview']['projects'],1)
    def test_mutation_rejects_foreign_origin(self):
        body=json.dumps({'path':self.tmp.name}).encode();r=urllib.request.Request(self.base+'/api/project/register',data=body,method='POST',headers={'Content-Type':'application/json','X-OMNX-CSRF':self.csrf,'Origin':'https://evil.example'})
        with self.assertRaises(urllib.error.HTTPError) as c:self.opener.open(r)
        self.assertEqual(c.exception.code,403)
