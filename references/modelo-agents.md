# AGENTS.md — OMNX Code Project Rules

> Este arquivo sincroniza as regras do CLAUDE.md para todos os agentes de AI
> (Lovable, Cursor, Windsurf, Codex, Jules, etc.). Fonte de verdade: `CLAUDE.md`.
> Gerado e mantido automaticamente pela skill omnx-code. Não edite manualmente.

---

## Stack obrigatória

- React 18 + TypeScript strict + Vite
- Tailwind CSS + shadcn/ui
- Supabase (auth + database + storage)
- Vercel (deploy) + Cloudflare (DNS/WAF)
- Nunca introduza dependências fora desta stack sem aprovação explícita do usuário

## Regras de segurança (inegociáveis)

- NUNCA use `SUPABASE_SERVICE_ROLE_KEY` no frontend ou em qualquer código client-side
- NUNCA exponha chaves de API, tokens ou secrets em código commitado
- NUNCA crie arquivos `.env` sem garantir que estão listados no `.gitignore`
- Sempre ative Row Level Security (RLS) em todas as tabelas do Supabase
- Sempre use tokens temporários e escopados — nunca chaves de admin para operações de usuário
- Ao detectar qualquer violação dessas regras no código existente, reporte imediatamente antes de continuar

## Regras de Git (inegociáveis)

- `.env`, `.env.*`, `*.pem`, `*.key` e arquivos com chaves sempre no `.gitignore`
- Commits seguem Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Nunca use mensagens genéricas: `update`, `ajustes`, `misc`, `wip`, `temp`, `fix stuff`
- Nunca force-push na branch `main` — o Lovable e o Vercel rastreiam essa branch
- Nunca delete ou renomeie a branch `main` sem reconectar o Lovable e o Vercel

## Regras de acesso Lovable (inegociáveis)

- Nunca remova deploy keys do GitHub Settings deste repositório
- Nunca revogue o OAuth app "Lovable" na conta GitHub
- Nunca renomeie ou transfira o repositório sem antes reconectar no painel do Lovable
- O diretório `.lovable/` e arquivos `lovable.config.*` são somente leitura — nunca edite, mova ou delete sem instrução explícita do usuário seguida de confirmação
- Nunca altere a visibilidade do repositório de forma que bloqueie o acesso do Lovable

## Fluxo de desenvolvimento

- Antes de codar qualquer feature: verifique se existem `PRD.md`, `ROADMAP.md` e `ARQUITETURA.md`
- Se não existirem → crie esses documentos primeiro. Não comece a codar sem eles
- Toda documentação técnica vai para `docs/[NOME].md`
- O `CLAUDE.md` é um índice enxuto — nunca coloque documentação longa diretamente nele
- Ao remover uma feature: delete o código, o doc em `docs/` e a entrada no índice do `CLAUDE.md`

## Comunicação

- Responda sempre em português brasileiro
- Seja didático e paciente — assuma que o usuário pode ter conhecimento zero sobre o tema
- Explique o que vai fazer antes de fazer
- Nunca tome ações irreversíveis (deletar dados, force-push, alterar permissões) sem confirmação explícita

---

Se o usuário pedir algo que viole as regras acima (usar `service_role_key`, tornar repo público, force-push em `main`, remover deploy key do Lovable), **recuse, explique o motivo e sugira a alternativa segura**.

---

> Sincronizado com `CLAUDE.md` pela skill omnx-code.
> Para documentação completa do projeto, leia o `CLAUDE.md` e os arquivos em `docs/`.
> Versão do template: omnx-code v1.7
