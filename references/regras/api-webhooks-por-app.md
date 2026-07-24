# 🔌 API & Webhooks por App (documentação completa + gerenciamento seguro)

> Complementa `docs/regras/apps-loja-de-apps.md`. Todo app do catálogo (regra 24) que expõe uma API própria e/ou consome/dispara webhooks é, na prática, uma interface pública — mesmo que hoje só um sistema converse com ela. O custo de documentar e dar uma tela de gerenciamento no momento em que a integração nasce é uma fração do custo de reconstruir esse conhecimento depois, quando ninguém mais lembra o formato do payload.

## Quando esta regra se aplica

Sempre que um app do catálogo (ver `docs/regras/apps-loja-de-apps.md`) tiver, ou passar a ter, qualquer um destes:
- Uma API própria exposta para sistemas externos chamarem (ex: `POST /api/apps/<app-slug>/...`)
- Um endpoint de webhook que **recebe** eventos de um sistema de terceiros (ex: Stripe, WhatsApp, GHL)
- Um disparo de webhook que o app **envia** para uma URL configurada pelo tenant quando algo acontece (ex: "pedido criado" → notifica o CRM do cliente)

Se o app não tem nenhuma integração externa, esta regra não se aplica a ele — não force documentação de API/webhook em um app que não tem nenhuma.

## 1. Documentação — uma pasta por app, sempre no mesmo padrão

Cada app com integração ganha sua própria pasta em `docs/apps/<app-slug>/`, nunca um arquivo genérico misturando todos os apps — isso é o que permite ao tenant (ou a outro time) abrir exatamente o que precisa sem ler documentação de apps que não usa.

```
docs/apps/<app-slug>/
├── API.md         # se o app expõe endpoints próprios
└── WEBHOOKS.md     # se o app recebe e/ou dispara webhooks
```

Ambos são referenciados em duas pontas — nunca só uma:
1. `docs/ARQUITETURA.md`, na seção "Arquitetura de Apps & Loja de Apps", na linha do app correspondente na matriz do catálogo
2. `docs/integracoes/README.md`, que continua sendo o índice geral de toda integração externa do projeto (regra já existente — este arquivo só passa a agrupar por app em vez de listar solto)

### `API.md` — o mínimo que precisa existir

- **Visão geral**: o que a API deste app faz, quem é o consumidor esperado (outro sistema do tenant, um parceiro, um app externo)
- **Base URL e padrão de rota** do app
- **Autenticação**: como o chamador se identifica (API key por tenant, Bearer token, OAuth) — nunca "autenticação simples" sem detalhar o mecanismo real
- **Rate limits conhecidos**, se houver
- **Por endpoint**: método HTTP, path, descrição, schema de request (campos, tipos, obrigatório/opcional), schema de response (sucesso e erro), pelo menos um exemplo `curl` funcional que qualquer pessoa consiga copiar, colar e rodar
- **Códigos de erro** que a API pode retornar e o que cada um significa

### `WEBHOOKS.md` — separado em duas seções, nunca misturadas

**Webhooks recebidos** (o app é quem recebe dados de fora):
- URL do endpoint, método HTTP
- Schema do payload esperado — exemplo de JSON real, não "um JSON com os dados"
- Campos obrigatórios vs. opcionais
- Autenticação esperada de quem envia (header de assinatura HMAC, secret compartilhado, IP allowlist)
- Código de resposta esperado em sucesso e em erro
- Comportamento em caso de payload malformado ou duplicado (idempotência)

**Webhooks disparados** (o app é quem envia dados para fora):
- Quais eventos disparam um webhook (ex: `pedido.criado`, `pagamento.aprovado`) e o schema do payload de cada evento
- Como o app assina o payload que envia (ex: header `X-Signature` com HMAC-SHA256 do body usando o secret do tenant), para quem recebe conseguir verificar autenticidade
- Política de retry: quantas tentativas, intervalo, timeout, e o que acontece se todas falharem (fila morta visível ao tenant, notificação, etc.)
- Onde o tenant vê o histórico de entregas (sucesso/falha, código de resposta, timestamp)

Toda mudança de contrato (novo campo obrigatório, mudança de formato) atualiza a documentação **no mesmo commit** que muda o código — mesmo princípio da regra de migrations: o que descreve o comportamento não pode ficar defasado em relação ao código.

## 2. Gerenciamento — tela dedicada dentro do próprio app, não um formulário solto

Cada app com integração ganha uma tela de **"Integrações"** (ou seção equivalente dentro das configurações do app), acessível de dentro do app na Loja de Apps — nunca uma tela genérica de "API keys do sistema todo" desconectada de qual app ela pertence. O objetivo é que o tenant configure sem precisar ler código nem abrir chat de suporte:

- **Chaves de API** (quando o app expõe endpoints): botão para gerar, tela mostra a chave completa **uma única vez** no momento da criação (nunca de novo depois — só uma versão mascarada tipo `sk_live_••••1a2b`), botão de revogar/rotacionar, e data da última utilização visível.
- **Webhooks configurados** (quando o app dispara eventos): formulário para cadastrar URL de destino, seleção de quais eventos aquele webhook escuta, secret gerado automaticamente pelo sistema (o tenant não digita o próprio secret), toggle ativo/inativo, e um botão de **"testar"** que dispara um payload de exemplo e mostra o resultado na hora.
- **Texto de apoio no próprio fluxo**: tooltip ou texto curto explicando o formato esperado, com link para o `API.md`/`WEBHOOKS.md` correspondente — a tela nunca é só um campo de texto vazio sem contexto.
- **Histórico de entregas** (webhooks recebidos e disparados): lista com status, timestamp e código de resposta, com opção de reenviar uma entrega que falhou.

## 3. Segurança — gerenciamento de credenciais nunca é opcional

Esta seção não substitui a auditoria da `/security-auditor` (que continua sendo a dona das regras detalhadas de segurança — ver `docs/regras/seguranca.md`); ela define o mínimo estrutural que qualquer API/webhook por app precisa ter antes de a `/security-auditor` sequer rodar em cima disso:

- **Chaves de API nunca ficam em texto plano no banco** — armazene hash (mesmo padrão de senha), nunca a chave original; a chave completa só existe no momento da geração, mostrada uma vez ao tenant.
- **Secrets de webhook são gerados pelo sistema**, nunca digitados pelo tenant — evita secret fraco ou reaproveitado de outro lugar.
- **Escopo por tenant, sempre**: uma chave de API ou um webhook criado por um tenant nunca é visível nem utilizável por outro — RLS/policy no mesmo padrão da regra de multi-tenant (`docs/regras/multi-tenant.md`).
- **Apenas papéis com permissão administrativa** (ver a matriz em `docs/NIVEIS-DE-ACESSO.md`, regra de níveis de acesso) podem criar, rotacionar ou revogar chaves e webhooks — nunca um papel comum.
- **Toda criação, rotação e revogação é auditada** — quem fez, quando, o quê (sem logar o valor da chave/secret em si).
- **Ativação segue a Loja de Apps**: se o tenant desativa o app na Loja de Apps (`docs/regras/apps-loja-de-apps.md`), as chaves de API e os webhooks daquele app param de funcionar imediatamente — nunca ficam "esquecidos" ativos com o app desligado. Reativar o app **não** gera chaves/secrets novos automaticamente; as credenciais existentes voltam a funcionar como estavam (mesmo princípio de "desativar oculta e bloqueia, nunca apaga" da regra de apps).

## Checklist rápido antes de considerar uma integração de app pronta

- [ ] `docs/apps/<app-slug>/API.md` existe (se o app expõe endpoints) com autenticação, endpoints, exemplos `curl` e códigos de erro?
- [ ] `docs/apps/<app-slug>/WEBHOOKS.md` existe (se o app recebe/dispara webhooks) com as seções "recebidos" e "disparados" separadas, schemas de payload reais e política de retry?
- [ ] Ambos referenciados em `docs/ARQUITETURA.md` (linha do app na matriz de apps) e em `docs/integracoes/README.md`?
- [ ] Existe tela de "Integrações" dentro do app, com geração/rotação de chave, cadastro de webhook, botão de teste e histórico de entregas?
- [ ] Chaves e secrets são gerados pelo sistema (nunca digitados pelo tenant) e armazenados como hash, nunca em texto plano?
- [ ] Apenas papel administrativo consegue gerenciar chaves/webhooks (verificado contra `docs/NIVEIS-DE-ACESSO.md`)?
- [ ] Desativar o app na Loja de Apps derruba imediatamente as chaves/webhooks daquele app?
