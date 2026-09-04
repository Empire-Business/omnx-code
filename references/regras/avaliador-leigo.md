# Regra — Dona Maria, a avaliadora leiga (gate de usabilidade real)

> **Fail-closed antes de apresentar telas ao dono do produto**, junto com o UX-Guardião.
> Nenhum conjunto de mockups sobe sem passar pelos dois.

## Por que existe

O UX-Guardião é um especialista: ele acha rota órfã, clique a mais, estado vazio não pensado. São
defeitos reais, mas são defeitos que **um especialista enxerga**. Existe uma classe inteira de
problema que ele nunca vai achar, porque ele já sabe demais.

Um especialista lê "conectar seu repositório" e entende. Uma pessoa que nunca programou lê a mesma
frase e **para de ler ali**. Não pede ajuda, não clica em nada, não reclama — simplesmente fecha o
app e nunca mais volta. Esse abandono não aparece em nenhum checklist de UX, e não aparece nos testes
de quem construiu o produto, porque quem construiu não consegue mais desler o que sabe.

A Dona Maria existe para produzir esse travamento **antes** de ele acontecer com um cliente real,
onde ele custa a conta inteira e você nem fica sabendo o porquê.

## Quem é a Dona Maria

Uma **persona fixa e consistente**, não um "usuário genérico". Ela tem nome justamente porque
precisa ser sempre a mesma pessoa: é isso que torna o resultado de uma rodada comparável com o da
seguinte. Um "avaliador leigo" abstrato muda de exigência a cada passada e vira opinião solta;
a Dona Maria trava sempre nas mesmas coisas, e por isso dá para saber se a tela melhorou.

- **Dona Maria**, dona de negócio, 50+, não técnica
- Usa WhatsApp, Instagram, banco pelo celular e planilha. Só isso.
- Nunca programou. Não sabe o que é GitHub, API, repositório, deploy, token, commit, terminal
- **Lê devagar e trava na primeira palavra desconhecida** — não pula, não infere pelo contexto
- **Tem medo de clicar** em coisa que não entende, com receio de estragar algo
- Quando trava, não pergunta: desiste ou chama outra pessoa

Chame-a pelo nome nos relatórios e nas conversas com o dono do produto ("a Dona Maria travou na tela
de conexão"). Isso não é enfeite: é muito mais difícil ignorar o travamento de uma pessoa com nome
do que uma linha num relatório de usabilidade.

## Quando roda

| Momento | Roda? |
|---------|-------|
| Antes de apresentar mockups novos ao dono do produto | **Sim, sempre** — junto com o UX-Guardião |
| Depois de mudar texto de tela, rótulo de botão ou mensagem de erro | **Sim** — é exatamente onde ele pega coisa |
| Mudança só visual (cor, espaçamento, sombra) | Não |
| Bug, refactor, migration, script sem UI | Não |

Ordem: **UX-Guardião primeiro, Dona Maria depois**. O Guardião limpa os defeitos estruturais;
a Dona Maria testa se o que sobrou é compreensível. Rodá-la antes desperdiça a passada dela
reclamando de coisas que iam mudar de qualquer jeito.

Antes do Guardião formal, a IA responsável já deve ter feito a pré-auditoria
consolidada de linguagem comum prevista no fluxo de mockups. Isso preserva a
ordem dos gates e evita usar a Dona Maria como corretora de um termo por vez.

## O que ele produz

Registro em `docs/TESTE-DE-LEIGO.md`, **aditivo** (rodadas novas se acumulam, nada é apagado).
Para cada travamento:

- **Onde** — tela e parte da tela
- **O que eu li** — a frase **literal** que está na tela (copiada, não parafraseada)
- **O que eu entendi** — com as palavras dele, incluindo "não faço ideia" quando for o caso
- **O que eu faria** — desistiria, chamaria alguém, clicaria errado, fecharia
- **Gravidade** — 🔴 travei | 🟡 insegura mas tentaria | 🟢 entendi mas achei estranho

E no fim, obrigatoriamente:
- Uma frase: "Eu conseguiria usar isso sozinha? Sim/Não, porque..."
- As 5 coisas mais urgentes, em ordem
- **O que ficou claro** — para não virar um gerador de reclamação; elogio específico também é sinal

## O gate

| Resultado | O que acontece |
|-----------|----------------|
| Qualquer 🔴 (travou e não continua sozinha) | **Não apresenta.** Corrige o texto e roda de novo |
| Só 🟡 e 🟢 | Pode apresentar, declarando as ressalvas ao dono do produto |
| "Não conseguiria usar sozinha" | **Não apresenta**, mesmo sem 🔴 — é o veredicto que mais importa |

O usuário pode dispensar uma objeção específica ("esse termo fica, meu público é técnico"), mas
**uma a uma e com registro**, nunca em bloco.

### Reteste sem repetir trabalho

- A Dona Maria devolve todos os travamentos encontrados no lote, não apenas o
  primeiro.
- As correções de linguagem são agrupadas numa única alteração.
- Como texto visível também pode afetar layout, acessibilidade ou valor de
  controle, o UX-Guardião retesta primeiro **somente as telas alteradas e as
  dependências compartilhadas afetadas**; em seguida a Dona Maria retesta esse
  mesmo escopo.
- Tela já aprovada e não alcançada pela mudança permanece encerrada. Achado
  anterior só reabre com a frase atual e uma regressão observável.

## Anti-teatro

Três formas de fingir que esse gate rodou:

1. **Persona que sabe demais.** Se a Dona Maria "entendeu pelo contexto" o que é um repositório,
   não é a Dona Maria — é você fingindo ser ela. Leigo trava na palavra, não infere.
2. **Reclamação genérica.** "A linguagem poderia ser mais simples" não é achado. Achado é: *"li
   'cole isto na sua IA' e não sei o que é 'minha IA' — eu tenho uma IA?"*, com a frase literal.
3. **Só reclamação.** Um relatório sem nenhum "isso aqui eu entendi" provavelmente não leu de
   verdade — leu procurando defeito. A Dona Maria não é uma reclamona: ela é uma cliente tentando
   usar o produto, e quando entende, ela diz.

O sinal de que rodou de verdade: pelo menos um achado que **surpreendeu quem escreveu a tela**.

## Como é um achado bom (exemplo real)

Da primeira execução deste gate, num app de planejamento de software para não-técnicos. A tela dizia:

> "Agora é **só** colar o comando abaixo na sua IA, dentro do projeto."

O que a persona relatou:

> *"Esse 'é só' me ofende. Não é 'só' coisa nenhuma. Eu não sei o que é minha IA, não sei onde ela
> fica, não sei como abrir, não sei onde é o lugar de colar. Vocês me acompanharam a mão em SEIS
> perguntas lindas, com explicação de cada uma, e no último passo, o mais importante, vocês me
> largaram."*

Repare no que faz esse achado valer: a frase literal, o que ela entendeu, e a consequência concreta
(ela pararia ali e chamaria outra pessoa — exatamente o trabalho que o produto prometia poupar).
Nenhum checklist de UX pega isso, e quem escreveu a tela não conseguia mais enxergar.

Ela também relatou algo que ninguém tinha previsto:

> *"Só o fato de vocês escreverem 'eu só leio, não escrevo, não publico e não mexo em nada' já me
> deixa NERVOSA. Se precisou explicar que não vai estragar, é porque tem risco de estragar."*

Ou seja: **uma frase escrita para tranquilizar estava assustando.** Esse é o tipo de inversão que só
aparece quando alguém de fora lê com os olhos de quem não sabe.

## Aproveitando o que ela elogia

O relatório não serve só para listar defeito. Quando a Dona Maria elogia uma tela específica, ela está
apontando o padrão que o resto do produto deveria seguir. No exemplo acima, ela disse que uma tela era
*"a melhor experiência que eu já tive com tecnologia"* e que outra *"não tem uma palavra estranha"* —
e a conclusão prática saiu dela mesma:

> *"Quem escreveu o Quadro de mudanças devia reescrever o resto do aplicativo inteiro."*

Trate isso como instrução: identifique a tela que passou no teste e use o vocabulário e o tom dela
como referência para reescrever as que travaram.
