# Migração recuperável de projetos legados

Migra somente método/documentação, não stack, banco, credenciais, funcionalidades ou produção.
Adoção por projeto selecionado; não percorre todos os repositórios do disco.

## 1. Identifique propriedade e estado
Leia a raiz governada, state conhecido, entradas e referências. Nome CLAUDE.md/.empire sozinho não
prova propriedade. Não toque global, dependências, submódulos, builds, backups e outras raízes.
`migrate inventory` fornece candidatos e blocos com linhas/hash, sem escrever. O agente decide quais
estão governados e lê apenas trechos necessários; não carregar segredos ou história inteira por rotina.

## 2. Interprete antes de aplicar
A classificação semântica NÃO é algoritmo determinístico. O agente prepara `resolutions.json` com
source_paths, mappings e writes, revisa conflitos e congela o plano. Scripts só aplicam mecânica validada.
Cada bloco original precisa de mapeamento exato. Não inventar requisito aprovado, ADR aceito ou Task
pendente a partir de mera presença no código/handoff. Mesclar só equivalência demonstrada.

Formato de resolução:
```json
{
  "source_paths": ["CLAUDE.md"],
  "mappings": [{
    "source_path": "CLAUDE.md", "block_id": "B-0000-<hash-do-inventario>",
    "block_sha256": "<sha256-real>", "category": "instruction",
    "treatment": "preserve", "destination": "AGENTS.md",
    "reason": "Regra operacional específica permanece válida.", "decision_ref": null
  }],
  "writes": {"AGENTS.md": "<texto final completo, preservando bloco e regras pertinentes>"}
}
```
Este exemplo não é um plano aplicável: substitua IDs/hashes pelo inventário real.
Categorias: instruction, requirement, initiative, task, architecture, decision, guide, session,
history, obsolete_template. Treatments: preserve (bytes do bloco presentes), replace (destino ativo
+ revisão explícita), supersede/history (justificativa e decisão). Instrução ativa não pode ficar só em backup.
Referência de instrução movida deve ser alcançável por AGENTS.md. Trabalho ativo precisa de Task válida.

`writes` contém texto final completo dos destinos. Destino existente também entra em source_paths;
não sobrescrever customização não inventariada. Task gerada deve validar schema. PRD futuro aprovado
continua requisito; proposta não vira autorização. Modelo de classificação não prova equivalência por si só.

Para conteúdo impossível de classificar, preserve eficácia escopada ou interrompa apenas essa substituição.
Não criar fila paralela no relatório. Task de revisão proposta pode acompanhar dúvida não bloqueante.

## 3. Planeje e revise
```sh
python <skill>/scripts/omnx.py --root <projeto> migrate inventory --output <local>/inventory.json
python <skill>/scripts/omnx.py --root <projeto> migrate plan \
  --resolutions <local>/resolutions.json --authority-ref <origem-real> \
  --bootstrap-ref <evidencia-de-AGENTS-lido-pela-skill> --output <local>/plan.json
```
Sem --output, nenhum arquivo de projeto é gravado. Plano inclui os conteúdos de destino:
guarde em local restrito, nunca commite plano bruto com conteúdo sensível. Relatório canônico é sanitizado.
Revisar fontes, destinos, mapeamentos, omissões, bootstrap e efeitos. O digest aprovado congela o plano.

## 4. Aplique
```sh
python <skill>/scripts/omnx.py --root <projeto> migrate apply \
  --plan <local>/plan.json --approved-digest <plan_digest-revisado>
```
Motor verifica precondições, copia originais como .bin inerte, confirma hashes, prepara staging,
escreve com CAS e journal, finaliza lock por último e verifica saídas.
Git sujo fora do escopo não impede; conflito dentro dele precisa reconciliação. Sem stash/reset/push.
Relatório não equivale a bootstrap nativo testado: fallback explícito é delimitado à sessão que leu AGENTS.
Ao migrar legado, remova CLAUDE.md ativo governado depois da consolidação; nunca criar stub equivalente.

## 5. Falha, retomada e rollback
```sh
python <skill>/scripts/omnx.py --root <projeto> migrate status MIG-<id>
python <skill>/scripts/omnx.py --root <projeto> migrate resume MIG-<id> --approved-digest <digest>
python <skill>/scripts/omnx.py --root <projeto> migrate rollback MIG-<id> --approved-digest <digest>
```
Resume usa plano persistido, não nova interpretação. Rollback compara pós-hashes e não sobrescreve
edição posterior. Conflito exige preservação/reconciliação, não --force. Backup corrompido impede remoção.
Histórico e journal locais permanecem após recuperação; não apagar automaticamente a única recuperação.
As operações não são transação atômica do repositório inteiro. São escritas atômicas por arquivo com
journal recuperável, lock local e CAS, testados por interrupção. Outra máquina exige coordenação Git.

## Limites explícitos da primeira distribuição
Migração semântica exige agente/revisor; não há parser que adivinhe aprovação/estado de todos os legados.
Paths fora dos destinos documentais suportados precisam migração técnica separada autorizada.
Conversão de encoding não UTF-8, hardlinks, symlinks e schemas futuros é bloqueada, não “consertada” às cegas.
Referências externas não são reescritas. O agente deve revisar links/escopos semânticos no plano.
