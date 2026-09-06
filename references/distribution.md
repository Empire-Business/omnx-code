# Instalação e atualização sem sobrescrita silenciosa

As duas pastas ZIP são skills completas, com manifesto e inventário SHA-256. Não são assinadas.
O checksum deste pacote serve para verificar bytes; obtenha o digest esperado por uma origem que você confia.
Não execute script baixado para decidir se o próprio download é confiável.

Bootstrap inicial: verificar ZIP/manifesto por ferramenta confiável, extrair em pasta nova e inspecionar.
Depois, um runtime já confiado pode verificar/extrair próximas versões sem executar código delas:
```sh
python <skill-confiada>/scripts/omnx.py update plan --archive <skill.zip> \
  --expected-sha256 <sha256-confiado> --destination <pasta-nova-versionada> \
  --current-version 2.0.0-rc.1 --output <local>/install-plan.json
python <skill-confiada>/scripts/omnx.py update apply --plan <local>/install-plan.json \
  --approved-digest <digest-do-plano>
```
`check` tem a mesma inspeção read-only. Não consulta rede nem ativa nada automaticamente.
Destino deve ser novo; instalação existente modificada não é sobrescrita. Repetir pacote idêntico no
mesmo destino é no-op. Rejeitar downgrade, ZIP traversal/links, colisões, expansão abusiva e hash errado.
Staging incompleto não vira instalação ativa. Versão anterior fica intacta para voltar a apontar o host.

Ativação da nova pasta no host e adoção de projeto são operações explícitas separadas. O instalador não
altera ~/.claude, ~/.agents, configurações globais ou repositórios por conta própria.
Não há auto-resolução global de versões por daemon: cada projeto tem lock; selecione a versão compatível.
Com múltiplos projetos, mantenha diretórios versionados e configure o host conforme seu fluxo verificado.
Incompatibilidade limita componente afetado, não leitura e manutenção segura independentes.

Rollback de pacote: reative pasta anterior preservada. Isso não converte schema do projeto para trás;
se houve migração documental, use seu rollback/compatibilidade antes de executar runtime antigo.

## Adoção explícita do conjunto no projeto

`method adopt --expected-sha256 <hash-do-lock> --authority-ref <origem> --auditor-dir <pasta>
--trusted-auditor-digest <sha256-do-integrity-json>` verifica catálogo de versão/arquivos e mantém
backup do lock anterior. `method verify --auditor-dir <pasta>` compara o conjunto. Não ativa o host.

O bootstrap em diretório novo é deliberado: não há update in-place que apague customizações.
Instale primeiro fora do diretório de descoberta automática do host; ative só a pasta validada.
