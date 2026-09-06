"""Additional negative and end-to-end local fixtures."""
from test_runtime import Base, PACKAGE
from omnxlib.core import *
from omnxlib import migration as mg, tasks as ts, audit as au, sessions, distribution as dist
import subprocess, sys, copy, io, zipfile, tempfile, unittest

class Additional(Base):
    def test_checkpoint_update_uses_actual_file_hash(self):
        self.init();x=self.task();first=sessions.save(self.fs,'session-cas',x['task']['id'],['AGENTS.md'],'Etapa um.');second=sessions.save(self.fs,'session-cas',x['task']['id'],['AGENTS.md'],'Etapa dois.',expected=first['sha256']);self.assertEqual(second['checkpoint']['next_action'],'Etapa dois.')
    def test_owner_transfer_requires_origin(self):
        self.init();x=self.task();s=ts.Store(self.fs);x=s.update(x['task']['id'],{'owner':'agent-A'},x['sha256'],transition='in_progress');self.expect('owner_transfer_required',lambda:s.update(x['task']['id'],{'owner':'agent-B'},x['sha256']))
    def test_invalid_task_timestamp_rejected_at_create(self):
        self.init();self.expect('invalid_time',lambda:ts.Store(self.fs).create({'title':'bad','acceptance':['test'],'created_at':'not-a-timestamp-but-long-enough'},'scope'))
    def test_backup_corruption_prevents_resume(self):
        p=self.legacy()
        def stop(point):
            if point=='snapshot_ready':raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):mg.apply(self.fs,p,p['plan_digest'],fault=stop)
        op=next(o for o in p['operations'] if o['before_sha256'] is not None);bp=f".omnx/local/migrations/{p['migration_id']}/backup/{op['id']}.bin"
        self.fs.write(bp,b'corrupted',self.fs.hash(bp));self.expect('backup_corrupt',lambda:mg.resume(self.fs,p['migration_id'],p['plan_digest']));self.assertIsNotNone(self.fs.read('CLAUDE.md'))
    def test_snapshot_failure_does_not_remove_source(self):
        p=self.legacy()
        def stop(point):
            if point.startswith('snapshot:'):raise OSError('disk full simulated')
        with self.assertRaises(OSError):mg.apply(self.fs,p,p['plan_digest'],fault=stop)
        self.assertIsNotNone(self.fs.read('CLAUDE.md'));self.assertNotEqual(mg.status(self.fs,p['migration_id'])['phase'],'applied')
    def test_missing_block_mapping_blocks_plan(self):
        self.fs.write('CLAUDE.md',b'# Rule\nDo not deploy.\n',None)
        res={'source_paths':['CLAUDE.md'],'mappings':[],'writes':{'AGENTS.md':'new'}}
        self.expect('unmapped_blocks',lambda:mg.make_plan(self.fs,'user:adopt','explicit:read',resolutions=res))
    def test_instruction_cannot_disappear_into_backup(self):
        self.fs.write('CLAUDE.md',b'# Rule\nDo not deploy.\n',None);b=mg.blocks(self.fs.read('CLAUDE.md'))[0]
        m={'source_path':'CLAUDE.md','block_id':b['id'],'block_sha256':b['sha256'],'category':'instruction','treatment':'history','destination':None,'reason':'Migrate','decision_ref':'user:review'}
        res={'source_paths':['CLAUDE.md'],'mappings':[m],'writes':{'AGENTS.md':'new'}}
        self.expect('inactive_custom_rule',lambda:mg.make_plan(self.fs,'user:adopt','explicit:read',resolutions=res))
    def test_known_destination_not_overwritten_uninventoried(self):
        self.fs.write('CLAUDE.md',b'# Rule\nOriginal.\n',None);self.fs.write('docs/notes.md',b'user custom',None)
        res={'source_paths':['CLAUDE.md'],'mappings':[],'writes':{'AGENTS.md':'new','docs/notes.md':'override'}}
        self.expect('unowned_destination',lambda:mg.make_plan(self.fs,'user:adopt','explicit:read',resolutions=res))
    def test_no_rollback_init_under_later_tasks(self):
        p=self.init();self.task();self.expect('rollback_dependents',lambda:mg.rollback(self.fs,p['migration_id'],p['plan_digest']));self.assertIsNotNone(self.fs.read('.omnx/project.yaml'))
    def test_doctor_read_only_even_without_setup(self):
        from omnxlib.project import doctor
        before=self.files();d=doctor(self.fs);self.assertEqual(d['health'],'needs_attention');self.assertEqual(before,self.files())
    def test_receipt_of_other_task_rejected(self):
        r=self.request();a=self.passed(r);a['task_id']='TASK-other';self.expect('response_identity',lambda:au.validate_response(r,a))
    def test_deferred_fail_rejected(self):
        r=self.request();a=au.response_template(r);a['control_results'][0]['result']='fail';self.expect('unassessed_pass',lambda:au.validate_response(r,a))
    def test_s3_deploy_requires_environment_observation(self):
        r=self.request();r['security_impact']='S3';a=self.passed(r);g=au.gate(self.fs,r,a,'deploy','local','user:deploy');self.assertIn('ENVIRONMENT_EVIDENCE_REQUIRED',g['reasons'])
    def test_future_evidence_rejected(self):
        r=self.request();a=self.passed(r);a['evidence'][0]['observed_at']='2099-01-01T00:00:00+00:00';self.expect('future_evidence',lambda:au.validate_response(r,a))
    def test_expired_evidence_requires_recheck(self):
        r=self.request();a=self.passed(r);a['evidence'][0]['observed_at']='2000-01-01T00:00:00+00:00';self.assertIn('EVIDENCE_EXPIRED_REVIEW_NEEDED',au.gate(self.fs,r,a,'merge','local')['reasons'])
    def test_permissions_do_not_allow_write(self):
        r=self.request();r['permissions']['application_writes']=True;self.expect('schema_validation',lambda:au.validate_request(r))
    def test_fake_claude_argv_plan_preserves_default(self):
        from omnxlib.cli import parser,dispatch
        self.init();out=dispatch(parser().parse_args(['--root',str(self.fs.root),'host','claude']))
        self.assertIn('--append-system-prompt-file',out['argv']);self.assertNotIn('--system-prompt-file',out['argv']);self.assertIsNone(self.fs.read('CLAUDE.md'))
    def test_host_bootstrap_needs_trust(self):
        from omnxlib.cli import parser,dispatch
        self.init();a=parser().parse_args(['--root',str(self.fs.root),'host','--execute','claude']);self.expect('untrusted_bootstrap',lambda:dispatch(a))
    def test_host_dangerous_flag_rejected(self):
        from omnxlib.cli import parser,dispatch
        self.init();a=parser().parse_args(['--root',str(self.fs.root),'host','claude','--','--dangerously-skip-permissions']);self.expect('unsafe_host_args',lambda:dispatch(a))
    def test_no_empty_full_audit_gate_pass(self):
        r=self.request();r['mode']='full';r['requested_controls']=[];a=self.passed(r);self.assertIn('EMPTY_CONTROL_COVERAGE',au.gate(self.fs,r,a,'merge','local')['reasons'])
    def test_proposed_task_does_not_gain_execution_from_audit(self):
        self.init();x=self.task('backlog');r=self.request();r['task_id']=x['task']['id'];r['orchestrator_id']='ORQ-test';a=self.passed(r);self.assertIn('TASK_NOT_AUTHORIZED',au.gate(self.fs,r,a,'merge','local')['reasons'])
    def test_semver_invalid_leading_zero(self):self.expect('invalid_version',lambda:dist.compare_versions('02.0.0','2.0.0'))
    def test_abrupt_subprocess_exit_releases_lock_and_resumes(self):
        p=mg.make_plan(self.fs,'user:crash-fixture','explicit-skill:read')
        planfile=self.fs.root/'test-plan.json';planfile.write_bytes(json_bytes(p))
        code="import sys,os;sys.path.insert(0,sys.argv[1]);from omnxlib.core import RootFS,external_data;from omnxlib.migration import apply;fs=RootFS(sys.argv[2]);p=external_data(sys.argv[3]);apply(fs,p,p['plan_digest'],fault=lambda point:os._exit(55) if point=='after:OP-0001' else None)"
        child=subprocess.run([sys.executable,'-c',code,str(PACKAGE/'scripts'),str(self.fs.root),str(planfile)],capture_output=True,timeout=15,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        self.assertEqual(child.returncode,55,child.stderr.decode())
        mg.resume(self.fs,p['migration_id'],p['plan_digest']);self.assertEqual(mg.status(self.fs,p['migration_id'])['phase'],'applied')
    def minimal_zip(self):
        files={'manifest.json':json_bytes({'name':'omnx-code','version':'2.0.0-rc.1','audit_contract_versions':['2.0']}),'SKILL.md':b'# synthetic fixture\n','script.py':b'raise RuntimeError("MUST NOT EXECUTE ON INSTALL")\n'}
        files['integrity.json']=json_bytes({'algorithm':'sha256','files':{k:digest(v) for k,v in files.items()}})
        path=self.fs.root/'fixture.zip'
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            for k,v in files.items():z.writestr('omnx-code/'+k,v)
        return path,digest(path.read_bytes())
    def test_install_checks_and_does_not_execute_code(self):
        p,h=self.minimal_zip();dest=self.fs.root/'installed';plan=dist.plan(p,h,dest);self.assertFalse(dest.exists());dist.apply(plan,plan['plan_digest']);self.assertTrue((dest/'script.py').exists())
    def test_install_repeat_identical_noop(self):
        p,h=self.minimal_zip();dest=self.fs.root/'installed';plan=dist.plan(p,h,dest);dist.apply(plan,plan['plan_digest']);self.assertEqual(dist.apply(plan,plan['plan_digest'])['changed_paths'],[])
    def test_install_preserves_modified_destination(self):
        p,h=self.minimal_zip();dest=self.fs.root/'installed';plan=dist.plan(p,h,dest);dist.apply(plan,plan['plan_digest']);(dest/'SKILL.md').write_text('user edit');self.expect('occupied_installation',lambda:dist.apply(plan,plan['plan_digest']));self.assertEqual((dest/'SKILL.md').read_text(),'user edit')
    def test_install_downgrade_blocked(self):
        p,h=self.minimal_zip();self.expect('downgrade_blocked',lambda:dist.plan(p,h,self.fs.root/'installed','9.0.0'))
    def test_install_requires_same_approved_plan(self):
        p,h=self.minimal_zip();plan=dist.plan(p,h,self.fs.root/'installed');self.expect('unapproved_plan',lambda:dist.apply(plan,'0'*64))

if __name__=='__main__':unittest.main(verbosity=2)
