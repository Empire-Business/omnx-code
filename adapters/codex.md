# Codex

Codex descobre AGENTS.md segundo sua hierarquia e regras de confiança. Preserve as instruções carregadas; não crie equivalência com CLAUDE.md.

Instale a skill pelo mecanismo do host e confirme qual versão foi carregada. Wrapper pode iniciar Codex na raiz selecionada. Captura de sessão direta depende de hooks locais do projeto.

~~~sh
python3 <omnx>/scripts/omnx.py --root <projeto> hooks install codex \
  --trust-root --expected-agents-sha256 <hash-atual-de-AGENTS.md>
~~~

O comando edita .codex/hooks.json local, preserva os outros eventos e não altera config global. Revise e confie nos hooks em /hooks para ativá-los. Eventos UserPromptSubmit, PostToolUse, Stop, Interrupt e SessionEnd iniciam/reutilizam Task, registram sinal compacto e tentam abrir o Console no primeiro pedido explícito de implementação. Sem trust, evento suportado ou projeto OMNX gerido, a cobertura não existe. Hook não registra transcript, argumentos, código ou resultado de teste.

Use $omnx-code ou $security-auditor conforme a tarefa. OpenAI metadata facilita descoberta, mas não comprova execução ou versão efetiva da instrução na sessão. O modelo efetivo só é preenchido quando o payload do host o expõe. Veja references/host-automation.md e references/model-policy.md.

Hooks locais foram testados com payloads sintéticos, não em sessão Codex real. Revise a configuração no host instalado e registre versão/teste real antes de declarar homologação.
