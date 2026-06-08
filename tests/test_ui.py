import pytest
from config.settings import settings

def test_default_dark_mode_setting():
    """Verifica se a configuração padrão de modo escuro está definida corretamente."""
    assert hasattr(settings, "DEFAULT_DARK_MODE")
    assert isinstance(settings.DEFAULT_DARK_MODE, bool)

def test_category_colors_exist():
    """Garante que a paleta de cores contém cores para categorias esperadas."""
    from config.categories import CATEGORY_COLORS
    assert "Outros" in CATEGORY_COLORS
    assert CATEGORY_COLORS["Outros"] == "#B0B3B8"

