# OMNX Code

**Skill gratuita para Claude Code.** Instala método, segurança e documentação automática em qualquer app React + TypeScript + Supabase + Vercel — em um comando.

---

## O que faz

- Cria e mantém o `CLAUDE.md` do seu projeto (guia vivo de arquitetura e decisões)
- Instala e atualiza automaticamente a skill `/security-auditor` (auditoria RLS, auth, env vars)
- Executa todo trabalho com tasks visíveis — você sempre sabe o que está sendo feito
- Obriga branch dedicada para cada nova feature, fix ou doc relevante
- Padroniza commits com `Conventional Commits` e corpo documentado
- Funciona em projetos novos e existentes (merge inteligente no CLAUDE.md)

## Instalação

### Claude Code
```bash
git clone https://github.com/Empire-Business/omnx-code ~/.claude/skills/omnx-code
```

### OpenAI Codex
```bash
git clone https://github.com/Empire-Business/omnx-code ~/.codex/skills/omnx-code
```

Pronto. A skill aparece automaticamente na lista de skills do Claude Code e do Codex.

## Como usar

No Claude Code, mencione `omnx-code` ou peça para "ativar o framework":

```
/omnx-code
```

Na primeira execução faz o setup completo. Nas seguintes, vai direto ao trabalho guiado pelo `CLAUDE.md`.

No trabalho normal, a skill opera em modo conservador com Git/GitHub:
- cria branch local dedicada para cada nova tarefa
- evita trabalhar direto em `main`/`master`
- não faz `push` ou abre PR sem pedido explícito
- gera commits padronizados e bem documentados

## Stack suportada

React · TypeScript · Supabase · Vercel

## Atualizar

```bash
cd ~/.claude/skills/omnx-code && git pull
```

## Skills relacionadas

- [security-auditor](https://github.com/Empire-Business/security-auditor) — auditoria e correção automática de segurança (instalada automaticamente pelo omnx-code)

## Versão

`v1.5` — [ver CHANGELOG](./CHANGELOG.md)

---

Grátis para sempre. MIT License — [ver LICENSE](./LICENSE).

> **Aviso:** esta skill gera sugestões via IA. O autor não se responsabiliza por falhas de
> segurança em apps construídos ou auditados com ela. Leia o [LICENSE](./LICENSE) completo.
