from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from handball.infrastructure.database.models.base import Baza


class Zawodnik(Baza):
    __tablename__ = "zawodnicy"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    imie: Mapped[str | None]
    nazwisko: Mapped[str | None]
    data_urodzenia: Mapped[date | None]
    foto_url: Mapped[str | None]
