import pandas as pd
from datetime import datetime
from data.repository import cache_repo, audit_repo
from utils.normalize import normalize


def save_manual_corrections(diff: pd.DataFrame, df_original: pd.DataFrame = None):
    if diff.empty:
        return
    cache = cache_repo.load()
    timestamp = datetime.now().isoformat()
    for idx, row in diff.iterrows():
        norm_title = normalize(row['title'])
        if norm_title:
            old_cat = None
            if df_original is not None and idx in df_original.index:
                old_cat = df_original.loc[idx, 'categoria']
            cache[norm_title] = {"categoria": row['categoria'], "source": "user"}
            audit_repo.add_entry(
                timestamp=timestamp,
                description=row['title'],
                old_category=old_cat,
                new_category=row['categoria'],
                source="user"
            )
    cache_repo.save(cache)