from datetime import datetime
from decimal import Decimal

from handball.domain.errors import NieZnalezionoHali
from handball.domain.venue_details import (
    FiltryZawodnikowHali,
    FrekwencjaHali,
    KomorkaKalendarzaHali,
    LimityStatystykHali,
    PorownanieHali,
    ProfilWynikowHali,
    PrzedzialHali,
    RankingDruzynyHali,
    RankingRozgrywekHali,
    RankingZawodnikaHali,
    RekordMeczuHali,
    RozkladKalendarzaHali,
    StatystykiHali,
    StronaZawodnikowHali,
    SzczegolyHali,
    TrendSezonuHali,
    ZawodnikHali,
)


class SzczegolyHaliInMemoryRepository:
    def __init__(self) -> None:
        self.szczegoly = SzczegolyHali(
            7,
            "Hala Testowa",
            "Kielce",
            "Sportowa",
            "1",
            4200,
            datetime(2020, 9, 1, 18),
            datetime(2026, 5, 20, 20),
            128,
            120,
            6,
            7,
            14,
            80,
        )
        self.filtry: FiltryZawodnikowHali | None = None
        self.limity: LimityStatystykHali | None = None

    def pobierz_szczegoly(self, id_hala: int) -> SzczegolyHali:
        if id_hala != self.szczegoly.id_hala:
            raise NieZnalezionoHali(id_hala)
        return self.szczegoly

    def pobierz_zawodnikow(
        self, id_hala: int, filtry: FiltryZawodnikowHali
    ) -> StronaZawodnikowHali:
        self.filtry = filtry
        return StronaZawodnikowHali(
            [
                ZawodnikHali(
                    9,
                    "Jan",
                    "Bramkowy",
                    datetime(2021, 1, 2),
                    datetime(2026, 2, 3),
                    25,
                    100,
                    Decimal("4.00"),
                    ("Drużyna A",),
                )
            ],
            25,
            filtry.strona,
            filtry.rozmiar_strony,
        )

    def pobierz_statystyki(self, id_hala: int, limity: LimityStatystykHali) -> StatystykiHali:
        self.limity = limity
        druzyny = [
            RankingDruzynyHali(i, f"Drużyna {i}", 20 - i, 10, 2, 8 - i, 500, 450)
            for i in range(1, 12)
        ]
        rozgrywki = [
            RankingRozgrywekHali(f"Liga {i}", 20 - i, 3, "2022", "2026") for i in range(1, 12)
        ]
        zawodnicy = [
            RankingZawodnikaHali(
                i,
                f"Zawodnik {i}",
                20 - i,
                100 - i,
                Decimal("5.00"),
                ("Drużyna A",),
            )
            for i in range(1, 12)
        ]
        return StatystykiHali(
            druzyny if limity.druzyny is None else druzyny[: limity.druzyny],
            rozgrywki if limity.rozgrywki is None else rozgrywki[: limity.rozgrywki],
            zawodnicy if limity.zawodnicy is None else zawodnicy[: limity.zawodnicy],
            zawodnicy[: limity.skuteczni_zawodnicy],
            11,
            11,
            11,
            [
                TrendSezonuHali("2024/2025", 8, Decimal("55.5"), Decimal("2100"), 6),
                TrendSezonuHali("2025/2026", 12, Decimal("58.2"), Decimal("2500"), 12),
            ],
            [RozkladKalendarzaHali("Sobota", 12), RozkladKalendarzaHali("Niedziela", 8)],
            [
                KomorkaKalendarzaHali("2024/2025", 9, 3),
                KomorkaKalendarzaHali("2025/2026", 2, 5),
            ],
            [PrzedzialHali("50–59", 13), PrzedzialHali("60–69", 7)],
            ProfilWynikowHali(
                Decimal("57.1"),
                Decimal("57"),
                Decimal("6.2"),
                42,
                71,
                Decimal("53"),
                Decimal("61"),
                Decimal("4.5"),
                3,
                9,
                14,
            ),
            FrekwencjaHali(18, 20, Decimal("2300"), Decimal("2250"), 4100, Decimal("54.8")),
            [
                PorownanieHali("Mecze na sezon", Decimal("10"), Decimal("8.4")),
                PorownanieHali("Bramki w meczu", Decimal("57.1"), Decimal("55.8")),
            ],
            [
                RekordMeczuHali(
                    "Najwięcej bramek",
                    101,
                    datetime(2026, 2, 1),
                    "Drużyna A",
                    "Drużyna B",
                    38,
                    33,
                    71,
                )
            ],
        )
