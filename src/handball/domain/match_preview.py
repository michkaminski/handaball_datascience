from __future__ import annotations

import statistics
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import date, datetime
from enum import StrEnum

from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
from handball.domain.match_predictions import PrognozaZapowiedzi
from handball.domain.team_details import KolejnoscPozycjiPolicy


class RezultatDruzyny(StrEnum):
    WYGRANA = "W"
    REMIS = "R"
    PORAZKA = "P"


@dataclass(frozen=True)
class DruzynaZapowiedzi:
    id_zespol: int | None
    nazwa: str | None


@dataclass(frozen=True)
class MeczZapowiedzi:
    id_mecz: int
    id_sezon: int
    sezon: str | None
    id_rozgrywki: int
    rozgrywki: str | None
    runda: str | None
    kolejka: str | None
    nr_kolejki: int | None
    data_faktyczna: datetime | None
    data_propozycji: datetime | None
    kolumna_gosp: DruzynaZapowiedzi
    kolumna_gosc: DruzynaZapowiedzi
    wynik_gosp: int | None
    wynik_gosc: int | None
    hala: str | None
    miasto: str | None
    zamiana: bool
    wycofany: bool
    walkower: bool

    @property
    def termin(self) -> datetime | None:
        return self.data_faktyczna or self.data_propozycji

    @property
    def gospodarz(self) -> DruzynaZapowiedzi:
        return self.kolumna_gosc if self.zamiana else self.kolumna_gosp

    @property
    def gosc(self) -> DruzynaZapowiedzi:
        return self.kolumna_gosp if self.zamiana else self.kolumna_gosc

    @property
    def bramki_gospodarza(self) -> int | None:
        return self.wynik_gosc if self.zamiana else self.wynik_gosp

    @property
    def bramki_goscia(self) -> int | None:
        return self.wynik_gosp if self.zamiana else self.wynik_gosc

    @property
    def rozegrany(self) -> bool:
        return (
            self.wynik_gosp is not None
            and self.wynik_gosc is not None
            and not self.wycofany
            and not self.walkower
        )


@dataclass(frozen=True)
class WystepZapowiedzi:
    id_mecz: int
    data: datetime
    id_sezon: int
    id_rozgrywki: int
    rozgrywki: str | None
    id_zespol: int
    id_rywal: int | None
    rywal: str | None
    u_siebie: bool
    bramki_zdobyte: int
    bramki_stracone: int

    @property
    def rezultat(self) -> RezultatDruzyny:
        if self.bramki_zdobyte > self.bramki_stracone:
            return RezultatDruzyny.WYGRANA
        if self.bramki_zdobyte < self.bramki_stracone:
            return RezultatDruzyny.PORAZKA
        return RezultatDruzyny.REMIS


@dataclass(frozen=True)
class OpcjeZapowiedzi:
    kadra_z_poprzedniego_sezonu: bool = False
    lata_bezposrednich: int | None = 10

    def __post_init__(self) -> None:
        if self.lata_bezposrednich is not None and self.lata_bezposrednich < 1:
            raise ValueError("Liczba lat meczów bezpośrednich musi być dodatnia.")


@dataclass(frozen=True)
class SezonKadry:
    id_sezon: int
    nazwa: str | None


@dataclass(frozen=True)
class ZawodnikKadry:
    id_zawodnik: int
    imie: str | None
    nazwisko: str | None
    numery: tuple[int, ...]
    pozycja: str | None
    mecze: int
    bramki: int
    zagrane: int | None = None
    data_urodzenia: date | None = None

    @property
    def zagral(self) -> bool:
        return (self.zagrane if self.zagrane is not None else self.mecze) >= 1


@dataclass(frozen=True)
class WystepSezonuZawodnika:
    id_zawodnik: int
    id_zespol: int | None
    zespol: str | None
    rozgrywki: str | None
    mecze: int
    bramki: int


@dataclass(frozen=True)
class KlubPoprzedniegoSezonu:
    nazwa: str
    mecze: int
    bramki: int


@dataclass(frozen=True)
class PoprzedniSezonZawodnika:
    mecze: int
    bramki: int
    inne_kluby: tuple[KlubPoprzedniegoSezonu, ...] = ()
    inne_ligi: tuple[str, ...] = ()
    tylko_druzyna: bool = False

    @property
    def srednia(self) -> float:
        return self.bramki / self.mecze if self.mecze else 0.0


@dataclass(frozen=True)
class CzlonekKadry:
    id_zawodnik: int
    imie: str | None
    nazwisko: str | None
    numery: tuple[int, ...]
    pozycja: str | None
    sezon: ZawodnikKadry | None
    poprzedni_sezon: PoprzedniSezonZawodnika | None = None
    data_urodzenia: date | None = None
    miejsce_strzelca: int | None = None

    @property
    def srednia(self) -> float | None:
        if self.sezon is None or not self.sezon.mecze:
            return None
        return self.sezon.bramki / self.sezon.mecze


@dataclass(frozen=True)
class GrupaKadry:
    kolejnosc: int
    czlonkowie: tuple[CzlonekKadry, ...]


@dataclass(frozen=True)
class KadraDruzyny:
    druzyna: DruzynaZapowiedzi
    grupy: tuple[GrupaKadry, ...]

    @property
    def liczba_zawodnikow(self) -> int:
        return sum(len(grupa.czlonkowie) for grupa in self.grupy)


@dataclass(frozen=True)
class Bilans:
    mecze: int
    wygrane: int
    remisy: int
    porazki: int
    bramki_zdobyte: int
    bramki_stracone: int

    @classmethod
    def z_wystepow(cls, wystepy: tuple[WystepZapowiedzi, ...]) -> Bilans:
        rezultaty = [w.rezultat for w in wystepy]
        return cls(
            mecze=len(wystepy),
            wygrane=rezultaty.count(RezultatDruzyny.WYGRANA),
            remisy=rezultaty.count(RezultatDruzyny.REMIS),
            porazki=rezultaty.count(RezultatDruzyny.PORAZKA),
            bramki_zdobyte=sum(w.bramki_zdobyte for w in wystepy),
            bramki_stracone=sum(w.bramki_stracone for w in wystepy),
        )

    @property
    def roznica(self) -> int:
        return self.bramki_zdobyte - self.bramki_stracone

    @property
    def srednia_zdobytych(self) -> float | None:
        return self.bramki_zdobyte / self.mecze if self.mecze else None

    @property
    def srednia_straconych(self) -> float | None:
        return self.bramki_stracone / self.mecze if self.mecze else None

    @property
    def procent_wygranych(self) -> float | None:
        return self.wygrane / self.mecze if self.mecze else None


@dataclass(frozen=True)
class Seria:
    rezultat: RezultatDruzyny
    dlugosc: int


@dataclass(frozen=True)
class ProfilDruzynyZapowiedzi:
    druzyna: DruzynaZapowiedzi
    forma: tuple[WystepZapowiedzi, ...]
    seria: Seria | None
    bilans_rozgrywek: Bilans
    bilans_miejsca: Bilans
    mediana_zdobytych: float | None
    mediana_straconych: float | None
    kadra: KadraDruzyny


@dataclass(frozen=True)
class BezposrednieMecze:
    mecze: tuple[WystepZapowiedzi, ...]
    bilans: Bilans
    od: datetime | None = None


@dataclass(frozen=True)
class ZapowiedzMeczu:
    mecz: MeczZapowiedzi
    stan_na: datetime
    gospodarz: ProfilDruzynyZapowiedzi
    gosc: ProfilDruzynyZapowiedzi
    bezposrednie: BezposrednieMecze
    prognoza: PrognozaZapowiedzi
    opcje: OpcjeZapowiedzi = OpcjeZapowiedzi()
    sezon_poprzedni: SezonKadry | None = None


class StatystykiZapowiedziCalculator:
    DLUGOSC_FORMY = 5

    def profil(
        self,
        druzyna: DruzynaZapowiedzi,
        wystepy: tuple[WystepZapowiedzi, ...],
        id_rozgrywki: int,
        u_siebie: bool,
        kadra: KadraDruzyny,
    ) -> ProfilDruzynyZapowiedzi:
        kolejne = self._od_najnowszych(wystepy)
        w_rozgrywkach = tuple(w for w in kolejne if w.id_rozgrywki == id_rozgrywki)
        return ProfilDruzynyZapowiedzi(
            druzyna=druzyna,
            forma=kolejne[: self.DLUGOSC_FORMY],
            seria=self.seria(kolejne),
            bilans_rozgrywek=Bilans.z_wystepow(w_rozgrywkach),
            bilans_miejsca=Bilans.z_wystepow(
                tuple(w for w in w_rozgrywkach if w.u_siebie == u_siebie)
            ),
            mediana_zdobytych=self._mediana([w.bramki_zdobyte for w in w_rozgrywkach]),
            mediana_straconych=self._mediana([w.bramki_stracone for w in w_rozgrywkach]),
            kadra=kadra,
        )

    def bezposrednie(
        self,
        wystepy_gospodarza: tuple[WystepZapowiedzi, ...],
        id_goscia: int | None,
        od: datetime | None = None,
    ) -> BezposrednieMecze:
        if id_goscia is None:
            return BezposrednieMecze((), Bilans.z_wystepow(()), od)
        wspolne = tuple(
            w
            for w in self._od_najnowszych(wystepy_gospodarza)
            if w.id_rywal == id_goscia and (od is None or w.data >= od)
        )
        return BezposrednieMecze(wspolne, Bilans.z_wystepow(wspolne), od)

    def poczatek_okresu(self, stan_na: datetime, lata: int | None) -> datetime | None:
        if lata is None:
            return None
        try:
            return stan_na.replace(year=stan_na.year - lata)
        except ValueError:
            return stan_na.replace(year=stan_na.year - lata, day=28)

    def seria(self, od_najnowszych: tuple[WystepZapowiedzi, ...]) -> Seria | None:
        if not od_najnowszych:
            return None
        pierwszy = od_najnowszych[0].rezultat
        dlugosc = 0
        for wystep in od_najnowszych:
            if wystep.rezultat != pierwszy:
                break
            dlugosc += 1
        return Seria(pierwszy, dlugosc)

    def _od_najnowszych(
        self, wystepy: tuple[WystepZapowiedzi, ...]
    ) -> tuple[WystepZapowiedzi, ...]:
        return tuple(sorted(wystepy, key=lambda w: (w.data, w.id_mecz), reverse=True))

    def _mediana(self, wartosci: list[int]) -> float | None:
        return float(statistics.median(wartosci)) if wartosci else None


class KadraZapowiedziCalculator:
    LICZBA_STRZELCOW = 5

    def __init__(
        self, kolejnosc: KolejnoscPozycjiPolicy, poziomy: KolejnoscRozgrywekPolicy
    ) -> None:
        self._kolejnosc = kolejnosc
        self._poziomy = poziomy

    def kadra(
        self,
        druzyna: DruzynaZapowiedzi,
        sezon: Sequence[ZawodnikKadry],
        dawni: Sequence[ZawodnikKadry] = (),
        poprzedni_sezon: Sequence[WystepSezonuZawodnika] = (),
        rozgrywki: str | None = None,
    ) -> KadraDruzyny:
        biezacy = {z.id_zawodnik: z for z in sezon}
        wczesniejsi = {z.id_zawodnik: z for z in dawni if z.zagral}
        miejsca = self.miejsca_strzelcow(sezon)
        poprzednie = self.poprzednie_sezony(
            poprzedni_sezon,
            druzyna.id_zespol,
            rozgrywki,
            frozenset(wczesniejsi) - frozenset(biezacy),
        )
        czlonkowie = [
            replace(
                self._czlonek(biezacy.get(id_zawodnik), wczesniejsi.get(id_zawodnik)),
                poprzedni_sezon=poprzednie.get(id_zawodnik),
                miejsce_strzelca=miejsca.get(id_zawodnik),
            )
            for id_zawodnik in dict.fromkeys([*biezacy, *wczesniejsi])
        ]
        grupy: dict[int, list[CzlonekKadry]] = {}
        for czlonek in czlonkowie:
            pozycje = (czlonek.pozycja,) if czlonek.pozycja else ()
            grupy.setdefault(self._kolejnosc.pozycja(pozycje), []).append(czlonek)
        return KadraDruzyny(
            druzyna=druzyna,
            grupy=tuple(
                GrupaKadry(kolejnosc, tuple(sorted(grupy[kolejnosc], key=self._klucz)))
                for kolejnosc in sorted(grupy)
            ),
        )

    def miejsca_strzelcow(self, zawodnicy: Sequence[ZawodnikKadry]) -> dict[int, int]:
        bramki = [z.bramki for z in zawodnicy if z.bramki > 0]
        miejsca: dict[int, int] = {}
        for zawodnik in zawodnicy:
            if zawodnik.bramki <= 0:
                continue
            miejsce = 1 + sum(1 for wartosc in bramki if wartosc > zawodnik.bramki)
            if miejsce <= self.LICZBA_STRZELCOW:
                miejsca[zawodnik.id_zawodnik] = miejsce
        return miejsca

    def poprzednie_sezony(
        self,
        wystepy: Sequence[WystepSezonuZawodnika],
        id_zespol: int | None,
        rozgrywki: str | None,
        tylko_druzyna: frozenset[int] = frozenset(),
    ) -> dict[int, PoprzedniSezonZawodnika]:
        poziom = self._poziom_ligi(rozgrywki)
        zawodnicy: dict[int, list[WystepSezonuZawodnika]] = {}
        for wystep in wystepy:
            zawodnicy.setdefault(wystep.id_zawodnik, []).append(wystep)
        wynik: dict[int, PoprzedniSezonZawodnika] = {}
        for id_zawodnik, lista in zawodnicy.items():
            dla_druzyny = id_zawodnik in tylko_druzyna
            liczone = [w for w in lista if w.id_zespol == id_zespol] if dla_druzyny else lista
            wynik[id_zawodnik] = PoprzedniSezonZawodnika(
                mecze=sum(w.mecze for w in liczone),
                bramki=sum(w.bramki for w in liczone),
                inne_kluby=self._inne_kluby(lista, id_zespol),
                inne_ligi=tuple(
                    dict.fromkeys(
                        (w.rozgrywki or "").strip()
                        for w in lista
                        if poziom is not None
                        and (inny := self._poziom_ligi(w.rozgrywki)) is not None
                        and inny != poziom
                    )
                ),
                tylko_druzyna=dla_druzyny,
            )
        return wynik

    def _inne_kluby(
        self, wystepy: Sequence[WystepSezonuZawodnika], id_zespol: int | None
    ) -> tuple[KlubPoprzedniegoSezonu, ...]:
        kluby: dict[int | None, list[WystepSezonuZawodnika]] = {}
        for wystep in wystepy:
            if wystep.id_zespol != id_zespol:
                kluby.setdefault(wystep.id_zespol, []).append(wystep)
        return tuple(
            KlubPoprzedniegoSezonu(
                nazwa=(lista[0].zespol or "").strip() or f"Drużyna #{id_klubu}",
                mecze=sum(w.mecze for w in lista),
                bramki=sum(w.bramki for w in lista),
            )
            for id_klubu, lista in kluby.items()
        )

    def _poziom_ligi(self, rozgrywki: str | None) -> int | None:
        if not rozgrywki:
            return None
        poziom = self._poziomy.poziom(rozgrywki)
        return poziom if poziom < len(self._poziomy.wzorce) else None

    def _czlonek(self, sezon: ZawodnikKadry | None, dawny: ZawodnikKadry | None) -> CzlonekKadry:
        glowny = sezon or dawny
        if glowny is None:
            raise ValueError("Członek kadry wymaga danych co najmniej jednego sezonu.")
        return CzlonekKadry(
            id_zawodnik=glowny.id_zawodnik,
            imie=glowny.imie or (dawny.imie if dawny else None),
            nazwisko=glowny.nazwisko or (dawny.nazwisko if dawny else None),
            numery=glowny.numery or (dawny.numery if dawny else ()),
            pozycja=glowny.pozycja or (dawny.pozycja if dawny else None),
            sezon=sezon,
            data_urodzenia=glowny.data_urodzenia or (dawny.data_urodzenia if dawny else None),
        )

    def _klucz(self, czlonek: CzlonekKadry) -> tuple[int, int, str, str, int]:
        return (
            -(czlonek.sezon.mecze if czlonek.sezon else 0),
            -(czlonek.poprzedni_sezon.mecze if czlonek.poprzedni_sezon else 0),
            (czlonek.nazwisko or "").casefold(),
            (czlonek.imie or "").casefold(),
            czlonek.id_zawodnik,
        )
