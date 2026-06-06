import pandas as pd
from datetime import datetime
import calendar
from typing import Dict, Any


def calculate_linear_projection(df: pd.DataFrame, global_budget: float, cat_budgets: dict) -> Dict[str, Any]:
    """Project end-of-month spending based on day-of-month progress.

    Returns per-category and global projection percentages, plus flag if
    projected spending exceeds 90% of budget.
    """
    today = datetime.now().day
    days_in_month = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
    progress = today / days_in_month

    df_gastos = df[df['tipo_transacao'] == 'gasto']

    total_spent = df_gastos['amount'].sum()
    global_projection_pct = (total_spent / progress / global_budget * 100) if progress > 0 and global_budget > 0 else 0
    global_warning = global_projection_pct >= 90 and global_budget > 0

    cat_spent = df_gastos.groupby('categoria')['amount'].sum()
    cat_projections = {}
    for cat, limit in cat_budgets.items():
        if limit <= 0:
            continue
        spent = cat_spent.get(cat, 0)
        projected = (spent / progress) if progress > 0 else 0
        cat_projections[cat] = {
            'spent': spent,
            'limit': limit,
            'projected': projected,
            'projected_pct': (projected / limit * 100),
            'warning': (projected / limit) >= 0.9,
        }

    return {
        'progress': progress,
        'days_in_month': days_in_month,
        'today': today,
        'global_projection_pct': global_projection_pct,
        'global_warning': global_warning,
        'cat_projections': cat_projections,
    }