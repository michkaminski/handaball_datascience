from __future__ import annotations

import re
from pathlib import Path

import pytest

from handball.domain.attendance_appeal import POJECIA_MAF
from mathlib.registry import CONTENT_DIR, ArticleValidator, MathRegistry, default_registry
from mathlib.render import ArticleRenderer

KORZEN = Path(__file__).parents[2] / "src" / "handball" / "interface"


@pytest.fixture(scope="module")
def rejestr() -> MathRegistry:
    return default_registry()


def test_wszystkie_artykuly_przechodza_walidacje_struktury_linkow_i_kotwic(
    rejestr: MathRegistry,
) -> None:
    problemy = ArticleValidator(rejestr).validate()
    assert not problemy, [f"{problem.article}: {problem.message}" for problem in problemy]


def test_kazde_pojecie_ma_artykul_i_poprawne_powiazania(rejestr: MathRegistry) -> None:
    for pojecie in rejestr.concepts.values():
        assert rejestr.article_path(pojecie).exists(), pojecie.id
        assert rejestr.category(pojecie.category) is not None
        assert all(powiazane in rejestr.concepts for powiazane in pojecie.related)
        assert all(klucz in rejestr.bibliography for klucz in pojecie.bibliography)


def test_bibliografia_ma_weryfikowalny_identyfikator(rejestr: MathRegistry) -> None:
    for wpis in rejestr.bibliography.values():
        dane = wpis.data
        assert dane.get("doi") or dane.get("url") or dane.get("publisher"), wpis.key
        if dane.get("doi"):
            assert re.fullmatch(r"10\.\d{4,9}/\S+", str(dane["doi"])), wpis.key


def test_odnosniki_modelu_maf_prowadza_do_istniejacych_kotwic(rejestr: MathRegistry) -> None:
    walidator = ArticleValidator(rejestr)
    for klucz, (pojecie, kotwica) in POJECIA_MAF.items():
        assert pojecie in rejestr.concepts, klucz
        koncept = rejestr.concepts[pojecie]
        fragment = rejestr.resolve_anchor(koncept, kotwica)
        identyfikatory = walidator.ids_of(rejestr.concepts[koncept.article])
        assert fragment is None or fragment in identyfikatory, f"{klucz}: {pojecie}#{fragment}"


def test_kotwice_popovera_istnieja_dla_wszystkich_pojec_dashboardu(rejestr: MathRegistry) -> None:
    walidator = ArticleValidator(rejestr)
    for pojecie, _ in POJECIA_MAF.values():
        koncept = rejestr.concepts[pojecie]
        identyfikatory = walidator.ids_of(rejestr.concepts[koncept.article])
        for kotwica in ("definicja", "wzor", "wyprowadzenie", "przyklad"):
            fragment = rejestr.resolve_anchor(koncept, kotwica)
            assert fragment in identyfikatory, f"{pojecie}#{fragment}"


def test_dashboard_uzywa_tylko_zarejestrowanych_kluczy_metryk() -> None:
    zrodla = [
        KORZEN / "templates" / "admin" / "reports" / "attendance" / "maf_panel.html",
        KORZEN / "static" / "js" / "attendance_appeal.js",
    ]
    klucze: set[str] = set()
    for plik in zrodla:
        tresc = plik.read_text(encoding="utf-8")
        klucze |= set(re.findall(r'data-maf-info="([a-z_]+)"', tresc))
        klucze |= set(re.findall(r"ikonaInfo\('([a-z_]+)'\)", tresc))
        klucze |= set(re.findall(r"'([a-z_]+)'\]\)\.map", tresc))
    assert klucze, "nie znaleziono odwołań"
    assert klucze <= set(POJECIA_MAF), sorted(klucze - set(POJECIA_MAF))


def test_url_pojecia_i_alias(rejestr: MathRegistry) -> None:
    assert rejestr.url("rozklad-beta") == "/matematyka/rozklady-prawdopodobienstwa/rozklad-beta/"
    assert rejestr.url("z-score") == "/matematyka/podstawy-statystyki/standaryzacja/#z-score"
    assert rejestr.url("r-hat", "wzor") == "/matematyka/walidacja-modeli/r-hat/#eq-r-hat"
    with pytest.raises(KeyError):
        rejestr.url("nie-istnieje")


def test_renderer_rozwiazuje_linki_cytowania_i_numeruje_sekcje(rejestr: MathRegistry) -> None:
    artykul = ArticleRenderer(rejestr).render(rejestr.concepts["rozklad-beta"])
    assert 'data-concept="' in artykul.html and 'href="/matematyka/' in artykul.html
    assert "data-bib" in artykul.html and "doi.org" in artykul.html
    assert [wpis.number for wpis in artykul.toc if wpis.level == 2] == [
        str(numer) for numer in range(1, 14)
    ]


def test_suma_kontrolna_tresci_odpowiada_plikowi_checksum(rejestr: MathRegistry) -> None:
    zapisana = (CONTENT_DIR / "CHECKSUM").read_text(encoding="utf-8").strip()
    assert rejestr.checksum() == zapisana
