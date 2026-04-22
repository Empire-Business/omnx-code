---
name: omnx-code
description: |
  Framework "vibe coding" completo para apps React + TypeScript + Supabase + Vercel.
  Instala e mantém o CLAUDE.md do projeto seguindo o padrão OMNX, garante
  que a skill /security-auditor está instalada e atualizada globalmente, e executa
  qualquer trabalho de desenvolvimento guiado pelo CLAUDE.md — com tasks 100% do tempo.

  Use SEMPRE que o usuário pedir para começar um projeto novo, codar qualquer feature,
  estruturar documentação, auditar segurança, ou sempre que mencionar "omnx",
  "omnx-code", "omnx code", ou pedir para "ativar o framework".
  Em projetos novos, esta skill é o primeiro passo obrigatório antes de qualquer código.
---

# OMNX Code

> Framework de desenvolvimento orientado a clareza, segurança e documentação viva.
> Tudo que você faz aqui é guiado pelo `CLAUDE.md` do projeto e executado com tasks visíveis.

---

## Versão e configuração

| Campo | Valor |
|-------|-------|
| Versão da skill | **1.7** |
| Security-auditor mínimo requerido | **v1.5** |
| GitHub (esta skill) | https://github.com/Empire-Business/omnx-code |
| GitHub (security-auditor) | https://github.com/Empire-Business/security-auditor |
| State document | `.empire/state.json` (na raiz do projeto do usuário) |

---

## Passo 0 — Criar tasks antes de qualquer ação

**Esta é a regra mais importante da skill: nunca execute nada sem criar tasks primeiro.**

Antes de fazer qualquer coisa, use `TaskCreate` para listar o que será feito. Isso dá ao usuário visibilidade total sobre cada etapa. Não importa se são 2 ou 20 tarefas — todas precisam aparecer antes de começar.

---

## Passo 1 — Detectar fase do projeto

Ao ser ativada, leia o state document para decidir o que fazer:

```bash
# Verificar se o state document existe
cat .empire/state.json
```

**Lógica de decisão:**

| Situação | Ação |
|----------|------|
| `.empire/state.json` não existe | → Fase de Setup (primeira vez) |
| `setup_complete: false` | → Continuar Setup incompleto |
| `setup_complete: true` | → Modo de Trabalho Normal |

Se o usuário pediu explicitamente "verificar atualizações" ou "atualizar skill" → ir direto para a seção **Auto-atualização**.

---

## Fase de Setup

### Tasks obrigatórias (criar todas antes de começar)

```
Task 1: Inicializar state document (.empire/state.json)
Task 2: Verificar e instalar/mesclar CLAUDE.md + AGENTS.md
Task 3: Verificar e instalar/atualizar skill /security-auditor
Task 4: Verificar e criar repositório GitHub privado
Task 5: Finalizar setup — marcar setup_complete: true
```

### Task 1 — State document

Crie a pasta `.empire/` e o arquivo `state.json` se ainda não existirem:

```json
{
  "omnx_version": "1.7",
  "setup_complete": false,
  "claude_md_installed": false,
  "claude_md_merged_at": null,
  "agents_md_installed": false,
  "agents_md_synced_at": null,
  "security_auditor_installed": false,
  "security_auditor_version": null,
  "github_repo": null,
  "github_repo_private": null,
  "last_update_check": null
}
```

Se o arquivo já existe, leia e preserve todos os campos existentes — apenas atualize os campos que forem alterados nesta execução.

Adicione `.empire/` ao `.gitignore` do projeto **somente** se o usuário não quiser versionar o state. Por padrão, pergunte se deve versionar ou não.

### Task 2 — CLAUDE.md

**Cenário A — CLAUDE.md não existe no projeto:**

Copie o conteúdo de `references/modelo-claude.md` (deste repositório da skill) como `CLAUDE.md` na raiz do projeto do usuário. Informe ao usuário que o arquivo foi criado e que ele deve revisar e personalizar as seções marcadas.

**Cenário B — CLAUDE.md já existe:**

Este é o cenário mais delicado. O objetivo é enriquecer sem destruir. Siga esta lógica:

1. Leia o `CLAUDE.md` existente do usuário
2. Leia o template em `references/modelo-claude.md`
3. Para cada seção do template que **não existe** no CLAUDE.md do usuário → adicione ao final
4. Para seções que **já existem** → preserve o conteúdo do usuário sem alteração
5. Se o CLAUDE.md do usuário tiver blocos de documentação longa (>30 linhas numa seção) que não são índices → mova-os para `docs/[NOME-DA-SECAO].md` e substitua no CLAUDE.md por uma linha de referência assim:

   ```
   → Documentação completa em `docs/[NOME-DA-SECAO].md`
   ```

6. Atualize a tabela "Índice de Documentos" do CLAUDE.md para listar os arquivos movidos para `docs/`

**Regra de ouro do merge:** o usuário nunca perde informação. Tudo que estava lá continua — apenas reorganizado.

Após concluir, atualize no state:
```json
"claude_md_installed": true,
"claude_md_merged_at": "<data ISO atual>"
```

### Task 2b — AGENTS.md (Lovable + outros agentes externos)

O `AGENTS.md` é o padrão aberto lido pelo Lovable, Cursor, Windsurf, Codex e outros agentes. Deve ser criado **na raiz do projeto** junto com o CLAUDE.md e mantido em sincronia com ele.

**Cenário A — AGENTS.md não existe no projeto:**

Copie o conteúdo de `references/modelo-agents.md` (deste repositório da skill) como `AGENTS.md` na raiz do projeto. Informe ao usuário que o arquivo foi criado e que o Lovable já vai lê-lo automaticamente.

**Cenário B — AGENTS.md já existe:**

Este é o cenário de merge. O objetivo é enriquecer sem destruir:

1. Leia o `AGENTS.md` existente
2. Verifique se as seguintes seções obrigatórias existem:
   - `## Regras de acesso Lovable (inegociáveis)`
   - `## Comandos OMNX`
   - `## Regras de segurança (inegociáveis)`
3. Para cada seção obrigatória que **não existe** → adicione ao final sem alterar o restante
4. Para seções que **já existem** → preserve o conteúdo do usuário sem alteração
5. Nunca apague seções existentes

**Regra de ouro do merge:** o usuário nunca perde informação. Tudo que estava lá continua.

**Limite de tamanho:** o Lovable processa melhor arquivos com menos de 10.000 caracteres. Após o merge, verifique o tamanho:

```bash
wc -c AGENTS.md
```

Se ultrapassar 9.500 caracteres, avise o usuário que o Lovable pode truncar o arquivo e sugira mover seções menos críticas para `docs/`.

Após concluir, atualize no state:
```json
"agents_md_installed": true,
"agents_md_synced_at": "<data ISO atual>"
```

### Task 3 — Security Auditor

A skill `/security-auditor` tem seu próprio repositório público:
`https://github.com/Empire-Business/security-auditor`

**Passo 1 — Verificar se está instalada:**

```bash
cat ~/.claude/skills/security-auditor/CHANGELOG.md 2>/dev/null | head -5
```

**Passo 2 — Determinar versão instalada:**

Leia a primeira linha `## vX.Y` do CHANGELOG.md local. Se o arquivo não existir, a skill não está instalada.

**Passo 3 — Obter versão mais recente do GitHub:**

```bash
# Busca a versão mais recente direto do repositório remoto
curl -s https://raw.githubusercontent.com/Empire-Business/security-auditor/main/CHANGELOG.md | head -5
```

Leia a primeira linha `## vX.Y` do resultado para obter a versão mais recente disponível.

**Passo 4 — Agir conforme a comparação:**

| Situação | Ação |
|----------|------|
| Não instalada | `git clone https://github.com/Empire-Business/security-auditor ~/.claude/skills/security-auditor` |
| Versão instalada < versão remota | `cd ~/.claude/skills/security-auditor && git pull` |
| Versão instalada < v1.5 (mínimo) e git pull não ajudou | Reinstalar via clone (ver fallback abaixo) |
| Versão instalada >= versão remota | Nada a fazer — reportar versão encontrada |

Se `git` ou `curl` não estiverem disponíveis, informe ao usuário que a instalação requer `git` e encerre com erro claro.

Após concluir, atualize no state:
```json
"security_auditor_installed": true,
"security_auditor_version": "<versão instalada>"
```

### Task 4 — GitHub: verificar e criar repositório privado

> **Regra absoluta: repositórios criados por esta skill são SEMPRE privados.**
> Nunca crie um repositório público, mesmo que o usuário peça explicitamente.
> Se o usuário insistir em público, explique o risco, recuse-se e oriente-o a mudar a visibilidade manualmente após a criação.

#### Passo 1 — Verificar se já existe remote `origin`

```bash
git remote get-url origin 2>/dev/null
```

| Resultado | Ação |
|-----------|------|
| URL retornada | Remote já existe → registrar no state e pular criação |
| Erro / vazio | Nenhum remote → seguir para Passo 2 |

Se o remote já existe, extraia o nome do repo e registre no state:
```json
"github_repo": "<owner>/<repo>",
"github_repo_private": null
```
(O campo `github_repo_private` fica `null` pois não é possível confirmar visibilidade sem chamar a API — deixe para o usuário verificar se necessário.)

#### Passo 2 — Verificar se `gh` CLI está disponível

```bash
gh --version 2>/dev/null
```

Se `gh` **não estiver disponível**, informe ao usuário:

```
⚠️ GitHub CLI (gh) não encontrado.
Para criar o repositório, instale o gh CLI:
  macOS:   brew install gh
  Linux:   https://cli.github.com/
  Windows: winget install GitHub.cli

Após instalar, execute: gh auth login
Depois chame /omnx-code novamente para concluir o setup.
```

Encerre esta task e registre no state:
```json
"github_repo": null,
"github_repo_private": null
```

#### Passo 3 — Verificar autenticação

```bash
gh auth status 2>/dev/null
```

Se não estiver autenticado, instrua o usuário:

```
⚠️ gh CLI não está autenticado.
Execute: gh auth login
Depois chame /omnx-code novamente para concluir o setup.
```

#### Passo 4 — Determinar nome do repositório

Use o nome da pasta atual como sugestão:

```bash
basename "$PWD"
```

Mostre ao usuário:

```
Vou criar o repositório GitHub privado com o nome: <nome-da-pasta>
Confirma esse nome? (Responda com o nome desejado ou "sim" para confirmar)
```

Aguarde a confirmação antes de criar. Se o usuário fornecer um nome diferente, use o nome informado.

#### Passo 5 — Criar repositório PRIVADO

```bash
gh repo create <nome-confirmado> \
  --private \
  --source=. \
  --remote=origin \
  --push \
  --description "Projeto criado com OMNX Code"
```

> **Flags obrigatórias:** `--private` é não-negociável. Nunca use `--public`.

Se o repositório já existir no GitHub com esse nome, o comando vai falhar. Nesse caso:

```bash
# Tentar adicionar o remote manualmente
gh repo view <owner>/<nome> --json sshUrl,url 2>/dev/null
git remote add origin <url-retornada>
git push -u origin main 2>/dev/null || git push -u origin master
```

#### Passo 6 — Confirmar visibilidade

Após criar, verifique que o repo é realmente privado:

```bash
gh repo view --json isPrivate -q '.isPrivate'
```

Se retornar `false` (público), torne-o privado imediatamente:

```bash
gh repo edit --visibility private
```

#### Passo 7 — Registrar no state

```json
"github_repo": "<owner>/<nome-do-repo>",
"github_repo_private": true
```

#### Aviso obrigatório sobre Lovable

Após o repositório ser criado ou detectado, informe ao usuário:

```
⚠️ Aviso de compatibilidade com Lovable:
Se este projeto estiver conectado ao Lovable (lovable.dev), NUNCA:
  - Remova a deploy key do GitHub Settings
  - Revogue o OAuth app "Lovable" na sua conta GitHub
  - Renomeie ou transfira o repositório sem reconectar no painel do Lovable
  - Force-push na branch main

Essas ações impedem o Lovable de abrir o projeto. A skill /omnx-code protege automaticamente contra essas ações, mas você pode fazê-las manualmente pelo GitHub — então fique atento.
```

---

### Task 5 — Finalizar setup

Marque o setup como concluído:

```json
"setup_complete": true
```

Apresente ao usuário um resumo do que foi feito:

```
✅ Setup OMNX Code concluído

- CLAUDE.md: [instalado / mesclado com projeto existente]
- /security-auditor: [instalado v1.5 / já estava atualizado v1.X]
- GitHub: [criado <owner>/<repo> (privado) / remote já existia / gh não disponível]
- State document: .empire/state.json criado

Agora você pode usar esta skill a qualquer momento para codar,
documentar ou auditar segurança. O CLAUDE.md é o seu índice — tudo parte dele.
```

---

## Modo de Trabalho Normal

Quando `setup_complete: true` e o usuário pede qualquer coisa (codar, refatorar, documentar, deletar feature, etc.):

### Regras obrigatórias

**1. Sempre criar tasks primeiro**
Antes de qualquer ação, crie tasks com `TaskCreate` descrevendo cada etapa. Nunca execute sem tasks visíveis.

**1.5. Sugerir, não forçar**
Sempre que uma ação de Git pudesse ser arriscada ou não-ideal (como trabalhar em `main`), explique o risco e sugira a alternativa ao usuário. Não bloqueie automaticamente — deixe o usuário decidir. A regra é: informar o risco, esperar confirmação, executar.

**2. Ler CLAUDE.md antes de começar**
O `CLAUDE.md` é o ponto de entrada de todo projeto. Leia-o antes de qualquer decisão técnica. Não assuma nada que não esteja documentado lá.

**3. Fazer higiene Git antes de tocar no código**
Antes de implementar qualquer funcionalidade, correção ou documentação, verifique:

```bash
git status --short
git branch --show-current
git remote get-url origin 2>/dev/null
```

Use essa checagem para decidir o fluxo:
- Se houver mudanças locais não relacionadas ou ambíguas, pare e peça direção ao usuário. Não misture trabalho novo com alteração antiga.
- Se estiver em `main` ou `master`, sugira ao usuário: "⚠️ Você está na branch '{branch_atual}'. Recomendo criar uma branch dedicada antes de prosseguir. Deseja que eu crie uma branch?" Aguarde confirmação antes de continuar.
- Se já estiver em uma branch de tarefa compatível com o pedido atual, pode continuar nela. Se a branch atual não corresponder ao escopo, sugira criar outra branch.

**4. Toda nova funcionalidade recomenda-se em branch separada**
Para qualquer trabalho novo fora de setup e auto-atualização, recomenda-se usar branch dedicada. Isso inclui `feature`, `fix`, `docs`, `refactor`, testes e tarefas técnicas.

Padrão de nome:

```text
feat/<slug-curto>
fix/<slug-curto>
docs/<slug-curto>
refactor/<slug-curto>
test/<slug-curto>
chore/<slug-curto>
```

**Fluxo recomendado:**

Ao iniciar trabalho novo em `main` ou `master`, informe ao usuário:

```
⚠️ Branch atual: {branch_atual}
Para este tipo de trabalho, recomendo criar uma branch dedicada.
Deseja que eu crie uma branch (ex: feat/{slug})? Responda com o slug desejado ou "sim" para sugestão automática.
```

Aguarde confirmação do usuário. Se ele recusar, prossiga com cuidado e documente no commit que o trabalho foi feito diretamente na branch principal.

**5. GitHub em modo conservador (`local first`)**
Por padrão, a skill pode:
- Criar branch local
- Editar arquivos
- Gerar commits locais

Por padrão, a skill não pode:
- Fazer `git push`
- Abrir PR
- Fazer merge em branch compartilhada
- Fazer rebase em branch compartilhada
- Alterar remote

Só faça escrita remota quando o usuário pedir explicitamente. Antes de qualquer ação remota, informe claramente qual branch será enviada e qual comando será executado.

**6. Documentar commits com padrão obrigatório**
Todo commit deve seguir `Conventional Commits` no assunto e usar corpo rico quando a mudança não for trivial.

Formato obrigatório:

```text
<tipo>: <resumo curto>

Contexto: <problema, motivação ou objetivo>
Mudanças: <o que foi alterado de forma concreta>
Impacto/Testes: <efeito esperado, riscos e como foi validado>
```

Tipos aceitos no assunto:
- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`

Regras adicionais:
- Não use mensagens genéricas como `update`, `ajustes`, `misc`, `wip` ou `temp`
- Separe commits por unidade lógica quando isso não quebrar o fluxo
- Se não houve teste, diga explicitamente em `Impacto/Testes`

Exemplo bom:

```text
feat: adiciona onboarding guiado no dashboard

Contexto: reduzir abandono na primeira sessão de uso
Mudanças: cria fluxo inicial com tour, estado persistido e CTA final
Impacto/Testes: validado com testes manuais no fluxo principal; sem impacto em usuários já onboarded
```

Exemplo ruim:

```text
update stuff
```

**7. Documentar em `docs/`, indexar no CLAUDE.md**
- Toda documentação técnica vai para `docs/[NOME].md`
- O `CLAUDE.md` é um índice enxuto — aponta para os docs, não os contém
- Após criar ou atualizar qualquer doc, atualize o campo "Atualizado em" da tabela no CLAUDE.md

**8. Sem código morto, sem documentação morta**
Ao remover uma feature ou componente:
- Delete o código
- Delete o arquivo de doc relacionado em `docs/`
- Remova a entrada correspondente no índice do CLAUDE.md
- Remova imports, referências e testes que não servem mais

**9. Seguir a stack obrigatória**
React 18 + TypeScript strict + Vite + Tailwind + shadcn/ui + Supabase + Vercel. Não introduza dependências fora desta stack sem aprovar com o usuário e documentar a decisão em `docs/ARQUITETURA.md`.

**10. Repositório GitHub sempre privado**
Nunca execute `gh repo edit --visibility public` nem qualquer variante que torne o repositório público. Se o usuário pedir explicitamente para tornar o repo público, explique o risco (exposição de variáveis de ambiente, chaves, segredos) e recuse-se. Oriente-o a fazer isso manualmente via GitHub Settings se ainda assim quiser. Ao criar qualquer repo novo durante o trabalho normal (fora do setup), aplique as mesmas regras da Task 4 do setup.

**11. Operações perigosas de Git são proibidas por padrão**
Não execute sem pedido explícito e contexto muito claro:
- `git push --force`
- `git reset --hard`
- `git checkout -- <arquivo>`
- `git clean -fd`
- merge direto em `main` ou `master`

Se alguma dessas ações parecer necessária, pare, explique o risco e peça direção.

**12. Seguir as fases do CLAUDE.md**
Se o projeto ainda não tem PRD, ROADMAP ou ARQUITETURA aprovados → não comece a codar. Siga a trilha obrigatória descrita no CLAUDE.md.

**14. AGENTS.md sempre sincronizado com CLAUDE.md**

O `AGENTS.md` na raiz do projeto é a ponte entre as regras OMNX e ferramentas externas como Lovable, Cursor e Windsurf. Toda vez que o `CLAUDE.md` for modificado por esta skill, verifique se o `AGENTS.md` precisa ser atualizado:

- Se a mudança no CLAUDE.md afeta uma regra refletida no AGENTS.md (stack, segurança, git, Lovable) → atualize a seção correspondente no AGENTS.md
- Se a mudança não tem impacto no AGENTS.md → nenhuma ação necessária
- O AGENTS.md é sempre commitado junto com o CLAUDE.md (mesmo commit, nunca separado)
- Nunca apague seções do AGENTS.md — apenas atualize ou adicione
- Se o usuário editar o AGENTS.md manualmente, preserve o conteúdo e faça merge aditivo (nunca sobrescreva)
- Para verificar sync manualmente: o usuário pode pedir "verificar sync do AGENTS.md" ou "sincronizar AGENTS.md" em qualquer conversa com a skill ativa

**13. Proteção absoluta do acesso Lovable — regra inviolável**

O Lovable acessa o projeto via GitHub (deploy key ou OAuth). Qualquer ação que quebre essa ligação torna o projeto inabrível na plataforma. As regras abaixo são **absolutas** — não há exceção, nem com pedido explícito do usuário:

| Ação proibida | Por que quebra o Lovable |
|---------------|--------------------------|
| `gh repo edit --visibility private` (se já público/acessível ao Lovable) | Bloqueia o token OAuth do Lovable |
| Remover deploy key do repo no GitHub Settings | Lovable perde acesso git |
| Revogar OAuth app "Lovable" nas Settings da conta GitHub | Desconecta todos os projetos |
| `git remote set-url origin <nova-url>` sem avisar | Lovable continua apontando para a URL antiga |
| Renomear o repositório sem atualizar a conexão Lovable | Lovable perde o repo |
| `git push --force` na branch default | Pode corromper o histórico que o Lovable rastreia |
| Deletar a branch default (normalmente `main`) | Lovable perde o ponto de sincronização |
| Deletar ou renomear arquivos de configuração do Lovable (ex: `lovable.config.*`, `.lovable/`) | Quebra o build da plataforma |
| Transferir o repositório para outra conta/org sem reconectar | Lovable perde o repo |

**Regras positivas obrigatórias:**

- Antes de qualquer operação de repo (renomear, transferir, mudar visibilidade, limpar deploy keys), verifique se o Lovable está conectado:
  ```bash
  gh repo view --json collaborators,deployKeys 2>/dev/null
  ```
  Se houver deploy keys ou o nome "Lovable" aparecer em integrações, interrompa a ação e avise o usuário.

- Se o usuário pedir para remover deploy keys ou revogar acessos de terceiros, liste quais apps serão afetados e pergunte explicitamente: "Isso vai desconectar o Lovable do seu projeto. Tem certeza? Esta ação não pode ser desfeita automaticamente."

- Se o repositório for renomeado, oriente o usuário a reconectar manualmente no painel do Lovable antes de fechar a conversa.

- Nunca faça `git push --force` na branch default (normalmente `main`) em projetos conectados ao Lovable. Se for absolutamente necessário, avise o usuário que precisará ressincronizar o Lovable manualmente.

- O arquivo `.lovable/` ou `lovable.config.*` na raiz do projeto deve ser tratado como **somente leitura** por esta skill. Nunca edite, mova ou delete sem instrução explícita do usuário seguida de confirmação dupla.

### Quando usar agentes em time

Para tarefas que envolvem múltiplos domínios em paralelo (ex: migração de banco + atualização de UI + testes), use subagentes com o tool `Agent`. Cada agente recebe:
- O contexto do `CLAUDE.md` do projeto
- Sua tarefa específica
- Instrução para usar `TaskCreate` e não agir fora do escopo dado

---

## Auto-atualização

Quando o usuário pedir "verifique atualizações", "atualize a skill" ou similar:

### Tasks a criar

```
Task 1: Atualizar omnx-code via git pull
Task 2: Verificar versão remota do security-auditor
Task 3: Atualizar security-auditor se necessário
Task 4: Verificar sync do AGENTS.md com o template atualizado
Task 5: Registrar last_update_check no state document
Task 6: Reportar ao usuário o que mudou
```

### Execução

**Task 1 — Atualizar esta skill:**

```bash
cd ~/.claude/skills/omnx-code
git fetch origin
# Salvar versão anterior para comparar depois
ANTES=$(git log -1 --format="%H")
git pull
DEPOIS=$(git log -1 --format="%H")
```

Se `ANTES == DEPOIS`, a skill já estava na versão mais recente.

Para mostrar o que mudou:
```bash
git diff $ANTES $DEPOIS -- CHANGELOG.md
```

**Task 2-3 — Verificar e atualizar security-auditor:**

```bash
# Versão instalada
VERSAO_LOCAL=$(cat ~/.claude/skills/security-auditor/CHANGELOG.md 2>/dev/null | grep -m1 "^## v" | sed 's/## //' | cut -d' ' -f1)

# Versão remota
VERSAO_REMOTA=$(curl -s https://raw.githubusercontent.com/Empire-Business/security-auditor/main/CHANGELOG.md | grep -m1 "^## v" | sed 's/## //' | cut -d' ' -f1)

echo "Instalada: $VERSAO_LOCAL | Remota: $VERSAO_REMOTA"
```

Se `VERSAO_LOCAL < VERSAO_REMOTA` (comparação de string semver), atualizar:
```bash
cd ~/.claude/skills/security-auditor && git pull
```

Se o diretório não for um repo git (instalação via fallback), usar o fluxo de clone descrito na Fase de Setup > Task 3.

**Task 4 — Verificar sync do AGENTS.md:**

Compare as seções obrigatórias do `AGENTS.md` do projeto com o template atualizado em `~/.claude/skills/omnx-code/references/modelo-agents.md`:

```bash
# Verificar se as seções obrigatórias existem no AGENTS.md do projeto
grep -c "## Comandos OMNX\|## Regras de acesso Lovable\|## Regras de segurança" AGENTS.md 2>/dev/null || echo "0"
```

Se retornar menos de 3 (alguma seção obrigatória faltando):
- Adicione as seções faltantes ao final do `AGENTS.md` do projeto (nunca sobrescreva)
- Inclua no commit da Task 5 do state

Se o `AGENTS.md` não existir no projeto atual, crie-o a partir do template (mesmo fluxo da Task 2b do setup).

**Task 5:** atualize no state do projeto:
```json
"last_update_check": "<data ISO atual>",
"agents_md_synced_at": "<data ISO atual>"
```

**Task 6:** apresente ao usuário:
- Versão anterior vs nova da skill omnx-code (com diff do CHANGELOG)
- Versão do security-auditor antes e depois
- Se alguma das duas estava na versão mais recente, reportar sem ruído

---

## Troca de Projeto Supabase

**Gatilhos:** "trocar projeto Supabase", "migrar Supabase", "novo projeto Supabase", "recriar Supabase", "mudar projeto Supabase", "reconstruir migrations", "reconstruir edge functions", ou qualquer variação que indique que o usuário quer apontar o projeto para um Supabase diferente.

> Este fluxo garante que migrations, edge functions, variáveis de ambiente e o state do projeto sejam migrados com segurança para o novo projeto Supabase, sem perda de dados nem configuração manual.

### Tasks obrigatórias (criar todas antes de começar)

```
Task 1: Auditar configuração Supabase atual
Task 2: Vincular ao novo projeto Supabase
Task 3: Aplicar todas as migrations no novo projeto
Task 4: Fazer deploy de todas as edge functions no novo projeto
Task 5: Atualizar variáveis de ambiente (.env e Vercel)
Task 6: Validar conectividade e registrar no state
```

---

### Task 1 — Auditar configuração Supabase atual

Colete tudo que existe no projeto atual antes de tocar em qualquer coisa:

```bash
# Verificar se Supabase CLI está instalado
supabase --version 2>/dev/null || echo "CLI não encontrado"

# Verificar se o projeto tem configuração Supabase local
cat supabase/config.toml 2>/dev/null | head -20

# Listar migrations existentes (ordem cronológica)
ls -1 supabase/migrations/ 2>/dev/null || echo "Pasta de migrations não encontrada"

# Listar edge functions existentes
ls -1 supabase/functions/ 2>/dev/null || echo "Nenhuma edge function encontrada"

# Verificar qual projeto está vinculado atualmente
supabase status 2>/dev/null || echo "Não vinculado a nenhum projeto"

# Mostrar variáveis de ambiente sensíveis (apenas nomes, não valores)
grep -E "SUPABASE|VITE_SUPABASE" .env* 2>/dev/null | sed 's/=.*/=<REDACTED>/'
```

Apresente o resultado ao usuário como um inventário:

```
📋 Inventário Supabase atual:
- Projeto vinculado: <project-ref ou "nenhum">
- Migrations: <N arquivos> — lista com nomes e datas
- Edge Functions: <lista de nomes ou "nenhuma">
- Variáveis detectadas: SUPABASE_URL, SUPABASE_ANON_KEY, [outras]
```

Se a pasta `supabase/` não existir, avise o usuário:

```
⚠️ Pasta supabase/ não encontrada neste projeto.
Este projeto não tem infraestrutura Supabase local versionada.
Não há migrations nem edge functions para migrar.
Deseja continuar apenas para atualizar as variáveis de ambiente?
```

Aguarde confirmação antes de prosseguir.

---

### Task 2 — Vincular ao novo projeto Supabase

**Passo 1 — Verificar login no Supabase CLI:**

```bash
supabase projects list 2>/dev/null || echo "Não autenticado"
```

Se não autenticado, instrua o usuário:

```
⚠️ Supabase CLI não está autenticado.
Execute: supabase login
Após fazer login, retorne e continue este fluxo.
```

Pare aqui e aguarde. Não prossiga sem autenticação.

**Passo 2 — Obter o Project Ref do novo projeto:**

Pergunte ao usuário:

```
Qual é o Project Ref do novo projeto Supabase?
(Encontre em: app.supabase.com → seu projeto → Settings → General → Reference ID)
Formato: 26 caracteres alfanuméricos — ex: abcdefghijklmnopqrstuvwxyz
```

Aguarde a resposta. Valide o formato (26 caracteres alfanuméricos). Se inválido, peça novamente.

**Passo 3 — Desvincular projeto atual e vincular ao novo:**

```bash
# Desvincular o projeto atual (se houver)
supabase unlink 2>/dev/null || true

# Vincular ao novo projeto
supabase link --project-ref <PROJECT_REF>
```

O CLI vai pedir a database password do novo projeto. Informe ao usuário que ele precisará digitar manualmente quando solicitado.

Após vincular, confirme:

```bash
supabase status
```

---

### Task 3 — Aplicar todas as migrations no novo projeto

> **Atenção:** Este passo aplica todas as migrations em ordem no banco do novo projeto. Se o banco já tiver dados ou schema parcial, pode haver conflito. Avise o usuário antes de executar.

```
⚠️ Você está prestes a aplicar <N> migrations no projeto <PROJECT_REF>.
Se o banco já tiver tabelas criadas manualmente, pode haver conflito.
Recomendo que o banco esteja vazio antes de continuar.
Confirma? (sim/não)
```

Aguarde confirmação. Se o usuário confirmar:

```bash
# Visualizar quais migrations serão aplicadas (dry-run)
supabase db push --dry-run 2>/dev/null || supabase migration list

# Aplicar as migrations
supabase db push
```

Se `supabase db push` não estiver disponível na versão do CLI, usar:

```bash
supabase db reset --linked
```

**Tratamento de erros:**

| Erro | Ação |
|------|------|
| `already exists` em alguma tabela | Listar qual migration causou o conflito e perguntar ao usuário se deseja pular ou parar |
| Falha de conexão | Verificar se o project-ref está correto e se a senha do banco foi informada |
| Permissão negada | O token de login pode não ter acesso ao projeto — pedir ao usuário para verificar no painel Supabase |

Após aplicar, confirme quantas migrations foram rodadas:

```bash
supabase migration list
```

---

### Task 4 — Deploy de todas as edge functions no novo projeto

```bash
# Listar todas as edge functions disponíveis
ls supabase/functions/ 2>/dev/null
```

Se não houver edge functions, pule esta task e informe ao usuário.

Se houver funções:

```bash
# Deploy de todas as funções de uma vez
supabase functions deploy --project-ref <PROJECT_REF>
```

Se o projeto preferir deploy individual (mais seguro para detectar erros por função):

```bash
# Para cada função listada na Task 1:
for fn in supabase/functions/*/; do
  fn_name=$(basename "$fn")
  echo "Deploying $fn_name..."
  supabase functions deploy "$fn_name" --project-ref <PROJECT_REF>
done
```

**Tratamento de erros por função:**

| Erro | Ação |
|------|------|
| Falha de build (TypeScript) | Mostrar o erro ao usuário e perguntar se quer pular a função problemática |
| Timeout de deploy | Tentar novamente. Se persistir, orientar o usuário a fazer deploy manual pela UI do Supabase |
| Variável de ambiente faltando | Listar as variáveis ausentes — serão configuradas na Task 5 |

Apresente um resumo:

```
✅ Edge Functions:
  - minha-funcao: deploy OK
  - outra-funcao: FALHOU (ver erro acima)
```

---

### Task 5 — Atualizar variáveis de ambiente

**Passo 1 — Obter as novas credenciais do projeto:**

```bash
# Buscar automaticamente via CLI (se tiver acesso)
supabase status --output json 2>/dev/null
```

Se o comando retornar os dados, extraia automaticamente:
- `API URL` → novo `SUPABASE_URL` / `VITE_SUPABASE_URL`
- `anon key` → novo `SUPABASE_ANON_KEY` / `VITE_SUPABASE_ANON_KEY`

Se não retornar, peça ao usuário:

```
Por favor, forneça as novas credenciais do projeto Supabase:
(Encontre em: app.supabase.com → seu projeto → Settings → API)

1. Project URL (ex: https://abcxyz.supabase.co)
2. anon public key (começa com eyJ...)
```

**Passo 2 — Atualizar `.env` local:**

> Nunca sobrescreva o `.env` inteiro. Apenas substitua as linhas de variáveis Supabase, preservando o resto.

Para cada variável identificada na Task 1, substitua o valor no `.env`:

```bash
# Exemplo de substituição segura (sem apagar outras variáveis)
# Apenas linhas com SUPABASE ou VITE_SUPABASE são alteradas
```

Use o Edit tool para fazer substituições cirúrgicas no `.env`, uma variável por vez.

**Passo 3 — Atualizar variáveis de ambiente no Vercel (se aplicável):**

Verifique se o projeto está conectado ao Vercel:

```bash
vercel env ls 2>/dev/null || echo "Vercel CLI não disponível ou projeto não vinculado"
```

Se disponível, liste as variáveis existentes e pergunte ao usuário se deseja atualizar:

```
Detectei que este projeto está conectado ao Vercel.
Deseja que eu atualize as variáveis de ambiente lá também?
(Isso vai sobrescrever SUPABASE_URL e SUPABASE_ANON_KEY no Vercel)
```

Se confirmar:

```bash
# Remover as antigas e adicionar as novas
vercel env rm SUPABASE_URL production --yes 2>/dev/null || true
vercel env add SUPABASE_URL production <<< "<novo-valor>"

vercel env rm VITE_SUPABASE_URL production --yes 2>/dev/null || true
vercel env add VITE_SUPABASE_URL production <<< "<novo-valor>"

# Repetir para ANON_KEY
```

**Passo 4 — Atualizar secrets nas edge functions:**

Se o projeto usa `supabase secrets set`:

```bash
# Listar secrets atuais
supabase secrets list --project-ref <PROJECT_REF>
```

Se houver secrets além das chaves padrão (ex: STRIPE_SECRET_KEY, RESEND_API_KEY), informe ao usuário que eles precisam ser reconfigurados manualmente:

```
⚠️ Os seguintes secrets precisam ser reconfigurados manualmente no novo projeto:
  - STRIPE_SECRET_KEY
  - RESEND_API_KEY
  - [outros listados]

Execute para cada um:
  supabase secrets set NOME_DO_SECRET=valor --project-ref <PROJECT_REF>

Ou configure pela UI: app.supabase.com → projeto → Edge Functions → Secrets
```

---

### Task 6 — Validar conectividade e registrar no state

**Passo 1 — Testar conexão com o novo projeto:**

```bash
# Verificar se consegue conectar e listar tabelas
supabase db execute --sql "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" 2>/dev/null
```

Se retornar as tabelas esperadas, a migração foi bem-sucedida.

**Passo 2 — Registrar no state document:**

Atualize `.empire/state.json` com:

```json
"supabase_project_ref": "<novo-project-ref>",
"supabase_migrated_at": "<data ISO atual>",
"supabase_migrations_applied": <N>,
"supabase_functions_deployed": ["lista", "de", "funções"]
```

**Passo 3 — Commit das mudanças de ambiente:**

> **Nunca versione valores de chaves de API.** Apenas arquivos de configuração estrutural.

```bash
# Verificar o que mudou
git diff --name-only
```

Faça commit apenas de arquivos estruturais (ex: `supabase/config.toml` se foi alterado). Nunca commite `.env`.

**Passo 4 — Resumo final para o usuário:**

```
✅ Migração Supabase concluída

Projeto anterior: <ref-antigo ou "não vinculado">
Projeto novo:     <novo-project-ref>

Migrations aplicadas:  <N>/<total>
Edge Functions:        <N OK> / <M com falha — ver log acima>
Variáveis .env:        atualizadas
Vercel:                [atualizado / pulado / não detectado]
Secrets:               [configurados / requer ação manual — ver lista acima]

Próximos passos obrigatórios antes de usar o projeto:
□ Teste o login e criação de conta no novo Supabase
□ Verifique se as RLS policies foram criadas pelas migrations
□ Reconfigure manualmente os secrets listados acima (se houver)
□ Se usa Lovable: faça um deploy de teste no Lovable para confirmar conectividade
```

---

## Referências

| Arquivo / URL | Conteúdo |
|---------------|----------|
| `references/modelo-claude.md` | Template padrão do CLAUDE.md a instalar nos projetos |
| `references/modelo-agents.md` | Template padrão do AGENTS.md (Lovable, Cursor, Windsurf, Codex) |
| `CHANGELOG.md` | Histórico de versões desta skill |
| https://github.com/Empire-Business/security-auditor | Repo oficial do security-auditor |
| https://agents.md | Padrão aberto AGENTS.md — referência da especificação |
