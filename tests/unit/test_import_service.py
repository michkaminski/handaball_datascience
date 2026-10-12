import json
from pathlib import Path

import pytest
from tests.helpers.import_data import ImportTestClient

from handball.domain.imports import (
    BladImportu,
    MeczImportu,
    OpcjaImportu,
    PrzebiegImportu,
    ZadaniePobrania,
)
from handball.infrastructure.import_store import ImportFileStore
from handball.services.import_service import ImportService


class ImportTestRepository:
    def __init__(self) -> None:
        self.zapisy = 0
        self.brakujace: list[ZadaniePobrania] = []
        self.mecze = {
            206511: MeczImportu(206511, 12007, 66727, "LOTTO Superliga", "A – B"),
            206512: MeczImportu(206512, 12009, 66728, "Superliga kobiet", "C – D"),
        }

    def pobierz_brakujace(self, ligi: list[int]) -> list[ZadaniePobrania]:
        return self.brakujace.copy()

    def pobierz_mecz(self, id_mecz: int) -> MeczImportu | None:
        return self.mecze.get(id_mecz)

    def pobierz_mecze(self, id_mecze: list[int]) -> list[MeczImportu]:
        return [
            self.mecze[identyfikator] for identyfikator in id_mecze if identyfikator in self.mecze
        ]

    def pobierz_sezony(self) -> list[OpcjaImportu]:
        return [OpcjaImportu(195, "2026/2027"), OpcjaImportu(194, "2025/2026")]

    def pobierz_rozgrywki_sezonu(self, id_sezon: int) -> list[OpcjaImportu]:
        return {
            195: [OpcjaImportu(12007, "LOTTO Superliga"), OpcjaImportu(12016, "I Liga Grupa A")],
            194: [OpcjaImportu(11592, "Superpuchar Polski kobiet")],
        }[id_sezon]

    def porownaj(self, przebieg: PrzebiegImportu) -> None:
        for rekord in przebieg.rekordy:
            rekord.zmiany = dict(rekord.dane)

    def zastosuj(self, przebieg: PrzebiegImportu) -> int:
        self.zapisy += 1
        return 42


def test_pobranie_podglad_zapis_i_wznowienie(tmp_path: Path) -> None:
    klient = ImportTestClient()
    repo = ImportTestRepository()
    magazyn = ImportFileStore(tmp_path)
    serwis = ImportService(magazyn, klient, repo)
    przebieg = serwis.rozpocznij([12007])
    with pytest.raises(BladImportu):
        serwis.zastosuj(przebieg.id)
    klient.awaria = True
    assert serwis.krok(przebieg.id).status == "BLAD"
    assert len(magazyn.pobierz(przebieg.id).kolejka) == 2
    klient.awaria = False
    serwis = ImportService(ImportFileStore(tmp_path), klient, repo)
    for _ in range(20):
        przebieg = serwis.krok(przebieg.id)
        if przebieg.status != "POBIERANIE":
            break
    assert przebieg.status == "PODGLAD", przebieg.blad
    assert repo.zapisy == 0
    mecz = next(r for r in przebieg.rekordy if r.tabela == "mecze")
    assert mecz.dane["zamiana"] is True
    assert mecz.dane["wynik_gosp_full"] == 29
    assert mecz.dane["wynik_gosc_full"] is None
    assert mecz.dane["id_zespol_gosc"] is None
    assert klient.zapytania.count("pokaz_sklad.php") == 1
    zawodnik = next(r for r in przebieg.rekordy if r.tabela == "mecze_zawodnicy")
    assert zawodnik.klucz["strona"] == "gosp"
    assert len(mecz.zrodla) == 2
    assert serwis.zastosuj(przebieg.id).status == "ZAPISANO"
    assert serwis.zastosuj(przebieg.id).id_przebieg_bazy == 42
    assert repo.zapisy == 1


@pytest.mark.parametrize("ligi", [[], [12007, 1], [12008]])
def test_odrzuca_niedozwolony_zakres(tmp_path: Path, ligi: list[int]) -> None:
    serwis = ImportService(ImportFileStore(tmp_path), ImportTestClient(), ImportTestRepository())
    with pytest.raises(BladImportu):
        serwis.rozpocznij(ligi)


def test_trwale_nieudane_zadanie_jest_pomijane_a_import_idzie_dalej(tmp_path: Path) -> None:
    klient = ImportTestClient()
    klient.awarie_dla["pokaz_sezony.php"] = 10
    magazyn = ImportFileStore(tmp_path)
    serwis = ImportService(magazyn, klient, ImportTestRepository())
    przebieg = serwis.rozpocznij([12007])
    for _ in range(20):
        przebieg = serwis.krok(przebieg.id)
        if przebieg.status in ("PODGLAD", "ZAPISANO"):
            break
    assert przebieg.status == "PODGLAD", przebieg.blad
    assert len(przebieg.pominiete) == 1
    assert przebieg.pominiete[0]["endpoint"] == "pokaz_sezony.php"
    assert przebieg.nieudane_probowania == {}


class NiepelneDaneTestClient(ImportTestClient):
    def __init__(self, pusta_lista: object, szczegoly: object) -> None:
        super().__init__()
        self._pusta_lista = pusta_lista
        self._szczegoly = szczegoly

    def pobierz(self, zadanie: ZadaniePobrania) -> tuple[str, bytes]:
        url, tresc = super().pobierz(zadanie)
        if zadanie.endpoint == "pokaz_mecze.php" and zadanie.parametry["Kolejka"] == 999:
            return url, json.dumps(self._pusta_lista).encode()
        if zadanie.endpoint == "pokaz_mecze_szczegoly.php":
            return url, json.dumps(self._szczegoly).encode()
        return url, tresc


@pytest.mark.parametrize("pusta_lista", [[], {}])
@pytest.mark.parametrize("szczegoly", [None, {}, [], {"0": []}])
def test_pomija_braki_i_konczy_podgladem(
    tmp_path: Path, pusta_lista: object, szczegoly: object
) -> None:
    klient = NiepelneDaneTestClient(pusta_lista, szczegoly)
    repo = ImportTestRepository()
    magazyn = ImportFileStore(tmp_path)
    serwis = ImportService(magazyn, klient, repo)
    przebieg = serwis.rozpocznij([12007])
    with magazyn.edytuj(przebieg.id) as zapisany:
        zapisany.kolejka.insert(
            0,
            ZadaniePobrania(
                "pokaz_mecze.php", {"Kolejka": 999}, "mecze", {"cid": 12007, "did": 999}
            ),
        )
    for _ in range(20):
        przebieg = serwis.krok(przebieg.id)
        assert przebieg.status != "BLAD", przebieg.blad
        if przebieg.status == "PODGLAD":
            break
    assert przebieg.status == "PODGLAD"
    assert przebieg.kolejka == []
    assert przebieg.blad is None
    assert klient.zapytania.count("pokaz_mecze.php") == 2
    assert klient.zapytania.count("pokaz_mecze_szczegoly.php") == 1
    assert "pokaz_sklad.php" in klient.zapytania
    assert any(r.tabela == "mecze" for r in przebieg.rekordy)
    assert not any(r.tabela == "mecze_zawodnicy" for r in przebieg.rekordy)
    assert repo.zapisy == 0


def test_import_uzupelniajacy_pobiera_tylko_wskazane_szczegoly(tmp_path: Path) -> None:
    repo = ImportTestRepository()
    repo.brakujace = [
        ZadaniePobrania(
            "pokaz_mecze_szczegoly.php",
            {"Zawody": 206511},
            "szczegoly",
            {"mid": 206511, "cid": 12007, "did": 66727},
        )
    ]
    klient = ImportTestClient()
    serwis = ImportService(ImportFileStore(tmp_path), klient, repo)
    przebieg = serwis.rozpocznij([12007], "uzupelniajacy")
    assert przebieg.tryb == "uzupelniajacy"
    assert klient.zapytania == []
    przebieg = serwis.krok(przebieg.id)
    assert przebieg.status == "PODGLAD"
    assert klient.zapytania == ["pokaz_mecze_szczegoly.php"]
    assert przebieg.kolejka == []
    assert all(r.uzupelnij for r in przebieg.rekordy)
    assert any(r.tabela == "zawodnicy" and r.klucz == {"id": 100} for r in przebieg.rekordy)
    assert any(r.tabela == "mecze_zawodnicy" for r in przebieg.rekordy)
    assert repo.zapisy == 0
    assert serwis.magazyn.pobierz(przebieg.id).tryb == "uzupelniajacy"


def test_brak_kandydatow_nie_powoduje_pobierania(tmp_path: Path) -> None:
    klient = ImportTestClient()
    serwis = ImportService(ImportFileStore(tmp_path), klient, ImportTestRepository())
    przebieg = serwis.rozpocznij([12007], "uzupelniajacy")
    assert przebieg.status == "PODGLAD"
    assert przebieg.rekordy == []
    assert serwis.krok(przebieg.id).status == "PODGLAD"
    assert klient.zapytania == []


def test_odrzuca_nieznany_tryb(tmp_path: Path) -> None:
    serwis = ImportService(ImportFileStore(tmp_path), ImportTestClient(), ImportTestRepository())
    with pytest.raises(BladImportu, match="tryb"):
        serwis.rozpocznij([12007], "nieznany")


def test_stary_przebieg_bez_trybu_jest_pelnym_importem() -> None:
    dokument = {"id": "test", "ligi": [12007], "rozpoczecie": "2026-09-19"}
    assert PrzebiegImportu(**dokument).tryb == "pelny"


def test_opcje_tabel_domyslnie_wybieraja_biezacy_sezon(tmp_path: Path) -> None:
    serwis = ImportService(ImportFileStore(tmp_path), ImportTestClient(), ImportTestRepository())
    opcje = serwis.opcje_tabel()
    assert opcje.wybrany_sezon == OpcjaImportu(195, "2026/2027")
    assert [r.id for r in opcje.rozgrywki] == [12007, 12016]
    assert serwis.opcje_tabel(194).rozgrywki == [OpcjaImportu(11592, "Superpuchar Polski kobiet")]
    assert serwis.opcje_tabel(999).wybrany_sezon == OpcjaImportu(195, "2026/2027")


def test_import_tabel_pobiera_tylko_tabele_wybranego_sezonu(tmp_path: Path) -> None:
    klient = ImportTestClient()
    repo = ImportTestRepository()
    serwis = ImportService(ImportFileStore(tmp_path), klient, repo)
    przebieg = serwis.rozpocznij_tabele(194, [11592])
    assert przebieg.tryb == "tabele" and przebieg.nazwa_trybu == "Tylko tabele"
    assert (przebieg.id_sezon, przebieg.nazwa_sezonu) == (194, "2025/2026")
    assert przebieg.nazwy_rozgrywek == ["Superpuchar Polski kobiet"]
    for _ in range(10):
        przebieg = serwis.krok(przebieg.id)
        if przebieg.status != "POBIERANIE":
            break
    assert przebieg.status == "PODGLAD", przebieg.blad
    assert klient.zapytania == ["pokaz_tabele_spis.php", "pokaz_tabela.php", "pokaz_tabela.php"]
    tabele = {r.tabela for r in przebieg.rekordy}
    assert tabele == {
        "tabele",
        "tabele_grupy",
        "tabele_wiersze",
        "zespoly",
        "zespoly_sezony",
        "zespoly_rozgrywki",
    }
    druzyna_sezonu = next(r for r in przebieg.rekordy if r.tabela == "zespoly_sezony")
    assert druzyna_sezonu.klucz["id_sezon"] == 194 and druzyna_sezonu.uzupelnij is True
    assert serwis.zastosuj(przebieg.id).status == "ZAPISANO"


@pytest.mark.parametrize(("sezon", "ligi"), [(194, []), (194, [12007]), (999, [12007])])
def test_import_tabel_odrzuca_rozgrywki_spoza_sezonu(
    tmp_path: Path, sezon: int, ligi: list[int]
) -> None:
    serwis = ImportService(ImportFileStore(tmp_path), ImportTestClient(), ImportTestRepository())
    with pytest.raises(BladImportu):
        serwis.rozpocznij_tabele(sezon, ligi)


def test_stary_przebieg_bez_sezonu_dotyczy_sezonu_2026_2027() -> None:
    przebieg = PrzebiegImportu("x", [12007], "2026-01-01T00:00:00")
    assert (przebieg.id_sezon, przebieg.nazwa_sezonu) == (195, "2026/2027")
    assert przebieg.nazwy_rozgrywek == ["Superliga mężczyzn"]


def test_import_jednego_meczu_pobiera_tylko_jego_szczegoly(tmp_path: Path) -> None:
    repo = ImportTestRepository()
    klient = ImportTestClient()
    serwis = ImportService(ImportFileStore(tmp_path), klient, repo)
    przebieg = serwis.rozpocznij_mecz(206511)
    assert przebieg.tryb == "mecz"
    assert przebieg.ligi == [12007]
    assert przebieg.id_mecz == 206511
    assert przebieg.nazwy_rozgrywek == ["LOTTO Superliga"]
    assert przebieg.nazwa_trybu == "Jeden mecz"
    przebieg = serwis.krok(przebieg.id)
    assert przebieg.status == "PODGLAD"
    assert klient.zapytania == ["pokaz_mecze_szczegoly.php"]
    assert not any(
        r.uzupelnij for r in przebieg.rekordy if r.tabela in ("mecze", "mecze_zawodnicy")
    )
    mecz = next(r for r in przebieg.rekordy if r.tabela == "mecze")
    assert mecz.klucz == {"id": 206511}
    assert mecz.dane["id_kolejka"] == 66727 and mecz.dane["wynik_gosp_full"] == 29
    assert any(r.tabela == "mecze_zawodnicy" for r in przebieg.rekordy)
    assert serwis.zastosuj(przebieg.id).status == "ZAPISANO"
    assert repo.zapisy == 1
    assert serwis.magazyn.pobierz(przebieg.id).id_mecz == 206511


def test_import_wybranych_meczow_pobiera_tylko_ich_szczegoly(tmp_path: Path) -> None:
    repo = ImportTestRepository()
    klient = ImportTestClient()
    serwis = ImportService(ImportFileStore(tmp_path), klient, repo)
    przebieg = serwis.rozpocznij_mecze([206512, 206511, 206512])
    assert przebieg.tryb == "mecze"
    assert przebieg.id_mecze == [206512, 206511]
    assert przebieg.ligi == [12007, 12009]
    assert przebieg.nazwa_trybu == "Wybrane mecze"
    assert przebieg.dopisek_meczow == "2 mecze"
    assert [zadanie.parametry["Zawody"] for zadanie in przebieg.kolejka] == [206512, 206511]
    for _ in range(5):
        przebieg = serwis.krok(przebieg.id)
        if przebieg.status != "POBIERANIE":
            break
    assert przebieg.status == "PODGLAD", przebieg.blad
    assert klient.zapytania == ["pokaz_mecze_szczegoly.php", "pokaz_mecze_szczegoly.php"]
    identyfikatory = {r.klucz["id"] for r in przebieg.rekordy if r.tabela == "mecze"}
    assert identyfikatory == {206511, 206512}
    assert serwis.zastosuj(przebieg.id).status == "ZAPISANO"
    assert repo.zapisy == 1


def test_import_jednego_zaznaczenia_zostaje_trybem_jednego_meczu(tmp_path: Path) -> None:
    serwis = ImportService(ImportFileStore(tmp_path), ImportTestClient(), ImportTestRepository())
    przebieg = serwis.rozpocznij_mecze([206511])
    assert przebieg.tryb == "mecz"
    assert przebieg.id_mecz == 206511
    assert przebieg.id_mecze == []


@pytest.mark.parametrize(
    "id_mecze",
    [[], [0], [206511, 999999], list(range(1, 82))],
)
def test_import_wybranych_meczow_odrzuca_zly_wybor(tmp_path: Path, id_mecze: list[int]) -> None:
    klient = ImportTestClient()
    serwis = ImportService(ImportFileStore(tmp_path), klient, ImportTestRepository())
    with pytest.raises(BladImportu):
        serwis.rozpocznij_mecze(id_mecze)
    assert klient.zapytania == []
    assert serwis.magazyn.historia() == []


def test_stary_przebieg_bez_listy_meczow_sie_wczytuje(tmp_path: Path) -> None:
    magazyn = ImportFileStore(tmp_path)
    dokument = {
        "id": "a" * 32,
        "ligi": [12007],
        "rozpoczecie": "2026-01-01T00:00:00",
        "status": "ZAPISANO",
        "kolejka": [],
        "wykonane": [],
        "skroty_zrodel": {},
        "rekordy": [],
        "blad": None,
        "id_przebieg_bazy": 1,
        "tryb": "mecz",
        "nieudane_probowania": {},
        "pominiete": [],
        "id_sezon": 195,
        "nazwa_sezonu": "2026/2027",
        "nazwy_lig": {},
        "id_mecz": 206511,
        "opis": "A – B",
    }
    with magazyn.polaczenie() as polaczenie:
        polaczenie.execute("INSERT INTO przebiegi VALUES (?, ?)", ("a" * 32, json.dumps(dokument)))
        polaczenie.commit()
    przebieg = magazyn.pobierz("a" * 32)
    assert przebieg.id_mecz == 206511
    assert przebieg.id_mecze == []
    assert przebieg.dopisek_meczow == "mecz 206511"


@pytest.mark.parametrize("id_mecz", [0, 999999])
def test_import_jednego_meczu_odrzuca_nieznany_mecz(tmp_path: Path, id_mecz: int) -> None:
    klient = ImportTestClient()
    serwis = ImportService(ImportFileStore(tmp_path), klient, ImportTestRepository())
    with pytest.raises(BladImportu):
        serwis.rozpocznij_mecz(id_mecz)
    assert klient.zapytania == []
    assert serwis.magazyn.historia() == []
