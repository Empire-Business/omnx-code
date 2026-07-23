# 🗄️ Banco de Dados — Supabase ou Local?

Antes de iniciar o desenvolvimento, a IA deve perguntar ao usuário qual estratégia de banco deseja usar:

## Opção A — Supabase direto
- O projeto já começa conectado ao Supabase em produção
- Ideal para quem quer avançar rápido e já tem conta no Supabase
- A IA configura a conexão usando **tokens temporários** (veja `docs/regras/acesso-supabase.md`)

## Opção B — Banco local primeiro (depois migra pro Supabase)
- O projeto começa com um banco PostgreSQL local via Docker
- **Todo o schema, migrations e seeds devem ser escritos desde o início pensando no Supabase**
- A migração para o Supabase deve funcionar sem erros com um único comando
- A IA deve garantir que nenhuma feature use algo incompatível com o Supabase
- Quando o usuário decidir migrar, a IA guia o processo passo a passo

> ⚠️ Se a Opção B for escolhida, a IA deve documentar em `docs/ARQUITETURA.md` como a migração será feita antes de escrever qualquer código.
