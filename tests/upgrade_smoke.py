#!/usr/bin/env python3
"""Opt-in adoption test using a previously trusted rc.1 package in a temp project.

This executes the explicitly supplied prior engine, only on generated fixtures.
Never pass an untrusted downloaded package. No real application is touched.
"""
import sys, argparse, tempfile, subprocess, json
from pathlib import Path
sys.dont_write_bytecode=True
PACKAGE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PACKAGE/'scripts'))
from omnxlib.core import *
from omnxlib import project, projection
from omnxlib.decisions import Store

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--previous-package',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    previous=Path(a.previous_package).resolve();assert (previous/'scripts/omnx.py').is_file()
    code=r'''
import sys,json
sys.dont_write_bytecode=True;sys.path.insert(0,sys.argv[1])
from omnxlib.core import *
from omnxlib import migration,tasks
from omnxlib.decisions import Store
fs=RootFS(sys.argv[2]);p=migration.make_plan(fs,'test:old-synthetic','test:explicit');migration.apply(fs,p,p['plan_digest'])
t=tasks.Store(fs).create({'title':'Synthetic existing delivery','status':'ready','authorization':{'status':'authorized','basis_ref':'test:existing'},'acceptance':['Preserve fixture']},'Do not publish.')
fs.write('src/app.txt',b'PRODUCT_SENTINEL_UNCHANGED',None)
fs.write('docs/ux/proposals/UX-old/screen.html',b'<h1>Previous proposal</h1>',None)
d=Store(fs).create({'type':'ux','title':'Old approval','question':'Approve synthetic layout?','subject_ref':'docs/ux/proposals/UX-old/screen.html','task_refs':[t['task']['id']],'options':[{'id':'a','label':'A','description':''},{'id':'b','label':'B','description':''}]})
d=Store(fs).update(d['decision']['id'],d['sha256'],status='approved',selected_option='a',authority_ref='test:old-human-fixture')
print(json.dumps({'task_id':t['task']['id'],'decision_id':d['decision']['id']}))
'''
    with tempfile.TemporaryDirectory(prefix='omnx-upgrade-') as temp:
        child=subprocess.run([sys.executable,'-c',code,str(previous/'scripts'),temp],capture_output=True,text=True,timeout=30);assert child.returncode==0,child.stderr
        ids=json.loads(child.stdout);fs=RootFS(temp);taskrel='.omnx/tasks/'+ids['task_id']+'.md';taskbefore=fs.read(taskrel);drel='.omnx/decisions/'+ids['decision_id']+'.json';original=fs.read(drel)
        before=project.verify_adoption(fs);assert before['matches']['omnx-code'] is False
        assert projection.read_project(temp)['read_only'] is True
        project.adopt(fs,before['lock_sha256'],'test:explicit-upgrade')
        assert project.verify_adoption(fs)['matches']['omnx-code'] is True
        view=projection.read_project(temp);assert view['counts']['legacy_decisions']==1 and view['counts']['pending_decisions']==0
        try:Store(fs).update(ids['decision_id'],digest(original),status='approved',selected_option='b',authority_ref='test:fixture');raise AssertionError('Legacy approval was reused')
        except MethodError as e:assert e.code=='legacy_decision',e.code
        x=Store(fs).revise(ids['decision_id'],digest(original),{})
        assert x['decision']['schema_version']==2 and x['decision']['status']=='pending' and x['decision']['selected_option'] is None
        assert x['decision']['legacy_record']['sha256']==digest(original)
        x=Store(fs).update(ids['decision_id'],x['sha256'],status='approved',selected_option='b',authority_ref='test:new-explicit-fixture')
        assert len(x['decision']['history'])==1 and x['decision']['selected_option']=='b'
        assert fs.read(taskrel)==taskbefore and fs.read('src/app.txt')==b'PRODUCT_SENTINEL_UNCHANGED'
        assert not fs.path('CLAUDE.md').exists()
    out={'executed_at':now(),'current_version':load_data((PACKAGE/'manifest.json').read_bytes())['version'],'previous_version':load_data((previous/'manifest.json').read_bytes())['version'],'result':'pass','checks':['Lock adoption explicit/CAS','Old package read-only before adoption','Old approval not trusted or reused','Original legacy decision retained','New revision explicitly approved','Task bytes and product sentinel unchanged','No CLAUDE.md created'],'scope':'One synthetic project built with supplied trusted rc.1 runtime. Not migration of a private user application or host session.'}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
