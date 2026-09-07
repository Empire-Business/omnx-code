# OMNX Console — validação da 2.1.0-rc.1

## Implementado
- Console local bundled no mesmo pacote da `omnx-code`.
- Catálogo local de projetos em pastas diferentes, sem mover repositórios.
- Dashboard de portfólio e comparação SemVer da versão OMNX adotada.
- Kanban derivado das Tasks canônicas.
- Galeria de imagens e HTML em `docs/ux/proposals/`.
- Decision Store com CAS, autoridade explícita e proteção contra aprovação de subject alterado.
- Prompt determinístico para retomar Task no Claude Code/Codex.
- API local em loopback com token efêmero e Origin check para mutações.
- HTML de mockup servido com CSP sandbox e scripts desabilitados.
- Launcher opt-in: bundle `.app` candidato no macOS, `.cmd` fallback no Windows e `.desktop` no Linux.

## Testado nesta entrega
- Linux / Python local.
- Suíte determinística completa da OMNX, incluindo testes do Console.
- Catálogo com projetos em diretórios distintos.
- Stale approval/CAS de Decision.
- Aprovação não altera Task nem autoriza produção.
- Descoberta de mockup e rejeição de symlink externo.
- API sem token rejeitada.
- POST com Origin externo rejeitado.
- Prompt determinístico sem autorização implícita de deploy.

## Não testado / não alegado
- Claude Code real e Codex real nesta sessão.
- Launcher clicável em macOS/Windows reais, assinatura/notarização ou instalador nativo.
- Browser matrix Safari/Chrome/Edge em sistemas reais.
- Aplicações reais do usuário ou projetos de produção.
- Benchmark real de tokens: o Console não chama modelo, mas o custo das sessões Claude/Codex depende do prompt e do projeto.

O Console é opcional. Se ele estiver indisponível, as skills e as fontes canônicas continuam funcionando sem ele.
