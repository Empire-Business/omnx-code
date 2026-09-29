# Instalação e atualização sem sobrescrita silenciosa

As duas pastas ZIP são skills completas, com manifesto e inventário SHA-256. Não são assinadas.
O checksum deste pacote serve para verificar bytes; obtenha o digest esperado por uma origem que você confia.
Não execute script baixado para decidir se o próprio download é confiável.

## Verificação remota e staging opt-in

A política de disponibilidade é local a cada projeto OMNX e começa desativada. Uma autorização explícita ativa, uma vez, consulta e staging de releases oficiais compatíveis:

~~~sh
python3 <skill>/scripts/omnx.py --root <projeto> update policy --enable \
  --consent --channel stable --check-interval-hours 24
~~~

Stable é padrão; escolha rc somente se quiser receber candidatos release candidate. A checagem pode ocorrer no primeiro prompt de implementação após o intervalo, sem atrasar o hook, ou manualmente com update auto-check. update remote-check força uma nova consulta. Falhas atualizam o estado local com disponibilidade indisponível e preservam a versão atual. Não há consulta por ferramenta, daemon, credencial nova nem telemetria.

O cliente usa a origem oficial configurada do GitHub, timeout curto, tamanho máximo, redirecionamentos HTTPS permitidos, SHA-256 publicado do asset, manifesto, compatibilidade do contrato/schema e a validação segura do instalador ZIP existente. Tags devem ser posteriores à versão local. O candidato é extraído inerte, com inventário verificado, sob .omnx/local/method-updates/omnx-code-<versão>. Estado local distingue installed_version, candidate_version, status e activation. Candidato staged significa preparado; não significa ativo, atualizado, assinado ou confiável como código executável.

A ativação continua escolha explícita do caminho versionado pelo host, em uma sessão futura. Nenhum ponto de extensão uniforme do Claude/Codex permite à instalação mudar a skill já carregada ou o resolver de todas as próximas sessões. O projeto mantém a versão adotada em .omnx/method.lock.json; confira a comparação entre pacote carregado, pacote adotado, Console e candidato antes de adotar. A versão real das instruções já carregadas na conversa não é observável em todos os hosts e permanece não confirmada. A política atual não faz ativação automática; não a descreva como “atualizada” só pelo staging.

Desativar sem remover o histórico:

~~~sh
python3 <skill>/scripts/omnx.py --root <projeto> update policy --disable
~~~

Interrupção ou falha de consulta não troca runtime. Versões staged permanecem lado a lado; nenhuma sessão concorrente substitui uma pasta ativa. Para recuperar, mantenha a versão anterior, escolha novamente o caminho estável do host e valide compatibilidade de schema antes de voltar a executar runtime antigo.

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
