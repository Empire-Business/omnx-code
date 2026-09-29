# OMNX Code 2.2.0-rc.1 — com Console 1.1.0-rc.1

Método de desenvolvimento para agentes com Task canônica, captura local de sessão e Console. Esta release acrescenta integração de hooks opt-in, política de modelos, referências PNG e consulta opt-in de releases.

**Use a pasta completa desta distribuição. Não misture scripts, assets ou schemas entre versões.**

## Para começar sem operar tudo manualmente

Instale a skill no ambiente do seu agente e peça:

> Use a omnx-code 2.2.0-rc.1 deste pacote. Confira a integridade e o projeto selecionado. Se os hooks locais já foram autorizados e confiados nesse projeto, registre a implementação na Task canônica e tente abrir o Console no início; pedidos de análise continuam sem setup. Preserve requisitos do PRD e use PNG como referência visual sem inventar rotas. Não altere aplicação, dados, credenciais ou produção fora do escopo. No fim, informe o que foi e o que não foi validado.

O agente pode executar os comandos abaixo por você. O painel **não chama Codex, Claude ou outra API de IA**. Copiar um prompt não executa trabalho; o agente o executará quando você o colar e autorizar o escopo pertinente.

## O que está incluído

Visão geral de projetos em pastas diferentes, Kanban com bloqueados/cancelados, galeria de telas estáticas, decisões de produto/UX com revisão e histórico, feedback, prompts curtos por referência, diagnóstico somente leitura, launcher e engine de tarefas/migração/auditoria.

Arquivos do projeto continuam canônicos. Não há banco/backend remoto, telemetria, execução de código do projeto, deploy ou migração de banco pela interface. Uma consulta opcional ao GitHub só ocorre após consentimento explícito de update.

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
python3 "/origem/omnx-code/scripts/omnx.py" console install --destination "/pasta-permanente/omnx-code-2.2.0-rc.1"
python3 "/pasta-permanente/omnx-code-2.2.0-rc.1/scripts/omnx.py" console shortcut --destination "/sua/area-de-trabalho"
```

Não sobrescreve uma instalação ou atalho existente. A criação de `.desktop`, `.app` ou `.cmd` é opt-in. Geração dos arquivos foi testada; macOS/Windows e a experiência de duplo clique nesses sistemas **não foram homologados nesta sessão**. Há fallback pelo comando Python.

## Atualizar ou adotar uma versão sem apagar o projeto

1. Encerre a instância antiga usando a janela/terminal que a iniciou. Não mate processos por nome indiscriminadamente.
2. Extraia a versão em pasta nova e verifique seus bytes. Mantenha o pacote anterior intacto.
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

### Atualização de disponibilidade (opt-in por projeto)

A consulta começa desativada. Após uma autorização única para consultar e preparar releases oficiais compatíveis, a checagem pode ocorrer uma vez no início de uma sessão de implementação, conforme o intervalo local. Stable é padrão; RC exige seleção explícita. A versão em uso continua fixa.

```sh
python3 "/skill/scripts/omnx.py" --root "/projeto" update policy --enable --consent --channel stable --check-interval-hours 24
python3 "/skill/scripts/omnx.py" --root "/projeto" update auto-check
```

O candidato verificado fica em `.omnx/local/method-updates/` e aguarda seleção explícita em uma próxima sessão. Isso preserva a skill já carregada e o host configurado. Hash SHA-256 verifica bytes, não autoria/assinatura. Falta de rede não altera o runtime atual. Veja `references/distribution.md`.

## Começar uma sessão com acompanhamento

Em uma raiz OMNX confiável, a configuração inicial é uma única instalação de hooks local por host. Confirme e revise `AGENTS.md` antes; use o hash atual do próprio arquivo:

```sh
shasum -a 256 AGENTS.md
python3 "/skill/scripts/omnx.py" --root "/projeto" hooks install codex --trust-root --expected-agents-sha256 HASH_ATUAL
python3 "/skill/scripts/omnx.py" --root "/projeto" hooks install claude --trust-root --expected-agents-sha256 HASH_ATUAL
```

O comando instala apenas no projeto escolhido e preserva os demais hooks. Codex ainda exige revisão e confiança em `/hooks`; Claude aplica hooks de projeto segundo as configurações de confiança. A partir daí, uma solicitação direta e explícita de implementação cria/reutiliza Task, grava eventos mínimos e tenta abrir o Console uma vez naquela sessão. Sessões abertas sem hooks ativos não são interceptadas. Interrupções criam checkpoint; fechamento ou parada do host não conclui a Task.

Uma verificação de perfil é local e não chama um modelo:

```sh
python3 "/skill/scripts/omnx.py" --root "/projeto" model choose --risk low --ambiguity low --verification objective
python3 "/skill/scripts/omnx.py" --root "/projeto" model configure economical --model ID_DO_HOST --effort low
```

`requested_model` e `effective_model` são campos diferentes. O último só é preenchido se um sinal do host expuser o modelo. A CLI não troca o modelo da sessão ativa nem inicia cobranças.

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

Sem garantia de “zero falhas”. Consulte `reports/VALIDATION.md` para resultados desta candidata. Hooks, seleção efetiva de modelo e ativação do host não foram homologados em sessões Claude/Codex reais. As avaliações comportamentais de modelo permanecem **não executadas**.

## Repositório e código-fonte

O ZIP contém a distribuição completa, não um patch. O conteúdo de `omnx-code/` vai na raiz do repositório, preservando `.git` e customizações/landing alheias ao runtime. Veja `REPOSITORY-UPGRADE.md`. Preserve as licenças. Manifesto é a fonte de versão; frontmatter e Console são verificados contra ele nos testes. Inventário SHA-256 não equivale a assinatura/autoria.
