# Console e decisões — contrato da rc.1

Consultar ao configurar hooks, abrir/instalar o painel, preparar uma decisão ou diagnosticar acompanhamento.

## Fronteiras

Console é interface local de acompanhamento. Sem LLM, shell da aplicação, deploy, migrations de dados, produção, editor arbitrário de PRD ou segundo banco. Hooks locais confiados podem solicitar sua abertura no início de sessão de implementação e associar workspace/Task; abertura manual continua disponível.

Catálogo local `~/.omnx-console/projects.json` distingue `workspace_id` (cópia/pasta) de `project_id` (produto). Clones e worktrees podem ter o mesmo project_id sem mesclar estado. Remover da lista não apaga arquivos. Versão exibida é comparação local; ausência de consulta remota não vira “última versão”.

A API resume projetos e pagina coleções. Bodies/histórico são carregados no detalhe. Cache usa identidade do arquivo/size/mtime/ctime; nunca autoriza escrita. Erro num item não oculta os itens válidos. Leituras incompletas mostram aviso, não contagem aparentemente completa. Estado `in_progress` não é presença da IA.

## Sessão e versão

No início de implementação, hooks confiados podem solicitar a abertura uma vez por sessão e direcionar o painel ao workspace e à Task. O retorno distingue servidor iniciado/reutilizado, navegador solicitado/indisponível e cliente conectado/não confirmado. Cliente autenticado só comprova uma conexão técnica desta máquina, não leitura humana. Sem hook instalado ou com falha de browser, o trabalho canônico continua.

O Console mostra a versão deste bundle, a versão adotada pelo projeto, candidato preparado e estado de conexão local separadamente. O modelo de skill já carregado na conversa não é observável uniformemente e deve aparecer como não confirmado; baixar/preparar um candidato não significa que a sessão o está usando.

## Única escrita pelas operações da engine

Task: estado e prioridade limitados pela autorização/dependências. O painel não conclui/cancela/reabre tarefas terminais nem concede autorização de implementação. A interface usa hash esperado e ID da tentativa; duas abas não sobrescrevem silenciosamente.

Decision: usar `decision create`, `decision show`, `decision update`, `decision revise`. Nunca editar JSON para fabricar aprovação.

## Decision schema 2

`create` aceita somente proposta pendente. Não aceita status aprovado, autoridade, data da decisão, opção selecionada ou histórico injetados. Opções têm IDs únicos. `subject_ref`, quando informado, deve existir e passar a política de path; a engine captura hash e manifesto. HTML inclui assets locais da pasta delimitada da proposta.

`read_record` calcula o hash dos mesmos bytes usados para a exibição. `update` exige esse hash. Aprovação com opções exige escolha explícita; sem arquivo, a aprovação abrange somente pergunta/opções, não uma tela imaginada. Aprovação de arquivo exige manifesto atual correspondente.

Fluxo: `pending → approved/rejected/changes_requested`; `changes_requested → revise → pending`. Estado aprovado é imutável em escolha/pergunta/feedback; uma alteração posterior requer decisão sucessora ou substituição explícita, preservando o histórico. `superseded` não desfaz trabalho nem cria aprovação nova.

Cada alteração v2 preserva o snapshot anterior com digest em `history`, dentro da mesma escrita atômica. Isso permite recuperação de contexto; **não é assinatura nem log resistente a um usuário hostil que pode regravar o arquivo inteiro**. Limite de histórico: 200 revisões; ao atingir, abrir sucessor justificado em vez de truncar.

Schema 1 da rc.1 é somente leitura/legado não verificado. `decision revise ID --expected-sha256 HASH --data NOVA_PROPOSTA.json` preserva original em `legacy_record`, recaptura sujeito e produz pendente v2. Jamais converter aprovação v1 automaticamente em aprovação v2. Se o conteúdo atual continua desejado, pedir reconfirmação escopada.

O Console permite responder somente `product`/`ux`. `risk`, `operation`, `release`, `migration` e demais tipos ficam em leitura. Autoridade local é atribuída pela sessão, não recebida do formulário. Ainda não é identidade forte. A decisão não libera publicação, não altera PRD/ADR/Task automaticamente e não desperta um agente.

Ao retomar: verificar projeto/cópia, revisão, autorização atual da Task e decisões relacionadas. Decisão aprovada de produto não equivale a compromisso de execução. Feedback não amplia escopo automaticamente. Materializar consequências somente onde aplicável e autorizado.

## API e sessão

Bind somente 127.0.0.1. Validar Host/Origin, sem CORS aberto. Pareamento de uso único via fragmento; cookie HttpOnly/SameSite Strict e CSRF para mutações. Sessão expira após oito horas, com limite de duas horas ociosa. Novas abas retomam cookie válido; links de abertura não são credenciais permanentes.

Previews usam capabilities curtas, somente leitura, ligadas a arquivos registrados e seus hashes, sem token da API. Não existe rota de “mostrar qualquer path”. Cada request de recurso revalida conteúdo. API/preview sem autorização/validade retorna falha, nunca o `.env` ou um caminho fora do escopo.

Página principal usa DOM seguro e eventos registrados, sem montar onclick com dados. Previews têm sanitização conservadora + sandbox + CSP, sem scripts/requests externos/formulários/navegação. Sanitização pode simplificar aparência; não remover proteção para preservar um widget interativo. Use screenshot ou sandbox externo confiável no fluxo do agente quando interação for necessária.

## Prompts econômicos

Padrão: intenção + IDs do projeto/cópia/Task + revisão + até 12 referências de decisão. Não copia body, feedback, critérios ou nomes de arquivos arbitrários como instruções. Autorizações propostas/terminais geram investigação, não execução. Explicar/revisar/investigar são somente leitura. Complete acrescenta orientação de leitura seletiva, não concatena PRD.

Prompt não é fonte atual nem consentimento novo. Agente local verifica cópia; remoto verifica sincronização dos artefatos antes de agir. Sem acesso, informar a lacuna. O custo de tokens surge no agente que recebe o prompt, não no Console.

## Operação e recuperação

`console open` inicia/reutiliza servidor local. `console stop` autentica a instância identificada antes de solicitar encerramento; não mata PID desconhecido. `console serve` mantém primeiro plano. `console install` copia pacote verificado para destino novo. `console shortcut` cria launcher em destino explicitamente escolhido, sem substituir arquivos existentes.

Porta indisponível, catálogo inválido, ambiente incompatível ou projeto movido não autorizam limpar arquivos. Diagnóstico é leitura. Reabrir pelo launcher resolve sessão expirada; divergência de lock exige adoção explícita, não migration automática do produto. Instalar rc.2 não atualiza contextos de agentes já em execução.
