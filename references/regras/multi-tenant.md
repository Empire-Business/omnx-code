# 🏢 Arquitetura de Usuários & Multi-Tenant (INEGOCIÁVEL)

**Todo sistema deste projeto é multi-tenant por padrão**, mesmo que hoje só exista um cliente/empresa usando. Migrar um schema single-tenant para multi-tenant depois que já existem dados em produção é caro e arriscado — nascer multi-tenant custa quase nada e evita essa dor depois.

> ⚠️ **Exceção:** só pule o modelo multi-tenant se o usuário confirmar explicitamente que o projeto é de uso único (ex: ferramenta interna pessoal, protótipo descartável) — e mesmo assim, documente a decisão em `docs/ARQUITETURA.md`.

## Modelo obrigatório

| Peça | O que é | Exemplo de nome |
|------|---------|------------------|
| **Tenant** | A entidade que isola os dados (empresa, conta, time) | `tenants` / `organizations` |
| **Membership** | Liga `auth.users` ao tenant — um usuário pode pertencer a vários tenants | `tenant_members` |
| **Papéis (roles)** | Nível de permissão do usuário dentro do tenant | `owner`, `admin`, `member` |
| **Isolamento** | Toda tabela de negócio carrega `tenant_id` (FK not-null) | `orders.tenant_id`, `projects.tenant_id` |

## Regras

- A tabela de tenants e a de membership entram na **primeira migration** do projeto — antes de qualquer tabela de negócio.
- Toda tabela de negócio nova (não-catálogo, não-config global) nasce com `tenant_id` desde o dia 1. Nunca "adiciona depois".
- Toda política RLS de tabela com `tenant_id` filtra por tenant **e** por papel quando a operação exigir (ex: `DELETE` só para `owner`/`admin`). Uma política que só checa `auth.uid()` sem checar o tenant vaza dados entre contas diferentes quando o mesmo usuário pertence a mais de um tenant.
- Se o produto permite trocar de tenant ativo (usuário em múltiplos tenants), o tenant ativo nunca é inferido de um dado enviado pelo cliente sem validar contra a tabela de membership.
- A matriz de permissões por papel (quem pode ver/criar/editar/deletar o quê) fica documentada em `docs/ARQUITETURA.md`, seção "Arquitetura de Usuários & Multi-Tenant" — **e**, em detalhe completo, em `docs/NIVEIS-DE-ACESSO.md` (ver `docs/regras/niveis-de-acesso.md`).
