# UX: decidir, não manter um espelho

Uma tela entregue pode mudar sem reabrir mockup. UX0/UX1 não exige sincronização histórica nem uma
aprovação para cada pixel. Se há padrão aprovado e requisitos claros, implemente o delta e valide o resultado.

Em UX2/UX3, responda qual decisão ainda falta. Escolha o artefato mais barato que esclarece essa decisão:
preview isolado, componente, Storybook, telas existentes anotadas, protótipo navegável ou mockup específico.
Não criar dois frontends só para satisfazer um nome. Produto sem interface não precisa de tela.
Pedido PRD-first prevalece sobre preferência de fluxo: marque incertezas pertinentes, prossiga no independente.

Proposta histórica em docs/ux/proposals/UX-id. Registre revisão, escopo e origem da aprovação material.
Não invente mockup_approved global. Se o delta muda consequência/interação aprovada, valide esse delta;
correção editorial não invalida toda aprovação anterior. Aprovação não autoriza deploy/dados/custo.

## Dona Maria
Simule a tarefa do público escolhido: onde começa, o que entende, qual ação escolhe, que feedback recebe.
Achado: tarefa, elemento/frase exato, interpretação possível, consequência, sugestão e severidade.
É hipótese de inspeção, não observação de usuário real. Não obrigar achado novo, surpresa ou nota.
Para usuário especialista, persona adequada em vez de leiga irrelevante. Interface interna também pode
ser usada por leigos; público importa mais que exposição pública.

## Guardião
Confira encontrabilidade, hierarquia, termos, estados vazio/loading/erro, confirmação de efeitos,
recuperação, teclado/foco, contraste e comportamento responsivo conforme delta. Três cliques não é lei.
Uma inicial + até duas revisões corretivas. Sem informação nova, mostre conflito/alternativas ao dono.
Rascunho pode ser mostrado cedo; divergência de revisores não bloqueia feedback.

Sem browser: declare ausência de verificação visual/interativa. Screenshot não comprova jornada;
inspeção de código não comprova clique. Não instalar nova infraestrutura sem autorização para fingir teste.

No Console, a aprovação canônica fica em Decision v2, não em outro APPROVAL.md editável.
Um Markdown da proposta pode apontar ao DEC sem duplicar resultado/autoridade.
Aprovação de arquivo se vincula ao manifesto capturado, incluindo CSS/imagens locais pertinentes.
Previews do Console são estáticos: não use essa visualização como evidência de jornada interativa.

## PNG e contrato funcional

Mockups oficiais novos usam PNG. Preserve outros formatos e aprovações históricas; backend, mudança pequena e correção não exigem mockup novo.

Para tela afetada, relacione o arquivo de referência a requisito/rota do PRD e componente real. Segurança e permissões prevalecem; PRD e decisões aprovadas definem função, rótulo, rota e regra de negócio; arquitetura define stack/contrato; PNG orienta identidade e aparência. Se o desenho usar nome diferente, mantenha o nome e rota documentados, adaptando a composição sem inventar produto.

Registre dimensões e proporção da imagem, mas trate recorte, página inteira, zoom, escala exportada e viewport CSS como desconhecidos até haver evidência. Em ausência de breakpoints do produto, confira 360, 390, 768, 1024, 1440 e 1920 CSS px e larguras intermediárias, alturas distintas e zoom quando útil. Considere sidebar/header, densidade, textos longos, estados e controles reais. Preserve hierarquia ao reorganizar em telas menores. Não comprima a tela toda, estique screenshot, fixe tudo ou oculte conteúdo por overflow. Consulte adapters/image-to-html.md.
