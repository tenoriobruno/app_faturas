# FASE 2 — EXECUÇÃO

Você está no Claude Code implementando um MVP de finanças pessoais.
O PLAN.md já foi aprovado. Implemente exatamente o que foi planejado.

## REGRAS DESTA SESSÃO

- Respostas curtas. Sem explicações longas.
- Não mostre código que não foi alterado.
- Não repita contexto anterior.
- Não invente features novas.
- Trabalhe um passo por vez.
- Após cada passo: rode `streamlit run app.py`, confirme que funciona, pare e aguarde.

## FILOSOFIA — SKILL CAVEMAN

Agir como engenheiro sênior construindo MVP em fim de semana.

USE:
- Funções pequenas e explícitas
- Lógica direta, sem mistério
- Nomes óbvios

EVITE:
- Classes desnecessárias
- Abstrações genéricas
- Qualquer pattern enterprise

Se dúvida entre sofisticado vs simples → ESCOLHA SIMPLES.

## ORDEM DE IMPLEMENTAÇÃO

Execute exatamente nessa ordem. Um passo por vez.

```
PASSO 1 → app.py vazio rodando sem erro
PASSO 2 → parsers/nubank.py + teste com CSV real
PASSO 3 → dashboard esqueleto (layout, sidebar, cards zerados)
PASSO 4 → gráficos Plotly com dados mock
PASSO 5 → categories.json (80+ keywords) + classifier/local_rules.py
PASSO 6 → utils/normalize.py + integração com local_rules
PASSO 7 → utils/storage.py + persistência em data/
PASSO 8 → tabela editável com st.data_editor salvando no disco
PASSO 9 → classifier/ai_classifier.py + cache persistente em cache/
PASSO 10 → assets/styles.css + polimento visual final
```

## ESPECIFICAÇÕES TÉCNICAS

### parsers/nubank.py
```python
# parse_nubank(filepath: str) -> pd.DataFrame
# Colunas CSV Nubank: date, title, amount
# Filtrar amount < 0 (gastos), converter para positivo
# Renomear title → description
# Adicionar coluna category = None
# Retornar: [date, description, amount, category]
# Tratar encoding latin-1 e utf-8
# Deduplicar por date+description+amount
```

### utils/normalize.py
```python
# normalize(description: str) -> str
# Lower case
# Remove acentos
# Remove números e IDs
# Remove asteriscos, barras, símbolos
# Remove parcelas (ex: "01/12")
# Strip e espaços duplos
```

### classifier/local_rules.py
```python
# classify_local(description: str) -> str | None
# Normaliza a descrição
# Busca qualquer keyword de categories.json
# Retorna categoria ou None
```

### classifier/ai_classifier.py
```python
# classify_ai(description: str) -> str
# Modelo: claude-haiku-3-5-20251001
# temperature=0, max_tokens=5
# Prompt mínimo < 30 tokens:
# "Classifique: {desc}
#  Categorias: Alimentação, Transporte, Saúde, Lazer,
#  Assinaturas, Compras, Moradia, Educação, Viagem, Outros.
#  Responda só a categoria."
```

### classifier/engine.py
```python
# classify(description: str) -> str
# 1. normalize(description)
# 2. checar cache em memória
# 3. classify_local()
# 4. se None → classify_ai()
# 5. salvar no cache
# 6. retornar categoria

# classify_batch(df) -> df
# aplica classify() em cada linha
# mostra progresso simples
```

### utils/storage.py
```python
# save_processed(df, filename)  → data/{filename}_processed.csv
# load_all_processed()          → DataFrame com todos os CSVs de data/
# load_cache()                  → dict de cache/categories_cache.json
# save_cache(cache)             → salva cache atualizado
```

### app.py — layout Streamlit

SIDEBAR:
- Logo "₿ finanças"
- st.file_uploader (múltiplos CSVs)
- Filtro mês/ano
- Métricas: X% classificado local, Y chamadas IA
- Botão exportar CSV

MAIN linha 1 — 3 cards:
- Total gasto no período (R$)
- Categoria líder (nome + %)
- Número de transações

MAIN linha 2 — 2 colunas:
- Pizza Plotly: gastos por categoria
- Barras Plotly: total por mês (últimos 6 meses)

MAIN linha 3:
- st.data_editor com coluna category como selectbox
- Ordenado por date desc
- Salvar edições automaticamente

### Visual

Paleta:
```
background: #0B0B0C
card:       #151517
border:     #26262B
primary:    #8A05BE
text:       #F5F5F5
text-muted: #A1A1AA
green:      #22C55E
red:        #EF4444
```

Tipografia: Inter (textos) + JetBrains Mono (valores e datas)

CSS obrigatório em assets/styles.css:
```css
#MainMenu, footer, header { visibility: hidden; }
```

Gráficos Plotly:
```python
paper_bgcolor='rgba(0,0,0,0)'
plot_bgcolor='rgba(0,0,0,0)'
font_color='#F5F5F5'
```

### categories.json — categorias obrigatórias

Incluir no mínimo:
- Alimentação: ifood, rappi, uber eats, mcdonalds, burger king, subway,
  starbucks, padaria, restaurante, mercado, supermercado, carrefour,
  extra, pao de acucar, hortifruti
- Transporte: uber, 99app, cabify, metro, sem parar, veloe, posto,
  ipiranga, shell, combustivel
- Assinaturas: netflix, spotify, amazon prime, youtube, globoplay,
  disney, hbo, apple, microsoft, adobe, chatgpt, claude, dropbox
- Saúde: farmacia, drogasil, droga raia, ultrafarma, hospital,
  clinica, dentista, unimed, hapvida
- Compras: amazon, mercado livre, shopee, americanas, magalu,
  casas bahia, shein, aliexpress
- Moradia: aluguel, condominio, energia, enel, eletropaulo,
  sabesp, gas, claro, vivo, tim, internet
- Viagem: booking, airbnb, latam, gol, azul, hotel, pousada
- Educação: udemy, coursera, alura, escola, faculdade, livraria
- Lazer: cinema, teatro, show, ingresso, steam, playstation,
  xbox, academia, smartfit

## CRITÉRIO DE PRONTO

Antes de declarar concluído confirmar:
- [ ] streamlit run app.py sobe sem erro
- [ ] Upload CSV do Nubank funciona
- [ ] > 85% classificado localmente
- [ ] Gráficos pizza e barras renderizando dark
- [ ] Tabela editável salva no disco
- [ ] Cache IA funcionando
- [ ] CSS esconde aparência padrão do Streamlit
- [ ] Custo estimado < $0.05 por 100 transações
- [ ] Relatório final: X chamadas IA, custo estimado $Y

## QUANDO TRAVAR

Se um passo ficar complexo:
- Troque temporariamente para claude-sonnet-4-6
- Resolva só aquele trecho
- Volte imediatamente para haiku-4-5

Se entrar em loop de bug:
- Pare
- Rode /clear
- Recomece o passo com contexto mínimo
