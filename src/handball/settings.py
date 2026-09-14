from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Ustawienia:
    tryb_debugowania: bool
    tajny_klucz: str
    host_bazy: str
    port_bazy: int
    nazwa_bazy: str
    uzytkownik_bazy: str
    haslo_bazy: str

    @classmethod
    def z_srodowiska(cls) -> Ustawienia:
        return cls(
            tryb_debugowania=os.environ.get("FLASK_DEBUG", "0") == "1",
            tajny_klucz=os.environ.get("SECRET_KEY", "dev"),
            host_bazy=os.environ.get("BAZA_HOST", "localhost"),
            port_bazy=int(os.environ.get("BAZA_PORT", "5432")),
            nazwa_bazy=os.environ.get("BAZA_NAZWA", "zprp"),
            uzytkownik_bazy=os.environ.get("BAZA_UZYTKOWNIK", "postgres"),
            haslo_bazy=os.environ.get("BAZA_HASLO", ""),
        )

    def waliduj(self) -> None:
        if not self.tajny_klucz:
            raise ValueError("SECRET_KEY nie moze byc puste")

    @property
    def adres_bazy_danych(self) -> str:
        return (
            f"postgresql+psycopg://{self.uzytkownik_bazy}:{self.haslo_bazy}"
            f"@{self.host_bazy}:{self.port_bazy}/{self.nazwa_bazy}"
        )
