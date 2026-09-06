# Roteamento proporcional

Classifique comportamento real, não arquivo/extensão. A classificação é responsabilidade do agente,
não uma inferência de regex. O helper `route` apenas projeta classes já avaliadas.

## Experiência
UX0: nenhuma experiência alterada. UX1: alteração local inequívoca, padrão preservado.
UX2: decisão relevante delimitada. UX3: jornada nova/ampla/crítica com incerteza material.
Valide o delta, não toda a história de mockups. UX2 pode já estar resolvido por padrão aprovado.

## Segurança
S0: nenhum impacto identificado em confiança/dados/efeitos. S1: caminho protegido, delta local.
S2: exposição/entrada/integração ou controle delimitado. S3: auth central, privilégios,
isolamento, segredo, dados destrutivos ou efeitos financeiros/acesso crítico.
Webhook de telemetria não obriga todo catálogo financeiro; webhook que concede acesso pago pode ser S3.
Refactor de helper central não é S0 só por intenção. CI mecânico barato pode continuar em S0.

## Operação
O0: inspeção sem efeito externo. O1: edição reversível/teste isolado autorizado.
O2: efeito remoto delimitado não produtivo ou consumo de serviço; autoridade de destino/custo necessária.
O3: produção, dinheiro, privilégio, destruição, rotação ou irreversibilidade; autoridade específica.
`git push` com auto-deploy pode ser O3. `npm test` pode executar código arbitrário ou chamar produção.

## Rotas
Análise → leitura → resposta. Ajuste → Task compacta → edição → teste pertinente.
Feature conhecida → requisito/critério → impacto → implementação/testes → documentos afetados.
UX incerta → brief mínimo → representação suficiente → decisão escopada → implementação.
Mudança crítica → controles pertinentes antes do desenho → código → evidência → operação autorizada.
Incidente → contenção autorizada e evidência, não reconstrução documental prévia.

Incerteza pede a menor investigação. Persistindo desconhecido relevante, limite a promoção que depende
dele e continue trabalho independente seguro. Não classifique S3 universalmente para evitar decidir.
