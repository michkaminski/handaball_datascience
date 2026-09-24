from typing import Any

from sqlalchemy import and_, case, or_

from handball.infrastructure.database.models.matches import Mecz


class StronyMeczuSql:
    @staticmethod
    def kolumna_gospodarza(strona: Any) -> Any:
        return or_(
            and_(strona == "gosp", Mecz.zamiana.is_not(True)),
            and_(strona == "gosc", Mecz.zamiana.is_(True)),
        )

    @staticmethod
    def kolumna_goscia(strona: Any) -> Any:
        return or_(
            and_(strona == "gosc", Mecz.zamiana.is_not(True)),
            and_(strona == "gosp", Mecz.zamiana.is_(True)),
        )

    @classmethod
    def wedlug_kolumny(cls, strona: Any, wartosc_gospodarza: Any, wartosc_goscia: Any) -> Any:
        return case(
            (cls.kolumna_gospodarza(strona), wartosc_gospodarza),
            (cls.kolumna_goscia(strona), wartosc_goscia),
        )

    @classmethod
    def zespol(cls, strona: Any) -> Any:
        return cls.wedlug_kolumny(strona, Mecz.id_zespol_gosp, Mecz.id_zespol_gosc)

    @classmethod
    def rywal(cls, strona: Any) -> Any:
        return cls.wedlug_kolumny(strona, Mecz.id_zespol_gosc, Mecz.id_zespol_gosp)
