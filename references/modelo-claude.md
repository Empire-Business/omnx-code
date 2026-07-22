# CLAUDE.md

> Este arquivo é o ponto de entrada da IA para este projeto.
> Funciona como um índice: não contém detalhes longos — aponta para os documentos certos.
> Toda instrução técnica detalhada vive em `docs/`. Este arquivo deve permanecer enxuto.

---

## 🔐 Segurança — Skill Obrigatória

**A IA DEVE executar a skill `/security-auditor` nos seguintes momentos, sem exceção, e só liberar com `security-report/verdict.json` em `"gate": "PASS"`:**

| Momento                                          | Obrigatório? |
|--------------------------------------------------|--------------|
| Início do projeto (antes de codar)               | ✅ Sim        |
| Antes de qualquer deploy em produção             | ✅ Sim        |
| Antes de merge em `main` ou PR de release        | ✅ Sim        |
| Após adicionar qualquer integração               | ✅ Sim        |
| Após rotacionar/trocar secrets ou env vars       | ✅ Sim        |
| Após migrations/RLS ou troca de projeto Supabase | ✅ Sim        |
| Quando solicitado pelo usuário                   | ✅ Sim        |

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

## 🏢 Arquitetura de Usuários & Multi-Tenant (INEGOCIÁVEL)

**Todo sistema deste projeto é multi-tenant por padrão**, mesmo que hoje só exista um cliente/empresa usando. Migrar um schema single-tenant para multi-tenant depois que já existem dados em produção é caro e arriscado — nascer multi-tenant custa quase nada e evita essa dor depois.

> ⚠️ **Exceção:** só pule o modelo multi-tenant se o usuário confirmar explicitamente que o projeto é de uso único (ex: ferramenta interna pessoal, protótipo descartável) — e mesmo assim, documente a decisão em `docs/ARQUITETURA.md`.

### Modelo obrigatório

| Peça | O que é | Exemplo de nome |
|------|---------|------------------|
| **Tenant** | A entidade que isola os dados (empresa, conta, time) | `tenants` / `organizations` |
| **Membership** | Liga `auth.users` ao tenant — um usuário pode pertencer a vários tenants | `tenant_members` |
| **Papéis (roles)** | Nível de permissão do usuário dentro do tenant | `owner`, `admin`, `member` |
| **Isolamento** | Toda tabela de negócio carrega `tenant_id` (FK not-null) | `orders.tenant_id`, `projects.tenant_id` |

### Regras

- A tabela de tenants e a de membership entram na **primeira migration** do projeto — antes de qualquer tabela de negócio.
- Toda tabela de negócio nova (não-catálogo, não-config global) nasce com `tenant_id` desde o dia 1. Nunca "adiciona depois".
- Toda política RLS de tabela com `tenant_id` filtra por tenant **e** por papel quando a operação exigir (ex: `DELETE` só para `owner`/`admin`). Uma política que só checa `auth.uid()` sem checar o tenant vaza dados entre contas diferentes quando o mesmo usuário pertence a mais de um tenant.
- Se o produto permite trocar de tenant ativo (usuário em múltiplos tenants), o tenant ativo nunca é inferido de um dado enviado pelo cliente sem validar contra a tabela de membership.
- A matriz de permissões por papel (quem pode ver/criar/editar/deletar o quê) fica documentada em `docs/ARQUITETURA.md`, seção "Arquitetura de Usuários & Multi-Tenant" — **e**, em detalhe completo, em `docs/NIVEIS-DE-ACESSO.md` (ver seção abaixo).

---

## 📐 UML — Modelagem Obrigatória (BLOQUEIA CÓDIGO E COMMIT)

**Nenhuma linha de código de domínio é escrita antes de existir um UML mínimo em `docs/UML.md`.** Código sem modelo prévio é como construir sem planta: funciona até duas partes do sistema terem sido pensadas de formas incompatíveis, e aí já existe código dos dois lados para desfazer.

Formato: **Mermaid** dentro do markdown (`classDiagram`, `sequenceDiagram`, `stateDiagram-v2`) — versionável no git, renderiza direto no GitHub, sem depender de ferramenta externa.

**Versão visual:** sempre que `docs/UML.md` for criado ou atualizado, a IA também gera `docs/UML.html` — uma página HTML autocontida com todos os diagramas renderizados visualmente em abas navegáveis (tema dark, interativo). Ambos entram no mesmo commit. O HTML abre em qualquer navegador, sem servidor.

### O que `docs/UML.md` precisa ter

1. **Diagrama de classes/entidades** — entidades principais do domínio, atributos essenciais, relacionamentos. Inclui a arquitetura de usuários/multi-tenant (tenant, membership, papéis — ver seção acima)
2. **Diagrama(s) de sequência** dos 2-3 fluxos mais críticos (ex: cadastro/login, a ação principal do produto, checkout/pagamento se houver)
3. **Diagrama de estados** (opcional, recomendado quando há entidade com ciclo de vida relevante — pedido, assinatura, workflow de aprovação)

### Regra para projeto novo

O UML é criado na FASE 0 do projeto, junto com `ARQUITETURA.md`, e **aprovado pelo usuário antes do primeiro código de domínio** (models, entidades, schema de banco).

### Regra para projeto existente sem UML (retroativo)

Se este projeto já tem código mas ainda não tem `docs/UML.md`, **nenhum commit novo pode ser feito até o UML existir**, mesmo que a mudança pedida seja pequena — falta de UML é dívida técnica bloqueante, igual dívida de segurança. Nesse caso:
1. O UML é gerado por engenharia reversa a partir do schema e código **reais** — nunca inventado
2. O usuário valida o diagrama gerado (código legado pode ter entidades que já não fazem sentido)
3. Só depois disso o commit pedido acontece

### Manutenção

Toda vez que uma entidade, relacionamento ou fluxo crítico muda, `docs/UML.md` e `docs/UML.html` sao atualizados no **mesmo commit** que muda o codigo — nunca depois. Toda migration nova (tabela, coluna, função/RPC, trigger, policy) é gatilho obrigatório de atualização do UML. Antes de concluir qualquer tarefa com migration, compare o timestamp da migration mais recente com o campo `Atualizado em` do UML: se estiver atrás, a tarefa não está concluída. Uma mudanca de schema/dominio commitada sem os arquivos UML correspondentes e tratada como bug, nao como pendencia.

---

## 🛂 Níveis de Acesso — Documentação Obrigatória (BLOQUEIA COMMIT E DEPLOY)

**Nenhum código de autenticação/autorização pode ser commitado, e nenhum deploy pode acontecer, sem `docs/NIVEIS-DE-ACESSO.md` existir e estar completo.** Isso vale mesmo em projetos de um único tenant — se há qualquer distinção de permissão entre usuários (ex: admin vs usuário comum), o documento é obrigatório. Não é uma boa prática opcional: é um gate, igual ao gate de segurança.

### O que o documento precisa ter

1. **Lista de todos os papéis (roles)** do sistema, com uma frase descrevendo quem é esse usuário e por que esse papel existe
2. **Matriz papel × recurso × ação** — para cada papel, o que ele pode `ver`, `criar`, `editar`, `deletar` em cada recurso/tabela/tela do sistema. Nenhuma célula pode ficar em branco ou marcada como "a definir" — se ainda não foi decidido, a decisão precisa ser tomada com o usuário antes de codar a permissão
3. **Telas/rotas por papel** — quais telas cada papel enxerga no menu e quais rotas são bloqueadas para ele
4. **Casos especiais** — comportamento quando um usuário perde acesso a um tenant, quando um recurso é compartilhado entre papéis, herança de permissão (se houver hierarquia entre papéis)

### Regra de atualização

Sempre que um papel novo é criado ou uma permissão muda, `docs/NIVEIS-DE-ACESSO.md` é atualizado **no mesmo commit** que muda o código — nunca depois, nunca "eu documento no final". Um papel ou permissão que existe no código/schema sem entrada correspondente no documento é tratado como bug, não como pendência.

---

## 🎫 Sistema de Tickets de Erro — Obrigatório (BLOQUEIA DEPLOY)

**Todo sistema com interface visível ao usuário final precisa ter um sistema de tickets de erro antes de ir para produção.** Não é opcional e não é "adicionar depois se der tempo": é o mesmo tipo de gate que segurança e níveis de acesso. Não se aplica a scripts internos ou jobs sem UI.

A ideia por trás disso é simples: um erro que o usuário não consegue reportar facilmente é um erro que nunca chega até quem pode corrigir. E um erro reportado sem contexto técnico (print, log, rota, navegador) vira uma investigação de "me manda mais detalhes" que atrasa a correção em dias. O objetivo é fechar essa distância: **do clique do usuário até a fila de correção, sem fricção e sem depender de descrição manual.**

### O que precisa existir

1. **Botão/atalho de "Reportar problema" visível em qualquer tela** — não escondido em um menu de configurações. Padrão recomendado: botão flutuante discreto (canto inferior) ou item fixo no menu principal, disponível em toda a aplicação autenticada.
2. **Captura automática ao acionar o report** (o usuário só descreve o que estava tentando fazer, opcionalmente — nunca precisa colar log ou tirar print manualmente):
   - Print de tela da tela atual no momento do report
   - Logs do console / stack trace do erro (se houver um erro JS associado)
   - Rota/URL atual e a ação que estava sendo executada
   - Timestamp, navegador, sistema operacional, resolução de tela
   - Id do usuário e do tenant (quando aplicável), sem expor dados sensíveis de outros usuários
3. **Captura automática também em erro não tratado** — um error boundary do React (para erros de render) e um handler global (`window.onerror` + `unhandledrejection`, para erros fora do ciclo de render) disparam a mesma captura sem exigir que o usuário clique em nada. O usuário vê uma tela amigável de erro ("algo deu errado, já avisamos o time") e o ticket é criado em segundo plano.
4. **Fila interna organizada por status** — os tickets caem numa área que o time de correção acompanha, com status mínimo: `novo → em análise → em correção → resolvido`. Pode ser uma tabela própria no Supabase com um painel simples (`/admin/tickets` ou equivalente, protegido por papel — ver seção de Níveis de Acesso) ou uma integração que envia o ticket para o sistema de suporte que o time já usa (ex: webhook para Linear/Slack/email). O importante é que nenhum ticket fica perdido em log que ninguém olha.

### Estrutura mínima de dados (se usar tabela própria no Supabase)

```sql
-- exemplo de shape mínimo — adapte nomes ao padrão do projeto
create table public.error_tickets (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references public.tenants(id),
  user_id uuid references auth.users(id),
  status text not null default 'novo' check (status in ('novo','em_analise','em_correcao','resolvido')),
  description text,           -- o que o usuário disse que estava fazendo (opcional)
  error_message text,         -- mensagem/stack trace, se houver
  route text,                 -- rota onde ocorreu
  screenshot_url text,        -- print enviado ao Storage
  browser_info jsonb,         -- navegador, SO, resolução
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);
```

Como toda tabela nova, entra em migration versionada (regra de Migrations acima) e tem RLS ativo: o usuário só cria tickets (não lê tickets de outros); a leitura/atualização de status fica restrita ao papel responsável pela correção, seguindo a matriz em `docs/NIVEIS-DE-ACESSO.md`.

### Regra de atualização

`docs/SISTEMA-DE-TICKETS.md` documenta: como o usuário reporta, o que é capturado automaticamente, onde a fila vive (tabela + painel, ou integração externa), os status do fluxo e quem é notificado em cada mudança. Esse documento é criado **antes do primeiro deploy** e atualizado sempre que o fluxo de captura ou a fila mudar — mesmo princípio já aplicado a UML (migrations) e Níveis de Acesso: o que descreve o comportamento não pode ficar defasado em relação ao código.

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
  └─ Criar ARQUITETURA.md (inclui Arquitetura de Usuários & Multi-Tenant)
  └─ Criar UML.md (classes/entidades + sequência dos fluxos críticos) — aprovação obrigatória antes de codar domínio
  └─ Criar design system em docs/DESIGN.md ou docs/design-system/ (gate para mockups)
  └─ Criar mockups navegáveis em docs/mockups/ (quando solicitado; só após PRD, UML e design system aprovados)
  └─ Definir estratégia de banco (Supabase direto ou local primeiro)
  └─ Definir modelo de tenant, membership e papéis (multi-tenant por padrão)

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
  └─ Criar tabelas de tenants, membership e papéis ANTES de qualquer tabela de negócio
  └─ Criar schema inicial com migrations versionadas (TODA alteração de banco é via migration — SQL direto proibido)
  └─ Toda tabela de negócio nasce com `tenant_id` (FK not-null)
  └─ Ativar RLS em todas as tabelas, filtrando por tenant onde aplicável
  └─ Documentar plano de migração (se Opção B)

FASE 3 — Autenticação e Autorização
  └─ Criar/atualizar docs/NIVEIS-DE-ACESSO.md com a matriz completa de papéis (GATE — bloqueia o commit abaixo se faltar)
  └─ Implementar auth com Supabase Auth
  └─ Implementar seleção/troca de tenant ativo (se usuário pode pertencer a múltiplos tenants)
  └─ Proteger rotas privadas por papel, conforme docs/NIVEIS-DE-ACESSO.md
  └─ Implementar refresh de sessão
  └─ Validar RLS com usuário autenticado em diferentes tenants e papéis

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
- **Arquitetura de Usuários & Multi-Tenant** — modelo de tenant, membership e papéis (ver seção dedicada acima)

> Somente após as 3 etapas concluídas e validadas, a IA pode iniciar o desenvolvimento. A etapa de codar autenticação/autorização tem um requisito adicional: `docs/NIVEIS-DE-ACESSO.md` (ver seção "Níveis de Acesso" acima) precisa existir e estar completo **antes** do primeiro commit desse código — é um gate, não uma etapa opcional.

---

## 📋 Etapa 3b — Mockups navegáveis (quando solicitado)

Se o usuário pedir mockups, protótipos ou "ver as telas" antes de codar, siga o fluxo de mockups da skill `omnx-code`:

### Pré-requisitos (gate fail-closed)

Nenhum mockup é gerado sem:
- `docs/PRD.md` aprovado
- `docs/ARQUITETURA.md` aprovado
- `docs/UML.md` + `docs/UML.html` criados
- Design system completo em `docs/DESIGN.md` ou `docs/design-system/`

Se algum item estiver faltando, crie-o primeiro com o usuário. Não "dê um jeitinho" e gere mockup pela metade.

### Entregáveis

- `docs/mockups/README.md` — inventário de telas com rastreabilidade ao PRD
- `docs/mockups/index.html` — hub navegável com lista de todas as telas
- `docs/mockups/tel-XXX-nome.html` — um arquivo HTML por tela
- `docs/mockups/VALIDACAO.md` — cobertura do PRD e fidelidade ao design system

### Regras dos mockups

- Use apenas HTML/CSS puro; abre direto no navegador sem servidor
- Um arquivo por tela — nunca várias telas no mesmo arquivo
- Cores, fontes, espaçamentos e componentes vêm 100% do design system
- Represente os estados relevantes de cada tela (vazio, erro, carregando, sucesso)
- Links entre telas funcionam; botões sem destino mostram `alert` explicando a ação
- Toda funcionalidade P0/P1 do PRD deve aparecer em pelo menos uma tela

> Detalhes completos do fluxo estão na seção "Fluxo de Mockups" do `SKILL.md` da `omnx-code`.

---

## 🗂️ Índice de Documentos

A IA deve ler todos os arquivos abaixo antes de executar qualquer tarefa:

| Arquivo                      | Descrição                                                | Atualizado em |
|------------------------------|----------------------------------------------------------|---------------|
| `docs/PRD.md`                | Requisitos completos do produto                          | —             |
| `docs/ARQUITETURA.md`        | Estrutura, decisões técnicas e fluxo de dados            | —             |
| `docs/UML.md`                | Diagramas de classes/entidades e sequencia (Mermaid) — **bloqueia codigo novo/commit se ausente/desatualizado** | — |
| `docs/UML.html`              | Versao visual interativa dos diagramas UML (abrir no navegador) — **gerado junto com UML.md no mesmo commit** | — |
| `docs/NIVEIS-DE-ACESSO.md`   | Matriz de papéis × permissões — **bloqueia commit e deploy se ausente/incompleta** | — |
| `docs/SISTEMA-DE-TICKETS.md` | Como o usuário reporta erro, o que é capturado automaticamente e a fila de correção — **bloqueia deploy se ausente/incompleto** | — |
| `docs/DESIGN.md`             | Design system (cores, tipografia, componentes, espaçamento) — **gate para mockups** | — |
| `docs/mockups/`              | Mockups navegáveis (um arquivo HTML por tela), gerados a partir do PRD e design system | — |
| `docs/handoffs/latest.md`    | Estado atual do projeto para retomada entre sessões      | —             |
| `docs/handoffs/HISTORY.md`   | Histórico cronológico das sessões anteriores             | —             |
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

## 🔄 Handoffs entre Sessões

Para economizar tokens e permitir que o usuário dê CLEAR no contexto, o projeto mantém handoffs em `docs/handoffs/`:

- `docs/handoffs/latest.md` — estado atual do projeto; lido na retomada de qualquer sessão
- `docs/handoffs/HISTORY.md` — histórico cronológico das sessões
- `docs/handoffs/README.md` — como usar os handoffs

A IA deve atualizar `latest.md` ao final de toda sessão significativa e lê-lo primeiro quando o usuário pedir para continuar, retomar ou limpar contexto.

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

**Modelagem (UML)**
- [ ] **`docs/UML.md` existe, com diagrama de classes/entidades e sequência dos fluxos críticos, ANTES de qualquer código de domínio ter sido escrito?** Em projeto existente sem UML, ele foi gerado por engenharia reversa e validado pelo usuário antes deste commit? Sem isso, o commit está BLOQUEADO (gate 1.6c).
- [ ] **`docs/UML.html` foi gerado junto com `docs/UML.md` no mesmo commit?** O HTML renderiza todos os diagramas visualmente com abas navegáveis e abre em qualquer navegador sem servidor.
- [ ] Toda entidade/relacionamento/fluxo crítico alterado nesta entrega está refletido no `docs/UML.md` e `docs/UML.html`, no mesmo commit?

**Arquitetura de Usuários & Multi-Tenant**
- [ ] **`docs/NIVEIS-DE-ACESSO.md` existe e cobre todos os papéis do sistema, sem células em branco na matriz?** Sem esse documento completo, o commit de código de auth/permissão e o deploy estão BLOQUEADOS (gate 1.6b — anti-teatro: um papel no código sem entrada no documento é bug).
- [ ] Toda tabela de negócio nova tem coluna `tenant_id` (FK not-null), exceto se o projeto foi explicitamente definido como single-tenant e isso está documentado em `docs/ARQUITETURA.md`?
- [ ] Toda política RLS de tabela com `tenant_id` filtra por tenant (não só por `auth.uid()`)?

**Sistema de Tickets de Erro**
- [ ] **Existe um botão/atalho de "Reportar problema" visível em qualquer tela da aplicação?** Sem isso, o deploy está BLOQUEADO (gate 1.6d).
- [ ] **A captura automática (print de tela, log/stack trace, rota, timestamp, navegador, usuário/tenant) funciona tanto pelo botão de reportar quanto por um error boundary/handler global de erro não tratado?**
- [ ] Os tickets caem numa fila interna organizada por status (`novo → em análise → em correção → resolvido`), seja tabela própria com painel ou integração com o sistema de suporte do time?
- [ ] **`docs/SISTEMA-DE-TICKETS.md` existe e documenta o fluxo completo (como reportar, o que é capturado, onde a fila vive, status, quem é notificado)?** Sem esse documento, o deploy está BLOQUEADO (gate 1.6d).

**Banco de Dados**
- [ ] RLS está ativo em todas as tabelas afetadas?
- [ ] Nenhuma `service_role_key` está no `.env` ou no código?
- [ ] Token do Supabase é temporário e está dentro do prazo de 7 dias?
- [ ] Toda mudança de banco está em uma migration versionada em `supabase/migrations/`?
- [ ] Nenhum SQL direto (SQL Editor, `supabase db execute`, `psql`, RPC de SQL) foi usado para alterar o banco?
- [ ] Tipos TypeScript regenerados após as migrations?

**Segurança**
- [ ] Skill `/security-auditor` foi executada nesta entrega?
- [ ] **`security-report/verdict.json` desta sessão existe com `"gate": "PASS"`?** Sem o artefato, ou com `gate != PASS`, o deploy está BLOQUEADO — P0/P1 em aberto (inclui `❔ não verificado`/`⚠️ ação manual`) derrubam o gate. Marcar este item sem o `verdict.json` é inválido (anti-teatro). A auditoria é report-only; auto-fix é opt-in.
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
- [ ] **Sistema de tickets de erro ativo em produção (botão de reportar + captura automática + fila) e `docs/SISTEMA-DE-TICKETS.md` atualizado?** ✅ OBRIGATÓRIO
- [ ] **Skill `/security-auditor` executada antes do deploy?** ✅ OBRIGATÓRIO
- [ ] A IA explicou ao usuário como verificar cada item no painel?
