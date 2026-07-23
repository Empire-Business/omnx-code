# 🧩 Arquitetura de Apps & Loja de Apps Interna (INEGOCIÁVEL)

**Todo sistema deste projeto nasce modular por padrão:** nenhuma funcionalidade é código solto sempre ativo. Cada função (ou conjunto coeso de funções) do produto é modelada como um **app**, listado num catálogo, e o tenant escolhe quais apps quer usar numa **Loja de Apps interna**. Isso vale mesmo se hoje o produto parecer ter "uma função só" — nesse caso ele nasce como um único app dentro da loja, não como código sem fronteira. Decompor em apps desde o início é barato; fatiar um monólito depois que já existe código e dados em produção é caro e cheio de acoplamento escondido.

> ⚠️ **Exceção:** só pule esse modelo se o usuário confirmar explicitamente que o projeto é uma ferramenta de uso único sem intenção de crescer (ex: script interno, protótipo descartável) — e mesmo assim, documente a decisão em `docs/ARQUITETURA.md`.

## Modelo obrigatório

| Peça | O que é | Exemplo de nome |
|------|---------|------------------|
| **Catálogo de apps** | Tabela global (não por tenant) com todo app disponível no sistema | `apps` |
| **Instalação por tenant** | Liga `tenants` a `apps` com estado ativo/inativo — o mesmo padrão de membership, mas para funcionalidades | `tenant_apps` |
| **App core** | App essencial que não pode ser desativado (ex: configurações da conta) | flag `is_core` em `apps` |
| **Dependência entre apps** | Um app pode exigir outro ativo para funcionar | tabela/coluna de dependência em `apps` |

## Regras

- A tabela de catálogo de apps e a de instalação por tenant entram **junto** com a tabela de tenants e membership, na primeira migration — antes de qualquer tabela de negócio específica de um app.
- Todo requisito funcional do PRD é atribuído a um app específico desde a etapa de PRD (seção "Apps do produto") — não existe funcionalidade "solta" sem app dono.
- Toda rota, componente de UI e endpoint/RPC de um app não-core verifica se aquele app está ativo (`enabled`) para o tenant atual antes de renderizar ou executar. Isso vale no frontend (esconder menu/rota) **e** no backend (RLS/policy ou checagem na function) — nunca confie só na UI escondida para bloquear acesso a um app desativado.
- Desativar um app **oculta e bloqueia acesso, nunca apaga dados** — reativar deve trazer tudo de volta como estava.
- O produto tem uma tela de **Loja de Apps** onde o admin do tenant vê o catálogo completo, o que já está ativo, e ativa/desativa cada app com efeito imediato (sem deploy).
- A matriz de apps do catálogo (nome, descrição, categoria, `is_core`, dependências) fica documentada em `docs/ARQUITETURA.md`, seção "Arquitetura de Apps & Loja de Apps".
