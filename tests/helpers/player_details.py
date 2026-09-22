from collections.abc import Iterable
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal

from handball.domain.errors import NieZnalezionoZawodnika
from handball.domain.matches import DaneMeczu, PozycjaListyMeczow, ZawodnikMeczu
from handball.domain.player_details import (
    AnalitykaMeczuZawodnika,
    DaneSezonoweZawodnika,
    FiltryMeczowZawodnika,
    MeczZawodnika,
    StronaMeczowZawodnika,
    SzczegolyZawodnika,
    WpisMeczowyZawodnika,
)

SZCZEGOLY_ZAWODNIKA = SzczegolyZawodnika(
    7,
    "Jan",
    "Testowy",
    date(1998, 1, 2),
    None,
    (
        DaneSezonoweZawodnika(
            10,
            "2026/2027",
            "Drużyna A",
            9,
            "RO",
            Decimal("192.0"),
            Decimal("94.5"),
            "Liga",
            120,
            20,
            30,
            10,
            2,
            1,
        ),
        DaneSezonoweZawodnika(11, "2025/2026", "Drużyna B", 5, "BR", Decimal("190.0"), None),
    ),
)

MECZ_ZAWODNIKA = MeczZawodnika(
    PozycjaListyMeczow(
        id_mecz=101,
        termin=datetime(2026, 9, 20, 18),
        sezon="2026/2027",
        rozgrywki="Liga",
        gospodarz="Drużyna A",
        gosc="Rywal B",
        mecz=DaneMeczu(id=101, wynik_gosp_full=30, wynik_gosc_full=25),
        hala=None,
    ),
    (
        WpisMeczowyZawodnika(
            "gosp",
            ZawodnikMeczu(
                nr_koszulki=9,
                pozycja="RO",
                bramki=0,
                karne_bramki=0,
                karne_liczba=None,
                dwie_minuty=1,
                upomnienie=False,
                dyskwalifikacja=None,
            ),
        ),
    ),
)


class SzczegolyZawodnikaInMemoryRepository:
    def __init__(self) -> None:
        self.szczegoly = SZCZEGOLY_ZAWODNIKA
        self.mecze = [
            replace(
                MECZ_ZAWODNIKA,
                mecz=replace(
                    MECZ_ZAWODNIKA.mecz,
                    id_mecz=101 + i,
                    mecz=replace(MECZ_ZAWODNIKA.mecz.mecz, id=101 + i),
                ),
            )
            for i in range(23)
        ]
        self.filtry: FiltryMeczowZawodnika | None = None

    def pobierz_szczegoly(self, id_zawodnik: int) -> SzczegolyZawodnika:
        if id_zawodnik != self.szczegoly.id_zawodnik:
            raise NieZnalezionoZawodnika(id_zawodnik)
        return self.szczegoly

    def pobierz_mecze(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> StronaMeczowZawodnika:
        self.filtry = filtry
        mecze = [
            m
            for m in self.mecze
            if (filtry.id_sezon is None or filtry.id_sezon == 195)
            and (not filtry.rozgrywki or m.mecz.rozgrywki == filtry.rozgrywki)
            and (
                not filtry.przeciwnik
                or filtry.przeciwnik.casefold() in (m.mecz.gosc or "").casefold()
            )
        ]
        mecze.sort(key=lambda m: (m.mecz.termin or datetime.min, m.mecz.id_mecz))
        if filtry.sortowanie == "-data":
            mecze.sort(key=lambda m: m.mecz.termin or datetime.min, reverse=True)
        strona = min(
            filtry.strona, max(1, (len(mecze) + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
        )
        poczatek = (strona - 1) * filtry.rozmiar_strony
        return StronaMeczowZawodnika(
            mecze[poczatek : poczatek + filtry.rozmiar_strony],
            len(mecze),
            strona,
            filtry.rozmiar_strony,
        )

    def pobierz_analityke(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> tuple[AnalitykaMeczuZawodnika, ...]:
        if id_zawodnik != self.szczegoly.id_zawodnik:
            raise NieZnalezionoZawodnika(id_zawodnik)
        mecze = [
            mecz
            for mecz in self.mecze
            if (filtry.id_sezon is None or filtry.id_sezon == 195)
            and (not filtry.rozgrywki or mecz.mecz.rozgrywki == filtry.rozgrywki)
            and (
                not filtry.przeciwnik
                or filtry.przeciwnik.casefold() in (mecz.mecz.gosc or "").casefold()
            )
        ]
        return tuple(
            AnalitykaMeczuZawodnika(
                id_mecz=mecz.mecz.id_mecz,
                termin=mecz.mecz.termin,
                sezon=mecz.mecz.sezon or "—",
                rozgrywki=mecz.mecz.rozgrywki or "—",
                bramki=self._suma(wpis.statystyki.bramki for wpis in mecz.wpisy),
                karne_bramki=self._suma(wpis.statystyki.karne_bramki for wpis in mecz.wpisy),
                karne_liczba=self._suma(wpis.statystyki.karne_liczba for wpis in mecz.wpisy),
                dwie_minuty=self._suma(wpis.statystyki.dwie_minuty for wpis in mecz.wpisy),
                upomnienia=self._suma(
                    int(wpis.statystyki.upomnienie)
                    if wpis.statystyki.upomnienie is not None
                    else None
                    for wpis in mecz.wpisy
                ),
                dyskwalifikacje=self._suma(
                    int(wpis.statystyki.dyskwalifikacja)
                    if wpis.statystyki.dyskwalifikacja is not None
                    else None
                    for wpis in mecz.wpisy
                ),
                miejsce=self._miejsce(mecz.wpisy),
            )
            for mecz in mecze
        )

    @staticmethod
    def _suma(wartosci: Iterable[int | None]) -> int | None:
        znane = [wartosc for wartosc in wartosci if wartosc is not None]
        return sum(znane) if znane else None

    @staticmethod
    def _miejsce(wpisy: tuple[WpisMeczowyZawodnika, ...]) -> str | None:
        mapa = {"gosp": "dom", "gosc": "wyjazd"}
        miejsca = {mapa[wpis.strona] for wpis in wpisy if wpis.strona in mapa}
        return miejsca.pop() if len(miejsca) == 1 else None
