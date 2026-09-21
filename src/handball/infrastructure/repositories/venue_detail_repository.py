from __future__ import annotations

from decimal import Decimal
from typing import cast

from sqlalchemy import Select, and_, case, distinct, func, or_, select, union_all
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.elements import ColumnElement

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoHali
from handball.domain.venue_details import (
    FiltryZawodnikowHali,
    FrekwencjaHali,
    KomorkaKalendarzaHali,
    LimityStatystykHali,
    PorownanieHali,
    ProfilWynikowHali,
    PrzedzialHali,
    RankingDruzynyHali,
    RankingRozgrywekHali,
    RankingZawodnikaHali,
    RekordMeczuHali,
    RozkladKalendarzaHali,
    StatystykiHali,
    StronaZawodnikowHali,
    SzczegolyHali,
    TrendSezonuHali,
    ZawodnikHali,
)
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.database.models.players import Zawodnik
from handball.infrastructure.database.models.teams import Zespol, ZespolSezon
from handball.infrastructure.database.models.venues import Hala


class SzczegolyHaliSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_szczegoly(self, id_hala: int) -> SzczegolyHali:
        try:
            hala = self._sesja.get(Hala, id_hala)
            if hala is None:
                raise NieZnalezionoHali(id_hala)
            termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
            rozegrany = and_(
                Mecz.wynik_gosp_full.is_not(None),
                Mecz.wynik_gosc_full.is_not(None),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
            )
            podsumowanie = self._sesja.execute(
                select(
                    func.min(termin),
                    func.max(termin),
                    func.count(Mecz.id),
                    func.count(Mecz.id).filter(rozegrany),
                    func.count(distinct(Rozgrywki.nazwa)),
                    func.count(distinct(Mecz.id_sezon)),
                )
                .select_from(Mecz)
                .outerjoin(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
                .where(Mecz.id_hala == id_hala)
            ).one()
            liczba_zawodnikow = (
                self._sesja.scalar(
                    select(func.count(distinct(MeczZawodnik.id_zawodnik)))
                    .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
                    .where(Mecz.id_hala == id_hala, rozegrany)
                )
                or 0
            )
            zespoly = union_all(
                select(Mecz.id_zespol_gosp.label("id_zespol")).where(
                    Mecz.id_hala == id_hala, Mecz.id_zespol_gosp.is_not(None)
                ),
                select(Mecz.id_zespol_gosc.label("id_zespol")).where(
                    Mecz.id_hala == id_hala, Mecz.id_zespol_gosc.is_not(None)
                ),
            ).subquery()
            liczba_druzyn = (
                self._sesja.scalar(select(func.count(distinct(zespoly.c.id_zespol)))) or 0
            )
            return SzczegolyHali(
                id_hala=hala.id,
                nazwa=hala.nazwa,
                miasto=hala.miasto,
                ulica=hala.ulica,
                numer=hala.numer,
                pojemnosc=hala.pojemnosc,
                pierwszy_mecz=podsumowanie[0],
                ostatni_mecz=podsumowanie[1],
                liczba_meczow=podsumowanie[2],
                liczba_rozegranych=podsumowanie[3],
                liczba_rozgrywek=podsumowanie[4],
                liczba_sezonow=podsumowanie[5],
                liczba_druzyn=liczba_druzyn,
                liczba_zawodnikow=liczba_zawodnikow,
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać karty hali.") from wyjatek

    def pobierz_zawodnikow(
        self, id_hala: int, filtry: FiltryZawodnikowHali
    ) -> StronaZawodnikowHali:
        try:
            zapytanie = self._zapytanie_zawodnikow(id_hala, filtry)
            liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
            ostatnia = max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
            numer = min(filtry.strona, ostatnia)
            kolumna = zapytanie.selected_columns[filtry.sortowanie.removeprefix("-")]
            porzadek = kolumna.desc() if filtry.sortowanie.startswith("-") else kolumna.asc()
            wiersze = (
                self._sesja.execute(
                    zapytanie.order_by(porzadek.nulls_last(), Zawodnik.id.asc())
                    .offset((numer - 1) * filtry.rozmiar_strony)
                    .limit(filtry.rozmiar_strony)
                )
                .mappings()
                .all()
            )
            druzyny = self._druzyny_zawodnikow(
                id_hala, [cast(int, wiersz["id_zawodnik"]) for wiersz in wiersze]
            )
            pozycje = [
                ZawodnikHali(
                    id_zawodnik=cast(int, wiersz["id_zawodnik"]),
                    imie=cast(str | None, wiersz["imie"]),
                    nazwisko=cast(str | None, wiersz["nazwisko"]),
                    pierwszy_wystep=wiersz["pierwszy_wystep"],
                    ostatni_wystep=wiersz["ostatni_wystep"],
                    wystepy=cast(int, wiersz["wystepy"]),
                    bramki=wiersz["bramki"],
                    srednia_bramek=wiersz["srednia_bramek"],
                    druzyny=druzyny.get(cast(int, wiersz["id_zawodnik"]), ()),
                )
                for wiersz in wiersze
            ]
            return StronaZawodnikowHali(pozycje, liczba, numer, filtry.rozmiar_strony)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać zawodników hali.") from wyjatek

    def _zapytanie_zawodnikow(
        self, id_hala: int, filtry: FiltryZawodnikowHali
    ) -> Select[tuple[object, ...]]:
        termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
        zapytanie = (
            select(
                Zawodnik.id.label("id_zawodnik"),
                Zawodnik.imie.label("imie"),
                Zawodnik.nazwisko.label("nazwisko"),
                func.min(termin).label("pierwszy_wystep"),
                func.max(termin).label("ostatni_wystep"),
                func.count(distinct(MeczZawodnik.id_mecz)).label("wystepy"),
                func.sum(MeczZawodnik.bramki).label("bramki"),
                (
                    func.sum(MeczZawodnik.bramki)
                    / func.nullif(func.count(distinct(MeczZawodnik.id_mecz)), 0)
                ).label("srednia_bramek"),
            )
            .join(MeczZawodnik, MeczZawodnik.id_zawodnik == Zawodnik.id)
            .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
            .where(
                Mecz.id_hala == id_hala,
                Mecz.wynik_gosp_full.is_not(None),
                Mecz.wynik_gosc_full.is_not(None),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
            )
            .group_by(Zawodnik.id, Zawodnik.imie, Zawodnik.nazwisko)
        )
        if filtry.szukaj:
            for slowo in filtry.szukaj.split():
                zapytanie = zapytanie.where(
                    or_(
                        Zawodnik.imie.icontains(slowo, autoescape=True),
                        Zawodnik.nazwisko.icontains(slowo, autoescape=True),
                    )
                )
        return cast(Select[tuple[object, ...]], zapytanie)

    def _druzyny_zawodnikow(
        self, id_hala: int, identyfikatory: list[int]
    ) -> dict[int, tuple[str, ...]]:
        if not identyfikatory:
            return {}
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        nazwa = case(
            (MeczZawodnik.strona == "gosp", gospodarz.nazwa),
            (MeczZawodnik.strona == "gosc", gosc.nazwa),
        )
        wiersze = self._sesja.execute(
            select(
                MeczZawodnik.id_zawodnik,
                func.array_agg(distinct(nazwa)).label("druzyny"),
            )
            .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
            .outerjoin(
                gospodarz,
                and_(
                    gospodarz.id_zespol == Mecz.id_zespol_gosp,
                    gospodarz.id_sezon == Mecz.id_sezon,
                ),
            )
            .outerjoin(
                gosc,
                and_(
                    gosc.id_zespol == Mecz.id_zespol_gosc,
                    gosc.id_sezon == Mecz.id_sezon,
                ),
            )
            .where(
                Mecz.id_hala == id_hala,
                Mecz.wynik_gosp_full.is_not(None),
                Mecz.wynik_gosc_full.is_not(None),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
                MeczZawodnik.id_zawodnik.in_(identyfikatory),
            )
            .group_by(MeczZawodnik.id_zawodnik)
        ).all()
        return {
            id_zawodnik: tuple(sorted(n for n in (nazwy or []) if n))
            for id_zawodnik, nazwy in wiersze
        }

    def pobierz_statystyki(self, id_hala: int, limity: LimityStatystykHali) -> StatystykiHali:
        try:
            druzyny, liczba_druzyn = self._ranking_druzyn(id_hala, limity.druzyny)
            rozgrywki, liczba_rozgrywek = self._ranking_rozgrywek(id_hala, limity.rozgrywki)
            zawodnicy, liczba_zawodnikow = self._ranking_zawodnikow(
                id_hala, limity.zawodnicy, False
            )
            skuteczni, _ = self._ranking_zawodnikow(id_hala, limity.skuteczni_zawodnicy, True)
            trendy = self._trendy_sezonowe(id_hala)
            dni, kalendarz = self._kalendarz(id_hala)
            profil, histogram = self._profil_wynikow(id_hala)
            frekwencja = self._frekwencja(id_hala)
            porownanie = self._porownanie(id_hala)
            rekordy = self._rekordy(id_hala)
            return StatystykiHali(
                druzyny,
                rozgrywki,
                zawodnicy,
                skuteczni,
                liczba_druzyn,
                liczba_rozgrywek,
                liczba_zawodnikow,
                trendy,
                dni,
                kalendarz,
                histogram,
                profil,
                frekwencja,
                porownanie,
                rekordy,
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać statystyk hali.") from wyjatek

    def _ranking_druzyn(
        self, id_hala: int, limit: int | None
    ) -> tuple[list[RankingDruzynyHali], int]:
        rozegrany = and_(
            Mecz.id_hala == id_hala,
            Mecz.wynik_gosp_full.is_not(None),
            Mecz.wynik_gosc_full.is_not(None),
            Mecz.wycofany.is_not(True),
            Mecz.id_zespol_walkower.is_(None),
        )
        strony = union_all(
            select(
                Mecz.id_zespol_gosp.label("id_zespol"),
                Mecz.wynik_gosp_full.label("zdobyte"),
                Mecz.wynik_gosc_full.label("stracone"),
            ).where(rozegrany, Mecz.id_zespol_gosp.is_not(None)),
            select(
                Mecz.id_zespol_gosc.label("id_zespol"),
                Mecz.wynik_gosc_full.label("zdobyte"),
                Mecz.wynik_gosp_full.label("stracone"),
            ).where(rozegrany, Mecz.id_zespol_gosc.is_not(None)),
        ).cte("mecze_druzyn_hali")
        zapytanie = (
            select(
                strony.c.id_zespol,
                Zespol.nazwa,
                func.count().label("mecze"),
                func.sum(case((strony.c.zdobyte > strony.c.stracone, 1), else_=0)),
                func.sum(case((strony.c.zdobyte == strony.c.stracone, 1), else_=0)),
                func.sum(case((strony.c.zdobyte < strony.c.stracone, 1), else_=0)),
                func.sum(strony.c.zdobyte),
                func.sum(strony.c.stracone),
            )
            .join(Zespol, Zespol.id == strony.c.id_zespol, isouter=True)
            .group_by(strony.c.id_zespol, Zespol.nazwa)
            .order_by(func.count().desc(), Zespol.nazwa.asc().nulls_last())
        )
        liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
        if limit is not None:
            zapytanie = zapytanie.limit(limit)
        return (
            [
                RankingDruzynyHali(
                    id_zespol,
                    nazwa,
                    mecze,
                    zwyciestwa,
                    remisy,
                    porazki,
                    zdobyte,
                    stracone,
                )
                for (
                    id_zespol,
                    nazwa,
                    mecze,
                    zwyciestwa,
                    remisy,
                    porazki,
                    zdobyte,
                    stracone,
                ) in self._sesja.execute(zapytanie)
            ],
            liczba,
        )

    def _ranking_rozgrywek(
        self, id_hala: int, limit: int | None
    ) -> tuple[list[RankingRozgrywekHali], int]:
        zapytanie = (
            select(
                Rozgrywki.nazwa,
                func.count(Mecz.id).label("mecze"),
                func.count(distinct(Mecz.id_sezon)).label("sezony"),
                func.min(Sezon.nazwa),
                func.max(Sezon.nazwa),
            )
            .join(Mecz, Mecz.id_rozgrywki == Rozgrywki.id)
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .where(
                Mecz.id_hala == id_hala,
                Mecz.wynik_gosp_full.is_not(None),
                Mecz.wynik_gosc_full.is_not(None),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
            )
            .group_by(Rozgrywki.nazwa)
            .order_by(func.count(Mecz.id).desc(), Rozgrywki.nazwa)
        )
        liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
        if limit is not None:
            zapytanie = zapytanie.limit(limit)
        return (
            [
                RankingRozgrywekHali(nazwa, mecze, sezony, pierwszy, ostatni)
                for nazwa, mecze, sezony, pierwszy, ostatni in self._sesja.execute(zapytanie)
            ],
            liczba,
        )

    def _ranking_zawodnikow(
        self, id_hala: int, limit: int | None, wedlug_sredniej: bool
    ) -> tuple[list[RankingZawodnikaHali], int]:
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        nazwa_druzyny = case(
            (MeczZawodnik.strona == "gosp", gospodarz.nazwa),
            (MeczZawodnik.strona == "gosc", gosc.nazwa),
        )
        wystepy = func.count(distinct(MeczZawodnik.id_mecz))
        bramki = func.coalesce(func.sum(MeczZawodnik.bramki), 0)
        srednia = cast(ColumnElement[Decimal], bramki / func.nullif(wystepy, 0))
        zapytanie = (
            select(
                Zawodnik.id,
                Zawodnik.imie,
                Zawodnik.nazwisko,
                wystepy.label("wystepy"),
                bramki.label("bramki"),
                srednia.label("srednia"),
                func.array_agg(distinct(nazwa_druzyny)).label("druzyny"),
            )
            .join(MeczZawodnik, MeczZawodnik.id_zawodnik == Zawodnik.id)
            .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
            .outerjoin(
                gospodarz,
                and_(
                    gospodarz.id_zespol == Mecz.id_zespol_gosp,
                    gospodarz.id_sezon == Mecz.id_sezon,
                ),
            )
            .outerjoin(
                gosc,
                and_(
                    gosc.id_zespol == Mecz.id_zespol_gosc,
                    gosc.id_sezon == Mecz.id_sezon,
                ),
            )
            .where(
                Mecz.id_hala == id_hala,
                Mecz.wynik_gosp_full.is_not(None),
                Mecz.wynik_gosc_full.is_not(None),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
            )
            .group_by(Zawodnik.id, Zawodnik.imie, Zawodnik.nazwisko)
        )
        if wedlug_sredniej:
            zapytanie = zapytanie.having(wystepy >= 3).order_by(
                srednia.desc(), bramki.desc(), Zawodnik.nazwisko
            )
        else:
            zapytanie = zapytanie.order_by(wystepy.desc(), bramki.desc(), Zawodnik.nazwisko)
        liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
        if limit is not None:
            zapytanie = zapytanie.limit(limit)
        pozycje = []
        for id_zawodnik, imie, nazwisko, ile, gole, avg, druzyny in self._sesja.execute(zapytanie):
            pozycje.append(
                RankingZawodnikaHali(
                    id_zawodnik,
                    " ".join(n for n in (imie, nazwisko) if n) or "Brak danych",
                    ile,
                    gole,
                    Decimal(avg),
                    tuple(sorted(n for n in (druzyny or []) if n)),
                )
            )
        return pozycje, liczba

    def _warunki_rozegranego(self, id_hala: int | None = None) -> tuple[ColumnElement[bool], ...]:
        warunki: list[ColumnElement[bool]] = [
            Mecz.wynik_gosp_full.is_not(None),
            Mecz.wynik_gosc_full.is_not(None),
            Mecz.wycofany.is_not(True),
            Mecz.id_zespol_walkower.is_(None),
        ]
        if id_hala is not None:
            warunki.append(Mecz.id_hala == id_hala)
        return tuple(warunki)

    def _trendy_sezonowe(self, id_hala: int) -> list[TrendSezonuHali]:
        suma = Mecz.wynik_gosp_full + Mecz.wynik_gosc_full
        zapytanie = (
            select(
                Sezon.nazwa,
                func.count(Mecz.id),
                func.avg(suma),
                func.avg(Mecz.widzowie).filter(Mecz.widzowie.is_not(None)),
                func.count(Mecz.widzowie).filter(Mecz.widzowie.is_not(None)),
            )
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .where(*self._warunki_rozegranego(id_hala))
            .group_by(Sezon.id, Sezon.nazwa)
            .order_by(Sezon.nazwa)
        )
        return [
            TrendSezonuHali(sezon, mecze, Decimal(srednia), self._decimal(widzowie), kompletne)
            for sezon, mecze, srednia, widzowie, kompletne in self._sesja.execute(zapytanie)
        ]

    def _kalendarz(
        self, id_hala: int
    ) -> tuple[list[RozkladKalendarzaHali], list[KomorkaKalendarzaHali]]:
        termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
        dzien = func.extract("dow", termin)
        miesiac = func.extract("month", termin)
        nazwy_dni = {
            0: "Niedziela",
            1: "Poniedziałek",
            2: "Wtorek",
            3: "Środa",
            4: "Czwartek",
            5: "Piątek",
            6: "Sobota",
        }
        dni_wiersze = self._sesja.execute(
            select(dzien, func.count(Mecz.id))
            .where(*self._warunki_rozegranego(id_hala), termin.is_not(None))
            .group_by(dzien)
            .order_by(dzien)
        ).all()
        kalendarz_wiersze = self._sesja.execute(
            select(Sezon.nazwa, miesiac, func.count(Mecz.id))
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .where(*self._warunki_rozegranego(id_hala), termin.is_not(None))
            .group_by(Sezon.nazwa, miesiac)
            .order_by(Sezon.nazwa, miesiac)
        ).all()
        dni = [
            RozkladKalendarzaHali(nazwy_dni[int(numer)], liczba) for numer, liczba in dni_wiersze
        ]
        kalendarz = [
            KomorkaKalendarzaHali(sezon, int(numer), liczba)
            for sezon, numer, liczba in kalendarz_wiersze
        ]
        return dni, kalendarz

    def _profil_wynikow(self, id_hala: int) -> tuple[ProfilWynikowHali, list[PrzedzialHali]]:
        suma = Mecz.wynik_gosp_full + Mecz.wynik_gosc_full
        roznica = func.abs(Mecz.wynik_gosp_full - Mecz.wynik_gosc_full)
        wiersz = self._sesja.execute(
            select(
                func.avg(suma),
                func.percentile_cont(0.5).within_group(suma),
                func.stddev_pop(suma),
                func.min(suma),
                func.max(suma),
                func.percentile_cont(0.25).within_group(suma),
                func.percentile_cont(0.75).within_group(suma),
                func.avg(roznica),
                func.count(Mecz.id).filter(roznica <= 1),
                func.count(Mecz.id).filter(roznica <= 3),
                func.count(Mecz.id).filter(roznica <= 5),
            ).where(*self._warunki_rozegranego(id_hala))
        ).one()
        profil = ProfilWynikowHali(
            self._decimal(wiersz[0]),
            self._decimal(wiersz[1]),
            self._decimal(wiersz[2]),
            wiersz[3],
            wiersz[4],
            self._decimal(wiersz[5]),
            self._decimal(wiersz[6]),
            self._decimal(wiersz[7]),
            wiersz[8],
            wiersz[9],
            wiersz[10],
        )
        koszyk = case(
            (suma < 40, "poniżej 40"),
            (suma < 50, "40–49"),
            (suma < 60, "50–59"),
            (suma < 70, "60–69"),
            else_="70 i więcej",
        )
        kolejnosc = case((suma < 40, 1), (suma < 50, 2), (suma < 60, 3), (suma < 70, 4), else_=5)
        histogram = [
            PrzedzialHali(etykieta, mecze)
            for etykieta, _, mecze in self._sesja.execute(
                select(koszyk, kolejnosc, func.count(Mecz.id))
                .where(*self._warunki_rozegranego(id_hala))
                .group_by(koszyk, kolejnosc)
                .order_by(kolejnosc)
            )
        ]
        return profil, histogram

    def _frekwencja(self, id_hala: int) -> FrekwencjaHali:
        wiersz = self._sesja.execute(
            select(
                func.count(Mecz.widzowie).filter(Mecz.widzowie.is_not(None)),
                func.count(Mecz.id),
                func.avg(Mecz.widzowie).filter(Mecz.widzowie.is_not(None)),
                func.percentile_cont(0.5)
                .within_group(Mecz.widzowie)
                .filter(Mecz.widzowie.is_not(None)),
                func.max(Mecz.widzowie),
                Hala.pojemnosc,
            )
            .join(Hala, Hala.id == Mecz.id_hala)
            .where(*self._warunki_rozegranego(id_hala))
            .group_by(Hala.pojemnosc)
        ).one_or_none()
        if wiersz is None:
            return FrekwencjaHali(0, 0, None, None, None, None)
        srednia = self._decimal(wiersz[2])
        wypelnienie = srednia * 100 / wiersz[5] if srednia is not None and wiersz[5] else None
        return FrekwencjaHali(
            wiersz[0], wiersz[1], srednia, self._decimal(wiersz[3]), wiersz[4], wypelnienie
        )

    def _porownanie(self, id_hala: int) -> list[PorownanieHali]:
        suma = Mecz.wynik_gosp_full + Mecz.wynik_gosc_full
        roznica = func.abs(Mecz.wynik_gosp_full - Mecz.wynik_gosc_full)
        hale = (
            select(
                Mecz.id_hala.label("id_hala"),
                (func.count(Mecz.id) / func.count(distinct(Mecz.id_sezon))).label("mecze_sezon"),
                func.avg(suma).label("bramki"),
                func.avg(roznica).label("roznica"),
                func.avg(Mecz.widzowie).filter(Mecz.widzowie.is_not(None)).label("widzowie"),
            )
            .where(*self._warunki_rozegranego(), Mecz.id_hala.is_not(None))
            .group_by(Mecz.id_hala)
            .cte("porownanie_hal")
        )
        aktualna = self._sesja.execute(select(hale).where(hale.c.id_hala == id_hala)).one_or_none()
        srednie = self._sesja.execute(
            select(
                func.avg(hale.c.mecze_sezon),
                func.avg(hale.c.bramki),
                func.avg(hale.c.roznica),
                func.avg(hale.c.widzowie),
            )
        ).one()
        if aktualna is None:
            return []
        return [
            PorownanieHali("Mecze na sezon", self._decimal(aktualna[1]), self._decimal(srednie[0])),
            PorownanieHali("Bramki w meczu", self._decimal(aktualna[2]), self._decimal(srednie[1])),
            PorownanieHali("Różnica bramek", self._decimal(aktualna[3]), self._decimal(srednie[2])),
            PorownanieHali("Frekwencja", self._decimal(aktualna[4]), self._decimal(srednie[3])),
        ]

    def _rekordy(self, id_hala: int) -> list[RekordMeczuHali]:
        termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        nazwa_gosp = case((Mecz.zamiana.is_(True), gosc.nazwa), else_=gospodarz.nazwa)
        nazwa_gosc = case((Mecz.zamiana.is_(True), gospodarz.nazwa), else_=gosc.nazwa)
        wynik_gosp = case(
            (Mecz.zamiana.is_(True), Mecz.wynik_gosc_full), else_=Mecz.wynik_gosp_full
        )
        wynik_gosc = case(
            (Mecz.zamiana.is_(True), Mecz.wynik_gosp_full), else_=Mecz.wynik_gosc_full
        )
        baza = (
            select(Mecz.id, termin, nazwa_gosp, nazwa_gosc, wynik_gosp, wynik_gosc)
            .outerjoin(
                gospodarz,
                and_(
                    gospodarz.id_zespol == Mecz.id_zespol_gosp, gospodarz.id_sezon == Mecz.id_sezon
                ),
            )
            .outerjoin(
                gosc, and_(gosc.id_zespol == Mecz.id_zespol_gosc, gosc.id_sezon == Mecz.id_sezon)
            )
            .where(*self._warunki_rozegranego(id_hala))
        )
        definicje = [
            ("Pierwszy mecz", termin.asc(), func.extract("epoch", termin)),
            ("Ostatni mecz", termin.desc(), func.extract("epoch", termin)),
            (
                "Najwięcej bramek",
                (Mecz.wynik_gosp_full + Mecz.wynik_gosc_full).desc(),
                Mecz.wynik_gosp_full + Mecz.wynik_gosc_full,
            ),
            (
                "Najmniej bramek",
                (Mecz.wynik_gosp_full + Mecz.wynik_gosc_full).asc(),
                Mecz.wynik_gosp_full + Mecz.wynik_gosc_full,
            ),
            (
                "Największa różnica",
                func.abs(Mecz.wynik_gosp_full - Mecz.wynik_gosc_full).desc(),
                func.abs(Mecz.wynik_gosp_full - Mecz.wynik_gosc_full),
            ),
            ("Najwyższa frekwencja", Mecz.widzowie.desc().nulls_last(), Mecz.widzowie),
        ]
        rekordy = []
        for rodzaj, porzadek, wartosc in definicje:
            wiersz = self._sesja.execute(
                baza.add_columns(cast(ColumnElement[object], wartosc))
                .order_by(cast(ColumnElement[object], porzadek), Mecz.id)
                .limit(1)
            ).one_or_none()
            if wiersz is not None and wiersz[6] is not None:
                rekordy.append(
                    RekordMeczuHali(
                        rodzaj,
                        wiersz[0],
                        wiersz[1],
                        wiersz[2],
                        wiersz[3],
                        wiersz[4],
                        wiersz[5],
                        int(wiersz[6]),
                    )
                )
        return rekordy

    def _decimal(self, wartosc: object) -> Decimal | None:
        return Decimal(str(wartosc)) if wartosc is not None else None
