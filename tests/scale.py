#!/usr/bin/env python3
"""Opt-in local projection measurements with synthetic tasks. No LLM/production."""
import sys, argparse, time, json, tempfile, platform
from pathlib import Path
from copy import deepcopy
sys.dont_write_bytecode=True
PACKAGE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PACKAGE/'scripts'))
from omnxlib.core import *
from omnxlib import tasks, migration, projection, console

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--sizes',nargs='+',type=int,default=[500,2000,10000]);a=ap.parse_args();results=[]
    for n in a.sizes:
        require(1<=n<=20000,'fixture_limit','Use 1 a 20000 tarefas sintéticas.')
        with tempfile.TemporaryDirectory(prefix='omnx-scale-') as root:
            fs=RootFS(root);plan=migration.make_plan(fs,'test:scale','test:explicit');migration.apply(fs,plan,plan['plan_digest'])
            x=tasks.Store(fs).create({'title':'Scale fixture','status':'ready','authorization':{'status':'authorized','basis_ref':'test:scale'},'acceptance':['Synthetic local criterion']},'Fixture body only.')
            template=x['task'];paths=[]
            for i in range(n-1):
                m=deepcopy(template);m['id']=new_id('TASK');m['title']='Synthetic work '+str(i);p=fs.root/'.omnx/tasks'/f'{m["id"]}.md';p.write_bytes(tasks.dump(m,'Fixture.\n'+'x'*1000));paths.append(p)
            projection.clear_cache();before=dict(projection.METRICS);t=time.perf_counter();p=projection.read_project(root);cold=time.perf_counter()-t;coldreads=projection.METRICS['metadata_reads']-before['metadata_reads']
            t=time.perf_counter();p=projection.read_project(root);warm=time.perf_counter()-t;warmreads=projection.METRICS['metadata_reads']-before['metadata_reads']-coldreads
            target=paths[-1] if paths else fs.path('.omnx/tasks/'+template['id']+'.md');meta,body=tasks.parse(target.read_bytes());meta['title']='One changed item';target.write_bytes(tasks.dump(meta,body))
            old=projection.METRICS['metadata_reads'];t=time.perf_counter();changed=projection.read_project(root);delta=time.perf_counter()-t;changedreads=projection.METRICS['metadata_reads']-old
            assert len(p['tasks'])==n and not p['partial'];assert warmreads==0 and changedreads==1
            prompt=console.prompt_for_task(changed,template['id']);assert len(prompt)<2400
            summary={k:v for k,v in changed.items() if k not in ('tasks','decisions','mockups','project')}
            row={'tasks':n,'cold_seconds':round(cold,4),'warm_seconds':round(warm,4),'one_change_seconds':round(delta,4),'cold_metadata_reads':coldreads,'unchanged_metadata_reads':warmreads,'one_change_metadata_reads':changedreads,'summary_bytes':len(json_bytes(summary)),'compact_prompt_characters':len(prompt),'partial':p['partial']};results.append(row);print(json.dumps(row),flush=True)
    report={'executed_at':now(),'python':platform.python_version(),'platform':platform.platform(),'package_version':load_data((PACKAGE/'manifest.json').read_bytes())['version'],'runs_per_size':1,'measurements':results,'model_tokens_actual':None,'scope':'Synthetic project projection only, single run per size. Not a browser-load, multi-user, slow-disk, Windows/macOS or token benchmark.'}
    Path(a.output).write_text(json.dumps(report,indent=2)+'\n');return 0
if __name__=='__main__':raise SystemExit(main())
