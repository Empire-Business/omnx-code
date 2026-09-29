"""Explicit CLI. Remote access is limited to opt-in release checks; no auto-deploy or hidden setup."""
from __future__ import annotations
import argparse
import subprocess
from .core import *

def parser():
    p=argparse.ArgumentParser(description='OMNX local runtime — defaults do not mutate applications.')
    p.add_argument('--root',help='Raiz de governança explícita; não inferida pelo cwd.')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor')
    sub.add_parser('verify-package')
    md=sub.add_parser('method').add_subparsers(dest='action',required=True)
    q=md.add_parser('verify');q.add_argument('--auditor-dir')
    q=md.add_parser('adopt');q.add_argument('--expected-sha256',required=True);q.add_argument('--authority-ref',required=True);q.add_argument('--auditor-dir');q.add_argument('--trusted-auditor-digest')
    r=sub.add_parser('route');r.add_argument('--ux',choices=['UX0','UX1','UX2','UX3'],required=True);r.add_argument('--security',choices=['S0','S1','S2','S3'],required=True);r.add_argument('--operation',choices=['O0','O1','O2','O3'],required=True)
    i=sub.add_parser('init');i.add_argument('--authority-ref',required=True);i.add_argument('--bootstrap-ref',required=True);i.add_argument('--output')
    t=sub.add_parser('task').add_subparsers(dest='action',required=True)
    l=t.add_parser('list');l.add_argument('--status');l.add_argument('--authorization')
    s=t.add_parser('show');s.add_argument('id')
    c=t.add_parser('create');c.add_argument('--data',required=True);c.add_argument('--body-file',required=True)
    for action in ('update','transition'):
        q=t.add_parser(action);q.add_argument('id');q.add_argument('--expected-sha256',required=True);q.add_argument('--data');q.add_argument('--body-file');q.add_argument('--authority-ref')
        if action=='transition':q.add_argument('--to',required=True)
    a=t.add_parser('archive');a.add_argument('id');a.add_argument('--expected-sha256',required=True)
    m=sub.add_parser('migrate').add_subparsers(dest='action',required=True)
    inv=m.add_parser('inventory');inv.add_argument('--paths',nargs='*');inv.add_argument('--output')
    mp=m.add_parser('plan');mp.add_argument('--resolutions');mp.add_argument('--authority-ref',required=True);mp.add_argument('--bootstrap-ref',required=True);mp.add_argument('--output')
    ap=m.add_parser('apply');ap.add_argument('--plan',required=True);ap.add_argument('--approved-digest',required=True)
    for a in ('resume','rollback'):
        q=m.add_parser(a);q.add_argument('id');q.add_argument('--approved-digest',required=True)
    st=m.add_parser('status');st.add_argument('id')
    a=sub.add_parser('audit').add_subparsers(dest='action',required=True)
    q=a.add_parser('catalog');q.add_argument('--family')
    q=a.add_parser('snapshot');q.add_argument('--paths',nargs='+',required=True);q.add_argument('--environment',default='local');q.add_argument('--output')
    q=a.add_parser('request');q.add_argument('--paths',nargs='+',required=True);q.add_argument('--controls',nargs='*',default=[]);q.add_argument('--surfaces',nargs='*',default=[]);q.add_argument('--objective',required=True);q.add_argument('--impact',choices=['S0','S1','S2','S3'],default='S2');q.add_argument('--mode',choices=['design','delta','full'],default='delta');q.add_argument('--task-id');q.add_argument('--orchestrator-id');q.add_argument('--environment',default='local');q.add_argument('--environment-digest');q.add_argument('--environment-observed',action='store_true');q.add_argument('--output')
    for action in ('validate-request','response-template','validate-response','persist'):
        q=a.add_parser(action);q.add_argument('--request',required=True);q.add_argument('--output')
        if action in ('validate-response','persist'):q.add_argument('--response',required=True)
    q=a.add_parser('scan');q.add_argument('--paths',nargs='+',required=True)
    q=sub.add_parser('gate');q.add_argument('--request',required=True);q.add_argument('--response',required=True);q.add_argument('--operation',choices=['local_edit','commit','merge','deploy'],required=True);q.add_argument('--environment',required=True);q.add_argument('--authority-ref');q.add_argument('--environment-digest')
    u=sub.add_parser('update').add_subparsers(dest='action',required=True)
    for action in ('check','plan'):
        q=u.add_parser(action);q.add_argument('--archive',required=True);q.add_argument('--expected-sha256',required=True);q.add_argument('--current-version');q.add_argument('--destination',required=True);q.add_argument('--output')
    q=u.add_parser('apply');q.add_argument('--plan',required=True);q.add_argument('--approved-digest',required=True)
    q=u.add_parser('policy');g=q.add_mutually_exclusive_group(required=True);g.add_argument('--enable',action='store_true');g.add_argument('--disable',action='store_true');q.add_argument('--channel',choices=['stable','rc']);q.add_argument('--check-interval-hours',type=int);q.add_argument('--consent',action='store_true');q.add_argument('--expected-sha256')
    q=u.add_parser('auto-check');q.add_argument('--force',action='store_true')
    q=u.add_parser('remote-check')
    d=sub.add_parser('decision').add_subparsers(dest='action',required=True)
    q=d.add_parser('list');q.add_argument('--status');q.add_argument('--type')
    q=d.add_parser('show');q.add_argument('id')
    q=d.add_parser('create');q.add_argument('--data',required=True)
    q=d.add_parser('revise');q.add_argument('id');q.add_argument('--expected-sha256',required=True);q.add_argument('--data',required=True)
    q=d.add_parser('update');q.add_argument('id');q.add_argument('--expected-sha256',required=True);q.add_argument('--status');q.add_argument('--selected-option');q.add_argument('--feedback');q.add_argument('--authority-ref')
    cns=sub.add_parser('console').add_subparsers(dest='action',required=True)
    q=cns.add_parser('open');q.add_argument('--port',type=int,default=0);q.add_argument('--no-browser',action='store_true')
    q=cns.add_parser('serve');q.add_argument('--port',type=int,default=0);q.add_argument('--no-browser',action='store_true');q.add_argument('--ready-file')
    cns.add_parser('stop')
    q=cns.add_parser('install');q.add_argument('--destination',required=True)
    q=cns.add_parser('register')
    q=cns.add_parser('projects')
    q=cns.add_parser('unregister');q.add_argument('project_id')
    q=cns.add_parser('shortcut');q.add_argument('--destination');q.add_argument('--name',default='OMNX Console')
    s=sub.add_parser('session').add_subparsers(dest='action',required=True)
    q=s.add_parser('check');q.add_argument('id')
    q=s.add_parser('save');q.add_argument('id');q.add_argument('--task-id',required=True);q.add_argument('--paths',nargs='+',required=True);q.add_argument('--next-action',required=True);q.add_argument('--context',default='');q.add_argument('--expected-sha256')
    hooks=sub.add_parser('hooks').add_subparsers(dest='action',required=True)
    for action in ('install','remove'):
        q=hooks.add_parser(action);q.add_argument('host',choices=['claude','codex']);q.add_argument('--trust-root',action='store_true');q.add_argument('--expected-agents-sha256',required=True)
    mods=sub.add_parser('model').add_subparsers(dest='action',required=True)
    q=mods.add_parser('configure');q.add_argument('profile',choices=['deterministic','economical','balanced','advanced']);q.add_argument('--model',dest='model_name');q.add_argument('--effort',choices=['low','medium','high','xhigh']);q.add_argument('--expected-sha256')
    q=mods.add_parser('choose');q.add_argument('--risk',choices=['low','medium','high','critical'],default='medium');q.add_argument('--ambiguity',choices=['low','medium','high'],default='medium');q.add_argument('--verification',choices=['script','objective','judgment'],default='objective');q.add_argument('--no-reasoning',action='store_true')
    q=mods.add_parser('recommend');q.add_argument('--task-id',required=True);q.add_argument('--risk',choices=['low','medium','high','critical']);q.add_argument('--ambiguity',choices=['low','medium','high'],default='medium');q.add_argument('--verification',choices=['script','objective','judgment'],default='objective');q.add_argument('--no-reasoning',action='store_true')
    vis=sub.add_parser('visual').add_subparsers(dest='action',required=True)
    q=vis.add_parser('inspect');q.add_argument('--reference',required=True)
    h=sub.add_parser('hook');h.add_argument('name',choices=['claude','codex']);h.add_argument('event',choices=sorted(set([*('UserPromptSubmit','PostToolUse','Stop','Interrupt','SessionEnd'),'console-open'])));h.add_argument('--managed-by',choices=['omnx'],required=True);h.add_argument('--session-hash');h.add_argument('--task-id')
    q=sub.add_parser('host');q.add_argument('name',choices=['claude','codex']);q.add_argument('--execute',action='store_true');q.add_argument('--trust-root',action='store_true');q.add_argument('--expected-agents-sha256');q.add_argument('host_args',nargs=argparse.REMAINDER)
    return p

def read_text(path):
    p=Path(path).absolute();raw=RootFS(p.parent).read(p.name)
    require(raw is not None,'missing_file','Arquivo de texto não encontrado.',4)
    try:return raw.decode('utf-8')
    except UnicodeError:raise MethodError('encoding','Arquivo precisa ser UTF-8.') from None

def verify_package():
    idx=load_data((PACKAGE/'integrity.json').read_bytes())
    require(idx.get('algorithm')=='sha256','invalid_inventory','Inventário inválido.')
    fs=RootFS(PACKAGE)
    for path,h in idx['files'].items():require(fs.hash(path)==h,'package_modified','Arquivo de pacote foi alterado.',3,path=path)
    actual={p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob('*') if p.is_file() and not ({'.git','__pycache__'}&set(p.parts)) and p.name!='integrity.json'}
    require(actual==set(idx['files']),'unexpected_package_file','Há arquivo inesperado no pacote.',3)
    return result('Bytes correspondem ao inventário. Isto não valida assinatura/autoria.',files_verified=len(actual))

def dispatch(a):
    if a.command=='verify-package':return verify_package()
    if a.command=='hook':
        from . import automation
        if a.event=='console-open':
            require(a.root and a.session_hash and re.fullmatch(r'[0-9a-f]{24}',a.session_hash),'hook_context','Contexto de abertura incompleto.')
            require(a.task_id and re.fullmatch(r'TASK-[A-Za-z0-9][A-Za-z0-9-]{1,90}',a.task_id),'hook_context','Task de abertura inválida.')
            return automation.console_open(RootFS(a.root),a.name,a.session_hash,a.task_id)
        raw=sys.stdin.buffer.read(automation.MAX_INPUT+1)
        require(len(raw)<=automation.MAX_INPUT,'hook_input_limit','Evento de hook excede o limite local.')
        payload=load_data(raw);return automation.handle_payload(a.name,a.event,payload)
    if a.command=='hooks':
        require(a.root,'root_required','Informe --root para instalar hooks no projeto selecionado.')
        from . import automation
        return automation.install_hooks(RootFS(a.root),a.host,a.expected_agents_sha256,a.trust_root,remove=a.action=='remove')
    if a.command=='model':
        require(a.root,'root_required','Informe --root para configurar ou recomendar perfil de modelo.')
        from . import model_policy
        fs=RootFS(a.root)
        if a.action=='configure':return model_policy.configure(fs,a.profile,a.model_name,a.effort,a.expected_sha256)
        if a.action=='choose':
            config,_=model_policy.read(fs)
            return result('Recomendação mecânica; nada foi selecionado ou chamado.',recommendation=model_policy.choose(risk=a.risk,ambiguity=a.ambiguity,verification=a.verification,reasoning_needed=not a.no_reasoning,configured=config))
        return model_policy.recommend(fs,a.task_id,a.risk,a.ambiguity,a.verification,not a.no_reasoning)
    if a.command=='visual':
        require(a.root,'root_required','Informe --root para inspecionar a referência dentro do projeto selecionado.')
        from . import previews
        return previews.inspect_png(RootFS(a.root),a.reference)
    if a.command=='route':
        refs=['references/routing.md']
        if a.ux in ('UX2','UX3'):refs.append('references/ux.md')
        if a.security in ('S2','S3'):refs.append('references/security-integration.md')
        if a.operation in ('O2','O3'):refs.append('references/operations-and-release.md')
        return result('Rota baseada na classificação fornecida; reavalie o diff real.',references=refs,auditor_required=a.security in ('S2','S3'),historical_mockup_sync=False,production_authority_required=a.operation=='O3')
    if a.command=='update':
        from . import distribution as d
        if a.action=='apply':return d.apply(external_data(a.plan),a.approved_digest)
        if a.action in ('check','plan'):return d.plan(a.archive,a.expected_sha256,a.destination,a.current_version)
        from . import updates
        require(a.root,'root_required','Informe --root para a política ou consulta automática local.')
        fs=RootFS(a.root)
        if a.action=='policy':return updates.configure(fs,a.enable if not a.disable else False,a.channel,a.check_interval_hours,a.consent,a.expected_sha256)
        return updates.auto_check(fs,force=True if a.action=='remote-check' else a.force)
    if a.command=='audit' and a.action in ('catalog','validate-request','response-template'):
        from . import audit
        if a.action=='catalog':return result('Selecione controles; isto não cria plano universal.',controls=[c for c in audit.registry()['controls'] if not a.family or c['id'].startswith('SEC-'+a.family+'-')])
        r=external_data(a.request);audit.validate_request(r)
        return audit.response_template(r) if a.action=='response-template' else result('Request estruturalmente válido; permissões declaradas não concedem autoridade.')
    if a.command=='console':
        from . import console as cs
        if a.action=='projects': return result('Catálogo local do Console; não é fonte de verdade do projeto.',projects=cs._catalog_read()['projects'])
        if a.action=='unregister': return result('Projeto removido apenas do catálogo local.',removed=cs.unregister(a.project_id))
        if a.action=='shortcut':
            from . import launcher
            return launcher.create(a.destination,a.name)
        if a.action=='register':
            require(a.root,'root_required','Informe --root para registrar um projeto.')
            return result('Projeto registrado no catálogo local.',project=cs.register(Path(a.root)))
        from . import launcher
        if a.action=='install':return launcher.install(a.destination)
        if a.action=='stop':return launcher.stop_console()
        if a.action=='serve':return cs.serve(Path(a.root) if a.root else None,a.port,not a.no_browser,ready_file=a.ready_file)
        return launcher.open_console(Path(a.root) if a.root else None,a.port,not a.no_browser)
    require(a.root,'root_required','Informe --root para operações que leem/escrevem um projeto.')
    fs=RootFS(a.root)
    if a.command=='decision':
        from .decisions import Store
        store=Store(fs)
        if a.action=='list': return result('Decisões canônicas; nenhuma execução é autorizada por listagem.',decisions=[{'path':p,'sha256':sha,**d} for p,d,sha in (store.read_record(x[1]['id']) for x in store.entries()) if (not a.status or d['status']==a.status) and (not a.type or d['type']==a.type)])
        if a.action=='show':
            path,d,sha=store.read_record(a.id); return result('Decisão lida.',path=path,sha256=sha,decision=d)
        if a.action=='create': return store.create(external_data(a.data,yaml_ok=True))
        if a.action=='revise':return store.revise(a.id,a.expected_sha256,external_data(a.data,yaml_ok=True))
        return store.update(a.id,a.expected_sha256,status=a.status,selected_option=a.selected_option,feedback=a.feedback,authority_ref=a.authority_ref)
    if a.command=='method':
        from . import project as pr
        if a.action=='verify':return pr.verify_adoption(fs,a.auditor_dir)
        return pr.adopt(fs,a.expected_sha256,a.authority_ref,a.auditor_dir,a.trusted_auditor_digest)
    if a.command=='doctor':
        from .project import doctor
        return doctor(fs)
    if a.command in ('init','migrate'):
        from . import migration as m
        if a.command=='init':return m.make_plan(fs,a.authority_ref,a.bootstrap_ref)
        if a.action=='inventory':return m.inventory(fs,a.paths)
        if a.action=='plan':return m.make_plan(fs,a.authority_ref,a.bootstrap_ref,resolutions=external_data(a.resolutions) if a.resolutions else None)
        if a.action=='apply':return m.apply(fs,external_data(a.plan),a.approved_digest)
        if a.action=='resume':return m.resume(fs,a.id,a.approved_digest)
        if a.action=='rollback':return m.rollback(fs,a.id,a.approved_digest)
        return m.status(fs,a.id)
    if a.command=='task':
        from .tasks import Store
        store=Store(fs)
        if a.action=='list':return result('Tasks canônicas; nenhuma escrita.',tasks=[{'path':p,'sha256':sha,**m} for p,m,b,sha in (store.read_record(x[1]['id']) for x in store.entries()) if (not a.status or m['status']==a.status) and (not a.authorization or m['authorization']['status']==a.authorization)])
        if a.action=='show':
            p,m,b,sha=store.read_record(a.id);return result('Task lida.',path=p,sha256=sha,task=m,body=b)
        if a.action=='create':return store.create(external_data(a.data,yaml_ok=True),read_text(a.body_file))
        if a.action=='archive':return store.archive(a.id,a.expected_sha256)
        return store.update(a.id,external_data(a.data,yaml_ok=True) if a.data else {},a.expected_sha256,body=read_text(a.body_file) if a.body_file else None,transition=a.to if a.action=='transition' else None,authority_ref=a.authority_ref)
    if a.command in ('audit','gate'):
        from . import audit
        if a.command=='gate':return audit.gate(fs,external_data(a.request),external_data(a.response),a.operation,a.environment,a.authority_ref,a.environment_digest)
        if a.action=='snapshot':return audit.snapshot(fs,a.paths,a.environment)
        if a.action=='request':return audit.make_request(fs,a.paths,a.controls,a.surfaces,a.objective,a.impact,a.mode,a.task_id,a.orchestrator_id,a.environment,a.environment_digest,a.environment_observed)
        if a.action=='scan':return audit.scan(fs,a.paths)
        r=external_data(a.request);res=external_data(a.response)
        if a.action=='persist':return audit.persist(fs,r,res)
        audit.validate_response(r,res,fs);return result('Identidade, cobertura, evidências e snapshot validados; não é autorização de deploy.')
    if a.command=='session':
        from . import sessions as s
        if a.action=='save':return s.save(fs,a.id,a.task_id,a.paths,a.next_action,a.context,a.expected_sha256)
        return s.check(fs,a.id)
    if a.command=='host':
        raw=fs.read('AGENTS.md');require(raw is not None,'missing_agents','AGENTS.md não existe.',4)
        args=list(a.host_args)
        if args and args[0]=='--':args=args[1:]
        forbidden=('--system-prompt','--system-prompt-file','--append-system-prompt','--append-system-prompt-file','--dangerously-skip-permissions','--dangerously-bypass-approvals-and-sandbox')
        require(not any(arg.split('=')[0] in forbidden for arg in args),'unsafe_host_args','Não substitua instruções/permissões pelo wrapper.')
        command=[a.name]
        if a.name=='claude':command+=['--append-system-prompt-file',str(fs.path('AGENTS.md'))]
        command+=args
        if not a.execute:return result('Plano de inicialização; nenhum host executado.',argv=command,cwd=str(fs.root),agents_sha256=digest(raw),limitations=['Suporte de host real requer teste na versão instalada. Nenhum CLAUDE.md será criado.'])
        require(a.trust_root and a.expected_agents_sha256==digest(raw),'untrusted_bootstrap','Execução exige raiz confiada e hash esperado das instruções.',5)
        require(__import__('shutil').which(a.name),'host_unavailable','CLI do host não encontrada.',4)
        # Forward only after explicit execution/permission; built-in prompt is preserved.
        rc=subprocess.call(command,cwd=fs.root)
        require(rc==0,'host_failed','Host retornou falha.',6,returncode=rc)
        return result('Processo do host encerrado. Verifique evidências específicas da sessão.')
    raise MethodError('unknown_command','Comando não implementado.')

def main():
    try:
        args=parser().parse_args();out=dispatch(args)
        if args.command=='hook':
            if out.get('status')=='warning':print(out['summary'],file=sys.stderr)
            return 0
        code=5 if out.get('decision')=='blocked' or out.get('status')=='needs_review' else 0
        if out.get('decision')=='blocked':out['status']='blocked';out['code']='GATE_BLOCKED'
        emit(out,getattr(args,'output',None));return code
    except MethodError as e:
        if 'args' in locals() and args.command=='hook':
            print('Registro OMNX indisponível; o host continua sem bloqueio.',file=sys.stderr);return 0
        emit({'status':'error','code':e.code,'summary':e.summary,'changed_paths':[],'limitations':[],'details':e.details});return e.exit_code
    except KeyboardInterrupt:
        emit({'status':'cancelled','code':'CANCELLED','summary':'Execução interrompida; consulte journal quando houver mutação iniciada.','changed_paths':[],'limitations':[]});return 8
    except (OSError,ValueError,KeyError,TypeError) as e:
        if 'args' in locals() and args.command=='hook':
            print('Registro OMNX indisponível; o host continua sem bloqueio.',file=sys.stderr);return 0
        # Do not echo raw parser errors, paths or secret-bearing input.
        emit({'status':'error','code':'RUNTIME_ERROR','summary':'Falha local. Nenhum sucesso é inferido; verifique permissões, entradas e journal.','changed_paths':[],'limitations':[],'error_type':type(e).__name__});return 7
