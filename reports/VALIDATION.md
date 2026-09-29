# Validação da OMNX Code 2.2.0-rc.1

## Execução desta candidata

| Camada | Resultado | Evidência |
|---|---|---|
| Suíte local completa: runtime, estado, migração, API HTTP, locks, processos e fixtures diárias | 270 testes, 0 falhas, 0 erros, 0 pulados; 26,662 s | `test-results-2.2.0-rc.1.json` |
| Fixtures adicionais de hooks, sessão, Console, PNG, política de modelos e update | 22 testes, todos aprovados; também incluídos na suíte completa | `tests/test_daily.py` |
| Estresse de registro do catálogo | 30 rodadas de 6 processos; 180 registros e catálogos completos | Execução local repetida após corrigir a corrida de inicialização |
| Inventário da árvore e ZIP extraído em pasta limpa | 146 arquivos verificados em ambos; manifesto confirma `2.2.0-rc.1` | `verify-package` local e após extração limpa; pacote em `/private/tmp` |
| Projeção com 500, 2.000 e 10.000 Tasks | Atualização sem alteração releu zero conteúdo; alteração de uma Task releu um arquivo | `scale-2.2.0-rc.1.json` |
| Sintaxe do JavaScript do Console | `node --check console/assets/app.js` passou | Comando local |
| Chromium/DOM ou navegador para HTTP | Não executado: Playwright não está instalado (`ModuleNotFoundError: No module named playwright`) | `browser-status-2.2.0-rc.1.json` |
| Repositório de origem image-to-html | Revisão e identificador do host documentados; nenhuma conversão executada porque não havia PNG de aplicação | `adapters/image-to-html.md`, `reports/SOURCES.md` |

Os testes completos rodaram em macOS arm64 com Python 3.12.14. A suíte HTTP local usa cliente Python e servidor loopback real; não equivale a browser→HTTP. Não foram instaladas dependências de teste.

## Escala observada

Uma execução por tamanho, com fixtures sintéticas e disco local:

| Tasks | Leitura fria | Sem alteração | Uma alteração | Leituras de conteúdo sem alteração / depois |
|---:|---:|---:|---:|---:|
| 500 | 0,255 s | 0,085 s | 0,064 s | 0 / 1 |
| 2.000 | 1,066 s | 0,125 s | 0,118 s | 0 / 1 |
| 10.000 | 4,643 s | 0,591 s | 0,597 s | 0 / 1 |

Não é benchmark estatístico de navegador, usuários simultâneos, disco lento ou rede. Prompt fixture tinha 1.086 caracteres; não é contagem de tokens nem evidência de economia de modelo.

## Limites de homologação

- Hooks foram testados com payloads sintéticos, não em sessões reais Codex/Claude. Trust/configuração de host, abertura gráfica, presença visual e cobertura de entradas devem ser homologados no host usado.
- A integração registra o runtime do hook/Console, mas a versão da skill já carregada na memória do host não é observável uniformemente.
- Nenhum modelo ou subagente foi chamado. Modelo/esforço efetivos, escalonamento real e custo permanecem não confirmados.
- Consultas de release foram cobertas com respostas simuladas: sem atualização, timeout, canal, digest, compatibilidade e staging. Nenhum request remoto foi feito durante os testes.
- Não foi fornecido PNG de aplicação. Dimensões são lidas do cabeçalho e não determinam viewport, crop ou escala CSS. Não há screenshot comparativo de aplicação.
- Não foram executados Playwright/Chromium, Safari, Windows, pentest externo, produção ou integração de aplicação real.

As avaliações em `evals/daily-workflow.json` continuam `not_run` para comportamento de modelo/host. Cobertura mecânica não altera esse estado.

## Histórico

A validação da 2.1.0-rc.2 foi arquivada em `history/VALIDATION-2.1.0-rc.2.md`. Os resultados desta seção pertencem somente à 2.2.0-rc.1.
