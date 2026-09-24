from collections import Counter
from collections.abc import Iterable, Sequence
from statistics import mean, median, pstdev

from handball.domain.goal_statistics import (
    FormaIRegularnosc,
    FormaWedlugMiejsca,
    MeczZBramkami,
    PunktFormy,
    RozstepSezonu,
    StatystykiBramekGrupy,
    StatystykiRozgrywekSezonu,
    StatystykiSezonu,
)

PROG_MALEJ_PROBY = 5
PROG_MINIMALNEJ_SREDNIEJ_DLA_CV = 0.1


class StatystykiBramekCalculator:
    def statystyki_grupy(self, mecze: Sequence[MeczZBramkami]) -> StatystykiBramekGrupy:
        znane = [m.bramki for m in mecze if m.bramki is not None]
        return StatystykiBramekGrupy(
            liczba_meczow=len(mecze),
            liczba_znanych=len(znane),
            suma=sum(znane) if znane else None,
            srednia=float(mean(znane)) if znane else None,
            mediana=float(median(znane)) if znane else None,
            dominanty=self.dominanty(znane),
            kwartyl_pierwszy=self.percentyl(znane, 0.25),
            kwartyl_trzeci=self.percentyl(znane, 0.75),
            minimum=min(znane, default=None),
            maksimum=max(znane, default=None),
        )

    def statystyki_sezonow(self, mecze: Sequence[MeczZBramkami]) -> tuple[StatystykiSezonu, ...]:
        sezony: dict[str, list[MeczZBramkami]] = {}
        for mecz in mecze:
            sezony.setdefault(mecz.sezon, []).append(mecz)
        wynik = []
        for sezon, mecze_sezonu in sezony.items():
            rozgrywki: dict[str, list[MeczZBramkami]] = {}
            for mecz in mecze_sezonu:
                rozgrywki.setdefault(mecz.rozgrywki, []).append(mecz)
            wynik.append(
                StatystykiSezonu(
                    sezon=sezon,
                    statystyki=self.statystyki_grupy(mecze_sezonu),
                    rozgrywki=tuple(
                        StatystykiRozgrywekSezonu(nazwa, self.statystyki_grupy(grupa))
                        for nazwa, grupa in rozgrywki.items()
                    ),
                )
            )
        return tuple(wynik)

    def forma(self, mecze: Sequence[MeczZBramkami]) -> FormaIRegularnosc:
        znane = [m.bramki for m in mecze if m.bramki is not None]
        posortowane = sorted(znane)
        n = len(znane)
        srednia = float(mean(znane)) if znane else None
        mediana = float(median(znane)) if znane else None
        q1 = self.percentyl(znane, 0.25)
        q3 = self.percentyl(znane, 0.75)
        iqr = q3 - q1 if q1 is not None and q3 is not None else None
        odchylenie = pstdev(znane) if n >= 2 else None
        mad = median([abs(w - mediana) for w in znane]) if n >= 2 and mediana is not None else None
        wspolczynnik_zmiennosci = (
            100 * odchylenie / srednia
            if odchylenie is not None
            and srednia is not None
            and srednia >= PROG_MINIMALNEJ_SREDNIEJ_DLA_CV
            else None
        )
        return FormaIRegularnosc(
            liczba_meczow=len(mecze),
            liczba_znanych=n,
            sezony=self._sezony_rozstepow(mecze),
            wszystkie=self._forma_meczow(mecze),
            dom=self._forma_meczow([mecz for mecz in mecze if mecz.miejsce == "dom"]),
            wyjazd=self._forma_meczow([mecz for mecz in mecze if mecz.miejsce == "wyjazd"]),
            srednia=srednia,
            mediana=mediana,
            dominanty=self.dominanty(znane),
            minimum=min(posortowane) if posortowane else None,
            maksimum=max(posortowane) if posortowane else None,
            kwartyl_pierwszy=q1,
            kwartyl_trzeci=q3,
            rozstep_miedzykwartylowy=iqr,
            odchylenie_standardowe=odchylenie,
            mad=mad,
            wspolczynnik_zmiennosci=wspolczynnik_zmiennosci,
            percentyl_10=self.percentyl(znane, 0.10),
            percentyl_90=self.percentyl(znane, 0.90),
            srednia_ucieta=self._srednia_ucieta(posortowane),
            udzial_0_bramek=100 * sum(w == 0 for w in znane) / n if n else None,
            udzial_1_2_bramki=100 * sum(1 <= w <= 2 for w in znane) / n if n else None,
            udzial_3_5_bramek=100 * sum(3 <= w <= 5 for w in znane) / n if n else None,
            udzial_6_plus_bramek=100 * sum(w >= 6 for w in znane) / n if n else None,
        )

    @staticmethod
    def mediana_wedlug_miejsca(mecze: Sequence[MeczZBramkami], miejsce: str) -> float | None:
        bramki = [m.bramki for m in mecze if m.bramki is not None and m.miejsce == miejsce]
        return float(median(bramki)) if bramki else None

    @staticmethod
    def suma(wartosci: Iterable[int | None]) -> int | None:
        znane = [wartosc for wartosc in wartosci if wartosc is not None]
        return sum(znane) if znane else None

    @staticmethod
    def percentyl(wartosci: Sequence[int], udzial: float) -> float | None:
        if not wartosci:
            return None
        uporzadkowane = sorted(wartosci)
        pozycja = (len(uporzadkowane) - 1) * udzial
        dol = int(pozycja)
        gora = min(dol + 1, len(uporzadkowane) - 1)
        return uporzadkowane[dol] + (uporzadkowane[gora] - uporzadkowane[dol]) * (pozycja - dol)

    @staticmethod
    def najdluzsza_seria(wartosci: Iterable[bool]) -> int:
        najlepsza = 0
        biezaca = 0
        for wartosc in wartosci:
            biezaca = biezaca + 1 if wartosc else 0
            najlepsza = max(najlepsza, biezaca)
        return najlepsza

    @staticmethod
    def dominanty(wartosci: Sequence[int]) -> tuple[int, ...]:
        if not wartosci:
            return ()
        czestosci = Counter(wartosci)
        maksimum = max(czestosci.values())
        return tuple(sorted(w for w, liczba in czestosci.items() if liczba == maksimum))

    @staticmethod
    def _srednia_ucieta(posortowane: Sequence[int]) -> float | None:
        if not posortowane:
            return None
        obcinka = int(len(posortowane) * 0.1)
        srodek = posortowane[obcinka : len(posortowane) - obcinka] or posortowane
        return float(mean(srodek))

    def _forma_meczow(self, mecze: Sequence[MeczZBramkami]) -> FormaWedlugMiejsca:
        znane = sum(1 for mecz in mecze if mecz.bramki is not None)
        return FormaWedlugMiejsca(
            liczba_znanych=znane,
            wystarczajaco_na_trend_5=znane >= PROG_MALEJ_PROBY,
            wystarczajaco_na_trend_10=znane >= 2 * PROG_MALEJ_PROBY,
            punkty=self._punkty_formy(mecze),
        )

    @staticmethod
    def _punkty_formy(mecze: Sequence[MeczZBramkami]) -> tuple[PunktFormy, ...]:
        historia: list[int] = []
        punkty = []
        for mecz in mecze:
            mediana_5 = srednia_5 = mediana_10 = None
            if mecz.bramki is not None:
                historia.append(mecz.bramki)
                if len(historia) >= PROG_MALEJ_PROBY:
                    okno_5 = historia[-PROG_MALEJ_PROBY:]
                    mediana_5 = float(median(okno_5))
                    srednia_5 = float(mean(okno_5))
                if len(historia) >= 2 * PROG_MALEJ_PROBY:
                    mediana_10 = float(median(historia[-2 * PROG_MALEJ_PROBY :]))
            punkty.append(
                PunktFormy(
                    id_mecz=mecz.id_mecz,
                    termin=mecz.termin,
                    sezon=mecz.sezon,
                    bramki=mecz.bramki,
                    mediana_kroczaca_5=mediana_5,
                    srednia_kroczaca_5=srednia_5,
                    mediana_kroczaca_10=mediana_10,
                )
            )
        return tuple(punkty)

    def _sezony_rozstepow(self, mecze: Sequence[MeczZBramkami]) -> tuple[RozstepSezonu, ...]:
        grupy: dict[str, list[int]] = {}
        for mecz in mecze:
            if mecz.bramki is not None:
                grupy.setdefault(mecz.sezon, []).append(mecz.bramki)
        wynik = []
        for sezon, wartosci in grupy.items():
            q1 = self.percentyl(wartosci, 0.25)
            q3 = self.percentyl(wartosci, 0.75)
            assert q1 is not None and q3 is not None
            iqr = q3 - q1
            dolna, gorna = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            wewnetrzne = [w for w in wartosci if dolna <= w <= gorna]
            wynik.append(
                RozstepSezonu(
                    sezon=sezon,
                    liczba_znanych=len(wartosci),
                    mala_proba=len(wartosci) < PROG_MALEJ_PROBY,
                    mediana=float(median(wartosci)),
                    kwartyl_pierwszy=q1,
                    kwartyl_trzeci=q3,
                    minimum=min(wewnetrzne) if wewnetrzne else min(wartosci),
                    maksimum=max(wewnetrzne) if wewnetrzne else max(wartosci),
                    wartosci_odstajace=tuple(sorted(w for w in wartosci if w < dolna or w > gorna)),
                )
            )
        return tuple(wynik)
