# AGENTS.md — OMNX Code Project Rules

> Este arquivo sincroniza as regras do CLAUDE.md para todos os agentes de AI
> (Lovable, Cursor, Windsurf, Codex, Jules, etc.). Fonte de verdade: `CLAUDE.md`.
> Gerado e mantido automaticamente pela skill omnx-code. Não edite manualmente.

---

## Stack obrigatória (detalhe: `docs/regras/stack.md`)

- React 18 + TypeScript strict + Vite
- Tailwind CSS + shadcn/ui
- Supabase (auth + database + storage)
- Vercel (deploy) + Cloudflare (DNS/WAF)
- Nunca introduza dependências fora desta stack sem aprovação explícita do usuário

## Regras de segurança (inegociáveis) (detalhe: `docs/regras/seguranca.md`)

- NUNCA use `SUPABASE_SERVICE_ROLE_KEY` no frontend ou em qualquer código client-side
- NUNCA exponha chaves de API, tokens ou secrets em código commitado
- NUNCA crie arquivos `.env` sem garantir que estão listados no `.gitignore`
- Sempre ative Row Level Security (RLS) em todas as tabelas do Supabase
- Sempre use tokens temporários e escopados — nunca chaves de admin para operações de usuário
- Ao detectar qualquer violação dessas regras no código existente, reporte imediatamente antes de continuar
- **Gate de deploy (fail-closed):** antes de qualquer deploy em produção, merge em `main` ou `git push` que dispare a Vercel, execute a skill `/security-auditor` e só prossiga se `security-report/verdict.json` existir com `"gate": "PASS"`. P0/P1 em aberto (ou `❔ não verificado`/`⚠️ ação manual` em P0/P1) BLOQUEIAM — recuse o push/merge até correção + re-teste. Sem `verdict.json` da sessão atual, não publique.
- A correção automática da auditor é opt-in: nunca aplique auto-fix sem confirmação explícita do usuário.

## Regra de UML obrigatório (inegociável) (detalhe: `docs/regras/uml.md`)

- Nenhum código de domínio (models, entidades, schema) é escrito em projeto novo antes de `docs/UML.md` existir e ser aprovado (diagrama de classes/entidades em Mermaid + sequência dos fluxos críticos)
- Em projeto existente sem `docs/UML.md`: nenhum commit novo acontece antes de gerar o UML por engenharia reversa do código/schema real e validar com o usuário
- `docs/UML.md` e `docs/UML.html` são atualizados no mesmo commit que qualquer mudança de entidade, relacionamento ou fluxo crítico — nunca depois
- Toda migration nova (tabela, coluna, função/RPC, trigger, policy) é gatilho obrigatório de atualização do UML; antes de concluir a tarefa, confira se o campo `Atualizado em` do UML cobre a migration mais recente — UML desatualizado é bug, não pendência

## Regra de arquitetura de usuários e multi-tenant (inegociável) (detalhe: `docs/regras/multi-tenant.md` e `docs/regras/niveis-de-acesso.md`)

- Todo sistema é multi-tenant por padrão: tabela de tenants + membership + papéis (roles) entram na primeira migration, antes de qualquer tabela de negócio
- Toda tabela de negócio nova carrega `tenant_id` (FK not-null) desde o dia 1
- Toda política RLS de tabela com `tenant_id` filtra por tenant, não só por `auth.uid()` — evita vazamento entre contas quando o mesmo usuário pertence a mais de um tenant
- Exceção só é válida se o usuário confirmar explicitamente projeto single-tenant, documentado em `docs/ARQUITETURA.md`
- **Gate obrigatório (fail-closed):** nenhum código de autenticação/autorização é commitado, e nenhum deploy acontece, sem `docs/NIVEIS-DE-ACESSO.md` existir com a matriz completa papel × recurso × ação (sem células em branco). Um papel/permissão no código sem entrada no documento é bug, não pendência
- `docs/NIVEIS-DE-ACESSO.md` é atualizado no mesmo commit que cria/altera um papel ou permissão — nunca depois

## Regra de arquitetura de apps e loja de apps (inegociável) (detalhe: `docs/regras/apps-loja-de-apps.md`)

- Todo sistema nasce modular: cada funcionalidade é um app listado num catálogo global (`apps`), e o tenant ativa/desativa cada um numa Loja de Apps interna — nunca código sempre ligado sem fronteira de app
- A tabela de catálogo de apps e a de instalação por tenant (`tenant_apps` ou equivalente) entram na primeira migration, junto com tenants/membership, antes de qualquer tabela de negócio
- Todo requisito funcional do PRD é atribuído a um app específico — nenhuma funcionalidade fica sem app dono
- Toda rota, componente e endpoint/RPC de um app não-core verifica se o app está ativo para o tenant atual, no frontend E no backend (RLS/policy) — nunca confie só na UI escondida
- Desativar um app oculta e bloqueia acesso, nunca apaga dados
- Exceção só é válida se o usuário confirmar explicitamente um app único sem loja, documentado em `docs/ARQUITETURA.md`
- **Gate obrigatório (fail-closed):** mockups gerados por esta skill incluem obrigatoriamente uma tela de Loja de Apps listando o catálogo com estado ativo/inativo, salvo exceção documentada

## Regra de API & webhooks por app (inegociável) (detalhe: `docs/regras/api-webhooks-por-app.md`)

- Todo app do catálogo que expõe API própria e/ou recebe/dispara webhooks documenta em `docs/apps/<app-slug>/API.md` (auth, endpoints, exemplos `curl`, códigos de erro) e/ou `docs/apps/<app-slug>/WEBHOOKS.md` (payloads recebidos e disparados, assinatura HMAC, retry) — nunca um arquivo genérico misturando vários apps
- Cada app com integração tem uma tela de "Integrações" dentro dele mesmo na Loja de Apps: gerar/rotacionar chave de API, cadastrar webhook (URL, eventos, secret gerado pelo sistema), botão de teste e histórico de entregas
- Chaves e secrets nunca ficam em texto plano no banco (hash, mesmo padrão de senha) e nunca são digitados pelo tenant — o sistema sempre gera
- Apenas papel administrativo (conforme `docs/NIVEIS-DE-ACESSO.md`) cria, rotaciona ou revoga chaves/webhooks; toda ação fica auditada
- **Gate obrigatório:** desativar um app na Loja de Apps derruba imediatamente o acesso das chaves/webhooks daquele app — nenhuma credencial fica ativa "esquecida" com o app desligado

## Regra de sistema de tickets de erro (inegociável) (detalhe: `docs/regras/sistema-de-tickets.md`)

- Todo projeto com interface visível ao usuário final precisa de um botão/atalho "Reportar problema" acessível a partir de qualquer tela — nunca escondido em menu de terceiro nível
- Um interceptor de `console.log/warn/error/info` e de `fetch`/XHR roda **desde o boot do app**, mantendo ring buffer em memória (últimas ~100-150 entradas de log, ~30-50 requisições) — sem isso "logs" no ticket fica sempre vazio, porque não dá pra capturar retroativamente o que já foi impresso antes do erro
- A captura de tela é real (via `html2canvas` ou equivalente) e vem **anexada automaticamente por padrão** ao abrir o report — não é um checkbox que o usuário precisa lembrar de marcar
- Ao reportar (ou ao ocorrer um erro não tratado, via error boundary + handler global), a aplicação captura automaticamente: print real, os dois ring buffers (console e rede), rota atual, timestamp, navegador/dispositivo e usuário/tenant — sem exigir que o usuário descreva o erro tecnicamente
- Os tickets caem numa fila interna com status (`novo → em análise → em correção → resolvido`), seja tabela própria no Supabase (com RLS: usuário só cria os próprios, papel responsável lê/atualiza) ou integração com o sistema de suporte do time
- **Gate obrigatório (fail-closed):** nenhum deploy em produção acontece sem o botão de reportar, a captura automática (print real + logs reais, testados forçando um erro de propósito) e a fila estarem funcionais, e sem `docs/SISTEMA-DE-TICKETS.md` documentar todo o fluxo
- `docs/SISTEMA-DE-TICKETS.md` é atualizado sempre que o fluxo de captura ou a fila mudar — nunca depois do deploy

## Regra de banco de dados (inegociável) (detalhe: `docs/regras/migrations.md` e `docs/regras/acesso-supabase.md`)

- TODA alteração no banco Supabase é feita via migration versionada em `supabase/migrations/`
- É PROIBIDO executar SQL direto para mudar o banco: nada de SQL Editor do Supabase, `supabase db execute`, `psql`, ou RPC que rode SQL arbitrário
- Nunca edite uma migration já aplicada — crie uma nova para corrigir
- A migration e o código que depende dela entram no mesmo commit
- `supabase/migrations/` nunca vai no `.gitignore` — é a fonte de verdade do schema
- Leitura (`SELECT`) para inspeção é permitida; qualquer mutação só via migration
- Após aplicar migrations, regenere os tipos: `supabase gen types typescript`

## Regras de Git (inegociáveis) (detalhe: `docs/regras/git.md`)

- `.env`, `.env.*`, `*.pem`, `*.key` e arquivos com chaves sempre no `.gitignore`
- Commits seguem Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Nunca use mensagens genéricas: `update`, `ajustes`, `misc`, `wip`, `temp`, `fix stuff`
- Nunca force-push na branch `main` — o Lovable e o Vercel rastreiam essa branch
- Nunca delete ou renomeie a branch `main` sem reconectar o Lovable e o Vercel

## Regras de acesso Lovable (inegociáveis)

- Nunca remova deploy keys do GitHub Settings deste repositório
- Nunca revogue o OAuth app "Lovable" na conta GitHub
- Nunca renomeie ou transfira o repositório sem antes reconectar no painel do Lovable
- O diretório `.lovable/` e arquivos `lovable.config.*` são somente leitura — nunca edite, mova ou delete sem instrução explícita do usuário seguida de confirmação
- Nunca altere a visibilidade do repositório de forma que bloqueie o acesso do Lovable

## Fluxo de desenvolvimento

- Antes de codar qualquer feature: verifique se existem `PRD.md`, `ROADMAP.md` e `ARQUITETURA.md`
- Se não existirem → crie esses documentos primeiro. Não comece a codar sem eles
- Antes de criar mockups/protótipos: exija `PRD.md`, `ARQUITETURA.md`, `UML.md` e design system (`docs/DESIGN.md` ou `docs/design-system/`) completos
- Mockups vão em `docs/mockups/`, um arquivo HTML por tela, navegáveis via `docs/mockups/index.html`
- Handoffs vão em `docs/handoffs/` (`latest.md`, `HISTORY.md`, `README.md`) — atualize ao final de toda sessão significativa e leia na retomada
- Toda documentação técnica vai para `docs/[NOME].md`
- O `CLAUDE.md` é um índice enxuto — nunca coloque documentação longa diretamente nele
- Ao remover uma feature: delete o código, o doc em `docs/` e a entrada no índice do `CLAUDE.md`

## Handoffs entre sessões

- `docs/handoffs/latest.md` guarda o estado atual do projeto e deve ser lido primeiro quando o usuário pedir para continuar, retomar ou limpar contexto
- `docs/handoffs/HISTORY.md` guarda o histórico cronológico — acrescente, nunca apague
- Atualize o handoff ao final de toda sessão que produzir mudanças significativas
- O handoff é um resumo, não substitui `PRD.md`, `ARQUITETURA.md`, `UML.md` ou outros docs

## Comunicação (detalhe: `docs/regras/comunicacao.md`)

- Responda sempre em português brasileiro
- Seja didático e paciente — assuma que o usuário pode ter conhecimento zero sobre o tema
- Explique o que vai fazer antes de fazer
- Nunca tome ações irreversíveis (deletar dados, force-push, alterar permissões) sem confirmação explícita

---

Se o usuário pedir algo que viole as regras acima (usar `service_role_key`, tornar repo público, force-push em `main`, remover deploy key do Lovable, executar SQL direto no banco em vez de migration, **fazer deploy/merge em `main` sem `security-report/verdict.json` com `gate: PASS`**, **commitar código de autenticação/autorização sem `docs/NIVEIS-DE-ACESSO.md` completo**, **criar tabela de negócio sem `tenant_id` em projeto multi-tenant**, **escrever código de domínio ou commitar sem `docs/UML.md` existir e estar atualizado**, **fazer deploy sem sistema de tickets de erro (botão de reportar + captura automática + fila) e sem `docs/SISTEMA-DE-TICKETS.md` completo**, **criar funcionalidade sem app dono no catálogo ou sem checagem de `tenant_apps.enabled` no backend**), **recuse, explique o motivo e sugira a alternativa segura**.

---

> Sincronizado com `CLAUDE.md` pela skill omnx-code.
> Para documentação completa do projeto, leia o `CLAUDE.md` e os arquivos em `docs/`.
> Versão do template: omnx-code v1.18
