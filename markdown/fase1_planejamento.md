# FASE 1 — PLANEJAMENTO

Você está no Claude Code construindo um MVP pessoal de gestão financeira inspirado no Guiabolso.

## REGRAS DESTA SESSÃO

- NÃO escreva código
- NÃO crie arquivos além do PLAN.md
- Respostas curtas e diretas
- Pare e aguarde aprovação do PLAN.md antes de qualquer coisa

## OBJETIVO

Gerar um PLAN.md detalhado que será usado na sessão de execução.
O plano deve ser tão claro que a execução não precise de decisões arquiteturais.

## CONTEXTO DO PROJETO

MVP pessoal de finanças. Não é SaaS. Não precisa escalar.
Orçamento: < $1 de desenvolvimento, < $0.05 por 100 transações classificadas.

## STACK DEFINIDA

- Python 3.11+
- Streamlit
- Pandas
- Plotly
- python-dotenv
- Anthropic SDK (claude-haiku-3-5-20251001 como fallback)

## ESTRUTURA DE PASTAS DEFINIDA

```
financas/
├── app.py
├── requirements.txt
├── .env
├── assets/
│   └── styles.css
├── data/
├── cache/
│   └── categories_cache.json
├── parsers/
│   └── nubank.py
├── classifier/
│   ├── engine.py
│   ├── local_rules.py
│   └── ai_classifier.py
├── utils/
│   ├── normalize.py
│   └── storage.py
└── categories.json
```

## O PLAN.md DEVE COBRIR

### 1. Responsabilidade de cada arquivo
- O que cada módulo faz
- O que importa de onde
- Fluxo de dados: upload → parse → normalizar → classificar → salvar → exibir

### 2. Fluxo completo passo a passo
1. Upload CSV pelo Streamlit
2. Parsing com pandas
3. Normalização da descrição
4. Classificação local (keywords + regex)
5. Fallback IA (Haiku) se local falhar
6. Cache persistente por descrição normalizada
7. Salvamento em data/ e cache/
8. Renderização no dashboard
9. Edição manual na tabela
10. Exportação CSV

### 3. Estratégia de economia de tokens
Ordem obrigatória antes de qualquer chamada IA:
1. Normalização → remove números, IDs, ruído
2. Cache local → se já classificado, retorna imediatamente
3. Keywords → busca em categories.json
4. Regex → padrões como "UBER*", "IFOOD*PEDIDO", "99*"
5. Fuzzy match → similaridade simples por token
6. IA (Haiku) → SOMENTE se tudo falhar

Meta: IA chamada em menos de 15% das transações.

### 4. Estratégia de normalização
Tratar casos reais do Nubank:
- "UBER TRIP 123ABC" → "uber trip"
- "IFOOD *PEDIDO" → "ifood"
- "MERCPAGO*LOJA123" → "mercpago"
- "COMPRA PARCELADA 01/12" → "compra parcelada"

### 5. Casos extremos a tratar
- CSV vazio ou corrompido
- Encoding inesperado (latin-1 vs utf-8)
- Uploads duplicados (deduplicar por date+description+amount)
- Estornos (amount positivo — excluir ou sinalizar)
- Parcelamentos (ex: "01/12")
- Compras internacionais

### 6. Estratégia visual Streamlit
- Como esconder aparência padrão do Streamlit via CSS
- Layout: sidebar + grid de cards + gráficos + tabela
- Objetivo: parecer fintech moderna, não app padrão do Streamlit

### 7. Plano incremental de execução
Listar os 10 passos com:
- O que implementar
- Como testar
- Critério de sucesso antes de avançar

### 8. Estimativa de custo
- % estimado classificado localmente
- Tokens por chamada IA
- Custo por 100 transações
- Meta: < $0.05 por 100 transações

## AO TERMINAR

Mostre apenas o PLAN.md.
Aguarde minha aprovação.
Não sugira próximos passos nem escreva código.
