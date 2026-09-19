import pytest

from handball.domain.imports import BladImportu, PrzebiegImportu, ZadaniePobrania
from handball.services.import_mapping import ZprpImportMapper


def _mapper() -> ZprpImportMapper:
    przebieg = PrzebiegImportu("test", [12007], "2026-01-01T00:00:00")
    return ZprpImportMapper(przebieg, "zrodlo")


def _mecz(**nadpisania: object) -> dict[str, object]:
    dane = {
        "Id": "206926",
        "ID_sezon": "195",
        "Id_rozgrywki": "12007",
        "Kategoria": "1",
        "ID_zespoly_gosp": "17588",
        "ID_zespoly_gosc": "18558",
    }
    dane.update(nadpisania)
    return dane


def test_szczegoly_nierozegranego_meczu_to_lista_bez_skladow() -> None:
    mapper = _mapper()
    mapper.szczegoly([[_mecz()]], {"cid": 12007, "did": 1, "mid": 206926})
    mecz = next(r for r in mapper._przebieg.rekordy if r.tabela == "mecze")
    assert mecz.klucz == {"id": 206926}
    assert not any(r.tabela == "mecze_zawodnicy" for r in mapper._przebieg.rekordy)


def test_szczegoly_nieprawidlowej_struktury_wskazuje_mecz() -> None:
    mapper = _mapper()
    with pytest.raises(BladImportu, match="206926"):
        mapper.szczegoly("cos innego", {"cid": 12007, "did": 1, "mid": 206926})


@pytest.mark.parametrize("dokument", [None, {}, [], {"0": []}, [[{}]], {"gosp": {}}])
def test_brak_naglowka_pomija_szczegoly_i_zachowuje_mecz(dokument: object) -> None:
    mapper = _mapper()
    kontekst = {"cid": 12007, "did": 1, "mid": 206926}
    mapper.mecz(_mecz(), kontekst)
    rekordy = list(mapper._przebieg.rekordy)
    mapper.szczegoly(dokument, kontekst)
    assert mapper._przebieg.rekordy == rekordy
    assert any(r.tabela == "mecze" for r in rekordy)


@pytest.mark.parametrize("dokument", [{}, []])
def test_pusta_kolejka_nie_blokuje_importu(dokument: object) -> None:
    mapper = _mapper()
    mapper.przetworz(
        ZadaniePobrania("pokaz_mecze.php", {"Kolejka": 1}, "mecze", {"cid": 12007, "did": 1}),
        dokument,
    )
    assert mapper._przebieg.rekordy == []
    assert mapper._przebieg.kolejka == []


@pytest.mark.parametrize("rodzaj", ["sezony", "rozgrywki", "rundy", "kolejki"])
def test_puste_dane_wymagane_nadal_zglaszaja_blad(rodzaj: str) -> None:
    with pytest.raises(BladImportu, match="Pusta odpowiedź"):
        _mapper().przetworz(ZadaniePobrania("test.php", {}, rodzaj), [])


@pytest.mark.parametrize("identyfikator", ["0", "999999"])
def test_bledny_id_w_obecnym_naglowku_nadal_blokuje_import(identyfikator: str) -> None:
    with pytest.raises(BladImportu):
        _mapper().szczegoly([[_mecz(Id=identyfikator)]], {"cid": 12007, "did": 1, "mid": 206926})
