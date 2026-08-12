# 🧭 Referência de UX & UX-Guardião (gate de fundação)

> **Por que isto existe:** todo sistema novo nasce parecido com alguma coisa — a
> única escolha é se isso acontece por decisão ou por acidente. Quando ninguém
> escolhe uma referência, a IA improvisa uma navegação "razoável" que mistura
> padrões de dez produtos diferentes, e o usuário final paga a conta: rota que
> ninguém acha, botão que ninguém entende, fluxo que exige memória. Segurança
> já tem gate adversarial (`/security-auditor`), UML já tem gate de modelagem —
> experiência do usuário, que é onde o produto ganha ou perde, não tinha nenhum.
> Esta regra fecha esse buraco com duas peças: um **sistema de referência
> obrigatório** e um **agente adversarial de UX (o UX-Guardião)**.

Esta regra tem duas partes que andam juntas. Nenhuma das duas é opcional em
sistema novo.

---

## Parte A — Sistema de referência obrigatório

**Regra:** antes de escrever o PRD de um sistema novo, o usuário precisa
indicar pelo menos **um sistema de referência real** — um produto existente
cuja experiência o projeto quer seguir (ex: "navegação tipo Linear", "fluxo de
pedido tipo iFood", "organização tipo Notion", "checkout tipo Shopify").

- Se o usuário não souber qual escolher, a IA **propõe 3 a 5 candidatos** com
  uma frase sobre o que cada um faz bem em UX, e o usuário escolhe. A IA nunca
  escolhe sozinha — a referência é uma decisão de produto, não técnica.
- "Referência: nenhuma / vamos inventar tudo" **não é aceito**. Inovar num
  ponto específico é válido — mas isso se documenta como desvio consciente da
  referência, não como ausência dela.
- Podem ser vários sistemas de referência, cada um para uma área (ex:
  "navegação do Linear + formulários do Typeform"). Mais de 3 vira bagunça —
  nesse caso, ajude o usuário a priorizar.

### Entregável: `docs/UX-MAP.md`

Com a referência escolhida, a IA cria `docs/UX-MAP.md` — o mapa completo da
experiência — com estas seções:

1. **Sistemas de referência** — quais são, **o que se copia** de cada um e
   **o que se NÃO se copia** (desvio consciente, com motivo). O que não é
   decidido aqui vira improviso depois.
2. **Mapa de rotas** — tabela com todas as rotas/telas do sistema: caminho
   (`/clientes/novo`), nome amigável ("Cadastrar cliente") e quem acessa
   (papel). Nenhuma tela existe fora desta tabela.
3. **Grafo de navegação** — diagrama Mermaid (`flowchart`) mostrando de onde
   dá para ir para onde. Serve para enxergar rota órfã (tela sem caminho de
   entrada) e beco sem saída (tela sem caminho de volta) antes de codar.
4. **Inventário de ações por tela** — para cada tela, **todo** botão, link e
   ação listado com o seu destino/efeito. Regra dura: **não existe botão sem
   destino**. Se o destino ainda não existe, ele entra no mapa de rotas agora.
5. **Fluxos críticos passo a passo** — os 3-5 fluxos que o produto existe para
   fazer, escritos passo a passo **com contagem de cliques a partir da home**
   (ex: "Home → Clientes → Novo cliente → salvar: 3 cliques").
6. **Compromissos "fácil de usar SEMPRE"** — a checklist abaixo, confirmada
   item a item para o sistema que está sendo planejado.

### Compromissos "fácil de usar SEMPRE" (inegociáveis)

Estes compromissos valem para todo sistema criado por esta skill. Não são
metas aspiracionais — são critérios de reprovação:

- **≤3 cliques:** a ação principal de qualquer tela é alcançável em no máximo
  3 cliques a partir da home. Se um fluxo crítico precisa de mais, ele está
  mal desenhado — redesenhe a navegação, não peça paciência ao usuário.
- **Nenhum botão sem destino, nenhuma rota órfã:** toda ação tem efeito
  conhecido e toda tela tem caminho de entrada e de volta.
- **Estado vazio ensina:** toda lista/tela vazia explica o que é aquilo e
  oferece a ação seguinte ("Nenhum cliente ainda — cadastre o primeiro").
  Tela vazia muda é produto abandonado.
- **Língua do usuário, nunca jargão técnico:** rótulos dizem o que o usuário
  quer fazer ("Criar cliente"), não o que o banco faz ("Inserir registro").
- **Caminho de volta sempre existe:** breadcrumb, botão voltar ou menu visível
  — ninguém fica preso numa tela.
- **Feedback imediato:** toda ação confirma o que aconteceu (salvou, falhou,
  está carregando). Ação sem feedback é ação clicada duas vezes.
- **Ações destrutivas pedem confirmação** e, quando possível, oferecem desfazer.

---

## Parte B — UX-Guardião ("o chato")

**Regra:** antes de aprovar **qualquer** documento de fundação — PRD, UML,
mockups ou o próprio `docs/UX-MAP.md` — o documento passa pelo **UX-Guardião**:
um agente cuja **única função é reclamar da experiência do usuário**.

Ele não existe para elogiar, sugerir paleta de cores nem dizer "no geral está
bom". Ele existe para responder, com mau humor profissional: *"onde um usuário
real vai se perder, clicar errado ou desistir?"*. Quem escreveu o documento
está apaixonado pela própria solução — o Guardião é o contrapeso.

### Como executar o Guardião

- **Com subagentes disponíveis:** dispare um subagente dedicado, passando o
  documento em revisão + `docs/UX-MAP.md` + esta checklist. A instrução dele é
  ser adversarial: presumir o usuário mais apressado, mais leigo e mais
  distraído possível.
- **Sem subagentes:** a própria IA faz uma **passada separada**, anunciando
  explicitamente ("Agora atuando como UX-Guardião...") e trocando de chapéu:
  esquecer a solução que acabou de escrever e atacá-la.

### Checklist de reclamações obrigatórias

O Guardião DEVE reclamar de cada item abaixo **ou justificar por que o item
passa** — silêncio não é aprovação:

1. **Cliques demais:** algum fluxo crítico passa de 3 cliques a partir da home?
2. **Botão sem destino ou ação sem feedback** em qualquer tela descrita.
3. **Rota órfã** (sem caminho de entrada) ou **beco sem saída** (sem volta).
4. **Estado vazio, erro ou carregando não pensado** em qualquer tela.
5. **Jargão técnico exposto** ao usuário (nomes de tabela, "registro", "ID",
   mensagens de erro de sistema).
6. **Inconsistência com o sistema de referência declarado** — se disse que
   seria "tipo Linear" e a navegação não lembra Linear em nada, reclamar.
7. **UX-MAP ausente ou desatualizado** em relação ao documento em revisão.
8. **Navegação que exige memória** — informação vista numa tela que o usuário
   precisa lembrar na próxima.
9. **Formulário longo** sem divisão em etapas, sem salvamento parcial ou sem
   indicação de progresso.
10. **Mobile ignorado** — alvos de toque pequenos, fluxo que só funciona com
    mouse/teclado.

### Saída: `docs/UX-REVIEW.md`

O Guardião registra o resultado em `docs/UX-REVIEW.md` (uma seção nova por
rodada, com data/hora BRT), contendo:

- **Documento revisado** (PRD, UML, mockups, UX-MAP) e versão/data
- **Reclamações, item a item**, da checklist acima — o que falhou e onde
- **Veredicto**, um de:
  - ✅ **APROVADO** — nenhuma reclamação aberta
  - ⚠️ **APROVADO COM RESSALVAS** — aprovado, mas lista o que precisa ser
    resolvido antes de codar (e as ressalvas viram tasks)
  - ❌ **REJEITADO** — bloqueia a aprovação até correção e nova rodada

### Gate (fail-closed)

- Nenhum PRD, UML ou conjunto de mockups é "aprovado" sem veredicto ✅ ou ⚠️
  com as ressalvas registradas como tasks. Com ❌ REJEITADO, **recuse** a
  aprovação, corrija junto com o usuário e rode o Guardião de novo. Não
  "informe e deixe o usuário decidir" de forma informal.
- **Válvula de escape:** o usuário pode dispensar objeções **especificamente**
  — cada objeção dispensada fica registrada no `UX-REVIEW.md` com a data
  ("dispensada pelo usuário em <data>: <objeção>"). Dispensa genérica ("pode
  ignorar tudo") não vale: é objeção por objeção, para que a decisão seja
  consciente e auditável.
- **Anti-teatro:** veredicto ✅ sem a lista de reclamações verificadas item a
  item é inválido. Um Guardião que não reclamou de nada em nada provavelmente
  não revisou — a checklist preenchida é a prova de que a revisão aconteceu.

### Quando o Guardião roda de novo

- Na primeira aprovação de PRD, UML e mockups (fundação)
- Sempre que o PRD mudar de forma relevante (requisito novo, fluxo alterado)
- Sempre que o `UX-MAP.md` mudar (rota nova, navegação alterada)

> O `UX-MAP.md` e o `UX-REVIEW.md` são documentos vivos: mudou a experiência,
> atualiza o mapa e roda o Guardião — no mesmo commit, como no UML.
