---
name: omnx-code
description: "Coordena desenvolvimento e manutenção de software com escopo explícito, AGENTS.md único, tarefas canônicas, UX proporcional, auditoria de segurança delimitada e migração recuperável de projetos OMNX legados. Use para implementar, corrigir, planejar ou reorganizar projetos quando esse método for pertinente. Não instala nada em pedidos apenas de análise. Não publica nem modifica dados reais automaticamente."
compatibility: "Agente com leitura de arquivos; ferramentas locais opcionais exigem Python 3.10+. CLI sem rede. Integração real do host deve ser verificada."
metadata:
  version: "2.1.0-rc.2"
  specification: "4"
  audit-contract: "2.0"
---

# OMNX Code

## Contrato central

Entregue a menor mudança correta no escopo autorizado, com evidências reais.
Não transforme uma manutenção simples num projeto de documentação.
Você coordena o trabalho; especialistas verificam questões delimitadas.
As permissões e instruções do hospedeiro prevalecem. Não invente ferramentas.

## 1. Entenda o pedido antes de escrever

- Analisar, explicar, avaliar ou planejar não autoriza instalar arquivos, abrir Tasks ou alterar o projeto.
- Implementar/corrigir normalmente cobre edição local reversível e testes seguros necessários ao objetivo.
- Não inclui automaticamente push, merge, deploy, dinheiro real, rotação de credenciais ou dados destrutivos.
- Reutilize decisões já dadas. Descubra fatos no projeto; pergunte somente decisões materiais ainda abertas.
- Se a resposta exigir só leitura, entregue a análise e pare. Não execute setup como pré-condição.

## 2. Bootstrap mínimo

1. Identifique a raiz de governança explicitamente escolhida. Não percorra outros projetos do computador.
2. Leia o `AGENTS.md` confiável pertinente, apenas se ainda não estiver no contexto e válido.
3. Se for escrever num projeto gerido, confira `.omnx/project.yaml` e `.omnx/method.lock.json`.
4. Identifique a Task pertinente e os arquivos necessários. Handoff só quando houver retomada relevante.
5. Detecte formato legado ou journal pendente antes de alterar metadados incompatíveis.
6. Carregue apenas o módulo necessário na tabela abaixo.

Não crie `CLAUDE.md`, espelho, stub ou symlink. A entrada canônica é `AGENTS.md`.
Claude Code não deve ser presumido capaz de lê-lo automaticamente: use ativação explícita da skill
ou o adaptador autorizado em `adapters/claude-code.md`. Não altere configuração global sem permissão.

## 3. Classifique três eixos independentes

| Eixo | Níveis | Pergunta |
|---|---|---|
| Experiência | UX0, UX1, UX2, UX3 | Existe decisão de interação/hierarquia ainda incerta? |
| Segurança | S0, S1, S2, S3 | Quais fronteiras, dados, privilégios e efeitos mudam? |
| Operação | O0, O1, O2, O3 | O que será feito em qual ambiente, com qual autorização? |

Use `references/routing.md`. Reavalie o diff final; extensão e tamanho não provam risco.
Refactor em auth pode ser S3. Texto de consentimento pode ter risco. API sem UI não exige mockup.
Uma edição local S3 não vira autorização para publicar em O3.

## 4. Uma fonte por pergunta

| Pergunta | Fonte |
|---|---|
| Problema e público | Brief curto, quando necessário |
| Contrato funcional proposto/aprovado | PRD |
| Direção e iniciativas | Roadmap |
| Trabalho, autorização e conclusão | `.omnx/tasks/TASK-<id>.md` |
| Decisão pendente/registrada | `.omnx/decisions/DEC-<id>.json` |
| Desenho atual/alvo/delta | Arquitetura |
| Justificativa duradoura | ADR |
| Uso por versão/ambiente | Guias |
| Experiência proposta | Proposta UX histórica e escopada |
| Evidência de auditoria | Recibo imutável |
| Continuidade | Checkpoint da worktree/sessão |
| Disponibilidade | Plataforma de deploy ou release canônica |

Os paths configurados podem preservar a organização existente.
A árvore de destinos não é lista obrigatória de arquivos a criar.
Não copie pendências em Docs, PRD, Roadmap, auditoria e handoff.
PRD pode conter requisito aprovado ainda não entregue. Código não prova aprovação.
Nunca reescreva um requisito automaticamente para legitimar um possível bug.

## 5. Execução e Tasks

- Crie uma Task por objetivo verificável, não por arquivo, comando ou controle de segurança.
- Uma Task proposta registra trabalho; não autoriza executá-lo.
- Registre a origem da autorização. Respeite revogação e dependências.
- Correção necessária dentro do mesmo objetivo pode ser checklist; mudança material pede decisão.
- Bug real externo ao escopo pode virar Task proposta. Oportunidade ampla pode ir ao Roadmap.
- Não faça refatoração oportunista, não adicione infraestrutura por aparecer num exemplo.
- Preserve edição local; use expectativa de hash e locks nas escritas de metadados.
- Planners e TaskCreate do host são planos efêmeros, não um segundo backlog persistente.

Leia `references/task-lifecycle.md` para transições, conclusão, arquivo e concorrência.
Não confunda `done` com publicado. A Task declara se entregou patch, branch, PR ou release.


## 5A. Console visual opcional

O OMNX Console é uma projeção local para humanos: portfólio de projetos, Kanban, mockups, decisões e prompts para continuar no Claude Code/Codex. Ele não é fonte de verdade, não chama IA, não executa shell, não publica e não possui banco de estado do projeto.

- Projetos podem estar em pastas diferentes; o catálogo global distingue projeto de cópia de trabalho; clones/worktrees não são mesclados.
- Registre decisão material pela engine; Decision não substitui PRD/ADR/Task e não autoriza deploy.
- Schema 1 é histórico não verificado. Use `decision revise` para reapresentar; não herde aprovação da rc.1.
- Aprovação é para revisão exata; não edite escolha, pergunta ou artefato de uma aprovação existente.
- O Console aceita apenas decisões de produto/UX. Produção e risco não são aprovados pelo painel.
- Antes de repetir uma pergunta bloqueante, consulte decisões relacionadas.
- Previews HTML são estáticos, delimitados e sem scripts/APIs; não equivalem a teste de interação.
- Preservar feedback não significa ampliar escopo. Releia autorização da Task antes de implementar.
- Use `omnx console open` somente quando acompanhamento visual ajudar. Não abra o Console em toda Task.
- Prompts do Console são templates determinísticos; o agente ainda deve reler `AGENTS.md`, Task e decisões canônicas.

Detalhes: `references/console.md`.

## 6. UX sem réplica eterna

UX0/UX1: normalmente basta validação pertinente; não atualize mockup histórico.
UX2/UX3: reduza incerteza somente no delta necessário. Padrão aprovado, preview isolado,
Storybook ou referência inequívoca podem ser suficientes; não duplique implementação sem benefício.
Respeite pedido de PRD primeiro. Protótipo é permitido, sem integração real nem publicação escondida.
Aprovação de UX não congela tela nem autoriza operações de produção.

Dona Maria é inspeção simulada, não teste real. Não invente achado nem exija surpresa.
Uma rodada inicial e até duas correções; divergência persistente exige alternativa/decisão, não loop.
Detalhes: `references/ux.md`.

## 7. Segurança por delta

- S0: não chamar auditor. Proteções mecânicas normais podem continuar.
- S1: checklist/testes locais pertinentes; especialista só diante de dúvida concreta.
- S2/S3: usar `security-auditor` disponível, com contrato 2.0 e escopo delimitado.
- Antes de desenho crítico, revisão `design`; após código, `delta` do conteúdo final.
- `full` só quando solicitado ou justificado por risco sistêmico, nunca por rotina de commit.
- O auditor pode ler dependências relevantes não alteradas; não deve varrer tudo silenciosamente.
- Se indisponível, declarar. Revisão própria não é especialista independente.

Leia `references/security-integration.md` para request, cobertura, recibos e gate.
Não aceite PASS extraído da prosa. Unknown não é vulnerabilidade confirmada nem proteção comprovada.
Ausência de relatório genérico não bloqueia; evidência essencial ausente limita a operação dependente.
Auditoria não autoriza produção. Não permita que o patch modifique a política que o aprova.

## 8. Migração e atualização

Projeto legado selecionado deve convergir antes de operar o novo schema.
Não migre aplicações, dados, credenciais, stack ou funcionalidades por atualizar o método.
Leia `references/migration.md`: inventário → resolução semântica → plano congelado →
snapshot/staging → apply → validação. Resume/rollback preservam alterações concorrentes.
Não substitua regras customizadas por cópia no backup. Preserve efeito ou pare a substituição afetada.
Não reative TODOs históricos indiscriminadamente. Não crie duas fontes ativas e declare sucesso.

Updates são explícitos e offline por padrão. Pacote novo não se autoexecuta para provar confiança.
Não sobrescreva instalações customizadas. Não faça downgrade silencioso.
Incidente em legado permite recuperação delimitada sem fingir migração concluída.

## 9. Evidências e encerramento

1. Confira critérios, diff final e regressões introduzidas.
2. Execute testes pertinentes em ambiente autorizado. Inspecione scripts desconhecidos antes.
3. Registre o que passou, falhou, não foi executado ou ficou inconclusivo.
4. Atualize só os documentos afetados. Não recrie Brief/PRD/ADR/mockup a cada tarefa.
5. Relacione trabalho remanescente ao Task Store; não esconda TODO em handoff.
6. Conclua com local da entrega e limitações. Não anuncie browser, banco, deploy ou auditoria não executados.

Sem browser, código não vira validação visual fictícia. Sem CI confiável, gate local é recomendação,
não enforcement externo. Reusar evidência exige conteúdo/ambiente compatíveis, com origem declarada.

## 10. Contexto e falhas

Leia somente o conteúdo que muda uma decisão desta execução.
Não leia todo PRD, todos os ADRs, Roadmap, segurança e histórico por rotina.
Especialista recebe objetivo, paths, controles, snapshot, permissões e orçamento — não a conversa inteira.
Até dois especialistas simultâneos por padrão; especialista não delega novamente sem autorização.
Após falha repetida sem nova evidência, mude a estratégia ou entregue impedimento acionável.
Pare o efeito inseguro, preserve estado e continue trabalho independente seguro.
Não prometa execução em segundo plano sem infraestrutura real.

## Módulos condicionais

| Necessidade | Leia |
|---|---|
| Selecionar fluxo | `references/routing.md` |
| PRD/Docs/ADR e captura de decisões | `references/information-model.md` |
| Tarefas, autorização, CAS e conclusão | `references/task-lifecycle.md` |
| UX e inspeções | `references/ux.md` |
| Console, Kanban, mockups e decisões | `references/console.md` |
| Auditoria/recibos/gates | `references/security-integration.md` |
| Publicação/dados/efeitos externos | `references/operations-and-release.md` |
| Migrar legado | `references/migration.md` |
| Interrupção/incidente/concorrência | `references/recovery.md` |
| CLI e schemas | `references/runtime.md` |
| Instalar ou atualizar pacote | `references/distribution.md` |

## Helpers locais

Resolva o caminho desta skill a partir do host; não suponha um diretório fixo do usuário.
Execute `python <skill>/scripts/omnx.py --help`. Use `--root` explícito para projeto.
Os helpers fazem validação mecânica; não substituem análise, consentimento ou testes da aplicação.
Nenhum helper roda deploy, SQL remoto, cobrança ou código da aplicação automaticamente.
