# Integração de segurança 2.0

A definição dos controles pertence ao security-auditor. contracts/control-index.json é cópia gerada
idêntica/pinada para validação offline, não segunda edição de política técnica.
Perfil de projeto usa null para desconhecido. Não duplicar características em outro baseline YAML.

## Chamada
Selecione risco e controles pertinentes; prepare request com objetivo, identidades, manifesto dos
arquivos e dependências, ambiente, política/registry, limites e permissões realmente disponíveis.
Use modo design antes de consolidar desenho crítico e delta depois do diff final. Não repetir full audit.
Orçamento padrão: até 30 arquivos relacionados, 30 tools, 2500 tokens de saída, 2 correções.
Expansão necessária deve ser explicada; cobertura parcial não é PASS. Sem cortar achado para caber.

Exemplo de helper (ajuste paths/controles ao projeto real):
```sh
python <skill>/scripts/omnx.py --root <projeto> audit request \
  --paths src/webhook.ts src/access.ts \
  --controls SEC-WEBHOOK-01 SEC-WEBHOOK-02 SEC-AUTHZ-01 \
  --surfaces paid-access-webhook --objective "Verificar concessão de acesso" \
  --impact S3 --mode delta --output <destino-local>/request.json
```
Em chamada coordenada, informar também --task-id e --orchestrator-id. O comando não chama um modelo;
a OMNX encaminha o request ao especialista disponível no host. Sem subagente, revisão própria é self_review.

## Resposta e recibo
Auditor retorna contrato, não backlog. Cada controle solicitado consta uma vez; deferred/unsupported
vira unknown com motivo. Pass/fail exige evidência. Design não certifica implementação.
Validar identidades, snapshot, policy/registry, coverage, origem das evidências e tipo de revisão.
Uma tentativa de reparo estrutural é aceitável; resposta inválida persistente é falha explícita.

Persistir recibo sanitizado S2/S3 quando autorizado, inclusive sem finding. IDs imutáveis: reenviar
mesmo conteúdo é no-op; conteúdo diferente com mesmo AUD-id é conflito. Finding referencia correção
em Task, não tem estado operacional paralelo. Em análise read-only, devolva arquivo fora do repositório.

## Gate
`gate` é avaliação local: allowed/blocked, razões e trabalho independente permitido.
Não instala CI/branch protection. Autorização fornecida por string não autentica autoridade humana.
Merge/deploy exige avaliação dos controles solicitados e snapshot compatível. Unknown não é fail,
mas pode impedir promoção que depende do controle. Alto/crítico exposto bloqueia por padrão.
No pacote inicial, aceitação de risco é registrada por schema, mas não remove bloqueios automaticamente.
Política externa mais rígida prevalece; adaptação de política exige revisão confiável fora do patch.

Commit local não exige relatório universal. Falta de documento genérico não é vulnerabilidade.
Vulnerabilidade preexistente relevante ao artefato publicado pode bloquear deploy sem impedir outras edições.
Deploy S3 exige ambiente observado e digest de configuração compatível, além de autoridade específica.
Esses campos precisam de fonte real; não preencha true por vontade de liberar.

## Reuso e limite
Arquivo inalterado não basta se helper, lockfile, policy ou ambiente relevante mudou. Monte manifesto
incluindo dependências reais. Hash não comprova drift externo nem assinatura. Evidência reaproveitada
precisa de origem explícita; nunca anuncie teste velho como reexecutado. Este runtime valida conteúdo
listado; selecionar cobertura e verificar ambiente são responsabilidades da revisão autorizada.
