from __future__ import annotations

import importlib
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType

from handball.contracts.pdf_renderer import GeneratorPdfNiedostepny


class WeasyPrintPdfRenderer:
    KOMUNIKAT_BRAKU = (
        "Generator PDF (WeasyPrint) nie znalazł bibliotek Pango. Zainstaluj MSYS2 i pakiet "
        "mingw-w64-x86_64-pango (instrukcja w README), a potem uruchom serwer przez run.bat "
        "albo wskaż katalog DLL w zmiennej WEASYPRINT_DLL_DIRECTORIES."
    )

    def __init__(self, katalog_bazowy: Path) -> None:
        self._katalog_bazowy = katalog_bazowy

    def renderuj(self, html: str, arkusze: Sequence[Path]) -> bytes:
        weasyprint = self._biblioteka()
        dokument = weasyprint.HTML(string=html, base_url=str(self._katalog_bazowy))
        wynik: bytes = dokument.write_pdf(
            stylesheets=[weasyprint.CSS(filename=str(arkusz)) for arkusz in arkusze]
        )
        return wynik

    def _biblioteka(self) -> ModuleType:
        try:
            return importlib.import_module("weasyprint")
        except (ImportError, OSError) as wyjatek:
            raise GeneratorPdfNiedostepny(self.KOMUNIKAT_BRAKU) from wyjatek
