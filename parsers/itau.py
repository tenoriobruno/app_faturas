import pandas as pd
from utils.logger import get_logger

log = get_logger(__name__)


def parse_itau(filepath: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, encoding='latin-1')

    df = df.rename(columns={
        'Data': 'date',
        'Lançamento': 'title',
        'Descrição': 'title',
        'Estabelecimento': 'title',
        'Valor': 'amount',
        'Categoria': 'categoria'
    })

    required_cols = ['date', 'title', 'amount']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"CSV deve ter colunas: {', '.join(required_cols)}")

    if df['amount'].dtype == object:
        df['amount'] = (
            df['amount']
            .astype(str)
            .str.replace('R$', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .str.strip()
        )

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])

    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date'])

    df['tipo_transacao'] = 'gasto'
    df.loc[df['amount'] < 0, 'tipo_transacao'] = 'estorno'
    df.loc[df['amount'] == 0, 'tipo_transacao'] = 'ajuste'

    mask_pagamento = df['title'].str.lower().str.contains('saldo|pagamento', na=False)
    df = df[~( (df['tipo_transacao'] == 'ajuste') | mask_pagamento )]

    df = df.drop_duplicates(subset=['date', 'title', 'amount'], keep='first')

    matches = df['title'].str.extract(r'\s+(\d{1,2})/(\d{1,2})$')
    p_atual = pd.to_numeric(matches[0], errors='coerce')
    p_total = pd.to_numeric(matches[1], errors='coerce')
    valid_mask = (p_total > 1) & (p_total <= 24) & (p_atual <= p_total)

    df['parcela_atual'] = p_atual.where(valid_mask, 1).fillna(1).astype(int)
    df['total_parcelas'] = p_total.where(valid_mask, 1).fillna(1).astype(int)

    df.loc[valid_mask, 'title'] = df.loc[valid_mask, 'title'].str.replace(r'\s+\d{1,2}/\d{1,2}$', '', regex=True)

    if 'categoria' not in df.columns:
        df['categoria'] = None

    return df[['date', 'title', 'amount', 'tipo_transacao', 'categoria', 'parcela_atual', 'total_parcelas']].copy()