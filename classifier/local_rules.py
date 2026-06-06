"""
Módulo de classificação baseado em regras locais (keywords e regex).
Consome o arquivo categories.json e aplica lógica de prioridade.
"""
import json
import re
from typing import Optional
import streamlit as st
from config.settings import settings

@st.cache_data
def load_categories():
    """Carrega as definições de categorias do arquivo JSON na raiz do projeto."""
    with open(settings.CATEGORIES_PATH, encoding='utf-8') as f:
        return json.load(f)


def classify_local(description: str, categories: dict = None) -> Optional[str]:
    """
    Classifica uma descrição baseada em keywords e regex.
    
    A lógica segue uma ordem estrita de precedência:
    1. Passa por TODAS as keywords de TODAS as categorias (quem casar primeiro vence).
    2. Se nenhum keyword casou, passa por TODOS os regex de TODAS as categorias.
    
    Isso garante que matches exatos de texto (ex: '99food') tenham prioridade 
    sobre matches genéricos (ex: 'restaurante').
    """
    if categories is None:
        categories = load_categories()
    desc_lower = description.lower()

    # 1. PASSA 1: Verifica todas as keywords de todas as categorias na ordem do JSON
    for category, rules in categories.items():
        for keyword in rules.get("keywords", []):
            if keyword.lower() in desc_lower:
                return category

    # 2. PASSA 2: Verifica todos os regex na ordem do JSON (fallback se keywords falharem)
    for category, rules in categories.items():
        for pattern in rules.get("regex", []):
            if re.search(pattern, description, re.IGNORECASE):
                return category

    return None
