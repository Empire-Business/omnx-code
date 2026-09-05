# 🖼️ Mockup-First — fluxo padrão com escolha do dono

> **Padrão recomendado:** em produto novo ou tela nova, o primeiro entregável é
> o mockup visual. **Escolha do dono:** ele pode pedir execução direta e dispensar
> o mockup para um escopo definido. A IA registra a decisão e avança sem discutir
> nem pedir nova confirmação.

## Por que esta ordem, e não a inversa

Ninguém consegue revisar um produto lendo requisitos. Um PRD de onze seções
parece certo para quem escreveu e parece certo para quem leu — até a tela
existir e a pessoa dizer "não era isso". Quando essa frase aparece depois do
PRD, do ROADMAP, do UML e do schema modelado, a correção já está espalhada por
cinco documentos e um banco. Quando aparece na tela HTML, custa apagar um
arquivo e desenhar de novo.

Tela é a única linguagem em que o dono do produto é fluente. É nela que ele
enxerga o campo que falta, o botão que não existe, o passo que está sobrando —
coisas que ele nunca vai encontrar numa lista de requisitos funcionais, porque
para achá-las ele teria que primeiro traduzir a lista em imagem mental, e essa
tradução é exatamente o trabalho que a IA está sendo paga para fazer.

O documento não perde valor nessa inversão: ganha. Ele deixa de ser uma aposta
sobre o que o produto vai ser e passa a ser a transcrição fiel de algo que já
foi visto e aceito. PRD escrito depois da tela aprovada é PRD que não precisa
de segunda rodada.

Esta escolha flexibiliza somente o processo de validação visual. Segurança,
migrations, RLS, isolamento multi-tenant, UML aplicável, testes e autorização
para publicar continuam sujeitos às suas próprias regras.

---

## Quando o fluxo padrão se aplica

Na ausência de uma escolha explícita, use mockup-first antes de documentos e
código da interface. Uma dispensa explícita remove esse bloqueio somente para o
escopo citado.

| Situação | Mockup primeiro? |
|----------|------------------|
| Projeto novo, do zero | Sim por padrão; dispensável pelo dono |
| Projeto existente, tela ou feature nova com UI | Sim por padrão no escopo afetado; dispensável pelo dono |
| Mudança visível numa tela já aprovada (campo novo, coluna nova, passo novo no fluxo) | Versão leve por padrão; dispensável pelo dono |
| Correção de bug, refactor, migration, ajuste de copy/estilo, performance | Não. Siga o Modo de Trabalho Normal direto |
| Script interno, job de background, CLI, integração sem tela | Não. Não há o que visualizar |

## Procedimento

1. Verifique se o dono pediu modo direto ou dispensou o mockup para o escopo.
2. Sem dispensa, rode o fluxo visual e registre a aprovação.
3. Com dispensa, explique o trade-off em uma frase, registre a fala literal,
   data, escopo e etapas dispensadas, e avance sem nova confirmação.
4. Mantenha os documentos técnicos sincronizados com o que for implementado.
5. Nunca presuma que uma dispensa vale para outra feature ou projeto.

## Uma única árvore de mockups

Todo projeto usa somente `docs/mockups/`; versões nunca criam pastas irmãs.

- Raiz de `docs/mockups/`: somente telas oficiais e aprovadas, com o
  `index.html` que o usuário abre para ver o que vale.
- `docs/mockups/em-aprovacao/<lote>/`: telas candidatas ainda sem aprovação.
- `docs/mockups/historico/<versao>-<apelido>/`: versões substituídas, rejeitadas
  ou exploratórias, sempre marcadas “NÃO IMPLEMENTAR”.

São proibidos nomes como `docs/mockups-v2/`, `docs/mockups-final/` e
`docs/novo-mockup/`. Se um projeto antigo já os tiver, consolide-os em
`historico/`, preserve os arquivos, corrija referências e mantenha um índice
que deixe inequívoco o que é oficial, o que aguarda aprovação e o que é apenas
histórico. Nenhuma versão é apagada sem pedido explícito do usuário.

## O que conta como aprovação

Aprovação é uma **frase do usuário**, nunca uma inferência da IA. "Ok",
"legal", "entendi" em contexto ambíguo não aprovam oito telas. O que conta:

- O usuário abriu os mockups (ou disse que abriu) e disse explicitamente que
  estão aprovados — no todo ou tela por tela.
- Cada tela tem status `aprovada` registrado em `docs/mockups/APROVACAO.md`,
  com data/hora BRT.
- Se ele aprovou com ressalvas ("aprovado, mas troca o rótulo desse botão"),
  as ressalvas viram tasks e ficam registradas junto — não somem na conversa.
- Quando houver muitas telas, a apresentação e a aprovação são divididas
  preferencialmente em lotes coesos de **3 a 4 telas**. Aprovação de um lote
  não é invalidada por mudança posterior fora dele; só reabre a tela alterada
  e as dependências compartilhadas realmente afetadas.

## Projeto que já tem PRD/UML aprovados

Mockup-first **não é licença para contradizer a fundação existente**. A tela
nova respeita o que já está documentado e aprovado. Se ela exigir mudar o PRD,
sincronize a mudança no mesmo commit. No modo padrão isso acontece depois da
aprovação da tela; no modo direto, sem essa espera visual.

## Escolha explícita e registrada

Se o usuário disser claramente que quer documento ou código antes das telas,
que “não precisa de mockup” ou que quer “ir direto”, respeite: o produto é dele.
Registre a dispensa em `docs/mockups/APROVACAO.md`; se a pasta não existir, use
`docs/handoffs/HISTORY.md`.

Dispensa não pedida não existe. No silêncio, telas primeiro. Dispensa pedida
não exige confirmação adicional e não pode ser transformada em novo gate.

## Anti-teatro

- Mockup gerado e nunca aberto pelo usuário **não cumpre** este gate. O ponto
  não é o arquivo existir, é a pessoa ter visto.
- Uma tela só com título e placeholder ("aqui vai a lista de clientes") não é
  mockup: não dá para aprovar o que não está desenhado. Conteúdo realista do
  domínio, estados vazios/erro/carregando, e links que funcionam.
- `APROVACAO.md` preenchido pela IA sem uma fala correspondente do usuário é
  falsificação de aprovação — o registro tem que citar o que ele disse.
