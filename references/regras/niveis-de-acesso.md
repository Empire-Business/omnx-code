# 🛂 Níveis de Acesso — Perfis de Permissão por Tenant (BLOQUEIA COMMIT E DEPLOY)

**Nenhum código de autenticação/autorização pode ser commitado, e nenhum deploy pode acontecer, sem `docs/NIVEIS-DE-ACESSO.md` existir e estar completo.** Vale mesmo em projeto de um tenant só: se há qualquer distinção de permissão entre usuários, o documento é obrigatório. É gate, não boa prática opcional.

---

## 1. O modelo obrigatório: PERMISSÕES em catálogo, PERFIS por tenant

**Todo sistema criado por esta skill nasce com perfis de acesso personalizáveis pelo tenant — nunca com papéis fixos gravados nas policies.**

A razão é a mesma do multi-tenant: nascer assim custa quase nada, e converter depois é caro. Com papéis fixos, **cada ajuste de permissão vira uma migration** — e o cliente não consegue ajustar nada sozinho. Num projeto real da OMNX isso apareceu do pior jeito possível: duas migrations no mesmo dia só para destravar um único usuário que precisava criar e publicar um formulário. Papel fixo não descreve a operação de nenhuma empresa por muito tempo.

### As três peças

| Peça | O que é | Escopo |
|---|---|---|
| **Permissão** | Uma ação nomeada (`forms.publish`, `org.delete`) com rótulo e descrição em português — o texto que o cliente lê na caixinha | **Global** (mesma lista para todos os tenants) |
| **Perfil de acesso** | Um conjunto de permissões com nome, criado pelo tenant: "Editor", "Comercial", "Financeiro" | **Por tenant** |
| **Atribuição** | Quais perfis cada pessoa tem — N por pessoa, permissão efetiva é a **união** | Por membro |

Schema mínimo (adapte nomes ao domínio):

```sql
permission_catalog(key PK, resource, label, description, is_dangerous, sort_order)
tenant_access_profiles(id PK, tenant_id FK, name, description, system_key)
tenant_access_profile_permissions(profile_id FK, permission_key FK)   -- PK composta
tenant_member_profiles(member_id FK, profile_id FK)                    -- PK composta
```

### A única função de autorização

Toda policy RLS e toda RPC checa `has_permission(tenant_id, 'recurso.acao')`. **Nunca** `role = 'admin'`, nunca lista de papéis numa policy. Um segundo helper (`my_permissions(tenant_id)`) alimenta a UI.

---

## 2. As cinco travas anti-tiro-no-pé (INEGOCIÁVEIS)

Dar ao cliente o poder de montar perfis cria o risco de ele se trancar para fora ou de alguém se auto-promover. Estas cinco travas eliminam os dois riscos **por construção**, não por validação de formulário:

1. **O perfil de dono concede tudo IMPLICITAMENTE.** `has_permission` devolve `true` para quem o tem sem consultar lista nenhuma. Não existe caixinha para desmarcar — é isto que torna o lockout impossível.
2. **O perfil de dono é imutável e indestrutível** (trigger no banco, não só na RPC).
3. **O tenant nunca fica sem dono** — trigger aborta a remoção do último.
4. **Ninguém concede o que não tem — em DUAS portas.** A RPC de criar/editar perfil recusa permissão que quem edita não possui, **e** a RPC de atribuir perfil recusa entregar um perfil que conceda além do que quem atribui tem. Cobrir só a primeira porta é o erro fácil de cometer: bastaria dar a si mesmo um perfil poderoso que já existe (criado legitimamente pelo dono) para escalar privilégio sem criar nada.
5. **Só quem já é dono cria outro dono.**

Escrita nas tabelas de perfil é **fail-closed**: policy apenas de `select`; toda mutação passa por RPC `security definer` que aplica as travas acima + a exigência de 2FA do tenant, e registra em `audit_logs`.

---

## 3. O que `docs/NIVEIS-DE-ACESSO.md` precisa ter

1. **O modelo** — as três peças acima e onde cada uma vive no schema deste projeto
2. **As cinco travas** — e onde cada uma é aplicada (trigger, RPC, UI)
3. **Catálogo de permissões** — toda chave, com o rótulo e a descrição em português que o cliente lê
4. **O que cada perfil PADRÃO concede** — matriz perfil × recurso × ação. Nenhuma célula em branco ou "a definir": se não foi decidido, decida com o usuário antes de codar
5. **Telas/rotas por permissão** — o que cada tela exige para aparecer no menu e para carregar
6. **Atores que não são perfis** — super admin (claim no JWT, nunca na tabela de membros) e visitante anônimo (autorizado por sessão/recurso público, nunca por perfil)
7. **Casos especiais** — perda de acesso a um tenant, pessoa com múltiplos perfis, permissão que a RLS não consegue expressar (ver §5)

---

## 4. Como adicionar uma permissão (tudo no MESMO commit)

1. **Migration:** linha no `permission_catalog` (com rótulo e descrição leigos) + conceder aos perfis padrão que devem tê-la — **inclusive no trigger que semeia tenant novo**, senão clientes criados depois nascem sem ela
2. **Constante de permissões no TypeScript** (espelho do catálogo)
3. **Método no hook de permissão da UI**
4. **Linha em `docs/NIVEIS-DE-ACESSO.md`**
5. **Teste anti-drift** comparando as chaves do TypeScript com as semeadas na migration

---

## 5. Quando a RLS não dá conta

RLS do Postgres **não distingue coluna**: uma policy de `update` numa tabela governa todas as colunas dela. Se duas permissões diferentes precisam mexer em colunas diferentes da mesma linha (ex: "publicar" vs "arquivar"), **não afrouxe a policy** — crie uma RPC `security definer` que checa `has_permission` dentro e executa só as escritas daquela ação. Afrouxar a policy concede junto tudo que ela protege.

---

## 6. Convertendo um projeto que já tem papéis fixos

Se a IA encontrar um projeto existente com papéis fixos nas policies, ela deve **alertar o usuário** e propor a conversão — não fazer sozinha. Quando autorizada, a regra que torna a conversão segura é:

> **A migration prova a si mesma.** Dentro da mesma transação, compare o resultado do modelo novo com o do modelo antigo para **todo membro real × toda permissão do catálogo**. Uma única divergência → `raise exception`, e a transação inteira desfaz. Prove também que sobraram **zero** policies checando papel.

Sem essa prova, a conversão é um salto no escuro sobre dados de produção. Com ela, é verificável.

Cubra os dois buracos do corte, senão o sistema quebra em silêncio para clientes novos:
- **tenant novo** precisa nascer com os perfis padrão (trigger de seed)
- **convite novo** precisa entrar com perfil (converta o fluxo de convite, ou espelhe papel → perfil por trigger enquanto a conversão não termina)

O helper antigo (`has_org_role` ou equivalente) pode sobreviver durante a transição, mas **redefinido para ler o modelo de perfis**. Deixá-lo lendo a tabela de papéis cria duas fontes de verdade — o que esta skill trata como bug, não como pendência.

---

## 7. Regra de atualização

Sempre que uma permissão nova nasce ou uma existente muda de dono, `docs/NIVEIS-DE-ACESSO.md` é atualizado **no mesmo commit** que muda o código — nunca depois, nunca "documento no final". Permissão que existe no código sem entrada no documento é bug, não pendência.
