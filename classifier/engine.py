"""
Motor de classificação que orquestra a normalização e as regras de negócio.
Serve como interface principal para classificar uma ou várias transações.
"""
import pandas as pd
from classifier.local_rules import classify_local, load_categories
from utils.normalize import normalize
from data.repository import cache_repo

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

    cache = cache_repo.load()
    before_len = len(cache)
    categories = load_categories()
    
    for idx, row in df[mask].iterrows():
        desc = row[desc_col]
        normalized = normalize(desc)
        
        if not normalized:
            df.at[idx, "categoria"] = "Outros"
            continue
            
        if normalized in cache:
            df.at[idx, "categoria"] = cache[normalized]["categoria"]
            continue
            
        local_cat = classify_local(normalized, categories=categories)
        if local_cat and local_cat != "Outros":
            df.at[idx, "categoria"] = local_cat
            cache[normalized] = {"categoria": local_cat, "source": "local"}
            continue
            
        # Fallback para categoria indeterminada (LLM desativado)
        fallback_cat = "Outros"
        df.at[idx, "categoria"] = fallback_cat
        cache[normalized] = {"categoria": fallback_cat, "source": "local"}
        
    if len(cache) > before_len:
        cache_repo.save(cache)

    return df
