import json
from pathlib import Path
from utils.logger import get_logger
from config.settings import settings

log = get_logger(__name__)

def load_cache() -> dict:
    """Carrega o cache de categorias do arquivo JSON e migra para a nova estrutura."""
    cache_path = Path(settings.CACHE_PATH)
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding='utf-8'))
            migrated = {}
            for k, v in data.items():
                if isinstance(v, str):
                    migrated[k] = {"categoria": v, "source": "local"}
                else:
                    migrated[k] = v
            return migrated
        except Exception as e:
            log.error(f"Erro ao carregar cache: {e}")
            return {}
    return {}

def save_cache(cache: dict):
    """Salva o cache de categorias no arquivo JSON."""
    cache_path = Path(settings.CACHE_PATH)
    try:
        cache_path.parent.mkdir(exist_ok=True, parents=True)
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        log.error(f"Erro ao salvar cache: {e}")
