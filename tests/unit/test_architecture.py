import ast
from pathlib import Path

import pytest


@pytest.mark.parametrize("warstwa", ["domain", "contracts", "services"])
def test_wewnetrzne_warstwy_nie_importuja_prezentacji_ani_infrastruktury(warstwa: str) -> None:
    korzen = Path(__file__).parents[2] / "src" / "handball" / warstwa
    zabronione = ("flask", "sqlalchemy", "handball.interface", "handball.infrastructure")
    naruszenia = []
    for plik in korzen.rglob("*.py"):
        for wezel in ast.walk(ast.parse(plik.read_text(encoding="utf-8"))):
            if isinstance(wezel, ast.ImportFrom):
                moduly = [wezel.module or ""]
            elif isinstance(wezel, ast.Import):
                moduly = [alias.name for alias in wezel.names]
            else:
                continue
            for modul in moduly:
                if any(
                    modul == prefiks or modul.startswith(prefiks + ".") for prefiks in zabronione
                ):
                    naruszenia.append(f"{plik.name}:{wezel.lineno}: {modul}")
    assert not naruszenia, naruszenia
