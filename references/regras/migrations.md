# 🗃️ Regra de Migrations — SQL Direto Proibido (INEGOCIÁVEL)

**Toda alteração no banco Supabase DEVE passar por uma migration versionada em `supabase/migrations/`.** Nenhuma mudança de banco pode ser feita por SQL direto. O schema do banco é reconstruído 100% a partir das migrations — sem exceção.

## ❌ Caminhos proibidos para alterar o banco

- SQL Editor do painel Supabase (Dashboard → SQL Editor → Run)
- `supabase db execute --sql "..."` ou `supabase db query` para mutação
- `psql -c`, `psql -f` solto, ou qualquer cliente direto rodando DDL/DML
- RPCs que executam SQL arbitrário (`db.sql(...)`, `exec_sql`, etc.)
- DDL/DML inline no código da aplicação (criar/alterar tabela em runtime)

Cobre tudo: tabelas, colunas, índices, enums, constraints, extensões, functions, triggers, views, policies de RLS, grants e seeds estruturais. **Se muda o banco, vira migration.**

## ✅ Fluxo obrigatório

```bash
supabase migration new <descricao>                 # 1. cria o arquivo
# editar supabase/migrations/<timestamp>_<desc>.sql # 2. escreve o SQL
supabase db push                                    # 3. aplica (remoto) — ou `supabase db reset` local
supabase gen types typescript --project-id <ref> \  # 4. regenera os tipos
  > src/integrations/supabase/types.ts
```

## Regras

- Nunca edite uma migration já aplicada — crie uma nova para corrigir
- A migration e o código que depende dela entram no **mesmo commit**
- `supabase/migrations/` nunca vai no `.gitignore` — é a fonte de verdade do schema
- A única exceção para SQL direto é leitura (`SELECT`) para inspeção — nunca para mutar
- Detalhes operacionais vivem em `docs/ARQUITETURA.md` (seção de banco)
