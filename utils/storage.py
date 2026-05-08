import json
from pathlib import Path
import streamlit as st

CACHE_PATH = Path("cache/categories_cache.json")

def load_cache() -> dict:
    """Carrega o cache de categorias do arquivo JSON."""
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding='utf-8'))
        except Exception as e:
            st.error(f"Erro ao carregar cache: {e}")
            return {}
    return {}

def save_cache(cache: dict):
    """Salva o cache de categorias no arquivo JSON."""
    try:
        CACHE_PATH.parent.mkdir(exist_ok=True)
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        st.error(f"Erro ao salvar cache: {e}")
