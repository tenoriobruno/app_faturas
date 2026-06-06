import pandas as pd
from typing import List, Dict, Any


def detect_anomalies(df: pd.DataFrame, df_consolidated: pd.DataFrame, sigma_threshold: float = 2.0) -> List[Dict[str, Any]]:
    """Detect category-level spending anomalies using standard deviation.

    Compares current-month category spending against historical monthly averages
    from df_consolidated. Flags categories where current spending exceeds
    mean + N * sigma.

    Returns list of dicts with category, current spend, avg, sigma, and excess_pct.
    """
    df_gastos = df[df['tipo_transacao'] == 'gasto']
    cat_current = df_gastos.groupby('categoria')['amount'].sum()

    if df_consolidated is None or df_consolidated.empty:
        return []

    df_hist = df_consolidated[df_consolidated['tipo_transacao'] == 'gasto'].copy()
    if df_hist.empty:
        return []

    df_hist['month'] = pd.to_datetime(df_hist['date']).dt.to_period('M')
    monthly_cat = df_hist.groupby(['month', 'categoria'])['amount'].sum().reset_index()
    cat_stats = monthly_cat.groupby('categoria')['amount'].agg(['mean', 'std']).fillna(0)

    anomalies = []
    for cat in cat_current.index:
        if cat not in cat_stats.index:
            continue
        mean_val = cat_stats.loc[cat, 'mean']
        std_val = cat_stats.loc[cat, 'std']
        if mean_val <= 0:
            continue

        current = cat_current[cat]
        threshold = mean_val + sigma_threshold * std_val

        if current > threshold:
            excess_pct = ((current - mean_val) / mean_val) * 100
            anomalies.append({
                'category': cat,
                'current_spend': current,
                'avg_spend': mean_val,
                'std_spend': std_val,
                'excess_pct': excess_pct,
            })

    anomalies.sort(key=lambda a: a['excess_pct'], reverse=True)
    return anomalies