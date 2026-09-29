# OMNX Console 1.1.0-rc.1

Componente embutido na OMNX Code 2.2.0-rc.1. Painel local, estático/determinístico, sem APIs de IA ou banco paralelo. Hooks de projeto confiados podem abri-lo no início de sessões de implementação e associá-lo à Task; isso não prova leitura humana nem cobre sessões sem hooks ativos.

```sh
python3 "/pasta/omnx-code/scripts/omnx.py" --root "/projeto" console open
```

`--root` vem antes de `console`. Para catálogo existente, omita `--root`. `console stop` encerra somente a instância identificada.

Contrato, segurança, decisões e limitações: `../references/console.md`. Instalação/atalho e adoção: `../README.md`. Validação efetivamente executada: `../reports/VALIDATION.md`.

O status de atividade vem de sinais reais recentes. Tarefa, sessão, presença do navegador e versão carregada permanecem estados separados. O painel atende esta máquina; não sincroniza uma equipe nem desperta agentes.

HTML de preview é intencionalmente estático. Não promete execução interativa nem identidade forte do aprovador. Não inclui Electron, binário desktop assinado, terminal ou conexão com modelos.
