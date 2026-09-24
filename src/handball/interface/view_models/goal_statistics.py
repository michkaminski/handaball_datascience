from dataclasses import dataclass


@dataclass(frozen=True)
class FormaWedlugMiejscaViewModel:
    liczba_znanych: str
    wystarczajaco_na_trend_5: bool
    wystarczajaco_na_trend_10: bool
    punkty: list[dict[str, int | str | float | None]]


@dataclass(frozen=True)
class FormaIRegularnoscViewModel:
    liczba_meczow: str
    liczba_znanych: str
    srednia: str
    mediana: str
    dominanta: str
    minimum: str
    maksimum: str
    kwartyle: str
    iqr: str
    odchylenie_standardowe: str
    mad: str
    wspolczynnik_zmiennosci: str
    percentyl_10: str
    percentyl_90: str
    srednia_ucieta: str
    udzial_0_bramek: str
    udzial_1_2_bramki: str
    udzial_3_5_bramek: str
    udzial_6_plus_bramek: str
    wszystkie: FormaWedlugMiejscaViewModel
    dom: FormaWedlugMiejscaViewModel
    wyjazd: FormaWedlugMiejscaViewModel
    sezony: list[dict[str, int | str | float | bool | list[int]]]
