# OMNX Code — 2.0.0-rc.1

Desenvolvimento assistido por IA com escopo explícito, tarefas canônicas e verificações proporcionais.
Recriação coordenada com security-auditor baseada na especificação v4 fornecida pelo usuário.

## Uso normal

Instale as duas skills. Na aplicação, peça ao agente para usar OMNX; não é necessário operar a CLI
manualmente em cada Task. A skill seleciona referências e usa helpers quando há trabalho mecânico.

> Use omnx-code para corrigir este comportamento. Preserve o escopo e as alterações locais.
> Não publique. Valide somente o delta pertinente e entregue as evidências.

Análise não instala arquivos. Manutenção pequena não exige PRD novo nem mockup histórico.
UX0–UX3 trata incerteza de experiência; S0–S3 trata risco; O0–O3 trata efeito/autorização.
Auditor recebe apenas o necessário. Task done não significa produção.

## Projeto novo

A adoção é explícita e mínima. O primeiro comando gera um plano, não aplica:
```sh
python scripts/omnx.py --root /caminho/projeto init \
  --authority-ref "conversa:pedido-real-de-adocao" \
  --bootstrap-ref "sessao:AGENTS-sera-lido-na-ativacao-explicita" \
  --output /tmp/omnx-plan.json
```
Revise o plano e sua origem real; aplique com o digest retornado:
```sh
python scripts/omnx.py --root /caminho/projeto migrate apply \
  --plan /tmp/omnx-plan.json --approved-digest DIGEST_REAL_DO_PLANO
python scripts/omnx.py --root /caminho/projeto doctor
```
O diretório de output precisa existir. Texto de autoridade nos exemplos é indicação de formato,
não uma permissão real. Não copie referência fictícia para declarar aprovação inexistente.

Adoção cria AGENTS, project.yaml, method.lock e exclusão da área local. Não cria PRD, mockup,
relatório de segurança ou dezenas de pastas vazias automaticamente.

## Projeto antigo

> Use a nova omnx-code para migrar o método deste projeto. Inventarie regras e documentos governados,
> preserve customizações, consolide pendências no Task Store e elimine CLAUDE.md ativo após conciliação.
> Não altere produto, banco ou credenciais. Mostre ambiguidades materiais; aplique só plano verificável.

Siga references/migration.md. Conteúdo legado exige resolução de blocos e destino antes de aplicar.
Não classificar é melhor que destruir: a substituição afetada fica pendente, não todo diagnóstico.
Resume/rollback são comandos reais, com journal e CAS. Backups são restritos e inertes (.bin).

## Adotar o auditor e verificar o conjunto

Depois de verificar os dois pacotes, use `method adopt` com hash atual do lock, origem real da decisão,
pasta do auditor e digest confiado do integrity.json dele. `method verify --auditor-dir ...` compara
os pacotes com o lock. S0 não exige instalar um auditor ausente. Não simule chamada independente.

## Conteúdo

SKILL.md enxuto; dez referências condicionais; templates opcionais; CLI; schemas de projeto/Tasks;
contrato de auditoria 2.0; migração recuperável; catálogo gerado do auditor; testes e evals separados.

A verificação de segurança é da skill especializada. O runtime apenas identifica conteúdo e valida
contratos/evidências declaradas. Nenhum script publica, cobra, executa SQL remoto ou instala ferramentas.

## Instalação

O ZIP é uma distribuição de skill, não um plugin de marketplace com conectores.
Extraia a pasta inteira, preservando SKILL.md na raiz dessa pasta. Primeiro use pasta nova ou cópia
recuperável; não sobrescreva customizações antigas sem revisar REPOSITORY-UPGRADE.md.

| Host local | Pessoal | Por projeto |
|---|---|---|
| Claude Code | `~/.claude/skills/<nome>/` | `.claude/skills/<nome>/` |
| Codex CLI | `~/.agents/skills/<nome>/` | `.agents/skills/<nome>/` |

Locais/invocação conforme documentação consultada em 6/9/2026; veja reports/SOURCES.md.
Em Claude Code use `/omnx-code` ou `/security-auditor`; em Codex CLI use `$omnx-code` ou
`$security-auditor`. Hosts corporativos, cloud e interfaces de upload podem ter mecanismo próprio.
Não confunda instruções do projeto (AGENTS.md) com a pasta de instalação da skill.

A distribuição foi testada como arquivos/scripts em Linux/Python, não dentro das CLIs reais.
Confirme descoberta/versão/escopo efetivo no seu ambiente. O instalador não modifica configuração global.

## Requisitos e verificação

As instruções funcionam com um agente capaz de ler arquivos; os helpers precisam de Python 3.10+.
Nesta entrega foram executados com Python 3.13.5/Linux. Nenhum pip, chave de API ou serviço externo é
necessário para os helpers. O modelo/assinatura do host são seus; os scripts não chamam API de LLM.

```sh
python scripts/omnx.py verify-package
python tests/run.py --output /tmp/omnx-test-results.json
```

`verify-package` compara bytes ao inventário, não autentica uma assinatura. O SHA-256 do ZIP deve vir
de uma origem confiada. Os arquivos não foram assinados digitalmente.
`tests/run.py` executa fixtures locais em diretórios temporários, sem testar sua aplicação/produção.

## O que está validado e o que não está

Consulte reports/VALIDATION.md e reports/test-results.json. Não há garantia de encontrar toda
vulnerabilidade nem de prever todo comportamento de um modelo. Os 130 cenários em evals/scenarios.json
são conjunto de aceitação comportamental, não 130 testes de modelo já aprovados.

Não foram executados Claude/Codex reais, homologação Windows/macOS, pentest, apps reais do usuário,
integrações Asaas/Hotmart/Supabase ou benchmark de tokens em modelo. Gates são avaliações locais,
não proteção de branch ou autorização de produção. Migração de texto precisa de resolução semântica
pelo agente/revisor: o motor não adivinha decisões de negócio.

## Atualizações e código-fonte

manifest.json identifica a versão. integrity.json é inventário gerado. Os scripts estão incluídos
em código-fonte e possuem testes. Preserve NOTICE/LICENSE e a licença de PyYAML.
Referências/históricos e exemplos não são arquivos que devam ser lidos inteiros em cada Task.

Para publicar o repositório, veja REPOSITORY-UPGRADE.md. Para distribuição versionada sem sobrescrita,
veja a referência de distribuição da OMNX. Atualização do pacote, migração documental e migração de
dados da aplicação são três operações diferentes.
