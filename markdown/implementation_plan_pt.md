# Plano de Implementação da Redesign da UI

## Objetivo
Redesenhar o dashboard financeiro em Streamlit para oferecer um visual moderno e premium, mantendo a funcionalidade existente. O redesign incluirá:
- **Alternador de modo escuro** com transição suave.
- **Cards com efeito de glass‑morphism** para métricas, gráficos e caixas de resumo.
- **Micro‑animações sutis** (fade‑in, elevação ao passar o mouse) usando transições CSS.
- **Layout responsivo** que funciona em desktops e tablets.
- **Paleta de cores refinada** (cor de destaque principal e cores das categorias) e **Fonte Google** (Inter).
- **Acessibilidade aprimorada** (contraste, contornos de foco).

---

## Revisão do Usuário Necessária
> [!IMPORTANTE]
> Por favor, revise as decisões a seguir e forneça feedback:
> 1. **Posicionamento do alternador de modo escuro** – barra lateral (topo) ou cabeçalho (canto direito)?
> 2. **Cor de destaque principal** – manter o `#0866FF` (azul Facebook) ou escolher outra.
> 3. **Intensidade da animação** – sutil (opacidade/escala) ou mais pronunciada (deslizamento).

---

## Perguntas Abertas
> [!AVISO]
> - O aplicativo deve suportar **detecção automática do tema do sistema** (modo escuro automático) além do alternador manual?
> - Deseja um **logotipo personalizado** no cabeçalho (necessita de arquivo de imagem)?

---

## Alterações Propostas
### 1. Estilização Central (`config/theme.py`)
- Expandir a string `CSS` com:
  - `@import` da fonte **Inter** do Google Fonts.
  - Variáveis `:root` para paletas clara e escura.
  - Classe `.dark-mode` que troca fundos, texto e cores dos cards.
  - Estilo de glass‑morphism (`backdrop-filter: blur(12px); background: rgba(255,255,255,0.25)` para modo claro, `rgba(0,0,0,0.25)` para modo escuro).
  - Transições globais (`transition: all 0.3s ease`) para mudança de tema fluida.
- Adicionar um **botão de alternância** que altera `st.session_state.dark_mode` e troca a classe `<body>` via `st.markdown` com um pequeno trecho de JavaScript.

### 2. Componente de Cabeçalho (`components/header.py` – novo arquivo)
- Renderizar o título do app e o **alternador de modo escuro** (ícone sol/lua) usando `st.markdown` e CSS customizado.
- Exportar `render_header()` para inclusão em `app.py`.

### 3. Barra Lateral (`components/sidebar.py`)
- Ajustes menores de UI para adotar a nova fonte e espaçamento.
- Garantir que a barra lateral respeite o tema atual (cores de fundo via variáveis CSS).

### 4. Cards de Métricas & Gráficos (`components/metrics.py` e arquivos de views existentes)
- Envolver cada `st.metric` e gráfico Plotly dentro de um contêiner `<div class="glass-card">`.
- Aplicar a nova classe CSS que fornece glass‑morphism, sombra sutil e elevação ao hover (`transform: translateY(-2px)`).
- Inserir `st.markdown` para o contêiner antes da métrica/gráfico.

### 5. Views (`views/*.py`)
- Atualizar importações para incluir o novo componente de cabeçalho.
- Substituir chamadas diretas `st.title` / `st.subheader` por equivalentes estilizados.
- Garantir que todos os gráficos utilizem o `PLOT_LAYOUT` atualizado (já com fundo transparente) e adicionem ajustes para modo escuro.

### 6. Layout Responsivo
- Utilizar grid/flexbox CSS dentro dos contêineres `glass-card` para adaptação ao tamanho da tela.
- Adicionar media queries (`@media (max-width: 768px)`) que empilham os cards verticalmente.

### 7. Melhorias de Acessibilidade
- Verificar razões de contraste para ambos os temas (usar `#FFFFFF` em fundos escuros, `#1C1E21` em fundos claros).
- Adicionar contornos `:focus-visible` a elementos interativos.
- Assegurar que o alternador de modo escuro seja acessível via teclado.

### 8. Gerenciamento de Assets
- Criar novo arquivo `assets/inter.css` (opcional) contendo regras `@font-face` caso deseje hospedar a fonte localmente.
- Atualizar `.gitignore` para manter os assets gerados sincronizados.

### 9. Cache & Configurações (`config/settings.py`)
- Incluir nova configuração `DEFAULT_DARK_MODE = False` que pode ser sobrescrita pela preferência do usuário.
- Persistir a escolha de tema em `st.session_state` entre reloads.

### 10. Documentação (`README.md`)
- Documentar os novos recursos de UI, como alternar o modo escuro e dependências necessárias.

---

## Plano de Verificação
### Checagens Automatizadas
- Executar a suíte de testes existente (`pytest -q`) para garantir que não haja regressões no tratamento de dados.
- Adicionar um **teste de snapshot** que renderiza a página inicial e verifica a presença da classe `.dark-mode` quando o alternador está ativo.

### Verificação Manual
1. **Alternar Tema** – Clicar no alternador, garantir que toda a UI transita suavemente e as cores mudam.
2. **Layout Responsivo** – Redimensionar a janela do navegador; os cards devem reorganizar-se adequadamente.
3. **Acessibilidade** – Usar Lighthouse do Chrome DevTools para validar contraste > 4.5:1 e navegação por teclado.
4. **Performance** – Verificar que o CSS adicional não aumenta perceptivelmente o tempo de carregamento (medir LCP < 2 s).

---

## Cronograma (aprox.)
- **Dia 1** – Expandir CSS, adicionar alternador de modo escuro, criar componente de cabeçalho.
- **Dia 2** – Refatorar contêineres de métricas/cards, aplicar glass‑morphism, atualizar views.
- **Dia 3** – Implementar layout responsivo, ajustes de acessibilidade, atualizar configurações.
- **Dia 4** – Escrever documentação, executar plano de verificação, corrigir regressões.
- **Dia 5** – Polimento final, merge para a branch principal.

---

*Este plano segue as diretrizes do CLAUDE.md: é mínimo, cirúrgico e altera apenas arquivos relacionados ao estilo da UI e renderização de componentes.*

The above content shows the entire, complete file contents of the requested file.
