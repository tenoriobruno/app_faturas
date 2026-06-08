import pandas as pd
from datetime import datetime
import calendar
from typing import Dict, Any, List

from config.settings import settings


def calculate_linear_projection(df: pd.DataFrame, global_budget: float, cat_budgets: dict) -> Dict[str, Any]:
    """Project end-of-month spending, or report the closed-month result.

    If the DataFrame's reference month is the current month, projects spending
    linearly based on day-of-month progress (and computes a safe daily pace
    for the remaining days). If it's a past/closed month, reports the actual
    result instead — projecting a closed month inflates meaningless numbers.

    Returns per-category and global figures, plus warning flags:
    - current month: warning if projection >= PROJECTION_WARN_PCT of budget
    - closed month: warning if actual spend >= budget (estourou)
    """
    now = datetime.now()
    df_gastos = df[df['tipo_transacao'] == 'gasto']

    ref_date = df['date'].max() if len(df) > 0 else None
    is_current_month = bool(
        ref_date is not None and ref_date.year == now.year and ref_date.month == now.month
    )

    if ref_date is not None:
        days_in_month = calendar.monthrange(ref_date.year, ref_date.month)[1]
    else:
        days_in_month = calendar.monthrange(now.year, now.month)[1]

    today = now.day if is_current_month else days_in_month
    days_remaining = max(days_in_month - today, 0)
    progress = today / days_in_month if days_in_month else 0

    total_spent = df_gastos['amount'].sum()
    cat_spent = df_gastos.groupby('categoria')['amount'].sum()

    global_available = global_budget - total_spent if global_budget > 0 else None
    global_daily_pace = None

    if is_current_month:
        global_projection_pct = (total_spent / progress / global_budget * 100) if progress > 0 and global_budget > 0 else 0
        global_warning = global_projection_pct >= settings.PROJECTION_WARN_PCT * 100 and global_budget > 0
        if global_budget > 0 and days_remaining > 0:
            global_daily_pace = global_available / days_remaining
    else:
        global_projection_pct = (total_spent / global_budget * 100) if global_budget > 0 else 0
        global_warning = global_projection_pct >= settings.BUDGET_OVER_PCT * 100 and global_budget > 0

    cat_projections = {}
    for cat, limit in cat_budgets.items():
        if limit <= 0:
            continue
        spent = cat_spent.get(cat, 0)
        spent_pct = (spent / limit * 100)

        if is_current_month:
            projected = (spent / progress) if progress > 0 else 0
            projected_pct = (projected / limit * 100)
            warning = (projected / limit) >= settings.PROJECTION_WARN_PCT
        else:
            projected = spent
            projected_pct = spent_pct
            warning = (spent / limit) >= settings.BUDGET_OVER_PCT

        cat_projections[cat] = {
            'spent': spent,
            'limit': limit,
            'spent_pct': spent_pct,
            'projected': projected,
            'projected_pct': projected_pct,
            'warning': warning,
        }

    return {
        'is_current_month': is_current_month,
        'progress': progress,
        'days_in_month': days_in_month,
        'today': today,
        'days_remaining': days_remaining,
        'global_spent': total_spent,
        'global_available': global_available,
        'global_daily_pace': global_daily_pace,
        'global_projection_pct': global_projection_pct,
        'global_warning': global_warning,
        'cat_projections': cat_projections,
    }


def calculate_budget_adherence_history(df_consolidated: pd.DataFrame, global_budget: float, n_months: int = 6) -> List[Dict[str, Any]]:
    """% do orçamento global usado em cada um dos últimos N meses (histórico de aderência).

    Usa os meses presentes em df_consolidated. Retorna lista ordenada do mês
    mais antigo para o mais recente, com gasto total e percentual do orçamento.
    """
    if global_budget <= 0 or df_consolidated is None or df_consolidated.empty:
        return []

    df_hist = df_consolidated[df_consolidated['tipo_transacao'] == 'gasto'].copy()
    if df_hist.empty:
        return []

    df_hist['month'] = pd.to_datetime(df_hist['date']).dt.to_period('M')
    monthly_spent = df_hist.groupby('month')['amount'].sum().sort_index()
    monthly_spent = monthly_spent.tail(n_months)

    return [
        {
            'month': str(period),
            'spent': spent,
            'pct': (spent / global_budget * 100),
        }
        for period, spent in monthly_spent.items()
    ]
