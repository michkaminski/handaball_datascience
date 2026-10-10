from __future__ import annotations

import json
import os
from pathlib import Path

from maf.records import CapacityOverride, ClubLineage

KATALOG_DOMYSLNY = Path(__file__).resolve().parents[3] / "var" / "maf"
KATALOG_KONFIGURACJI = Path(__file__).resolve().parents[3] / "config" / "maf"


def katalog_modeli() -> Path:
    return Path(os.environ.get("MAF_KATALOG", str(KATALOG_DOMYSLNY)))


def wczytaj_kontynuacje(katalog: Path = KATALOG_KONFIGURACJI) -> tuple[ClubLineage, ...]:
    plik = katalog / "kontynuacje_klubow.json"
    if not plik.exists():
        return ()
    dane = json.loads(plik.read_text(encoding="utf-8"))
    return tuple(
        ClubLineage(int(wpis["poprzedni"]), int(wpis["obecny"]), str(wpis.get("uwagi", "")))
        for wpis in dane.get("kontynuacje", [])
    )


def wczytaj_korekty_pojemnosci(
    katalog: Path = KATALOG_KONFIGURACJI,
) -> tuple[CapacityOverride, ...]:
    plik = katalog / "korekty_pojemnosci.json"
    if not plik.exists():
        return ()
    dane = json.loads(plik.read_text(encoding="utf-8"))
    return tuple(
        CapacityOverride(
            venue_id=wpis.get("id_hali"),
            season_key=wpis.get("sezon"),
            match_id=wpis.get("id_meczu"),
            capacity=int(wpis["pojemnosc"]),
            note=str(wpis.get("uwagi", "")),
        )
        for wpis in dane.get("korekty", [])
    )
