# Objective
Remover arquivos e trechos de código morto para limpar o repositório, reduzir o tamanho do ambiente virtual e organizar arquivos de planejamento legados.

# Affected files
- `components/ui/__init__.py` (deletar)
- `components/ui/components.py` (deletar)
- `requirements.txt`
- `config/settings.py`
- `categories.json`
- `.gitignore`

# What NOT to touch
- Outras dependências ativas no `requirements.txt` (Streamlit, Pandas, etc.).
- Outras chaves de categoria no `categories.json`.

# Step by step instructions
1. Remova por completo o diretório `components/ui/` e seus arquivos internos.
2. No arquivo `requirements.txt`, remova a dependência `google-generativeai==0.8.3`.
3. No arquivo `config/settings.py`, remova a linha `GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")`.
4. No arquivo `categories.json`, limpe o regex da categoria `"Outros"`, alterando `"regex": [".*"]` para `"regex": []`.
5. Crie o diretório `docs/archive/` na raiz do projeto.
6. Mova todos os 22 arquivos Markdown de histórico e planejamento legados (incluindo `novo_plano_gpt.md`, `prompt_qwen3.md`, `RESUMO_FASE1.md` e a pasta inteira `markdown/`) para `docs/archive/`.
7. Adicione a pasta `docs/archive/` no `.gitignore` se preferir ocultar do controle de versão principal, ou apenas mantenha a pasta organizada no repositório.

# Success criteria
- O aplicativo inicia corretamente com `streamlit run app.py`.
- O arquivo `categories.json` continua sendo um JSON sintaticamente válido.
- A árvore de arquivos da raiz do projeto fica limpa e legível.

# Complexity
Low
