# OMNX Code 2.1.0-rc.2 — com Console 1.0.0-rc.2

Método de desenvolvimento para agentes + painel local opcional. Esta release corrige defeitos reproduzidos da `2.1.0-rc.1`, em vez de acrescentar outro sistema de organização.

**Use a pasta completa deste ZIP. Não misture scripts, assets ou schemas da rc.1 com os da rc.2.**

## Para começar sem operar tudo manualmente

Instale a skill no ambiente do seu agente e peça:

> Use a omnx-code 2.1.0-rc.2 deste pacote. Primeiro confira a versão, a integridade dos arquivos e o projeto selecionado. Prepare o acompanhamento visual sem alterar código da aplicação, banco, credenciais ou produção. Se o projeto usa a OMNX anterior, preserve as customizações e proponha a adoção/migração apropriada. Não reaproveite aprovações de decisões schema 1. Abra o Console ao terminar e deixe claro o que foi e o que não foi validado.

O agente pode executar os comandos abaixo por você. O painel **não chama Codex, Claude ou outra API de IA**. Copiar um prompt não executa trabalho; o agente o executará quando você o colar e autorizar o escopo pertinente.

## O que está incluído

Visão geral de projetos em pastas diferentes, Kanban com bloqueados/cancelados, galeria de telas estáticas, decisões de produto/UX com revisão e histórico, feedback, prompts curtos por referência, diagnóstico somente leitura, launcher e engine de tarefas/migração/auditoria.

Arquivos do projeto continuam canônicos. Não há banco paralelo, telemetria, serviço remoto, execução de código do projeto, deploy ou migração de banco pela interface.

O nome “Método atual” compara o lock do projeto com **esta instalação local**, não com a última versão do GitHub. Isso não é certificado de saúde ou de segurança do produto.

## Requisitos

Helpers e servidor: **Python 3.10+**. Não precisa de `pip install`, Node, npm, chave de API ou banco. PyYAML 6.0.3 puro está incluído com sua licença. Interface: navegador moderno.

O launcher aponta para o Python e a pasta usados na sua criação. Ele não é um binário autossuficiente assinado/notarizado. Coloque o pacote em uma pasta permanente antes de criar o ícone. Mover ou apagar a instalação quebra o atalho, mas não apaga nenhum projeto.

## Abrir

Use o caminho absoluto da instalação. `--root` vem **antes** de `console`:

```sh
python3 "/caminho/omnx-code/scripts/omnx.py" verify-package
python3 "/caminho/omnx-code/scripts/omnx.py" --root "/caminho/projeto" console open
```

No Windows, use o executável Python disponível (`python` ou `py -3`) em vez de presumir `python3`.

`console open` registra explicitamente a pasta informada, inicia um servidor local quando necessário, reaproveita a instância desta instalação e abre o navegador. Registrar a pasta **não instala/migra o método dentro do projeto**. Um projeto incompatível continua visível em leitura.

Depois de registrar seus projetos:

```sh
python3 "/caminho/omnx-code/scripts/omnx.py" console open
python3 "/caminho/omnx-code/scripts/omnx.py" console stop
```

Abrir o Console é uma autorização explícita para iniciar esse servidor local. Ele não mantém agentes trabalhando. O comando `stop` só encerra a instância identificada; nenhum projeto é apagado.

Para diagnóstico em primeiro plano:

```sh
python3 "/caminho/omnx-code/scripts/omnx.py" console serve --no-browser
```

A URL contém uma chave **de uso único**, em fragmento, válida por dois minutos para pareamento. Não a compartilhe. Depois, a sessão usa cookie HttpOnly/SameSite e proteção CSRF. Se expirar, reabra pelo comando ou ícone, em vez de reutilizar um link antigo.

## Instalar uma vez e criar ícone

A skill pode ficar em pasta permanente já escolhida. Como alternativa explícita, `console install` copia o pacote verificado para **uma pasta nova**, cujo diretório pai precisa existir:

```sh
python3 "/origem/omnx-code/scripts/omnx.py" console install --destination "/pasta-permanente/omnx-code-2.1.0-rc.2"
python3 "/pasta-permanente/omnx-code-2.1.0-rc.2/scripts/omnx.py" console shortcut --destination "/sua/area-de-trabalho"
```

Não sobrescreve uma instalação ou atalho existente. A criação de `.desktop`, `.app` ou `.cmd` é opt-in. Geração dos arquivos foi testada; macOS/Windows e a experiência de duplo clique nesses sistemas **não foram homologados nesta sessão**. Há fallback pelo comando Python.

## Atualizar da rc.1 sem apagar o projeto

1. Encerre a instância antiga usando a janela/terminal que a iniciou. Não mate processos por nome indiscriminadamente.
2. Extraia a rc.2 em pasta nova e verifique seus bytes. Mantenha o pacote anterior intacto.
3. Configure/ative a nova skill no agente; abrir um ZIP não substitui o contexto de uma sessão já em execução.
4. No projeto novo-modelo, `method verify` mostra a divergência e o hash atual do lock. `method adopt` atualiza apenas a adoção do pacote, com backup e CAS:

```sh
python3 "/nova/omnx-code/scripts/omnx.py" --root "/projeto" method verify
python3 "/nova/omnx-code/scripts/omnx.py" --root "/projeto" method adopt \
  --expected-sha256 HASH_ATUAL_DO_LOCK \
  --authority-ref "ORIGEM_REAL_DA_AUTORIZACAO"
```

O texto acima indica onde inserir valores reais; não é uma autorização fictícia para copiar. A adoção não faz deploy, não altera o banco e não reorganiza produto/PRD automaticamente.

5. Decisões antigas schema 1 aparecem como **histórico não verificado**. Para voltar a usá-las, o agente lê a decisão/artefato atual e executa `decision revise`, preservando o original e reapresentando uma revisão pendente. Você aprova novamente somente o escopo necessário. Veja `references/console.md`.
6. Recrie o atalho apontando para a nova instalação, sem sobrescrever às cegas o anterior.

Não é necessário reescrever o PRD, mockups ou todas as Tasks para adotar esta patch release. Projeto ainda no formato `.empire`/`CLAUDE.md` precisa da migração semântica explícita, não apenas da adoção de versão.

## Projetos realmente legados

Peça à skill para inventariar fontes governadas, preservar regras customizadas e produzir o plano semântico antes da escrita. `migrate plan` não adivinha a classificação. A aplicação mecânica oferece snapshot, journal, CAS, resume e rollback. Detalhes em `references/migration.md`.

A migração reorganiza o método: não troca stack, não remove Loja de Apps/tickets existentes, não migra dados reais, não publica. Ambiguidade relevante não pode ser escondida apenas no backup.

## Projeto novo

```sh
python3 "/skill/scripts/omnx.py" --root "/projeto" init \
  --authority-ref "ORIGEM_REAL_DO_PEDIDO" \
  --bootstrap-ref "COMO_AGENTS_SERA_LIDO" --output "/pasta-existente/plano.json"
python3 "/skill/scripts/omnx.py" --root "/projeto" migrate apply \
  --plan "/pasta-existente/plano.json" --approved-digest DIGEST_REAL_DO_PLANO
```

O primeiro comando só gera plano. Reveja antes de aplicar. Não cria uma árvore inteira de documentos vazios. Apenas `AGENTS.md` é entrada canônica; nunca criar espelho `CLAUDE.md`.

## Skill no Claude Code e Codex

Pastas documentadas de skills pessoais: Claude Code `~/.claude/skills/omnx-code/`; Codex CLI `~/.agents/skills/omnx-code/`. Alguns hosts/clouds possuem instalação própria. Não mantenha versões duplicadas descobertas pelo host sem identificar qual está ativa.

Claude Code não deve ser presumido capaz de carregar `AGENTS.md` automaticamente: use ativação explícita ou adaptador autorizado. Leia `adapters/claude-code.md` e `adapters/codex.md`. Nenhum teste de presença de executável comprova integração real do modelo.

O contrato com `security-auditor` continua 2.0, catálogo revisão 1. Esta entrega não modifica a skill do auditor. S0 não exige chamá-la; S2/S3 precisam de verificação pertinente e evidência real. Instalação/adoção do auditor é explícita.

## Testar e verificar

```sh
python3 "/skill/scripts/omnx.py" verify-package
python3 "/skill/tests/run.py" --output "/fora-do-pacote/testes.json"
```

`tests/run.py` usa fixtures locais e servidor loopback em testes HTTP; não executa sua aplicação. Deixe saídas fora do diretório inventariado para não invalidar `verify-package`.

Desenvolvimento da interface, com Playwright/Chromium previamente instalados:

```sh
python3 "/skill/tests/browser/run.py" --output "/fora-do-pacote/browser.json"
python3 "/skill/tests/browser/run.py" --isolated-dom --output "/fora-do-pacote/dom.json"
python3 "/skill/tests/scale.py" --output "/fora-do-pacote/escala.json"
```

O primeiro é ponta a ponta HTTP real. O segundo usa transporte/clipboard/histórico simulados e documentos offline para testar o DOM com a engine; **não substitui o primeiro**. Veja `reports/VALIDATION.md` para o que foi executado, bloqueado ou não homologado.

## Limites deliberados

Aprovação do Console é um registro de usuário local, não autenticação forte ou assinatura independente. Usuário/processo com acesso irrestrito à conta pode alterar os próprios arquivos. Gates locais não substituem CI protegido.

HTML no Console é **estático**, sanitizado, sem scripts, navegação ou APIs. Imagens e CSS locais permitidos são vinculados ao manifesto da proposta. Um preview bonito não demonstra que a jornada ou integração funciona. Não forneça dados reais/sigilosos nos mockups; redaction textual é defensiva, não detector perfeito de segredos/PII/imagens.

Sem garantia de “zero falhas”. Esta candidata corrige as falhas reproduzidas e inclui testes de regressão. Não houve homologação em Claude/Codex reais, macOS, Windows, Safari, projetos privados do usuário ou produção. Os 130 cenários de modelo permanecem **planejados**, não executados.

## Repositório e código-fonte

O ZIP contém a distribuição completa, não um patch. O conteúdo de `omnx-code/` vai na raiz do repositório, preservando `.git` e customizações/landing alheias ao runtime. Veja `REPOSITORY-UPGRADE.md`. Preserve as licenças. Manifesto é a fonte de versão; frontmatter e Console são verificados contra ele nos testes. Inventário SHA-256 não equivale a assinatura/autoria.
