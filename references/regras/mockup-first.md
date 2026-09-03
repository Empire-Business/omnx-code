# 🖼️ Mockup-First — a pessoa VISUALIZA antes de qualquer documento

> **Regra:** em qualquer pedido de produto — sistema novo do zero ou tela nova
> em projeto que já existe — o primeiro entregável é o **mockup visual das
> telas**, aberto no navegador e aprovado pelo dono do produto. Só depois nasce
> PRD, ROADMAP, ARQUITETURA, UML, UX-MAP ou qualquer linha de código.

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

**Isso não afrouxa nenhum gate.** PRD, UML, UX-MAP, níveis de acesso, sistema
de tickets e segurança continuam todos obrigatórios, com o mesmo rigor. Só
muda a ordem: eles passam a ser escritos **a partir** das telas aprovadas, em
vez de as telas serem desenhadas a partir deles.

---

## O que o gate trava

Escrever ou aprovar `docs/PRD.md`, `docs/ROADMAP.md`, `docs/ARQUITETURA.md`,
`docs/UML.md`, `docs/UX-MAP.md` ou qualquer código de produto **de uma tela que
o usuário ainda não viu e aprovou**.

| Situação | Mockup primeiro? |
|----------|------------------|
| Projeto novo, do zero | **Sim, sempre.** O primeiro entregável da fundação é `docs/mockups/`, não o PRD |
| Projeto existente, tela ou feature nova com UI | **Sim.** Mockupe só a(s) tela(s) nova(s) e os pontos de entrada afetados — não o app inteiro |
| Mudança visível numa tela já aprovada (campo novo, coluna nova, passo novo no fluxo) | **Sim, versão leve.** Atualize o HTML daquela tela e mostre antes de codar |
| Correção de bug, refactor, migration, ajuste de copy/estilo, performance | Não. Siga o Modo de Trabalho Normal direto |
| Script interno, job de background, CLI, integração sem tela | Não. Não há o que visualizar |

## Procedimento (fail-closed)

1. Antes de criar/editar documento de fundação ou codar tela nova, verifique se
   existe `docs/mockups/APROVACAO.md` com aprovação **explícita** do usuário
   cobrindo as telas em questão.
2. Se não existe, ou existe mas não cobre a tela nova: **pare e rode o fluxo de
   mockups** da skill `omnx-code`. Não escreva "só um rascunho do PRD enquanto
   isso" — rascunho vira âncora, e a partir daí o mockup passa a servir o
   documento em vez do contrário. A regra se inverte sozinha por esse caminho.
3. Só depois da aprovação registrada, siga para PRD → ROADMAP → ARQUITETURA →
   UML → código, cada documento descrevendo o que as telas aprovadas mostram.
4. Se as telas mudarem numa revisão posterior, os documentos que descrevem
   aquelas telas são atualizados **no mesmo commit** — tela e documento nunca
   divergem.

## O que conta como aprovação

Aprovação é uma **frase do usuário**, nunca uma inferência da IA. "Ok",
"legal", "entendi" em contexto ambíguo não aprovam oito telas. O que conta:

- O usuário abriu os mockups (ou disse que abriu) e disse explicitamente que
  estão aprovados — no todo ou tela por tela.
- Cada tela tem status `aprovada` registrado em `docs/mockups/APROVACAO.md`,
  com data/hora BRT.
- Se ele aprovou com ressalvas ("aprovado, mas troca o rótulo desse botão"),
  as ressalvas viram tasks e ficam registradas junto — não somem na conversa.

## Projeto que já tem PRD/UML aprovados

Mockup-first **não é licença para contradizer a fundação existente**. A tela
nova respeita o que já está documentado e aprovado. Se ela exigir mudar o PRD
(requisito novo, regra de negócio diferente), a mudança do PRD acontece
**depois** da aprovação da tela, no mesmo commit da tela — e o UX-Guardião
revalida, porque fluxo mudou.

## Válvula de escape (explícita e registrada)

Se o usuário disser claramente que quer o documento antes das telas ("já sei
exatamente o que quero, escreve o PRD primeiro"), respeite: o produto é dele.
Mas antes explique em **uma frase** o que ele está trocando, e registre a
dispensa em `docs/mockups/APROVACAO.md` com data e o que foi dispensado.

Dispensa não pedida não existe. No silêncio, telas primeiro.

## Anti-teatro

- Mockup gerado e nunca aberto pelo usuário **não cumpre** este gate. O ponto
  não é o arquivo existir, é a pessoa ter visto.
- Uma tela só com título e placeholder ("aqui vai a lista de clientes") não é
  mockup: não dá para aprovar o que não está desenhado. Conteúdo realista do
  domínio, estados vazios/erro/carregando, e links que funcionam.
- `APROVACAO.md` preenchido pela IA sem uma fala correspondente do usuário é
  falsificação de aprovação — o registro tem que citar o que ele disse.
