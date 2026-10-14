# Execução direta e validação limitada

Esta política de trabalho vale também para referências, helpers, hooks, bibliotecas e subagentes. Não é um limite nativo nem uma barreira técnica do host. Respeite instruções obrigatórias de maior prioridade e informe conflitos concretos; não alegue que a skill ou uma regra global prevalece sobre tudo.

## Banco e infraestrutura

Sem pedido expresso da operação, identificando o ambiente de destino, não:

- Crie bancos descartáveis, temporários, de teste ou auxiliares de migrations, incluindo shadow databases.
- Inicialize instâncias, clusters ou servidores de banco; suba containers ou stack local para validar código.
- Clone bancos, restaure dumps para testes ou crie schemas alternativos para contornar a restrição.
- Execute migrations para validar, reaplique seu histórico ou faça reset, rollback, drop, truncate ou seed para testar.
- Tente sucessivos ambientes até passar; use banco real ou produção como substituto do banco descartável proibido.

“Implemente”, “corrija”, “valide”, “teste a funcionalidade” e “deixe funcionando” não autorizam essas operações. Exceção exige operação e ambiente expressos pelo usuário, vale só para aquela tarefa e não altera o padrão permanente. Não peça autorização a cada etapa: continue o trabalho permitido e registre a pendência.

Quando a mudança exigir migration, leia schema e migrations relevantes, prepare o SQL e revise dependências, nomes, tipos, permissões e compatibilidade com o código. Não edite migrations antigas já aplicadas para facilitar testes. Sem autorização de execução, informe: “Migration preparada e revisada estaticamente; execução e validação em banco não realizadas.” Criar o arquivo não valida a migration em banco.

## Verificações

- Por tarefa, no máximo 2 execuções de validação no total, contando repetições e subagentes, com até 60 segundos cada. Não é obrigatório consumir ambas.
- Antes de iniciar, imponha timeout que encerre o processo e seus filhos associados. Use mecanismo já disponível, sem instalar ferramentas. Espera da ferramenta ou retorno de ID de sessão não encerra processos. Se não puder limitar com segurança um comando potencialmente demorado, não o inicie.
- Confira a definição do script e os hooks diretamente relacionados. Se preparar banco, infraestrutura, migrations ou dados, não execute sem a autorização específica acima. Se uma inspeção curta não esclarecer os efeitos, registre a dúvida e não execute.
- Escolha a menor verificação útil. Não agrupe baterias para contornar o limite. Não execute automaticamente suíte completa, E2E completo, carga, stress, cobertura completa, watch, repetições até passar ou sequência de lint + tipos + build + testes.
- Não reescreva scripts, remova testes, esconda falhas ou desative proteções para caber no orçamento.

Falhou: leia o erro, corrija a causa identificada e no escopo, e repita apenas se houver orçamento. Causa de ambiente, credencial, serviço indisponível ou infraestrutura ausente não autoriza reconstruir o ambiente.

Atingiu o limite: pare. Não aumente timeout, reinicie orçamento ou abra agente/sessão para continuar verificando. Compactação, retomada, revisão de segurança e smoke após publicação compartilham o orçamento da tarefa. Alto risco e melhor prática não são exceções.

Se houver falha crítica ou faltar validação essencial, declare a entrega pendente de validação; não anuncie sucesso, faça deploy ou execute mudanças de banco para compensar. Preserve os controles de segurança e entregue a pendência específica.

## Escopo e encerramento

Investigue somente o necessário, implemente a menor alteração correta e pare ao atender o pedido. Não crie documentação, ambientes ou melhorias fora do escopo. Preserve as escolhas do usuário de modelo, esforço, velocidade, service tier, perfis e aliases, além de autenticação, MCPs, integrações e permissões. Não configure essas escolhas por iniciativa da skill.

Informe o que mudou, o que foi efetivamente verificado, o que ficou pendente e por quê, e bloqueios reais. Para ajustes apenas de instruções, releitura e conferência estática bastam; não abra ambientes nem rode testes de aplicação por rotina.
