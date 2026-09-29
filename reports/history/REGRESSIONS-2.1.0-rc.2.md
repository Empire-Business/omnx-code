# Falhas conhecidas da rc.1 — correções verificáveis

| ID anterior | Correção | Evidência de regressão |
|---|---|---|
| R01 — inicialização interrompida | Coleção de elementos + binding seguro; interface reescrita com DOM | Assets test + B01/B02 no ensaio DOM |
| R02 — opção aprovada mutável | Estado aprovado imutável, histórico, CAS | DecisionHardening.test_R02_approved_choice_immutable |
| R03 — criar já aprovado | Allowlist de proposta, create apenas pending | test_R03_create_cannot_approve/forge_actor |
| R04 — hash ausente pulava conferência | Hash/manifesto capturados; mudanças de arquivo/assets bloqueiam | test_R04_missing_hash_is_captured + subject/css tests |
| R05 — uma Task inválida ocultava todas | Leitura por objeto, erros explícitos, preservação de itens válidos | test_R05_one_bad_task_does_not_hide_valid + B03 |
| R06 — clone substituía entrada | workspace_id por cópia separado de project_id | test_R06_clones_remain_distinct + B01 |
| R07 — rota podia servir .env | Rota removida, ID registrado/capability por manifesto | HTTPHardening.test_R07_* + grant/path tests |
| R08 — bloqueados sumiam | Sete colunas, contagens e paginação | test_R08_blocked_in_counts_and_rows + B02/B11 |
| R09 — nome virava JavaScript | textContent/addEventListener; nenhum onclick interpolado | Assets test + B04/B06 |
| R10 — prompt gigante/credencial | Referências/identidades/intenções, sem body concatenado | test_R10_prompt_bounded_no_bodies + B05 + scale |
| R11 — releitura dupla em cada atualização | Cache por metadados, coleções compactas, detalhes sob demanda | test_R11_unchanged_refresh_no_metadata_read + scale |
| R12 — texto/hash de leituras diferentes | Hash calculado dos mesmos bytes + CAS | test_R12_* + B08/B09 |

Além dessas falhas: testes de concorrência, idempotência, CSRF, Host/Origin, expiração, tipo de decisão, saída parcial, schema futuro, abertura/reuso/encerramento em processos Linux e recuperação de migração.

Os testes DOM usam transporte simulado e engine real de fixtures. Testes HTTP usam servidor real com cliente Python. Isso não equivale a homologação ponta a ponta browser→HTTP nesta máquina, bloqueada por política do ambiente. Ver `VALIDATION.md`.

Não se afirma que esses testes encontram toda vulnerabilidade possível. A ausência de regressão conhecida não certifica a segurança de aplicações que usarão a skill.
