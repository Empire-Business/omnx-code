# Hooks, sessões e acompanhamento local

Carregar ao configurar hooks ou diagnosticar captura automática. O suporte é por projeto, explícito e confiado; uma skill textual sozinha não intercepta sessões.

## Ativação única

Revise o AGENTS.md da raiz escolhida e calcule o hash atual antes de instalar. A CLI recusa a instalação se raiz/hash não corresponderem. O comando altera somente a configuração local daquele projeto e preserva os grupos de hooks existentes:

~~~sh
shasum -a 256 AGENTS.md
python3 <skill>/scripts/omnx.py --root <projeto> hooks install codex \
  --trust-root --expected-agents-sha256 <hash-atual>
python3 <skill>/scripts/omnx.py --root <projeto> hooks install claude \
  --trust-root --expected-agents-sha256 <hash-atual>
~~~

Codex usa .codex/hooks.json; o usuário ainda deve revisar e confiar na definição em /hooks. Claude Code usa .claude/settings.local.json e respeita a confiança local do projeto. Nenhum arquivo global é instalado. Omissão, recusa ou remoção da configuração significa que a captura não está ativa.

Eventos/configurações seguem as referências oficiais consultadas em 28 de setembro de 2026: [hooks do Codex](https://learn.chatgpt.com/docs/hooks?translationFallback=de-DE) e [hooks do Claude Code](https://code.claude.com/docs/en/hooks). Eventos, permissões e payloads podem mudar; confirme no host instalado antes de ampliar cobertura.

## Caminho capturado

- UserPromptSubmit cria ou reutiliza uma Task canônica somente quando a primeira linha parece um pedido explícito de implementação em inglês ou português. Explicações, análises e prompts ambíguos não iniciam Console nem Task. A classificação por prefixo pode deixar passar outras formas de pedido.
- A Task fica em .omnx/tasks e usa uma referência estável derivada da sessão/turno. A origem registrada aponta ao prompt recebido; isso não concede permissões de produto, produção, publicação, cobrança ou migração de dados.
- O resumo é a primeira linha, com limite de 180 caracteres e remoção de alguns padrões comuns de segredo/e-mail. Redaction por padrão não é detector completo; evite incluir dados pessoais, clientes, segredos ou texto privado no título.
- PostToolUse registra somente sinal de atividade, sem argumentos, saída, arquivos ou conteúdo de código. Eventos idempotentes usam IDs do host quando disponíveis.
- Codex registra Interrupt, Stop e SessionEnd; Claude registra Stop e SessionEnd conforme os eventos disponíveis. O encerramento gera checkpoint compacto e não marca a Task como concluída. Uma atualização canônica de Task espelha bloqueio, revisão ou conclusão no journal.
- No primeiro pedido de implementação da sessão, o launcher tenta iniciar/reutilizar o Console e direcioná-lo à cópia de trabalho e Task. A tentativa é deduplicada. Fechar o navegador não interrompe código nem reabre a janela repetidamente.
- Consulta de release em segundo plano só começa quando a política opt-in daquele projeto está ativa e o intervalo expirou.

## Estados e recuperação

A Task canônica, o estado da sessão e a presença do Console são campos diferentes. O journal local em .omnx/local/automation/ guarda IDs com hash, timestamps, estado/etapa, próximo passo e até 100 sinais compactos por sessão. Não guarda conversa, chamadas de ferramenta ou código. Clones/worktrees têm identidade própria.

Console: servidor iniciado/reutilizado, abertura do navegador solicitada/indisponível/não solicitada e cliente autenticado conectado/não confirmado são registrados separadamente. Cliente conectado não significa que alguém leu a tela. Sem sinal recente, a UI mostra atividade não confirmada e mantém o estado canônico da Task.

Falha no browser/Console não impede a edição nem apaga o registro local. Conflito temporário de metadados recebe poucas tentativas idempotentes; se persistir, o hook retorna aviso sem bloquear o host. Confira o journal e Task com CLI antes de afirmar acompanhamento confirmado. Corrija acesso/integração e gere novo evento ou atualização canônica; não invente heartbeat nem progresso percentual.

Remover somente hooks OMNX:

~~~sh
python3 <skill>/scripts/omnx.py --root <projeto> hooks remove codex \
  --trust-root --expected-agents-sha256 <hash-atual>
~~~

## Cobertura real

| Host | Entrada direta | Captura após configuração | Limites atuais |
|---|---|---|---|
| Codex | Sim, pelo hook local do projeto confiado | Prompt, atividade de ferramenta, interrupção, parada e fim da sessão | Revisar/confiar em /hooks; payload de ferramenta não é guardado; hooks novos seguem o projeto selecionado |
| Claude Code | Sim, pelo hook local do projeto | Prompt, atividade de ferramenta, parada e fim da sessão | Confiança local do host; não há evento Interrupt configurado nesta integração |
| Sessão sem hooks | Parcial | Nenhuma captura automática garantida | Wrapper/ativação manual pode orientar, mas não intercepta outras formas de entrada |

A confiabilidade do evento depende da versão/configuração do host. Consulte reports/VALIDATION.md; testes sintéticos não equivalem a homologação em Claude Code ou Codex reais.
