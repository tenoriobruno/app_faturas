import pandas as pd
from data.repository import cache_repo
from utils.normalize import normalize

def save_manual_corrections(diff: pd.DataFrame):
    if diff.empty:
        return
    cache = cache_repo.load()
    for _, row in diff.iterrows():
        norm_title = normalize(row['title'])
        if norm_title:
            cache[norm_title] = {"categoria": row['categoria'], "source": "user"}
    cache_repo.save(cache)
