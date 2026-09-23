import math
from collections.abc import Sequence
from datetime import datetime
from statistics import mean, median, variance

from handball.contracts.opponent_defense_repository import DefensywaRywalaReadRepository
from handball.domain.opponent_defense import (
    KLASY_DEFENSYWY,
    AnalizaDefensywyRywala,
    FiltryDefensywyRywala,
    KonfiguracjaDefensywyRywala,
    MeczLigowy,
    MeczZDefensywaRywala,
    StatystykiKlasyDefensywy,
    WspolczynnikiKorelacji,
    WynikRegresji,
    WystapienieZDanymiLigowymi,
)

LiniaZespolu = list[tuple[datetime, int]]


def _percentyl(wartosci: Sequence[int], udzial: float) -> float | None:
    if not wartosci:
        return None
    posortowane = sorted(wartosci)
    pozycja = (len(posortowane) - 1) * udzial
    dol = int(pozycja)
    gora = min(dol + 1, len(posortowane) - 1)
    return posortowane[dol] + (posortowane[gora] - posortowane[dol]) * (pozycja - dol)


def pearson(pary: Sequence[tuple[float, float]]) -> float | None:
    if len(pary) < 2:
        return None
    xs = [x for x, _ in pary]
    ys = [y for _, y in pary]
    xbar, ybar = mean(xs), mean(ys)
    licznik = sum((x - xbar) * (y - ybar) for x, y in pary)
    suma_x = sum((x - xbar) ** 2 for x in xs)
    suma_y = sum((y - ybar) ** 2 for y in ys)
    mianownik = math.sqrt(suma_x * suma_y)
    return licznik / mianownik if mianownik else None


def _rangi(wartosci: Sequence[float]) -> list[float]:
    kolejnosc = sorted(range(len(wartosci)), key=lambda i: wartosci[i])
    rangi = [0.0] * len(wartosci)
    i = 0
    while i < len(kolejnosc):
        j = i
        while j + 1 < len(kolejnosc) and wartosci[kolejnosc[j + 1]] == wartosci[kolejnosc[i]]:
            j += 1
        srednia_ranga = (i + j) / 2 + 1
        for m in range(i, j + 1):
            rangi[kolejnosc[m]] = srednia_ranga
        i = j + 1
    return rangi


def spearman(pary: Sequence[tuple[float, float]]) -> float | None:
    if len(pary) < 2:
        return None
    xs = [x for x, _ in pary]
    ys = [y for _, y in pary]
    return pearson(list(zip(_rangi(xs), _rangi(ys), strict=True)))


def regresja_liniowa(pary: Sequence[tuple[float, float]]) -> WynikRegresji:
    n = len(pary)
    if n < 2:
        return WynikRegresji(None, None, None, None, n)
    xs = [x for x, _ in pary]
    ys = [y for _, y in pary]
    xbar, ybar = mean(xs), mean(ys)
    sxx = sum((x - xbar) ** 2 for x in xs)
    if sxx == 0:
        return WynikRegresji(None, None, None, None, n)
    sxy = sum((x - xbar) * (y - ybar) for x, y in pary)
    beta1 = sxy / sxx
    beta0 = ybar - beta1 * xbar
    predykcje = [beta0 + beta1 * x for x in xs]
    sst = sum((y - ybar) ** 2 for y in ys)
    ssr = sum((yhat - ybar) ** 2 for yhat in predykcje)
    r_kwadrat = ssr / sst if sst else None
    przedzial = None
    if n > 2 and sst:
        sse = sum((y - yhat) ** 2 for y, yhat in zip(ys, predykcje, strict=True))
        wariancja_resztowa = sse / (n - 2)
        se_beta1 = math.sqrt(wariancja_resztowa / sxx)
        margines = 1.96 * se_beta1
        przedzial = (beta1 - margines, beta1 + margines)
    return WynikRegresji(beta0, beta1, r_kwadrat, przedzial, n)


def _ga_przed(historia: LiniaZespolu, przed: datetime | None) -> tuple[float | None, int]:
    if przed is None:
        return None, 0
    wartosci = [bramki for kiedy, bramki in historia if kiedy < przed]
    if not wartosci:
        return None, 0
    return sum(wartosci) / len(wartosci), len(wartosci)


def klasyfikuj_defense_factor(
    defense_factor: float, konfiguracja: KonfiguracjaDefensywyRywala
) -> str:
    if defense_factor < konfiguracja.granica_bardzo_mocna:
        return "Bardzo mocna"
    if defense_factor < konfiguracja.granica_mocna:
        return "Mocna"
    if defense_factor <= konfiguracja.granica_slaba:
        return "Przeciętna"
    if defense_factor <= konfiguracja.granica_bardzo_slaba:
        return "Słaba"
    return "Bardzo słaba"


class DefensywaRywalaService:
    def __init__(self, repozytorium: DefensywaRywalaReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_analize(
        self,
        id_zawodnik: int,
        filtry: FiltryDefensywyRywala,
        konfiguracja: KonfiguracjaDefensywyRywala | None = None,
    ) -> AnalizaDefensywyRywala:
        konfiguracja = konfiguracja or KonfiguracjaDefensywyRywala()
        przeciwnicy = (
            self._repozytorium.pobierz_zespoly_o_nazwie(filtry.przeciwnik)
            if filtry.przeciwnik
            else None
        )
        wystapienia = self._filtruj(
            self._repozytorium.pobierz_wystapienia(id_zawodnik), filtry, przeciwnicy
        )
        identyfikatory = frozenset(w.id_rozgrywki for w in wystapienia)
        linie_zespolow, linie_lig = self._zbuduj_linie(
            self._repozytorium.pobierz_mecze_ligowe(identyfikatory)
        )
        linie_poprzednie: dict[int, dict[int, LiniaZespolu]] = {}
        if konfiguracja.uzyj_poprzedniego_sezonu:
            do_sprawdzenia = frozenset(
                (w.id_rozgrywki, w.rozgrywki, w.rok_rozpoczecia_sezonu)
                for w in wystapienia
                if w.rok_rozpoczecia_sezonu is not None
            )
            mapa_poprzednich = self._repozytorium.pobierz_poprzednie_rozgrywki(do_sprawdzenia)
            poprzednie_id = frozenset(mapa_poprzednich.values())
            linie_poprzednie_surowe, _ = self._zbuduj_linie(
                self._repozytorium.pobierz_mecze_ligowe(poprzednie_id)
            )
            for biezace_id, poprzednie_id_rozgrywki in mapa_poprzednich.items():
                linie_poprzednie[biezace_id] = linie_poprzednie_surowe.get(
                    poprzednie_id_rozgrywki, {}
                )
        mecze = tuple(
            self._policz_mecz(w, linie_zespolow, linie_lig, linie_poprzednie, konfiguracja)
            for w in wystapienia
        )
        pary = [
            (m.defense_factor, float(m.bramki_zawodnika))
            for m in mecze
            if m.defense_factor is not None and m.bramki_zawodnika is not None
        ]
        klasy = tuple(
            self._statystyki_klasy(
                klasa,
                [
                    m.bramki_zawodnika
                    for m in mecze
                    if m.klasa_defensywy == klasa and m.bramki_zawodnika is not None
                ],
                konfiguracja.progi_prawdopodobienstwa,
            )
            for klasa in KLASY_DEFENSYWY
        )
        return AnalizaDefensywyRywala(
            id_zawodnik=id_zawodnik,
            mecze=mecze,
            klasy=klasy,
            korelacja=WspolczynnikiKorelacji(pearson(pary), spearman(pary), len(pary)),
            regresja=regresja_liniowa(pary),
            konfiguracja=konfiguracja,
            liczba_wystapien=len(mecze),
            liczba_meczow_ze_znanymi_bramkami=sum(
                1 for m in mecze if m.bramki_zawodnika is not None
            ),
            liczba_meczow_z_defense_factor=len(pary),
        )

    @staticmethod
    def _filtruj(
        wystapienia: tuple[WystapienieZDanymiLigowymi, ...],
        filtry: FiltryDefensywyRywala,
        przeciwnicy: frozenset[int] | None = None,
    ) -> list[WystapienieZDanymiLigowymi]:
        wynik = [
            w
            for w in wystapienia
            if (not filtry.tylko_pelne_dane or w.dane_pelne)
            and (filtry.id_sezon is None or w.id_sezon == filtry.id_sezon)
            and (not filtry.rozgrywki or w.rozgrywki == filtry.rozgrywki)
            and (filtry.miejsce is None or w.miejsce == filtry.miejsce)
            and (przeciwnicy is None or w.id_zespol_przeciwnika in przeciwnicy)
        ]
        if filtry.liczba_ostatnich_sezonow is not None:
            sezony = sorted(
                {(w.rok_rozpoczecia_sezonu or 0, w.id_sezon) for w in wynik}, reverse=True
            )
            dozwolone = {id_sezon for _, id_sezon in sezony[: filtry.liczba_ostatnich_sezonow]}
            wynik = [w for w in wynik if w.id_sezon in dozwolone]
        return wynik

    @staticmethod
    def _zbuduj_linie(
        mecze_ligowe: tuple[MeczLigowy, ...],
    ) -> tuple[dict[int, dict[int, LiniaZespolu]], dict[int, LiniaZespolu]]:
        linie_zespolow: dict[int, dict[int, LiniaZespolu]] = {}
        linie_lig: dict[int, LiniaZespolu] = {}
        for m in mecze_ligowe:
            linie_lig.setdefault(m.id_rozgrywki, []).append((m.termin, m.bramki_stracone))
            linie_zespolow.setdefault(m.id_rozgrywki, {}).setdefault(m.id_zespol, []).append(
                (m.termin, m.bramki_stracone)
            )
        for lista in linie_lig.values():
            lista.sort(key=lambda p: p[0])
        for zespoly in linie_zespolow.values():
            for lista in zespoly.values():
                lista.sort(key=lambda p: p[0])
        return linie_zespolow, linie_lig

    def _policz_mecz(
        self,
        w: WystapienieZDanymiLigowymi,
        linie_zespolow: dict[int, dict[int, LiniaZespolu]],
        linie_lig: dict[int, LiniaZespolu],
        linie_poprzednie: dict[int, dict[int, LiniaZespolu]],
        konfiguracja: KonfiguracjaDefensywyRywala,
    ) -> MeczZDefensywaRywala:
        historia_zespolu = linie_zespolow.get(w.id_rozgrywki, {}).get(w.id_zespol_przeciwnika, [])
        historia_ligi = linie_lig.get(w.id_rozgrywki, [])
        ga_team, n = _ga_przed(historia_zespolu, w.termin)
        ga_league, _ = _ga_przed(historia_ligi, w.termin)
        historia_poprzednia = linie_poprzednie.get(w.id_rozgrywki, {}).get(
            w.id_zespol_przeciwnika, []
        )
        ga_previous = (
            mean(bramki for _, bramki in historia_poprzednia) if historia_poprzednia else None
        )
        ga_smoothed = defense_factor = klasa = None
        ga_team_wartosc = ga_team if ga_team is not None else 0.0
        if ga_league is not None:
            k = konfiguracja.k_shrinkage
            if konfiguracja.uzyj_poprzedniego_sezonu and ga_previous is not None:
                w_wagi = konfiguracja.w_poprzedni_sezon
                ga_smoothed = (n * ga_team_wartosc + w_wagi * ga_previous + k * ga_league) / (
                    n + w_wagi + k
                )
            elif n == 0:
                ga_smoothed = ga_league
            else:
                ga_smoothed = (n * ga_team_wartosc + k * ga_league) / (n + k)
            if ga_league:
                defense_factor = ga_smoothed / ga_league
                klasa = klasyfikuj_defense_factor(defense_factor, konfiguracja)
        return MeczZDefensywaRywala(
            id_mecz=w.id_mecz,
            termin=w.termin,
            sezon=w.sezon,
            rozgrywki=w.rozgrywki,
            druzyna_zawodnika=w.druzyna_zawodnika,
            przeciwnik=w.przeciwnik,
            miejsce=w.miejsce,
            bramki_zawodnika=w.bramki_zawodnika,
            wynik_druzyny_zawodnika=w.wynik_druzyny_zawodnika,
            wynik_przeciwnika=w.wynik_przeciwnika,
            ga_team=ga_team,
            ga_previous=ga_previous if konfiguracja.uzyj_poprzedniego_sezonu else None,
            ga_smoothed=ga_smoothed,
            ga_league=ga_league,
            n_meczy_rywala=n,
            defense_factor=defense_factor,
            klasa_defensywy=klasa,
        )

    @staticmethod
    def _statystyki_klasy(
        klasa: str, bramki: Sequence[int], progi: Sequence[int]
    ) -> StatystykiKlasyDefensywy:
        n = len(bramki)
        if n == 0:
            return StatystykiKlasyDefensywy(
                klasa=klasa,
                n=0,
                suma_bramek=0,
                srednia=None,
                mediana=None,
                minimum=None,
                maksimum=None,
                kwartyl_pierwszy=None,
                kwartyl_trzeci=None,
                wariancja=None,
                odchylenie_standardowe=None,
                udzialy_progowe=tuple((p, 0.0) for p in progi),
                minimum_wewnetrzne=None,
                maksimum_wewnetrzne=None,
                wartosci_odstajace=(),
            )
        wariancja_probki = variance(bramki) if n >= 2 else None
        q1 = _percentyl(bramki, 0.25)
        q3 = _percentyl(bramki, 0.75)
        assert q1 is not None and q3 is not None
        iqr = q3 - q1
        dolna, gorna = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        wewnetrzne = [b for b in bramki if dolna <= b <= gorna]
        return StatystykiKlasyDefensywy(
            klasa=klasa,
            n=n,
            suma_bramek=sum(bramki),
            srednia=mean(bramki),
            mediana=float(median(bramki)),
            minimum=min(bramki),
            maksimum=max(bramki),
            kwartyl_pierwszy=q1,
            kwartyl_trzeci=q3,
            wariancja=wariancja_probki,
            odchylenie_standardowe=math.sqrt(wariancja_probki)
            if wariancja_probki is not None
            else None,
            udzialy_progowe=tuple((p, sum(b >= p for b in bramki) / n) for p in progi),
            minimum_wewnetrzne=min(wewnetrzne) if wewnetrzne else min(bramki),
            maksimum_wewnetrzne=max(wewnetrzne) if wewnetrzne else max(bramki),
            wartosci_odstajace=tuple(sorted(b for b in bramki if b < dolna or b > gorna)),
        )
