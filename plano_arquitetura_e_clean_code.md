# Plano de Arquitetura de Software e Clean Code

## 📌 Diagnóstico Atual
O projeto cresceu rapidamente de forma orgânica. Embora as pastas (`analysis`, `components`, `utils`) pareçam organizadas, o código interno de vários arquivos **viola os princípios SOLID**, especificamente a **Responsabilidade Única (SRP)**.

**Principais Problemas (Redundâncias e Complexidades):**
1. **Acoplamento View vs Lógica:** Arquivos como `analysis/installments.py` e `components/budget.py` misturam pesadamente transformações de Pandas (Lógica de Negócio) com comandos do Streamlit (UI). Isso impede que a lógica seja testada isoladamente.
2. **Camada de Dados Dispersa:** O `utils/storage.py` lê/salva o cache, e o `components/budget.py` lê/salva o budget. Ambos repetem as mesmas lógicas de abrir arquivo, fazer parse de JSON e lidar com exceções.
3. **App.py Monolítico:** O arquivo `app.py` atua como Controlador, Roteador e View ao mesmo tempo, fazendo a montagem das abas, cálculos de KPIs e injeção de estado, resultando num arquivo muito longo.
4. **Passagem de Estado:** Os DataFrames são passados como argumentos para cada função de renderização exaustivamente, ignorando o poder do `st.session_state`.

---

## 🎯 Solução Proposta: Clean Architecture (MVC Adaptado)

### 1. Refatoração da Camada de Dados (Repository Pattern)
**Problema:** Múltiplos arquivos abrindo JSON diretamente.
**Solução:** Criar a pasta `data/` com um arquivo `repository.py`.
* Teremos classes simples (`CacheRepository`, `BudgetRepository`) que lidam estritamente com ler e escrever dados no disco.
* Remove os "try/except" com manipulação de JSON de dentro dos componentes visuais.

### 2. Separação Estrita de UI vs Lógica
**Problema:** `import streamlit as st` dentro da pasta de análise de dados.
**Solução:**
* **`core/` (antigo `analysis` e `classifier`):** Ficará responsável **apenas** por Matemática e Pandas. Exemplo: `calculate_installments()` recebe um DataFrame e retorna um DataFrame mastigado. Zero Streamlit.
* **`views/` (Nova pasta):** Ficará responsável por exibir os dados. Exemplo: `views/installments_view.py` chama a função do `core`, recebe o DataFrame pronto, e usa `st.progress` e `st.plotly_chart` para desenhar na tela.

### 3. "Emagrecimento" do `app.py`
O `app.py` deve ser apenas o "Ponto de Entrada" do sistema.
Ele fará apenas:
1. `st.set_page_config` e injeção de tema.
2. Carregar dados básicos.
3. Renderizar a Sidebar.
4. Mostrar o `st.tabs()` e chamar as respectivas `views` para cada aba.
**Meta:** `app.py` com menos de 50 linhas. Toda a lógica de KPIs e cálculos de deltas vai para `views/overview_view.py`.

### 4. Gerenciamento de Estado (Session State)
Em vez de funções como `render_sidebar(df, categories)` retornarem um DataFrame gigante copiado, os filtros modificarão o `st.session_state['df_filtered']`.
As `views` consumirão os dados do Session State de forma global, reduzindo drasticamente o número de variáveis flutuando no código.

---

## 🚀 Roteiro de Execução (Sprints de Refatoração)

**Fase 1: Abstração de Dados e Estado**
- Criar `data/repository.py` unificando a leitura de `categories_cache.json` e `budget.json`.
- Excluir lógicas de JSON do `storage.py` e do `budget.py`.
- Introduzir `st.session_state['df']` no topo do sistema.

**Fase 2: Isolamento do Core (Lógica de Negócio)**
- Limpar `analysis/` movendo tudo relacionado a `st.*` para arquivos temporários.
- Garantir que as funções matemáticas (ex: detecção de recorrências, fatiamento de dados) sejam 100% agnósticas à UI.

**Fase 3: Construção das Views e Limpeza Final do App.py**
- Criar a pasta `views/` contendo: `overview.py`, `transactions.py`, `recurrences.py`, `installments.py`.
- Mover todos os blocos `with st.col:` e `st.metric:` do `app.py` e de `components/` para suas repectivas views.
- Reduzir o `app.py` para atuar apenas como maestro/roteador do Streamlit.

---

Este plano focará em diminuir a confusão, reutilizar funções e garantir que o projeto seja facilmente escalável para os próximos anos sem quebrar.
