from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from handball.infrastructure.database.models.base import Baza


class Hala(Baza):
    __tablename__ = "hale"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    nazwa: Mapped[str | None]
    miasto: Mapped[str | None]
