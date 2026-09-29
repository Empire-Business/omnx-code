# Recuperação, sessões e concorrência

Use checkpoint por projeto/worktree/sessão, não latest global. Ele referencia Task e snapshot, última
conclusão real e próxima ação dentro da Task. Não copia backlog, PRD ou conversa inteira.
A Task pode ter sido cancelada/revogada desde o checkpoint; fonte canônica prevalece.
Compare hash de Task e arquivos antes de reutilizar. Estado desconhecido não vira conclusão.

Locks do runtime coordenam processos locais cooperantes, liberados pelo sistema ao fechar/crash.
Não apague lock só pela idade; não alegue coordenação entre computadores. Git/PR deve resolver integração
entre máquinas. CAS rejeita edição perdida. Arquivos de metadados não devem ser editados por dois agentes
sem ler a versão atual e coordenar. Escrita arbitrária externa não é magicamente serializada pelo runtime.

Cancelamento impede novos efeitos; operação remota já enviada pode ter concluído. Verifique identidade
antes de repetir. Nunca refaça cobrança por timeout às cegas.

Migração interrompida: doctor → migrate status → resume com mesmo plano/digest ou rollback.
Não modifique manualmente journal/backup para forçar sucesso. Edição posterior causa conflito deliberado,
não autorização para restaurar por cima. Guarde cópia, reconcilie diferenças e replique só a correção necessária.

Em incidente com schema legado incompatível, faça diagnóstico/estabilização local autorizados fora das
escritas normais de metadados. Guarde evidência restrita temporária com correlação; importe uma vez após
migração. Isso não é segundo backlog permanente. Não reorganize toda documentação antes de conter dano.

Falha não prevista: pare apenas efeito inseguro, preserve identidade/evidência, classifique a incerteza,
faça menor verificação segura e entregue a decisão necessária. Não retry infinito nem trabalho assíncrono fictício.

## Journal automático do host

Hooks ativos podem manter journal por cópia de trabalho, host e sessão em .omnx/local/automation. O journal registra sinais compactos, hash da sessão, estado observado, próximo passo e referência à Task canônica; não é backlog nem cópia de conversa. Task e journal têm estados separados.

Interrupção/sessão encerrada gera checkpoint para a Task não terminal. Encerramento do host não significa conclusão. Sinal com mais de cinco minutos aparece como sem atividade recente, mesmo se a Task continua in_progress. Compare a Task, o checkpoint e os arquivos antes de retomar.

Hooks usam tentativas limitadas para colisão temporária de metadados e falham abertos. Se o journal indicar indisponível, não afirme que progresso foi capturado. Console/browser não é dependência do journal, e fechar a janela não encerra o host. Verifique falhas antes de fazer replay ou repetir eventos; IDs de evento tornam reenvio idempotente.
