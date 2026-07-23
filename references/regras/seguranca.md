# 🔐 Segurança — Skill Obrigatória

**A IA DEVE executar a skill `/security-auditor` nos seguintes momentos, sem exceção, e só liberar com `security-report/verdict.json` em `"gate": "PASS"`:**

| Momento                                          | Obrigatório? |
|--------------------------------------------------|--------------|
| Início do projeto (antes de codar)               | ✅ Sim        |
| Antes de qualquer deploy em produção             | ✅ Sim        |
| Antes de merge em `main` ou PR de release        | ✅ Sim        |
| Após adicionar qualquer integração               | ✅ Sim        |
| Após rotacionar/trocar secrets ou env vars       | ✅ Sim        |
| Após migrations/RLS ou troca de projeto Supabase | ✅ Sim        |
| Quando solicitado pelo usuário                   | ✅ Sim        |

> Toda diretriz, checklist e política de segurança deste projeto vive dentro da skill `/security-auditor`. A IA não deve tentar replicar ou substituir essas instruções aqui.
