---
name: empire-vibe-coding
description: |
  Framework "vibe coding" completo para apps React + TypeScript + Supabase + Vercel.
  Instala e mantém o CLAUDE.md do projeto seguindo o padrão Empire Business, garante
  que a skill /security-auditor está instalada e atualizada globalmente, e executa
  qualquer trabalho de desenvolvimento guiado pelo CLAUDE.md — com tasks 100% do tempo.

  Use SEMPRE que o usuário pedir para começar um projeto novo, codar qualquer feature,
  estruturar documentação, auditar segurança, ou sempre que mencionar "empire",
  "vibe coding", "empire-vibe-coding", ou pedir para "ativar o framework".
  Em projetos novos, esta skill é o primeiro passo obrigatório antes de qualquer código.
---

# Empire Vibe Coding

> Framework de desenvolvimento orientado a clareza, segurança e documentação viva.
> Tudo que você faz aqui é guiado pelo `CLAUDE.md` do projeto e executado com tasks visíveis.

---

## Versão e configuração

| Campo | Valor |
|-------|-------|
| Versão da skill | **1.1** |
| Security-auditor mínimo requerido | **v1.5** |
| GitHub (esta skill) | https://github.com/Empire-Business/empire-vibe-coding |
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
Task 2: Verificar e instalar/mesclar CLAUDE.md
Task 3: Verificar e instalar/atualizar skill /security-auditor
Task 4: Finalizar setup — marcar setup_complete: true
```

### Task 1 — State document

Crie a pasta `.empire/` e o arquivo `state.json` se ainda não existirem:

```json
{
  "empire_version": "1.0",
  "setup_complete": false,
  "claude_md_installed": false,
  "claude_md_merged_at": null,
  "security_auditor_installed": false,
  "security_auditor_version": null,
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

**Fallback — se git/curl não estiver disponível:**

```bash
mkdir -p ~/.claude/skills/security-auditor/references
cp bundled-skills/security-auditor/SKILL.md ~/.claude/skills/security-auditor/
cp bundled-skills/security-auditor/CHANGELOG.md ~/.claude/skills/security-auditor/
cp bundled-skills/security-auditor/references/*.md ~/.claude/skills/security-auditor/references/
```

> O fallback usa a versão bundled neste repo (pode estar um pouco defasada). Informe ao usuário que a versão instalada é a bundled e recomende fazer `git pull` depois.

Após concluir, atualize no state:
```json
"security_auditor_installed": true,
"security_auditor_version": "<versão instalada>"
```

### Task 4 — Finalizar setup

Marque o setup como concluído:

```json
"setup_complete": true
```

Apresente ao usuário um resumo do que foi feito:

```
✅ Setup Empire Vibe Coding concluído

- CLAUDE.md: [instalado / mesclado com projeto existente]
- /security-auditor: [instalado v1.5 / já estava atualizado v1.X]
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

**2. Ler CLAUDE.md antes de começar**
O `CLAUDE.md` é o ponto de entrada de todo projeto. Leia-o antes de qualquer decisão técnica. Não assuma nada que não esteja documentado lá.

**3. Documentar em `docs/`, indexar no CLAUDE.md**
- Toda documentação técnica vai para `docs/[NOME].md`
- O `CLAUDE.md` é um índice enxuto — aponta para os docs, não os contém
- Após criar ou atualizar qualquer doc, atualize o campo "Atualizado em" da tabela no CLAUDE.md

**4. Sem código morto, sem documentação morta**
Ao remover uma feature ou componente:
- Delete o código
- Delete o arquivo de doc relacionado em `docs/`
- Remova a entrada correspondente no índice do CLAUDE.md
- Remova imports, referências e testes que não servem mais

**5. Seguir a stack obrigatória**
React 18 + TypeScript strict + Vite + Tailwind + shadcn/ui + Supabase + Vercel. Não introduza dependências fora desta stack sem aprovar com o usuário e documentar a decisão em `docs/ARQUITETURA.md`.

**6. Seguir as fases do CLAUDE.md**
Se o projeto ainda não tem PRD, ROADMAP ou ARQUITETURA aprovados → não comece a codar. Siga a trilha obrigatória descrita no CLAUDE.md.

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
Task 1: Atualizar empire-vibe-coding via git pull
Task 2: Verificar versão remota do security-auditor
Task 3: Atualizar security-auditor se necessário
Task 4: Registrar last_update_check no state document
Task 5: Reportar ao usuário o que mudou
```

### Execução

**Task 1 — Atualizar esta skill:**

```bash
cd ~/.claude/skills/empire-vibe-coding
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

**Task 4:** atualize no state do projeto:
```json
"last_update_check": "<data ISO atual>"
```

**Task 5:** apresente ao usuário:
- Versão anterior vs nova da skill empire-vibe-coding (com diff do CHANGELOG)
- Versão do security-auditor antes e depois
- Se alguma das duas estava na versão mais recente, reportar sem ruído

---

## Referências

| Arquivo / URL | Conteúdo |
|---------------|----------|
| `references/modelo-claude.md` | Template padrão do CLAUDE.md a instalar nos projetos |
| `CHANGELOG.md` | Histórico de versões desta skill |
| `bundled-skills/security-auditor/` | Versão bundled do security-auditor (fallback offline) |
| https://github.com/Empire-Business/security-auditor | Repo oficial do security-auditor (fonte primária) |
