import importlib
from pathlib import Path

import pytest

from handball.contracts.pdf_renderer import GeneratorPdfNiedostepny
from handball.infrastructure.pdf_renderer import WeasyPrintPdfRenderer


def test_brak_bibliotek_pango_zglasza_niedostepny_generator(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def brak_biblioteki(nazwa: str) -> None:
        raise OSError(f"cannot load library {nazwa}")

    monkeypatch.setattr(importlib, "import_module", brak_biblioteki)
    with pytest.raises(GeneratorPdfNiedostepny, match="WEASYPRINT_DLL_DIRECTORIES"):
        WeasyPrintPdfRenderer(tmp_path).renderuj("<p>test</p>", [])


def test_weasyprint_tworzy_pdf_a4_z_arkuszem(tmp_path: Path) -> None:
    try:
        importlib.import_module("weasyprint")
    except OSError:
        pytest.skip("WeasyPrint bez bibliotek Pango w tym środowisku")
    arkusz = tmp_path / "druk.css"
    arkusz.write_text("@page{size:A4}", encoding="utf-8")
    pdf = WeasyPrintPdfRenderer(tmp_path).renderuj(
        '<p style="break-after:page">Zażółć</p><p>gęślą jaźń</p>', [arkusz]
    )
    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")
