# 🔐 Segurança — Princípios e Uso da Skill /security-auditor

**A IA DEVE aplicar os princípios de segurança do OMNX em todas as fases do projeto, mesmo quando a `/security-auditor` não está sendo executada no momento.**

## Princípios obrigatórios (sempre ativos)

| Princípio | Onde vive | Quando verificar |
|-----------|-----------|------------------|
| Tenant isolation (`tenant_id` FK not-null em tabelas de negócio) | `docs/ARQUITETURA.md`, migrations | Em toda tabela nova |
| RLS ativo em todas as tabelas afetadas | migrations, policies | Em toda tabela nova/alterada |
| Níveis de acesso documentados | `docs/NIVEIS-DE-ACESSO.md` | Antes de código de permissão e deploy |
| Secrets nunca no código | `.env`, `.gitignore`, Vercel env | Em todo commit |
| Headers de segurança e rate limiting | `vercel.json`, middleware de API | Em toda rota/endpoint novo |
| Tokens temporários (máx. 7 dias) | `.env`, `supabase` CLI | Ao rotacionar chaves |

## Uso da skill `/security-auditor`

A `/security-auditor` é uma skill especializada em auditoria de segurança. Seu uso segue estas regras:

| Momento | Obrigatório? | Observação |
|---------|--------------|------------|
| Instalação/atualização | ✅ Sim, automática | A `mestre-code` instala e mantém a `/security-auditor` atualizada sempre (compatibilidade de versão e princípios). |
| Fundação do app (primeiro setup) | ✅ Sim | Acionada automaticamente para revisar PRD, ARQUITETURA e NIVEIS-DE-ACESSO. |
| Antes de deploy em produção | ⚠️ Recomendado / opt-in | O usuário pode CHAMAR explicitamente. Sem auditoria, o deploy só prossegue se todos os princípios acima estiverem verificados. |
| Antes de merge em `main` ou PR de release | ⚠️ Recomendado / opt-in | O usuário pode CHAMAR explicitamente. |
| Após adicionar qualquer integração | ⚠️ Recomendado / opt-in | O usuário pode CHAMAR explicitamente. |
| Após rotacionar/trocar secrets ou env vars | ⚠️ Recomendado / opt-in | O usuário pode CHAMAR explicitamente. |
| Após migrations/RLS ou troca de projeto Supabase | ⚠️ Recomendado / opt-in | O usuário pode CHAMAR explicitamente. |
| Quando solicitado pelo usuário | ✅ Sim | Sempre que o usuário pedir "auditar segurança", "verificar segurança", etc. |

> Toda diretriz, checklist e política de segurança detalhada do projeto vive dentro da skill `/security-auditor`. A IA não deve tentar replicar ou substituir essas instruções quando a skill estiver ativa; quando não estiver sendo executada, aplica os princípios acima como linha de base.
