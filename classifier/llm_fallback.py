import json
import google.generativeai as genai
from config.settings import settings

# Tenta configurar o genai se a chave estiver presente
api_key = settings.GEMINI_API_KEY
if api_key:
    genai.configure(api_key=api_key)

def load_categories_schema():
    cat_path = settings.CATEGORIES_PATH
    if cat_path.exists():
        categories = json.loads(cat_path.read_text(encoding='utf-8'))
        return list(categories.keys())
    return []

def classify_with_llm(description: str) -> str:
    """Classifica a descrição usando o Gemini caso as regras locais falhem."""
    if not api_key:
        return "Outros"
        
    categories = load_categories_schema()
    if not categories:
        return "Outros"
        
    categories_str = ", ".join(categories)
    
    prompt = f"""
    Você é um assistente de classificação financeira.
    Classifique a transação "{description}" em EXATAMENTE UMA das seguintes categorias:
    [{categories_str}]
    
    Responda APENAS com o nome exato da categoria, sem aspas, pontuação ou texto adicional.
    Se não for possível determinar com clareza, responda: Outros
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Valida se a resposta é uma categoria válida
        if result in categories:
            return result
        return "Outros"
    except Exception:
        return "Outros"
