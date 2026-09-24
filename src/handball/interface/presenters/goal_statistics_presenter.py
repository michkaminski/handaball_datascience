from collections import Counter
from collections.abc import Sequence

from handball.domain.goal_statistics import (
    FormaIRegularnosc,
    FormaWedlugMiejsca,
    MeczZBramkami,
    StatystykiBramekGrupy,
    StatystykiSezonu,
)
from handball.interface.presenters.match_presenter import MeczFormat
from handball.interface.view_models.goal_statistics import (
    FormaIRegularnoscViewModel,
    FormaWedlugMiejscaViewModel,
)


class StatystykiBramekPresenter:
    def __init__(self, formatowanie: MeczFormat) -> None:
        self._format = formatowanie

    def przygotuj_forme(self, dane: FormaIRegularnosc) -> FormaIRegularnoscViewModel:
        return FormaIRegularnoscViewModel(
            liczba_meczow=str(dane.liczba_meczow),
            liczba_znanych=str(dane.liczba_znanych),
            srednia=self.liczba(dane.srednia),
            mediana=self.liczba(dane.mediana),
            dominanta=self.dominanta(dane.dominanty),
            minimum=self.liczba(dane.minimum),
            maksimum=self.liczba(dane.maksimum),
            kwartyle=self.kwartyle(dane.kwartyl_pierwszy, dane.kwartyl_trzeci),
            iqr=self.liczba(dane.rozstep_miedzykwartylowy),
            odchylenie_standardowe=self.liczba(dane.odchylenie_standardowe),
            mad=self.liczba(dane.mad),
            wspolczynnik_zmiennosci=self.procent(dane.wspolczynnik_zmiennosci),
            percentyl_10=self.liczba(dane.percentyl_10),
            percentyl_90=self.liczba(dane.percentyl_90),
            srednia_ucieta=self.liczba(dane.srednia_ucieta),
            udzial_0_bramek=self.procent(dane.udzial_0_bramek),
            udzial_1_2_bramki=self.procent(dane.udzial_1_2_bramki),
            udzial_3_5_bramek=self.procent(dane.udzial_3_5_bramek),
            udzial_6_plus_bramek=self.procent(dane.udzial_6_plus_bramek),
            wszystkie=self._forma_wedlug_miejsca(dane.wszystkie),
            dom=self._forma_wedlug_miejsca(dane.dom),
            wyjazd=self._forma_wedlug_miejsca(dane.wyjazd),
            sezony=[
                {
                    "sezon": sezon.sezon,
                    "n": sezon.liczba_znanych,
                    "mala_proba": sezon.mala_proba,
                    "mediana": sezon.mediana,
                    "q1": sezon.kwartyl_pierwszy,
                    "q3": sezon.kwartyl_trzeci,
                    "minimum": sezon.minimum,
                    "maksimum": sezon.maksimum,
                    "odstajace": list(sezon.wartosci_odstajace),
                }
                for sezon in dane.sezony
            ],
        )

    def statystyki_sezonow(self, sezony: Sequence[StatystykiSezonu]) -> list[dict[str, object]]:
        return [
            {
                "sezon": sezon.sezon,
                **self._statystyki_grupy(sezon.statystyki),
                "rozgrywki": [
                    {"rozgrywki": grupa.rozgrywki, **self._statystyki_grupy(grupa.statystyki)}
                    for grupa in sezon.rozgrywki
                ],
            }
            for sezon in sezony
        ]

    @staticmethod
    def rozklad(mecze: Sequence[MeczZBramkami]) -> list[dict[str, int]]:
        wszystkie = Counter(m.bramki for m in mecze if m.bramki is not None)
        dom = Counter(m.bramki for m in mecze if m.bramki is not None and m.miejsce == "dom")
        wyjazd = Counter(m.bramki for m in mecze if m.bramki is not None and m.miejsce == "wyjazd")
        return [
            {
                "bramki": wartosc,
                "mecze": wszystkie[wartosc],
                "dom": dom.get(wartosc, 0),
                "wyjazd": wyjazd.get(wartosc, 0),
            }
            for wartosc in sorted(wszystkie)
        ]

    def kwartyle(self, pierwszy: float | None, trzeci: float | None) -> str:
        if pierwszy is None or trzeci is None:
            return "—"
        return f"{self.liczba(pierwszy)}–{self.liczba(trzeci)}"

    @staticmethod
    def dominanta(dominanty: Sequence[int]) -> str:
        return ", ".join(str(w) for w in dominanty) or "—"

    @staticmethod
    def miejsce_etykieta(miejsce: str | None) -> str:
        return {"dom": "U siebie", "wyjazd": "Na wyjeździe"}.get(miejsce or "", "—")

    @staticmethod
    def procent(wartosc: float | None) -> str:
        return f"{wartosc:.1f}%" if wartosc is not None else "—"

    @staticmethod
    def liczba(wartosc: int | float | None) -> str:
        if wartosc is None:
            return "—"
        if isinstance(wartosc, float):
            return f"{wartosc:.1f}"
        return str(wartosc)

    @staticmethod
    def _statystyki_grupy(statystyki: StatystykiBramekGrupy) -> dict[str, object]:
        return {
            "mecze": statystyki.liczba_meczow,
            "znane": statystyki.liczba_znanych,
            "suma": statystyki.suma,
            "srednia": statystyki.srednia,
            "mediana": statystyki.mediana,
            "dominanty": list(statystyki.dominanty),
            "q1": statystyki.kwartyl_pierwszy,
            "q3": statystyki.kwartyl_trzeci,
            "minimum": statystyki.minimum,
            "maksimum": statystyki.maksimum,
        }

    def _forma_wedlug_miejsca(self, dane: FormaWedlugMiejsca) -> FormaWedlugMiejscaViewModel:
        return FormaWedlugMiejscaViewModel(
            liczba_znanych=str(dane.liczba_znanych),
            wystarczajaco_na_trend_5=dane.wystarczajaco_na_trend_5,
            wystarczajaco_na_trend_10=dane.wystarczajaco_na_trend_10,
            punkty=[
                {
                    "id_mecz": punkt.id_mecz,
                    "etykieta": self._format.data(punkt.termin),
                    "sezon": punkt.sezon,
                    "bramki": punkt.bramki,
                    "mediana_5": punkt.mediana_kroczaca_5,
                    "srednia_5": punkt.srednia_kroczaca_5,
                    "mediana_10": punkt.mediana_kroczaca_10,
                }
                for punkt in dane.punkty
            ],
        )
