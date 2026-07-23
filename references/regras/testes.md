# 🧪 Padrão de Testes

- **Vitest** — testes unitários: hooks, utilitários, schemas Zod, lógica de negócio
- **Integração** — chamadas ao Supabase, autenticação, autorização
- **Playwright** — fluxos críticos do usuário no navegador real
- Credenciais de teste ficam no `.env` sob `TEST_USER_EMAIL` e `TEST_USER_PASSWORD`
- Nenhuma entrega pode quebrar testes existentes
