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
