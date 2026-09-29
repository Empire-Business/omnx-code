# Defeitos reproduzidos e correções — 2.2.0-rc.1

| Problema confirmado | Correção | Evidência |
|---|---|---|
| Launcher anunciava abertura sem checar o retorno do navegador | Retorno, exceção, servidor e conexão técnica agora têm estados separados | test_launcher_reports_browser_failure_and_unconfirmed_client |
| Falha ao abrir Console podia ser confundida com falha de registro ou encerrar o fluxo | Task/journal são gravados antes da abertura; erro do launcher falha aberto e é deduplicado | test_console_launch_is_once_and_failed_browser_does_not_lose_task |
| Sessões simultâneas podiam colidir no lock não bloqueante da Task | Hooks fazem poucas tentativas idempotentes; tarefas e journals seguem separados | test_parallel_sessions_and_replay_keep_tasks_separate; test_same_host_session_in_two_worktrees_keeps_local_journals |
| Registros simultâneos do catálogo local podiam falhar durante a inicialização do lock | Lock no diretório raiz privado do catálogo com espera limitada | test_catalog_registration_concurrent_processes; 30 rodadas de 6 processos passaram |
| `verify-package` contava `.git` e bytecode da árvore de desenvolvimento como arquivos do pacote | Verificação ignora apenas metadados Git e `__pycache__`, mantendo a lista do pacote estrita | test_verify_package_ignores_repository_metadata |
| Uma checagem de release concorrente aparecia como indisponibilidade ou tentava gravar por cima | Segunda sessão informa checagem em andamento sem rede/escrita concorrente | test_concurrent_update_check_reports_in_progress_without_network |
| Ausência, timeout, incompatibilidade ou digest incorreto poderiam parecer atualização concluída | Policy opt-in, canal, hash, manifesto e compatibilidade mantêm a versão atual e registram falha/candidato | tests em test_daily.py e test-results-2.2.0-rc.1.json |

As correções históricas R01–R12 da 2.1.0-rc.2 estão preservadas em history/REGRESSIONS-2.1.0-rc.2.md. Testes de servidor HTTP usam loopback real e fixtures locais; Playwright/Chromium não estavam disponíveis nesta rodada. Não equivale a homologação browser→HTTP nem de host real.
