# Perfil OMNX para image-to-html

Este adaptador integra o trabalho visual do repositório [Empire-Business/image-to-html](https://github.com/Empire-Business/image-to-html/tree/d18ba1626b23786adc44c19d58046ea6abd4758d) ao método OMNX. Revisão consultada: d18ba1626b23786adc44c19d58046ea6abd4758d; identificador real da skill no frontmatter: img-to-html. Referência consultada em 28 de setembro de 2026.

## Quando usar

Use a skill do host img-to-html em implementação visual de telas a partir de PNG. Não precisa invocá-la para ajuste pequeno de backend, correção editorial ou componente existente sem mudança visual relevante. Não solicite aprovação de cada camada técnica quando PNG, PRD, arquitetura e escopo deixam a solução clara.

## Precedência do projeto

1. Segurança, permissões e limites do ambiente continuam obrigatórios.
2. PRD/documentação funcional vigente e decisões aprovadas definem funções, rótulos oficiais, rotas, permissões e regras de negócio.
3. Arquitetura aprovada define stack, contratos e integração. O código ajuda a localizar a implementação.
4. PNG define linguagem visual: hierarquia, composição, proporções, tipografia, cor, espaçamento e aparência de componentes.

Se o PNG desenhar “Mentorias” e PRD disser “Clients”, conserve a composição visual, use o nome “Clients” e implemente a rota documentada. O desenho não cria requisito ou rota, e não é motivo para reescrever PRD. Registre divergências relevantes e como foram resolvidas.

## Fluxo integrado

1. Identifique o PNG sem enviar referência privada a serviço externo. omnx visual inspect --reference <arquivo.png> lê cabeçalho, tamanho, proporção e bytes; não analisa pixels.
2. Confirme se é viewport, captura de página inteira, recorte, zoom ou escala de exportação. A CLI informa esses atributos como desconhecidos; não infira CSS pixels pelas dimensões da imagem.
3. Leia apenas o PRD, rota, decisão, arquitetura e componentes necessários à tela.
4. Use leitura estrutural, decomposição em regiões, tokens, fontes, componentes, assets e comparação visual da referência. Reutilize logo, fontes, ícones e assets aprovados do projeto.
5. Implemente o resultado final na stack, nos componentes e nos tokens existentes. HTML intermediário pode ajudar a análise, mas não vira um frontend paralelo obrigatório.
6. Preserve hierarquia e identidade ao adaptar larguras, densidade, quebra, sidebar/header, textos longos e estados vazios/loading/erro/permissão. Não estique imagem, reduza página inteira com zoom, fixe todas as posições ou esconda conteúdo por overflow.
7. Confira os breakpoints documentados. Se não existirem, use larguras representativas 360, 390, 768, 1024, 1440 e 1920 CSS px, mais largura intermediária, alturas distintas e zoom quando pertinente. Valide teclado, foco, navegação, ação e feedback separadamente de screenshot.
8. Para cada tela afetada, mantenha vínculo curto entre arquivo PNG, requisito/rota e componente real. Compare screenshot em composição equivalente; em outros tamanhos compare hierarquia e identidade.

## Dependências e modo independente

A revisão consultada usa fluxo de estrutura → regiões → fundo → componentes/fontes → assets → integração/revisão, e produz HTML/CSS/JS estáticos quando executada de forma independente. No adaptador OMNX, a saída é incorporada na aplicação e stack existente; requisitos funcionais prevalecem ao desenho. Limites sem framework, bundler ou dev server do modo independente não são obrigações universais deste projeto.

Na revisão registrada, a referência to-wireframe não estava disponível; não a invoque nem prometa essa etapa. openrouter-img e find-font são auxiliares opcionais e não fazem parte deste fluxo. Não execute script remoto sem inspeção, não envie PNG privado a terceiro e não gere assets novamente por IA sem necessidade/autorização. Se helper estiver ausente, prossiga com análise visual e ferramentas disponíveis para a parte segura, registrando a limitação.

Este pacote atual não incluiu PNG de uma aplicação para conversão visual real. Portanto, este release documenta/testa o perfil e a inspeção de metadados; não reivindica screenshot, comparação visual ou conversão executada com img-to-html.
