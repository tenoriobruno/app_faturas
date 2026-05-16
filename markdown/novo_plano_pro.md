# Plano de Evolução e Refatoração: Dashboard Financeiro (App Faturas)

Este documento atua como o blueprint arquitetural e de roadmap de features para o projeto `app_faturas`. Ele foi concebido para ser lido e executado de forma autônoma por Agentes IA.

A priorização foi feita através do framework de **Custo x Benefício**, ordenando tarefas que entregam **Maior Impacto de Produto** com o **Menor Esforço de Desenvolvimento**.

## Estratégia de Execução para Agente IA
1. Implemente rigorosamente **uma sprint por vez**. Não pule de contexto.
2. Após modificar cada arquivo, valide se o código roda localmente sem exceções.
3. Mantenha os padrões visuais rígidos já definidos em `config/theme.py`.
4. Garanta que qualquer regra de classificação nova alimente o `cache/categories_cache.json`.

---

## 🏃 Sprint 1: Experiência Core e Redução de Atrito (Alto Impacto / Baixo Esforço)

### 1. Upload UI Dinâmico
- **Descrição**: Substituir a necessidade do usuário largar arquivos manualmente em pastas locais pelo uso da interface web.
- **Arquivos Impactados**: `app.py`
- **Ação**:
  - Na sidebar (`st.sidebar`), adicionar um `st.file_uploader` configurado para arquivos `.csv`.
  - Ao receber o arquivo, persisti-lo dentro do diretório referenciado pela variável `DATA_PATH` (`os.getenv("DATA_PATH")`).
  - Atualizar o estado e forçar `st.rerun()` para que o sistema re-ingira e classifique a base de dados.

### 2. Filtros Laterais Dinâmicos
- **Descrição**: Permitir interações diretas (drill-down) com os dados sem precisar rolar pela página.
- **Arquivos Impactados**: `app.py`, novo arquivo `components/sidebar.py`
- **Ação**:
  - Extrair o seletor atual de CSV para a sidebar.
  - Adicionar multi-seleção de categorias (`st.multiselect`) e campo de texto rápido para busca em transações (`st.text_input` no título).
  - Filtrar localmente o `df` antes de enviar os dados para as métricas e o Plotly de `render_donut`.

### 3. Comparativo de Performance (KPI Deltas)
- **Descrição**: Demonstrar claramente se o usuário está gastando mais ou menos do que o normal.
- **Arquivos Impactados**: `app.py`
- **Ação**:
  - No bloco `📊 Resumo do Período`, para cada `st.metric`, cruze os dados do CSV atual com o CSV cronologicamente anterior no `df_consolidated`.
  - Utilize o parâmetro `delta` do Streamlit metric (ex: `delta="-R$ 150 (Melhoria)"` ou `delta="R$ 300 (Pior)"`) para ilustrar variação financeira em Valor Total e Ticket Médio.

---

## 🏃 Sprint 2: Inteligência Financeira Avançada (Alto Impacto / Médio Esforço)

### 4. Controle de Orçamento Global (Budgets)
- **Descrição**: Estabelecer e observar tetos de gastos.
- **Arquivos Impactados**: `config/budget.json` (criar), `components/budget.py` (criar), `app.py`.
- **Ação**:
  - Criar lógica para ler/escrever uma meta mensal de gastos globais (ex: R$ 5000) e/ou meta por categoria (ex: Delivery R$ 400).
  - Usar `st.progress()` ou um bullet chart no Plotly para evidenciar como o gasto do mês atual se comporta em relação à meta (Verde se < 80%, Laranja se < 100%, Vermelho se > 100%).

### 5. Tracking e Agrupamento de Assinaturas
- **Descrição**: Diferenciar custos únicos de custos recorrentes fixos.
- **Arquivos Impactados**: `analysis/recurrences.py` (criar), `app.py`.
- **Ação**:
  - Fazer análise no `df_consolidated` (todo histórico). Transações com o mesmo `title` ou base (com pequena variação de valor) registradas em >= 3 meses seguidos são flaggadas como Assinatura.
  - Mostrar em UI dedicada um bloco "Gastos Fixos Recorrentes", somando qual o "teto mínimo de entrada do mês" por culpa das assinaturas.

### 6. Projeção de Parcelas
- **Descrição**: Antever o impacto de compras a prazo nos próximos meses.
- **Arquivos Impactados**: `analysis/installments.py` (criar), `parsers/nubank.py`, `app.py`.
- **Ação**:
  - Adicionar regex no parser do nubank para detectar o sufixo de parcelas (ex: `Compra xpto 02/05`, `04/10`, etc).
  - Extrair as colunas `parcela_atual` e `total_parcelas`.
  - Apresentar um painel de "Dívidas Ativas" exibindo a linha do tempo de encerramento das parcelas e o acúmulo das contas passivas futuras.

---

## 🏃 Sprint 3: Refatoração, Automação LLM e Escalabilidade (Médio Impacto / Alto Esforço)

### 7. Agente Auxiliar LLM de Classificação "Zero Outros"
- **Descrição**: Minimizar ou zerar transações não reconhecidas caindo no balde inútil de categoria "Outros".
- **Arquivos Impactados**: `classifier/engine.py`, `classifier/llm_fallback.py` (criar).
- **Ação**:
  - Adicionar uma etapa extra em `classify_batch()`. Se após passar pelas regras locais de `local_rules.py` algo retornar "Outros", utilizar uma chamada barata de modelo de IA generativa (via biblioteca `google-genai` com um modelo como Gemini Flash).
  - Passar como context (system prompt) o schema `categories.json` completo e pedir estritamente a predição.
  - Gravar no `categories_cache.json` permanentemente para evitar novas inferências caras na mesma string.

### 8. Modularização Multi-Page App (MPA)
- **Descrição**: Acomodar o crescimento do sistema separando as views.
- **Arquivos Impactados**: Nova pasta `pages/`, `app.py`
- **Ação**:
  - Converter a aplicação para arquitetura Multi-Page padrão do Streamlit.
  - `app.py` virará o hub de entrypoint/Dashboard padrão.
  - Criar `pages/1_Historico.py`: Apenas visualizações longas de ano/semestre e comparativos.
  - Criar `pages/2_Gerenciar_Categorias.py`: Interface administrativa para editar de forma perene o JSON de regras e orçamentos, ou treinar/purgar o cache local.

### 9. Exportação Rica de Relatório
- **Descrição**: Gerar saídas utilizáveis para fora da plataforma.
- **Arquivos Impactados**: `utils/export.py` (criar), `app.py`
- **Ação**:
  - Possibilitar a exportação do subset visualizado em formato CSV enxuto consolidado.
  - (Opcional avançado) Gerar PDF de report com os plots do Plotly (usando `kaleido` ou similiar).
