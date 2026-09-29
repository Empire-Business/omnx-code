"""Project-scoped, privacy-minimal host lifecycle capture.

Hooks are advisory and fail open: they record only identifiers and lifecycle
signals, never transcripts, tool arguments, outputs, or code contents.
"""
from __future__ import annotations
import re
import shlex
import subprocess
import sys
import time
import itertools
from pathlib import Path
from .core import *

EVENTS={
    'codex':('UserPromptSubmit','PostToolUse','Stop','Interrupt','SessionEnd'),
    'claude':('UserPromptSubmit','PostToolUse','Stop','SessionEnd'),
}
MAX_INPUT=2*1024*1024

def session_identity(host,raw):
    require(host in EVENTS,'invalid_host','Host sem integração de ciclo de vida.')
    require(isinstance(raw,str) and 1<=len(raw)<=512,'invalid_session','ID de sessão ausente ou inválido.')
    h=digest((host+'\0'+raw).encode())
    return h,host.title()+'-'+h[:32]

def resolve_root(cwd):
    require(isinstance(cwd,str) and Path(cwd).is_absolute(),'invalid_cwd','Evento do host não trouxe um cwd absoluto.')
    start=Path(cwd).absolute()
    require(start.is_dir() and not start.is_symlink(),'invalid_cwd','cwd do host não é uma pasta segura.')
    for root in (start,*start.parents):
        if (root/'.omnx/project.yaml').is_file() and (root/'.omnx/method.lock.json').is_file():
            return RootFS(root)
    raise MethodError('unmanaged_project','Nenhum projeto OMNX gerido foi encontrado neste cwd.',4)

def _path(fs,host,session_hash):
    wid=digest(str(fs.root).encode())
    return f'.omnx/local/automation/{wid}/{host}-{session_hash[:24]}.json'

def _event_id(host,session_hash,event,payload):
    stable=(payload.get('tool_call_id') or payload.get('tool_use_id') or payload.get('call_id')) if event=='PostToolUse' else (payload.get('turn_id') or payload.get('tool_call_id') or payload.get('tool_use_id') or payload.get('call_id'))
    if not stable and event=='UserPromptSubmit':
        prompt=payload.get('prompt','')
        stable=digest(prompt.encode('utf-8','replace')) if isinstance(prompt,str) else 'invalid'
    if not stable and event in ('PostToolUse','Stop'):
        stable=f'{event.lower()}:{int(time.time()/10)}'
    if not stable:stable=event # session-level lifecycle events are singletons
    return digest(canonical({'host':host,'session':session_hash,'event':event,'stable':str(stable)[:512]}))

def _read(fs,rel):
    raw=fs.read(rel,512*1024)
    if raw is None:return None,None
    value=load_data(raw);validate(value,schema('automation-session'))
    return value,digest(raw)

def _write(fs,rel,journal,expected):
    validate(journal,schema('automation-session'))
    fs.write(rel,json_bytes(journal),expected)

def _clean_excerpt(prompt):
    # Keep only one short first-line scope hint; never persist a prompt/transcript.
    line=next((x.strip() for x in prompt.splitlines() if x.strip()),'')
    line=re.sub(r'<pasted_content[^>]*>.*?</pasted_content>','[conteúdo colado omitido]',line,flags=re.I)
    line=re.sub(r'(?i)\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{12,}|xox[baprs]-[A-Za-z0-9-]{12,})\b','[segredo omitido]',line)
    line=re.sub(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b','[email omitido]',line)
    line=re.sub(r'\s+',' ',line).strip(' `\t\r\n')
    return line[:180]

def implementation_intent(prompt):
    if not isinstance(prompt,str) or len(prompt)>MAX_INPUT:return False
    line=next((x.strip() for x in prompt.splitlines() if x.strip()),'').lower()
    if re.match(r'^(what|how|why|explain|analyze|review|plan|o que|como|por que|explique|analise|revise|planeje)\b',line):return False
    return bool(re.match(r'^(please\s+)?(implement|fix|update|add|build|change|create|refactor|migrate|corrija|implemente|atualize|adicione|crie|construa|refatore|migre|edite)\b',line))

def _new_journal(fs,host,session_hash,session_id_hash):
    from . import project
    cfg=project.config(fs);wid=digest(str(fs.root).encode())
    return {'schema_version':1,'project_id':cfg['project_id'],'worktree_id':wid,'host':host,'session_id_hash':session_id_hash,'task_id':None,'state':'active','stage':'unknown','last_signal':'Nenhuma atividade confirmada.','last_signal_at':now(),'next_step':'Aguardando um pedido de implementação explícito.','console_attempted':False,'console_server_status':'not_started','browser_status':'not_requested','client_status':'not_confirmed','client_connected_at':None,'events':[]}

def _append(fs,host,session_hash,event_id,event_type,*,signal,state=None,stage=None,next_step=None,task_id=None,console=None):
    from .project import ensure_writable
    ensure_writable(fs)
    rel=_path(fs,host,session_hash)
    with metadata_lock(fs,'automation'):
        ensure_writable(fs);journal,old_hash=_read(fs,rel)
        if journal is None:journal=_new_journal(fs,host,session_hash,session_hash);old_hash=None
        if any(row['event_id']==event_id for row in journal['events']):
            return rel,journal,False
        if task_id is not None:journal['task_id']=task_id
        if state is not None:journal['state']=state
        if stage is not None:journal['stage']=stage
        journal['last_signal']=signal;journal['last_signal_at']=now()
        if next_step is not None:journal['next_step']=next_step
        if console:
            journal.update(console)
        row={'event_id':event_id,'type':event_type,'at':now(),'state':journal['state'],'stage':journal['stage'],'task_id':journal['task_id'],'signal':signal[:200]}
        journal['events']=(journal['events']+[row])[-100:]
        _write(fs,rel,journal,old_hash)
    return rel,journal,True

def _start_task(fs,host,session_hash,prompt,model):
    from .tasks import Store
    from . import model_policy
    turn=str(model.get('turn_id') or digest(prompt.encode('utf-8','replace')))
    ref='AUTO-'+digest((session_hash+'\0'+turn).encode())[:24]
    title=_clean_excerpt(prompt) or 'Implementação iniciada pelo host'
    require(bool(title),'invalid_scope','Pedido sem resumo utilizável.')
    cfg,_=model_policy.read(fs)
    recommendation=model_policy.infer(prompt,cfg)
    security_context=bool(re.search(r'\b(auth|authentication|authorization|permission|isolation|tenant|payment|credential|secret|database|security|seguran[cç]a|autentica[cç][aã]o|autoriza[cç][aã]o|pagamento|credencial|banco de dados)\b',prompt,re.I))
    payload={'id':'TASK-'+ref,'automation_ref':ref,'title':title,'status':'ready','authorization':{'status':'authorized','basis_ref':f'host-prompt:{host}:{session_hash[:24]}'},'acceptance':['Escopo do pedido verificado contra as fontes canônicas.','Implementação e limitações registradas com evidência observável.'],'owner':f'host:{host}:{session_hash[:24]}','impact':{'ux':'UX1','security':'S2' if security_context else 'S1','rationale':'Classificação conservadora baseada no escopo textual; o perfil de modelo não concede permissão operacional.'},'model_policy':recommendation}
    body=f"Registro automático a partir do primeiro pedido de implementação desta sessão {host}.\n\nResumo de escopo (primeira linha, truncada e com padrões comuns de segredo removidos):\n{title}\n\nEste registro não concede deploy, migração de dados, cobrança, push, merge nem outras permissões além do pedido recebido."
    created=Store(fs).create(payload,body)
    task=created['task'];sha=created['sha256']
    if task['status']=='ready':
        try:updated=Store(fs).update(task['id'],{},sha,transition='in_progress')
        except MethodError as exc:
            if exc.code!='stale_state':raise
            path,task,_,sha=Store(fs).read_record(task['id']);updated={'task':task,'sha256':sha}
        task=updated['task']
    return task

def _observe_model(fs,task_id,payload):
    model=payload.get('model')
    if not isinstance(model,str) or not model or len(model)>160:return False
    from .tasks import Store
    store=Store(fs)
    try:path,task,body,sha=store.read_record(task_id)
    except MethodError:return False
    current=task.get('model_policy')
    if not current:return False
    if current.get('effective_model')==model:return True
    current={**current,'effective_model':model,'effective_status':'observed'}
    try:store.update(task_id,{'model_policy':current},sha)
    except MethodError:return False
    return True

def _checkpoint_open_task(fs,host,session_hash,task_id,next_action,context):
    from .tasks import Store
    _,task,_,_=Store(fs).read_record(task_id)
    if task['status'] in ('done','cancelled'):return None
    from .sessions import save
    return save(fs,host.title()+'-'+session_hash[:32],task_id,['AGENTS.md'],next_action,context)

def handle_payload(host,event,payload,*,open_console=True,_attempt=0):
    """Record a real hook event. Every failure is returned as a warning, never a host block."""
    try:
        require(host in EVENTS and event in EVENTS[host],'invalid_event','Evento de ciclo de vida não suportado.')
        require(type(payload)is dict,'invalid_event','Entrada de hook inválida.')
        require(payload.get('hook_event_name',event)==event,'event_mismatch','Nome do evento diverge do hook.')
        fs=resolve_root(payload.get('cwd'));session_hash,_=session_identity(host,payload.get('session_id'))
        from .project import ensure_writable
        ensure_writable(fs)
        prompt=payload.get('prompt','')
        event_id=_event_id(host,session_hash,event,payload)
        rel=_path(fs,host,session_hash);journal,_=_read(fs,rel)
        task_id=journal.get('task_id') if journal else None
        if event=='UserPromptSubmit':
            if not implementation_intent(prompt):return result('Pedido não classificado como implementação; nenhum serviço ou Task foi iniciado.',tracked=False)
            if journal and any(row['event_id']==event_id for row in journal['events']):return result('Evento repetido; Task e journal não foram duplicados.',tracked=True,task_id=task_id)
            if task_id:
                try:
                    from .tasks import Store
                    if Store(fs).read_record(task_id)[1]['status'] in ('done','cancelled'):task_id=None
                except MethodError:task_id=None
            if task_id is None:
                task=_start_task(fs,host,session_hash,prompt,payload)
                task_id=task['id']
            _observe_model(fs,task_id,payload)
            _,journal,created=_append(fs,host,session_hash,event_id,event,signal='Pedido de implementação recebido pelo host.',state='active',stage='implementation',next_step='Continuar a Task autorizada; registrar bloqueios, revisão e evidências no fluxo canônico.',task_id=task_id)
            if not journal['console_attempted'] and open_console:
                # Claim once before spawning. A failed browser/server never reopens insistently.
                launch_id=digest((host+'\0'+session_hash+'\0console').encode())
                try:
                    rel,journal,_=_append(fs,host,session_hash,launch_id,'console-launch-requested',signal='Console solicitado para esta sessão.',state='active',stage='implementation',task_id=task_id,console={'console_attempted':True,'console_server_status':'starting','browser_status':'not_requested','client_status':'not_confirmed'})
                    entry=Path(__file__).resolve().parents[1]/'omnx.py'
                    args=[sys.executable,str(entry),'--root',str(fs.root),'hook',host,'console-open','--session-hash',session_hash[:24],'--task-id',task_id,'--managed-by','omnx']
                    subprocess.Popen(args,cwd=str(fs.root),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,close_fds=True,start_new_session=(os.name!='nt'),creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS if os.name=='nt' else 0))
                except Exception:
                    _append(fs,host,session_hash,digest((launch_id+'failed').encode()),'console-launch-failed',signal='Console indisponível; acompanhamento local continua.',console={'console_attempted':True,'console_server_status':'unavailable','browser_status':'unavailable','client_status':'not_confirmed'})
            try:
                from . import updates
                if updates.should_check(fs):
                    entry=Path(__file__).resolve().parents[1]/'omnx.py'
                    subprocess.Popen([sys.executable,str(entry),'--root',str(fs.root),'update','auto-check'],cwd=str(fs.root),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,close_fds=True,start_new_session=(os.name!='nt'),creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS if os.name=='nt' else 0))
            except Exception:pass
            return result('Evento automático registrado na Task canônica.',tracked=True,task_id=task_id,journal=rel,console_status=journal.get('console_server_status','starting'))
        if not journal or not task_id:return result('Evento sem Task ativa nesta sessão; nenhum backlog foi criado.',tracked=False)
        if event=='PostToolUse':
            _append(fs,host,session_hash,event_id,event,signal='Atividade de ferramenta observada; conteúdo e argumentos não foram registrados.',state='active',stage='implementation',task_id=task_id,next_step='Continuar a implementação autorizada e registrar evidências observáveis.')
        elif event=='Interrupt':
            checkpoint=_checkpoint_open_task(fs,host,session_hash,task_id,'Retomar a Task canônica; comparar o estado atual antes de continuar.','Interrupção observada pelo hook; conversa e saída das ferramentas não foram armazenadas.')
            _append(fs,host,session_hash,event_id,event,signal='Interrupção observada; checkpoint local disponível.',state='interrupted',stage='implementation',task_id=task_id,next_step='Retomar pelo checkpoint e comparar a Task com o estado atual.')
            return result('Interrupção registrada.',tracked=True,task_id=task_id,checkpoint=checkpoint.get('changed_paths',[]))
        elif event=='Stop':
            _checkpoint_open_task(fs,host,session_hash,task_id,'Retomar pela Task; conclusão não foi inferida.','Turno do host encerrado; tarefa permanece aberta até evidência canônica.')
            _append(fs,host,session_hash,event_id,event,signal='Turno encerrado; conclusão não confirmada.',state='idle',stage='unknown',task_id=task_id,next_step='Retomar ou registrar revisão/bloqueio com evidência. A tarefa não foi concluída.')
        elif event=='SessionEnd':
            _checkpoint_open_task(fs,host,session_hash,task_id,'Retomar pela Task e comparar o estado atual.','Sessão encerrada; tarefa permanece aberta até evidência canônica.')
            _append(fs,host,session_hash,event_id,event,signal='Sessão encerrada; conclusão não confirmada.',state='ended',stage='unknown',task_id=task_id,next_step='Reabra o host e retome pela Task se o trabalho continuar.')
        return result('Sinal de ciclo de vida registrado.',tracked=True,task_id=task_id,journal=rel)
    except MethodError as exc:
        # Parallel host sessions share the canonical Task store. Its metadata
        # lock is intentionally non-blocking; retry this idempotent event a few
        # times so a short concurrent write does not lose the session signal.
        if exc.code in ('locked','stale_state') and _attempt<4:
            time.sleep(.025*(_attempt+1))
            return handle_payload(host,event,payload,open_console=open_console,_attempt=_attempt+1)
        return {'status':'warning','code':'TRACKING_UNAVAILABLE','summary':'Registro OMNX indisponível nesta execução; o host pode continuar sem acompanhamento confirmado.','changed_paths':[],'limitations':[type(exc).__name__]}
    except Exception as exc:
        # Hook failures must not block the user prompt/tool. Do not echo paths,
        # event contents, parser details, or exception text.
        return {'status':'warning','code':'TRACKING_UNAVAILABLE','summary':'Registro OMNX indisponível nesta execução; o host pode continuar sem acompanhamento confirmado.','changed_paths':[],'limitations':[type(exc).__name__]}

def console_open(fs,host,session_hash,task_id):
    from . import launcher
    try:
        from .tasks import Store
        automation_ref=Store(fs).read_record(task_id)[1].get('automation_ref')
        item=launcher.open_console(fs.root,context={'task_id':task_id,'automation_ref':automation_ref})
        server='reused' if item.get('reused') else 'started'
        browser=item.get('browser_status','unavailable')
        details={'console_server_status':server,'browser_status':browser,'client_status':'connected' if item.get('client_connected') else 'not_confirmed'}
        _append(fs,host,session_hash,digest(('console-result\0'+session_hash).encode()),'console-result',signal='Abertura do Console processada; conexão do cliente é verificada separadamente.',state='active',stage='implementation',task_id=task_id,console=details)
        return item
    except Exception:
        _append(fs,host,session_hash,digest(('console-failed\0'+session_hash).encode()),'console-result',signal='Console indisponível; acompanhamento local continua.',task_id=task_id,console={'console_server_status':'unavailable','browser_status':'unavailable','client_status':'not_confirmed'})
        return {'status':'warning','code':'CONSOLE_UNAVAILABLE','summary':'Console indisponível; a captura da Task continua ativa.','changed_paths':[],'limitations':['Acesso local: python <omnx>/scripts/omnx.py console open --root <projeto>']}

def confirm_console(fs,automation_ref,task_id):
    match=re.fullmatch(r'AUTO-([0-9a-f]{24})',automation_ref or '')
    if not match:return False
    try:
        from .tasks import Store
        if Store(fs).read_record(task_id)[1].get('automation_ref')!=automation_ref:return False
    except MethodError:return False
    base=f'.omnx/local/automation/{digest(str(fs.root).encode())}';root=fs.path(base)
    if not root.exists():return False
    ok=False
    for p in itertools.islice(root.glob('*.json'),500):
        try:
            host=p.name.split('-',1)[0];journal,_=_read(fs,p.relative_to(fs.root).as_posix())
            if host not in EVENTS or not journal or journal.get('task_id')!=task_id:continue
            session_hash=journal['session_id_hash'];eid=digest(('client-connected\0'+session_hash).encode())
            _append(fs,host,session_hash,eid,'console-client-connected',signal='Cliente autenticado do Console conectado; leitura humana não é confirmada.',task_id=task_id,console={'client_status':'connected','client_connected_at':now()});ok=True
        except (MethodError,OSError):continue
    return ok

def activity_for_task(fs,task_id):
    """Latest real lifecycle signal for this task in this exact worktree."""
    base=f'.omnx/local/automation/{digest(str(fs.root).encode())}'
    root=fs.path(base)
    if not root.exists():return None
    matches=[]
    for p in itertools.islice(root.glob('*.json'),200):
        try:
            journal,_=_read(fs,p.relative_to(fs.root).as_posix())
            if journal and journal.get('task_id')==task_id:matches.append(journal)
        except (MethodError,OSError):continue
    if not matches:return None
    journal=max(matches,key=lambda x:x['last_signal_at'])
    try:age=(dt.datetime.now(dt.timezone.utc)-timestamp(journal['last_signal_at']).astimezone(dt.timezone.utc)).total_seconds()
    except (MethodError,ValueError):age=None
    fresh=age is not None and 0<=age<=300
    return {'host':journal['host'],'session_ref':journal['host'].title()+'-'+journal['session_id_hash'][:8],'state':journal['state'] if fresh else 'stale','stage':journal['stage'] if fresh else 'unknown','signal':journal['last_signal'] if fresh else 'Sem atividade recente; estado da Task continua separado.','last_signal_at':journal['last_signal_at'],'fresh':fresh,'next_step':journal['next_step'] if fresh else 'Reabra o host e compare o checkpoint com a Task canônica.','console_server_status':journal['console_server_status'],'browser_status':journal['browser_status'],'client_status':journal['client_status'],'client_connected_at':journal['client_connected_at']}

def record_task_transition(fs,task):
    """Mirror real canonical status changes into active worktree journals."""
    state='active' if task['status'] in ('ready','in_progress','review','blocked') else 'ended'
    stage={'blocked':'blocked','review':'review','done':'completed','cancelled':'cancelled'}.get(task['status'],'implementation')
    signal={'blocked':'Task canônica bloqueada.','review':'Task canônica em revisão.','done':'Task canônica concluída com evidência.','cancelled':'Task canônica cancelada.','in_progress':'Task canônica em execução.','ready':'Task canônica pronta.'}.get(task['status'],'Estado canônico atualizado.')
    base=f'.omnx/local/automation/{digest(str(fs.root).encode())}'
    root=fs.path(base)
    if not root.exists():return True
    ok=True
    for p in itertools.islice(root.glob('*.json'),500):
        try:
            host=p.name.split('-',1)[0];journal,_=_read(fs,p.relative_to(fs.root).as_posix())
            if host not in EVENTS or not journal or journal.get('task_id')!=task['id']:continue
            _append(fs,host,journal['session_id_hash'],digest(canonical({'task':task['id'],'sha':fs.hash('.omnx/tasks/'+task['id']+'.md'),'state':task['status']})),'task-state',signal=signal,state=state,stage=stage,task_id=task['id'],next_step=(task.get('blocked_reason') or ('Revisar critérios e evidências.' if stage=='review' else 'Continuar a Task a partir do estado registrado.'))[:500])
        except Exception:ok=False
    return ok

def install_hooks(fs,host,expected_agents_sha256,trust_root,*,remove=False):
    from .project import ensure_writable
    ensure_writable(fs)
    require(trust_root and fs.hash('AGENTS.md')==expected_agents_sha256,'untrusted_bootstrap','Instalação de hooks exige raiz confiada e hash atual de AGENTS.md.',5)
    require(host in EVENTS,'invalid_host','Host sem suporte.')
    if host=='codex':rel='.codex/hooks.json'
    else:rel='.claude/settings.local.json'
    raw=fs.read(rel,1024*1024);old_hash=digest(raw) if raw is not None else None
    if remove and raw is None:return result('Nenhuma configuração local de hooks para remover.',path=rel)
    data=load_data(raw) if raw is not None else {}
    require(type(data)is dict,'invalid_hook_config','Configuração de hooks precisa ser um objeto JSON.')
    if host=='codex':
        hooks=data.get('hooks',{});require(type(hooks)is dict,'invalid_hook_config','Seção hooks do Codex inválida.')
    else:
        hooks=data.setdefault('hooks',{});require(type(hooks)is dict,'invalid_hook_config','Seção hooks do Claude inválida.')
    marker='--managed-by omnx'
    entrypoint=Path(__file__).resolve().parents[1]/'omnx.py'
    command=f'{shlex.quote(sys.executable)} {shlex.quote(str(entrypoint))} hook {host} {{event}} --managed-by omnx'
    event_names=EVENTS[host]
    for event in event_names:
        groups=hooks.get(event,[])
        require(type(groups)is list,'invalid_hook_config',f'Hook {event} precisa ser uma lista.')
        kept=[]
        for group in groups:
            require(type(group)is dict,'invalid_hook_config',f'Grupo {event} inválido.')
            children=group.get('hooks',[]);require(type(children)is list,'invalid_hook_config',f'Handlers de {event} inválidos.')
            filtered=[h for h in children if not (isinstance(h,dict) and marker in h.get('command',''))]
            if filtered:group={**group,'hooks':filtered};kept.append(group)
        if remove:
            if kept:hooks[event]=kept
            else:hooks.pop(event,None)
            continue
        hooks[event]=kept
        new_command=command.format(event=event)
        handler={'type':'command','command':new_command,'timeout':3 if event in ('Interrupt','SessionEnd') else 15}
        if event in ('PostToolUse',):handler['async']=True
        hooks[event].append({'hooks':[handler]})
        changed=True
    if host=='codex':data['hooks']=hooks
    elif hooks:data['hooks']=hooks
    else:data.pop('hooks',None)
    newraw=json_bytes(data)
    if newraw==raw:return result('Hooks OMNX já estão no estado solicitado.',path=rel,sha256=old_hash)
    fs.write(rel,newraw,old_hash,0o600)
    return result('Hooks de projeto instalados sem alterar handlers existentes.' if not remove else 'Somente hooks OMNX foram removidos.',changed_paths=[rel],sha256=digest(newraw),limitations=['Codex exige revisão e confiança da definição em /hooks. Claude Code aplica hooks de projeto conforme trust settings. A instalação não altera arquivos globais.'])
