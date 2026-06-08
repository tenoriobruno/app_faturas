import re
from config.categories import CATEGORY_COLORS
from config.settings import settings


def test_every_category_has_color():
    """Toda categoria definida em categories.json deve ter cor no palette."""
    names = settings.get_category_names()
    missing = [n for n in names if n not in CATEGORY_COLORS]
    assert missing == [], f"Categorias sem cor no palette: {missing}"


def test_all_colors_are_valid_hex():
    for cat, color in CATEGORY_COLORS.items():
        assert re.fullmatch(r"#[0-9A-Fa-f]{6}", color), f"Cor inválida em {cat}: {color}"
