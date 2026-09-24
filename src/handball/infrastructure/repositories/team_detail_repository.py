from dataclasses import fields
from typing import Any

from sqlalchemy import Float, Integer, Select, and_, cast, distinct, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoDruzyny
from handball.domain.matches import DaneMeczu, PozycjaListyMeczow
from handball.domain.options import OpcjaWyboru
from handball.domain.team_details import (
    DaneZestawieniaDruzyny,
    FiltryDruzyny,
    FiltryZawodnikowDruzyny,
    FiltryZestawieniaDruzyny,
    HalaDruzyny,
    MeczDruzyny,
    OpcjeFiltrowDruzyny,
    SezonDruzyny,
    StronaMeczowDruzyny,
    StronaZawodnikowDruzyny,
    SzczegolyDruzyny,
    WpisZestawienia,
    ZawodnikDruzyny,
)
from handball.infrastructure.database.match_conditions import WarunkiMeczuSql
from handball.infrastructure.database.match_sides import StronyMeczuSql
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.database.models.players import Zawodnik
from handball.infrastructure.database.models.teams import Zespol, ZespolSezon
from handball.infrastructure.database.models.venues import Hala

LIMIT_HAL = 5


class SzczegolyDruzynySQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_szczegoly(self, id_zespol: int) -> SzczegolyDruzyny:
        try:
            zespol = self._sesja.get(Zespol, id_zespol)
            if zespol is None:
                raise NieZnalezionoDruzyny(id_zespol)
            sezony = self._sesja.execute(
                select(ZespolSezon, Sezon.nazwa)
                .join(Sezon, Sezon.id == ZespolSezon.id_sezon)
                .where(ZespolSezon.id_zespol == id_zespol)
                .order_by(Sezon.rok_rozpoczecia.desc().nulls_last(), Sezon.id.desc())
            ).all()
            liczba_meczow = self._sesja.scalar(
                select(func.count(Mecz.id)).where(self._mecz_druzyny(id_zespol))
            )
            gospodarz = or_(
                and_(Mecz.id_zespol_gosp == id_zespol, Mecz.zamiana.is_not(True)),
                and_(Mecz.id_zespol_gosc == id_zespol, Mecz.zamiana.is_(True)),
            )
            liczba = func.count(Mecz.id)
            hale = self._sesja.execute(
                select(
                    Hala.id,
                    Hala.nazwa,
                    Hala.miasto,
                    liczba,
                    func.count(Mecz.widzowie),
                    cast(func.avg(Mecz.widzowie), Float),
                )
                .join(Mecz, Mecz.id_hala == Hala.id)
                .where(gospodarz)
                .group_by(Hala.id, Hala.nazwa, Hala.miasto)
                .order_by(liczba.desc(), Hala.nazwa)
                .limit(LIMIT_HAL)
            ).all()
            return SzczegolyDruzyny(
                id_zespol=zespol.id,
                nr_klubu=zespol.nr_klubu,
                nazwa=zespol.nazwa,
                plec=zespol.plec,
                kategoria=zespol.kategoria,
                wycofany=zespol.wycofany,
                liczba_meczow=liczba_meczow or 0,
                sezony=tuple(
                    SezonDruzyny(
                        id_zespol_sezon=wpis.id,
                        id_sezon=wpis.id_sezon,
                        sezon=nazwa_sezonu,
                        nazwa=wpis.nazwa,
                        plec=wpis.plec,
                        kategoria=wpis.kategoria,
                        miasto=wpis.miasto,
                        wycofany=wpis.wycofany,
                    )
                    for wpis, nazwa_sezonu in sezony
                ),
                hale=tuple(HalaDruzyny(*wiersz) for wiersz in hale),
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać karty drużyny.") from wyjatek

    def pobierz_opcje_filtrow(self, id_zespol: int) -> OpcjeFiltrowDruzyny:
        try:
            sezony = self._sesja.execute(
                select(Sezon.id, Sezon.nazwa)
                .join(ZespolSezon, ZespolSezon.id_sezon == Sezon.id)
                .where(ZespolSezon.id_zespol == id_zespol)
                .order_by(Sezon.rok_rozpoczecia.desc().nulls_last(), Sezon.id.desc())
            ).all()
            rozgrywki = self._sesja.scalars(
                select(distinct(Rozgrywki.nazwa))
                .join(Mecz, Mecz.id_rozgrywki == Rozgrywki.id)
                .where(self._mecz_druzyny(id_zespol), Rozgrywki.nazwa.is_not(None))
                .order_by(Rozgrywki.nazwa)
            ).all()
            return OpcjeFiltrowDruzyny(
                sezony=tuple(OpcjaWyboru(id_sezon, nazwa) for id_sezon, nazwa in sezony),
                rozgrywki=tuple(rozgrywki),
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać filtrów drużyny.") from wyjatek

    def pobierz_mecze(self, id_zespol: int, filtry: FiltryDruzyny) -> StronaMeczowDruzyny:
        try:
            zapytanie = self._zapytanie_meczow(id_zespol, filtry)
            if filtry.tylko_zakonczone:
                zapytanie = zapytanie.where(WarunkiMeczuSql.zakonczony())
            liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
            numer = min(
                filtry.strona, max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
            )
            termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
            porzadek = termin.desc() if filtry.sortowanie == "-data" else termin.asc()
            wiersze = self._sesja.execute(
                zapytanie.order_by(porzadek.nulls_last(), Mecz.id)
                .limit(filtry.rozmiar_strony)
                .offset((numer - 1) * filtry.rozmiar_strony)
            ).all()
            return StronaMeczowDruzyny(
                [self._mecz(id_zespol, *wiersz) for wiersz in wiersze],
                liczba,
                numer,
                filtry.rozmiar_strony,
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać meczów drużyny.") from wyjatek

    def pobierz_wszystkie_mecze(
        self, id_zespol: int, filtry: FiltryDruzyny
    ) -> tuple[MeczDruzyny, ...]:
        try:
            termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
            wiersze = self._sesja.execute(
                self._zapytanie_meczow(id_zespol, filtry).order_by(
                    termin.asc().nulls_last(), Mecz.id
                )
            ).all()
            return tuple(self._mecz(id_zespol, *wiersz) for wiersz in wiersze)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać analityki drużyny.") from wyjatek

    def pobierz_zestawienie(
        self, id_zespol: int, filtry: FiltryZestawieniaDruzyny
    ) -> DaneZestawieniaDruzyny:
        try:
            wpis_druzyny = select(MeczZawodnik.id_mecz).where(
                MeczZawodnik.id_mecz == Mecz.id,
                MeczZawodnik.strona.in_(("gosp", "gosc")),
                StronyMeczuSql.zespol(MeczZawodnik.strona) == id_zespol,
            )
            termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
            wiersze = self._sesja.execute(
                self._zapytanie_meczow(
                    id_zespol,
                    FiltryDruzyny(
                        id_sezon=filtry.id_sezon,
                        rozgrywki=filtry.rozgrywki,
                        przeciwnik=filtry.przeciwnik,
                    ),
                )
                .where(wpis_druzyny.exists())
                .order_by(termin.asc().nulls_last(), Mecz.id)
            ).all()
            mecze = tuple(self._mecz(id_zespol, *wiersz) for wiersz in wiersze)
            if not mecze:
                return DaneZestawieniaDruzyny((), ())
            wpisy = self._sesja.execute(
                select(MeczZawodnik, Zawodnik.imie, Zawodnik.nazwisko)
                .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
                .outerjoin(Zawodnik, Zawodnik.id == MeczZawodnik.id_zawodnik)
                .where(
                    MeczZawodnik.id_mecz.in_([m.mecz.id_mecz for m in mecze]),
                    MeczZawodnik.strona.in_(("gosp", "gosc")),
                    StronyMeczuSql.zespol(MeczZawodnik.strona) == id_zespol,
                )
                .order_by(MeczZawodnik.id_mecz, MeczZawodnik.id_zawodnik)
            ).all()
            return DaneZestawieniaDruzyny(
                mecze,
                tuple(
                    WpisZestawienia(
                        id_mecz=wpis.id_mecz,
                        id_zawodnik=wpis.id_zawodnik,
                        imie=imie or wpis.imie,
                        nazwisko=nazwisko or wpis.nazwisko,
                        nr_koszulki=wpis.nr_koszulki,
                        pozycja=wpis.pozycja,
                        bramki=wpis.bramki,
                        dwie_minuty=wpis.dwie_minuty,
                        upomnienie=wpis.upomnienie,
                        dyskwalifikacja=wpis.dyskwalifikacja,
                        karne_bramki=wpis.karne_bramki,
                        karne_liczba=wpis.karne_liczba,
                    )
                    for wpis, imie, nazwisko in wpisy
                ),
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(
                "Nie udało się odczytać zestawienia sezonu drużyny."
            ) from wyjatek

    def pobierz_zawodnikow(
        self, id_zespol: int, filtry: FiltryZawodnikowDruzyny
    ) -> StronaZawodnikowDruzyny:
        try:
            zapytanie = self._zapytanie_zawodnikow(id_zespol, filtry)
            liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
            numer = min(
                filtry.strona, max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
            )
            kolumny = zapytanie.selected_columns
            pole = filtry.sortowanie.lstrip("-")
            wyrazenie = {
                "bramki": kolumny.bramki,
                "mecze": kolumny.mecze,
                "srednia": kolumny.srednia,
                "nazwisko": kolumny.nazwisko,
                "ostatni_mecz": kolumny.ostatni_mecz,
            }[pole]
            porzadek = wyrazenie.desc() if filtry.sortowanie.startswith("-") else wyrazenie.asc()
            wiersze = self._sesja.execute(
                zapytanie.order_by(
                    porzadek.nulls_last(),
                    kolumny.nazwisko.asc().nulls_last(),
                    kolumny.id_zawodnik,
                )
                .limit(filtry.rozmiar_strony)
                .offset((numer - 1) * filtry.rozmiar_strony)
            ).mappings()
            pozycje = [
                ZawodnikDruzyny(
                    id_zawodnik=wiersz["id_zawodnik"],
                    imie=wiersz["imie"],
                    nazwisko=wiersz["nazwisko"],
                    mecze=wiersz["mecze"],
                    mecze_ze_znanymi_bramkami=wiersz["znane"],
                    bramki=wiersz["bramki"],
                    karne_bramki=wiersz["karne_bramki"],
                    karne_liczba=wiersz["karne_liczba"],
                    dwie_minuty=wiersz["dwie_minuty"],
                    upomnienia=wiersz["upomnienia"],
                    dyskwalifikacje=wiersz["dyskwalifikacje"],
                    sezony=tuple(sorted(wiersz["sezony"] or ())),
                    ostatni_mecz=wiersz["ostatni_mecz"],
                )
                for wiersz in wiersze
            ]
            return StronaZawodnikowDruzyny(pozycje, liczba, numer, filtry.rozmiar_strony)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać zawodników drużyny.") from wyjatek

    @staticmethod
    def _mecz_druzyny(id_zespol: int) -> Any:
        return or_(Mecz.id_zespol_gosp == id_zespol, Mecz.id_zespol_gosc == id_zespol)

    def _zapytanie_meczow(
        self, id_zespol: int, filtry: FiltryDruzyny
    ) -> Select[tuple[Mecz, str, str, str | None, str | None, str | None]]:
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        zapytanie = (
            select(Mecz, Sezon.nazwa, Rozgrywki.nazwa, gospodarz.nazwa, gosc.nazwa, Hala.nazwa)
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .outerjoin(
                gospodarz,
                and_(
                    gospodarz.id_zespol == Mecz.id_zespol_gosp,
                    gospodarz.id_sezon == Mecz.id_sezon,
                ),
            )
            .outerjoin(
                gosc,
                and_(gosc.id_zespol == Mecz.id_zespol_gosc, gosc.id_sezon == Mecz.id_sezon),
            )
            .outerjoin(Hala, Hala.id == Mecz.id_hala)
            .where(self._mecz_druzyny(id_zespol))
        )
        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(Mecz.id_sezon == filtry.id_sezon)
        if filtry.rozgrywki:
            zapytanie = zapytanie.where(Rozgrywki.nazwa == filtry.rozgrywki)
        if filtry.przeciwnik:
            rywale = select(ZespolSezon.id_zespol).where(
                ZespolSezon.nazwa.icontains(filtry.przeciwnik, autoescape=True)
            )
            zapytanie = zapytanie.where(
                or_(
                    and_(Mecz.id_zespol_gosp == id_zespol, Mecz.id_zespol_gosc.in_(rywale)),
                    and_(Mecz.id_zespol_gosc == id_zespol, Mecz.id_zespol_gosp.in_(rywale)),
                )
            )
        return zapytanie

    @staticmethod
    def _mecz(
        id_zespol: int,
        mecz: Mecz,
        sezon: str,
        rozgrywki: str,
        gospodarz: str | None,
        gosc: str | None,
        hala: str | None,
    ) -> MeczDruzyny:
        return MeczDruzyny(
            PozycjaListyMeczow(
                id_mecz=mecz.id,
                termin=mecz.data_faktyczna or mecz.data_propozycji,
                sezon=sezon,
                rozgrywki=rozgrywki,
                gospodarz=gospodarz,
                gosc=gosc,
                mecz=DaneMeczu(
                    **{pole.name: getattr(mecz, pole.name) for pole in fields(DaneMeczu)}
                ),
                hala=hala,
            ),
            "gosp" if mecz.id_zespol_gosp == id_zespol else "gosc",
        )

    @staticmethod
    def _zapytanie_zawodnikow(id_zespol: int, filtry: FiltryZawodnikowDruzyny) -> Select[Any]:
        wpisy = (
            select(
                MeczZawodnik.id_zawodnik.label("id_zawodnik"),
                func.count(distinct(MeczZawodnik.id_mecz)).label("mecze"),
                func.count(MeczZawodnik.bramki).label("znane"),
                func.sum(MeczZawodnik.bramki).label("bramki"),
                func.sum(MeczZawodnik.karne_bramki).label("karne_bramki"),
                func.sum(MeczZawodnik.karne_liczba).label("karne_liczba"),
                func.sum(MeczZawodnik.dwie_minuty).label("dwie_minuty"),
                func.sum(cast(MeczZawodnik.upomnienie, Integer)).label("upomnienia"),
                func.sum(cast(MeczZawodnik.dyskwalifikacja, Integer)).label("dyskwalifikacje"),
                func.array_agg(distinct(Sezon.nazwa)).label("sezony"),
                func.max(func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)).label(
                    "ostatni_mecz"
                ),
                func.max(MeczZawodnik.imie).label("imie_wpisu"),
                func.max(MeczZawodnik.nazwisko).label("nazwisko_wpisu"),
            )
            .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .where(
                MeczZawodnik.strona.in_(("gosp", "gosc")),
                StronyMeczuSql.zespol(MeczZawodnik.strona) == id_zespol,
            )
            .group_by(MeczZawodnik.id_zawodnik)
        )
        if filtry.id_sezon is not None:
            wpisy = wpisy.where(Mecz.id_sezon == filtry.id_sezon)
        if filtry.rozgrywki:
            wpisy = wpisy.where(Rozgrywki.nazwa == filtry.rozgrywki)
        agregat = wpisy.subquery()
        imie = func.coalesce(Zawodnik.imie, agregat.c.imie_wpisu)
        nazwisko = func.coalesce(Zawodnik.nazwisko, agregat.c.nazwisko_wpisu)
        zapytanie = select(
            agregat.c.id_zawodnik,
            imie.label("imie"),
            nazwisko.label("nazwisko"),
            agregat.c.mecze,
            agregat.c.znane,
            agregat.c.bramki,
            (cast(agregat.c.bramki, Float) / func.nullif(agregat.c.znane, 0)).label("srednia"),
            agregat.c.karne_bramki,
            agregat.c.karne_liczba,
            agregat.c.dwie_minuty,
            agregat.c.upomnienia,
            agregat.c.dyskwalifikacje,
            agregat.c.sezony,
            agregat.c.ostatni_mecz,
        ).outerjoin(Zawodnik, Zawodnik.id == agregat.c.id_zawodnik)
        if filtry.zawodnik:
            fraza = filtry.zawodnik
            zapytanie = zapytanie.where(
                or_(
                    imie.icontains(fraza, autoescape=True),
                    nazwisko.icontains(fraza, autoescape=True),
                    func.concat(imie, " ", nazwisko).icontains(fraza, autoescape=True),
                    func.concat(nazwisko, " ", imie).icontains(fraza, autoescape=True),
                )
            )
        return zapytanie
