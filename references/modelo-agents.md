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
- **Gate de deploy (fail-closed):** antes de qualquer deploy em produção, merge em `main` ou `git push` que dispare a Vercel, execute a skill `/security-auditor` e só prossiga se `security-report/verdict.json` existir com `"gate": "PASS"`. P0/P1 em aberto (ou `❔ não verificado`/`⚠️ ação manual` em P0/P1) BLOQUEIAM — recuse o push/merge até correção + re-teste. Sem `verdict.json` da sessão atual, não publique.
- A correção automática da auditor é opt-in: nunca aplique auto-fix sem confirmação explícita do usuário.

## Regra de UML obrigatório (inegociável)

- Nenhum código de domínio (models, entidades, schema) é escrito em projeto novo antes de `docs/UML.md` existir e ser aprovado (diagrama de classes/entidades em Mermaid + sequência dos fluxos críticos)
- Em projeto existente sem `docs/UML.md`: nenhum commit novo acontece antes de gerar o UML por engenharia reversa do código/schema real e validar com o usuário
- `docs/UML.md` é atualizado no mesmo commit que qualquer mudança de entidade, relacionamento ou fluxo crítico — nunca depois

## Regra de arquitetura de usuários e multi-tenant (inegociável)

- Todo sistema é multi-tenant por padrão: tabela de tenants + membership + papéis (roles) entram na primeira migration, antes de qualquer tabela de negócio
- Toda tabela de negócio nova carrega `tenant_id` (FK not-null) desde o dia 1
- Toda política RLS de tabela com `tenant_id` filtra por tenant, não só por `auth.uid()` — evita vazamento entre contas quando o mesmo usuário pertence a mais de um tenant
- Exceção só é válida se o usuário confirmar explicitamente projeto single-tenant, documentado em `docs/ARQUITETURA.md`
- **Gate obrigatório (fail-closed):** nenhum código de autenticação/autorização é commitado, e nenhum deploy acontece, sem `docs/NIVEIS-DE-ACESSO.md` existir com a matriz completa papel × recurso × ação (sem células em branco). Um papel/permissão no código sem entrada no documento é bug, não pendência
- `docs/NIVEIS-DE-ACESSO.md` é atualizado no mesmo commit que cria/altera um papel ou permissão — nunca depois

## Regra de banco de dados (inegociável)

- TODA alteração no banco Supabase é feita via migration versionada em `supabase/migrations/`
- É PROIBIDO executar SQL direto para mudar o banco: nada de SQL Editor do Supabase, `supabase db execute`, `psql`, ou RPC que rode SQL arbitrário
- Nunca edite uma migration já aplicada — crie uma nova para corrigir
- A migration e o código que depende dela entram no mesmo commit
- `supabase/migrations/` nunca vai no `.gitignore` — é a fonte de verdade do schema
- Leitura (`SELECT`) para inspeção é permitida; qualquer mutação só via migration
- Após aplicar migrations, regenere os tipos: `supabase gen types typescript`

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

Se o usuário pedir algo que viole as regras acima (usar `service_role_key`, tornar repo público, force-push em `main`, remover deploy key do Lovable, executar SQL direto no banco em vez de migration, **fazer deploy/merge em `main` sem `security-report/verdict.json` com `gate: PASS`**, **commitar código de autenticação/autorização sem `docs/NIVEIS-DE-ACESSO.md` completo**, **criar tabela de negócio sem `tenant_id` em projeto multi-tenant**, **escrever código de domínio ou commitar sem `docs/UML.md` existir e estar atualizado**), **recuse, explique o motivo e sugira a alternativa segura**.

---

> Sincronizado com `CLAUDE.md` pela skill omnx-code.
> Para documentação completa do projeto, leia o `CLAUDE.md` e os arquivos em `docs/`.
> Versão do template: omnx-code v1.10
