from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from handball.domain.attendance_analytics import PunktTrendu, RaportFrekwencji
from handball.domain.attendance_calendar import GrupaKalendarza, HeatmapaFrekwencji
from handball.domain.attendance_data_science import GrupaEfektu, HistogramFrekwencji
from handball.domain.attendance_opponents import RankingPrzeciwnikow
from handball.interface.presenters.attendance_cities_presenter import MiastaWykresPresenter

LIMIT_KLUBOW_NA_WYKRESIE = 15
LIMIT_PRZECIWNIKOW_NA_WYKRESIE = 20


class FrekwencjaWykresPresenter:
    def __init__(self, miasta: MiastaWykresPresenter | None = None) -> None:
        self._miasta = miasta or MiastaWykresPresenter()

    def przygotuj(self, raport: RaportFrekwencji) -> dict[str, Any]:
        wybrany = raport.filtry.id_sezon
        kalendarz = raport.kalendarz
        return {
            "sezony": [self._sezon(punkt, wybrany) for punkt in raport.trend.punkty],
            "bez_zer": raport.filtry.bez_zer,
            "heatmapa": self._heatmapa(kalendarz.heatmapa),
            "histogram": self._histogram(raport.data_science.histogram),
            "kluby": self._kluby(raport),
            **self._miasta.przygotuj(raport.miasta),
            "miesiace": self._grupy(kalendarz.miesiace),
            "dni": self._grupy(kalendarz.dni_tygodnia),
            "godziny": self._grupy(kalendarz.godziny),
            "przeciwnicy": self._przeciwnicy(raport.przeciwnicy),
            "pokrycie": [self._pokrycie(punkt) for punkt in raport.trend.punkty],
            "efektDnia": self._efekt_dnia(raport.data_science.dni_tygodnia),
        }

    def _sezon(self, punkt: PunktTrendu, wybrany: int | None) -> dict[str, Any]:
        podsumowanie = punkt.sezon.podsumowanie
        return {
            "sezon": punkt.sezon.nazwa,
            "srednia": podsumowanie.srednia,
            "mediana": podsumowanie.mediana,
            "q1": podsumowanie.q1,
            "q3": podsumowanie.q3,
            "suma": podsumowanie.suma,
            "srednia_kroczaca": punkt.srednia_kroczaca,
            "zmiana": punkt.zmiana,
            "znane": podsumowanie.znane,
            "rozegrane": podsumowanie.rozegrane,
            "wybrany": punkt.sezon.id_sezon == wybrany,
        }

    def _pokrycie(self, punkt: PunktTrendu) -> dict[str, Any]:
        podsumowanie = punkt.sezon.podsumowanie
        pokrycie = podsumowanie.pokrycie
        return {
            "sezon": punkt.sezon.nazwa,
            "znane": podsumowanie.znane,
            "rozegrane": podsumowanie.rozegrane,
            "pokrycie": None if pokrycie is None else round(pokrycie * 100, 1),
        }

    def _kluby(self, raport: RaportFrekwencji) -> list[dict[str, Any]]:
        return [
            {
                "nazwa": wiersz.klub.nazwa,
                "srednia": wiersz.klub.podsumowanie.srednia,
                "znane": wiersz.klub.podsumowanie.znane,
            }
            for wiersz in raport.ranking[:LIMIT_KLUBOW_NA_WYKRESIE]
        ]

    def _grupy(self, grupy: Sequence[GrupaKalendarza]) -> list[dict[str, Any]]:
        return [
            {
                "etykieta": grupa.etykieta,
                "srednia": grupa.srednia,
                "znane": grupa.znane,
                "rozegrane": grupa.rozegrane,
            }
            for grupa in grupy
        ]

    def _przeciwnicy(self, ranking: RankingPrzeciwnikow) -> list[dict[str, Any]]:
        if not ranking.aktywny:
            return []
        return [
            {
                "nazwa": wiersz.przeciwnik.nazwa,
                "srednia": wiersz.przeciwnik.srednia,
                "roznica": wiersz.roznica,
            }
            for wiersz in ranking.wiersze[:LIMIT_PRZECIWNIKOW_NA_WYKRESIE]
        ]

    def _efekt_dnia(self, grupy: Sequence[GrupaEfektu]) -> list[dict[str, Any]]:
        return [
            {"etykieta": grupa.etykieta, "srednia": grupa.srednia, "n": grupa.n} for grupa in grupy
        ]

    def _heatmapa(self, heatmapa: HeatmapaFrekwencji) -> dict[str, Any]:
        indeksy = {godzina: indeks for indeks, godzina in enumerate(heatmapa.godziny)}
        komorki = [
            {
                "x": indeksy[komorka.godzina],
                "y": komorka.dzien - 1,
                "srednia": komorka.srednia,
                "znane": komorka.znane,
                "rozegrane": komorka.rozegrane,
            }
            for komorka in heatmapa.komorki
            if komorka.srednia is not None
        ]
        srednie = [komorka["srednia"] for komorka in komorki]
        return {
            "dni": list(heatmapa.dni),
            "godziny": list(heatmapa.etykiety_godzin),
            "komorki": komorki,
            "minimum": min(srednie) if srednie else None,
            "maksimum": max(srednie) if srednie else None,
        }

    def _histogram(self, histogram: HistogramFrekwencji | None) -> dict[str, Any]:
        if histogram is None:
            return {"przedzialy": [], "percentyle": []}
        return {
            "przedzialy": [
                {
                    "etykieta": przedzial.etykieta,
                    "od": przedzial.od,
                    "do": przedzial.do,
                    "liczba": przedzial.liczba,
                }
                for przedzial in histogram.przedzialy
            ],
            "percentyle": [
                {"procent": percentyl.procent, "wartosc": percentyl.wartosc}
                for percentyl in histogram.percentyle
            ],
        }
