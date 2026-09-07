# OMNX Console 1.0.0-rc.2

Componente embutido na OMNX Code 2.1.0-rc.2. Painel local opcional, estático/determinístico, sem APIs de IA ou banco paralelo.

```sh
python3 "/pasta/omnx-code/scripts/omnx.py" --root "/projeto" console open
```

`--root` vem antes de `console`. Para catálogo existente, omita `--root`. `console stop` encerra somente a instância identificada.

Contrato, segurança, decisões e limitações: `../references/console.md`. Instalação/atalho e adoção: `../README.md`. Validação efetivamente executada: `../reports/VALIDATION.md`.

HTML de preview é intencionalmente estático. Não promete execução interativa nem identidade forte do aprovador. Não inclui Electron, binário desktop assinado, terminal ou conexão com modelos.
