# Plano de Convergência: novo_plano_claude.md

Após analisar o estado atual da implementação (Sprints 1-3 realizadas a partir do `novo_plano_pro.md`) cruzando com o projeto arquitetural avançado proposto em `plano_claude.md` e `plano_antigravity_claude.md`, foi identificado que embora o sistema já possua as features, ele as implementou numa versão "Base".

O plano a seguir detalha exatamente **o que ainda não foi feito** e **o que precisa ser aprimorado (refatorado)** para atingir a robustez, performance estatística e testabilidade exigidas pelo plano original do Claude.

---

## 🛠️ Fase 1: Arquitetura Core e Tratamento de Dados (Baseado em S1 e S8)
*Foco em remover hardcodes, preparar a base para testes e lidar com transações negativas.*

1. **Configuração e Logs Centralizados:**
   - Criar `config/settings.py` contendo a classe de ambiente (`DATA_PATH`, `BUDGET_PATH`, chaves de API, constantes de batch de IA).
   - Criar `utils/logger.py` para injetar logs consistentes, substituindo os prints e `except: pass` silenciosos atuais por `log.warning` ou `log.error`.

2. **Refatoração de Estornos e Ajustes:**
   - Alterar `parsers/nubank.py` para **não** filtrar logo de cara `amount > 0`.
   - Adicionar a coluna `tipo_transacao`: `gasto` (positivo), `estorno` (negativo), `ajuste` (zero).
   - Ocultar/descartar apenas os pagamentos de fatura/ajustes, mas manter estornos para abater no cálculo final.

3. **Otimização do Engine e Tracking de Cache:**
   - No `engine.py`, parar de salvar o `categories_cache.json` a cada string individual iterada. Fazer o diff de contagem de chaves e salvar o cache **uma única vez por batch**.
   - Mudar a estrutura do cache de `{"nome": "Categoria"}` para `{"nome": {"categoria": "Categoria", "source": "local/ai/user"}}`.

---

## 🧠 Fase 2: IA Avançada e Analítica Estatística (Baseado em S2, S4 e S7)
*Foco em aumentar a assertividade matemática do sistema e diminuir custos de API.*

4. **Classificador LLM em Batch (S2):**
   - Atualmente a IA é chamada linha a linha, o que é ineficiente e caro. Refatorar `llm_fallback.py` para processar transações que caíram em "Outros" em blocos de até 20 strings.
   - Retornar um JSON array para associar o resultado em batch de uma vez no DataFrame.

5. **Lógica Estatística para Recorrências (S4):**
   - Substituir o count simplório. Uma conta só é assinatura se: `variance_pct <= 10%`, os dias de diferença entre as compras forem `entre 25 e 35 dias`, e desvio padrão for `<= 5`.
   - Adicionar flag `Status: Ativa/Inativa` (se a próxima projeção já devia ter ocorrido há mais de 7 dias e não ocorreu, inativa).

6. **Validação Rígida e Progresso de Parcelas (S7):**
   - Melhorar a regex de parcelas adicionando *guards*: `total_parcelas > 1 AND <= 24` e `parcela_atual <= total_parcelas`. Isso evita capturar "1/2" que faz parte de um endereço ou tamanho.
   - Na renderização, calcular quantas estão pagas vs total e exibir com a barra nativa `st.progress()`.

---

## 🎛️ Fase 3: UI, Filtros Robustos e Testabilidade (Baseado em S3, S5, S6 e S8)
*Foco na separação de responsabilidades (MVC) e qualidade de software.*

7. **Isolamento de Filtros e Média Móvel (S3 e S6):**
   - Criar `utils/filters.py` exportando uma função pura `apply_filters`.
   - Adicionar no Sidebar: Seletor de Data (`date_input`), multiselect de Tipo (`gasto`, `estorno`) e Checkboxes rápidos ("Ocultar Outros", "Apenas Outros").
   - Nos gráficos de histórico, plotar a **Média Móvel de 3 meses** (pontilhada) para demonstrar a tendência direcional de gastos.

8. **Orçamento Editável em UI (S5):**
   - Hoje o orçamento é apenas lido. Inserir campos de edição (`st.number_input`) diretamente no Streamlit usando um `st.expander` e salvar de volta no `budget.json` ao clicar em "Salvar".

9. **Separação por Views e Testes (S8):**
   - Desacoplar o monolito de renderização do `app.py`. Mover as métricas para `views/overview.py`, as tabelas para `views/transactions.py`, etc, roteadas por abas (`st.tabs`).
   - Implementar uma suíte sólida de testes com `pytest` na pasta `tests/` cobrindo o `normalize.py`, detecção de parcelas do parser e funções puras matemáticas de agregação.
