# 📋 Etapas 1-3b — PRD, ROADMAP, ARQUITETURA e Mockups

## Etapa 1 — PRD.md (obrigatório antes de qualquer código)

A IA deve criar `docs/PRD.md` com as seguintes seções:

1. **Visão Geral** — O que é, para quem é, qual problema resolve
2. **Objetivos de Negócio** — Métricas de sucesso, proposta de valor
3. **Personas** — Quem vai usar, contexto, necessidades
4. **Requisitos Funcionais** — Funcionalidades com prioridade (P0/P1/P2)
5. **Apps do produto** — cada requisito funcional agrupado no app a que pertence (ver `docs/regras/apps-loja-de-apps.md`); todo requisito tem um app dono, nenhum fica solto
6. **Requisitos Não-Funcionais** — Performance, acessibilidade, SEO, escalabilidade
7. **Fluxos Principais** — Jornadas do usuário passo a passo
8. **Regras de Negócio** — Validações, restrições, comportamentos esperados
9. **Integrações Externas** — Serviços externos que serão consumidos
10. **Critérios de Aceitação** — Como saber quando cada feature está "pronta"
11. **Fora de Escopo** — O que NÃO será feito nesta versão

> ⚠️ A IA **não pode avançar para o ROADMAP** sem PRD aprovado pelo usuário.

## Etapa 2 — ROADMAP.md

Com base no PRD aprovado, criar `docs/ROADMAP.md` com:

- Fases numeradas (Fase 0 — Setup, Fase 1 — MVP, etc.)
- Para cada fase: tarefas com status `[ ]` / `[→]` / `[x]`
- Critério de conclusão da fase
- Dependências entre fases
- Estimativa de esforço (Baixo / Médio / Alto)
- Histórico de atualizações com data/hora BRT

> ⚠️ A IA **não pode começar a codar** sem ROADMAP aprovado.

## Etapa 3 — ARQUITETURA.md

Após PRD e ROADMAP aprovados, criar `docs/ARQUITETURA.md` com:

- Diagrama textual da arquitetura (frontend, banco, serviços externos)
- Estrutura de pastas do projeto
- Decisões de arquitetura justificadas
- Fluxo de dados entre camadas
- **Estratégia de banco escolhida e, se local, plano de migração para o Supabase**
- **Arquitetura de Usuários & Multi-Tenant** — modelo de tenant, membership e papéis (ver `docs/regras/multi-tenant.md`)
- **Arquitetura de Apps & Loja de Apps** — catálogo de apps, modelo de instalação por tenant e dependências entre apps (ver `docs/regras/apps-loja-de-apps.md`)

> Somente após as 3 etapas concluídas e validadas, a IA pode iniciar o desenvolvimento. A etapa de codar autenticação/autorização tem um requisito adicional: `docs/NIVEIS-DE-ACESSO.md` (ver `docs/regras/niveis-de-acesso.md`) precisa existir e estar completo **antes** do primeiro commit desse código — é um gate, não uma etapa opcional.

## Etapa 3b — Mockups navegáveis (quando solicitado)

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
- **Tela de Loja de Apps é obrigatória** — lista o catálogo de apps definido em `docs/ARQUITETURA.md`, com estado ativo/inativo por app e controle de ativação para o tenant (ver `docs/regras/apps-loja-de-apps.md`). Só pode ser omitida em projeto explicitamente definido como app único.

> Detalhes completos do fluxo estão na seção "Fluxo de Mockups" do `SKILL.md` da `omnx-code`.
