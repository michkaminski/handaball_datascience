from sqlalchemy import case, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych
from handball.domain.opponent_defense import MeczLigowy, WystapienieZDanymiLigowymi
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.database.models.teams import ZespolSezon


class DefensywaRywalaSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_wystapienia(self, id_zawodnik: int) -> tuple[WystapienieZDanymiLigowymi, ...]:
        try:
            termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
            miejsce = case(
                (MeczZawodnik.strona == "gosp", "dom"), (MeczZawodnik.strona == "gosc", "wyjazd")
            )
            gospodarz_sezon = aliased(ZespolSezon)
            gosc_sezon = aliased(ZespolSezon)
            zapytanie = (
                select(
                    Mecz.id,
                    termin,
                    Mecz.id_sezon,
                    Sezon.nazwa,
                    Sezon.rok_rozpoczecia,
                    Mecz.id_rozgrywki,
                    Rozgrywki.nazwa,
                    Mecz.id_zespol_gosp,
                    gospodarz_sezon.nazwa,
                    Mecz.id_zespol_gosc,
                    gosc_sezon.nazwa,
                    Mecz.wynik_gosp_full,
                    Mecz.wynik_gosc_full,
                    Mecz.wycofany,
                    Mecz.id_zespol_walkower,
                    Mecz.zamiana,
                    func.max(miejsce),
                    func.count(func.distinct(MeczZawodnik.strona)),
                    func.sum(MeczZawodnik.bramki),
                )
                .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
                .join(Sezon, Sezon.id == Mecz.id_sezon)
                .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
                .outerjoin(
                    gospodarz_sezon,
                    (gospodarz_sezon.id_zespol == Mecz.id_zespol_gosp)
                    & (gospodarz_sezon.id_sezon == Mecz.id_sezon),
                )
                .outerjoin(
                    gosc_sezon,
                    (gosc_sezon.id_zespol == Mecz.id_zespol_gosc)
                    & (gosc_sezon.id_sezon == Mecz.id_sezon),
                )
                .where(
                    MeczZawodnik.id_zawodnik == id_zawodnik,
                    MeczZawodnik.strona.in_(("gosp", "gosc")),
                )
                .group_by(
                    Mecz.id,
                    termin,
                    Mecz.id_sezon,
                    Sezon.nazwa,
                    Sezon.rok_rozpoczecia,
                    Mecz.id_rozgrywki,
                    Rozgrywki.nazwa,
                    Mecz.id_zespol_gosp,
                    gospodarz_sezon.nazwa,
                    Mecz.id_zespol_gosc,
                    gosc_sezon.nazwa,
                    Mecz.wynik_gosp_full,
                    Mecz.wynik_gosc_full,
                    Mecz.wycofany,
                    Mecz.id_zespol_walkower,
                    Mecz.zamiana,
                )
                .order_by(termin.asc().nulls_last(), Mecz.id)
            )
            wynik = []
            for (
                id_mecz,
                kiedy,
                id_sezon,
                sezon,
                rok,
                id_rozgrywki,
                rozgrywki,
                id_gosp,
                nazwa_gosp,
                id_gosc,
                nazwa_gosc,
                wynik_gosp,
                wynik_gosc,
                wycofany,
                id_walkower,
                zamiana,
                miejsce_wartosc,
                liczba_stron,
                bramki,
            ) in self._sesja.execute(zapytanie):
                if liczba_stron != 1 or id_gosp is None or id_gosc is None:
                    continue
                u_siebie = miejsce_wartosc == "dom"
                kolumna_gospodarza = u_siebie != bool(zamiana)
                dane_pelne = (
                    wynik_gosp is not None
                    and wynik_gosc is not None
                    and wycofany is not True
                    and id_walkower is None
                    and kiedy is not None
                )
                wynik.append(
                    WystapienieZDanymiLigowymi(
                        id_mecz=id_mecz,
                        termin=kiedy,
                        id_sezon=id_sezon,
                        sezon=sezon,
                        rok_rozpoczecia_sezonu=rok,
                        id_rozgrywki=id_rozgrywki,
                        rozgrywki=rozgrywki,
                        id_zespol_zawodnika=id_gosp if kolumna_gospodarza else id_gosc,
                        druzyna_zawodnika=nazwa_gosp if kolumna_gospodarza else nazwa_gosc,
                        id_zespol_przeciwnika=id_gosc if kolumna_gospodarza else id_gosp,
                        przeciwnik=nazwa_gosc if kolumna_gospodarza else nazwa_gosp,
                        miejsce=miejsce_wartosc,
                        bramki_zawodnika=bramki,
                        wynik_druzyny_zawodnika=wynik_gosp if kolumna_gospodarza else wynik_gosc,
                        wynik_przeciwnika=wynik_gosc if kolumna_gospodarza else wynik_gosp,
                        dane_pelne=dane_pelne,
                    )
                )
            return tuple(wynik)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(
                "Nie udało się odczytać występów zawodnika na tle defensywy rywali."
            ) from wyjatek

    def pobierz_mecze_ligowe(
        self, identyfikatory_rozgrywek: frozenset[int]
    ) -> tuple[MeczLigowy, ...]:
        if not identyfikatory_rozgrywek:
            return ()
        try:
            termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
            zapytanie = select(
                Mecz.id_rozgrywki,
                Mecz.id_zespol_gosp,
                Mecz.id_zespol_gosc,
                Mecz.wynik_gosp_full,
                Mecz.wynik_gosc_full,
                termin,
            ).where(
                Mecz.id_rozgrywki.in_(identyfikatory_rozgrywek),
                Mecz.wynik_gosp_full.is_not(None),
                Mecz.wynik_gosc_full.is_not(None),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
                Mecz.id_zespol_gosp.is_not(None),
                Mecz.id_zespol_gosc.is_not(None),
                termin.is_not(None),
            )
            wynik = []
            for (
                id_rozgrywki,
                id_gosp,
                id_gosc,
                wynik_gosp,
                wynik_gosc,
                kiedy,
            ) in self._sesja.execute(zapytanie):
                wynik.append(MeczLigowy(id_rozgrywki, id_gosp, kiedy, wynik_gosc))
                wynik.append(MeczLigowy(id_rozgrywki, id_gosc, kiedy, wynik_gosp))
            return tuple(wynik)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać meczów ligowych.") from wyjatek

    def pobierz_zespoly_o_nazwie(self, fraza: str) -> frozenset[int]:
        try:
            zapytanie = (
                select(ZespolSezon.id_zespol)
                .where(ZespolSezon.nazwa.icontains(fraza, autoescape=True))
                .distinct()
            )
            return frozenset(self._sesja.scalars(zapytanie))
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać zespołów przeciwnika.") from wyjatek

    def pobierz_poprzednie_rozgrywki(
        self, rozgrywki_do_sprawdzenia: frozenset[tuple[int, str, int]]
    ) -> dict[int, int]:
        if not rozgrywki_do_sprawdzenia:
            return {}
        try:
            wynik: dict[int, int] = {}
            for id_rozgrywki, nazwa, rok in rozgrywki_do_sprawdzenia:
                poprzednie = (
                    self._sesja.execute(
                        select(Rozgrywki.id)
                        .join(Sezon, Sezon.id == Rozgrywki.id_sezon)
                        .where(Rozgrywki.nazwa == nazwa, Sezon.rok_rozpoczecia == rok - 1)
                    )
                    .scalars()
                    .all()
                )
                if len(poprzednie) == 1:
                    wynik[id_rozgrywki] = poprzednie[0]
            return wynik
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać poprzednich rozgrywek.") from wyjatek
