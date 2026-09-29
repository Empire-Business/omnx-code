# Changelog

## 2.2.0-rc.1 — Console 1.1.0-rc.1

- Hooks de projeto Codex/Claude opt-in registram início, atividade limitada, interrupção, encerramento e checkpoint sem copiar conversa, argumentos ou código.
- Sessões de implementação criam/reutilizam uma Task canônica idempotente, tentam abrir o Console uma vez e preservam sinais separados para tarefa, sessão e cliente local.
- PNG como referência padrão para novos mockups; comando de leitura de dimensões e perfil OMNX do image-to-html documentam precedência de PRD/rotas e adaptação responsiva.
- Política de release opt-in consulta Stable por padrão, filtra RC, valida compatibilidade e SHA-256 do GitHub, e prepara candidato lado a lado sem ativação no host.
- Política configurável de perfis determinístico/econômico/equilibrado/avançado registra modelo e esforço solicitados, sem alegar seleção, custo ou uso efetivo não observados.
- `console open` informa estados separados para servidor, navegador e conexão técnica; a UI mostra atividade recente, política de modelo e candidato preparado.
- Preservada compatibilidade do schema de projeto 1 e dos contratos do auditor 2.0; schemas novos cobrem sessões, modelos e updates.
- Limite conhecido: host não oferece forma uniforme de trocar a skill/modelo da sessão ativa ou apontar todas as próximas sessões para o candidato; ativação segue seleção explícita no caminho versionado.

## 2.1.0-rc.2 — Console 1.0.0-rc.2

- Corrige inicialização JavaScript, elimina handlers interpolados e restringe previews a capabilities registradas.
- Decision v2: criação apenas pendente, escolha explícita, manifestos, CAS de bytes únicos, histórico atômico e imutabilidade de aprovação.
- Decision v1 preservada como histórico não verificado, com reapresentação explícita; sem aprovação retroativa.
- Kanban inclui bloqueados/cancelados; erro isolado não remove tarefas válidas. Clones/worktrees mantêm entradas independentes.
- Prompts por referência, limitados e conscientes de intenção/autorização, sem copiar bodies ou credenciais.
- Indexação incremental, resumos, paginação, detalhes sob demanda e limites de leitura.
- Sessão com cookie/CSRF/expiração, CSP e isolamento; UI não aprova release/risco/O3.
- Open destacado/reutilizável, stop autenticado, instalação local nova e launchers com quoting e Python explícito.
- Recovery cobre interrupção antes do journal; rollback não apaga novas decisões/evidências; gate considera controles adicionais falhos.
- Regressões de engine, HTTP, processos, concorrência e DOM isolado. Limitações reais de host/navegador registradas em reports/VALIDATION.md.

## Histórico anterior

## 2.1.0-rc.1 — 2026-09-06

### Added
- OMNX Console local bundled: portfolio de projetos, Kanban, galeria de mockups, decisões e prompts determinísticos.
- Decision Store canônico em `.omnx/decisions/` com schema, CAS e autoridade explícita.
- `omnx console open/register/projects/unregister/shortcut`.
- Visualização de versões adotadas por projeto sem exigir que projetos estejam na mesma pasta.

### Safety / architecture
- Console não chama IA, não executa shell, não faz deploy e não possui banco de verdade próprio.
- Servidor restrito a loopback com token efêmero, Origin check em mutações e previews HTML sem scripts.
- Catálogo global é conveniência local reconstruível; dados canônicos continuam no projeto.

## 2.0.0-rc.1 — 2026-09-06

Recriação coordenada baseada na especificação v4. Release candidate implementada e testada localmente.

- Núcleos pequenos e referências condicionais; AGENTS.md único no método.
- Três eixos UX/S/O, mockup histórico sem sincronização e auditoria delimitada.
- Task Store com autorização explícita, CAS, dependências e arquivamento por ID.
- Migração semântica planejada com aplicação mecânica, snapshot, journal, resume e rollback.
- Contrato 2.0, catálogo de 31 controles, recibos imutáveis e gates locais.
- Distribuição offline por digest em diretório novo; sem download/execução/deploy automáticos.
- Testes determinísticos e de injeção de falha; matriz de evals comportamentais separada.

Não inclui homologação em Claude/Codex reais, benchmarks de tokens de modelos, pentest de aplicação
ou integração de CI independente. Consulte reports/VALIDATION.md para os resultados da construção.
