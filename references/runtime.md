# CLI, schemas e limites mecânicos

Python 3.10+. Entrada `scripts/omnx.py`; root explícito para projeto. Sem pip; rede opcional limitada à consulta de releases depois de consentimento local.
PyYAML puro 6.0.3 está incluído com licença. Parser rejeita chaves duplicadas, aliases, tags executáveis,
profundidade/tamanho excessivo e tipos desconhecidos. Frontmatter de Task usa parser real, não regex de YAML.
Validador JSON Schema implementa o subconjunto usado pelos schemas empacotados; não é motor genérico completo.

Comandos: doctor; method verify/adopt; init (gera plano); task list/show/create/update/transition/archive;
migrate inventory/plan/apply/status/resume/rollback; audit catalog/snapshot/request/response-template/
validate-request/validate-response/persist/scan; gate; update check/plan/apply/policy/auto-check/remote-check; session save/check; hooks install/remove; model configure/choose/recommend; visual inspect; hook interno; host; verify-package.
Consulte --help do comando para flags exatas. Init e migrate plan não aplicam mudanças.

Entradas estruturadas podem ser arquivos JSON ou YAML seguro onde indicado; todas as escritas são explícitas.
Task create recebe --data e --body-file. Update/transition/archive recebem --expected-sha256.
Resposta normal: status, code, summary, changed_paths, limitations e dados pertinentes.
Saídas explicitamente pedidas com --output não sobrescrevem conteúdo diferente; escolha novo arquivo.

Exit codes: 0 sucesso; 2 entrada/schema inválido; 3 conflito/stale state; 4 capacidade/arquivo ausente;
5 política/revisão necessária; 6 execução parcial/falha de host; 7 erro local inesperado; 8 cancelamento.
Doctor pode retornar saúde needs_attention como resultado diagnóstico bem-sucedido, sem corrigir nada.

Segurança de paths: relativos POSIX, sem .., symlink, hardlink, arquivos especiais, nomes de dispositivo,
colisão de caixa em ZIP ou Unicode não normalizado. POSIX usa descritores de diretório/O_NOFOLLOW/fsync.
Windows tem caminho alternativo, mas não foi homologado em host real; veja reports/VALIDATION.md.
Locks são locais/cooperantes. Não alegar proteção contra processo hostil com acesso irrestrito ao mesmo usuário.

Schemas adicionais de release e decisão de risco são registros para integrar ao fluxo humano/CI;
não existe comando que publique, conceda exceção, rotacione segredo ou autentique consentimento por texto.
Valores de autoridade são referências, não assinatura. Campos de evidência não executam testes por si só.

Schemas de model-policy e automation-session definem mapeamento local de perfil e journal mínimo por sessão. update-policy e update-state separam consentimento de consulta/staging de uma versão ativa. Task aceita automation_ref e model_policy opcionais. Nenhum campo de perfil executa ou seleciona uma IA.

## Console e Decision rc.2

`decision list/show/create/update/revise`; `console register/projects/unregister/open/serve/stop/install/shortcut`.
Open inicia/reutiliza explicitamente servidor local; não inicia agentes. Serve fica em primeiro plano.
Decision schema 1 é leitura histórica; somente schema 2 é escrito. Criar não aprova; revise não herda aprovação.
Na API do Console, autenticação usa pareamento de uma vez + cookie/CSRF, não token em query.
Comando de adoção do pacote não migra Decision automaticamente. Veja references/console.md.
