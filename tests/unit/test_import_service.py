import json
from pathlib import Path

import pytest
from tests.helpers.import_data import ImportTestClient

from handball.domain.imports import BladImportu, PrzebiegImportu, ZadaniePobrania
from handball.infrastructure.import_store import ImportFileStore
from handball.services.import_service import ImportService


class ImportTestRepository:
    def __init__(self) -> None:
        self.zapisy = 0
        self.brakujace: list[ZadaniePobrania] = []

    def pobierz_brakujace(self, ligi: list[int]) -> list[ZadaniePobrania]:
        return self.brakujace.copy()

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
