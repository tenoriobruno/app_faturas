import pandas as pd
from data.repository import IgnoredRecurrencesRepository

def detect_recurrences(df_consolidated: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta assinaturas baseadas em transações com mesmo título ou categoria 'Assinaturas'
    que aparecem em 3 ou mais meses distintos.
    Retorna apenas um DataFrame limpo, sem comandos de UI.
    """
    if df_consolidated.empty:
        return pd.DataFrame()

    df = df_consolidated.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.to_period('M')

    # Detecta assinaturas com base na categoria ou número de meses
    recurrences = df.groupby('title').agg(
        months_count=('month_year', 'nunique'),
        avg_amount=('amount', 'mean'),
        last_date=('date', 'max'),
        categoria=('categoria', 'first')
    ).reset_index()

    # Considera recorrente se aparece em >= 3 meses distintos ou se a categoria for 'Assinaturas'
    mask = (recurrences['months_count'] >= 3) | (recurrences['categoria'] == 'Assinaturas')
    fixed_costs = recurrences[mask].sort_values(by='avg_amount', ascending=False)

    # Filtra assinaturas ignoradas
    ignored_repo = IgnoredRecurrencesRepository()
    fixed_costs = fixed_costs[~fixed_costs['title'].isin(ignored_repo.get_ignored_recurrences())]

    return fixed_costs
