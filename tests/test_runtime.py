"""Deterministic tests with synthetic local fixtures; no real host/application audit."""
import unittest
import tempfile
import subprocess
import os
import sys
import json
import copy
import threading
import time
import zipfile
import io
from pathlib import Path

PACKAGE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PACKAGE/'scripts'))
sys.dont_write_bytecode=True
from omnxlib.core import *
from omnxlib import migration as mg, project as pr, tasks as ts, audit as au, distribution as dist, sessions

class Base(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.fs=RootFS(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def init(self):
        p=mg.make_plan(self.fs,'user:test-adoption','explicit-skill:canonical-read');mg.apply(self.fs,p,p['plan_digest']);return p
    def task(self,status='ready'):
        return ts.Store(self.fs).create({'title':'Objetivo sintético','status':status,'authorization':{'status':'authorized' if status=='ready' else 'proposed','basis_ref':'user:synthetic-scope' if status=='ready' else None},'acceptance':['Resultado esperado verificável.']},'Somente fixture local. Não publicar.')
    def expect(self,code,fn):
        with self.assertRaises(MethodError) as c:fn()
        self.assertEqual(c.exception.code,code)
    def files(self):return {p.relative_to(self.fs.root).as_posix():p.read_bytes() for p in self.fs.root.rglob('*') if p.is_file()}
    def legacy(self):
        self.fs.write('CLAUDE.md',b'# Local rule\r\nNever deploy automatically.\r\n',None)
        self.fs.write('AGENTS.md',b'# Existing rule\nKeep user data.\n',None)
        self.fs.write('src/app.py',b'untouched = True\n',None)
        paths=['CLAUDE.md','AGENTS.md'];mappings=[]
        combined=pr.AGENTS.encode()+b'\n'
        for path in paths:
            raw=self.fs.read(path);combined+=raw+b'\n'
            for b in mg.blocks(raw):
                mappings.append({'source_path':path,'block_id':b['id'],'block_sha256':b['sha256'],'category':'instruction','treatment':'preserve','destination':'AGENTS.md','reason':'Preservar regra operacional customizada.','decision_ref':None})
        resolutions={'source_paths':paths,'mappings':mappings,'writes':{'AGENTS.md':combined.decode()}}
        return mg.make_plan(self.fs,'user:legacy-migration','explicit-skill:AGENTS-reviewed',resolutions=resolutions)
    def request(self,controls=None):
        if self.fs.read('src/input.py') is None:self.fs.write('src/input.py',b'def handle(x): return x\n',None)
        return au.make_request(self.fs,['src/input.py'],controls or ['SEC-INPUT-01'],['input'],'Revisão sintética local')
    def passed(self,r):
        a=au.response_template(r)
        a['execution_status']='completed';a['surface_discovery_status']='completed';a['unassessed_surfaces']=[];a['limitations']=[]
        for i,row in enumerate(a['control_results']):
            eid='EV-test-'+str(i)
            row.update(assessment='evaluated',result='pass',evidence_ids=[eid],rationale='Evidência sintética do teste deste runtime.',limitation_code=None)
            a['evidence'].append({'id':eid,'kind':'test','reference':'test-runtime:synthetic-test','result':'pass','environment':'local','observed_at':now(),'summary':'Fixture sintética local; não auditoria real.'})
        return a

class ParserAndFilesystem(Base):
    def test_json_duplicate(self):self.expect('duplicate_key',lambda:load_data('{"role":1,"role":2}'))
    def test_yaml_duplicate(self):self.expect('duplicate_key',lambda:load_data('role: one\nrole: two',yaml_ok=True))
    def test_yaml_alias(self):self.expect('yaml_alias',lambda:load_data('a: &x [1]\nb: *x',yaml_ok=True))
    def test_yaml_executable_tag(self):self.expect('invalid_document',lambda:load_data('!!python/object/apply:os.system ["touch nope"]',yaml_ok=True))
    def test_json_nonfinite(self):self.expect('invalid_number',lambda:load_data('{"x":NaN}'))
    def test_timestamp_without_zone(self):self.expect('invalid_time',lambda:timestamp('2026-09-06T12:00:00'))
    def test_yaml_timestamp_stays_string(self):self.assertIsInstance(load_data('date: 2026-09-06',yaml_ok=True)['date'],str)
    def test_size_limit(self):self.expect('document_limit',lambda:load_data(b' '* (MAX_DOCUMENT+1)))
    def test_deep_yaml(self):self.expect('document_limit',lambda:load_data('['*60+'0'+']'*60,yaml_ok=True))
    def test_duplicate_non_string_yaml(self):self.expect('invalid_key',lambda:load_data('1: value',yaml_ok=True))
    def test_path_traversal(self):self.expect('invalid_path',lambda:self.fs.write('../escape',b'x',None))
    def test_absolute_path(self):self.expect('invalid_path',lambda:self.fs.read('/etc/passwd'))
    def test_windows_device(self):self.expect('invalid_path',lambda:portable_path('docs/CON.md'))
    def test_unicode_normalization(self):self.expect('invalid_path',lambda:portable_path('docs/cafe\u0301.md'))
    def test_symlink_rejected(self):
        outside=Path(self.tmp.name).parent/'not-written-by-test'
        (self.fs.root/'link').symlink_to(outside);self.expect('unsafe_link',lambda:self.fs.read('link'))
    def test_hardlink_rejected(self):
        self.fs.write('original',b'x',None);os.link(self.fs.root/'original',self.fs.root/'linked');self.expect('unsafe_link',lambda:self.fs.read('linked'))
    def test_file_obstructs_directory(self):
        self.fs.write('docs',b'x',None);self.expect('path_conflict',lambda:self.fs.write('docs/PRD.md',b'x',None))
    def test_cas(self):
        self.fs.write('file',b'one',None);self.expect('stale_state',lambda:self.fs.write('file',b'two',digest(b'other')));self.assertEqual(self.fs.read('file'),b'one')
    def test_lock_contention(self):
        with metadata_lock(self.fs):self.expect('locked',lambda:self._lock_once())
    def _lock_once(self):
        with metadata_lock(self.fs):pass
    def test_lock_released(self):
        with metadata_lock(self.fs):pass
        self._lock_once()
    def test_unknown_schema_keyword(self):self.expect('unsupported_schema',lambda:validate({}, {'unevaluatedProperties':False}))
    def test_schema_bool_not_int(self):self.expect('schema_validation',lambda:validate(True,{'type':'integer'}))

class TaskTests(Base):
    def setUp(self):super().setUp();self.init()
    def test_proposed_not_ready(self):
        x=self.task('backlog');self.expect('unauthorized_task',lambda:ts.Store(self.fs).update(x['task']['id'],{},x['sha256'],transition='ready'))
    def test_explicit_authorization(self):
        x=self.task('backlog');s=ts.Store(self.fs);x=s.update(x['task']['id'],{'authorization':{'status':'authorized','basis_ref':'user:approve'}},x['sha256'],authority_ref='user:approve');x=s.update(x['task']['id'],{},x['sha256'],transition='ready');self.assertEqual(x['task']['status'],'ready')
    def test_authorization_change_requires_origin(self):
        x=self.task('backlog');self.expect('missing_authority',lambda:ts.Store(self.fs).update(x['task']['id'],{'authorization':{'status':'authorized','basis_ref':'user:approve'}},x['sha256']))
    def test_owner_required(self):
        x=self.task();self.expect('missing_owner',lambda:ts.Store(self.fs).update(x['task']['id'],{},x['sha256'],transition='in_progress'))
    def test_invalid_transition(self):
        x=self.task();self.expect('invalid_transition',lambda:ts.Store(self.fs).update(x['task']['id'],{},x['sha256'],transition='done'))
    def test_cas_task(self):
        x=self.task();s=ts.Store(self.fs);s.update(x['task']['id'],{'title':'Changed'},x['sha256']);self.expect('stale_state',lambda:s.update(x['task']['id'],{'title':'Lost'},x['sha256']))
    def test_cycle(self):
        a=self.task();b=self.task();s=ts.Store(self.fs);a=s.update(a['task']['id'],{'depends_on':[b['task']['id']]},a['sha256']);self.expect('dependency_cycle',lambda:s.update(b['task']['id'],{'depends_on':[a['task']['id']]},b['sha256']))
    def test_missing_dependency(self):
        x=self.task();self.expect('missing_dependency',lambda:ts.Store(self.fs).update(x['task']['id'],{'depends_on':['TASK-nonexistent']},x['sha256']))
    def test_dependency_blocks_execution(self):
        a=self.task();b=self.task();s=ts.Store(self.fs);a=s.update(a['task']['id'],{'depends_on':[b['task']['id']]},a['sha256']);self.expect('dependency_not_done',lambda:s.update(a['task']['id'],{'owner':'actor'},a['sha256'],transition='in_progress'))
    def test_revoke_stops_active(self):
        x=self.task();s=ts.Store(self.fs);x=s.update(x['task']['id'],{'owner':'actor'},x['sha256'],transition='in_progress');x=s.update(x['task']['id'],{'authorization':{'status':'revoked','basis_ref':'user:stop'}},x['sha256'],authority_ref='user:stop');self.assertEqual(x['task']['status'],'blocked')
    def done(self):
        x=self.task();s=ts.Store(self.fs);x=s.update(x['task']['id'],{'owner':'actor'},x['sha256'],transition='in_progress');x=s.update(x['task']['id'],{},x['sha256'],transition='review')
        closure={'scope_met':True,'diff_reviewed':True,'documentation':'Sem mudança pertinente.','known_regression':False,'delivery':'patch','evidence':[{'ref':'test:synthetic','result':'pass','summary':'Fixture executada.'}],'limitations':[],'authority_ref':'user:synthetic-scope'}
        return s.update(x['task']['id'],{'closure':closure},x['sha256'],transition='done')
    def test_done_not_deploy(self):self.assertEqual(self.done()['task']['closure']['delivery'],'patch')
    def test_archive_resolves_id(self):
        x=self.done();s=ts.Store(self.fs);s.archive(x['task']['id'],x['sha256']);p,m,b=s.get(x['task']['id']);self.assertIn('/archive/',p)
    def test_ids_no_counter_collision(self):
        ids=[self.task()['task']['id'] for _ in range(20)];self.assertEqual(len(ids),len(set(ids)))
    def test_cancel_requires_origin(self):
        x=self.task();self.expect('missing_authority',lambda:ts.Store(self.fs).update(x['task']['id'],{'cancel_reason':'Escopo cancelado'},x['sha256'],transition='cancelled'))
    def test_cancelled_not_resumed(self):
        x=self.task();s=ts.Store(self.fs);x=s.update(x['task']['id'],{'cancel_reason':'Escopo cancelado'},x['sha256'],transition='cancelled',authority_ref='user:cancel');self.expect('invalid_transition',lambda:s.update(x['task']['id'],{},x['sha256'],transition='ready'))
    def test_frontmatter_future_schema_rejected(self):
        x=self.task();m=x['task'];m['schema_version']=99;self.expect('schema_validation',lambda:ts.dump(m,'Corpo.'))
    def test_terminal_task_needs_no_checkpoint(self):
        x=self.done();self.expect('inactive_task',lambda:sessions.save(self.fs,'session-one',x['task']['id'],['AGENTS.md'],'Nada para fazer.'))
    def test_checkpoint_detects_cancel(self):
        x=self.task();sessions.save(self.fs,'session-one',x['task']['id'],['AGENTS.md'],'Executar task.')
        self.assertTrue(sessions.check(self.fs,'session-one')['reusable']);ts.Store(self.fs).update(x['task']['id'],{'cancel_reason':'Parar'},x['sha256'],transition='cancelled',authority_ref='user:cancel');self.assertFalse(sessions.check(self.fs,'session-one')['reusable'])

class MigrationTests(Base):
    def test_init_plan_no_mutation(self):
        before=self.files();mg.make_plan(self.fs,'user:adopt','explicit-skill:read');self.assertEqual(before,self.files())
    def test_inventory_no_mutation(self):
        self.fs.write('CLAUDE.md',b'# Rules\nPreserve.\n',None);before=self.files();mg.inventory(self.fs);self.assertEqual(before,self.files())
    def test_existing_requires_semantics(self):
        self.fs.write('CLAUDE.md',b'# Custom\nNo production.\n',None);self.assertEqual(mg.make_plan(self.fs,'user:adopt','explicit-skill:read')['status'],'needs_review')
    def test_legacy_consolidated_preserves_app(self):
        p=self.legacy();mg.apply(self.fs,p,p['plan_digest']);self.assertIsNone(self.fs.read('CLAUDE.md'));self.assertIn(b'Never deploy automatically.',self.fs.read('AGENTS.md'));self.assertEqual(self.fs.read('src/app.py'),b'untouched = True\n')
    def test_preserve_crlf_bytes(self):
        p=self.legacy();mg.apply(self.fs,p,p['plan_digest']);self.assertIn(b'Never deploy automatically.\r\n',self.fs.read('AGENTS.md'))
    def test_rollback_restores_original(self):
        p=self.legacy();old=self.fs.read('AGENTS.md');mg.apply(self.fs,p,p['plan_digest']);mg.rollback(self.fs,p['migration_id'],p['plan_digest']);self.assertEqual(self.fs.read('AGENTS.md'),old);self.assertIsNotNone(self.fs.read('CLAUDE.md'))
    def test_backup_inert(self):
        p=self.legacy();mg.apply(self.fs,p,p['plan_digest']);back=self.fs.root/'.omnx/local/migrations'/p['migration_id']/'backup';self.assertTrue(list(back.glob('*.bin')));self.assertFalse(list(back.rglob('CLAUDE.md')))
    def test_apply_digest_required(self):
        p=self.legacy();self.expect('unapproved_plan',lambda:mg.apply(self.fs,p,'0'*64))
    def test_tampered_plan(self):
        p=self.legacy();p['authority_ref']='attacker:other';self.expect('tampered_plan',lambda:mg.apply(self.fs,p,p['plan_digest']))
    def test_plan_other_root(self):
        p=self.legacy()
        with tempfile.TemporaryDirectory() as d:self.expect('wrong_root',lambda:mg.apply(RootFS(d),p,p['plan_digest']))
    def test_stale_plan(self):
        p=self.legacy();self.fs.write('CLAUDE.md',b'User edit\n',self.fs.hash('CLAUDE.md'));self.expect('stale_plan',lambda:mg.apply(self.fs,p,p['plan_digest']));self.assertEqual(self.fs.read('CLAUDE.md'),b'User edit\n')
    def test_second_apply_noop(self):
        p=self.legacy();mg.apply(self.fs,p,p['plan_digest']);before={o['path']:self.fs.read(o['path']) for o in p['operations']};mg.apply(self.fs,p,p['plan_digest']);self.assertEqual(before,{o['path']:self.fs.read(o['path']) for o in p['operations']})
    def test_updated_project_plan_noop(self):self.init();self.assertTrue(mg.make_plan(self.fs,'user:adopt','explicit-skill:read')['noop'])
    def test_rollback_respects_user_edit(self):
        p=self.legacy();mg.apply(self.fs,p,p['plan_digest']);self.fs.write('AGENTS.md',b'User edit afterwards\n',self.fs.hash('AGENTS.md'));self.expect('rollback_conflict',lambda:mg.rollback(self.fs,p['migration_id'],p['plan_digest']));self.assertEqual(self.fs.read('AGENTS.md'),b'User edit afterwards\n')
    def test_future_schema_preserved(self):
        self.fs.write('.omnx/project.yaml',b'{"schema_version":99}\n',None);before=self.files();self.expect('schema_validation',lambda:mg.make_plan(self.fs,'user:adopt','explicit-skill:read'));self.assertEqual(before,self.files())
    def test_protected_product_write(self):self.expect('migration_scope',lambda:mg.allowed('src/auth.ts'))
    def test_backups_excluded_inventory(self):
        self.init();inv=mg.inventory(self.fs);self.assertTrue(all('/local/' not in s['path'] for s in inv['sources']))
    def test_incomplete_journal_blocks_tasks(self):
        p=mg.make_plan(self.fs,'user:adopt','explicit-skill:read')
        def fail(point):
            if point=='after:OP-0001':raise RuntimeError('Injected crash')
        with self.assertRaises(RuntimeError):mg.apply(self.fs,p,p['plan_digest'],fault=fail)
        self.expect('migration_pending',lambda:pr.ensure_writable(self.fs));mg.resume(self.fs,p['migration_id'],p['plan_digest']);self.assertFalse(pr.pending(self.fs))
    def test_no_git_supported(self):p=self.init();self.assertEqual(pr.doctor(self.fs)['health'],'ready')
    def test_git_dirty_unrelated_preserved(self):
        subprocess.run(['git','init','-q',str(self.fs.root)],check=True);self.fs.write('app.txt',b'user work\n',None);self.init();self.assertEqual(self.fs.read('app.txt'),b'user work\n')
    def test_block_split_fences(self):
        raw=b'# Section\n```py\n# not a heading\n```\n## Real\ntext\n';b=mg.blocks(raw);self.assertEqual(len(b),2);self.assertEqual(b''.join(x['raw'] for x in b),raw)
    def test_rollback_interruption_resume(self):
        p=self.legacy();mg.apply(self.fs,p,p['plan_digest']);hit=[False]
        def fail(point):
            if not hit[0]:hit[0]=True;raise RuntimeError('Injected rollback interruption')
        with self.assertRaises(RuntimeError):mg.rollback(self.fs,p['migration_id'],p['plan_digest'],fault=fail)
        mg.rollback(self.fs,p['migration_id'],p['plan_digest']);self.assertIsNotNone(self.fs.read('CLAUDE.md'));self.assertEqual(mg.status(self.fs,p['migration_id'])['phase'],'rolled_back')

class AuditTests(Base):
    def test_template_not_pass(self):
        r=self.request();a=au.response_template(r);au.validate_response(r,a,self.fs);self.assertEqual(a['execution_status'],'partial');self.assertTrue(all(x['result']=='unknown' for x in a['control_results']))
    def test_missing_control(self):
        r=self.request();a=au.response_template(r);a['control_results']=[];self.expect('missing_control',lambda:au.validate_response(r,a))
    def test_duplicate_control(self):
        r=self.request();a=au.response_template(r);a['control_results']*=2;self.expect('duplicate_control',lambda:au.validate_response(r,a))
    def test_unknown_enum(self):
        r=self.request();a=au.response_template(r);a['control_results'][0]['result']='sort_of_safe';self.expect('schema_validation',lambda:au.validate_response(r,a))
    def test_missing_evidence_for_pass(self):
        r=self.request();a=au.response_template(r);a['control_results'][0].update(result='pass',assessment='evaluated');self.expect('unsupported_conclusion',lambda:au.validate_response(r,a))
    def test_different_snapshot(self):
        r=self.request();a=au.response_template(r);a['snapshot_content_digest']='f'*64;self.expect('snapshot_mismatch',lambda:au.validate_response(r,a))
    def test_dirty_file_invalidates(self):
        r=self.request();a=self.passed(r);self.fs.write('src/input.py',b'changed\n',self.fs.hash('src/input.py'));self.expect('stale_evidence',lambda:au.validate_response(r,a,self.fs))
    def test_unrelated_file_does_not_invalidate(self):
        r=self.request();a=self.passed(r);self.fs.write('other.txt',b'changed',None);au.validate_response(r,a,self.fs)
    def test_environment_digest_tampering(self):
        r=self.request();r['snapshot']['environment_config_digest']='a'*64;self.expect('snapshot_digest',lambda:au.validate_request(r))
    def test_completed_unknown_not_gate_pass(self):
        r=self.request();a=au.response_template(r);a.update(execution_status='completed',surface_discovery_status='completed',unassessed_surfaces=[]);a['control_results'][0]['assessment']='evaluated';au.validate_response(r,a);self.assertEqual(au.gate(self.fs,r,a,'merge','local')['decision'],'blocked')
    def test_design_not_implementation(self):
        r=self.request();r['mode']='design';a=self.passed(r);self.assertIn('DESIGN_IS_NOT_IMPLEMENTATION',au.gate(self.fs,r,a,'merge','local')['reasons'])
    def test_tenant_pass_requires_behavior(self):
        r=self.request(['SEC-TENANT-01']);a=self.passed(r);a['evidence'][0]['kind']='static';self.expect('behavior_not_verified',lambda:au.validate_response(r,a))
    def test_no_automatic_production(self):
        r=self.request();a=self.passed(r);self.assertIn('DEPLOY_AUTHORITY_REQUIRED',au.gate(self.fs,r,a,'deploy','local')['reasons'])
    def test_valid_local_merge(self):
        r=self.request();a=self.passed(r);self.assertEqual(au.gate(self.fs,r,a,'merge','local')['decision'],'allowed')
    def test_policy_modified_rejected(self):
        r=self.request();r['policy_digest']='f'*64;self.expect('policy_mismatch',lambda:au.validate_request(r))
    def test_registry_modified_rejected(self):
        r=self.request();r['control_registry_digest']='f'*64;self.expect('registry_mismatch',lambda:au.validate_request(r))
    def test_false_completion(self):
        r=self.request();a=au.response_template(r);a['execution_status']='completed';self.expect('false_completion',lambda:au.validate_response(r,a))
    def test_synthetic_example_field_rejected(self):
        r=self.request();a=self.passed(r);a['evidence'][0]['synthetic_example']=True;self.expect('schema_validation',lambda:au.validate_response(r,a))
    def test_secret_path_not_snapshotted(self):
        self.fs.write('.env',b'not-a-real-secret',None);self.expect('secret_path',lambda:au.snapshot(self.fs,['.env']))
    def test_scan_redacts_before_output(self):
        fake=b'sb_secret_' + b'SYNTHETIC_TEST_VALUE_000'
        self.fs.write('source.txt',fake,None);out=au.scan(self.fs,['source.txt']);self.assertTrue(out['candidates']);self.assertNotIn(fake.decode(),json.dumps(out))
    def test_public_key_not_automatic_secret(self):
        self.fs.write('source.txt',b'sb_publishable_SYNTHETIC_TEST_VALUE_000',None);self.assertFalse(au.scan(self.fs,['source.txt'])['candidates'])
    def test_receipt_idempotency(self):
        self.init();r=self.request();a=self.passed(r);au.persist(self.fs,r,a);second=au.persist(self.fs,r,a);self.assertEqual(second['changed_paths'],[])
    def test_receipt_immutable(self):
        self.init();r=self.request();a=self.passed(r);au.persist(self.fs,r,a);a['metrics']['tool_calls']=12;self.expect('receipt_conflict',lambda:au.persist(self.fs,r,a))
    def test_local_commit_not_universal_gate(self):
        r=self.request();a=au.response_template(r);self.assertEqual(au.gate(self.fs,r,a,'commit','local')['decision'],'allowed')
    def test_new_file_is_manifested(self):
        r=self.request();self.assertIsNotNone(r['snapshot']['files'][0]['sha256'])
    def test_git_index_change_invalidates(self):
        subprocess.run(['git','init','-q',str(self.fs.root)],check=True);r=self.request();a=self.passed(r);subprocess.run(['git','-C',str(self.fs.root),'add','src/input.py'],check=True);self.expect('stale_evidence',lambda:au.validate_response(r,a,self.fs))

class CLIAndDistribution(Base):
    def cli(self,*args):
        entry='omnx.py' if (PACKAGE/'scripts/omnx.py').exists() else 'auditor.py'
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
        return subprocess.run([sys.executable,str(PACKAGE/'scripts'/entry),*args],capture_output=True,text=True,env=env,timeout=20)
    def test_semver_prerelease(self):
        self.assertLess(dist.compare_versions('2.0.0-rc.1','2.0.0'),0);self.assertLess(dist.compare_versions('2.0.0-rc.2','2.0.0-rc.10'),0)
    def test_semver_stable(self):self.assertGreater(dist.compare_versions('2.0.0','1.24.1'),0)
    def test_route_s0_no_auditor(self):
        if not (PACKAGE/'scripts/omnx.py').exists():self.skipTest('Entrypoint de especialista deliberadamente não expõe roteamento.')
        p=self.cli('route','--ux','UX1','--security','S0','--operation','O1');self.assertEqual(p.returncode,0,p.stdout);d=json.loads(p.stdout);self.assertFalse(d['auditor_required']);self.assertFalse(d['historical_mockup_sync'])
    def test_cli_help(self):self.assertEqual(self.cli('--help').returncode,0)
    def test_cli_invalid_json_no_secret_echo(self):
        p=self.fs.root/'bad.json';p.write_text('{"secret":"SYNTHETIC_PRIVATE_VALUE" garbage')
        out=self.cli('audit','validate-request','--request',str(p));self.assertNotEqual(out.returncode,0);self.assertNotIn('SYNTHETIC_PRIVATE_VALUE',out.stdout+out.stderr)
    def zip_candidate(self,entries):
        path=self.fs.root/'candidate.zip'
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            for name,value in entries:z.writestr(name,value)
        return path,digest(path.read_bytes())
    def test_zip_traversal(self):
        p,d=self.zip_candidate([('../outside',b'x')]);self.expect('invalid_path',lambda:dist.inspect_archive(p,d))
    def test_zip_duplicate_case(self):
        p,d=self.zip_candidate([('omnx-code/Foo',b'x'),('omnx-code/foo',b'y')]);self.expect('archive_collision',lambda:dist.inspect_archive(p,d))
    def test_zip_symlink(self):
        path=self.fs.root/'candidate.zip'
        with zipfile.ZipFile(path,'w') as z:
            zi=zipfile.ZipInfo('omnx-code/link');zi.create_system=3;zi.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(zi,'/etc/passwd')
        self.expect('archive_link',lambda:dist.inspect_archive(path,digest(path.read_bytes())))
    def test_zip_wrong_digest(self):
        p,d=self.zip_candidate([('omnx-code/foo',b'x')]);self.expect('artifact_integrity',lambda:dist.inspect_archive(p,'0'*64))
    def test_zip_incomplete(self):
        p,d=self.zip_candidate([('omnx-code/foo',b'x')]);self.expect('incomplete_package',lambda:dist.inspect_archive(p,d))
    def test_zip_bomb_limit(self):
        p,d=self.zip_candidate([('omnx-code/foo',b'0'*(MAX_DOCUMENT+1))]);self.expect('archive_limit',lambda:dist.inspect_archive(p,d))

# Real fault injection at each write boundary in a minimal migration, counted separately.
class FaultInjection(Base):pass
for point in ['journal_created','snapshot_ready']+[f'{phase}:OP-{i:04d}' for i in range(1,5) for phase in ('snapshot','before','after')]:
    def test(self,point=point):
        p=mg.make_plan(self.fs,'user:fault-test','explicit-skill:test')
        def fail(where):
            if where==point:raise RuntimeError('Injected crash')
        with self.assertRaises(RuntimeError):mg.apply(self.fs,p,p['plan_digest'],fault=fail)
        mg.resume(self.fs,p['migration_id'],p['plan_digest'])
        for op in p['operations']:self.assertEqual(self.fs.hash(op['path']),op['after_sha256'])
        self.assertEqual(mg.status(self.fs,p['migration_id'])['phase'],'applied')
    setattr(FaultInjection,'test_resume_'+point.replace(':','_').replace('-','_'),test)

if __name__=='__main__':unittest.main(verbosity=2)
