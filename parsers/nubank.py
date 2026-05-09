"""
Módulo responsável pelo processamento de arquivos CSV exportados pelo Nubank.
Realiza limpeza, normalização de nomes de colunas e deduplicação.
"""
import pandas as pd


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

    # Limpeza básica: garante tipos numéricos e remove vazios
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])

    # Filtra apenas gastos (valores positivos no CSV do Nubank)
    # Nota: No CSV do Nubank, pagamentos de fatura costumam ser negativos ou zero
    df = df[df['amount'] > 0]

    # Deduplicação baseada na tríade data/título/valor
    df = df.drop_duplicates(subset=['date', 'title', 'amount'], keep='first')

    # Extrai informações de parcelamento (ex: "Compra xpto 02/05")
    # Captura padrão " [número]/[número]" no final da string
    matches = df['title'].str.extract(r'\s+(\d{1,2})/(\d{1,2})$')
    df['parcela_atual'] = pd.to_numeric(matches[0]).fillna(1).astype(int)
    df['total_parcelas'] = pd.to_numeric(matches[1]).fillna(1).astype(int)
    
    # Remove a info de parcela do título para não atrapalhar agrupamentos
    df['title'] = df['title'].str.replace(r'\s+\d{1,2}/\d{1,2}$', '', regex=True)

    # Garante que a coluna categoria existe (mesmo que vazia)
    if 'categoria' not in df.columns:
        df['categoria'] = None

    return df[['date', 'title', 'amount', 'categoria', 'parcela_atual', 'total_parcelas']].copy()
