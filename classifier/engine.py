"""
Motor de classificação que orquestra a normalização e as regras de negócio.
Serve como interface principal para classificar uma ou várias transações.
"""
import pandas as pd
from classifier.local_rules import classify_local
from utils.normalize import normalize
from utils.storage import load_cache, save_cache


_cache = None

def get_cache():
    global _cache
    if _cache is None:
        _cache = load_cache()
    return _cache

def classify(description: str) -> str:
    """
    Pipeline de classificação para uma única descrição:
    1. Normaliza o texto (remove ruído)
    2. Consulta o cache persistente
    3. Tenta classificação local (keywords/regex)
    4. Atualiza cache e retorna resultado
    """
    normalized = normalize(description)
    if not normalized:
        return "Outros"

    cache = get_cache()
    if normalized in cache:
        return cache[normalized]

    result = classify_local(normalized)
    
    if not result or result == "Outros":
        from classifier.llm_fallback import classify_with_llm
        result = classify_with_llm(description) or "Outros"
    
    # Atualiza cache em memória e persiste
    cache[normalized] = result
    save_cache(cache)
    
    return result


def classify_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica a classificação em lote a um DataFrame.
    Identifica automaticamente se deve usar a coluna 'title' ou 'description'.
    Preserva categorias já preenchidas no CSV.
    """
    df = df.copy()

    # Identifica a coluna de descrição (title ou description)
    desc_col = "description" if "description" in df.columns else "title"

    if "categoria" not in df.columns:
        df["categoria"] = None

    # Só classifica as linhas onde a categoria está vazia ou é NaN
    mask = df["categoria"].isna() | (df["categoria"].astype(str).str.strip() == "")
    
    if mask.any():
        df.loc[mask, "categoria"] = df.loc[mask, desc_col].apply(classify)

    return df
