"""
Módulo de utilidades para normalização de texto das transações.
Remove acentos, caracteres especiais e números irrelevantes para facilitar o matching.
"""
import re
import unicodedata


def normalize(text: str) -> str:
    """
    Normaliza o texto da descrição da transação.
    
    1. Converte para minúsculo
    2. Remove acentos (NFD normalization)
    3. Remove datas no formato DD/MM
    4. Remove caracteres especiais
    5. Remove números longos (IDs de transação)
    6. Remove tokens curtos (< 2 caracteres)
    """
    if not isinstance(text, str):
        return ""

    # Minúsculo e remoção de acentos
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Remove datas (ex: 12/05)
    text = re.sub(r'\b\d{1,2}/\d{1,2}\b', '', text)
    
    # Remove caracteres especiais por espaço
    text = re.sub(r'[*@#$%&()[\]{}<>,.;:]', ' ', text)
    
    # Remove números longos (frequentemente IDs ou datas sem barra)
    text = re.sub(r'\d{6,}', '', text)
    
    # Tokenização e limpeza de tokens muito curtos
    tokens = text.split()
    tokens = [t for t in tokens if len(t) >= 2]

    return ' '.join(tokens).strip()
