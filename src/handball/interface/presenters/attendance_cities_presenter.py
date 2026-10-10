from __future__ import annotations

from typing import Any

from handball.domain.attendance_aggregate import AgregatFrekwencji, MiaryRozkladu
from handball.domain.attendance_cities import RaportMiast, WierszMiasta

LIMIT_MIAST_NA_WYKRESIE = 15


class MiastaWykresPresenter:
    def przygotuj(self, raport: RaportMiast) -> dict[str, Any]:
        wiodace = raport.ranking[:LIMIT_MIAST_NA_WYKRESIE]
        return {
            "miasta": [self._miasto(wiersz) for wiersz in wiodace],
            "miastaSzczegoly": [self._szczegoly(wiersz) for wiersz in wiodace],
        }

    def _miasto(self, wiersz: WierszMiasta) -> dict[str, Any]:
        miasto = wiersz.miasto
        return {
            "klucz": miasto.klucz,
            "nazwa": miasto.miasto,
            "suma": miasto.suma,
            "srednia": miasto.srednia,
            "mediana": miasto.rozklad.mediana,
            "dominanta": miasto.rozklad.dominanta,
            "znane": miasto.znane,
            "kluby": miasto.liczba_klubow,
        }

    def _szczegoly(self, wiersz: WierszMiasta) -> dict[str, Any]:
        return {
            "klucz": wiersz.miasto.klucz,
            "nazwa": wiersz.miasto.miasto,
            "sezony": [
                {
                    "sezon": sezon.sezon,
                    "rozegrane": sezon.agregat.rozegrane,
                    **self._miary(sezon.agregat, sezon.rozklad),
                }
                for sezon in wiersz.sezony
            ],
            "rozgrywki": [
                {"nazwa": pozycja.rozgrywki, **self._miary(pozycja.agregat, pozycja.rozklad)}
                for pozycja in wiersz.wg_rozgrywek
            ],
            "hale": [
                {"nazwa": hala.etykieta, **self._miary(hala.agregat, hala.rozklad)}
                for hala in wiersz.hale
            ],
        }

    @staticmethod
    def _miary(agregat: AgregatFrekwencji, rozklad: MiaryRozkladu) -> dict[str, Any]:
        return {
            "suma": agregat.suma,
            "srednia": agregat.srednia,
            "mediana": rozklad.mediana,
            "znane": agregat.znane,
        }
