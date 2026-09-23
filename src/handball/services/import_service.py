from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from uuid import uuid4

from handball.contracts.import_repository import ImportRepository
from handball.contracts.import_storage import ImportStore, ZprpReadClient
from handball.domain.imports import (
    LIGI_IMPORTU,
    BladImportu,
    OpcjeImportuTabel,
    PrzebiegImportu,
    ZadaniePobrania,
)
from handball.services.import_mapping import ZprpImportMapper

LIMIT_PROB_ZADANIA = 3


class ImportService:
    def __init__(
        self, magazyn: ImportStore, klient: ZprpReadClient, repozytorium: ImportRepository
    ) -> None:
        self.magazyn = magazyn
        self._klient = klient
        self._repozytorium = repozytorium

    def rozpocznij(self, ligi: list[int], tryb: str = "pelny") -> PrzebiegImportu:
        if not ligi or not set(ligi).issubset(LIGI_IMPORTU):
            raise BladImportu("Wybierz przynajmniej jedną z rozgrywek sezonu 2026/2027.")
        if tryb not in ("pelny", "uzupelniajacy"):
            raise BladImportu("Nieprawidłowy tryb importu.")
        przebieg = PrzebiegImportu(
            uuid4().hex, sorted(set(ligi)), datetime.now(UTC).isoformat(), tryb=tryb
        )
        if tryb == "uzupelniajacy":
            przebieg.kolejka = self._repozytorium.pobierz_brakujace(przebieg.ligi)
            if not przebieg.kolejka:
                przebieg.status = "PODGLAD"
        else:
            przebieg.kolejka = [
                ZadaniePobrania("pokaz_sezony.php", {}, "sezony"),
                ZadaniePobrania("pokaz_rozgrywki.php", {"Sezon": 195}, "rozgrywki"),
            ]
        self.magazyn.dodaj(przebieg)
        return przebieg

    def opcje_tabel(self, id_sezon: int | None = None) -> OpcjeImportuTabel:
        sezony = self._repozytorium.pobierz_sezony()
        wybrany = next((s for s in sezony if s.id == id_sezon), sezony[0] if sezony else None)
        rozgrywki = self._repozytorium.pobierz_rozgrywki_sezonu(wybrany.id) if wybrany else []
        return OpcjeImportuTabel(sezony, wybrany, rozgrywki)

    def rozpocznij_tabele(self, id_sezon: int, ligi: list[int]) -> PrzebiegImportu:
        opcje = self.opcje_tabel(id_sezon)
        if opcje.wybrany_sezon is None or opcje.wybrany_sezon.id != id_sezon:
            raise BladImportu("Wybierz sezon z listy.")
        dostepne = {r.id: r.nazwa for r in opcje.rozgrywki}
        if not ligi or not set(ligi).issubset(dostepne):
            raise BladImportu("Wybierz przynajmniej jedne rozgrywki wybranego sezonu.")
        wybrane = sorted(set(ligi))
        przebieg = PrzebiegImportu(
            uuid4().hex,
            wybrane,
            datetime.now(UTC).isoformat(),
            tryb="tabele",
            id_sezon=id_sezon,
            nazwa_sezonu=opcje.wybrany_sezon.nazwa,
            nazwy_lig={str(cid): dostepne[cid] for cid in wybrane},
        )
        przebieg.kolejka = [
            ZadaniePobrania(
                "pokaz_tabele_spis.php", {"Rozgrywki": cid}, "tabele_spis", {"cid": cid}
            )
            for cid in wybrane
        ]
        self.magazyn.dodaj(przebieg)
        return przebieg

    def krok(self, identyfikator: str) -> PrzebiegImportu:
        with self.magazyn.edytuj(identyfikator) as przebieg:
            if przebieg.status not in ("POBIERANIE", "BLAD"):
                return przebieg
            roboczy = deepcopy(przebieg)
            roboczy.blad = None
            roboczy.status = "POBIERANIE"
            try:
                while roboczy.kolejka:
                    zadanie = roboczy.kolejka[0]
                    klucz = sha256(
                        json.dumps([zadanie.endpoint, zadanie.parametry], sort_keys=True).encode()
                    ).hexdigest()
                    if klucz in roboczy.wykonane:
                        roboczy.kolejka.pop(0)
                        continue
                    try:
                        url, tresc = self._klient.pobierz(zadanie)
                        self.magazyn.zapisz_zrodlo(identyfikator, klucz, url, tresc)
                        ZprpImportMapper(roboczy, klucz).przetworz(
                            zadanie, json.loads(tresc.decode("utf-8-sig"))
                        )
                    except BladImportu as blad:
                        proby = roboczy.nieudane_probowania.get(klucz, 0) + 1
                        roboczy.nieudane_probowania[klucz] = proby
                        if proby < LIMIT_PROB_ZADANIA:
                            raise
                        roboczy.kolejka.pop(0)
                        roboczy.nieudane_probowania.pop(klucz, None)
                        roboczy.pominiete.append(
                            {
                                "endpoint": zadanie.endpoint,
                                "parametry": zadanie.parametry,
                                "blad": str(blad),
                            }
                        )
                        continue
                    roboczy.kolejka.pop(0)
                    roboczy.wykonane.append(klucz)
                    roboczy.skroty_zrodel[klucz] = sha256(tresc).hexdigest()
                    roboczy.nieudane_probowania.pop(klucz, None)
                    break
                if not roboczy.kolejka:
                    self._repozytorium.porownaj(roboczy)
                    roboczy.status = "PODGLAD"
                przebieg.__dict__.update(roboczy.__dict__)
            except BladImportu as blad:
                roboczy.status = "BLAD"
                roboczy.blad = str(blad)
                przebieg.__dict__.update(roboczy.__dict__)
            return przebieg

    def zastosuj(self, identyfikator: str) -> PrzebiegImportu:
        with self.magazyn.edytuj(identyfikator) as przebieg:
            if przebieg.status == "ZAPISANO":
                return przebieg
            if przebieg.status != "PODGLAD":
                raise BladImportu("Zapis wymaga ukończonego podglądu zmian.")
            try:
                przebieg.id_przebieg_bazy = self._repozytorium.zastosuj(przebieg)
                przebieg.status = "ZAPISANO"
                przebieg.blad = None
            except BladImportu as blad:
                przebieg.blad = str(blad)
            return przebieg

    def odswiez_podglad(self, identyfikator: str) -> PrzebiegImportu:
        with self.magazyn.edytuj(identyfikator) as przebieg:
            if przebieg.status != "PODGLAD":
                raise BladImportu("Podgląd jest dostępny po zakończeniu pobierania.")
            self._repozytorium.porownaj(przebieg)
            przebieg.blad = None
            return przebieg
