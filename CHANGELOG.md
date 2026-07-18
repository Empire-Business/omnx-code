# Changelog — omnx-code

Histórico de versões da skill. Ao fazer qualquer atualização, registre aqui a versão, data e o que foi adicionado/modificado.

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
