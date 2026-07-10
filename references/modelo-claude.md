# CLAUDE.md

> Este arquivo é o ponto de entrada da IA para este projeto.
> Funciona como um índice: não contém detalhes longos — aponta para os documentos certos.
> Toda instrução técnica detalhada vive em `docs/`. Este arquivo deve permanecer enxuto.

---

## 🔐 Segurança — Skill Obrigatória

**A IA DEVE executar a skill `/security-auditor` nos seguintes momentos, sem exceção:**

| Momento                              | Obrigatório? |
|--------------------------------------|--------------|
| Início do projeto (antes de codar)   | ✅ Sim        |
| Antes de qualquer deploy em produção | ✅ Sim        |
| Após adicionar qualquer integração   | ✅ Sim        |
| Quando solicitado pelo usuário       | ✅ Sim        |

> Toda diretriz, checklist e política de segurança deste projeto vive dentro da skill `/security-auditor`. A IA não deve tentar replicar ou substituir essas instruções aqui.

---

## 🗄️ Banco de Dados — Supabase ou Local?

Antes de iniciar o desenvolvimento, a IA deve perguntar ao usuário qual estratégia de banco deseja usar:

### Opção A — Supabase direto
- O projeto já começa conectado ao Supabase em produção
- Ideal para quem quer avançar rápido e já tem conta no Supabase
- A IA configura a conexão usando **tokens temporários** (veja seção abaixo)

### Opção B — Banco local primeiro (depois migra pro Supabase)
- O projeto começa com um banco PostgreSQL local via Docker
- **Todo o schema, migrations e seeds devem ser escritos desde o início pensando no Supabase**
- A migração para o Supabase deve funcionar sem erros com um único comando
- A IA deve garantir que nenhuma feature use algo incompatível com o Supabase
- Quando o usuário decidir migrar, a IA guia o processo passo a passo

> ⚠️ Se a Opção B for escolhida, a IA deve documentar em `docs/ARQUITETURA.md` como a migração será feita antes de escrever qualquer código.

---

## 🔑 Regras de Acesso ao Supabase (INEGOCIÁVEIS)

### ❌ Proibições absolutas

```
# NUNCA adicionar ao .env:
SUPABASE_SERVICE_ROLE_KEY=...   ← PROIBIDO
```

- A **service role key bypassa toda a segurança (RLS)** do Supabase — nunca deve aparecer no código do projeto, no `.env`, nem em nenhum arquivo versionado
- Se a IA identificar a service role key em qualquer lugar, deve alertar imediatamente e recusar continuar até que seja removida

### ✅ Como a IA acessa o Supabase

A IA deve usar **tokens temporários da conta do Supabase**, gerados via Supabase CLI, que **expiram em 7 dias**:

```bash
# O usuário gera o token assim:
supabase login
# O token fica salvo localmente e expira automaticamente em 7 dias
```

- Esses tokens têm escopo limitado e expiram, reduzindo risco de vazamento
- A cada semana (ou quando expirar), o usuário deve gerar um novo token
- A IA deve lembrar o usuário de renovar o token quando estiver próximo de expirar

---

## 🗃️ Regra de Migrations — SQL Direto Proibido (INEGOCIÁVEL)

**Toda alteração no banco Supabase DEVE passar por uma migration versionada em `supabase/migrations/`.** Nenhuma mudança de banco pode ser feita por SQL direto. O schema do banco é reconstruído 100% a partir das migrations — sem exceção.

### ❌ Caminhos proibidos para alterar o banco

- SQL Editor do painel Supabase (Dashboard → SQL Editor → Run)
- `supabase db execute --sql "..."` ou `supabase db query` para mutação
- `psql -c`, `psql -f` solto, ou qualquer cliente direto rodando DDL/DML
- RPCs que executam SQL arbitrário (`db.sql(...)`, `exec_sql`, etc.)
- DDL/DML inline no código da aplicação (criar/alterar tabela em runtime)

Cobre tudo: tabelas, colunas, índices, enums, constraints, extensões, functions, triggers, views, policies de RLS, grants e seeds estruturais. **Se muda o banco, vira migration.**

### ✅ Fluxo obrigatório

```bash
supabase migration new <descricao>                 # 1. cria o arquivo
# editar supabase/migrations/<timestamp>_<desc>.sql # 2. escreve o SQL
supabase db push                                    # 3. aplica (remoto) — ou `supabase db reset` local
supabase gen types typescript --project-id <ref> \  # 4. regenera os tipos
  > src/integrations/supabase/types.ts
```

### Regras

- Nunca edite uma migration já aplicada — crie uma nova para corrigir
- A migration e o código que depende dela entram no **mesmo commit**
- `supabase/migrations/` nunca vai no `.gitignore` — é a fonte de verdade do schema
- A única exceção para SQL direto é leitura (`SELECT`) para inspeção — nunca para mutar
- Detalhes operacionais vivem em `docs/ARQUITETURA.md` (seção de banco)

---

## 🚫 Regras de Git (INEGOCIÁVEIS)

```
# .gitignore OBRIGATÓRIO — a IA deve criar/verificar no início do projeto:
.env
.env.local
.env.*.local
*.env
```

> ❌ **É PROIBIDO fazer commit do `.env` ou qualquer arquivo com credenciais.**
> Se a IA detectar que o `.env` está sendo commitado (ou não está no `.gitignore`), deve parar tudo e corrigir antes de continuar.

---

## 🚦 Trilha Obrigatória — Do Zero ao App em Produção

Para quem está começando um app do zero, esta é a ordem que **deve ser seguida**. Nenhuma etapa pode ser pulada.

```
FASE 0 — Segurança & Planejamento
  └─ Executar skill /security-auditor
  └─ Criar PRD.md (aprovação obrigatória do usuário)
  └─ Criar ROADMAP.md (aprovação obrigatória do usuário)
  └─ Criar ARQUITETURA.md
  └─ Definir estratégia de banco (Supabase direto ou local primeiro)

FASE 1 — Setup do Projeto
  └─ Criar projeto React + TypeScript (stack Lovable)
  └─ Configurar ESLint, Prettier, Husky
  └─ Criar .gitignore (com .env bloqueado)
  └─ Configurar Tailwind CSS + shadcn/ui
  └─ Configurar React Router
  └─ Configurar React Query (TanStack Query)
  └─ Configurar Zustand (se necessário)
  └─ Configurar Zod para validações

FASE 2 — Banco de Dados
  └─ (Opção A) Conectar ao Supabase via token temporário
  └─ (Opção B) Subir PostgreSQL local via Docker
  └─ Criar schema inicial com migrations versionadas (TODA alteração de banco é via migration — SQL direto proibido)
  └─ Ativar RLS em todas as tabelas
  └─ Documentar plano de migração (se Opção B)

FASE 3 — Autenticação
  └─ Implementar auth com Supabase Auth
  └─ Proteger rotas privadas
  └─ Implementar refresh de sessão
  └─ Validar RLS com usuário autenticado

FASE 4 — Features (MVP)
  └─ Implementar P0 do PRD
  └─ Testes unitários com Vitest
  └─ Testes de integração

FASE 5 — Deploy
  └─ Executar skill /security-auditor (OBRIGATÓRIO antes do deploy)
  └─ Configurar Vercel
  └─ Configurar variáveis de ambiente no painel do Vercel
  └─ Configurar domínio + Cloudflare
  └─ Ativar Vercel Analytics
  └─ Testes end-to-end com Playwright nos fluxos críticos

FASE 6 — Pós-lançamento
  └─ Monitorar erros (Sentry ou similar)
  └─ Revisar e renovar tokens do Supabase (a cada 7 dias)
  └─ Atualizar ROADMAP.md e MUDANCAS.md
```

---

## 📋 Etapa 1 — PRD.md (obrigatório antes de qualquer código)

A IA deve criar `docs/PRD.md` com as seguintes seções:

1. **Visão Geral** — O que é, para quem é, qual problema resolve
2. **Objetivos de Negócio** — Métricas de sucesso, proposta de valor
3. **Personas** — Quem vai usar, contexto, necessidades
4. **Requisitos Funcionais** — Funcionalidades com prioridade (P0/P1/P2)
5. **Requisitos Não-Funcionais** — Performance, acessibilidade, SEO, escalabilidade
6. **Fluxos Principais** — Jornadas do usuário passo a passo
7. **Regras de Negócio** — Validações, restrições, comportamentos esperados
8. **Integrações Externas** — Serviços externos que serão consumidos
9. **Critérios de Aceitação** — Como saber quando cada feature está "pronta"
10. **Fora de Escopo** — O que NÃO será feito nesta versão

> ⚠️ A IA **não pode avançar para o ROADMAP** sem PRD aprovado pelo usuário.

---

## 📋 Etapa 2 — ROADMAP.md

Com base no PRD aprovado, criar `docs/ROADMAP.md` com:

- Fases numeradas (Fase 0 — Setup, Fase 1 — MVP, etc.)
- Para cada fase: tarefas com status `[ ]` / `[→]` / `[x]`
- Critério de conclusão da fase
- Dependências entre fases
- Estimativa de esforço (Baixo / Médio / Alto)
- Histórico de atualizações com data/hora BRT

> ⚠️ A IA **não pode começar a codar** sem ROADMAP aprovado.

---

## 📋 Etapa 3 — ARQUITETURA.md

Após PRD e ROADMAP aprovados, criar `docs/ARQUITETURA.md` com:

- Diagrama textual da arquitetura (frontend, banco, serviços externos)
- Estrutura de pastas do projeto
- Decisões de arquitetura justificadas
- Fluxo de dados entre camadas
- **Estratégia de banco escolhida e, se local, plano de migração para o Supabase**

> Somente após as 3 etapas concluídas e validadas, a IA pode iniciar o desenvolvimento.

---

## 🗂️ Índice de Documentos

A IA deve ler todos os arquivos abaixo antes de executar qualquer tarefa:

| Arquivo                      | Descrição                                                | Atualizado em |
|------------------------------|----------------------------------------------------------|---------------|
| `docs/PRD.md`                | Requisitos completos do produto                          | —             |
| `docs/ARQUITETURA.md`        | Estrutura, decisões técnicas e fluxo de dados            | —             |
| `docs/ROADMAP.md`            | Tarefas pendentes, em andamento e concluídas             | —             |
| `docs/MUDANCAS.md`           | Changelog de todas as alterações relevantes              | —             |
| `docs/integracoes/vercel.md` | Configuração de deploy, domínio e segurança no Vercel    | —             |
| `docs/integracoes/README.md` | Índice de todas as integrações externas documentadas     | —             |

> **Regra:** toda vez que um arquivo acima for alterado, atualizar o campo "Atualizado em" com data/hora BRT (ex: `20/03/2025 às 14h32 BRT`).

---

## 🧱 Stack Obrigatória (React + TypeScript — padrão Lovable)

| Camada            | Tecnologia                              |
|-------------------|-----------------------------------------|
| Framework         | React 18 + TypeScript (strict mode)     |
| Build             | Vite                                    |
| Estilo            | Tailwind CSS + shadcn/ui                |
| Roteamento        | React Router v6                         |
| Estado servidor   | TanStack Query (React Query)            |
| Estado global     | Zustand (quando necessário)             |
| Validação         | Zod                                     |
| Formulários       | React Hook Form + Zod                   |
| Banco / Auth      | Supabase                                |
| Testes unitários  | Vitest                                  |
| Testes E2E        | Playwright                              |
| Deploy            | Vercel                                  |
| CDN / Segurança   | Cloudflare                              |

---

## 🧠 Como a IA deve se comunicar

- Usar linguagem didática, como se falasse com alguém sem experiência em programação
- Explicar cada conceito antes de usá-lo
- Usar analogias do mundo real para simplificar ideias técnicas
- Evitar jargão — quando inevitável, explicar o que significa logo em seguida
- Ser paciente e claro, assumindo zero conhecimento prévio
- Responder sempre em **Português do Brasil**

---

## 🔄 Fluxo de Deploy Automático

```
Você salva o código
       ↓
GitHub recebe a atualização
       ↓
Vercel detecta automaticamente
       ↓
Vercel compila e publica (~1-2 min)
       ↓
Site atualizado no ar ✅
```

- Branch `main` → Deploy em **produção** (site real)
- Outras branches → Deploy em **preview** (URL temporária para testes)

---

## 📋 Checklist de Entrega

A IA deve verificar cada item antes de considerar qualquer tarefa concluída:

**Documentação**
- [ ] PRD.md existe e foi aprovado pelo usuário?
- [ ] ROADMAP.md existe e está atualizado?
- [ ] MUDANCAS.md foi atualizado com a descrição da entrega?

**Código**
- [ ] O código compila sem erros TypeScript?
- [ ] Nenhum `any` foi usado sem justificativa documentada?
- [ ] Nenhuma chave, segredo ou dado sensível está exposto no código?
- [ ] `.env` está no `.gitignore` e **não foi commitado**?

**Banco de Dados**
- [ ] RLS está ativo em todas as tabelas afetadas?
- [ ] Nenhuma `service_role_key` está no `.env` ou no código?
- [ ] Token do Supabase é temporário e está dentro do prazo de 7 dias?
- [ ] Toda mudança de banco está em uma migration versionada em `supabase/migrations/`?
- [ ] Nenhum SQL direto (SQL Editor, `supabase db execute`, `psql`, RPC de SQL) foi usado para alterar o banco?
- [ ] Tipos TypeScript regenerados após as migrations?

**Segurança**
- [ ] Skill `/security-auditor` foi executada nesta entrega?
- [ ] Headers de segurança estão configurados no `vercel.json`?
- [ ] Rate limiting está ativo nas rotas novas?

**Deploy**
- [ ] `vercel.json` existe com todos os headers de segurança?
- [ ] Todas as variáveis de ambiente estão no painel do Vercel (não no código)?
- [ ] HTTPS ativo e funcionando (cadeado verde)?
- [ ] Vercel Analytics ativo?
- [ ] A IA explicou ao usuário como verificar o deploy no painel do Vercel?

**Testes**
- [ ] Testes unitários cobrem hooks, utilitários, schemas Zod e lógica de negócio?
- [ ] Testes de integração cobrem chamadas ao Supabase, auth e autorização?
- [ ] Testes E2E cobrem os fluxos críticos do usuário?
- [ ] Nenhum teste existente foi quebrado?

---

## 🧪 Padrão de Testes

- **Vitest** — testes unitários: hooks, utilitários, schemas Zod, lógica de negócio
- **Integração** — chamadas ao Supabase, autenticação, autorização
- **Playwright** — fluxos críticos do usuário no navegador real
- Credenciais de teste ficam no `.env` sob `TEST_USER_EMAIL` e `TEST_USER_PASSWORD`
- Nenhuma entrega pode quebrar testes existentes

---

## 🌐 Configuração Vercel + Cloudflare

**Passos para conectar domínio:**
1. Em **Settings → Domains** no Vercel, adicionar o domínio e copiar o CNAME
2. No painel DNS do Cloudflare, adicionar o CNAME do Vercel com proxy ativo (ícone laranja)
3. Em **SSL/TLS** no Cloudflare, selecionar modo **Full (Strict)**

**Configurações de segurança obrigatórias no Cloudflare:**

| Configuração          | Onde ativar                    | Por que fazer                                      |
|-----------------------|--------------------------------|----------------------------------------------------|
| WAF (Firewall)        | Security → WAF                 | Bloqueia automaticamente ataques conhecidos        |
| Bot Fight Mode        | Security → Bots                | Identifica e bloqueia bots maliciosos              |
| Rate Limiting         | Security → WAF → Rate Limiting | Limita acessos por IP por minuto                   |
| HTTPS Always          | SSL/TLS → Edge Certificates    | Redireciona HTTP para HTTPS                        |
| HSTS                  | SSL/TLS → Edge Certificates    | Força HTTPS permanentemente                        |
| Min TLS Version: 1.2  | SSL/TLS → Edge Certificates    | Bloqueia protocolos antigos e inseguros            |
| Turnstile (captcha)   | Turnstile                      | Proteção anti-bot nas páginas de login/signup      |

> 💡 **O que é o WAF?** Imagine um segurança na porta de uma festa com uma lista de "tipos suspeitos" — o WAF faz isso digitalmente, bloqueando padrões de ataque antes mesmo de chegarem ao seu site.

---

## 📋 Checklist de Deploy (Vercel)

- [ ] Conta Vercel criada e conectada ao GitHub?
- [ ] Todas as variáveis de ambiente adicionadas no painel do Vercel?
- [ ] `vercel.json` criado com todos os headers de segurança?
- [ ] HTTPS ativo (cadeado verde no navegador)?
- [ ] Preview Deployments protegidos por senha ou login?
- [ ] Domínio personalizado configurado (se aplicável)?
- [ ] Cloudflare configurado na frente do Vercel?
- [ ] WAF e Bot Fight Mode ativos no Cloudflare?
- [ ] Rate Limiting configurado no Cloudflare?
- [ ] Vercel Analytics ativo?
- [ ] **Skill `/security-auditor` executada antes do deploy?** ✅ OBRIGATÓRIO
- [ ] A IA explicou ao usuário como verificar cada item no painel?
