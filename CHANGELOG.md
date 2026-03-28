# Changelog — empire-vibe-coding

Histórico de versões da skill. Ao fazer qualquer atualização, registre aqui a versão, data e o que foi adicionado/modificado.

---

## v1.1 — 2026-03-28

### Modificado
- **Security-auditor agora tem repo próprio**: `https://github.com/Empire-Business/security-auditor`. Instalação e atualização usam `git clone` / `git pull` deste repo como fonte primária
- **Verificação de versão remota**: durante setup e auto-update, consulta o CHANGELOG.md remoto via `curl` para comparar com a versão instalada antes de atualizar
- **Fallback bundled mantido**: se git/curl não estiverem disponíveis, usa `bundled-skills/security-auditor/` como fallback offline
- **Auto-atualização aprimorada**: atualiza empire-vibe-coding e security-auditor de forma independente, cada uma pelo seu próprio repo

---

## v1.0 — 2026-03-28

### Inicial

- **Setup automático de CLAUDE.md**: instala o template Empire em projetos novos; faz merge inteligente em projetos existentes sem destruir conteúdo do usuário
- **Bundled security-auditor v1.5**: verifica se a skill `/security-auditor` está instalada globalmente e na versão mínima exigida; instala ou atualiza automaticamente
- **State document** (`.empire/state.json`): rastreia fase do projeto (setup vs. trabalho normal), versões instaladas e data do último update check
- **Máquina de estados**: detecta automaticamente se é primeira execução (setup) ou projeto já configurado (modo trabalho)
- **Tasks obrigatórias 100% do tempo**: toda ação é precedida de `TaskCreate`, dando visibilidade ao usuário sobre o que será feito
- **Modo de trabalho normal**: segue CLAUDE.md como índice, documenta em `docs/`, sem código morto nem documentação morta
- **Auto-atualização via git pull**: ao pedido do usuário, faz `git pull` no diretório da skill e re-verifica o security-auditor bundled
- **Landing page bilíngue (PT/EN)**: página estática hospedável no Vercel com design Empire Business DS1 v2.0
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
