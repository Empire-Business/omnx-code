"""Local fixtures for host lifecycle, Console launch state, model policy and updates."""
import concurrent.futures
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

PACKAGE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PACKAGE/'scripts'));sys.dont_write_bytecode=True
from omnxlib.core import *
from omnxlib import automation, console, model_policy, previews, projection, tasks, updates, launcher
from test_runtime import Base

class HostLifecycle(Base):
    def setUp(self):super().setUp();self.init()
    def payload(self,event='UserPromptSubmit',**extra):
        return {'cwd':str(self.fs.root),'session_id':'fixture-session-1','hook_event_name':event,**extra}
    def journal(self,host='codex',session='fixture-session-1'):
        session_hash,_=automation.session_identity(host,session)
        return self.fs.data(automation._path(self.fs,host,session_hash))
    def test_clear_implementation_creates_canonical_task_and_minimal_journal(self):
        p=self.payload(prompt='Implement a small, verifiable local change.',turn_id='turn-1',model='codex-model-test')
        out=automation.handle_payload('codex','UserPromptSubmit',p,open_console=False)
        self.assertTrue(out['tracked']);task=tasks.Store(self.fs).read_record(out['task_id'])[1]
        self.assertEqual(task['status'],'in_progress');self.assertEqual(task['authorization']['basis_ref'].split(':')[0],'host-prompt')
        self.assertEqual(task['model_policy']['effective_model'],'codex-model-test')
        j=self.journal();self.assertEqual(j['task_id'],task['id']);self.assertNotIn('prompt',json.dumps(j));self.assertEqual(len(j['events']),1)
    def test_read_only_prompt_does_not_create_task_or_console_state(self):
        out=automation.handle_payload('codex','UserPromptSubmit',self.payload(prompt='How does this project work?'),open_console=False)
        self.assertFalse(out['tracked']);self.assertEqual(tasks.Store(self.fs).entries(),[])
        self.assertFalse(self.fs.path('.omnx/local/automation').exists())
    def test_duplicate_hook_is_idempotent(self):
        p=self.payload(prompt='Fix the reproducible fixture issue.',turn_id='turn-1')
        first=automation.handle_payload('codex','UserPromptSubmit',p,open_console=False)
        second=automation.handle_payload('codex','UserPromptSubmit',p,open_console=False)
        self.assertEqual(first['task_id'],second['task_id']);self.assertEqual(len(tasks.Store(self.fs).entries()),1);self.assertEqual(len(self.journal()['events']),1)
    def test_console_launch_is_once_and_failed_browser_does_not_lose_task(self):
        p=self.payload(prompt='Implement a bounded local change.',turn_id='turn-1')
        with patch.object(automation.subprocess,'Popen',side_effect=OSError('synthetic headless launcher')):
            first=automation.handle_payload('codex','UserPromptSubmit',p)
            second=automation.handle_payload('codex','UserPromptSubmit',p)
        self.assertTrue(first['tracked']);self.assertEqual(first['task_id'],second['task_id'])
        journal=self.journal();self.assertTrue(journal['console_attempted']);self.assertEqual(journal['console_server_status'],'unavailable')
        self.assertEqual(len(tasks.Store(self.fs).entries()),1)
    def test_launcher_reports_browser_failure_and_unconfirmed_client(self):
        with tempfile.TemporaryDirectory() as catalog:
            cat=Path(catalog);descriptor={'pid':123,'port':34567,'instance_id':'fixture-instance','launcher_token':'x'*40}
            launch={'url':'http://127.0.0.1:34567/#key=single-use','instance_id':'fixture-instance','workspace_id':'WSP-'+'a'*24,'task_id':None}
            with patch.object(console,'CATALOG_DIR',cat),patch.object(console,'CATALOG',cat/'projects.json'),patch.object(launcher,'_existing',return_value=descriptor),patch.object(launcher,'_http',side_effect=[launch,{'client_connected_count':0}]),patch.object(launcher.webbrowser,'open',return_value=False):
                out=launcher.open_console(self.fs.root)
        self.assertEqual(out['server_status'],'reused');self.assertEqual(out['browser_status'],'unavailable')
        self.assertEqual(out['client_status'],'not_confirmed');self.assertNotIn('Console aberto',out['summary'])
    def test_parallel_sessions_and_replay_keep_tasks_separate(self):
        def start(session):
            p={**self.payload(prompt='Implement one bounded local change.',turn_id='turn-1'),'session_id':session}
            return automation.handle_payload('codex','UserPromptSubmit',p,open_console=False)['task_id']
        with concurrent.futures.ThreadPoolExecutor(2) as pool:ids=list(pool.map(start,['session-a','session-b']))
        self.assertEqual(len(set(ids)),2);self.assertEqual(len(tasks.Store(self.fs).entries()),2)
    def test_same_host_session_in_two_worktrees_keeps_local_journals(self):
        with tempfile.TemporaryDirectory() as clone:
            other=RootFS(clone)
            other.write('.omnx/project.yaml',self.fs.read('.omnx/project.yaml'),None)
            other.write('.omnx/method.lock.json',self.fs.read('.omnx/method.lock.json'),None)
            other.write('AGENTS.md',self.fs.read('AGENTS.md'),None)
            same={'prompt':'Implement one bounded local change.','turn_id':'turn-1','session_id':'shared-host-session'}
            a=automation.handle_payload('codex','UserPromptSubmit',{**same,'cwd':str(self.fs.root)},open_console=False)
            b=automation.handle_payload('codex','UserPromptSubmit',{**same,'cwd':str(other.root)},open_console=False)
            self.assertTrue(a['tracked'] and b['tracked']);self.assertEqual(a['task_id'],b['task_id'])
            one=automation._path(self.fs,'codex',automation.session_identity('codex','shared-host-session')[0])
            two=automation._path(other,'codex',automation.session_identity('codex','shared-host-session')[0])
            self.assertNotEqual(one,two);self.assertTrue(self.fs.path(one).exists());self.assertTrue(other.path(two).exists())
    def test_interruption_checkpoint_and_canonical_status_mirror(self):
        start=automation.handle_payload('codex','UserPromptSubmit',self.payload(prompt='Implement a safe fixture change.',turn_id='turn-1'),open_console=False)
        interrupted=automation.handle_payload('codex','Interrupt',self.payload('Interrupt',turn_id='turn-1'),open_console=False)
        self.assertEqual(interrupted['status'],'ok');self.assertTrue(self.fs.path(interrupted['checkpoint'][0]).exists())
        journal=self.journal();self.assertEqual(journal['state'],'interrupted');self.assertEqual(journal['task_id'],start['task_id'])
        _,task,_,sha=tasks.Store(self.fs).read_record(start['task_id'])
        tasks.Store(self.fs).update(task['id'],{'blocked_reason':'Waiting for a defined input.'},sha,transition='blocked')
        journal=self.journal();self.assertEqual(journal['stage'],'blocked');self.assertEqual(journal['state'],'active')
    def test_stale_signal_is_not_presented_as_live_activity(self):
        start=automation.handle_payload('codex','UserPromptSubmit',self.payload(prompt='Create a bounded local fixture.',turn_id='turn-1'),open_console=False)
        rel=automation._path(self.fs,'codex',automation.session_identity('codex','fixture-session-1')[0]);j,sha=automation._read(self.fs,rel);j['last_signal_at']='2020-01-01T00:00:00+00:00'
        self.fs.write(rel,json_bytes(j),sha)
        view=automation.activity_for_task(self.fs,start['task_id']);self.assertFalse(view['fresh']);self.assertEqual(view['state'],'stale');self.assertIn('Sem atividade',view['signal'])
    def test_model_profiles_escalate_for_risk_and_use_scripts_for_determinism(self):
        config,_=model_policy.read(self.fs)
        self.assertEqual(model_policy.choose(risk='low',ambiguity='low',verification='script',reasoning_needed=False,configured=config)['profile'],'deterministic')
        self.assertEqual(model_policy.choose(risk='critical',ambiguity='low',verification='objective',reasoning_needed=True,configured=config)['profile'],'advanced')
        configured=model_policy.configure(self.fs,'economical','configured-model','low')
        rec=model_policy.choose(risk='low',ambiguity='low',verification='objective',reasoning_needed=True,configured=configured['policy'])
        self.assertEqual(rec['requested_model'],'configured-model');self.assertEqual(rec['effective_status'],'not_observed');self.assertEqual(rec['cost_status'],'unknown')
    def test_hook_installation_preserves_user_hooks_and_is_idempotent(self):
        original={'description':'user hooks','hooks':{'UserPromptSubmit':[{'hooks':[{'type':'command','command':'user-hook'}]}]}}
        self.fs.write('.codex/hooks.json',json_bytes(original),None)
        agents_hash=self.fs.hash('AGENTS.md')
        first=automation.install_hooks(self.fs,'codex',agents_hash,True)
        installed=load_data(self.fs.read('.codex/hooks.json'))
        self.assertEqual(installed['hooks']['UserPromptSubmit'][0]['hooks'][0]['command'],'user-hook')
        self.assertEqual(len(installed['hooks']['UserPromptSubmit']),2)
        second=automation.install_hooks(self.fs,'codex',agents_hash,True);self.assertFalse(second['changed_paths'])
        removed=automation.install_hooks(self.fs,'codex',self.fs.hash('AGENTS.md'),True,remove=True)
        self.assertTrue(removed['changed_paths']);self.assertEqual(self.fs.data('.codex/hooks.json'),original)
    def test_claude_hooks_use_local_settings_and_preserve_other_values(self):
        original={'theme':'dark','hooks':{'Stop':[{'hooks':[{'type':'command','command':'existing'}]}]}}
        self.fs.write('.claude/settings.local.json',json_bytes(original),None)
        automation.install_hooks(self.fs,'claude',self.fs.hash('AGENTS.md'),True)
        saved=self.fs.data('.claude/settings.local.json')
        self.assertEqual(saved['theme'],'dark');self.assertEqual(saved['hooks']['Stop'][0]['hooks'][0]['command'],'existing')
        self.assertTrue(any('--managed-by omnx' in h['command'] for g in saved['hooks']['UserPromptSubmit'] for h in g['hooks']))
    def test_png_inspection_reports_pixels_without_guessing_viewport(self):
        raw=b'\x89PNG\r\n\x1a\n'+(13).to_bytes(4,'big')+b'IHDR'+(1600).to_bytes(4,'big')+(900).to_bytes(4,'big')+bytes([8,2,0,0,0])+b'crc!'
        self.fs.write('docs/ux/proposals/current.png',raw,None)
        out=previews.inspect_png(self.fs,'docs/ux/proposals/current.png')
        self.assertEqual((out['width'],out['height']),(1600,900));self.assertEqual(out['possible_crop'],'unknown');self.assertEqual(out['css_viewport'],'not_inferred')
        with self.assertRaises(MethodError):previews.inspect_png(self.fs,'/etc/passwd')

class UpdaterFixtures(Base):
    def setUp(self):super().setUp();self.init()
    def archive(self,version='99.0.0',project_schema=1):
        con='1.2.0-rc.1'
        files={'SKILL.md':b'# candidate\n','manifest.json':json_bytes({'name':'omnx-code','version':version,'audit_contract_versions':['2.0'],'project_schema_version':project_schema,'console':{'version':con,'project_schema_versions':[project_schema]}}),'console/console-manifest.json':json_bytes({'name':'omnx-console','version':con,'project_schema_versions':[project_schema]})}
        files['integrity.json']=json_bytes({'algorithm':'sha256','files':{p:digest(b) for p,b in files.items()}})
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            for path,raw in files.items():z.writestr('omnx-code/'+path,raw)
        return out.getvalue()
    def test_default_update_policy_is_disabled_and_offline(self):
        with patch.object(updates,'_http_json',side_effect=AssertionError('network must not run')):
            out=updates.auto_check(self.fs)
        self.assertEqual(out['status'],'disabled')
    def test_consent_required_and_stable_is_default(self):
        with self.assertRaises(MethodError):updates.configure(self.fs,True)
        out=updates.configure(self.fs,True,consent=True)
        self.assertEqual(out['policy']['channel'],'stable');self.assertTrue(out['policy']['enabled'])
        consented=out['policy']['consented_at'];changed=updates.configure(self.fs,True,channel='rc')
        self.assertEqual(changed['policy']['consented_at'],consented);self.assertEqual(changed['policy']['channel'],'rc')
    def test_concurrent_update_check_reports_in_progress_without_network(self):
        updates.configure(self.fs,True,consent=True)
        with metadata_lock(self.fs,'updates'),patch.object(updates,'_http_json',side_effect=AssertionError('another check owns the lock')):
            out=updates.auto_check(self.fs,force=True)
        self.assertEqual(out['status'],'in_progress');self.assertEqual(out['update_state'],None)
    def test_channel_selection_keeps_rc_out_of_stable(self):
        release={'tag_name':'v99.0.0-rc.1','prerelease':True,'draft':False}
        self.assertIsNone(updates._select_release([release],'stable','1.0.0'))
        self.assertEqual(updates._select_release([release],'rc','1.0.0'),release)
    def test_no_new_release_keeps_installed_version(self):
        updates.configure(self.fs,True,consent=True)
        with patch.object(updates,'_http_json',return_value=json_bytes([])):out=updates.auto_check(self.fs,force=True)
        self.assertEqual(out['update_state']['status'],'no_update')
        self.assertEqual(out['update_state']['installed_version'],'2.2.0-rc.1')
    def test_timeout_marks_unavailable_and_preserves_runtime(self):
        updates.configure(self.fs,True,consent=True)
        with patch.object(updates,'_http_json',side_effect=TimeoutError()):out=updates.auto_check(self.fs,force=True)
        self.assertEqual(out['status'],'warning');self.assertEqual(out['update_state']['status'],'unavailable')
        self.assertEqual(out['update_state']['installed_version'],'2.2.0-rc.1')
    def test_incompatible_project_schema_is_not_staged(self):
        updates.configure(self.fs,True,consent=True)
        archive=self.archive(project_schema=2);sha=digest(archive);version='99.0.0'
        release={'tag_name':'v'+version,'prerelease':False,'draft':False,'assets':[{'name':'omnx-code-'+version+'.zip','browser_download_url':'https://github.com/Empire-Business/omnx-code/releases/download/v'+version+'/omnx-code-'+version+'.zip','digest':'sha256:'+sha}]}
        with patch.object(updates,'_http_json',side_effect=[json_bytes([release]),archive]):out=updates.auto_check(self.fs,force=True)
        self.assertEqual(out['update_state']['status'],'incompatible')
        self.assertFalse(self.fs.path('.omnx/local/method-updates').exists())
    def test_stage_candidate_without_activating_current_package(self):
        updates.configure(self.fs,True,channel='stable',consent=True)
        archive=self.archive();sha=digest(archive);version='99.0.0'
        release={'tag_name':'v'+version,'prerelease':False,'draft':False,'assets':[{'name':'omnx-code-'+version+'.zip','browser_download_url':'https://github.com/Empire-Business/omnx-code/releases/download/v'+version+'/omnx-code-'+version+'.zip','digest':'sha256:'+sha}]}
        with patch.object(updates,'_http_json',side_effect=[json_bytes([release]),archive]):out=updates.auto_check(self.fs,force=True)
        state=out['update_state'];self.assertEqual(state['status'],'staged');self.assertEqual(state['candidate_version'],version);self.assertEqual(state['activation'],'manual_host_selection_required')
        self.assertTrue(self.fs.path(state['stage_path']+'/manifest.json').exists());self.assertEqual(load_data((PACKAGE/'manifest.json').read_bytes())['version'],'2.2.0-rc.1')
    def test_bad_digest_fails_without_activation(self):
        updates.configure(self.fs,True,consent=True)
        version='99.0.0';release={'tag_name':'v'+version,'prerelease':False,'draft':False,'assets':[{'name':'omnx-code-'+version+'.zip','browser_download_url':'https://github.com/Empire-Business/omnx-code/releases/download/v'+version+'/omnx-code-'+version+'.zip','digest':'sha256:'+'0'*64}]}
        with patch.object(updates,'_http_json',side_effect=[json_bytes([release]),self.archive()]):out=updates.auto_check(self.fs,force=True)
        self.assertEqual(out['status'],'warning');self.assertEqual(out['update_state']['status'],'unavailable')
        self.assertFalse(self.fs.path('.omnx/local/method-updates').exists())

if __name__=='__main__':unittest.main()
