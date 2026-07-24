# 🔄 Handoffs entre Sessões

Para economizar tokens e permitir que o usuário dê CLEAR no contexto, o projeto mantém handoffs em `docs/handoffs/`:

- `docs/handoffs/latest.md` — estado atual do projeto; lido na retomada de qualquer sessão
- `docs/handoffs/HISTORY.md` — histórico cronológico das sessões
- `docs/handoffs/README.md` — como usar os handoffs

A IA deve atualizar `latest.md` ao final de toda sessão significativa e lê-lo primeiro quando o usuário pedir para continuar, retomar ou limpar contexto.

> Detalhes completos do fluxo (o que registrar, quando criar/atualizar) estão na seção "Fluxo de Handoffs" do `SKILL.md` da `mestre-code`.
