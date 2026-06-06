import pandas as pd
from typing import Dict, Any

def calculate_overview_metrics(df_current: pd.DataFrame, df_previous: pd.DataFrame = None) -> Dict[str, Any]:
    df_gastos = df_current[df_current['tipo_transacao'] == 'gasto']
    total_tx = len(df_gastos)
    valor_total = df_gastos['amount'].sum() if total_tx > 0 else 0
    ticket_medio = df_gastos['amount'].mean() if total_tx > 0 else 0
    top_cat = df_gastos.groupby('categoria')['amount'].sum().idxmax() if total_tx > 0 else "N/A"
    
    outros_pct = (df_current['categoria'] == 'Outros').sum() / len(df_current) * 100 if len(df_current) > 0 else 0

    delta_tx, delta_valor, delta_ticket = None, None, None
    if df_previous is not None:
        prev_gastos = df_previous[df_previous['tipo_transacao'] == 'gasto']
        prev_tx = len(prev_gastos)
        prev_valor = prev_gastos['amount'].sum() if prev_tx > 0 else 0
        prev_ticket = prev_gastos['amount'].mean() if prev_tx > 0 else 0

        delta_tx = total_tx - prev_tx
        delta_valor = valor_total - prev_valor
        delta_ticket = ticket_medio - prev_ticket

    return {
        'total_tx': total_tx,
        'valor_total': valor_total,
        'ticket_medio': ticket_medio,
        'top_cat': top_cat,
        'outros_pct': outros_pct,
        'delta_tx': delta_tx,
        'delta_valor': delta_valor,
        'delta_ticket': delta_ticket
    }
