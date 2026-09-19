from __future__ import annotations

import datetime

from sqlalchemy import ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from handball.infrastructure.database.models.base import Baza


class Mecz(Baza):
    __tablename__ = "mecze"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_sezon: Mapped[int] = mapped_column(ForeignKey("public.sezony.id"))
    id_rozgrywki: Mapped[int] = mapped_column(ForeignKey("public.rozgrywki.id"))
    id_kolejka: Mapped[int] = mapped_column(ForeignKey("public.kolejki.id"))
    id_zespol_gosp: Mapped[int | None] = mapped_column(ForeignKey("public.zespoly.id"))
    id_zespol_gosc: Mapped[int | None] = mapped_column(ForeignKey("public.zespoly.id"))
    id_hala: Mapped[int | None] = mapped_column(ForeignKey("public.hale.id"))
    data_faktyczna: Mapped[datetime.datetime | None]
    wynik_gosp_full: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_gosc_full: Mapped[int | None] = mapped_column(SmallInteger)
    wycofany: Mapped[bool | None]
    zamiana: Mapped[bool | None]
