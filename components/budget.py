import streamlit as st
import pandas as pd
from data.repository import budget_repo
from core.projections import calculate_linear_projection


def render_budget(df: pd.DataFrame):
    st.subheader("🎯 Acompanhamento de Orçamento")

    budgets = budget_repo.load()
    if not budgets:
        st.info("Nenhum orçamento configurado. Configure no menu Editar abaixo.")
        budgets = {"global": 0, "categories": {}}

    global_budget = budgets.get("global", 0)
    cat_budgets = budgets.get("categories", {})

    projection = calculate_linear_projection(df, global_budget, cat_budgets)

    total_spent = df[df['tipo_transacao'] == 'gasto']['amount'].sum()

    if global_budget > 0:
        pct_global = min(total_spent / global_budget, 1.0)
        color = "#E74C3C" if pct_global >= 1.0 else "#F39C12" if pct_global >= 0.8 else "#2ECC71"

        proj_html = ""
        if projection['global_warning']:
            proj_html = (
                f'<span style="color:#E74C3C;font-size:0.8rem;font-weight:600;">'
                f'⚠️ Projeção: {projection["global_projection_pct"]:.1f}% do orçamento</span>'
            )

        st.markdown(
            f'<div class="glass-card" style="padding:16px 20px;">'
            f'<span style="font-weight:600;">Global</span> &nbsp;'
            f'<span style="color:var(--text-secondary);">R$ {total_spent:,.2f} / R$ {global_budget:,.2f} ({pct_global*100:.1f}%)</span>'
            f'<div style="background:var(--track-bg);border-radius:10px;margin-top:10px;">'
            f'<div style="width:{pct_global*100}%;background:{color};height:10px;border-radius:10px;transition:width 0.4s ease;"></div>'
            f'</div>'
            f'{proj_html}'
            f'</div>',
            unsafe_allow_html=True
        )

    if cat_budgets:
        st.write("**Por Categoria:**")
        cat_spent = df[df['tipo_transacao'] == 'gasto'].groupby('categoria')['amount'].sum()
        cat_proj = projection['cat_projections']

        for cat, limit in cat_budgets.items():
            spent = cat_spent.get(cat, 0)
            if limit > 0:
                pct_cat = min(spent / limit, 1.0)
                color_cat = "#E74C3C" if pct_cat >= 1.0 else "#2ECC71"

                proj_cat_html = ""
                if cat in cat_proj and cat_proj[cat]['warning']:
                    proj_cat_html = (
                        f'<span style="color:#E74C3C;font-size:0.75rem;font-weight:600;">'
                        f'⚠️ Projeção: {cat_proj[cat]["projected_pct"]:.1f}% do limite</span>'
                    )

                st.markdown(
                    f'<div class="glass-card" style="padding:12px 16px;margin-bottom:8px;">'
                    f'<span style="font-weight:600;">{cat}</span> &nbsp;'
                    f'<span style="color:var(--text-secondary);font-size:0.88rem;">R$ {spent:,.2f} / R$ {limit:,.2f}</span>'
                    f'<div style="background:var(--track-bg);border-radius:8px;margin-top:8px;">'
                    f'<div style="width:{pct_cat*100}%;background:{color_cat};height:8px;border-radius:8px;transition:width 0.4s ease;"></div>'
                    f'</div>'
                    f'{proj_cat_html}'
                    f'</div>',
                    unsafe_allow_html=True
                )

    render_budget_editor(df, budgets)


def render_budget_editor(df: pd.DataFrame, budgets: dict):
    with st.expander("✏️ Editar Orçamento"):
        global_budget = budgets.get("global", 0)
        cat_budgets = budgets.get("categories", {})

        new_global = st.number_input("Orçamento Global", min_value=0.0, value=float(global_budget), step=100.0)

        st.write("Orçamentos por Categoria:")
        new_cats = {}
        all_cats = list(df['categoria'].unique())
        for c in cat_budgets.keys():
            if c not in all_cats:
                all_cats.append(c)
        all_cats = [c for c in all_cats if c and c != "Outros"]

        configured = [c for c in all_cats if c in cat_budgets and cat_budgets[c] > 0]
        unconfigured = [c for c in all_cats if c not in configured]

        search = st.text_input("Filtrar categoria", key="budget_editor_filter")
        search_lower = search.strip().lower()

        def render_field(c):
            val = float(cat_budgets.get(c, 0.0))
            new_val = st.number_input(f"Orçamento - {c}", min_value=0.0, value=val, step=50.0, key=f"b_{c}".replace(" ", "_"))
            if new_val >= 0:
                new_cats[c] = new_val

        if configured:
            st.write("**Já configuradas:**")
            for c in configured:
                if not search_lower or search_lower in c.lower():
                    render_field(c)

        if unconfigured:
            st.write("**Sem limite definido:**")
            for c in unconfigured:
                if not search_lower or search_lower in c.lower():
                    render_field(c)

        if st.button("Salvar Orçamento"):
            new_b = {"global": new_global, "categories": new_cats}
            budget_repo.save(new_b)
            st.success("Orçamento salvo com sucesso!")
            st.rerun()