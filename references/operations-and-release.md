# Operações, release e dados

Autorização de implementação cobre trabalho local pertinente, não publicação automática.
Antes de O2/O3 confirme destino, ambiente, dados, efeito/custo, credencial e autoridade já concedida.
Não renove confirmação para cada edição segura do mesmo escopo. Renove se consequência/alvo mudar materialmente.

Para publicar, identifique artefato/commit, configuração, flags, migrações e evidências do conteúdo final.
Use registro da plataforma como canônico; sem plataforma, registro de release sanitizado com schema fornecido.
Não usar nome da branch como prova de deploy. Build bem-sucedido não prova release saudável.
Após publicação autorizada, conferir resultado e smoke test pertinentes. Falha deve aparecer como falha/parcial.

Flag frontend não é autorização backend. Feature em staging/canário/tenant específico não está disponível
universalmente. Guia estável não anuncia o que ainda está Unreleased.

Mudança de dados exige salvaguardas proporcionais: alvo, compatibilidade, snapshot/backup restaurável,
possível coexistência de versões e plano de recuperação. CRUD normal não exige migration por ser DML.
Nunca usar reset remoto como fallback de push incremental. Comando indisponível pede diagnóstico.
Git revert não desfaz exclusão, e-mail enviado ou pagamento; compensação/reconciliação é operação específica.
Não invente rollback infalível. Se irreversível, declare antes e exija mitigação/autoridade apropriadas.

Gate local avalia evidências/política, não instala proteção de branch. Em ambiente com política externa,
ela prevalece e precisa ser verificada na referência confiável, não editada pelo próprio patch.
