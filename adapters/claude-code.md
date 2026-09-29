# Claude Code sem CLAUDE.md

Somente AGENTS.md é canônico. Claude Code não deve ser presumido capaz de ler esse arquivo em toda sessão; use a skill instalada ou o wrapper confiável para as instruções atuais.

Hooks locais podem capturar sessões diretas depois da configuração inicial aprovada:

~~~sh
python3 <omnx>/scripts/omnx.py --root <projeto> hooks install claude \
  --trust-root --expected-agents-sha256 <hash-atual-de-AGENTS.md>
~~~

A configuração fica em .claude/settings.local.json. Os grupos já existentes são preservados; nenhuma configuração global, bypass de permissão ou arquivo CLAUDE.md é instalado. Claude deve confiar na raiz do projeto para os hooks locais serem executados. UserPromptSubmit, PostToolUse, Stop e SessionEnd registram sinais compactos, Task canônica e checkpoint, e tentam abrir o Console uma vez no início da implementação. Esta integração não registra argumento/saída de ferramenta e não configura evento Interrupt. Falha do hook é fail-open e deve aparecer como ausência de captura confirmada.

O wrapper de execução da OMNX continua disponível e requer --execute, confiança da raiz e hash atual. Ele mantém o prompt padrão do host, não cria CLAUDE.md e recusa flags conhecidas para substituir prompt ou pular proteções. Não é sandbox para todas as opções da CLI.

Versão do hook não prova a versão de instrução já carregada pelo modelo; configuração de esforço/modelo também pode ser herdada ou substituída pelo host. Veja references/host-automation.md e references/model-policy.md.

Hooks foram testados com fixtures sintéticas, não em Claude Code real. Confirme versão, trust e execução no host antes de afirmar homologação automática.
