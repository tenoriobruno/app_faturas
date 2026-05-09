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
    
    if not mask.any():
        return df

    cache = get_cache()
    before_len = len(cache)
    
    for idx, row in df[mask].iterrows():
        desc = row[desc_col]
        normalized = normalize(desc)
        
        if not normalized:
            df.at[idx, "categoria"] = "Outros"
            continue
            
        if normalized in cache:
            df.at[idx, "categoria"] = cache[normalized]["categoria"]
            continue
            
        local_cat = classify_local(normalized)
        if local_cat and local_cat != "Outros":
            df.at[idx, "categoria"] = local_cat
            cache[normalized] = {"categoria": local_cat, "source": "local"}
            continue
            
        # fallback LLM line-by-line (mantido simples conforme instrucao de evitar batch)
        # O usuário solicitou deixar o ponto de LLM para depois, então vamos tratar caso a lib não exista.
        try:
            from classifier.llm_fallback import classify_with_llm
            llm_cat = classify_with_llm(desc) or "Outros"
        except ImportError:
            llm_cat = "Outros"
            
        df.at[idx, "categoria"] = llm_cat
        cache[normalized] = {"categoria": llm_cat, "source": "ai"}
        
    if len(cache) > before_len:
        save_cache(cache)

    return df
