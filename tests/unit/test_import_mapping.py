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


def _mapper_tabel() -> tuple[ZprpImportMapper, PrzebiegImportu]:
    przebieg = PrzebiegImportu(
        "tabele", [12007], "2026-01-01T00:00:00", tryb="tabele", id_sezon=194
    )
    return ZprpImportMapper(przebieg, "zrodlo"), przebieg


def test_spis_tabel_tworzy_tabele_grupy_i_zadania_dla_kazdej_grupy() -> None:
    mapper, przebieg = _mapper_tabel()
    mapper.przetworz(
        ZadaniePobrania(
            "pokaz_tabele_spis.php", {"Rozgrywki": 12007}, "tabele_spis", {"cid": 12007}
        ),
        {
            "1": {"tabela_id": "1", "tabela_nazwa": "Runda zasadnicza"},
            "2": {
                "tabela_id": "2",
                "tabela_nazwa": "Play-off",
                "menu2": {"1": {"tabela_Id2": "5", "tabela_nazwa2": "Grupa mistrzowska"}},
            },
        },
    )
    grupy = [r for r in przebieg.rekordy if r.tabela == "tabele_grupy"]
    assert [g.klucz["grupa_id"] for g in grupy] == [0, 5]
    assert grupy[1].klucz["id_tabela"] == {
        "tabela": "tabele",
        "klucz": {"id_rozgrywki": 12007, "tabela_id": 2},
    }
    assert grupy[1].dane["grupa_nazwa"] == "Grupa mistrzowska"
    assert [z.parametry for z in przebieg.kolejka] == [
        {"Rozgrywki": 12007, "Tabela": 1, "Tabela2": 0},
        {"Rozgrywki": 12007, "Tabela": 2, "Tabela2": 5},
    ]


def test_tabela_mapuje_wiersze_miejsca_i_kryteria_z_naglowka() -> None:
    mapper, przebieg = _mapper_tabel()
    mapper.przetworz(
        ZadaniePobrania("pokaz_tabela.php", {}, "tabela", {"cid": 12007, "tid": 1, "gid": 0}),
        {
            "1": {"ID_zespoly": "14066", "Nazwa": "Lubin", "PunktyZdobyte": "9", "Zd_St": "20"},
            "2": {"ID_zespoly": "0"},
            "3": {"ID_zespoly": "14059", "Nazwa": "Lublin", "PunktyEx": None},
            "0": {"NazwaRozgrywek": "Superliga", "Kryteria": "Kryteria: P_Zd"},
        },
    )
    wiersze = [r for r in przebieg.rekordy if r.tabela == "tabele_wiersze"]
    assert [(w.klucz["id_zespol"], w.dane["miejsce"]) for w in wiersze] == [(14066, 1), (14059, 3)]
    assert wiersze[0].dane["punkty_zdobyte"] == 9 and wiersze[0].dane["zd_st"] == "20"
    assert wiersze[0].dane["kryteria"] == "Kryteria: P_Zd"
    assert wiersze[1].dane["punkty_ex"] is None
    assert wiersze[0].klucz["id_tabela_grupa"]["klucz"]["grupa_id"] == 0
    assert not przebieg.kolejka


@pytest.mark.parametrize("dokument", [None, [], {}])
def test_brak_tabel_w_rozgrywkach_nie_blokuje_importu(dokument: object) -> None:
    mapper, przebieg = _mapper_tabel()
    mapper.przetworz(
        ZadaniePobrania("pokaz_tabele_spis.php", {}, "tabele_spis", {"cid": 12007}), dokument
    )
    assert przebieg.rekordy == [] and przebieg.kolejka == []
