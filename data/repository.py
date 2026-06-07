import json
from pathlib import Path
from utils.logger import get_logger
from config.settings import settings

log = get_logger(__name__)

class JSONRepository:
    def __init__(self, filepath: Path):
        self.filepath = Path(filepath)

    def load(self) -> dict:
        if self.filepath.exists():
            try:
                return json.loads(self.filepath.read_text(encoding='utf-8'))
            except Exception as e:
                log.error(f"Erro ao carregar {self.filepath.name}: {e}")
                return {}
        return {}

    def save(self, data: dict):
        try:
            self.filepath.parent.mkdir(exist_ok=True, parents=True)
            self.filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception as e:
            log.error(f"Erro ao salvar {self.filepath.name}: {e}")

class CacheRepository(JSONRepository):
    def load(self) -> dict:
        data = super().load()
        migrated = {}
        for k, v in data.items():
            if isinstance(v, str):
                migrated[k] = {"categoria": v, "source": "local"}
            else:
                migrated[k] = v
        return migrated

    def invalidate_if_stale(self, reference_path: Path) -> bool:
        """Invalidates cache if reference_path is newer than cache."""
        if not self.filepath.exists() or reference_path.stat().st_mtime > self.filepath.stat().st_mtime:
            self.filepath.parent.mkdir(exist_ok=True, parents=True)
            self.filepath.write_text("{}", encoding="utf-8")
            return True
        return False



class IgnoredRecurrencesRepository(JSONRepository):
    def __init__(self):
        super().__init__(settings.CACHE_PATH / "ignored_recurrences.json")

    def add_recurrence(self, recurrence):
        data = super().load()
        if recurrence not in data.get("ignored_recurrences", []):
            data.setdefault("ignored_recurrences", []).append(recurrence)
            super().save(data)

    def get_ignored_recurrences(self):
        data = super().load()
        return data.get("ignored_recurrences", [])

    def __contains__(self, recurrence):
        data = super().load()
        return recurrence in data.get("ignored_recurrences", [])


class AuditLogRepository(JSONRepository):
    def __init__(self):
        super().__init__(settings.CACHE_PATH / "audit_log.json")

    def add_entry(self, timestamp: str, description: str, old_category, new_category: str, source: str):
        data = self.load()
        entries = data.get("entries", [])
        entries.append({
            "timestamp": timestamp,
            "description": description,
            "old_category": old_category,
            "new_category": new_category,
            "source": source
        })
        data["entries"] = entries
        self.save(data)

    def get_entries(self) -> list:
        data = self.load()
        return data.get("entries", [])


# Singletons
cache_repo = CacheRepository(settings.CACHE_PATH / "categories_cache.json")
budget_repo = JSONRepository(settings.BUDGET_PATH / "budget.json")
audit_repo = AuditLogRepository()
