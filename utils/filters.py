import pandas as pd

def apply_filters(df: pd.DataFrame, search_text: str, selected_cats: list, val_range: tuple, date_range: tuple, tipos: list, hide_outros: bool, only_outros: bool) -> pd.DataFrame:
    df_filtered = df.copy()
    
    if search_text:
        mask = df_filtered['title'].str.contains(search_text, case=False, na=False)
        df_filtered = df_filtered[mask]
        
    if selected_cats:
        df_filtered = df_filtered[df_filtered['categoria'].isin(selected_cats)]
        
    if val_range and len(val_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['amount'] >= val_range[0]) & 
            (df_filtered['amount'] <= val_range[1])
        ]
        
    if date_range and len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['date'].dt.date >= date_range[0]) & 
            (df_filtered['date'].dt.date <= date_range[1])
        ]
        
    if tipos:
        df_filtered = df_filtered[df_filtered['tipo_transacao'].isin(tipos)]
        
    if hide_outros:
        df_filtered = df_filtered[df_filtered['categoria'] != 'Outros']
        
    if only_outros:
        df_filtered = df_filtered[df_filtered['categoria'] == 'Outros']
        
    return df_filtered
