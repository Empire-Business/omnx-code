# Tasks: trabalho acionável, autorização separada

Um arquivo Markdown por objetivo em .omnx/tasks/TASK-uuid.md. Frontmatter aceita YAML seguro ou JSON
(subconjunto YAML); CLI gera JSON para evitar coerção implícita. Corpo guarda escopo específico.
Nunca editar índice gerado para mudar estado. Arquivo legado TASKS.md exige migração, não duplicação.

Campos mínimos: schema_version, id, title, status, authorization, acceptance, created_at, updated_at.
Autorização: proposed/authorized/revoked e basis_ref. Criação não concede autoridade.
IDs UUID evitam contador global; IDs legados válidos são preservados. Título parecido não prova duplicata.

## Transições
backlog → ready/cancelled. ready → in_progress/blocked/cancelled.
in_progress → blocked/review/cancelled. blocked → ready/in_progress/cancelled.
review → done/in_progress/blocked/cancelled. done → in_progress somente reabertura explícita.
Cancelled permanece histórico. Mudança nova normalmente recebe nova Task, em vez de reabrir entrega antiga.

Ready/in_progress/review/done exigem autorização. In_progress exige owner.
Dependências precisam existir e formar grafo sem ciclos; para executar/concluir precisam estar done.
Bloqueio tem causa e condição de saída. Cancelamento/reabertura/alteração de autorização tem origem explícita.

## Escrita
Use CLI com --expected-sha256 obtido em task show/list. Releia em conflito; não substitua arquivo inteiro
para resolver divergência. Atualizações usam lock local e CAS. Arquivo arquivado mantém ID resolvível.
Não atribua a si autoridade de produto usando um texto genérico de conveniência.
O helper verifica referências declaradas, não autentica a pessoa no outro lado da conversa.

## Definition of Done
Critérios satisfeitos, diff revisado, nenhuma regressão conhecida que invalide o escopo,
testes/evidência pertinentes e documentação afetada sincronizada ou declarada não aplicável.
Closure declara patch/branch/pull_request/merged/sandbox/production/investigation.
Não requer produção se pedido era entregar código. Referência release: só quando publicação realmente ocorreu.
S3 não pode terminar por “não testado”. Controles de promoção continuam exigidos no gate separado.
A existência de uma string de evidência não prova seu conteúdo: agente/revisor deve conferi-la.

## Descobertas
Defeito introduzido deve ser corrigido no escopo. Passo proporcional necessário pode ser checklist.
Bug externo real → proposta sem execução. Dependência que altera risco/custo material → decisão.
Oportunidade ampla → Roadmap se útil. Preferência trivial → não abrir artefato por obrigação.

Archive move Task terminal mantendo bytes e ID. Não existe limpeza automática de histórico.
