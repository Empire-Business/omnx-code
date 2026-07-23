# 📐 UML — Modelagem Obrigatória (BLOQUEIA CÓDIGO E COMMIT)

**Nenhuma linha de código de domínio é escrita antes de existir um UML mínimo em `docs/UML.md`.** Código sem modelo prévio é como construir sem planta: funciona até duas partes do sistema terem sido pensadas de formas incompatíveis, e aí já existe código dos dois lados para desfazer.

Formato: **Mermaid** dentro do markdown (`classDiagram`, `sequenceDiagram`, `stateDiagram-v2`) — versionável no git, renderiza direto no GitHub, sem depender de ferramenta externa.

**Versão visual:** sempre que `docs/UML.md` for criado ou atualizado, a IA também gera `docs/UML.html` — uma página HTML autocontida com todos os diagramas renderizados visualmente em abas navegáveis (tema dark, interativo). Ambos entram no mesmo commit. O HTML abre em qualquer navegador, sem servidor.

## O que `docs/UML.md` precisa ter

1. **Diagrama de classes/entidades** — entidades principais do domínio, atributos essenciais, relacionamentos. Inclui a arquitetura de usuários/multi-tenant (tenant, membership, papéis) e a arquitetura de apps (`App` do catálogo, `TenantApp` de instalação por tenant — ver `docs/regras/multi-tenant.md` e `docs/regras/apps-loja-de-apps.md`)
2. **Diagrama(s) de sequência** dos 2-3 fluxos mais críticos (ex: cadastro/login, a ação principal do produto, checkout/pagamento se houver)
3. **Diagrama de estados** (opcional, recomendado quando há entidade com ciclo de vida relevante — pedido, assinatura, workflow de aprovação)

## Regra para projeto novo

O UML é criado na FASE 0 do projeto, junto com `ARQUITETURA.md`, e **aprovado pelo usuário antes do primeiro código de domínio** (models, entidades, schema de banco).

## Regra para projeto existente sem UML (retroativo)

Se este projeto já tem código mas ainda não tem `docs/UML.md`, **nenhum commit novo pode ser feito até o UML existir**, mesmo que a mudança pedida seja pequena — falta de UML é dívida técnica bloqueante, igual dívida de segurança. Nesse caso:
1. O UML é gerado por engenharia reversa a partir do schema e código **reais** — nunca inventado
2. O usuário valida o diagrama gerado (código legado pode ter entidades que já não fazem sentido)
3. Só depois disso o commit pedido acontece

## Manutenção

Toda vez que uma entidade, relacionamento ou fluxo crítico muda, `docs/UML.md` e `docs/UML.html` são atualizados no **mesmo commit** que muda o código — nunca depois. Toda migration nova (tabela, coluna, função/RPC, trigger, policy) é gatilho obrigatório de atualização do UML. Antes de concluir qualquer tarefa com migration, compare o timestamp da migration mais recente com o campo `Atualizado em` do UML: se estiver atrás, a tarefa não está concluída. Uma mudança de schema/domínio commitada sem os arquivos UML correspondentes é tratada como bug, não como pendência.
