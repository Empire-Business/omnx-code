# Validação da OMNX Code 2.1.0-rc.2

## O que foi executado

| Camada | Resultado | Evidência |
|---|---|---|
| Runtime, estado, migração, HTTP real, paths, locks e processos Linux | 247 testes, 0 falhas, 0 erros, 0 pulados | `test-results-2.1.0-rc.2.json` |
| Interface no Chromium 144, com assets reais e transporte de fixtures offline | 13 cenários completos passaram | `browser-dom-rc2.json` |
| Navegador acessando servidor por HTTP real | Bloqueado pelo ambiente: `ERR_BLOCKED_BY_ADMINISTRATOR` | `browser-http-status.json` |
| Projeto sintético criado com pacote rc.1 e adotado pela rc.2 | Passou; Task/código preservados, aprovação antiga não herdada | `upgrade-rc1-to-rc2.json` |
| Projeção com 500, 2.000 e 10.000 Tasks | Contagem completa; atualização sem alteração fez zero releituras de conteúdo | `scale-rc2.json` |
| Manifestos, sintaxe JS, 13 schemas e contrato/catálogo pinado do auditor | Verificados | `contract-check-rc2.json` |

Os testes foram executados em Linux/Python 3.13.5. Há verificação gramatical de Python 3.10, não execução real nessa versão. Nenhuma aplicação do usuário, produção, conta externa, segredo real ou cobrança foi usada.

## O que “teste no navegador” significa aqui

O ensaio DOM abriu a interface no Chromium com **app.js/style.css reais**, sem reescrever seu código. A camada de teste substituiu fetch por um adaptador local que opera fixtures pela engine. Histórico de navegação, geração de UUID, clipboard e URL do iframe foram substituídos por doubles; o iframe recebeu documento offline sanitizado. Não houve túnel para contornar a política de rede do navegador.

Foram exercitados: inicialização, clones, Kanban/bloqueados, erro isolado, conteúdo hostil como texto, prompt, preview estático, opção obrigatória, persistência, duas abas com revisão desatualizada, sujeito alterado, release somente leitura, transição de Task, teclado e layout mobile. O teste HTTP separado usa servidor real e cliente Python, com cookies, CSRF, origem, capabilities, expiração e idempotência.

**As duas camadas não equivalem à homologação ponta a ponta browser→HTTP.** O runner real está incluído em `tests/browser/run.py`, sem `--isolated-dom`, para executar onde essa conexão for permitida. Não remover políticas corporativas para fazê-lo passar.

Durante desenvolvimento, houve execuções preliminares interrompidas no encerramento do ensaio Playwright e correções do próprio adaptador offline. Não foram contadas como rodadas aprovadas. O JSON indicado registra uma execução completa que chegou ao fim. Isso reforça a distinção entre validação DOM e homologação do ambiente real.

## Escala observada — uma execução por tamanho

| Tasks | Leitura fria | Atualização sem alterações | Arquivos relidos sem alteração | Arquivos relidos após mudar uma Task |
|---:|---:|---:|---:|---:|
| 500 | 0,35 s | 0,04 s | 0 | 1 |
| 2.000 | 1,39 s | 0,16 s | 0 | 1 |
| 10.000 | 6,91 s | 0,84 s | 0 | 1 |

Medição da projeção local, não benchmark estatístico de navegador, múltiplos usuários, disco lento ou rede. O processo ainda consulta metadados e monta resumos; não significa zero CPU/I/O. O prompt compacto dessas fixtures tinha 1.086 caracteres; não é contagem de tokens nem comprovação de economia no modelo.

## Limites e suporte

Não foram executados modelos independentes/subagentes, Claude Code/Codex reais, macOS, Windows, Safari, pentest externo, integrações de pagamento/banco ou os 130 evals comportamentais de modelo. O catálogo de controles continua pinado ao auditor 2.0.0-rc.1; compatibilidade estrutural não comprova uma chamada ao modelo.

Launchers Mac/Windows foram gerados e seus conteúdos verificados, mas não clicados nesses sistemas. Abertura/reuso/stop em processos Linux foram testados por CLI sem navegador. O runtime requer Python; não é um app nativo assinado.

Aprovação local não é prova forte de identidade. Hash/histórico não impedem um processo hostil com controle irrestrito da mesma conta de regravar arquivos. Gates locais não são CI protegido. Redaction não é detector perfeito de segredos/PII, especialmente em imagens. Previews são estáticos e podem ter aparência simplificada pela sanitização.

## Liberação

Esta é **release candidate corrigida**, não certificação “sem falhas”. Falhas conhecidas R01–R12 têm correções e testes em `REGRESSIONS.md`. Não aceitar aprovações v1 da rc.1 como atuais: reapresentar e reconfirmar somente o escopo necessário.

A distribuição deve ser verificada após extração com `verify-package` e suas suítes locais. Resultados de reexecução do ZIP final são fornecidos junto à entrega quando disponíveis; testes não chamam sua aplicação.
