# Top 5 Melhorias: App Faturas

## 1. Substituição Gemini → Ollama (Local LLM)
**Problema:** Dependência de API externa, custo (mesmo que baixo) e privacidade de dados financeiros.
**Solução:** Integrar Ollama para rodar modelos (ex: Llama 3, Mistral) localmente.
**Impacto:** Custo zero, 100% privacidade, independência de internet para classificação.

## 2. Migração JSON → SQLite
**Problema:** `JSONRepository` é ineficiente para buscas, não garante integridade referencial e torna-se lento com volume de dados.
**Solução:** Implementar banco de dados SQLite para armazenar transações, cache de categorias e configurações.
**Impacto:** Consultas rápidas, maior robustez, facilidade para gerar relatórios complexos.

## 3. Interface de Gestão de Regras (UI)
**Problema:** Para adicionar novas categorias ou ajustar regex, é necessário editar `categories.json` manualmente no arquivo.
**Solução:** Criar uma aba "Configurações" no Streamlit para editar palavras-chave e regex de categorias via app.
**Impacto:** UX melhorada, agilidade no refinamento da classificação.

## 4. Implementação de Testes Automatizados
**Problema:** Lógica de normalização e parsing de CSV é sensível a mudanças no formato do Nubank. Sem testes, bugs surgem silenciosamente.
**Solução:** Adicionar suíte de testes com `pytest` focada em `utils/normalize.py` e `parsers/nubank.py`.
**Impacto:** Garantia de estabilidade, confiança em refatorações.

## 5. Dashboard de Projeção Financeira (Forecasting)
**Problema:** O app foca no passado (transações realizadas). A lógica de parcelas em `core/` é subutilizada.
**Solução:** Criar visualizações de fluxo de caixa futuro baseadas em parcelas e recorrências detectadas.
**Impacto:** Transformar app de "extrato" em ferramenta de "planejamento".
