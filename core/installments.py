import pandas as pd

def calculate_future_installments(df_consolidated: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula parcelas futuras baseado no extrato.
    Retorna apenas um DataFrame limpo, sem comandos de UI.
    """
    if df_consolidated.empty or 'parcela_atual' not in df_consolidated.columns:
        return pd.DataFrame()
        
    df = df_consolidated.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    parceladas = df[df['total_parcelas'] > 1].copy()
    
    # Mantém a entrada mais recente
    parceladas = parceladas.sort_values('date').groupby(['title', 'amount', 'total_parcelas']).last().reset_index()
    
    return parceladas

def calculate_projection(parceladas: pd.DataFrame, last_data_date: pd.Timestamp) -> tuple[float, list]:
    total_remaining_debt = 0
    future_data = []
    
    for _, row in parceladas.iterrows():
        faltam = row['total_parcelas'] - row['parcela_atual']
        if faltam > 0:
            for i in range(1, int(faltam) + 1):
                future_month_date = pd.to_datetime(row['date']) + pd.DateOffset(months=i)
                
                if future_month_date > last_data_date:
                    total_remaining_debt += row['amount']
                    future_data.append({
                        'title': row['title'],
                        'amount': row['amount'],
                        'future_month': future_month_date.to_period('M')
                    })
    return total_remaining_debt, future_data
