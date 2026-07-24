# 📋 Checklist de Entrega

A IA deve verificar cada item antes de considerar qualquer tarefa concluída:

**Documentação**
- [ ] PRD.md existe e foi aprovado pelo usuário?
- [ ] ROADMAP.md existe e está atualizado?
- [ ] MUDANCAS.md foi atualizado com a descrição da entrega?

**Código**
- [ ] O código compila sem erros TypeScript?
- [ ] Nenhum `any` foi usado sem justificativa documentada?
- [ ] Nenhuma chave, segredo ou dado sensível está exposto no código?
- [ ] `.env` está no `.gitignore` e **não foi commitado**?

**Modelagem (UML)** — ver `docs/regras/uml.md`
- [ ] **`docs/UML.md` existe, com diagrama de classes/entidades e sequência dos fluxos críticos, ANTES de qualquer código de domínio ter sido escrito?** Em projeto existente sem UML, ele foi gerado por engenharia reversa e validado pelo usuário antes deste commit? Sem isso, o commit está BLOQUEADO (gate 1.6c).
- [ ] **`docs/UML.html` foi gerado junto com `docs/UML.md` no mesmo commit?** O HTML renderiza todos os diagramas visualmente com abas navegáveis e abre em qualquer navegador sem servidor.
- [ ] Toda entidade/relacionamento/fluxo crítico alterado nesta entrega está refletido no `docs/UML.md` e `docs/UML.html`, no mesmo commit?

**Arquitetura de Usuários & Multi-Tenant** — ver `docs/regras/multi-tenant.md`
- [ ] **`docs/NIVEIS-DE-ACESSO.md` existe e cobre todos os papéis do sistema, sem células em branco na matriz?** Sem esse documento completo, o commit de código de auth/permissão e o deploy estão BLOQUEADOS (gate 1.6b — anti-teatro: um papel no código sem entrada no documento é bug).
- [ ] Toda tabela de negócio nova tem coluna `tenant_id` (FK not-null), exceto se o projeto foi explicitamente definido como single-tenant e isso está documentado em `docs/ARQUITETURA.md`?
- [ ] Toda política RLS de tabela com `tenant_id` filtra por tenant (não só por `auth.uid()`)?

**Arquitetura de Apps & Loja de Apps** — ver `docs/regras/apps-loja-de-apps.md`
- [ ] Todo requisito funcional novo do PRD está atribuído a um app do catálogo (`docs/ARQUITETURA.md`, seção "Arquitetura de Apps & Loja de Apps")?
- [ ] A tabela de catálogo de apps e a de instalação por tenant (`tenant_apps` ou equivalente) existem desde a primeira migration, junto com tenants/membership?
- [ ] Toda rota, componente e endpoint/RPC de um app não-core verifica se o app está ativo para o tenant atual, tanto no frontend quanto no backend (RLS/policy)?
- [ ] Desativar um app oculta e bloqueia acesso sem apagar dados?
- [ ] A tela de Loja de Apps existe, lista o catálogo completo e permite ativar/desativar cada app com efeito imediato — exceto se o projeto foi explicitamente definido como app único (documentado em `docs/ARQUITETURA.md`)?

**API & Webhooks por App** — ver `docs/regras/api-webhooks-por-app.md` (só se o app tiver integração externa)
- [ ] `docs/apps/<app-slug>/API.md` existe (se o app expõe endpoints), com autenticação, endpoints, exemplos `curl` e códigos de erro?
- [ ] `docs/apps/<app-slug>/WEBHOOKS.md` existe (se o app recebe/dispara webhooks), com seções "recebidos" e "disparados" separadas, payloads reais e política de retry?
- [ ] Existe tela de "Integrações" dentro do app com geração/rotação de chave, cadastro de webhook, botão de teste e histórico de entregas?
- [ ] Chaves/secrets são gerados pelo sistema (nunca digitados pelo tenant) e armazenados como hash, nunca em texto plano?
- [ ] Apenas papel administrativo consegue gerenciar chaves/webhooks (conferido contra `docs/NIVEIS-DE-ACESSO.md`)?
- [ ] Desativar o app na Loja de Apps derruba imediatamente as chaves/webhooks daquele app?

**Sistema de Tickets de Erro** — ver `docs/regras/sistema-de-tickets.md`
- [ ] **Existe um botão/atalho de "Reportar problema" visível em qualquer tela da aplicação?** Sem isso, o deploy está BLOQUEADO (gate 1.6d).
- [ ] **Existe um interceptor de `console.log/warn/error/info` e de `fetch`/XHR rodando desde o boot do app**, mantendo ring buffer em memória (não é implementado "sob demanda" ao clicar no botão — se for, os logs anteriores ao clique já se perderam)?
- [ ] **A captura de tela é real** (via `html2canvas` ou equivalente, gerando uma imagem de verdade do DOM) **e anexada automaticamente por padrão** ao abrir o report — não um checkbox que o usuário precisa lembrar de marcar?
- [ ] A mesma captura (print + logs + rede + contexto) funciona tanto pelo botão de reportar quanto por um error boundary/handler global de erro não tratado, sem exigir clique do usuário?
- [ ] **Verificação anti-teatro feita:** um erro de teste foi forçado, o ticket gerado foi aberto, e `screenshot_url` mostra uma imagem real, `console_logs` tem entradas anteriores ao erro, e `network_logs` reflete requisições reais — nenhum desses três campos está vazio, nulo ou com placeholder?
- [ ] Os tickets caem numa fila interna organizada por status (`novo → em análise → em correção → resolvido`), seja tabela própria com painel ou integração com o sistema de suporte do time?
- [ ] **`docs/SISTEMA-DE-TICKETS.md` existe e documenta o fluxo completo (como reportar, o que é capturado, onde a fila vive, status, quem é notificado)?** Sem esse documento, o deploy está BLOQUEADO (gate 1.6d).

**Banco de Dados** — ver `docs/regras/migrations.md` e `docs/regras/acesso-supabase.md`
- [ ] RLS está ativo em todas as tabelas afetadas?
- [ ] Nenhuma `service_role_key` está no `.env` ou no código?
- [ ] Token do Supabase é temporário e está dentro do prazo de 7 dias?
- [ ] Toda mudança de banco está em uma migration versionada em `supabase/migrations/`?
- [ ] Nenhum SQL direto (SQL Editor, `supabase db execute`, `psql`, RPC de SQL) foi usado para alterar o banco?
- [ ] Tipos TypeScript regenerados após as migrations?

**Segurança** — ver `docs/regras/seguranca.md`
- [ ] Skill `/security-auditor` foi executada nesta entrega?
- [ ] **`security-report/verdict.json` desta sessão existe com `"gate": "PASS"`?** Sem o artefato, ou com `gate != PASS`, o deploy está BLOQUEADO — P0/P1 em aberto (inclui `❔ não verificado`/`⚠️ ação manual`) derrubam o gate. Marcar este item sem o `verdict.json` é inválido (anti-teatro). A auditoria é report-only; auto-fix é opt-in.
- [ ] Headers de segurança estão configurados no `vercel.json`?
- [ ] Rate limiting está ativo nas rotas novas?

**Deploy** — ver `docs/regras/deploy.md`
- [ ] `vercel.json` existe com todos os headers de segurança?
- [ ] Todas as variáveis de ambiente estão no painel do Vercel (não no código)?
- [ ] HTTPS ativo e funcionando (cadeado verde)?
- [ ] Vercel Analytics ativo?
- [ ] A IA explicou ao usuário como verificar o deploy no painel do Vercel?

**Testes** — ver `docs/regras/testes.md`
- [ ] Testes unitários cobrem hooks, utilitários, schemas Zod e lógica de negócio?
- [ ] Testes de integração cobrem chamadas ao Supabase, auth e autorização?
- [ ] Testes E2E cobrem os fluxos críticos do usuário?
- [ ] Nenhum teste existente foi quebrado?
