# Dashboard Financeiro (Nubank)

Dashboard moderno, elegante e interativo desenvolvido em Streamlit para visualização, classificação automática e controle orçamentário dos seus gastos do cartão Nubank.

## 🚀 Recursos
- **Visual Premium**: Layout moderno com efeitos de glassmorphism e design fluído responsivo.
- **Alternador de Modo Escuro**: Botão dinâmico ☀️/🌙 no cabeçalho com transição suave de cores.
- **Gráficos Dinâmicos**: Gráficos de rosca e barras interativos usando Plotly que se integram ao tema claro/escuro.
- **Acompanhamento de Orçamento**: Definição de limites globais e por categoria com barras de progresso interativas.
- **Filtros Avançados**: Barra lateral estilizada com busca textual, seleção de múltiplas categorias, faixa de valores e período.
- **Classificação Manual**: Tabela de transações interativa que permite reclassificar despesas manualmente e salvar o histórico para futuros uploads.

## 🛠️ Instalação e Execução

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o Streamlit:
   ```bash
   streamlit run app.py
   ```

## 🎨 Estrutura de Design & UI
O tema do aplicativo é consolidado no arquivo [theme.py](file:///Users/brunotenorio/workspace/app_faturas/config/theme.py) e suporta:
- Variáveis CSS customizadas para alternância dinâmica entre modo claro e escuro.
- Cards com efeito glass-morphic (`.glass-card`).
- Micro-animações e elevação sutil em hover nos cards e elementos interativos.
