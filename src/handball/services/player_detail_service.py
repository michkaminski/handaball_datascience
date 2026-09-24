from statistics import median

from handball.contracts.player_detail_repository import SzczegolyZawodnikaReadRepository
from handball.domain.goal_statistics import FormaIRegularnosc
from handball.domain.player_details import (
    FiltryMeczowZawodnika,
    PodsumowanieAnalityczneZawodnika,
    StronaMeczowZawodnika,
    SzczegolyZawodnika,
)
from handball.services.goal_statistics import StatystykiBramekCalculator


class SzczegolyZawodnikaService:
    def __init__(self, repozytorium: SzczegolyZawodnikaReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_szczegoly(self, id_zawodnik: int) -> SzczegolyZawodnika:
        return self._repozytorium.pobierz_szczegoly(id_zawodnik)

    def pobierz_mecze(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> StronaMeczowZawodnika:
        return self._repozytorium.pobierz_mecze(id_zawodnik, filtry)


class SzczegolyZawodnikaAnalyticsService:
    def __init__(
        self,
        repozytorium: SzczegolyZawodnikaReadRepository,
        kalkulator: StatystykiBramekCalculator | None = None,
    ) -> None:
        self._repozytorium = repozytorium
        self._kalkulator = kalkulator or StatystykiBramekCalculator()

    def pobierz_podsumowanie(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> PodsumowanieAnalityczneZawodnika:
        mecze = self._repozytorium.pobierz_analityke(id_zawodnik, filtry)
        kalkulator = self._kalkulator
        bramki = [m.bramki for m in mecze if m.bramki is not None]
        rekord = max(bramki, default=None)
        return PodsumowanieAnalityczneZawodnika(
            mecze=mecze,
            statystyki_sezonow=kalkulator.statystyki_sezonow(mecze),
            liczba_meczow=len(mecze),
            liczba_znanych_bramek=len(bramki),
            suma_bramek=sum(bramki) if bramki else None,
            srednia_bramek=sum(bramki) / len(bramki) if bramki else None,
            mediana_bramek=float(median(bramki)) if bramki else None,
            mediana_bramek_dom=kalkulator.mediana_wedlug_miejsca(mecze, "dom"),
            mediana_bramek_wyjazd=kalkulator.mediana_wedlug_miejsca(mecze, "wyjazd"),
            dominanty_bramek=kalkulator.dominanty(bramki),
            kwartyl_pierwszy=kalkulator.percentyl(bramki, 0.25),
            kwartyl_trzeci=kalkulator.percentyl(bramki, 0.75),
            mecze_z_bramka=sum(w > 0 for w in bramki),
            karne_bramki=kalkulator.suma(m.karne_bramki for m in mecze),
            karne_liczba=kalkulator.suma(m.karne_liczba for m in mecze),
            dwie_minuty=kalkulator.suma(m.dwie_minuty for m in mecze),
            upomnienia=kalkulator.suma(m.upomnienia for m in mecze),
            dyskwalifikacje=kalkulator.suma(m.dyskwalifikacje for m in mecze),
            rekord_bramek=rekord,
            rekordowe_mecze=tuple(
                mecz.id_mecz for mecz in mecze if rekord is not None and mecz.bramki == rekord
            ),
            najdluzsza_seria_z_bramka=kalkulator.najdluzsza_seria(
                m.bramki is not None and m.bramki > 0 for m in mecze
            ),
            znane_karne_bramki=sum(m.karne_bramki is not None for m in mecze),
            znane_karne_liczba=sum(m.karne_liczba is not None for m in mecze),
            znane_dwie_minuty=sum(m.dwie_minuty is not None for m in mecze),
            znane_upomnienia=sum(m.upomnienia is not None for m in mecze),
            znane_dyskwalifikacje=sum(m.dyskwalifikacje is not None for m in mecze),
        )

    def pobierz_forme(self, id_zawodnik: int, filtry: FiltryMeczowZawodnika) -> FormaIRegularnosc:
        return self._kalkulator.forma(self._repozytorium.pobierz_analityke(id_zawodnik, filtry))
