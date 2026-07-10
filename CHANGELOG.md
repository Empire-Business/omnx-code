# Changelog — omnx-code

Histórico de versões da skill. Ao fazer qualquer atualização, registre aqui a versão, data e o que foi adicionado/modificado.

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
