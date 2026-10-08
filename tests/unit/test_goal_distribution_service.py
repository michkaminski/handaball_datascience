from datetime import datetime

import pytest

from handball.domain.goal_distribution import (
    FiltryRozkladuBramek,
    LiniaWyniku,
    MeczRozkladu,
    OpcjaFiltrow,
    OpcjeFiltrowRozkladu,
    RodzajSerii,
)
from handball.services.goal_distribution_service import RozkladBramekService


class RozkladPamieciowy:
    def __init__(self) -> None:
        self.filtry: FiltryRozkladuBramek | None = None

    def pobierz_opcje(self) -> OpcjeFiltrowRozkladu:
        return OpcjeFiltrowRozkladu(
            sezony=(OpcjaFiltrow("195", "2025/2026"),),
            rozgrywki=(OpcjaFiltrow("Superliga", "Superliga"),),
        )

    def pobierz_wyniki(self, filtry: FiltryRozkladuBramek) -> tuple[LiniaWyniku, ...]:
        self.filtry = filtry
        return (LiniaWyniku(30, 28, 4), LiniaWyniku(25, 25, 2))

    def pobierz_mecze(
        self, filtry: FiltryRozkladuBramek, rodzaj: RodzajSerii, bramki: int
    ) -> tuple[MeczRozkladu, ...]:
        self.wybor = (filtry, rodzaj, bramki)
        return (
            MeczRozkladu(
                7, datetime(2026, 3, 1, 18, 30), "2025/2026", "Superliga", "Kielce", "Wisła", 30, 28
            ),
        )


def test_serwis_sklada_raport_z_wynikow_repozytorium() -> None:
    repozytorium = RozkladPamieciowy()
    filtry = FiltryRozkladuBramek(id_sezon=195, rozgrywki="Superliga", plec="M")

    raport = RozkladBramekService(repozytorium).pobierz_raport(filtry)

    assert repozytorium.filtry == filtry
    assert raport.suma.liczba_meczow == 6
    assert raport.gospodarze.dominanty == (30,)
    assert raport.goscie.dominanty == (28,)


def test_serwis_przekazuje_wybor_meczow_i_odrzuca_ujemne_bramki() -> None:
    repozytorium = RozkladPamieciowy()
    filtry = FiltryRozkladuBramek()

    mecze = RozkladBramekService(repozytorium).pobierz_mecze(filtry, RodzajSerii.GOSPODARZE, 30)

    assert repozytorium.wybor == (filtry, RodzajSerii.GOSPODARZE, 30)
    assert mecze[0].wynik_etykieta == "30:28"
    assert mecze[0].data_etykieta == "2026-03-01 18:30"
    with pytest.raises(ValueError):
        RozkladBramekService(repozytorium).pobierz_mecze(filtry, RodzajSerii.SUMA, -1)
