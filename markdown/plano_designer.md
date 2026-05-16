# Plano de Otimização de Design e Cores (app_faturas)

## 📌 Diagnóstico do Problema
Os problemas relatados (fontes brancas em fundos brancos, tabelas pretas invisíveis, botões e sidebar ilegíveis) ocorrem devido a um **conflito de temas**. O código atual no `config/theme.py` injeta um CSS forçado ("hardcoded") projetado para um tema claro, mas o Streamlit está aplicando nativamente o "Dark Mode" (provavelmente herdado do seu sistema operacional). Isso gera uma quimera visual onde fundos nativos ficam escuros, mas os cards customizados ficam claros com textos invertidos.

## 🎯 Solução Proposta: Padronização Nativa + Design Premium
A melhor forma de ter um design "Wow" e resolver esses problemas de contraste não é escrever mais CSS, mas sim **domar o motor de temas do Streamlit** e usar CSS apenas para micro-ajustes (como arredondamento e sombras).

### 1. Configuração de Tema Base (`.streamlit/config.toml`)
A espinha dorsal da correção. Devemos forçar o tema para um "Light Mode Premium" (ou Dark Mode, se preferir), garantindo que botões, uploads, inputs e tabelas usem o mesmo esquema de cores sem conflitar.

**Proposta de `config.toml`:**
```toml
[theme]
base = "light"
primaryColor = "#3B82F6"      # Azul vibrante para o botão "Baixar CSV", Sliders e Ativos
backgroundColor = "#F8FAFC"   # Fundo geral muito suave (Slate-50)
secondaryBackgroundColor = "#FFFFFF" # Fundo da Sidebar e dos Cards (Upload, Selectbox)
textColor = "#0F172A"         # Texto principal escuro e forte (Slate-900)
font = "sans serif"
```

### 2. Refatoração do `config/theme.py` (Limpeza de CSS)
Removeremos as regras de cor excessivas que forçam `!important` para `background` e `color` e focaremos apenas em "Glassmorphism" e "Aesthetics":
* **Cards & Expander:** Manter as bordas arredondadas (`border-radius: 16px`) e sombras suaves (`box-shadow: 0 4px 20px rgba(0,0,0,0.04)`).
* **Métricas (KPIs):** Dar ênfase tipográfica aos números usando fontes maiores e limpar as cores rígidas para que sigam o `textColor` nativo.
* **Tabelas de Dados:** Como o Streamlit cuidará das cores base, a tabela do "Ver Dados" assumirá um fundo branco com letras escuras, resolvendo a questão do texto preto no fundo preto.

### 3. Melhoria de Tipografia e Hierarquia Visual
* **Upload de Faturas:** Ao definirmos o `secondaryBackgroundColor` para `#FFFFFF`, o fundo ao redor do uploader ficará limpo e legível. A fonte não será mais cinza sobre fundo escuro.
* **Acompanhamento de Orçamento:** O texto branco que você mencionou sumirá. Usaremos a hierarquia de fontes do Streamlit, garantindo contraste (Preto no Branco).

### 4. Otimização da Paleta de Categorias (`CATEGORY_COLORS`)
As cores atuais no Gráfico de Rosquinha (Donut) estão um pouco saturadas e podem poluir a tela. Substituiremos por uma **paleta harmoniosa premium**, dividida por grupos de cores quentes e frias, para dar uma aparência mais profissional e moderna (ex: Tons pastéis vívidos, inspirados em painéis de BI da Stripe ou Nubank).

### 5. Botões e Ações
* **Botão "Baixar CSV":** Atualmente está preto porque herda estilos padrões. Ao ativarmos o `primaryColor = "#3B82F6"`, botões de ação e checkboxes ficarão com um azul vibrante moderno, deixando a sidebar convidativa e clara.

---

## 🚀 Próximos Passos para a Implementação
1. Criar o diretório `.streamlit/` e o arquivo `config.toml` forçando o tema Light.
2. Limpar o `config/theme.py` removendo as tags de `color` e `background` conflitantes do CSS.
3. Atualizar a paleta de cores do Plotly para combinar com o novo design.
4. Reiniciar o servidor Streamlit para aplicar o novo arquivo TOML nativo.

Se você estiver de acordo com este plano, posso realizar a implementação agora mesmo!
