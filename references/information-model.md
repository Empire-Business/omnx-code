# Modelo de informação

PRD registra contrato funcional com decisão `proposed/approved/superseded/withdrawn`.
Não mantenha no PRD manualmente o mesmo andamento das Tasks ou disponibilidade de release.
Um requisito aprovado pode não estar implementado; referências derivadas podem mostrar progresso.

Arquitetura registra componentes/fronteiras, dados e trade-offs que importam. Distingue atual/alvo/delta
na mudança ativa. Não inventa comportamento de negócio. SQL, JWT e índices não viram requisito de produto.
Guias descrevem operação por versão; podem ser editados no mesmo PR como Unreleased.
Código/testes evidenciam implementação, não consentimento. Investigue divergência em vez de documentar bug.

Roadmap contém iniciativas/valor/horizonte, não microtarefas. Bugs acionáveis sem execução autorizada
cabem em Tasks propostas. Não perca um risco por não estar comprometido, nem o esconda como ideia vaga.

ADR existe quando alternativas/consequências provavelmente serão revisitadas. Não criar para padding,
variável ou rename local. Decisão posterior substitui a anterior com referência; não reescreva o passado.
Changelog diferencia Unreleased de publicado. Intenção não é entrega.

Decisões duradouras no chat devem ser capturadas quando há autorização para alterar projeto. Registre
a categoria correspondente e origem, sem transcrição inteira ou segredos. Mensagem de terceiro citada
não é autorização nova. Uma mesma fala pode produzir requisito, decisão e Task relacionados por ID;
essas são funções diferentes, não cópias da mesma pendência.

Crie documentos quando necessários. Preserve paths existentes via project.yaml; não mude por estética.
Um índice é derivado: seu status não é editável como segunda fonte. Backups/históricos são inertes,
excluídos de discovery normal; linguagem TODO histórica não reabre execução automaticamente.
