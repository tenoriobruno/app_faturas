# Objective
Implementar um log de auditoria persistente para modificações manuais de categorias e estender a arquitetura de parsing para aceitar transações do banco Itaú.

# Affected files
- `data/repository.py`
- `services/classification.py`
- `parsers/itau.py` (novo arquivo)
- `parsers/__init__.py` (novo arquivo)
- `app.py`

# What NOT to touch
- A lógica interna de normalização e classificação do Nubank.
- O formato final de colunas do DataFrame das transações.

# Step by step instructions
1. Em `data/repository.py`, implemente a classe `AuditLogRepository` para salvar e carregar históricos de edições manuais em `cache/audit_log.json`.
2. Em `services/classification.py`, integre o `AuditLogRepository` para gerar um registro de log toda vez que o usuário alterar manualmente a categoria de uma transação. Grave: timestamp, descrição original, categoria anterior, categoria nova e fonte.
3. Crie o arquivo `parsers/itau.py` contendo a classe ou função de processamento para faturas CSV do Itaú. Garanta que o DataFrame de retorno obedeça exatamente ao mesmo esquema do parser Nubank (`date`, `title`, `amount`, `tipo_transacao`, `categoria`, `parcela_atual`, `total_parcelas`).
4. Crie o arquivo `parsers/__init__.py` e implemente um método factory de autodetecção que inspecione a primeira linha/cabeçalho de qualquer CSV inserido para escolher o parser correto (Nubank ou Itaú).
5. Modifique `app.py` para utilizar o factory de parsers genérico em vez do import e chamada direta ao módulo `parsers.nubank`.

# Success criteria
- Edições na tabela de transações são registradas em `cache/audit_log.json`.
- O app é capaz de identificar, parsear, categorizar e renderizar faturas do banco Itaú mantendo consistência de dados.

# Complexity
High
