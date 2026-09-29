# Política de modelo por tarefa

Carregar ao escolher ou registrar perfil de modelo. A política é local ao projeto, determinística e sem chamadas a modelos.

## Perfis

| Perfil | Quando usar | Trabalho típico |
|---|---|---|
| deterministic | Sem raciocínio necessário e verificação mecânica disponível | Busca exata, inventário, checksum, schema, lint, formatação e testes |
| economical | Escopo claro, baixo risco e resultado objetivamente verificável | Mudança simples com teste determinístico |
| balanced | Implementação comum, investigação moderada ou integração delimitada | Manutenção multi-arquivo e análise com evidência suficiente |
| advanced | Risco alto/crítico, ambiguidade importante ou julgamento difícil | Autenticação, autorização, isolamento, migração, falha sistêmica e revisão crítica |

Use menor custo esperado para concluir corretamente. Tamanho do diff não determina risco. Não faça várias tentativas econômicas depois de falha objetiva ou repetição sem progresso quando uma análise avançada é justificável.

## Configurar e consultar

Os mapeamentos opcionais ficam em .omnx/local/model-policy.json. Configure IDs conhecidos pelo host, sem fixar uma lista global de modelos ou preços:

~~~sh
python3 <skill>/scripts/omnx.py --root <projeto> model configure economical \
  --model <id-do-host> --effort low
python3 <skill>/scripts/omnx.py --root <projeto> model choose \
  --risk low --ambiguity low --verification objective
python3 <skill>/scripts/omnx.py --root <projeto> model recommend \
  --task-id TASK-<id> --ambiguity medium --verification objective
~~~

model choose e model recommend são recomendações locais. A sessão pode herdar modelo, esforço ou política de uma configuração superior. Os hooks capturam o modelo efetivo somente quando o payload real do host o expõe. Nenhuma troca dinâmica de modelo/esforço é alegada; o host precisa aplicar a seleção explicitamente. Os payloads atuais não confirmam esforço efetivo.

## Registro e limites

Uma Task pode conter perfil, modelo/esforço solicitados, modelo efetivo quando observado, razão e status de custo. Custo permanece desconhecido até existir medição confiável; não se calcula preço ou economia a partir de caracteres. Configurar nome não prova que o host reconhece, permite ou usou o modelo. Não guarde chave de API nesta política.

A classificação automática inicial usa regras locais conservadoras sobre risco textual e clareza. Reavalie risco, necessidade de visão/ferramentas, contexto, orçamento, verificabilidade e precedência do host no começo de cada tarefa/subobjetivo relevante. Se indisponível ou incompatível, registre como não confirmado e prossiga com um modelo autorizado pelo host. Uma seleção do perfil não concede permissões operacionais.
