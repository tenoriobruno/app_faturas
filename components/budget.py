import streamlit as st
import pandas as pd
import json
from pathlib import Path

BUDGET_PATH = Path("config/budget.json")

def load_budgets() -> dict:
    if BUDGET_PATH.exists():
        try:
            return json.loads(BUDGET_PATH.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}

def render_budget(df: pd.DataFrame):
    st.subheader("🎯 Acompanhamento de Orçamento")
    
    budgets = load_budgets()
    if not budgets:
        st.info("Nenhum orçamento configurado. Configure em `config/budget.json`.")
        return

    global_budget = budgets.get("global", 0)
    cat_budgets = budgets.get("categories", {})

    total_spent = df['amount'].sum()
    
    if global_budget > 0:
        pct_global = min(total_spent / global_budget, 1.0)
        st.write(f"**Global:** R$ {total_spent:,.2f} / R$ {global_budget:,.2f} ({pct_global*100:.1f}%)")
        st.progress(pct_global)
        if pct_global >= 1.0:
            st.error("Orçamento global estourado!")
        elif pct_global >= 0.8:
            st.warning("Atenção: 80% do orçamento global atingido.")
            
    if cat_budgets:
        st.write("**Por Categoria:**")
        cat_spent = df.groupby('categoria')['amount'].sum()
        for cat, limit in cat_budgets.items():
            spent = cat_spent.get(cat, 0)
            if limit > 0:
                pct_cat = min(spent / limit, 1.0)
                st.write(f"*{cat}:* R$ {spent:,.2f} / R$ {limit:,.2f}")
                st.progress(pct_cat)
