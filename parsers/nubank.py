"""
Módulo responsável pelo processamento de arquivos CSV exportados pelo Nubank.
Realiza limpeza, normalização de nomes de colunas e deduplicação.
"""
import pandas as pd
from utils.logger import get_logger

log = get_logger(__name__)


def parse_nubank(filepath: str) -> pd.DataFrame:
    """
    Lê um arquivo CSV do Nubank e retorna um DataFrame padronizado.
    
    Argumentos:
        filepath: Caminho para o arquivo .csv
        
    Retorna:
        pd.DataFrame com colunas ['date', 'title', 'amount', 'categoria']
    """
    # Tenta ler com UTF-8, cai para Latin-1 se falhar (Nubank varia)
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, encoding='latin-1')

    # Padroniza nomes de colunas para uso interno
    df = df.rename(columns={
        'Data': 'date',
        'Descrição': 'title',
        'Valor': 'amount',
        'Categoria': 'categoria'
    })

    # Caso o usuário tenha adicionado uma 4ª coluna sem cabeçalho padrão
    # ou se for o formato "Data,Descrição,Valor,Categoria"
    if 'categoria' not in df.columns and len(df.columns) >= 4:
        # Se a última coluna não for uma das obrigatórias, assumimos que é a categoria
        potential_cat_col = df.columns[-1]
        if potential_cat_col not in ['date', 'title', 'amount', 'Data', 'Descrição', 'Valor']:
            df = df.rename(columns={potential_cat_col: 'categoria'})

    # Validação de colunas obrigatórias
    required_cols = ['date', 'title', 'amount']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"CSV deve ter colunas: {', '.join(required_cols)}")

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])

    # tipo_transacao: >0 gasto, <0 estorno, 0 ajuste
    df['tipo_transacao'] = 'gasto'
    df.loc[df['amount'] < 0, 'tipo_transacao'] = 'estorno'
    df.loc[df['amount'] == 0, 'tipo_transacao'] = 'ajuste'

    # Filtramos transações de ajuste ou pagamento de fatura, mas mantemos estornos
    mask_pagamento = df['title'].str.lower().str.contains('saldo|pagamento', na=False)
    df = df[~( (df['tipo_transacao'] == 'ajuste') | mask_pagamento )]

    # Deduplicação baseada na tríade data/título/valor
    df = df.drop_duplicates(subset=['date', 'title', 'amount'], keep='first')

    # Extrai informações de parcelamento (ex: "Compra xpto 02/05")
    matches = df['title'].str.extract(r'\s+(\d{1,2})/(\d{1,2})$')
    
    # Guards matemáticos para evitar capturar tamanho de roupa ou números de rua como parcela
    p_atual = pd.to_numeric(matches[0], errors='coerce')
    p_total = pd.to_numeric(matches[1], errors='coerce')
    valid_mask = (p_total > 1) & (p_total <= 24) & (p_atual <= p_total)
    
    df['parcela_atual'] = p_atual.where(valid_mask, 1).fillna(1).astype(int)
    df['total_parcelas'] = p_total.where(valid_mask, 1).fillna(1).astype(int)
    
    # Remove a info de parcela do título apenas se for válido
    df.loc[valid_mask, 'title'] = df.loc[valid_mask, 'title'].str.replace(r'\s+\d{1,2}/\d{1,2}$', '', regex=True)

    # Garante que a coluna categoria existe (mesmo que vazia)
    if 'categoria' not in df.columns:
        df['categoria'] = None

    return df[['date', 'title', 'amount', 'tipo_transacao', 'categoria', 'parcela_atual', 'total_parcelas']].copy()
