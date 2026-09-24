from typing import Any

from sqlalchemy import Date, and_, cast, func, or_

from handball.infrastructure.database.models.matches import Mecz


class WarunkiMeczuSql:
    @staticmethod
    def zakonczony() -> Any:
        dzisiaj = cast(func.timezone("Europe/Warsaw", func.now()), Date)
        termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
        return or_(
            termin < dzisiaj,
            and_(Mecz.wynik_gosp_full.is_not(None), Mecz.wynik_gosc_full.is_not(None)),
        )
