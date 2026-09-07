'use strict';
// Data from projects is never interpolated into executable HTML or handlers.
const $ = (s, root = document) => root.querySelector(s);
const $$ = (s, root = document) => [...root.querySelectorAll(s)];
const S = {csrf: '', projects: [], selected: '', view: 'home', query: '', detail: null, loading: false, generation: 0};
const labels = {backlog:'Backlog', ready:'Pronto', in_progress:'Em execução', blocked:'Bloqueado', review:'Revisão', done:'Concluído', cancelled:'Cancelado', pending:'Precisa de você', approved:'Aprovado', changes_requested:'Aguardando a IA', rejected:'Não aprovado', superseded:'Substituído'};
const columns = ['backlog','ready','in_progress','blocked','review','done','cancelled'];
const priorityLabels = {low:'Baixa',medium:'Normal',high:'Alta',critical:'Crítica'};
const moves = {backlog:['ready'],ready:['in_progress','blocked'],in_progress:['review','blocked'],blocked:['ready','in_progress'],review:['in_progress','blocked'],done:[],cancelled:[]};
function el(tag, props = {}, ...children) {
  const n = document.createElement(tag);
  for (const [k,v] of Object.entries(props)) {
    if (v === undefined || v === null) continue;
    if (k === 'class') n.className = v;
    else if (k === 'text') n.textContent = v;
    else if (k.startsWith('on') && typeof v === 'function') n.addEventListener(k.slice(2).toLowerCase(), v);
    else if (k === 'dataset') Object.assign(n.dataset, v);
    else if (k in n && !k.startsWith('aria')) n[k] = v;
    else n.setAttribute(k, String(v));
  }
  for (const child of children.flat(Infinity)) {
    if (child !== null && child !== undefined) n.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return n;
}
const button = (text, fn, cls='secondary', props={}) => el('button',{class:cls,text,onClick:fn,type:'button',...props});
const badge = (text, cls='neutral') => el('span',{class:'badge '+cls,text});
const empty = (title, text) => el('div',{class:'empty'},el('h2',{text:title}),el('p',{text}));
function toast(message) { const n=$('#toast');n.textContent=message;n.classList.remove('hidden');clearTimeout(toast.timer);toast.timer=setTimeout(()=>n.classList.add('hidden'),6000); }
function showError(error) { toast(error.message || 'Não foi possível confirmar esta operação. Atualize antes de repetir.'); }
async function api(path, options={}) {
  const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),15000);
  try {
    const response=await fetch(path,{credentials:'same-origin',cache:'no-store',signal:controller.signal,...options,
      headers:{...(options.method ? {'Content-Type':'application/json','X-OMNX-CSRF':S.csrf} : {}),...(options.headers||{})}});
    const data=await response.json();
    if (!response.ok) { const err=new Error(data.summary||data.error||'Falha local.');err.code=data.error;throw err; }
    return data;
  } catch(e) { if(e.name==='AbortError') throw new Error('Não recebi a confirmação. Atualize o estado antes de repetir uma ação.');throw e; }
  finally {clearTimeout(timer);}
}
async function post(path,body) {return api(path,{method:'POST',body:JSON.stringify(body)});}
function reqid() {return crypto.randomUUID();}
function query(args) {return new URLSearchParams(args).toString();}
function shortPath(path) {return String(path||'').split(/[\\/]/).slice(-3).join('/');}
function dateLabel(value) {if(!value)return 'Não informado';const d=new Date(value);return Number.isNaN(+d)?'Não informado':d.toLocaleString('pt-BR');}
function selected() {return S.projects.find(p=>p.workspace_id===S.selected);}
function matches(text) {return !S.query||String(text).toLocaleLowerCase('pt-BR').includes(S.query.toLocaleLowerCase('pt-BR'));}
function title(titleText, subtitle, action=null) {return el('div',{class:'hero'},el('div',{},el('div',{class:'eyebrow',text:'OMNX · CONTROLE DO PROJETO'}),el('h1',{text:titleText}),el('p',{text:subtitle})),action);}
function stat(number,label) {return el('div',{class:'stat'},el('strong',{text:number}),el('span',{text:label}));}
function versionBadge(p) {
  const v=p.version_status||{};
  const text={current:'Método atual nesta instalação',outdated:'Atualização local disponível',newer:'Projeto usa versão mais nova',unknown:'Versão não identificada',invalid:'Versão inválida'}[v.status]||'Versão não identificada';
  return badge(text,v.status==='outdated'?'blue':v.status==='current'?'good':'neutral');
}
function errorsPanel(p) {
  if(!p.partial&&!p.read_only)return null;
  return el('div',{class:'notice',role:'note'},el('strong',{text:p.read_only?'Acompanhamento em modo leitura':'Alguns itens precisam de atenção'}),
    ...(p.read_only_reasons||[]).map(x=>el('p',{text:x})),
    p.partial?el('p',{text:`${p.errors.length} aviso(s). Os itens válidos continuam disponíveis; a contagem pode ser parcial.`}):null,
    button('Ver diagnóstico',()=>diagnostic(p)));
}
function projectCard(p) {
  const c=p.counts||{},counts=c.by_status||{};
  return el('article',{class:'card project-card'},
    el('div',{class:'project-top'},el('span',{class:'project-icon',text:(p.name||'P').slice(0,1).toUpperCase()}),el('div',{},el('h3',{text:p.name}),el('small',{class:'muted',text:shortPath(p.path)}))),
    el('div',{class:'badges'},versionBadge(p),p.read_only?badge('Somente leitura'):null),
    !p.available?el('p',{class:'muted',text:'Pasta indisponível. Localize novamente; nenhum arquivo foi apagado.'}):
      el('div',{class:'project-counts'},el('span',{},el('b',{text:counts.in_progress||0}),' em execução'),el('span',{},el('b',{text:counts.blocked||0}),' bloqueadas'),el('span',{},el('b',{text:c.pending_decisions||0}),' decisões')),
    el('div',{class:'project-actions'},button('Abrir projeto',()=>chooseProject(p.workspace_id),'primary',{disabled:!p.available}),button('Remover da lista',()=>removeProject(p),'text-button')));
}
function chooseProject(wid,view='tasks') {S.selected=wid;$('#projectSelect').value=wid;S.detail=null;S.view=view;render();}
async function refresh(force=false) {
  if(S.loading)return;S.loading=true;$('#refreshBtn').disabled=true;
  try {
    const data=await api('/api/projects'+(force?'?refresh=1':''));S.projects=data.projects;
    const select=$('#projectSelect');select.replaceChildren(el('option',{value:'',text:'Todos os projetos'}));
    for(const p of S.projects)select.append(el('option',{value:p.workspace_id,text:p.name+' · '+shortPath(p.path)}));
    if(!S.projects.some(p=>p.workspace_id===S.selected))S.selected='';select.value=S.selected;
    $('#consoleVersion').textContent='OMNX '+data.overview.bundle_version;
    $('#decisionBadge').textContent=data.overview.pending_decisions||'';
    $('#freshness').textContent='Estado lido em '+dateLabel(data.refreshed_at)+' · Não representa presença da IA em tempo real';
    S.detail=null;await render();
  } catch(e) {
    $('#freshness').textContent='Não foi possível atualizar. O estado exibido pode estar desatualizado.';
    if(!S.projects.length)$('#content').replaceChildren(empty('O painel precisa de atenção',e.message),button('Tentar novamente',()=>refresh(true)));
    showError(e);
  } finally {S.loading=false;$('#refreshBtn').disabled=false;}
}
async function projectData(force=false) {
  if(S.detail&&S.detail.workspace_id===S.selected&&!force)return S.detail;
  const wid=S.selected;const p=await api('/api/project?'+query({workspace_id:wid,...(force?{refresh:'1'}:{})}));
  if(wid===S.selected)S.detail=p;return p;
}
function home() {
  const ps=S.projects.filter(p=>matches(p.name+' '+p.path));const available=ps.filter(p=>p.available);
  const pending=available.reduce((n,p)=>n+(p.counts?.pending_decisions||0),0);
  const active=available.reduce((n,p)=>n+(p.counts?.by_status?.in_progress||0),0);
  const blocked=available.reduce((n,p)=>n+(p.counts?.by_status?.blocked||0),0);
  const hero=title('Clareza sobre o que vem a seguir.', 'Acompanhe entregas, veja telas e tome decisões. A execução continua no seu Codex ou Claude Code.',button('＋ Adicionar projeto',addProject,'primary'));
  const attention=el('div',{class:'attention-grid'},...available.filter(p=>p.counts.pending_decisions).map(p=>el('div',{class:'card attention'},badge('Precisa de você','amber'),el('h3',{text:p.name}),el('p',{text:`${p.counts.pending_decisions} decisão(ões) aguardando sua revisão.`}),button('Ver decisões',()=>chooseProject(p.workspace_id,'decisions')))));
  if(!attention.childNodes.length)attention.append(el('div',{class:'card attention calm'},el('h3',{text:'Nenhuma decisão pendente nos registros carregados.'}),el('p',{text:'Isso não certifica a segurança do produto. Informações desconhecidas e erros de leitura aparecem separadamente.'})));
  return [hero,el('div',{class:'stats'},stat(ps.length,'Cópias de projetos'),stat(active,'Tarefas em execução'),stat(pending,'Decisões para você'),stat(blocked,'Tarefas bloqueadas')),
    el('div',{class:'section-head'},el('h2',{text:'Precisa da sua atenção'})),attention,
    el('div',{class:'section-head'},el('h2',{text:'Seus projetos'}),el('span',{class:'muted',text:'Podem estar em pastas diferentes'})),
    el('div',{class:'projects'},...ps.map(projectCard)),!ps.length?empty('Adicione seu primeiro projeto','A pasta do projeto continua sendo a fonte dos dados. O catálogo guarda apenas sua localização.'):null];
}
async function render() {
  const gen=++S.generation;$$('.nav').forEach(n=>{n.classList.toggle('active',n.dataset.view===S.view);n.setAttribute('aria-current',n.dataset.view===S.view?'page':'false');});
  const content=$('#content');
  if(S.view==='home'){content.replaceChildren(...home().filter(Boolean));return;}
  if(S.view==='projects'){content.replaceChildren(title('Seus projetos','Cada pasta é uma cópia independente. Clones não misturam aprovações.',button('＋ Adicionar projeto',addProject,'primary')),el('div',{class:'projects'},...S.projects.filter(p=>matches(p.name+' '+p.path)).map(projectCard)));return;}
  if(!S.selected){content.replaceChildren(empty('Escolha um projeto','Selecione uma cópia de trabalho no topo ou abra um dos projetos abaixo.'),el('div',{class:'projects'},...S.projects.map(projectCard)));return;}
  content.replaceChildren(empty('Lendo este projeto…','Carregamento local, sem chamada a IA.'));
  try {
    const p=await projectData();if(gen!==S.generation)return;
    let parts=[];
    if(S.view==='tasks')parts=await kanban(p,gen);
    if(S.view==='mockups')parts=await gallery(p,gen);
    if(S.view==='decisions')parts=await decisionList(p,gen);
    if(gen===S.generation)content.replaceChildren(...[errorsPanel(p),...parts].filter(Boolean));
  } catch(e) {if(gen===S.generation)content.replaceChildren(empty('Não foi possível abrir esta visão',e.message),button('Atualizar',()=>refresh(true)));}
}
async function collection(p,name,args={}) {return api('/api/project?'+query({workspace_id:p.workspace_id,collection:name,...args}));}
async function kanban(p,gen) {
  const board=el('div',{class:'kanban','aria-label':'Quadro de tarefas'});
  const pages=await Promise.all(columns.map(status=>collection(p,'tasks',{status,limit:30})));
  for(let i=0;i<columns.length;i++) {
    const status=columns[i],page=pages[i],list=el('div',{class:'column-cards'});
    let loaded=page.items.length;
    const column=el('section',{class:'column '+(status==='blocked'?'is-blocked':''),dataset:{status}},el('h2',{},labels[status],el('span',{text:page.total})),list);
    const append=items=>items.filter(t=>matches(t.title)).forEach(t=>list.append(taskCard(p,t)));
    append(page.items);
    if(page.total>loaded) {
      const more=button('Carregar mais',async()=>{more.disabled=true;try{const next=await collection(p,'tasks',{status,offset:loaded,limit:30});append(next.items);loaded+=next.items.length;if(loaded>=next.total)more.remove();else more.disabled=false;}catch(e){showError(e);more.disabled=false;}},'text-button');column.append(more);
    }
    if(!p.read_only && !['done','cancelled'].includes(status)) {
      column.addEventListener('dragover',e=>{e.preventDefault();column.classList.add('drag-over');});column.addEventListener('dragleave',()=>column.classList.remove('drag-over'));
      column.addEventListener('drop',async e=>{e.preventDefault();column.classList.remove('drag-over');const id=e.dataTransfer.getData('text/plain');if(!/^TASK-[A-Za-z0-9-]+$/.test(id))return;await taskModal(p,id,status);});
    }
    board.append(column);
  }
  return [title(p.name,'Kanban de trabalho registrado. “Em execução” não significa que uma IA está conectada agora.'),board,el('p',{class:'muted',text:'Arraste para preparar uma mudança de estado. Concluir, cancelar ou reabrir exige o fluxo de validação do agente. Cartões ocultos pela paginação continuam nas contagens.'})];
}
function taskCard(p,t) {
  const card=el('article',{class:'task-card',tabIndex:0,role:'button','aria-label':t.title,draggable:!p.read_only&&t.authorization==='authorized'&&!['done','cancelled'].includes(t.status)},
    el('div',{class:'task-top'},badge(priorityLabels[t.priority]||'Normal',t.priority==='high'?'amber':'neutral'),t.authorization!=='authorized'?badge('Não autorizada'):null),
    el('h3',{text:t.title}),t.blocked_reason?el('p',{class:'blocked-note',text:t.blocked_reason}):null,
    el('small',{class:'muted',text:'Atualizada '+dateLabel(t.updated_at)}));
  card.addEventListener('click',()=>taskModal(p,t.id));card.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();taskModal(p,t.id);}});
  card.addEventListener('dragstart',e=>e.dataTransfer.setData('text/plain',t.id));return card;
}
async function gallery(p) {
  const grid=el('div',{class:'mockup-grid'});const page=await collection(p,'mockups',{limit:24});let loaded=page.items.length;
  const add=rows=>rows.filter(m=>matches(m.title+' '+m.name)).forEach(m=>grid.append(el('article',{class:'card mockup'},button(m.kind==='html'?'▧  Abrir tela':'▧  Abrir imagem',()=>mockModal(p,m),'preview-placeholder'),el('h3',{text:m.title}),el('p',{class:'muted',text:m.name}),badge(m.kind==='html'?'Preview estático':'Imagem'),el('small',{class:'muted',text:Math.ceil(m.bytes/1024)+' KiB · carregado ao abrir'}))));
  add(page.items);const parts=[title('Telas de '+p.name,'Propostas e registros históricos. Abrir uma tela não chama IA, não executa seus scripts e não acessa APIs.'),grid];
  if(!loaded)parts.push(empty('Nenhuma tela cadastrada','Peça ao agente para salvar uma imagem ou HTML estático na pasta de propostas UX do projeto.'));
  if(page.total>loaded) {const more=button('Carregar mais telas',async()=>{more.disabled=true;try{const next=await collection(p,'mockups',{offset:loaded,limit:24});add(next.items);loaded+=next.items.length;if(loaded>=next.total)more.remove();else more.disabled=false;}catch(e){showError(e);more.disabled=false;}});parts.push(more);}
  parts.push(el('p',{class:'muted',text:'HTML é uma visualização protegida: scripts, formulários enviados, navegação e recursos externos são bloqueados. Para jornadas interativas, use um preview externo confiável no fluxo do agente, não reduza a proteção do painel.'}));return parts;
}
async function decisionList(p) {
  const page=await collection(p,'decisions',{limit:100});const list=el('div',{class:'decision-list'});
  const add=rows=>rows.filter(d=>matches(d.title)).sort((a,b)=>(a.status==='pending'?-1:0)-(b.status==='pending'?-1:0)).forEach(d=>list.append(el('article',{class:'card decision-card'},badge(d.legacy_unverified?'Registro antigo — revisar':labels[d.status]||d.status,d.status==='pending'?'amber':'neutral'),el('h3',{text:d.title}),el('p',{class:'muted',text:d.type==='ux'?'Experiência do produto':d.type==='product'?'Decisão de produto':'Decisão técnica · somente leitura no painel'}),button('Ver proposta e histórico',()=>decisionModal(p,d.id)))));
  add(page.items);const parts=[title('Decisões de '+p.name,'Aprovar registra sua escolha. Não publica, não altera o PRD sozinho e não acorda automaticamente uma IA.'),list];
  if(!page.items.length)parts.push(empty('Nenhuma decisão registrada','A IA deve abrir uma decisão somente quando houver uma escolha humana necessária.'));
  let loaded=page.items.length;if(page.total>loaded){const more=button('Carregar mais decisões',async()=>{more.disabled=true;try{const n=await collection(p,'decisions',{offset:loaded,limit:100});add(n.items);loaded+=n.items.length;if(loaded>=n.total)more.remove();else more.disabled=false;}catch(e){showError(e);more.disabled=false;}});parts.push(more);}return parts;
}
function modal(...children) {const d=$('#modal');$('#modalBody').replaceChildren(...children.filter(Boolean));if(!d.open)d.showModal();d.scrollTop=0;}
function closeModal() {$('#modal').close();}
async function taskModal(p,id,target=null) {
  try {
    const t=await api('/api/task?'+query({workspace_id:p.workspace_id,id}));
    const actions=el('div',{class:'actions'},button(t.authorization.status==='authorized'&&!['done','cancelled'].includes(t.status)?'Copiar prompt para continuar':'Copiar prompt para investigar',()=>promptModal(p,id),'primary'),button('Pedir explicação à IA',()=>promptModal(p,id,'explain')));
    const parts=[el('h2',{text:t.title}),el('div',{class:'badges'},badge(labels[t.status]),badge(t.authorization.status==='authorized'?'Execução autorizada':'Sem autorização de execução')),el('p',{class:'muted',text:p.name+' · '+shortPath(p.path)}),el('h3',{text:'Escopo registrado'}),el('div',{class:'body-text',text:t.body}),el('h3',{text:'Para considerar pronto'}),el('ul',{},...t.acceptance.map(a=>el('li',{text:a}))),actions];
    if(t.blocked_reason)parts.splice(3,0,el('div',{class:'notice',text:'Bloqueio: '+t.blocked_reason}));
    if(!p.read_only&&t.authorization.status==='authorized'&&(moves[t.status]||[]).length){
      const select=el('select',{'aria-label':'Novo estado'},el('option',{value:'',text:'Escolha o próximo estado'}),...moves[t.status].map(s=>el('option',{value:s,text:labels[s]})));
      if(target&&(moves[t.status]||[]).includes(target))select.value=target;
      const reason=el('input',{placeholder:'Motivo, se for bloquear','aria-label':'Motivo do bloqueio',maxLength:2000});
      const confirm=button('Registrar estado',async()=>{if(!select.value)return;confirm.disabled=true;try{await post('/api/task/transition',{workspace_id:p.workspace_id,task_id:id,expected_sha256:t.sha256,to:select.value,blocked_reason:reason.value||undefined,request_id:reqid()});closeModal();await refresh(true);toast('Estado registrado. Isso não iniciou uma IA.');}catch(e){showError(e);confirm.disabled=false;}});
      parts.push(el('div',{class:'subpanel'},el('h3',{text:'Organizar o quadro'}),select,reason,confirm,el('p',{class:'muted',text:'A engine confere a autorização e as dependências. Uma mudança aqui não executa código.'})));
    }
    parts.push(el('details',{},el('summary',{text:'Detalhes técnicos'}),el('pre',{text:JSON.stringify({id:t.id,revision:t.sha256,impact:t.impact,delivery:t.closure?.delivery},null,2)})));
    modal(...parts);
  } catch(e){showError(e);}
}
function previewElement(grant) {
  if(grant.kind==='image')return el('img',{src:grant.url,alt:'Proposta visual do projeto',class:'preview-image',onError:()=>toast('Não foi possível exibir a imagem; ela pode ter mudado. Reabra o preview.')});
  return el('iframe',{src:grant.url,sandbox:'',title:'Visualização estática isolada da proposta',class:'preview-frame',referrerPolicy:'no-referrer'});
}
async function mockModal(p,m) {
  try {const grant=await post('/api/preview',{workspace_id:p.workspace_id,preview_id:m.id});modal(el('h2',{text:m.title}),el('p',{class:'muted',text:m.path}),el('div',{class:'preview'},previewElement(grant)),el('p',{class:'muted',text:'Visualização protegida: sem scripts ou APIs. A proposta histórica não precisa acompanhar futuras mudanças.'}));}catch(e){showError(e);}
}
async function decisionModal(p,id) {
  try {
    const d=await api('/api/decision?'+query({workspace_id:p.workspace_id,id}));
    const parts=[el('h2',{text:d.title}),el('p',{class:'decision-question',text:d.question}),el('div',{class:'badges'},badge(d.legacy_unverified?'Registro antigo — requer reconfirmação':labels[d.status]||d.status),badge('Revisão '+d.revision))];
    let previewValid=true;
    if(d.subject_ref) {
      parts.push(el('p',{class:'muted',text:'Proposta: '+d.subject_ref}));
      try {const grant=await post('/api/preview',{workspace_id:p.workspace_id,decision_id:id,expected_sha256:d.sha256});parts.push(el('div',{class:'preview'},previewElement(grant)));}
      catch(e){previewValid=false;parts.push(el('div',{class:'notice',text:e.message}));}
    }
    const options=el('fieldset',{class:'options'},el('legend',{text:'Escolha proposta'}));
    for(const o of d.options)options.append(el('label',{class:'option'},el('input',{type:'radio',name:'decision-option',value:o.id,checked:d.selected_option===o.id,disabled:d.status!=='pending'||p.read_only||d.legacy_unverified}),el('span',{},el('b',{text:o.label}),d.recommended_option===o.id?badge('Recomendação registrada','blue'):null,el('small',{text:o.description}))));
    if(d.options.length)parts.push(options);
    if(!d.subject_ref)parts.push(el('p',{class:'muted',text:'Sem arquivo de tela vinculado: a decisão abrange somente a pergunta e as opções desta revisão, não um preview externo.'}));
    if(d.feedback.length)parts.push(el('div',{class:'subpanel'},el('h3',{text:'Feedback registrado'}),...d.feedback.map(f=>el('p',{class:'body-text',text:f}))));
    const canDecide=!p.read_only&&!d.legacy_unverified&&d.status==='pending'&&['ux','product'].includes(d.type);
    if(canDecide){
      const feedback=el('textarea',{placeholder:'Descreva um ajuste ou observação…','aria-label':'Feedback da decisão',maxLength:4096});
      const error=el('p',{class:'form-error',role:'alert'});let sending=false;options.addEventListener('change',()=>{error.textContent='';});
      const actions=el('div',{class:'actions'});
      const send=async status=>{
        if(sending)return;const option=$('input[name="decision-option"]:checked',options)?.value;
        if(status==='approved'&&d.options.length&&!option){error.textContent='Escolha uma opção antes de aprovar.';return;}
        if(status==='changes_requested'&&!feedback.value.trim()){error.textContent='Descreva o ajuste solicitado.';return;}
        sending=true;$$('button',actions).forEach(b=>b.disabled=true);error.textContent='';
        try{await post('/api/decision/update',{workspace_id:p.workspace_id,decision_id:id,expected_sha256:d.sha256,status,selected_option:status==='approved'?option:undefined,feedback:feedback.value.trim()||undefined,request_id:reqid()});closeModal();await refresh(true);toast(status==='approved'?'Escolha registrada. Copie o prompt para o agente continuar.':'Resposta registrada. A IA verá o estado quando retomar.');}
        catch(e){error.textContent=e.message;sending=false;$$('button',actions).forEach(b=>b.disabled=false);if(['stale_state','stale_subject'].includes(e.code)){$$('button',actions).forEach(b=>b.disabled=true);actions.append(button('Reabrir revisão atual',()=>decisionModal(p,id)));}}
      };
      actions.append(button('Aprovar proposta',()=>send('approved'),'primary',{disabled:!previewValid}),button('Pedir alteração',()=>send('changes_requested')),button('Não aprovar',()=>send('rejected'),'danger'));
      parts.push(el('h3',{text:'Sua resposta'}),feedback,error,actions,el('p',{class:'muted',text:'Registro de usuário local, não assinatura de identidade. Não autoriza segurança, migração de dados ou produção.'}));
    }else parts.push(el('div',{class:'notice neutral',text:d.status==='changes_requested'?'Você já pediu alterações. A IA precisa reapresentar uma revisão antes de nova aprovação.':d.legacy_unverified?'Uma aprovação antiga da rc.1 não será reaproveitada. Peça à IA para revisar este registro com decision revise.':'Esta decisão é histórica, está em modo leitura ou exige o fluxo técnico apropriado.'}));
    for(const tid of d.task_refs)parts.push(button('Copiar prompt da tarefa relacionada',()=>promptModal(p,tid)));
    const history=el('details',{},el('summary',{text:'Histórico de revisões e limites'}),el('p',{class:'muted',text:'Histórico preservado no registro atômico. Não é atestação independente nem prova de identidade humana.'}));
    for(const e of d.history||[])history.append(el('div',{class:'history-event'},el('b',{text:'Revisão '+e.previous.revision+' · '+(labels[e.previous.status]||e.previous.status)}),el('p',{text:e.previous.selected_option?'Escolha: '+e.previous.selected_option:e.previous.question}),el('small',{text:dateLabel(e.recorded_at)})));
    if(d.legacy_record)history.append(el('p',{text:'Original v1 preservado para rastreabilidade; sua aprovação não foi convertida em aprovação nova.'}));
    parts.push(history);modal(...parts);
  }catch(e){showError(e);}
}
async function promptModal(p,tid,mode='compact') {
  try {
    const r=await api('/api/prompt?'+query({workspace_id:p.workspace_id,task_id:tid,mode}));
    const text=el('textarea',{class:'prompt',value:r.prompt,readOnly:true,'aria-label':'Prompt para copiar'});
    modal(el('h2',{text:'Continuar no seu agente'}),el('p',{class:'muted',text:'O painel não chamou IA. O texto usa IDs e referências, não copia o corpo inteiro de documentos.'}),text,button('Copiar prompt',async()=>{try{await navigator.clipboard.writeText(r.prompt);toast('Prompt copiado. Cole no agente que tem acesso a esta cópia do projeto.');}catch(e){text.focus();text.select();toast('Texto selecionado. Use o comando de copiar do seu computador.');}},'primary'),el('p',{class:'muted',text:r.prompt.length+' caracteres. O consumo de tokens só ocorre quando o agente processar o prompt e os arquivos necessários.'}));
  }catch(e){showError(e);}
}
function addProject() {
  const input=el('input',{class:'wide',placeholder:'/caminho/completo/do/projeto','aria-label':'Pasta do projeto'}),error=el('p',{class:'form-error',role:'alert'});
  const save=button('Adicionar pasta',async()=>{save.disabled=true;try{await post('/api/project/register',{path:input.value.trim()});closeModal();await refresh(true);}catch(e){error.textContent=e.message;save.disabled=false;}},'primary');
  modal(el('h2',{text:'Adicionar um projeto'}),el('p',{text:'Cole o caminho absoluto da pasta. A IA também pode registrá-la com console register, sem você procurar os arquivos.'}),input,error,save,el('p',{class:'muted',text:'Isto só adiciona a localização ao catálogo. Não instala a OMNX no projeto nem altera seus arquivos.'}));
}
function removeProject(p) {modal(el('h2',{text:'Remover apenas da lista?'}),el('p',{text:p.name+' · '+p.path}),el('p',{text:'Nenhum código, tarefa, decisão ou arquivo do projeto será apagado.'}),button('Remover da lista',async()=>{try{await post('/api/project/unregister',{workspace_id:p.workspace_id});closeModal();await refresh(true);}catch(e){showError(e);}},'danger'));}
async function diagnostic(p) {try{const d=await api('/api/diagnostics?'+query({workspace_id:p.workspace_id}));modal(el('h2',{text:'Diagnóstico do acompanhamento'}),el('pre',{class:'diagnostic',text:JSON.stringify(d,null,2)}),el('p',{class:'muted',text:'Leitura somente. Nenhum documento foi consertado ou alterado automaticamente.'}));}catch(e){showError(e);}}
async function bootstrap() {
  // Fragment is not sent in HTTP requests. Remove it before loading project data.
  const fragment=new URLSearchParams(location.hash.slice(1));const key=fragment.get('key');history.replaceState(null,'',location.pathname);
  try {const session=key?await api('/api/session',{method:'POST',headers:{'Content-Type':'application/json','X-OMNX-Bootstrap':key},body:'{}'}):await api('/api/session');S.csrf=session.csrf;await refresh();}
  catch(e){$('#freshness').textContent='Sessão local não pareada';$('#content').replaceChildren(empty('Abra o Console pelo ícone ou comando OMNX',e.message+' Não compartilhe a chave de abertura.'));}
}
$$('.nav').forEach(n=>n.addEventListener('click',()=>{S.view=n.dataset.view;render();}));
$('#refreshBtn').addEventListener('click',()=>refresh(true));$('#addProjectBtn').addEventListener('click',addProject);
$('#projectSelect').addEventListener('change',e=>{S.selected=e.target.value;S.detail=null;render();});
let searchTimer;$('#search').addEventListener('input',e=>{S.query=e.target.value;clearTimeout(searchTimer);searchTimer=setTimeout(render,220);});
$('#closeModal').addEventListener('click',closeModal);$('#modal').addEventListener('click',e=>{if(e.target===$('#modal'))closeModal();});
setInterval(()=>{if(S.csrf&&!document.hidden&&!$('#modal').open&&!S.loading)refresh();},30000);
bootstrap();
