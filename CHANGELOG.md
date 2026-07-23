# Changelog — omnx-code

Histórico de versões da skill. Ao fazer qualquer atualização, registre aqui a versão, data e o que foi adicionado/modificado.

---

## v1.17.1 — 2026-07-23

### Migração de CLAUDE.md antigo para o formato índice — segura, opt-in, não-bloqueante

Adicionado a pedido do usuário: a mudança da v1.17 (CLAUDE.md/AGENTS.md como índice de `docs/regras/`) não pode "quebrar" projetos já configurados por versões anteriores da skill. Esta versão deixa isso explícito e dá um caminho claro e seguro para quem quiser migrar.

### Adicionado
- **`SKILL.md`, Passo 2 ("Ler CLAUDE.md antes de começar")**: nova nota de compatibilidade — um `CLAUDE.md` de versão anterior (regras inline, sem `docs/regras/`) ou um link quebrado para `docs/regras/<nome>.md` nunca bloqueia o trabalho normal; a skill lê o que existir e ignora links mortos, sem parar para reorganizar sozinha.
- **`SKILL.md`, Task 2, Cenário B**: dividido em **B.1** (adicionar regras que faltam — seguro, aditivo, roda direto) e **B.2** (reorganizar regras já escritas inline — delicado, só roda sob pedido explícito do usuário ou confirmação no primeiro setup, nunca automático em projeto já em uso). B.2 segue uma ordem específica para nunca deixar o projeto num estado quebrado: checagem de git limpo → mostrar o plano → criar os arquivos novos em `docs/regras/` primeiro (sem tocar no CLAUDE.md) → só depois editar o CLAUDE.md → mostrar o diff → commit dedicado só para a reorganização → lembrar o usuário que `git revert` desfaz tudo.
- **Gatilhos novos na descrição da skill**: "reorganiza o CLAUDE.md", "migra pro novo formato", "deixa o CLAUDE.md enxuto", "atualiza pro padrão de índice", "meu CLAUDE.md está gigante" — para quem já tem projeto configurado e quer migrar sob demanda.
- **`SKILL.md`, regra 7**: esclarecido que o gate de "extrair conteúdo grande para docs/regras/" vale para conteúdo que **a própria skill está escrevendo agora**, não para retroagir sobre conteúdo pré-existente sem pedido do usuário — evita que uma tarefa de código dispare uma reorganização não solicitada como efeito colateral.

---

## v1.17 — 2026-07-23

### CLAUDE.md e AGENTS.md viram índices — conteúdo completo migra para docs/regras/

Adicionado a pedido do usuário: `references/modelo-claude.md` estava passando de 600 linhas e crescendo a cada gate novo, o que aumenta o custo de toda sessão nova (o CLAUDE.md é lido no início de todo trabalho). A partir desta versão, o template nasce como índice — cada regra tem um resumo de 1-2 frases + link — e o conteúdo completo de cada regra vive em um arquivo próprio.

### Adicionado
- **`references/regras/*.md`** (18 arquivos novos): cada regra inegociável do projeto (segurança, banco de dados, multi-tenant, apps & loja de apps, UML, níveis de acesso, sistema de tickets, acesso ao Supabase, migrations, git, trilha obrigatória, PRD/ROADMAP/ARQUITETURA/mockups, stack, comunicação, deploy, handoffs, checklist de entrega, testes) agora tem um arquivo próprio e completo, extraído sem perda de conteúdo do `modelo-claude.md` anterior.
- **`references/modelo-claude.md` reescrito**: de ~620 linhas para um índice enxuto com tabela "Índice de Regras" (resumo + link para `docs/regras/<nome>.md`) e a tabela "Índice de Documentos" já existente, mantida.
- **`references/modelo-agents.md`**: cada seção ganhou um ponteiro `(detalhe: docs/regras/<nome>.md)` para a versão completa da regra, mantendo o corpo do arquivo condensado como já era.
- **`SKILL.md`, Task 2**: Cenário A agora copia `references/regras/*.md` para `docs/regras/*.md` no projeto do usuário, junto com o `CLAUDE.md`. Cenário B (merge) foi reescrito para, além de nunca perder informação do usuário, extrair qualquer seção de regra que hoje esteja inline no `CLAUDE.md` do usuário para `docs/regras/<nome>.md`, deixando só a linha de índice.
- **`SKILL.md`, regra 7**: passou a codificar o gate contínuo — não é só uma regra de instalação inicial. Qualquer regra nova ou seção existente que cresça além de ~15-20 linhas direto no `CLAUDE.md`/`AGENTS.md` deve ser extraída para `docs/regras/` antes da tarefa ser considerada concluída.

---

## v1.16 — 2026-07-23

### Regra 24 — Arquitetura de Apps & Loja de Apps interna obrigatória

Adicionado a pedido do usuário: todo sistema criado por esta skill nasce modular por padrão — cada funcionalidade do produto é modelada como um app listado num catálogo, e o produto expõe uma Loja de Apps interna onde o tenant ativa/desativa cada app. É o mesmo raciocínio da regra 21 (multi-tenant): decompor em apps desde o início é barato, fatiar um monólito depois é caro.

### Adicionado
- **Regra 24 (`SKILL.md`) — "Arquitetura de Apps & Loja de Apps interna"**: define catálogo de apps (tabela global com `slug`, `is_core`, dependências), instalação por tenant (`tenant_apps`), gate de acesso em runtime (frontend E backend/RLS, nunca só UI escondida) e a tela de Loja de Apps. Exceção só é válida com confirmação explícita do usuário para app único, documentada em `docs/ARQUITETURA.md`.
- **Gate 1.6c (UML)**: diagrama de classes agora inclui obrigatoriamente `App` e `TenantApp` como entidades.
- **Fluxo de Mockups**: inventário de telas exige obrigatoriamente uma tela de Loja de Apps (P0 mesmo sem menção explícita no PRD); Task 7 de validação confere se ela está atualizada com o catálogo; novo item na tabela de anti-padrões.
- **`references/modelo-claude.md`**: nova seção "🧩 Arquitetura de Apps & Loja de Apps Interna (INEGOCIÁVEL)"; Etapa 1 (PRD) ganha a seção "Apps do produto"; Etapa 3 (Arquitetura) e Etapa 3b (mockups) atualizadas; nova linha no Índice de Documentos; novo bloco no Checklist de Entrega ("Arquitetura de Apps & Loja de Apps"); "Trilha Obrigatória" (FASE 0 e FASE 2) atualizada.
- **`references/modelo-agents.md`**: nova seção "Regra de arquitetura de apps e loja de apps (inegociável)", sincronizada com o CLAUDE.md, e item novo na lista de violações que devem ser recusadas.
- **Descrição da skill**: menciona explicitamente que todo sistema gerado nasce modular com Loja de Apps interna.

---

## v1.15 — 2026-07-22

### Gate 1.6d — Sistema de tickets de erro obrigatório antes de deploy

Adicionado a pedido do usuário: nenhum sistema com interface visível ao usuário final pode ir para produção sem um sistema de tickets de erro funcional.

### Adicionado
- **Gate 1.6d (`SKILL.md`) — "Sistema de tickets de erro antes de deploy"**: fail-closed, independente dos gates 1.6/1.6b/1.6c, exige (1) botão/atalho de "Reportar problema" visível em qualquer tela, (2) função de captura automática — acionada pelo botão OU por error boundary/handler global de erro não tratado — que reúne print de tela, log/stack trace, rota, timestamp, navegador/dispositivo e usuário/tenant, e envia tudo para uma fila interna sem exigir descrição técnica manual do usuário, e (3) `docs/SISTEMA-DE-TICKETS.md` documentando o fluxo completo (como reportar, o que é capturado, onde a fila vive, status `novo → em análise → em correção → resolvido`, quem é notificado). Commit simples em branch de feature apenas avisa; push/merge para `main`/`master`/PR de release/deploy bloqueia sem os três itens.
- **`references/modelo-claude.md`**: nova seção "🎫 Sistema de Tickets de Erro — Obrigatório (BLOQUEIA DEPLOY)" com especificação técnica completa (shape mínimo de tabela Supabase com RLS, error boundary + handler global, fila por status), entrada na tabela "Índice de Documentos", itens novos no "Checklist de Entrega" e no "Checklist de Deploy".
- **`references/modelo-agents.md`**: nova seção "Regra de sistema de tickets de erro (inegociável)" sincronizada com o CLAUDE.md, e item novo na lista de violações que devem ser recusadas.

---

## v1.14 — 2026-07-19

### Regra 20c — Projetos Supabase efêmeros de validação — nunca deletar sozinho

Adicionado a pedido do usuário: quando for preciso validar migrations/RLS/isolamento com escrita real e não houver banco de teste, a skill pode criar um projeto Supabase efêmero via Management API, aplicar migrations e testar — mas nunca pode excluir esse projeto automaticamente. Ao terminar, deve renomear o projeto para o prefixo `DELETAR-`, reportar ao usuário o nome exato, o `project-ref` e a região para exclusão manual, registrar em documento o que foi criado e para quê, e nunca tocar em nenhum projeto Supabase que não tenha criado na mesma execução.

---

## v1.13.1 — 2026-07-17

### Correção do pin de auto-atualização da própria skill

Atualiza o pin `PINNED_TAG`/`PINNED_SHA` da Task 4 (auto-update da omnx-code) para `v1.13.0` (SHA `0cea2e46c38a97d39035be4020f3661c1421662e`), acompanhando o release anterior.

---

## v1.13 — 2026-07-17

### Regra 23 — Documentação obrigatória para integrações de API/webhook

Adicionado a pedido do usuário: toda integração de API externa ou webhook (recebido ou disparado pelo app) agora exige três coisas antes de ser considerada pronta.

### Adicionado
- **Regra 23 (`SKILL.md`) — "Toda integração de API/webhook precisa ser documentada e configurável na UI"**: (1) documentação ampla em `docs/` (o que a integração faz, autenticação, rate limits, comportamento em falha), indexada no CLAUDE.md como as demais docs (regra 7); (2) parte didática na UI de configuração — instruções, tooltips e exemplo de formato quando a integração exigir credencial/URL/parâmetro do usuário, para não depender de suporte ou leitura de código; (3) contrato de dados claro no lado que recebe — método HTTP, schema/exemplo real de payload, campos obrigatórios/opcionais, autenticação esperada, códigos de resposta, e um exemplo de request funcional (`curl` ou equivalente) para qualquer sistema externo integrar sem precisar perguntar. Documentação atualiza no mesmo commit que qualquer mudança de contrato, mesmo princípio já aplicado a migrations (regra 20).

---

## v1.12.1 — 2026-07-17

### Correção do pin de auto-atualização da própria skill

O pin `PINNED_TAG`/`PINNED_SHA` usado pela Task 4 do fluxo de auto-atualização (que verifica a própria omnx-code) ainda apontava para `v1.10.0` — desatualizado desde o release v1.11. Corrigido para apontar para `v1.12.0` (SHA `16fc4be975f0b570757f7ed56aee9aafd7ac678f`), a última tag estável antes deste patch.

---

## v1.12 — 2026-07-17

### Orientação sobre branches soltas sem PR na higiene Git

Ajuste pedido pelo usuário: a Regra 3 (higiene Git, "Modo de Trabalho Normal") ganhou orientação para lidar com branches que ficam soltas sem PR, sem virar automação nova.

### Adicionado
- **Regra 3 (`SKILL.md`) — "Branches soltas sem PR"**: ao rodar a checagem normal de `git status`/`git branch` desta regra, a skill agora avisa se a branch atual (ou outras branches locais) parece velha, divergente de `main`/`master` por muitos commits, ou sem PR aberto associado, e orienta como resolver: rebasear/atualizar com `main` com frequência em vez de deixar divergir, abrir PR cedo (mesmo em draft) para sinalizar trabalho em progresso, e perguntar ao usuário antes de deletar branch claramente abandonada (nunca deletar sozinha).
- **Sugestão de checagem periódica via `/schedule`**: a skill deixa explícito que ela mesma não faz varredura automática/periódica de branches; se o usuário quiser esse tipo de checagem rodando com regularidade, é sugerido usar a skill `/schedule` para configurar um agente agendado — sem instalar nenhuma automação sozinha.

---

## v1.11 — 2026-07-16

### Handoffs entre sessões e economia de tokens

Ajuste pedido pelo usuário: a skill agora cria e mantém docs de handoff em pasta dedicada (`docs/handoffs/`) para que o usuário possa dar CLEAR no contexto e retomar o trabalho em uma nova sessão. Também passa a operar de forma mais enxuta para economizar tokens.

### Adicionado
- **Passo 1.6 no `SKILL.md` — Detecção de Handoff**: roda em toda ativação da skill, detectando pedidos de continuidade ("continuar", "retomar", "handoff", "limpar contexto", "nova sessão", etc.) e lendo `docs/handoffs/latest.md` antes de reconstruir o contexto do zero.
- **Seção "Fluxo de Handoffs" no `SKILL.md`**: workflow completo para criar/atualizar `docs/handoffs/latest.md`, `docs/handoffs/HISTORY.md` e `docs/handoffs/README.md`, com templates, regras de tamanho (máximo 200 linhas para `latest.md`) e anti-padrões.
- **Regra 22 no Modo de Trabalho Normal — Economia de tokens**: diretrizes para evitar releituras desnecessárias, resumir outputs, usar tasks enxutas e confiar no handoff como cache de contexto.
- **Campos no state document**: `handoffs_enabled: true` e `last_handoff_at` para rastrear quando o handoff foi atualizado pela última vez.
- **Mensagem de setup final atualizada**: informa ao usuário sobre `docs/handoffs/` e como pedir handoff.
- **Atualização dos templates**: `references/modelo-claude.md` (seção "Handoffs entre Sessões" + índice de documentos) e `references/modelo-agents.md` (seções "Handoffs entre sessões" e atualização do fluxo de desenvolvimento).
- **Triggers na descrição da skill**: `SKILL.md` frontmatter agora menciona "continuar", "retomar", "handoff", "limpar contexto", "nova sessão" e economia de tokens como contextos de ativação.

---

### Fluxo de Mockups navegáveis e fidelidade ao PRD/design system

Ajuste pedido pelo usuário: a skill agora cria mockups/protótipos navegáveis de forma rigorosa, 100% fiéis ao PRD e ao design system, com um arquivo HTML por tela.

### Adicionado
- **Seção "Fluxo de Mockups" no `SKILL.md`**: workflow completo para criar mockups em `docs/mockups/`, acionado por pedidos de mockup, protótipo, wireframe ou "telas do app".
- **Gate fail-closed para mockups**: nenhum mockup é gerado sem `docs/PRD.md`, `docs/ARQUITETURA.md`, `docs/UML.md` + `docs/UML.html` e design system completo (`docs/DESIGN.md` ou `docs/design-system/`). Se faltar algo, a skill cria a documentação primeiro com o usuário.
- **Um arquivo HTML por tela**: cada tela vira `docs/mockups/tel-XXX-nome.html`; há um `docs/mockups/index.html` como hub de navegação e `docs/mockups/README.md` com rastreabilidade PRD ↔ telas.
- **Design system mínimo exigido**: lista explícita de cores, tipografia, espaçamento, componentes base e layout que o design system deve cobrir antes de iniciar mockups.
- **Validação obrigatória**: task dedicada para verificar cobertura dos requisitos P0/P1 do PRD e fidelidade visual ao design system, registrada em `docs/mockups/VALIDACAO.md`.
- **Mockups autocontidos**: HTML/CSS puro, sem frameworks externos, abrem direto no navegador (`file://`), com links entre telas funcionando e botões sem destino exibindo `alert` descritivo.
- **Rigor de nomenclatura e CSS**: cada tela deve usar o nome `tel-XXX-nome-da-tela.html` e ter CSS inline no próprio arquivo; `styles.css` compartilhado e nomes genéricos são proibidos explicitamente.
- **Atualização dos templates**: `references/modelo-claude.md` (trilha FASE 0, índice de documentos, seção "Etapa 3b — Mockups navegáveis") e `references/modelo-agents.md` (fluxo de desenvolvimento) refletem o novo fluxo e o design system.
- **Triggers na descrição da skill**: `SKILL.md` frontmatter agora menciona mockups, protótipos, wireframes e "telas do app" como contextos de ativação.

### Arquitetura de usuários e multi-tenant obrigatória

Ajuste pedido pelo usuário: todo sistema criado pela skill deve ter arquitetura de usuários bem definida e ser multi-tenant por padrão, com gate fail-closed bloqueando commit/deploy sem documentação de acesso.

### Adicionado
- **Regra 21 (`SKILL.md`)**: todo projeto novo nasce multi-tenant (tenants + membership + papéis antes de qualquer tabela de negócio, `tenant_id` em toda tabela de negócio, RLS sempre filtrando por tenant). Exceção só com confirmação explícita do usuário, documentada em `docs/ARQUITETURA.md`.
- **Gate 1.6b (fail-closed, `SKILL.md`)**: nenhum código de autenticação/autorização é commitado, e nenhum deploy acontece, sem `docs/NIVEIS-DE-ACESSO.md` existir com a matriz completa papel × recurso × ação (sem células em branco). Espelha o gate de segurança (1.6) — os dois são independentes e ambos precisam passar.
- **`docs/NIVEIS-DE-ACESSO.md`** vira documento obrigatório do índice de documentos, com seção própria no template `modelo-claude.md` explicando o que ele precisa conter.
- **Templates sincronizados**: `references/modelo-claude.md` (seção "Arquitetura de Usuários & Multi-Tenant", seção "Níveis de Acesso", trilha obrigatória FASE 0/2/3, checklist de entrega) e `references/modelo-agents.md` (regra dedicada + lista de recusa) ganham as mesmas regras.
- **Gate 1.6c — UML obrigatório antes de codar (fail-closed, `SKILL.md`)**: nenhum código de domínio é escrito em projeto novo sem `docs/UML.md` (diagrama de classes/entidades + sequência dos fluxos críticos, em Mermaid) existir e ser aprovado pelo usuário. Em projeto existente sem UML, nenhum commit novo acontece antes de gerar o diagrama por engenharia reversa do código real e validar com o usuário. Atualização do UML entra no mesmo commit que qualquer mudança de entidade/fluxo — nunca depois. Reflete em `docs/UML.md` no índice de documentos, checklist de entrega e `references/modelo-agents.md`.
- **UML visual obrigatório (`docs/UML.html`, `SKILL.md` + `references/modelo-uml.html`)**: sempre que `docs/UML.md` for criado ou atualizado, a IA também gera `docs/UML.html` — uma página HTML autocontida que renderiza todos os diagramas visualmente com abas navegáveis, tema dark e interatividade (Mermaid.js via CDN). O template base está em `references/modelo-uml.html`. Ambos os arquivos entram no mesmo commit. Checklist de entrega e índice do `modelo-claude.md` atualizados para incluir `UML.html`. Reflete em `modelo-agents.md` (menção a ambos os arquivos).
- **Passo 1.5 — gate de versão da própria omnx-code (fail-closed, roda em TODA ativação da skill)**: antes de qualquer task de setup ou trabalho normal, a skill compara sua versão local (CHANGELOG/`git describe` em disco, sem rede) com a versão remota mais recente (`CHANGELOG.md` do GitHub, com cache de 24h em `.empire/state.json` via `last_version_gate_check`/`last_version_gate_checked_at`). Se local < remota, **bloqueia** qualquer trabalho e dispara a Auto-atualização automaticamente (sem esperar o usuário pedir), parando e pedindo reload após o self-update. Falha de rede sem cache válido exige confirmação explícita do usuário antes de prosseguir (nunca decide sozinho). Fecha a lacuna em que um projeto ficava rodando indefinidamente com uma `omnx-code` desatualizada até alguém lembrar de pedir "atualiza a skill".

### Gate 1.6b relaxado para commit simples

Ajuste pedido pelo usuário: verificação de segurança/documentação de acesso estava travando commits simples em branch de feature, não só PR/publicação.

### Modificado
- **Gate 1.6b (`SKILL.md`)**: deixa de ser fail-closed em todo commit que toca papéis/RLS/auth. Agora só recusa (fail-closed) antes de push/merge para `main`/`master`, PR de release ou deploy — em commit simples de trabalho incremental, apenas avisa e sugere atualizar `docs/NIVEIS-DE-ACESSO.md`, sem bloquear. O gate 1.6 (security-auditor) e o 1.6c (UML) continuam fail-closed como antes — não foram alterados.
- **Regra 1.5 (`SKILL.md`)**: texto atualizado para refletir que 1.6b só é inegociável antes de publicar; 1.6 e 1.6c continuam inegociáveis em todo commit relevante.

### Sugestão de banco de teste/staging para mudanças críticas

Ajuste pedido pelo usuário: a skill deve sugerir (não forçar) testar em banco de teste/staging antes de aplicar migrations arriscadas em produção.

### Adicionado
- **Regra 20b (`SKILL.md`)**: antes de `supabase db push` de migrations que fazem `DROP`/`ALTER` destrutivo, mudança de tipo de coluna, backfill de dados, mudança de RLS em tabela com tráfego, ou qualquer migration sem `DOWN` claro, a skill sugere rodar primeiro num projeto Supabase de staging ou banco local antes de ir para produção. É sugestão (regra 1.5), não gate fail-closed — o usuário decide.

### Nota
Esta entrada ainda não foi commitada nem tagueada no repositório `Empire-Business/omnx-code` — é uma edição local. O mecanismo de self-update desta skill usa tag/SHA pinado (`v1.10.0`), então essas mudanças só se propagam para outras máquinas/projetos depois de commitadas e publicadas com uma nova tag verificada.

---

## v1.10 — 2026-07-10

### Gate real e update verificado (red-team da integração com a security-auditor)

Esta versão nasce do red-team da **costura** com a `/security-auditor`: o "gate" era checkbox e o "update assinado" não tinha no que pinnar. Pódio em `security-auditor/references/hall-of-fame.md` (Rodada 2).

### Adicionado
- **Gate de deploy fail-closed (regra 1.6 no Modo de Trabalho Normal)**: antes de `git push`/`git merge` em `main`, PR de release, `supabase functions deploy` ou `vercel --prod`, a skill lê `security-report/verdict.json` e **recusa** a publicação se `gate != PASS` (ou sem artefato da sessão). Inverte o "sugerir, não forçar" para segurança. Registra `last_audit_gate/at/commit` no state.
- **Passo 0 anti-downgrade no setup**: varre `~/.claude`, `~/.codex`, `~/.agents` (e symlinks quebrados), detecta cópias `< v1.10` ou em `main` e **trava** até o usuário decidir (remover ou linkar para a canônica). Fecha a sombra `~/.agents` com RCE cego.
- **Frontmatter estruturado**: `version`, `min_security_auditor: "1.10"`, `contract_version: 1`.
- **Roteamento de triggers** declarado na descrição: em pedido puro de auditoria, delega à `/security-auditor`; em "atualiza a skill", a omnx-code é dona e atualiza as duas.

### Modificado
- **Update verificado de verdade** (Task 3 e Auto-atualização): `git verify-tag <TAG> && git checkout <TAG>` (verificar antes); removido `|| echo`; `git fetch --tags`; `curl -fsSL --max-time --proto '=https' --tlsv1.2` (falha fechado em erro de rede); comparação semver com `sort -V` (não lexicográfica); sem `git pull --ff-only` automático; sem tag, pede SHA explícito (nunca `main`). State ganha `security_auditor_ref`.
- **Release carimbado (`v1.10.0`)**: o setup (Passo 0), a Task 1-2 e o self-update (Task 4) agora pinnam `v1.10.0` + SHA da auditor (`41fd0d6…`) e da própria omnx (`20289c2…`), validando a tag anotada pelo SHA imutável (nunca "tag mais alta", nunca `main`).
- **Passo 0 varre as DUAS skills e corrige atalhos de forma portavel**: o loop agora cobre `omnx-code` e `security-auditor` em `~/.claude`, `~/.codex`, `~/.agents`; detecta symlink quebrado ou apontando para caminho estrangeiro (ex.: `~/Desenvolvimento/...`, `/Users/<outro>/...`) e recria o atalho para a canonica usando `$HOME` (nunca caminho fixo), para funcionar em qualquer computador.
- **Self-update por último + reload**: a omnx-code atualiza a `security-auditor` primeiro e a si mesma **por último**; após self-update, para e instrui reinvocação (reload) em vez de continuar com regra velha.
- **`AGENTS.md` espelha o gate** (bypass de agentes externos fechado): regra de gate fail-closed + "deploy sem auditoria" na lista de recusa; rodapé `v1.8 → v1.10`.
- **`references/modelo-claude.md` e `modelo-claude.md`**: checklist de Segurança agora exige o `verdict.json` da sessão com `gate: PASS` (anti checkbox-theater); tabela de momentos ampliada (merge em `main`, rotação de secrets/env, migrations/RLS, troca de Supabase).
- **Copy honesta**: "sempre atualizado" → "atualização verificada sob demanda"; "em um comando" → "em um pedido (confirmações por risco)" (`README.md`, `landing/index.html`).
- Versão da skill no frontmatter e CHANGELOG: `1.9 → 1.10`.

### Segurança
- Gate agora tem atuador dentro do que a skill controla (recusa push/merge); o atuador no GitHub/Vercel (status check/branch protection) fica como guia por projeto.
- Update sem tag assinada não degrada mais para `main`: falha fechado pedindo SHA ao usuário.

---

## v1.9 — 2026-07-10

### Modificado
- **Acoplamento com a `/security-auditor` endurecido**: mínimo requerido `v1.5` → `v1.9`; a auditoria agora é tratada como **gate de deploy** (achados P0/P1 bloqueiam até correção + re-teste) e **report-only por padrão** — auto-fix é opt-in e nunca roda sem confirmação explícita do usuário
- **Atualização segura (inegociável)**: eliminado `git pull` cego e qualquer `rm -rf && git clone` no setup e na auto-atualização — tanto da `omnx-code` quanto da `security-auditor`. Novo fluxo: `git fetch` → inspecionar o diff real do `SKILL.md` → aplicar **por tag ou commit verificado** (`git verify-tag` quando houver assinatura) → pedir confirmação antes de alterar a skill. Em conflito, `git stash && git pull --ff-only` (nunca apagar)
- **Task 3 (Setup)** e **Auto-atualização** reescritas para o fluxo verificado; comparação por `curl` do `CHANGELOG.md` remoto mantida apenas como heurística (não é prova de versão)
- `references/modelo-claude.md` e `modelo-claude.md`: checklist de Segurança agora exige que nenhum P0/P1 fique em aberto antes do deploy
- `README.md` e `landing/index.html`: copy atualizada de "correção automática" para "correção assistida" e de "git pull" para "atualização verificada"
- Versão da skill no frontmatter do `SKILL.md`: `1.8` → `1.9`; `omnx_version` no state document: `1.8` → `1.9`

### Segurança
- Fecha o vetor de RCE em massa de `git pull` cego na branch `main`: conteúdo puxado passa a ser tratado como não confiável e aplicado só por referência imutável (tag/SHA), alinhado ao Guardrails v2 da `security-auditor` v1.9

---

## v1.8 — 2026-07-10

### Adicionado
- **Regra absoluta de migrations (Regra 20 no Modo de Trabalho Normal):** toda alteração de banco Supabase DEVE passar por migration versionada em `supabase/migrations/`. SQL direto é proibido para qualquer mutação — SQL Editor do painel, `supabase db execute`, `psql`, RPCs de SQL arbitrário e DDL/DML inline no código. Cobre tabelas, colunas, índices, enums, constraints, extensões, functions, triggers, views, policies de RLS, grants e seeds estruturais
- **Fluxo obrigatório documentado:** `supabase migration new` → editar arquivo → `supabase db push` (ou `db reset` local) → `supabase gen types typescript`
- **Regras inegociáveis:** nunca editar migration já aplicada (criar nova); migration e código dependente entram no mesmo commit; `supabase/migrations/` nunca no `.gitignore`; verificar drift com `supabase migration list`; única exceção é leitura (`SELECT`) para inspeção
- **Seção "Regra de Migrations — SQL Direto Proibido (INEGOCIÁVEL)"** adicionada ao template `references/modelo-claude.md` (instalado como `CLAUDE.md` nos projetos)
- **Seção "Regra de banco de dados (inegociável)"** adicionada ao template `references/modelo-agents.md` (lido por Lovable, Cursor, Windsurf, Codex)
- Itens de migrations adicionados ao checklist de entrega (Banco de Dados) do template do CLAUDE.md
- Frase de recusa do `AGENTS.md` atualizada para incluir "executar SQL direto no banco em vez de migration"

### Modificado
- `omnx_version` no state document: `1.7` → `1.8`
- Versão da skill no frontmatter do `SKILL.md`: `1.7` → `1.8`
- Versão do template no rodapé do `references/modelo-agents.md`: `v1.7` → `v1.8`
- FASE 2 (Banco de Dados) do template do CLAUDE.md reforça que toda alteração é via migration

---

## v1.4 — 2026-03-28

### Adicionado
- **Task 4 — GitHub Setup**: novo passo obrigatório no setup que verifica se o projeto já possui remote `origin` e, caso contrário, cria o repositório GitHub via `gh` CLI
- **Repositório sempre privado**: regra absoluta — todo repositório criado pela skill usa `--private`. A skill se recusa a criar repos públicos mesmo se o usuário pedir explicitamente, e orienta a mudança manual se necessário
- **Verificação de visibilidade pós-criação**: após criar o repo, confirma `isPrivate: true` via `gh repo view --json isPrivate`. Se por algum motivo estiver público, executa `gh repo edit --visibility private` imediatamente
- **Campos no state document**: `github_repo` e `github_repo_private` adicionados ao `.empire/state.json`
- **Regra 6 no Modo de Trabalho Normal**: proíbe qualquer comando que torne o repo público durante o trabalho normal, não só no setup
- **Detecção de `gh` CLI**: se não instalado ou não autenticado, exibe instruções claras e aguarda o usuário resolver antes de continuar

### Modificado
- `omnx_version` no state document: `1.2` → `1.4`
- Summary do setup inclui linha de status do GitHub (criado / já existia / gh não disponível)
- Task 4 (antiga "Finalizar setup") renumerada para Task 5

---

## v1.3 — 2026-03-28

### Modificado
- **Removido `bundled-skills/security-auditor/`**: fallback offline eliminado. Security-auditor é instalado exclusivamente via `git clone https://github.com/Empire-Business/security-auditor`. Se `git` não estiver disponível, a skill retorna erro claro.

---

## v1.2 — 2026-03-28

### Modificado
- **Renomeado de `omnx-vibe-coding` para `omnx-code`**: repo GitHub, nome da skill, comando `/omnx-code`, diretório de instalação `~/.claude/skills/omnx-code`
- **Nova identidade visual na landing page**: fundo preto, verde neon (#00FF88), wordmark OMNX em texto — sem dependência de logo PNG externo
- **Removidas referências ao Empire Business design system**: landing page agora usa design system próprio OMNX

---

## v1.1 — 2026-03-28

### Modificado
- **Security-auditor agora tem repo próprio**: `https://github.com/Empire-Business/security-auditor`. Instalação e atualização usam `git clone` / `git pull` deste repo como fonte primária
- **Verificação de versão remota**: durante setup e auto-update, consulta o CHANGELOG.md remoto via `curl` para comparar com a versão instalada antes de atualizar
- **Fallback bundled mantido**: se git/curl não estiverem disponíveis, usa `bundled-skills/security-auditor/` como fallback offline
- **Auto-atualização aprimorada**: atualiza omnx-code e security-auditor de forma independente, cada uma pelo seu próprio repo

---

## v1.0 — 2026-03-28

### Inicial

- **Setup automático de CLAUDE.md**: instala o template padrão em projetos novos; faz merge inteligente em projetos existentes sem destruir conteúdo do usuário
- **Bundled security-auditor v1.5**: verifica se a skill `/security-auditor` está instalada globalmente e na versão mínima exigida; instala ou atualiza automaticamente
- **State document** (`.empire/state.json`): rastreia fase do projeto (setup vs. trabalho normal), versões instaladas e data do último update check
- **Máquina de estados**: detecta automaticamente se é primeira execução (setup) ou projeto já configurado (modo trabalho)
- **Tasks obrigatórias 100% do tempo**: toda ação é precedida de `TaskCreate`, dando visibilidade ao usuário sobre o que será feito
- **Modo de trabalho normal**: segue CLAUDE.md como índice, documenta em `docs/`, sem código morto nem documentação morta
- **Auto-atualização via git pull**: ao pedido do usuário, faz `git pull` no diretório da skill e re-verifica o security-auditor bundled
- **Landing page bilíngue (PT/EN)**: página estática hospedável no Vercel
- **Versão mínima do security-auditor requerida**: v1.5

---

## Como registrar uma nova versão

Ao fazer qualquer atualização na skill, adicione uma entrada no topo deste arquivo seguindo o padrão:

```markdown
## vX.Y — YYYY-MM-DD

### Adicionado
- [o que foi adicionado]

### Modificado
- [o que foi alterado em algo existente]

### Removido
- [o que foi deletado]

### Corrigido
- [bugs ou comportamentos errados corrigidos]
```

Use **vX.Y** onde X é versão major (mudanças grandes de arquitetura) e Y é minor (novas features ou melhorias). Bump minor para adições; bump major para refatorações completas.
