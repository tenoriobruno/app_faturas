import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ROOT_DIR = Path(__file__).parent.parent
    DATA_PATH = Path(os.getenv("DATA_PATH", "."))
    CACHE_PATH = ROOT_DIR / "cache"
    BUDGET_PATH = ROOT_DIR / "config" / "budget.json"
    CATEGORIES_PATH = ROOT_DIR / "categories.json"
    DEFAULT_DARK_MODE = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Limiares de orçamento (frações 0-1) — únicos no app, usados por
    # components/budget.py e core/projections.py
    BUDGET_WARN_PCT = 0.8
    BUDGET_OVER_PCT = 1.0
    PROJECTION_WARN_PCT = 0.9

    BUDGET_COLOR_OK = "#2ECC71"
    BUDGET_COLOR_WARN = "#F39C12"
    BUDGET_COLOR_OVER = "#E74C3C"

    def get_category_names(self):
        with open(self.CATEGORIES_PATH, encoding='utf-8') as f:
            return list(json.load(f).keys())

    @staticmethod
    def budget_color(pct: float) -> str:
        """Cor associada a um percentual de uso de orçamento (pct em fração 0-1)."""
        if pct >= Settings.BUDGET_OVER_PCT:
            return Settings.BUDGET_COLOR_OVER
        if pct >= Settings.BUDGET_WARN_PCT:
            return Settings.BUDGET_COLOR_WARN
        return Settings.BUDGET_COLOR_OK

settings = Settings()
