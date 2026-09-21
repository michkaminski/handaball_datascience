from datetime import datetime

from handball.domain.errors import NieZnalezionoSedziego
from handball.domain.referee_details import (
    AktywnoscSezonuSedziego,
    FiltryMeczowSedziego,
    MeczSedziego,
    StatystykaDruzynySedziego,
    StatystykaPartneraSedziego,
    StatystykaRozgrywekSedziego,
    StatystykaSezonRozgrywkiSedziego,
    StatystykiSedziego,
    StronaMeczowSedziego,
    SzczegolySedziego,
)


class SzczegolySedziegoInMemoryRepository:
    def __init__(self) -> None:
        self.filtry_meczow: FiltryMeczowSedziego | None = None
        self.filtry_statystyk: FiltryMeczowSedziego | None = None

    def pobierz_szczegoly(self, id_sedzia: int) -> SzczegolySedziego:
        if id_sedzia != 11:
            raise NieZnalezionoSedziego(id_sedzia)
        return SzczegolySedziego(
            11, "Kowalski Jan", "Płock", datetime(2020, 9, 1), datetime(2026, 5, 1), 34, 5, 3, 18
        )

    def pobierz_mecze(self, id_sedzia: int, filtry: FiltryMeczowSedziego) -> StronaMeczowSedziego:
        self.filtry_meczow = filtry
        return StronaMeczowSedziego(
            [
                MeczSedziego(
                    101,
                    datetime(2026, 2, 1, 18),
                    "2025/2026",
                    "Superliga",
                    "Wisła Płock",
                    31,
                    28,
                    "Kielce",
                    ((12, "Nowak Adam"),),
                )
            ],
            1,
            filtry.strona,
            filtry.rozmiar_strony,
        )

    def pobierz_statystyki(
        self, id_sedzia: int, filtry: FiltryMeczowSedziego
    ) -> StatystykiSedziego:
        self.filtry_statystyk = filtry
        sezony = [AktywnoscSezonuSedziego(195, "2025/2026", 18, ("Superliga", "Puchar Polski"))]
        rozgrywki = [StatystykaRozgrywekSedziego("Superliga", 15)]
        historia = [StatystykaSezonRozgrywkiSedziego("2025/2026", "Superliga", 15)]
        druzyny = [StatystykaDruzynySedziego(1, "Wisła Płock", 14, 8, 6)]
        partnerzy = [StatystykaPartneraSedziego(12, "Nowak Adam", 20)]
        return StatystykiSedziego(18, 1, 2, 1, sezony, rozgrywki, historia, druzyny, partnerzy)
