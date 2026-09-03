# 📋 Etapas 0-3 — Mockups, UX-MAP, PRD, ROADMAP e ARQUITETURA

> **A ordem aqui é telas → documentos.** Nenhum destes documentos é escrito antes de o usuário VISUALIZAR e aprovar os mockups das telas (Etapa 0). O porquê está em `docs/regras/mockup-first.md` (gate 1.6f, fail-closed): documento aprovado por leitura é aposta; documento escrito a partir de tela aprovada é transcrição.

## Etapa 0 — Mockups das telas (o PRIMEIRO passo, obrigatório antes de tudo)

Nenhum sistema novo começa pelo PRD nem pelo UX-MAP: começa pela tela que a pessoa consegue ver.

1. A IA colhe um **brief mínimo** (6 perguntas curtas, mandadas de uma vez) e o usuário escolhe pelo menos um **sistema de referência real** (se não souber, a IA propõe 3-5 candidatos — a IA nunca escolhe sozinha)
2. A IA propõe o **baseline visual provisório** embutido nas telas — o design system escrito **não** é pré-requisito, é consequência
3. A IA gera os mockups navegáveis em `docs/mockups/` (um HTML autocontido por tela, com a tela de Loja de Apps obrigatória)
4. O **UX-Guardião** revisa as telas e as reclamações são corrigidas **antes** de o usuário ver (gate 1.6e)
5. A IA **abre as telas no navegador** e o usuário aprova ou pede alteração, tela por tela — o loop repete até todas estarem aprovadas
6. A aprovação é registrada em `docs/mockups/APROVACAO.md` e o baseline aprovado é promovido para `docs/DESIGN.md`

> ⚠️ Sem `docs/mockups/APROVACAO.md` com aprovação explícita do usuário, **nada abaixo é escrito**. Detalhes completos: `docs/regras/mockup-first.md` e a seção "Fluxo de Mockups" do `SKILL.md` da `omnx-code`.

## Etapa 0b — UX-MAP.md (transcrição das telas aprovadas)

Com as telas aprovadas, a IA cria `docs/UX-MAP.md`: mapa de rotas, grafo de navegação, inventário de ações por tela (nenhum botão sem destino), fluxos críticos com contagem de cliques e os compromissos "fácil de usar SEMPRE".

Escrito nesta ordem ele deixa de ser previsão e passa a ser transcrição verificável: rota no mapa sem HTML correspondente é bug do mapa; link em HTML sem rota no mapa é buraco no mapa.

> ⚠️ Sem `docs/UX-MAP.md`, o PRD não é escrito. Especificação completa: `docs/regras/ux-referencia-e-guardiao.md` (gate 1.6e).

## Etapa 1 — PRD.md (depois das telas aprovadas, antes de qualquer código)

A IA deve criar `docs/PRD.md` **descrevendo o que está nas telas aprovadas** — cada requisito funcional aponta para a(s) tela(s) `TEL-XXX` que o mostram. Requisito sem tela e tela sem requisito são gaps a resolver, não detalhes. Seções:

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

> ⚠️ A IA **não pode avançar para o ROADMAP** sem PRD aprovado pelo usuário — e a aprovação do PRD **só é válida depois da revisão do UX-Guardião** (veredicto ✅ ou ⚠️ registrado em `docs/UX-REVIEW.md`, conforme `docs/regras/ux-referencia-e-guardiao.md`). Veredicto ❌ bloqueia: corrige e roda o Guardião de novo. O mesmo vale para o UML (regra 1.6c). E nada disso é escrito antes das telas aprovadas (gate 1.6f).

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

## Etapa 3b — Manutenção dos mockups

Os mockups não morrem depois da fundação: eles são a referência visual do produto. Toda tela nova, e toda mudança visível em tela já aprovada, volta a passar pela Etapa 0 em versão leve — desenha, mostra, aprova, e só então atualiza PRD/UML/código no mesmo commit (gate 1.6f).

### Entregáveis da pasta

- `docs/mockups/README.md` — sistema(s) de referência, baseline visual, inventário de telas e suposições assumidas
- `docs/mockups/index.html` — hub navegável com todas as telas
- `docs/mockups/tel-XXX-nome.html` — um arquivo HTML por tela
- `docs/mockups/APROVACAO.md` — status por tela, rodadas, falas do usuário, dispensas (fonte da verdade do gate 1.6f)
- `docs/mockups/VALIDACAO.md` — cobertura do brief e, depois do PRD existir, a checagem cruzada telas ↔ requisitos P0/P1
- `docs/mockups/arquivo-v<N>-<apelido>/` — versões anteriores arquivadas antes de regenerar

### Regras dos mockups

- Use apenas HTML/CSS puro; abre direto no navegador, offline, sem servidor
- Um arquivo por tela — nunca várias telas no mesmo arquivo; CSS inline, sem CSS compartilhado nem CDN
- Cores, fontes e espaçamentos vêm do baseline visual (provisório na Etapa 0, `docs/DESIGN.md` depois de promovido)
- Represente os estados relevantes de cada tela (vazio, erro, carregando, sucesso) e use dados realistas do domínio — nunca placeholder
- Declare no rodapé de cada tela as suposições que a IA tomou por conta própria
- Links entre telas funcionam; botão sem destino mostra `alert` explicando a ação
- Toda capacidade citada pelo usuário aparece em pelo menos uma tela; depois do PRD, todo requisito P0/P1 também
- **Tela de Loja de Apps é obrigatória** — lista o catálogo de apps com estado ativo/inativo por tenant e controle de ativação (ver `docs/regras/apps-loja-de-apps.md`). Só pode ser omitida em projeto explicitamente definido como app único
- Antes de regenerar telas existentes, arquive a versão anterior em `docs/mockups/arquivo-v<N>-<apelido>/`

> Detalhes completos do fluxo estão em `docs/regras/mockup-first.md` e na seção "Fluxo de Mockups" do `SKILL.md` da `omnx-code`.
