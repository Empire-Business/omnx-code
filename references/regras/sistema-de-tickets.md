# 🎫 Sistema de Tickets de Erro — Obrigatório (BLOQUEIA DEPLOY)

**Todo sistema com interface visível ao usuário final precisa ter um sistema de tickets de erro antes de ir para produção.** Não é opcional e não é "adicionar depois se der tempo": é o mesmo tipo de gate que segurança e níveis de acesso. Não se aplica a scripts internos ou jobs sem UI.

A ideia por trás disso é simples: um erro que o usuário não consegue reportar facilmente é um erro que nunca chega até quem pode corrigir. E um erro reportado sem contexto técnico (print, log, rota, navegador) vira uma investigação de "me manda mais detalhes" que atrasa a correção em dias. O objetivo é fechar essa distância: **do clique do usuário até a fila de correção, sem fricção e sem depender de descrição manual.**

> ⚠️ **Onde as implementações costumam sair pobres (e por que isso não passa mais no gate):** é fácil escrever um botão "Reportar problema" que abre um formulário de texto livre e chamar isso de "sistema de tickets" — mas isso não captura nada automaticamente, é só um formulário de contato com nome chique. Da mesma forma, é fácil prometer "logs do console" sem implementar nenhuma captura real — o JavaScript **não tem acesso retroativo** ao que já foi impresso no console antes do erro acontecer; sem um interceptor rodando desde o boot do app, "logs do console" no ticket vem **vazio**, o que é pior que não prometer nada. As seções abaixo existem para fechar exatamente essas duas lacunas: log tem que vir de um buffer real, e print tem que ser gerado de verdade, não simulado.

## O que precisa existir

1. **Botão/atalho de "Reportar problema" visível em qualquer tela** — não escondido em um menu de configurações. Padrão recomendado: botão flutuante discreto (canto inferior) ou item fixo no menu principal, disponível em toda a aplicação autenticada.

2. **Interceptor de logs rodando desde o boot do app (obrigatório, não é detalhe de implementação — é o que faz "logs" ser real em vez de promessa vazia)**
   - Logo na inicialização (antes de qualquer outra coisa renderizar), sobrescreva `console.log`, `console.warn`, `console.error` e `console.info` para, além do comportamento normal, empurrar cada chamada (timestamp, nível, argumentos serializados) para um **ring buffer em memória** com as últimas ~100-150 entradas (descarta as mais antigas conforme novas chegam — não deixa crescer sem limite).
   - Da mesma forma, intercepte `fetch` (e `XMLHttpRequest`, se usado) para manter um ring buffer separado das últimas ~30-50 requisições de rede: método, URL, status HTTP, duração. Isso é o que permite diagnosticar "a tela travou porque a API X retornou 500" sem pedir pro usuário abrir o DevTools.
   - No momento do report (manual ou automático), o conteúdo **atual** desses dois buffers é serializado e vai junto com o ticket. Sem o interceptor, não existe conteúdo para serializar — por isso ele precisa estar ativo desde o boot, não só ser criado "quando o botão for clicado".

3. **Captura de tela real do estado atual da UI, anexada automaticamente por padrão** — não é um checkbox que o usuário precisa lembrar de marcar; o print já vem pronto quando o modal de report abre, e o usuário pode removê-lo antes de enviar se quiser (ex: dado sensível na tela).
   - Implementação recomendada: biblioteca de screenshot de DOM (ex: `html2canvas` ou equivalente) capturando o `<body>` (ou o container principal da aplicação) no momento do clique/erro, gerando um `blob`/`dataURL` que é enviado ao Storage do Supabase (bucket dedicado, ex: `error-screenshots`, não público) e referenciado por `screenshot_url` no ticket.
   - Não use a Screen Capture API do navegador (`getDisplayMedia`) como mecanismo principal: ela exige que o usuário conceda permissão de compartilhamento de tela a cada uso, o que quebra o objetivo de ser automático. Reserve-a, se quiser, como opção manual extra ("compartilhar minha tela toda" para casos raros) — nunca como o único caminho.
   - No modal de report, mostre uma **prévia visível da imagem capturada** antes de enviar — isso é o que prova pro usuário (e pra quem for validar o gate depois) que a captura realmente aconteceu, em vez de ser um campo vazio no banco.

4. **Captura automática também em erro não tratado** — um error boundary do React (para erros de render) e um handler global (`window.onerror` + `unhandledrejection`, para erros fora do ciclo de render) disparam a mesma captura (print + buffers de log/rede + contexto) sem exigir que o usuário clique em nada. O usuário vê uma tela amigável de erro ("algo deu errado, já avisamos o time") e o ticket é criado em segundo plano, usando os mesmos ring buffers e a mesma função de screenshot do item 2 e 3 — não uma implementação paralela mais fraca "só pra esse caso".

5. **Contexto adicional em todo ticket** — rota/URL atual e a ação que estava sendo executada (quando identificável), timestamp, navegador, sistema operacional, resolução de tela, id do usuário e do tenant (quando aplicável, sem expor dados sensíveis de outros usuários).

6. **Fila interna organizada por status** — os tickets caem numa área que o time de correção acompanha, com status mínimo: `novo → em análise → em correção → resolvido`. Pode ser uma tabela própria no Supabase com um painel simples (`/admin/tickets` ou equivalente, protegido por papel — ver `docs/regras/niveis-de-acesso.md`) ou uma integração que envia o ticket para o sistema de suporte que o time já usa (ex: webhook para Linear/Slack/email). O importante é que nenhum ticket fica perdido em log que ninguém olha.

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
  screenshot_url text,        -- print gerado via html2canvas (ou equivalente) e enviado ao Storage — nunca nulo em report manual
  console_logs jsonb,         -- ring buffer de console.log/warn/error/info no momento do report (últimas ~100-150 entradas)
  network_logs jsonb,         -- ring buffer de fetch/XHR no momento do report (últimas ~30-50 requisições: método, URL, status, duração)
  browser_info jsonb,         -- navegador, SO, resolução
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);
```

Como toda tabela nova, entra em migration versionada (ver `docs/regras/migrations.md`) e tem RLS ativo: o usuário só cria tickets (não lê tickets de outros); a leitura/atualização de status fica restrita ao papel responsável pela correção, seguindo a matriz em `docs/NIVEIS-DE-ACESSO.md`.

## Verificação anti-teatro (fazer antes de marcar este gate como cumprido)

Não basta o código existir — teste que a captura funciona de verdade:

1. Force um erro de propósito (ex: um botão de teste que lança uma exceção, removido antes do deploy final ou escondido atrás de uma flag de dev).
2. Abra o ticket criado (no painel ou direto na tabela) e confirme, olhando os dados reais:
   - `screenshot_url` aponta para uma imagem que **abre e mostra a tela real** no momento do erro — não um placeholder, não uma imagem em branco.
   - `console_logs` tem entradas **anteriores** ao erro (prova que o ring buffer estava rodando desde antes, não só capturando o próprio erro).
   - `network_logs` reflete requisições reais feitas pela aplicação.
3. Se qualquer um desses três campos estiver vazio, nulo ou com dado falso/placeholder, o sistema de tickets **não está pronto** — corrija antes de considerar o gate cumprido, mesmo que o botão e a tabela existam.

## Regra de atualização

`docs/SISTEMA-DE-TICKETS.md` documenta: como o usuário reporta, o que é capturado automaticamente (print real via screenshot de DOM, ring buffer de console, ring buffer de rede), onde a fila vive (tabela + painel, ou integração externa), os status do fluxo e quem é notificado em cada mudança. Esse documento é criado **antes do primeiro deploy** e atualizado sempre que o fluxo de captura ou a fila mudar — mesmo princípio já aplicado a UML (migrations) e Níveis de Acesso: o que descreve o comportamento não pode ficar defasado em relação ao código.
