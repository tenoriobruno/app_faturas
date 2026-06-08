import streamlit as st
import pandas as pd
from data.repository import budget_repo
from core.projections import calculate_linear_projection, calculate_budget_adherence_history
from config.settings import settings


def _load_budgets() -> dict:
    budgets = budget_repo.load()
    if not budgets:
        return {"global": 0, "categories": {}}
    return budgets


def render_budget(df: pd.DataFrame, df_consolidated: pd.DataFrame = None):
    st.subheader("🎯 Acompanhamento de Orçamento")

    budgets = _load_budgets()
    if not budget_repo.load():
        st.info("Nenhum orçamento configurado. Configure no menu Editar abaixo.")

    global_budget = budgets.get("global", 0)
    cat_budgets = budgets.get("categories", {})

    projection = calculate_linear_projection(df, global_budget, cat_budgets)
    is_current = projection['is_current_month']

    total_spent = df[df['tipo_transacao'] == 'gasto']['amount'].sum()

    if global_budget > 0:
        pct_global = min(total_spent / global_budget, 1.0)
        color = settings.budget_color(pct_global)

        extra_html = ""
        if is_current:
            if projection['global_warning']:
                extra_html = (
                    f'<span style="color:{settings.BUDGET_COLOR_OVER};font-size:0.8rem;font-weight:600;">'
                    f'⚠️ Projeção: {projection["global_projection_pct"]:.1f}% do orçamento</span><br>'
                )
            available = projection['global_available']
            pace = projection['global_daily_pace']
            if available is not None:
                if available >= 0:
                    pace_txt = f' &nbsp;·&nbsp; Ritmo seguro: R$ {pace:,.2f}/dia pelos próximos {projection["days_remaining"]} dia(s)' if pace is not None else ''
                    extra_html += (
                        f'<span style="font-size:0.8rem;color:var(--text-secondary);">'
                        f'💡 Disponível: R$ {available:,.2f} restantes{pace_txt}</span>'
                    )
                else:
                    extra_html += (
                        f'<span style="font-size:0.8rem;color:{settings.BUDGET_COLOR_OVER};font-weight:600;">'
                        f'🚨 Orçamento estourado em R$ {-available:,.2f}</span>'
                    )
        else:
            if projection['global_warning']:
                extra_html = (
                    f'<span style="color:{settings.BUDGET_COLOR_OVER};font-size:0.8rem;font-weight:600;">'
                    f'❌ Fechou estourado em {projection["global_projection_pct"]:.1f}% do orçamento</span>'
                )
            else:
                extra_html = (
                    f'<span style="color:{settings.BUDGET_COLOR_OK};font-size:0.8rem;font-weight:600;">'
                    f'✅ Fechou em {projection["global_projection_pct"]:.1f}% do orçamento</span>'
                )

        st.markdown(
            f'<div class="glass-card" style="padding:16px 20px;">'
            f'<span style="font-weight:600;">Global</span> &nbsp;'
            f'<span style="color:var(--text-secondary);">R$ {total_spent:,.2f} / R$ {global_budget:,.2f} ({pct_global*100:.1f}%)</span>'
            f'<div style="background:var(--track-bg);border-radius:10px;margin-top:10px;">'
            f'<div style="width:{pct_global*100}%;background:{color};height:10px;border-radius:10px;transition:width 0.4s ease;"></div>'
            f'</div>'
            f'<div style="margin-top:8px;">{extra_html}</div>'
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
                color_cat = settings.budget_color(pct_cat)

                proj_cat_html = ""
                if cat in cat_proj and cat_proj[cat]['warning']:
                    if is_current:
                        proj_cat_html = (
                            f'<span style="color:{settings.BUDGET_COLOR_OVER};font-size:0.75rem;font-weight:600;">'
                            f'⚠️ Projeção: {cat_proj[cat]["projected_pct"]:.1f}% do limite</span>'
                        )
                    else:
                        proj_cat_html = (
                            f'<span style="color:{settings.BUDGET_COLOR_OVER};font-size:0.75rem;font-weight:600;">'
                            f'❌ Fechou estourado: {cat_proj[cat]["spent_pct"]:.1f}% do limite</span>'
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

    render_adherence_history(df_consolidated, global_budget)
    render_budget_editor(df, budgets)


def render_adherence_history(df_consolidated: pd.DataFrame, global_budget: float):
    """Histórico de aderência: % do orçamento global usado nos últimos meses."""
    if df_consolidated is None or global_budget <= 0:
        return

    history = calculate_budget_adherence_history(df_consolidated, global_budget)
    if len(history) < 2:
        return

    with st.expander("📊 Histórico de Aderência ao Orçamento Global"):
        for h in history:
            pct = min(h['pct'] / 100, 1.0)
            color = settings.budget_color(pct)
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
                f'<span style="font-size:0.8rem;color:var(--text-secondary);width:64px;">{h["month"]}</span>'
                f'<div style="flex:1;background:var(--track-bg);border-radius:8px;">'
                f'<div style="width:{pct*100}%;background:{color};height:8px;border-radius:8px;"></div>'
                f'</div>'
                f'<span style="font-size:0.8rem;color:var(--text-secondary);width:54px;text-align:right;">{h["pct"]:.0f}%</span>'
                f'</div>',
                unsafe_allow_html=True
            )


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


def render_budget_sidebar_summary(df: pd.DataFrame):
    """Resumo compacto do orçamento global na sidebar — sempre visível."""
    budgets = _load_budgets()
    global_budget = budgets.get("global", 0)
    if global_budget <= 0:
        return

    total_spent = df[df['tipo_transacao'] == 'gasto']['amount'].sum()
    pct = min(total_spent / global_budget, 1.0)
    color = settings.budget_color(pct)

    st.sidebar.markdown(
        f'<div style="margin:4px 4px 12px;padding:10px 12px;border-radius:8px;background:var(--card-bg, rgba(255,255,255,0.04));">'
        f'<span style="font-size:0.78rem;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.03em;">🎯 Orçamento</span><br>'
        f'<span style="font-size:0.85rem;">R$ {total_spent:,.0f} / R$ {global_budget:,.0f} ({pct*100:.0f}%)</span>'
        f'<div style="background:var(--track-bg);border-radius:8px;margin-top:6px;">'
        f'<div style="width:{pct*100}%;background:{color};height:6px;border-radius:8px;"></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
