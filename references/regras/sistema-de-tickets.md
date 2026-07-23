# 🎫 Sistema de Tickets de Erro — Obrigatório (BLOQUEIA DEPLOY)

**Todo sistema com interface visível ao usuário final precisa ter um sistema de tickets de erro antes de ir para produção.** Não é opcional e não é "adicionar depois se der tempo": é o mesmo tipo de gate que segurança e níveis de acesso. Não se aplica a scripts internos ou jobs sem UI.

A ideia por trás disso é simples: um erro que o usuário não consegue reportar facilmente é um erro que nunca chega até quem pode corrigir. E um erro reportado sem contexto técnico (print, log, rota, navegador) vira uma investigação de "me manda mais detalhes" que atrasa a correção em dias. O objetivo é fechar essa distância: **do clique do usuário até a fila de correção, sem fricção e sem depender de descrição manual.**

## O que precisa existir

1. **Botão/atalho de "Reportar problema" visível em qualquer tela** — não escondido em um menu de configurações. Padrão recomendado: botão flutuante discreto (canto inferior) ou item fixo no menu principal, disponível em toda a aplicação autenticada.
2. **Captura automática ao acionar o report** (o usuário só descreve o que estava tentando fazer, opcionalmente — nunca precisa colar log ou tirar print manualmente):
   - Print de tela da tela atual no momento do report
   - Logs do console / stack trace do erro (se houver um erro JS associado)
   - Rota/URL atual e a ação que estava sendo executada
   - Timestamp, navegador, sistema operacional, resolução de tela
   - Id do usuário e do tenant (quando aplicável), sem expor dados sensíveis de outros usuários
3. **Captura automática também em erro não tratado** — um error boundary do React (para erros de render) e um handler global (`window.onerror` + `unhandledrejection`, para erros fora do ciclo de render) disparam a mesma captura sem exigir que o usuário clique em nada. O usuário vê uma tela amigável de erro ("algo deu errado, já avisamos o time") e o ticket é criado em segundo plano.
4. **Fila interna organizada por status** — os tickets caem numa área que o time de correção acompanha, com status mínimo: `novo → em análise → em correção → resolvido`. Pode ser uma tabela própria no Supabase com um painel simples (`/admin/tickets` ou equivalente, protegido por papel — ver `docs/regras/niveis-de-acesso.md`) ou uma integração que envia o ticket para o sistema de suporte que o time já usa (ex: webhook para Linear/Slack/email). O importante é que nenhum ticket fica perdido em log que ninguém olha.

## Estrutura mínima de dados (se usar tabela própria no Supabase)

```sql
-- exemplo de shape mínimo — adapte nomes ao padrão do projeto
create table public.error_tickets (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references public.tenants(id),
  user_id uuid references auth.users(id),
  status text not null default 'novo' check (status in ('novo','em_analise','em_correcao','resolvido')),
  description text,           -- o que o usuário disse que estava fazendo (opcional)
  error_message text,         -- mensagem/stack trace, se houver
  route text,                 -- rota onde ocorreu
  screenshot_url text,        -- print enviado ao Storage
  browser_info jsonb,         -- navegador, SO, resolução
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);
```

Como toda tabela nova, entra em migration versionada (ver `docs/regras/migrations.md`) e tem RLS ativo: o usuário só cria tickets (não lê tickets de outros); a leitura/atualização de status fica restrita ao papel responsável pela correção, seguindo a matriz em `docs/NIVEIS-DE-ACESSO.md`.

## Regra de atualização

`docs/SISTEMA-DE-TICKETS.md` documenta: como o usuário reporta, o que é capturado automaticamente, onde a fila vive (tabela + painel, ou integração externa), os status do fluxo e quem é notificado em cada mudança. Esse documento é criado **antes do primeiro deploy** e atualizado sempre que o fluxo de captura ou a fila mudar — mesmo princípio já aplicado a UML (migrations) e Níveis de Acesso: o que descreve o comportamento não pode ficar defasado em relação ao código.
