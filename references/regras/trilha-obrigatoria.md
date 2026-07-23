# 🚦 Trilha Obrigatória — Do Zero ao App em Produção

Para quem está começando um app do zero, esta é a ordem que **deve ser seguida**. Nenhuma etapa pode ser pulada.

```
FASE 0 — Segurança & Planejamento
  └─ Executar skill /security-auditor
  └─ Criar PRD.md (aprovação obrigatória do usuário)
  └─ Criar ROADMAP.md (aprovação obrigatória do usuário)
  └─ Criar ARQUITETURA.md (inclui Arquitetura de Usuários & Multi-Tenant e Arquitetura de Apps & Loja de Apps)
  └─ Criar UML.md (classes/entidades + sequência dos fluxos críticos) — aprovação obrigatória antes de codar domínio
  └─ Criar design system em docs/DESIGN.md ou docs/design-system/ (gate para mockups)
  └─ Criar mockups navegáveis em docs/mockups/ (quando solicitado; só após PRD, UML e design system aprovados — inclui obrigatoriamente a tela de Loja de Apps)
  └─ Definir estratégia de banco (Supabase direto ou local primeiro)
  └─ Definir modelo de tenant, membership e papéis (multi-tenant por padrão)
  └─ Definir catálogo de apps e modelo de instalação por tenant (modular por padrão)

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
  └─ Criar tabelas de tenants, membership, papéis, catálogo de apps e instalação por tenant ANTES de qualquer tabela de negócio
  └─ Criar schema inicial com migrations versionadas (TODA alteração de banco é via migration — SQL direto proibido)
  └─ Toda tabela de negócio nasce com `tenant_id` (FK not-null) e pertence a um app do catálogo
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
