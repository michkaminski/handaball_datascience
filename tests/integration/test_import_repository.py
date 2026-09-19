import os
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from handball.domain.imports import BladImportu
from handball.infrastructure.import_store import ImportFileStore
from handball.infrastructure.repositories.import_repository import ImportSQLAlchemyRepository
from handball.services.import_service import ImportService
from tests.helpers.import_data import ImportTestClient


@pytest.mark.skipif(
    not os.environ.get("HDS_TEST_DATABASE_URL"), reason="Wymaga izolowanego PostgreSQL"
)
def test_transakcja_audyt_idempotencja_konflikt_i_rollback(tmp_path: Path) -> None:
    adres = make_url(os.environ["HDS_TEST_DATABASE_URL"])
    assert adres.host in ("localhost", "127.0.0.1")
    assert adres.database == "hds_import_test" and adres.port != 5432
    silnik = create_engine(adres, execution_options={"postgresql_readonly": True})
    magazyn = ImportFileStore(tmp_path)
    repo = ImportSQLAlchemyRepository(silnik, magazyn)
    klient = ImportTestClient()
    serwis = ImportService(magazyn, klient, repo)
    przebieg = serwis.rozpocznij([12007])
    for _ in range(20):
        przebieg = serwis.krok(przebieg.id)
        if przebieg.status != "POBIERANIE":
            break
    assert przebieg.status == "PODGLAD", przebieg.blad
    zapis = serwis.zastosuj(przebieg.id)
    assert zapis.status == "ZAPISANO", zapis.blad
    assert repo.zastosuj(przebieg) == zapis.id_przebieg_bazy
    with silnik.connect() as c:
        assert c.execute(text("SHOW transaction_read_only")).scalar_one() == "on"
        mecz = c.execute(text("SELECT * FROM public.mecze WHERE id=206511")).mappings().one()
        assert mecz["wynik_gosp_full"] == 29
        assert mecz["wynik_gosc_full"] is None
        assert mecz["id_zespol_gosc"] is None
        assert mecz["id_hala"] is not None
        assert (
            c.execute(text("SELECT count(*) FROM logs.mecze_log WHERE id=206511")).scalar_one() >= 1
        )
        liczba_logow = c.execute(text("SELECT count(*) FROM logs.mecze_log")).scalar_one()
        liczba_plikow = c.execute(text("SELECT count(*) FROM public.pliki_zrodlowe")).scalar_one()
        c.rollback()
    ponowny = deepcopy(przebieg)
    ponowny.id = uuid4().hex
    for zrodlo in przebieg.wykonane:
        url, tresc = magazyn.zrodlo(przebieg.id, zrodlo)
        magazyn.zapisz_zrodlo(ponowny.id, zrodlo, url, tresc)
    repo.porownaj(ponowny)
    assert ponowny.podsumowanie["nowe"] == 0
    assert ponowny.podsumowanie["zmienione"] == 0
    repo.zastosuj(ponowny)
    with silnik.connect() as c:
        assert c.execute(text("SELECT count(*) FROM logs.mecze_log")).scalar_one() == liczba_logow
        assert (
            c.execute(text("SELECT count(*) FROM public.pliki_zrodlowe")).scalar_one()
            == liczba_plikow
        )
        c.rollback()
    poprawka = deepcopy(ponowny)
    poprawka.id = uuid4().hex
    for zrodlo in przebieg.wykonane:
        url, tresc = magazyn.zrodlo(przebieg.id, zrodlo)
        magazyn.zapisz_zrodlo(poprawka.id, zrodlo, url, tresc)
    zmiana = next(r for r in poprawka.rekordy if r.tabela == "mecze")
    zmiana.dane["wynik_gosp_full"] = 30
    repo.porownaj(poprawka)
    nieaktualny = deepcopy(poprawka)
    nieaktualny.id = uuid4().hex
    repo.zastosuj(poprawka)
    with pytest.raises(BladImportu, match="Baza zmieniła"):
        repo.zastosuj(nieaktualny)
    bledny = deepcopy(poprawka)
    bledny.id = uuid4().hex
    for zrodlo in przebieg.wykonane:
        url, tresc = magazyn.zrodlo(przebieg.id, zrodlo)
        magazyn.zapisz_zrodlo(bledny.id, zrodlo, url, tresc)
    next(r for r in bledny.rekordy if r.tabela == "mecze").dane["wynik_gosp_full"] = 31
    next(r for r in bledny.rekordy if r.tabela == "mecze_zawodnicy").dane["bramki"] = 999999
    repo.porownaj(bledny)
    with pytest.raises(BladImportu):
        repo.zastosuj(bledny)
    with silnik.connect() as c:
        assert (
            c.execute(text("SELECT wynik_gosp_full FROM public.mecze WHERE id=206511")).scalar_one()
            == 30
        )
        assert (
            c.execute(
                text(
                    "SELECT count(*) FROM logs.import_przebiegi WHERE parametry->>'hds_id'='test-blad'"
                )
            ).scalar_one()
            == 0
        )
        c.rollback()
    silnik.dispose()
