from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from handball.domain.attendance_appeal import MODELE_MAF
from handball.infrastructure.maf_store import (
    katalog_modeli,
    wczytaj_kontynuacje,
    wczytaj_korekty_pojemnosci,
)
from handball.infrastructure.repositories.attendance_appeal_repository import (
    MeczeMafSQLAlchemyRepository,
)
from handball.settings import Ustawienia
from maf.artifacts import ArtifactStore
from maf.nuts import SamplerSettings
from maf.training import MafTrainer


class TreningMafCommand:
    def __init__(self, ustawienia: Ustawienia, katalog: Path) -> None:
        self._ustawienia = ustawienia
        self._katalog = katalog

    def wykonaj(
        self, klucze: list[str], ustawienia_samplera: SamplerSettings, backtest: bool
    ) -> int:
        silnik = create_engine(
            self._ustawienia.adres_bazy_danych,
            execution_options={"postgresql_readonly": True},
        )
        trener = MafTrainer(
            ArtifactStore(self._katalog),
            ustawienia_samplera,
            overrides=wczytaj_korekty_pojemnosci(),
            lineage=wczytaj_kontynuacje(),
            progress=self._log,
        )
        wybrane = [model for model in MODELE_MAF if not klucze or model.spec.key in klucze]
        if not wybrane:
            self._log(f"Nieznane modele: {klucze}")
            return 2
        for model in wybrane:
            with Session(silnik) as sesja:
                repozytorium = MeczeMafSQLAlchemyRepository(sesja)
                mecze = repozytorium.pobierz_mecze(model.plec)
                nazwy = repozytorium.pobierz_nazwy_klubow()
                sesja.rollback()
            wynik = trener.train(mecze, model.spec, nazwy, backtest=backtest)
            self._log(f"{model.spec.key}: wersja {wynik.version}, status {wynik.status}")
        return 0

    def _log(self, komunikat: str) -> None:
        print(komunikat, flush=True)


def main(argumenty: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Trening Modelu Atrakcyjności Frekwencyjnej (MAF)")
    parser.add_argument(
        "modele", nargs="*", help="klucze modeli, np. M-wypelnienie; puste = wszystkie"
    )
    parser.add_argument("--lancuchy", type=int, default=4)
    parser.add_argument("--rozgrzewka", type=int, default=1000)
    parser.add_argument("--probki", type=int, default=1500)
    parser.add_argument("--ziarno", type=int, default=20261010)
    parser.add_argument("--bez-backtestu", action="store_true")
    opcje = parser.parse_args(argumenty)
    ustawienia = SamplerSettings(
        chains=opcje.lancuchy,
        warmup=opcje.rozgrzewka,
        draws=opcje.probki,
        seed=opcje.ziarno,
    )
    polecenie = TreningMafCommand(Ustawienia.z_srodowiska(), katalog_modeli())
    return polecenie.wykonaj(opcje.modele, ustawienia, not opcje.bez_backtestu)


if __name__ == "__main__":
    sys.exit(main())
