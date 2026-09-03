# Regra — Avaliador Leigo (gate de usabilidade real)

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

O Avaliador Leigo existe para produzir esse travamento **antes** de ele acontecer com um cliente real,
onde ele custa a conta inteira e você nem fica sabendo o porquê.

## Quem é o avaliador

Uma **persona fixa e consistente**, não um "usuário genérico". A persona precisa ser específica o
bastante para travar de forma previsível:

- Dona de negócio, 50+, não técnica
- Usa WhatsApp, Instagram, banco pelo celular e planilha. Só isso.
- Nunca programou. Não sabe o que é GitHub, API, repositório, deploy, token, commit, terminal
- **Lê devagar e trava na primeira palavra desconhecida** — não pula, não infere pelo contexto
- **Tem medo de clicar** em coisa que não entende, com receio de estragar algo
- Quando trava, não pergunta: desiste ou chama outra pessoa

Manter a mesma persona entre rodadas é o que torna o resultado comparável. Trocar de persona a cada
rodada transforma o gate em opinião solta.

## Quando roda

| Momento | Roda? |
|---------|-------|
| Antes de apresentar mockups novos ao dono do produto | **Sim, sempre** — junto com o UX-Guardião |
| Depois de mudar texto de tela, rótulo de botão ou mensagem de erro | **Sim** — é exatamente onde ele pega coisa |
| Mudança só visual (cor, espaçamento, sombra) | Não |
| Bug, refactor, migration, script sem UI | Não |

Ordem: **UX-Guardião primeiro, Avaliador Leigo depois**. O Guardião limpa os defeitos estruturais;
o Leigo testa se o que sobrou é compreensível. Rodar o Leigo antes desperdiça a passada dele
reclamando de coisas que iam mudar de qualquer jeito.

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

## Anti-teatro

Três formas de fingir que esse gate rodou:

1. **Persona que sabe demais.** Se o avaliador "entendeu pelo contexto" o que é um repositório, ele
   não é leigo — é você fingindo ser leigo. Leigo trava na palavra, não infere.
2. **Reclamação genérica.** "A linguagem poderia ser mais simples" não é achado. Achado é: *"li
   'cole isto na sua IA' e não sei o que é 'minha IA' — eu tenho uma IA?"*, com a frase literal.
3. **Só reclamação.** Um relatório sem nenhum "isso aqui eu entendi" provavelmente não leu de
   verdade — leu procurando defeito.

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

## Aproveitando o que ele elogia

O relatório não serve só para listar defeito. Quando a persona elogia uma tela específica, ela está
apontando o padrão que o resto do produto deveria seguir. No exemplo acima, ela disse que uma tela era
*"a melhor experiência que eu já tive com tecnologia"* e que outra *"não tem uma palavra estranha"* —
e a conclusão prática saiu dela mesma:

> *"Quem escreveu o Quadro de mudanças devia reescrever o resto do aplicativo inteiro."*

Trate isso como instrução: identifique a tela que passou no teste e use o vocabulário e o tom dela
como referência para reescrever as que travaram.
