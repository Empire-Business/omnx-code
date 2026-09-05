# CLAUDE.md

> Este arquivo é o ponto de entrada da IA para este projeto.
> Funciona como um **índice**: cada regra abaixo tem um resumo de 1-2 frases e um link para o arquivo completo em `docs/regras/`. Nada de conteúdo longo aqui — se uma explicação precisar de mais que um parágrafo curto, ela mora em `docs/regras/<nome>.md`, não neste arquivo.
> Isso existe por um motivo prático: o `CLAUDE.md` é lido no início de toda sessão. Se ele crescer sem controle, cada sessão nova gasta mais tokens só para carregar contexto antes de fazer qualquer trabalho. Um índice enxuto com regras completas em arquivos separados resolve isso sem perder nada — a IA só abre o arquivo detalhado quando a tarefa realmente toca aquele assunto.

---

## 🗂️ Índice de Regras (`docs/regras/`)

| Regra | Resumo | Arquivo completo |
|-------|--------|-------------------|
| 🖼️ Validação de UI (Regra Zero) | Mockup-first e revisões de UX são o padrão recomendado; o dono pode dispensar explicitamente mockup, UX-Guardião e/ou Dona Maria para um escopo, com registro e sem novo bloqueio | `docs/regras/mockup-first.md` |
| 🔐 Segurança | `/security-auditor` obrigatória em todo início de projeto, deploy, merge em `main`, integração nova e troca de secrets — só libera com `gate: PASS` | `docs/regras/seguranca.md` |
| 🗄️ Banco de dados | Supabase direto ou local-primeiro-depois-migra — escolha documentada em `docs/ARQUITETURA.md` | `docs/regras/banco-de-dados.md` |
| 🏢 Multi-tenant | Todo sistema nasce multi-tenant (tenant + membership + papéis), `tenant_id` em toda tabela de negócio, RLS por tenant | `docs/regras/multi-tenant.md` |
| 🧩 Apps & Loja de Apps | Todo sistema nasce modular: catálogo de apps + instalação por tenant, com tela de Loja de Apps para ativar/desativar | `docs/regras/apps-loja-de-apps.md` |
| 🔌 API & Webhooks por app | Cada app com integração tem `docs/apps/<app-slug>/API.md` + `WEBHOOKS.md` e tela própria de "Integrações" (chaves, webhooks, histórico) — desativar o app derruba o acesso na hora | `docs/regras/api-webhooks-por-app.md` |
| 📐 UML | Nenhum código de domínio sem `docs/UML.md` (+`UML.html`) aprovado antes — bloqueia código e commit | `docs/regras/uml.md` |
| 🛂 Níveis de acesso | Permissões em catálogo global + **perfis que cada tenant monta** (nunca papéis fixos nas policies); `has_permission()` como única checagem; 5 travas anti-lockout; `docs/NIVEIS-DE-ACESSO.md` completo — bloqueia commit de auth e deploy | `docs/regras/niveis-de-acesso.md` |
| 🎫 Sistema de tickets de erro | Botão de reportar + captura automática (print, log, rota) + fila por status — bloqueia deploy | `docs/regras/sistema-de-tickets.md` |
| 🧭 UX: referência & Guardião | Referência real e revisão adversarial recomendadas; o dono pode dispensar qualquer uma para o escopo atual | `docs/regras/ux-referencia-e-guardiao.md` |
| [avaliador-leigo.md](docs/regras/avaliador-leigo.md) | **Dona Maria**, revisão leiga recomendada depois do UX-Guardião; dispensável integralmente pelo dono para um lote ou mudança, com registro. |
| 🔑 Acesso ao Supabase | Nunca `service_role_key` no client; tokens temporários (7 dias) via `supabase login` | `docs/regras/acesso-supabase.md` |
| 🗃️ Migrations | Toda mudança de banco via migration versionada — SQL direto proibido | `docs/regras/migrations.md` |
| 🚫 Git | `.env` e credenciais sempre no `.gitignore`, nunca commitados | `docs/regras/git.md` |
| 🚦 Trilha obrigatória | Ordem das fases do zero à produção (FASE 0 = telas aprovadas, até FASE 6) | `docs/regras/trilha-obrigatoria.md` |
| 📋 Mockups, UX-MAP, PRD, ROADMAP e ARQUITETURA | Etapas 0-3 no fluxo visual padrão e caminho equivalente quando o dono escolhe modo direto | `docs/regras/prd-roadmap-arquitetura.md` |
| 🧱 Stack obrigatória | React + TypeScript + Supabase + Vercel — a stack padrão Lovable | `docs/regras/stack.md` |
| 🧠 Comunicação | Como a IA deve falar com o usuário (didático, português, sem jargão) | `docs/regras/comunicacao.md` |
| 🔄 Deploy | Fluxo automático GitHub → Vercel, config Cloudflare, checklist de deploy | `docs/regras/deploy.md` |
| 🔄 Handoffs | Como o projeto mantém estado entre sessões em `docs/handoffs/` | `docs/regras/handoffs.md` |
| 📋 Checklist de entrega | Checklist completo antes de considerar qualquer tarefa concluída | `docs/regras/checklist-de-entrega.md` |
| 🧪 Testes | Vitest, integração e Playwright — o que cada camada cobre | `docs/regras/testes.md` |

> **Regra de manutenção deste índice:** toda vez que a skill `omnx-code` adicionar uma regra nova ou expandir uma existente além de um resumo curto, o conteúdo completo vai para um arquivo novo ou existente em `docs/regras/`, e aqui entra só a linha da tabela. Ver regra 7 (`SKILL.md` da `omnx-code`) para o gate que garante isso continuamente, não só na instalação inicial.

---

## 🗂️ Índice de Documentos

A IA deve saber que os arquivos abaixo existem e consultá-los quando a tarefa tocar o assunto — não precisa reler todos a cada sessão, só os relevantes para o pedido atual.

| Arquivo                      | Descrição                                                | Atualizado em |
|------------------------------|----------------------------------------------------------|---------------|
| `docs/regras/`               | Todas as regras inegociáveis do projeto, uma por arquivo (ver índice acima) | — |
| `docs/mockups/`              | **Árvore única de telas.** Raiz = oficiais aprovadas; `em-aprovacao/<lote>/` = candidatas; `historico/<versao>/` = substituídas. Nunca criar `mockups-v2` ou árvore paralela. `APROVACAO.md` é a fonte da verdade do gate | — |
| `docs/PRD.md`                | Requisitos completos do produto, descrevendo as telas aprovadas | —             |
| `docs/ARQUITETURA.md`        | Estrutura, decisões técnicas, fluxo de dados, e seções de Multi-Tenant e Apps | —             |
| `docs/UML.md` + `docs/UML.html` | Diagramas de classes/entidades e sequência (Mermaid + versão visual) — **bloqueia código novo/commit se ausente/desatualizado** | — |
| `docs/NIVEIS-DE-ACESSO.md`   | Matriz de papéis × permissões — **bloqueia commit e deploy se ausente/incompleta** | — |
| `docs/SISTEMA-DE-TICKETS.md` | Como o usuário reporta erro, o que é capturado automaticamente e a fila de correção — **bloqueia deploy se ausente/incompleto** | — |
| `docs/UX-MAP.md` | Mapa da experiência transcrito das telas aprovadas: referências, rotas, grafo de navegação, ações por tela, fluxos com cliques — **bloqueia aprovação de PRD/UML se ausente** | — |
| `docs/UX-REVIEW.md` | Reclamações e veredictos do UX-Guardião quando essa revisão é executada; dispensas explícitas ficam registradas | — |
| `docs/DESIGN.md`             | Design system (cores, tipografia, componentes, espaçamento) — nasce da **promoção** do baseline visual aprovado nas telas, não como pré-requisito delas | — |
| `docs/handoffs/latest.md`    | Estado atual do projeto para retomada entre sessões      | —             |
| `docs/handoffs/HISTORY.md`   | Histórico cronológico das sessões anteriores             | —             |
| `docs/ROADMAP.md`            | Tarefas pendentes, em andamento e concluídas             | —             |
| `docs/MUDANCAS.md`           | Changelog de todas as alterações relevantes              | —             |
| `docs/integracoes/vercel.md` | Configuração de deploy, domínio e segurança no Vercel    | —             |
| `docs/integracoes/README.md` | Índice de todas as integrações externas documentadas, agrupado por app | — |
| `docs/apps/<app-slug>/API.md` | Documentação da API própria do app (auth, endpoints, exemplos `curl`) — um arquivo por app com API | — |
| `docs/apps/<app-slug>/WEBHOOKS.md` | Webhooks recebidos e disparados pelo app (payloads, assinatura, retry) — um arquivo por app com webhook | — |

> **Regra:** toda vez que um arquivo acima for alterado, atualizar o campo "Atualizado em" com data/hora BRT (ex: `20/03/2025 às 14h32 BRT`).

---

> Sincronizado com `AGENTS.md` — ambos apontam para os mesmos arquivos em `docs/regras/`. Se editar uma regra, atualize o arquivo em `docs/regras/`, não este índice.
