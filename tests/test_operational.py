"""Process-level recovery, concurrency and package-budget regressions."""
import os, sys, json, time, tempfile, subprocess, threading, concurrent.futures, unittest
from pathlib import Path
from unittest.mock import patch
PACKAGE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PACKAGE/'scripts'));sys.dont_write_bytecode=True
from omnxlib.core import *
from omnxlib import console as cs, launcher, tasks, migration as mg, project
from omnxlib.decisions import Store
from test_runtime import Base

class Concurrency(Base):
    def setUp(self):super().setUp();self.init()
    def test_two_writers_same_decision_only_one_approval(self):
        x=Store(self.fs).create({'title':'Escolha','question':'A ou B?','type':'product','options':[{'id':'a','label':'A','description':''},{'id':'b','label':'B','description':''}]})
        barrier=threading.Barrier(2)
        def vote(option):
            barrier.wait()
            try:Store(self.fs).update(x['decision']['id'],x['sha256'],status='approved',selected_option=option,authority_ref='test:concurrent');return 'ok'
            except MethodError as e:return e.code
        with concurrent.futures.ThreadPoolExecutor(2) as pool:out=list(pool.map(vote,['a','b']))
        self.assertEqual(out.count('ok'),1);self.assertEqual(len(out),2);self.assertTrue(any(v in ('stale_state','locked') for v in out))
        self.assertEqual(len(Store(self.fs).get(x['decision']['id'])[1]['history']),1)
    def test_two_task_writers_do_not_lose_update(self):
        x=self.task();barrier=threading.Barrier(2)
        def change(priority):
            barrier.wait()
            try:tasks.Store(self.fs).update(x['task']['id'],{'priority':priority},x['sha256']);return 'ok'
            except MethodError as e:return e.code
        with concurrent.futures.ThreadPoolExecutor(2) as pool:out=list(pool.map(change,['high','low']))
        self.assertEqual(out.count('ok'),1);self.assertEqual(len(out),2);self.assertTrue(any(v in ('stale_state','locked') for v in out))
    def test_catalog_registration_concurrent_processes(self):
        with tempfile.TemporaryDirectory() as home:
            roots=[]
            for i in range(6):p=Path(home)/f'project{i}';p.mkdir();roots.append(p)
            env={**os.environ,'OMNX_CONSOLE_HOME':str(Path(home)/'catalog'),'PYTHONDONTWRITEBYTECODE':'1'}
            children=[subprocess.Popen([sys.executable,str(PACKAGE/'scripts/omnx.py'),'--root',str(p),'console','register'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env) for p in roots]
            for child in children:
                o,e=child.communicate(timeout=15);self.assertEqual(child.returncode,0,e.decode())
            cat=json.loads((Path(home)/'catalog/projects.json').read_text());self.assertEqual(len(cat['projects']),6)
    def test_decision_write_failure_preserves_previous_record(self):
        x=Store(self.fs).create({'title':'Q','question':'Q?','type':'product'});rel='.omnx/decisions/'+x['decision']['id']+'.json';before=self.fs.read(rel)
        original=RootFS.write
        def full(fs,path,*args,**kwargs):
            if path==rel:raise OSError(28,'synthetic full disk')
            return original(fs,path,*args,**kwargs)
        with patch.object(RootFS,'write',full):
            with self.assertRaises(OSError):Store(self.fs).update(x['decision']['id'],x['sha256'],status='approved',authority_ref='test:fixture')
        self.assertEqual(self.fs.read(rel),before)
    def test_future_decision_schema_preserved_and_readonly(self):
        from omnxlib import projection
        rel='.omnx/decisions/DEC-future.json';raw=json_bytes({'schema_version':999,'id':'DEC-future','opaque':'keep'})
        self.fs.write(rel,raw,None);out=projection.read_project(self.fs.root)
        self.assertTrue(out['partial']);self.assertEqual(self.fs.read(rel),raw)

class DeltaDependencies(Base):
    def setUp(self):super().setUp();self.init()
    def test_unrelated_invalid_record_does_not_freeze_authorized_edit(self):
        x=self.task();self.fs.write('.omnx/tasks/TASK-invalid.md',b'---\nbroken',None)
        y=tasks.Store(self.fs).update(x['task']['id'],{'priority':'high'},x['sha256'])
        self.assertEqual(y['task']['priority'],'high')
    def test_new_task_does_not_read_unrelated_invalid_record(self):
        self.fs.write('.omnx/tasks/TASK-invalid.md',b'---\nbroken',None)
        self.assertEqual(self.task()['task']['status'],'ready')
    def test_invalid_required_dependency_still_blocks(self):
        x=self.task();rel='.omnx/tasks/'+x['task']['id']+'.md';self.fs.write(rel,b'---\nbroken',self.fs.hash(rel))
        with self.assertRaises(MethodError):tasks.Store(self.fs).create({'title':'Depends on broken task','acceptance':['Test'],'depends_on':[x['task']['id']]},'Explicit fixture scope.')
    def test_change_follows_only_its_dependency_closure(self):
        x=self.task()
        with patch.object(tasks.Store,'entries',side_effect=AssertionError('No full-store read for an independent mutation')):
            y=tasks.Store(self.fs).update(x['task']['id'],{'priority':'low'},x['sha256'])
        self.assertEqual(y['task']['priority'],'low')

class LauncherProcesses(unittest.TestCase):
    def call(self,home,*args):
        env={**os.environ,'OMNX_CONSOLE_HOME':str(home),'PYTHONDONTWRITEBYTECODE':'1'}
        p=subprocess.run([sys.executable,str(PACKAGE/'scripts/omnx.py'),*args],env=env,capture_output=True,text=True,timeout=18)
        self.assertEqual(p.returncode,0,p.stderr+' '+p.stdout);return json.loads(p.stdout)
    def test_open_twice_reuses_process_and_stop_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            h=Path(tmp)/'catalog'
            try:
                a=self.call(h,'console','open','--no-browser');b=self.call(h,'console','open','--no-browser')
                self.assertFalse(a['reused']);self.assertTrue(b['reused']);self.assertEqual(a['pid'],b['pid']);self.assertNotEqual(a['console_url'],b['console_url'])
                d=json.loads(next(h.glob('instance-*.json')).read_text());health=launcher._http(d['port'],'/api/health');self.assertEqual(health['instance_id'],d['instance_id'])
            finally:
                self.call(h,'console','stop')
                deadline=time.monotonic()+5
                while time.monotonic()<deadline and list(h.glob('instance-*.json')):time.sleep(.1)
            self.assertFalse(list(h.glob('instance-*.json')))
            self.call(h,'console','stop')
    def test_invalid_descriptor_does_not_probe_all_pids(self):
        with tempfile.TemporaryDirectory() as tmp:
            fs=RootFS(tmp);fs.write('instance.json',json_bytes({'schema_version':1,'pid':-1,'port':9001,'launcher_token':'x'*40,'instance_id':'bad'}),None)
            with patch.object(os,'kill',side_effect=AssertionError('must not inspect negative pid')):
                with self.assertRaises(MethodError) as e:launcher._existing(fs,'instance.json')
            self.assertEqual(e.exception.code,'invalid_instance')

class Assets(unittest.TestCase):
    def test_runtime_js_has_no_inline_execution_or_html_interpolation(self):
        js=(PACKAGE/'console/assets/app.js').read_text();self.assertNotIn('innerHTML',js);self.assertNotIn('eval(',js);self.assertNotIn('new Function',js)
        self.assertIn("$$('.nav').forEach",js);self.assertNotIn("$('.nav').forEach",js.replace("$$('.nav').forEach",''))
        self.assertIn("'blocked'",js);self.assertIn("'cancelled'",js)
    def test_skill_budget(self):
        core=(PACKAGE/'SKILL.md').read_text();self.assertLessEqual(sum(bool(x.strip()) for x in core.splitlines()),400)
    def test_console_manifest_decision_support_is_consistent(self):
        m=json.loads((PACKAGE/'console/console-manifest.json').read_text());self.assertEqual(m['decision_schema_write_versions'],[2]);self.assertEqual(m['decision_schema_read_versions'],[1,2]);self.assertIn(2,m['decision_schema_versions'])
