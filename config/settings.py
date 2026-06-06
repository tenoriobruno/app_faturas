import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ROOT_DIR = Path(__file__).parent.parent
    DATA_PATH = Path(os.getenv("DATA_PATH", "."))
    CACHE_PATH = ROOT_DIR / "cache" / "categories_cache.json"
    BUDGET_PATH = ROOT_DIR / "config" / "budget.json"
    CATEGORIES_PATH = ROOT_DIR / "categories.json"
    DEFAULT_DARK_MODE = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    def get_category_names(self):
        with open(self.CATEGORIES_PATH, encoding='utf-8') as f:
            return list(json.load(f).keys())

settings = Settings()
