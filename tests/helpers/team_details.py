from datetime import datetime
from typing import Any

from handball.domain.errors import NieZnalezionoDruzyny
from handball.domain.matches import DaneMeczu, PozycjaListyMeczow
from handball.domain.options import OpcjaWyboru
from handball.domain.team_details import (
    DaneZestawieniaDruzyny,
    FiltryDruzyny,
    FiltryZawodnikowDruzyny,
    FiltryZestawieniaDruzyny,
    HalaDruzyny,
    MeczDruzyny,
    OpcjeFiltrowDruzyny,
    SezonDruzyny,
    StronaMeczowDruzyny,
    StronaZawodnikowDruzyny,
    SzczegolyDruzyny,
    WpisZestawienia,
    ZawodnikDruzyny,
)

ID_DRUZYNY = 272

SZCZEGOLY_DRUZYNY = SzczegolyDruzyny(
    id_zespol=ID_DRUZYNY,
    nr_klubu=68,
    nazwa="Wisła Test",
    plec="M",
    kategoria="Senior",
    wycofany=False,
    liczba_meczow=4,
    sezony=(
        SezonDruzyny(12, 195, "2026/2027", "Wisła Test", "M", "Senior", "Płock", False),
        SezonDruzyny(11, 194, "2025/2026", "Wisła Test", "M", "Senior", None, False),
        SezonDruzyny(10, 193, "2024/2025", "Stara Wisła", "M", "Senior", "Płock", False),
    ),
    hale=(HalaDruzyny(43, "Orlen Arena", "Płock", 2, 2, 1850.0),),
)


def mecz_druzyny(
    id_mecz: int,
    termin: datetime,
    sezon: str,
    kolumna: str,
    wynik: tuple[int | None, int | None],
    rozgrywki: str = "Liga",
    **dane: Any,
) -> MeczDruzyny:
    return MeczDruzyny(
        PozycjaListyMeczow(
            id_mecz=id_mecz,
            termin=termin,
            sezon=sezon,
            rozgrywki=rozgrywki,
            gospodarz="Wisła Test" if kolumna == "gosp" else "Rywal <b>",
            gosc="Rywal <b>" if kolumna == "gosp" else "Wisła Test",
            mecz=DaneMeczu(
                id=id_mecz,
                wynik_gosp_full=wynik[0],
                wynik_gosc_full=wynik[1],
                **dane,
            ),
            hala=None,
        ),
        kolumna,
    )


MECZE_DRUZYNY = (
    mecz_druzyny(1, datetime(2024, 9, 1, 18), "2024/2025", "gosp", (30, 25), widzowie=2000),
    mecz_druzyny(
        2,
        datetime(2025, 9, 1, 18),
        "2025/2026",
        "gosc",
        (28, 28),
        dogrywka_karne_gosp=3,
        dogrywka_karne_gosc=5,
        widzowie=5100,
    ),
    mecz_druzyny(
        3,
        datetime(2026, 9, 1, 18),
        "2026/2027",
        "gosc",
        (27, 31),
        zamiana=True,
        rozgrywki="Puchar",
        widzowie=0,
    ),
    mecz_druzyny(4, datetime(2026, 9, 8, 18), "2026/2027", "gosp", (None, None), widzowie=900),
)

ZAWODNICY_DRUZYNY = [
    ZawodnikDruzyny(
        id_zawodnik=7,
        imie="Jan",
        nazwisko="Testowy",
        mecze=3,
        mecze_ze_znanymi_bramkami=2,
        bramki=9,
        karne_bramki=2,
        karne_liczba=3,
        dwie_minuty=1,
        upomnienia=0,
        dyskwalifikacje=None,
        sezony=("2024/2025", "2026/2027"),
        ostatni_mecz=datetime(2026, 9, 1, 18),
    )
]


def wpis_zestawienia(id_mecz: int, id_zawodnik: int, **dane: Any) -> WpisZestawienia:
    wartosci: dict[str, Any] = {
        "imie": "Jan" if id_zawodnik == 7 else "Adam",
        "nazwisko": "Testowy" if id_zawodnik == 7 else "Bramkarz <b>",
        "nr_koszulki": 9 if id_zawodnik == 7 else 1,
        "pozycja": "Rozgrywający" if id_zawodnik == 7 else "Bramkarz",
        "bramki": 0,
        "dwie_minuty": None,
        "upomnienie": None,
        "dyskwalifikacja": None,
        "karne_bramki": None,
        "karne_liczba": None,
    }
    wartosci.update(dane)
    return WpisZestawienia(id_mecz=id_mecz, id_zawodnik=id_zawodnik, **wartosci)


WPISY_ZESTAWIENIA = (
    wpis_zestawienia(1, 7, bramki=6, karne_bramki=2, karne_liczba=3, dwie_minuty=1),
    wpis_zestawienia(1, 8, bramki=None),
    wpis_zestawienia(2, 7, bramki=4, pozycja="Skrzydłowy", upomnienie=True),
    wpis_zestawienia(3, 7, bramki=5, karne_bramki=1, karne_liczba=1),
)


class SzczegolyDruzynyInMemoryRepository:
    def __init__(self, mecze: tuple[MeczDruzyny, ...] = MECZE_DRUZYNY) -> None:
        self.mecze = mecze
        self.filtry_zawodnikow: FiltryZawodnikowDruzyny | None = None
        self.filtry_meczow: FiltryDruzyny | None = None
        self.filtry_zestawienia: FiltryZestawieniaDruzyny | None = None

    def pobierz_szczegoly(self, id_zespol: int) -> SzczegolyDruzyny:
        if id_zespol != ID_DRUZYNY:
            raise NieZnalezionoDruzyny(id_zespol)
        return SZCZEGOLY_DRUZYNY

    def pobierz_opcje_filtrow(self, id_zespol: int) -> OpcjeFiltrowDruzyny:
        return OpcjeFiltrowDruzyny(
            (OpcjaWyboru(195, "2026/2027"), OpcjaWyboru(194, "2025/2026")), ("Liga", "Puchar")
        )

    def pobierz_mecze(self, id_zespol: int, filtry: FiltryDruzyny) -> StronaMeczowDruzyny:
        self.filtry_meczow = filtry
        wybrane = self._filtruj(filtry)
        return StronaMeczowDruzyny(list(reversed(wybrane)), len(wybrane), filtry.strona, 20)

    def pobierz_wszystkie_mecze(
        self, id_zespol: int, filtry: FiltryDruzyny
    ) -> tuple[MeczDruzyny, ...]:
        return tuple(self._filtruj(filtry))

    def pobierz_zestawienie(
        self, id_zespol: int, filtry: FiltryZestawieniaDruzyny
    ) -> DaneZestawieniaDruzyny:
        self.filtry_zestawienia = filtry
        mecze = tuple(
            m
            for m in self.mecze[:3]
            if filtry.rozgrywki is None or m.mecz.rozgrywki == filtry.rozgrywki
        )
        identyfikatory = {m.mecz.id_mecz for m in mecze}
        return DaneZestawieniaDruzyny(
            mecze, tuple(w for w in WPISY_ZESTAWIENIA if w.id_mecz in identyfikatory)
        )

    def pobierz_zawodnikow(
        self, id_zespol: int, filtry: FiltryZawodnikowDruzyny
    ) -> StronaZawodnikowDruzyny:
        self.filtry_zawodnikow = filtry
        return StronaZawodnikowDruzyny(ZAWODNICY_DRUZYNY, 45, filtry.strona, 20)

    def _filtruj(self, filtry: FiltryDruzyny) -> list[MeczDruzyny]:
        return [
            mecz
            for mecz in self.mecze
            if (filtry.rozgrywki is None or mecz.mecz.rozgrywki == filtry.rozgrywki)
        ]
