from parsers.nubank import parse_nubank
from parsers.itau import parse_itau
from utils.logger import get_logger

log = get_logger(__name__)


def detect_bank(filepath: str) -> str:
    for enc in ('utf-8', 'latin-1'):
        try:
            with open(filepath, 'r', encoding=enc) as f:
                header = f.readline().strip().lower()
            break
        except UnicodeDecodeError:
            continue
    else:
        return 'nubank'
    if any(token in header for token in ('estabelecimento', 'lançamento')):
        return 'itau'
    return 'nubank'


def parse_csv(filepath: str):
    bank = detect_bank(filepath)
    log.info(f"Detectado banco: {bank} para {filepath}")
    if bank == 'itau':
        return parse_itau(filepath)
    return parse_nubank(filepath)