import streamlit as st
import pandas as pd
from data.repository import budget_repo

def render_budget(df: pd.DataFrame):
    st.subheader("🎯 Acompanhamento de Orçamento")
    
    budgets = budget_repo.load()
    if not budgets:
        st.info("Nenhum orçamento configurado. Configure no menu Editar abaixo.")
        budgets = {"global": 0, "categories": {}}

    global_budget = budgets.get("global", 0)
    cat_budgets = budgets.get("categories", {})

    total_spent = df[df['tipo_transacao'] == 'gasto']['amount'].sum()
    
    if global_budget > 0:
        pct_global = min(total_spent / global_budget, 1.0)
        color = "#E74C3C" if pct_global >= 1.0 else "#F39C12" if pct_global >= 0.8 else "#2ECC71"
        st.markdown(
            f'<div class="glass-card" style="padding:16px 20px;">'
            f'<span style="font-weight:600;">Global</span> &nbsp;'
            f'<span style="color:var(--text-secondary);">R$ {total_spent:,.2f} / R$ {global_budget:,.2f} ({pct_global*100:.1f}%)</span>'
            f'<div style="background:var(--track-bg);border-radius:10px;margin-top:10px;">'
            f'<div style="width:{pct_global*100}%;background:{color};height:10px;border-radius:10px;transition:width 0.4s ease;"></div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
            
    if cat_budgets:
        st.write("**Por Categoria:**")
        cat_spent = df[df['tipo_transacao'] == 'gasto'].groupby('categoria')['amount'].sum()
        for cat, limit in cat_budgets.items():
            spent = cat_spent.get(cat, 0)
            if limit > 0:
                pct_cat = min(spent / limit, 1.0)
                color_cat = "#E74C3C" if pct_cat >= 1.0 else "#2ECC71"
                st.markdown(
                    f'<div class="glass-card" style="padding:12px 16px;margin-bottom:8px;">'
                    f'<span style="font-weight:600;">{cat}</span> &nbsp;'
                    f'<span style="color:var(--text-secondary);font-size:0.88rem;">R$ {spent:,.2f} / R$ {limit:,.2f}</span>'
                    f'<div style="background:var(--track-bg);border-radius:8px;margin-top:8px;">'
                    f'<div style="width:{pct_cat*100}%;background:{color_cat};height:8px;border-radius:8px;transition:width 0.4s ease;"></div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
                
    with st.expander("✏️ Editar Orçamento"):
        new_global = st.number_input("Orçamento Global", min_value=0.0, value=float(global_budget), step=100.0)
        
        st.write("Orçamentos por Categoria:")
        new_cats = {}
        all_cats = list(df['categoria'].unique())
        for c in cat_budgets.keys():
            if c not in all_cats: all_cats.append(c)
        all_cats = [c for c in all_cats if c and c != "Outros"]
        
        for c in all_cats:
            val = float(cat_budgets.get(c, 0.0))
            new_val = st.number_input(f"Orçamento - {c}", min_value=0.0, value=val, step=50.0, key=f"b_{c}".replace(" ", "_"))
            if new_val >= 0:
                new_cats[c] = new_val
                
        if st.button("Salvar Orçamento"):
            new_b = {"global": new_global, "categories": new_cats}
            budget_repo.save(new_b)
            st.success("Orçamento salvo com sucesso!")
            st.rerun()
