# 🔑 Regras de Acesso ao Supabase (INEGOCIÁVEIS)

## ❌ Proibições absolutas

```
# NUNCA adicionar ao .env:
SUPABASE_SERVICE_ROLE_KEY=...   ← PROIBIDO
```

- A **service role key bypassa toda a segurança (RLS)** do Supabase — nunca deve aparecer no código do projeto, no `.env`, nem em nenhum arquivo versionado
- Se a IA identificar a service role key em qualquer lugar, deve alertar imediatamente e recusar continuar até que seja removida

## ✅ Como a IA acessa o Supabase

A IA deve usar **tokens temporários da conta do Supabase**, gerados via Supabase CLI, que **expiram em 7 dias**:

```bash
# O usuário gera o token assim:
supabase login
# O token fica salvo localmente e expira automaticamente em 7 dias
```

- Esses tokens têm escopo limitado e expiram, reduzindo risco de vazamento
- A cada semana (ou quando expirar), o usuário deve gerar um novo token
- A IA deve lembrar o usuário de renovar o token quando estiver próximo de expirar
