from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from handball.contracts.team_detail_repository import SzczegolyDruzynyReadRepository
from handball.contracts.team_report_repository import KadraRaportuReadRepository
from handball.domain.match_preview import WystepSezonuZawodnika, ZawodnikKadry
from handball.domain.match_rules import StatusMeczu
from handball.domain.team_details import (
    FiltryDruzyny,
    FiltryZawodnikowDruzyny,
    FiltryZestawieniaDruzyny,
    SezonDruzyny,
    SzczegolyDruzyny,
    WpisZestawienia,
    WystepDruzyny,
    WystepDruzynyPolicy,
    ZawodnikDruzyny,
)
from handball.domain.team_report import (
    DOMYSLNA_LICZBA_MECZOW,
    KolejnoscZawodnikowRaportuPolicy,
    MeczRaportu,
    PoprzedniSezonZawodnikaRaportu,
    RaportDruzyny,
    StronaZestawien,
    StrzelecMeczu,
    ZawodnikRaportu,
    ZestawieniaDruzyny,
)
from handball.services.match_preview_service import Zegar
from handball.services.team_detail_service import BilansDruzynyCalculator, ZestawienieDruzynyService

NAJWIECEJ_ZAWODNIKOW = 100
LICZBA_SEZONOW = 5
STRZELCOW_MECZU = 3


class RaportDruzynyService:
    def __init__(
        self,
        druzyny: SzczegolyDruzynyReadRepository,
        kadry: KadraRaportuReadRepository,
        zestawienie: ZestawienieDruzynyService,
        bilanse: BilansDruzynyCalculator,
        reguly: WystepDruzynyPolicy,
        kolejnosc: KolejnoscZawodnikowRaportuPolicy,
        zegar: Zegar,
    ) -> None:
        self._druzyny = druzyny
        self._kadry = kadry
        self._zestawienie = zestawienie
        self._bilanse = bilanse
        self._reguly = reguly
        self._kolejnosc = kolejnosc
        self._zegar = zegar

    def pobierz_raport(
        self, id_zespol: int, id_sezon: int, liczba_meczow: int = DOMYSLNA_LICZBA_MECZOW
    ) -> RaportDruzyny:
        szczegoly = self._druzyny.pobierz_szczegoly(id_zespol)
        sezon = self._sezon(szczegoly, id_sezon)
        teraz = self._zegar.teraz()
        wystepy = self._wystepy_do_sezonu(id_zespol, szczegoly, sezon)
        wystepy_sezonu = [w for w in wystepy if w.sezon == sezon.sezon]
        rozgrywki = tuple(dict.fromkeys(w.rozgrywki for w in wystepy_sezonu))
        zawodnicy, ze_skladu = self._zawodnicy(id_zespol, id_sezon, teraz)
        poprzedni = self._kadry.pobierz_poprzedni_sezon(id_sezon)
        if poprzedni is not None and zawodnicy:
            zawodnicy = self._z_poprzednim_sezonem(zawodnicy, poprzedni.id_sezon, teraz)
        bilanse = self._bilanse.bilanse_sezonow(
            wystepy, {s.sezon: s.nazwa for s in szczegoly.sezony}
        )
        kolejnosc = {s.sezon: i for i, s in enumerate(szczegoly.sezony)}
        return RaportDruzyny(
            szczegoly=szczegoly,
            sezon=sezon,
            poprzedni_sezon=poprzedni.nazwa if poprzedni else None,
            rozgrywki=rozgrywki,
            bilans=self._bilanse.bilans(wystepy_sezonu),
            sezony=tuple(
                sorted(bilanse, key=lambda b: kolejnosc.get(b.sezon, len(kolejnosc)))[
                    :LICZBA_SEZONOW
                ]
            ),
            zawodnicy=self._kolejnosc.uporzadkuj(zawodnicy),
            ze_skladu=ze_skladu,
            mecze=self._ostatnie_mecze(id_zespol, szczegoly, wystepy, liczba_meczow),
            stan_na=teraz,
        )

    def pobierz_zestawienia(self, id_zespol: int, id_sezon: int) -> ZestawieniaDruzyny:
        szczegoly = self._druzyny.pobierz_szczegoly(id_zespol)
        sezon = self._sezon(szczegoly, id_sezon)
        teraz = self._zegar.teraz()
        strony = [self._strona_zestawien(id_zespol, szczegoly, sezon.id_sezon, sezon.sezon, teraz)]
        poprzedni = self._kadry.pobierz_poprzedni_sezon(id_sezon)
        if poprzedni is not None:
            strony.append(
                self._strona_zestawien(
                    id_zespol, szczegoly, poprzedni.id_sezon, poprzedni.nazwa or "—", teraz
                )
            )
        return ZestawieniaDruzyny(szczegoly=szczegoly, strony=tuple(strony), stan_na=teraz)

    def _strona_zestawien(
        self,
        id_zespol: int,
        szczegoly: SzczegolyDruzyny,
        id_sezon: int,
        nazwa_sezonu: str,
        teraz: datetime,
    ) -> StronaZestawien:
        sezon = next((s for s in szczegoly.sezony if s.id_sezon == id_sezon), None)
        if sezon is None:
            return StronaZestawien(nazwa_sezonu, None, (), None, None)
        wystepy = self._wystepy(id_zespol, FiltryDruzyny(id_sezon=id_sezon))
        zestawienie = self._zestawienie.pobierz_zestawienie(
            id_zespol, FiltryZestawieniaDruzyny(id_sezon=id_sezon)
        )
        kadra = self._kadry.pobierz_kadre(id_zespol, id_sezon, teraz)
        roczniki = {z.id_zawodnik: z.data_urodzenia for z in kadra}
        brakujace = {w.id_zawodnik for w in zestawienie.wiersze} - set(roczniki)
        if brakujace:
            for z in self._kadry.pobierz_sklad_sezonu(id_zespol, id_sezon):
                roczniki.setdefault(z.id_zawodnik, z.data_urodzenia)
        return StronaZestawien(
            sezon=sezon.sezon,
            nazwa_druzyny=sezon.nazwa,
            rozgrywki=tuple(dict.fromkeys(w.rozgrywki for w in wystepy)),
            bilans=self._bilanse.bilans(wystepy),
            zestawienie=zestawienie,
            roczniki=roczniki,
        )

    @staticmethod
    def _sezon(szczegoly: SzczegolyDruzyny, id_sezon: int) -> SezonDruzyny:
        sezon = next((s for s in szczegoly.sezony if s.id_sezon == id_sezon), None)
        if sezon is None:
            raise ValueError("Drużyna nie ma wpisu w wybranym sezonie.")
        return sezon

    def _wystepy(self, id_zespol: int, filtry: FiltryDruzyny) -> list[WystepDruzyny]:
        return [
            self._reguly.wystep(mecz)
            for mecz in self._druzyny.pobierz_wszystkie_mecze(id_zespol, filtry)
        ]

    def _wystepy_do_sezonu(
        self, id_zespol: int, szczegoly: SzczegolyDruzyny, sezon: SezonDruzyny
    ) -> list[WystepDruzyny]:
        pozycja = szczegoly.sezony.index(sezon)
        dozwolone = {s.sezon for s in szczegoly.sezony[pozycja:]}
        return [w for w in self._wystepy(id_zespol, FiltryDruzyny()) if w.sezon in dozwolone]

    def _zawodnicy(
        self, id_zespol: int, id_sezon: int, teraz: datetime
    ) -> tuple[list[ZawodnikRaportu], bool]:
        statystyki = {
            z.id_zawodnik: z
            for z in self._druzyny.pobierz_zawodnikow(
                id_zespol,
                FiltryZawodnikowDruzyny(id_sezon=id_sezon, rozmiar_strony=NAJWIECEJ_ZAWODNIKOW),
            ).pozycje
        }
        kadra = {z.id_zawodnik: z for z in self._kadry.pobierz_kadre(id_zespol, id_sezon, teraz)}
        if not statystyki and not kadra:
            sklad = self._kadry.pobierz_sklad_sezonu(id_zespol, id_sezon)
            return [self._zawodnik(z.id_zawodnik, z, None) for z in sklad], bool(sklad)
        identyfikatory = list(dict.fromkeys([*kadra, *statystyki]))
        return [self._zawodnik(i, kadra.get(i), statystyki.get(i)) for i in identyfikatory], False

    @staticmethod
    def _zawodnik(
        id_zawodnik: int, kadra: ZawodnikKadry | None, statystyki: ZawodnikDruzyny | None
    ) -> ZawodnikRaportu:
        return ZawodnikRaportu(
            id_zawodnik=id_zawodnik,
            imie=(kadra.imie if kadra else None) or (statystyki.imie if statystyki else None),
            nazwisko=(kadra.nazwisko if kadra else None)
            or (statystyki.nazwisko if statystyki else None),
            numery=kadra.numery if kadra else (),
            pozycja=kadra.pozycja if kadra else None,
            data_urodzenia=kadra.data_urodzenia if kadra else None,
            sezon=statystyki,
        )

    def _z_poprzednim_sezonem(
        self, zawodnicy: list[ZawodnikRaportu], id_poprzedni: int, teraz: datetime
    ) -> list[ZawodnikRaportu]:
        wystepy = self._kadry.pobierz_wystepy_zawodnikow(
            [z.id_zawodnik for z in zawodnicy], id_poprzedni, teraz
        )
        grupy: dict[int, list[WystepSezonuZawodnika]] = {}
        for wystep in wystepy:
            grupy.setdefault(wystep.id_zawodnik, []).append(wystep)
        return [
            ZawodnikRaportu(
                id_zawodnik=z.id_zawodnik,
                imie=z.imie,
                nazwisko=z.nazwisko,
                numery=z.numery,
                pozycja=z.pozycja,
                data_urodzenia=z.data_urodzenia,
                sezon=z.sezon,
                poprzedni=PoprzedniSezonZawodnikaRaportu(
                    tuple(sorted(grupy.get(z.id_zawodnik, []), key=lambda w: -w.mecze))
                ),
            )
            for z in zawodnicy
        ]

    def _ostatnie_mecze(
        self,
        id_zespol: int,
        szczegoly: SzczegolyDruzyny,
        wystepy: Sequence[WystepDruzyny],
        liczba: int,
    ) -> tuple[MeczRaportu, ...]:
        rozegrane = [
            w
            for w in wystepy
            if w.status in {StatusMeczu.ROZEGRANY, StatusMeczu.WALKOWER} and w.termin is not None
        ]
        ostatnie = sorted(rozegrane, key=lambda w: (w.termin, w.id_mecz), reverse=True)[:liczba]
        identyfikatory_sezonow = {s.sezon: s.id_sezon for s in szczegoly.sezony}
        wpisy: dict[int, dict[int, WpisZestawienia]] = {}
        for nazwa in dict.fromkeys(w.sezon for w in ostatnie):
            id_sezon = identyfikatory_sezonow.get(nazwa)
            if id_sezon is None:
                continue
            dane = self._druzyny.pobierz_zestawienie(
                id_zespol, FiltryZestawieniaDruzyny(id_sezon=id_sezon)
            )
            for wpis in dane.wpisy:
                wpisy.setdefault(wpis.id_mecz, {})[wpis.id_zawodnik] = wpis
        return tuple(self._mecz(w, list(wpisy.get(w.id_mecz, {}).values())) for w in ostatnie)

    @staticmethod
    def _mecz(wystep: WystepDruzyny, wpisy: Sequence[WpisZestawienia]) -> MeczRaportu:
        def suma(wartosci: list[int | None]) -> int | None:
            znane = [w for w in wartosci if w is not None]
            return sum(znane) if znane else None

        strzelcy = sorted((w for w in wpisy if w.bramki), key=lambda w: -(w.bramki or 0))
        return MeczRaportu(
            wystep=wystep,
            strzelcy=tuple(
                StrzelecMeczu(RaportDruzynyService._skrot(w), w.bramki or 0)
                for w in strzelcy[:STRZELCOW_MECZU]
            ),
            karne_bramki=suma([w.karne_bramki for w in wpisy]),
            karne_liczba=suma([w.karne_liczba for w in wpisy]),
            dwie_minuty=suma([w.dwie_minuty for w in wpisy]),
        )

    @staticmethod
    def _skrot(wpis: WpisZestawienia) -> str:
        inicjal = f"{wpis.imie[0]}." if wpis.imie else ""
        return " ".join(c for c in (inicjal, wpis.nazwisko or "") if c) or f"#{wpis.id_zawodnik}"
