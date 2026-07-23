# 🛂 Níveis de Acesso — Documentação Obrigatória (BLOQUEIA COMMIT E DEPLOY)

**Nenhum código de autenticação/autorização pode ser commitado, e nenhum deploy pode acontecer, sem `docs/NIVEIS-DE-ACESSO.md` existir e estar completo.** Isso vale mesmo em projetos de um único tenant — se há qualquer distinção de permissão entre usuários (ex: admin vs usuário comum), o documento é obrigatório. Não é uma boa prática opcional: é um gate, igual ao gate de segurança.

## O que o documento precisa ter

1. **Lista de todos os papéis (roles)** do sistema, com uma frase descrevendo quem é esse usuário e por que esse papel existe
2. **Matriz papel × recurso × ação** — para cada papel, o que ele pode `ver`, `criar`, `editar`, `deletar` em cada recurso/tabela/tela do sistema. Nenhuma célula pode ficar em branco ou marcada como "a definir" — se ainda não foi decidido, a decisão precisa ser tomada com o usuário antes de codar a permissão
3. **Telas/rotas por papel** — quais telas cada papel enxerga no menu e quais rotas são bloqueadas para ele
4. **Casos especiais** — comportamento quando um usuário perde acesso a um tenant, quando um recurso é compartilhado entre papéis, herança de permissão (se houver hierarquia entre papéis)

## Regra de atualização

Sempre que um papel novo é criado ou uma permissão muda, `docs/NIVEIS-DE-ACESSO.md` é atualizado **no mesmo commit** que muda o código — nunca depois, nunca "eu documento no final". Um papel ou permissão que existe no código/schema sem entrada correspondente no documento é tratado como bug, não como pendência.
