"""Read-tolerant, bounded incremental projections. Never authoritative for writes."""
from __future__ import annotations
from collections import OrderedDict, Counter
from copy import deepcopy
import threading
import time
from pathlib import PurePosixPath
from .core import *
from . import tasks, decisions
from .previews import walk_files, preview_base, ENTRY_EXTS
from .privacy import public_object

MAX_ROWS=20000
MAX_METADATA=512*1024
CACHE_ENTRIES=25000
CACHE_TTL_SECONDS=2
_CACHE=OrderedDict();_LOCK=threading.RLock()
METRICS={'metadata_reads':0,'cache_hits':0}

def clear_cache():
    with _LOCK:_CACHE.clear();METRICS.update(metadata_reads=0,cache_hits=0)

def workspace_id(root):return 'WSP-'+digest(str(Path(root).absolute().resolve()).encode())[:24]

def _fingerprint(p):
    s=p.stat();return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def _snapshot(fs,rel,parser):
    """Parsed fields and digest come from the same bytes. Stat only caches display."""
    p=fs.path(rel);before=_fingerprint(p);key=(str(fs.root),rel)
    with _LOCK:
        cached=_CACHE.get(key)
        if cached and cached[0]==before:
            METRICS['cache_hits']+=1;_CACHE.move_to_end(key);return deepcopy(cached[1])
    raw=fs.read(rel,limit=MAX_METADATA)
    require(raw is not None,'stale_state','Arquivo mudou durante a leitura.',3)
    value=parser(raw);out=(value,digest(raw))
    after=_fingerprint(p)
    with _LOCK:
        METRICS['metadata_reads']+=1
        if before==after:
            _CACHE[key]=(after,deepcopy(out));_CACHE.move_to_end(key)
            while len(_CACHE)>CACHE_ENTRIES:_CACHE.popitem(last=False)
    return out

def _task_summary(raw):
    m,_=tasks.parse(raw)
    return {k:m.get(k) for k in ('id','title','status','owner','blocked_reason','updated_at','impact','priority','depends_on')} | {'authorization':m['authorization']['status'],'acceptance_count':len(m['acceptance'])}

def _decision_summary(raw):
    d=decisions.check(load_data(raw))
    return {k:d.get(k) for k in ('id','type','title','status','updated_at','revision','task_refs','subject_ref')} | {'legacy_unverified':d['schema_version']==1,'history_count':len(d.get('history',[]))}

def _files(fs,kind):
    base='.omnx/tasks' if kind=='tasks' else '.omnx/decisions'
    root=fs.path(base)
    if not root.exists():return
    require(root.is_dir(),'store_conflict','A pasta de registros está ocupada por um arquivo.',3)
    prefix='TASK-' if kind=='tasks' else 'DEC-';suffix='.md' if kind=='tasks' else '.json'
    with os.scandir(root) as it:
        for i,p in enumerate(it):
            require(i<MAX_ROWS,'scan_limit','Lista parcial: mais registros que o limite configurado.',6)
            if p.name.startswith(prefix) and p.name.endswith(suffix) and not p.is_dir(follow_symlinks=False):
                yield base+'/'+p.name

def _issue(e,rel):
    if isinstance(e,MethodError):return {'path':rel,'code':e.code,'summary':e.summary}
    return {'path':rel,'code':'unavailable_file','summary':'Não foi possível ler este item. Os demais continuam disponíveis.'}

def read_project(root,*,summary_only=False):
    fs=RootFS(root);errors=[];project={};lock={};read_only=False;reasons=[]
    for rel,label in (('.omnx/project.yaml','project'),('.omnx/method.lock.json','method-lock')):
        try:
            raw=fs.read(rel,MAX_METADATA)
            require(raw is not None,'not_initialized','Projeto sem configuração OMNX compatível.',4)
            val=load_data(raw,yaml_ok=label=='project');validate(val,schema(label))
            if label=='project':project=val
            else:lock=val
        except (MethodError,OSError) as e:
            errors.append(_issue(e,rel));read_only=True;reasons.append('Configuração ausente, inválida ou de versão não suportada.')
    from .project import pending
    try:
        if pending(fs):read_only=True;reasons.append('Migração interrompida: retome ou restaure antes de editar metadados.')
        if fs.read('CLAUDE.md') is not None or fs.read('.omnx/TASKS.md') is not None:
            read_only=True;reasons.append('Projeto legado: migração explícita necessária.')
        if not fs.read('AGENTS.md'):read_only=True;reasons.append('AGENTS.md não está disponível.')
    except (MethodError,OSError) as e:errors.append(_issue(e,'.omnx'));read_only=True
    loaded=load_data((PACKAGE/'manifest.json').read_bytes())['version']
    adopted=lock.get('adopted_packages',{}).get('omnx-code') or {}
    if adopted.get('version')!=loaded:
        read_only=True;reasons.append('Versão adotada difere do runtime: acompanhamento disponível, escrita requer adoção explícita.')
    out={'workspace_id':workspace_id(root),'project_id':str(project.get('project_id') or workspace_id(root)),
         'name':project.get('name') or fs.root.name,'path':str(fs.root),'available':True,'project':project,'method_lock':lock,
         'read_only':read_only,'read_only_reasons':list(dict.fromkeys(reasons)),'tasks':[],'decisions':[],'mockups':[],
         'errors':errors,'partial':False,'refreshed_at':now()}
    for kind,parser in (('tasks',_task_summary),('decisions',_decision_summary)):
        try:
            for rel in _files(fs,kind):
                try:
                    m,sha=_snapshot(fs,rel,parser)
                    expected=m['id']+('.md' if kind=='tasks' else '.json')
                    require(PurePosixPath(rel).name==expected,'record_filename','ID e nome do arquivo divergem.',3)
                    out[kind].append({**m,'sha256':sha,'path':rel})
                except (MethodError,OSError,UnicodeError,ValueError) as e:
                    out['errors'].append(_issue(e,rel));out['partial']=True
        except (MethodError,OSError) as e:out['errors'].append(_issue(e,kind));out['partial']=True
        out[kind].sort(key=lambda m:(m.get('updated_at') or '',m['id']),reverse=True)
    try:
        base=preview_base(fs,project)
        for rel in walk_files(fs,base,maximum=10000):
            if PurePosixPath(rel).suffix.lower() not in ENTRY_EXTS:continue
            try:
                p=fs.path(rel);s=p.stat()
                require(s.st_size<=8*1024*1024,'preview_limit','Preview acima de 8 MiB não foi carregado.',6)
                out['mockups'].append({'id':'PRE-'+digest(rel.encode())[:24],'name':p.name,'title':p.parent.name.replace('-',' '),'path':rel,'kind':'html' if p.suffix.lower() in ('.html','.htm') else 'image','bytes':s.st_size})
                if len(out['mockups'])>=500:
                    out['errors'].append({'path':base,'code':'preview_limit','summary':'Galeria limitada a 500 arquivos. Separe propostas antigas para reduzir a lista.'});out['partial']=True;break
            except (MethodError,OSError) as e:out['errors'].append(_issue(e,rel));out['partial']=True
    except (MethodError,OSError) as e:out['errors'].append(_issue(e,'previews'));out['partial']=True
    out['counts']={'tasks':len(out['tasks']),'by_status':dict(Counter(t['status'] for t in out['tasks'])),
                   'pending_decisions':sum(d['status']=='pending' and not d['legacy_unverified'] for d in out['decisions']),
                   'awaiting_agent':sum(d['status']=='changes_requested' for d in out['decisions']),
                   'legacy_decisions':sum(d['legacy_unverified'] for d in out['decisions']),'previews':len(out['mockups'])}
    out['partial']=out['partial'] or bool(out['errors'])
    out['revision']=object_digest({k:out[k] for k in ('tasks','decisions','mockups','method_lock','errors')})
    if summary_only:
        for k in ('tasks','decisions','mockups','project'):out.pop(k,None)
    return public_object(out)

def task_detail(fs,tid):
    path,m,body,sha=tasks.Store(fs).read_record(tid)
    return public_object({**m,'authorization_status':m['authorization']['status'],'body':body,'path':path,'sha256':sha})

def decision_detail(fs,did):
    path,d,sha=decisions.Store(fs).read_record(did)
    return public_object({**d,'path':path,'sha256':sha,'legacy_unverified':d['schema_version']==1})
