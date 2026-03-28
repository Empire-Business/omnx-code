# Changelog — omnx-code

Histórico de versões da skill. Ao fazer qualquer atualização, registre aqui a versão, data e o que foi adicionado/modificado.

---

## v1.4 — 2026-03-28

### Adicionado
- **Task 4 — GitHub Setup**: novo passo obrigatório no setup que verifica se o projeto já possui remote `origin` e, caso contrário, cria o repositório GitHub via `gh` CLI
- **Repositório sempre privado**: regra absoluta — todo repositório criado pela skill usa `--private`. A skill se recusa a criar repos públicos mesmo se o usuário pedir explicitamente, e orienta a mudança manual se necessário
- **Verificação de visibilidade pós-criação**: após criar o repo, confirma `isPrivate: true` via `gh repo view --json isPrivate`. Se por algum motivo estiver público, executa `gh repo edit --visibility private` imediatamente
- **Campos no state document**: `github_repo` e `github_repo_private` adicionados ao `.empire/state.json`
- **Regra 6 no Modo de Trabalho Normal**: proíbe qualquer comando que torne o repo público durante o trabalho normal, não só no setup
- **Detecção de `gh` CLI**: se não instalado ou não autenticado, exibe instruções claras e aguarda o usuário resolver antes de continuar

### Modificado
- `omnx_version` no state document: `1.2` → `1.4`
- Summary do setup inclui linha de status do GitHub (criado / já existia / gh não disponível)
- Task 4 (antiga "Finalizar setup") renumerada para Task 5

---

## v1.3 — 2026-03-28

### Modificado
- **Removido `bundled-skills/security-auditor/`**: fallback offline eliminado. Security-auditor é instalado exclusivamente via `git clone https://github.com/Empire-Business/security-auditor`. Se `git` não estiver disponível, a skill retorna erro claro.

---

## v1.2 — 2026-03-28

### Modificado
- **Renomeado de `empire-vibe-coding` para `omnx-code`**: repo GitHub, nome da skill, comando `/omnx-code`, diretório de instalação `~/.claude/skills/omnx-code`
- **Nova identidade visual na landing page**: fundo preto, verde neon (#00FF88), wordmark OMNX em texto — sem dependência de logo PNG externo
- **Removidas referências ao Empire Business design system**: landing page agora usa design system próprio OMNX

---

## v1.1 — 2026-03-28

### Modificado
- **Security-auditor agora tem repo próprio**: `https://github.com/Empire-Business/security-auditor`. Instalação e atualização usam `git clone` / `git pull` deste repo como fonte primária
- **Verificação de versão remota**: durante setup e auto-update, consulta o CHANGELOG.md remoto via `curl` para comparar com a versão instalada antes de atualizar
- **Fallback bundled mantido**: se git/curl não estiverem disponíveis, usa `bundled-skills/security-auditor/` como fallback offline
- **Auto-atualização aprimorada**: atualiza omnx-code e security-auditor de forma independente, cada uma pelo seu próprio repo

---

## v1.0 — 2026-03-28

### Inicial

- **Setup automático de CLAUDE.md**: instala o template padrão em projetos novos; faz merge inteligente em projetos existentes sem destruir conteúdo do usuário
- **Bundled security-auditor v1.5**: verifica se a skill `/security-auditor` está instalada globalmente e na versão mínima exigida; instala ou atualiza automaticamente
- **State document** (`.empire/state.json`): rastreia fase do projeto (setup vs. trabalho normal), versões instaladas e data do último update check
- **Máquina de estados**: detecta automaticamente se é primeira execução (setup) ou projeto já configurado (modo trabalho)
- **Tasks obrigatórias 100% do tempo**: toda ação é precedida de `TaskCreate`, dando visibilidade ao usuário sobre o que será feito
- **Modo de trabalho normal**: segue CLAUDE.md como índice, documenta em `docs/`, sem código morto nem documentação morta
- **Auto-atualização via git pull**: ao pedido do usuário, faz `git pull` no diretório da skill e re-verifica o security-auditor bundled
- **Landing page bilíngue (PT/EN)**: página estática hospedável no Vercel
- **Versão mínima do security-auditor requerida**: v1.5

---

## Como registrar uma nova versão

Ao fazer qualquer atualização na skill, adicione uma entrada no topo deste arquivo seguindo o padrão:

```markdown
## vX.Y — YYYY-MM-DD

### Adicionado
- [o que foi adicionado]

### Modificado
- [o que foi alterado em algo existente]

### Removido
- [o que foi deletado]

### Corrigido
- [bugs ou comportamentos errados corrigidos]
```

Use **vX.Y** onde X é versão major (mudanças grandes de arquitetura) e Y é minor (novas features ou melhorias). Bump minor para adições; bump major para refatorações completas.
