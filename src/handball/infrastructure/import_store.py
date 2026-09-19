from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

from handball.domain.imports import (
    BladImportu,
    PrzebiegImportu,
    RekordImportu,
    ZadaniePobrania,
)


class ImportFileStore:
    def __init__(self, katalog: Path) -> None:
        self.katalog = katalog

    @contextmanager
    def polaczenie(self) -> Iterator[sqlite3.Connection]:
        self.katalog.mkdir(parents=True, exist_ok=True)
        polaczenie = sqlite3.connect(self.katalog / "imports.sqlite3", timeout=2)
        try:
            polaczenie.execute(
                "CREATE TABLE IF NOT EXISTS przebiegi (id TEXT PRIMARY KEY, dokument TEXT NOT NULL)"
            )
            polaczenie.commit()
            yield polaczenie
        except sqlite3.OperationalError as blad:
            raise BladImportu("Inna operacja importu trwa. Spróbuj ponownie.") from blad
        finally:
            polaczenie.close()

    @contextmanager
    def edytuj(self, identyfikator: str) -> Iterator[PrzebiegImportu]:
        with self.polaczenie() as polaczenie:
            polaczenie.execute("BEGIN IMMEDIATE")
            przebieg = self._odczytaj(polaczenie, identyfikator)
            yield przebieg
            polaczenie.execute(
                "UPDATE przebiegi SET dokument=? WHERE id=?",
                (json.dumps(asdict(przebieg), ensure_ascii=False), identyfikator),
            )
            polaczenie.commit()

    def dodaj(self, przebieg: PrzebiegImportu) -> None:
        with self.polaczenie() as polaczenie:
            polaczenie.execute(
                "INSERT INTO przebiegi VALUES (?,?)",
                (przebieg.id, json.dumps(asdict(przebieg), ensure_ascii=False)),
            )
            polaczenie.commit()

    def pobierz(self, identyfikator: str) -> PrzebiegImportu:
        with self.polaczenie() as polaczenie:
            return self._odczytaj(polaczenie, identyfikator)

    def historia(self) -> list[PrzebiegImportu]:
        with self.polaczenie() as polaczenie:
            return [
                self._z_dokumentu(wiersz[0])
                for wiersz in polaczenie.execute(
                    "SELECT dokument FROM przebiegi ORDER BY rowid DESC LIMIT 30"
                )
            ]

    def _odczytaj(self, polaczenie: sqlite3.Connection, identyfikator: str) -> PrzebiegImportu:
        wiersz = polaczenie.execute(
            "SELECT dokument FROM przebiegi WHERE id=?", (identyfikator,)
        ).fetchone()
        if wiersz is None:
            raise BladImportu("Nie znaleziono przebiegu importu.")
        return self._z_dokumentu(wiersz[0])

    def _z_dokumentu(self, tekst: str) -> PrzebiegImportu:
        dane = json.loads(tekst)
        dane["kolejka"] = [ZadaniePobrania(**r) for r in dane["kolejka"]]
        dane["rekordy"] = [RekordImportu(**r) for r in dane["rekordy"]]
        return PrzebiegImportu(**dane)

    def zapisz_zrodlo(self, przebieg: str, identyfikator: str, url: str, tresc: bytes) -> None:
        katalog = self.katalog / przebieg
        katalog.mkdir(parents=True, exist_ok=True)
        tymczasowy = katalog / f"{identyfikator}.tmp"
        tymczasowy.write_bytes(tresc)
        tymczasowy.replace(katalog / f"{identyfikator}.json")
        (katalog / f"{identyfikator}.url").write_text(url, encoding="utf-8")

    def zrodlo(self, przebieg: str, identyfikator: str) -> tuple[str, bytes]:
        katalog = self.katalog / przebieg
        return (
            (katalog / f"{identyfikator}.url").read_text(encoding="utf-8"),
            (katalog / f"{identyfikator}.json").read_bytes(),
        )
