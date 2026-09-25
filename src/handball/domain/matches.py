from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from handball.domain.options import OpcjaWyboru

SORTOWANIA_DOZWOLONE = frozenset({"data", "-data"})
JEDEN_DZIEN = timedelta(days=1)

WZORZEC_CZESCIOWEJ_DATY = re.compile(r"^(?P<rok>\d{4})(-(?P<miesiac>\d{2})(-(?P<dzien>\d{2}))?)?$")


def zakres_z_czesciowej_daty(tekst: str) -> tuple[datetime, datetime]:
    dopasowanie = WZORZEC_CZESCIOWEJ_DATY.match(tekst.strip())
    if not dopasowanie:
        raise ValueError(f"niepoprawny format daty: {tekst!r}")

    rok = int(dopasowanie.group("rok"))
    miesiac = dopasowanie.group("miesiac")
    dzien = dopasowanie.group("dzien")

    if dzien is not None:
        start = datetime(rok, int(miesiac), int(dzien))
        koniec = start + JEDEN_DZIEN
        return start, koniec

    if miesiac is not None:
        miesiac_int = int(miesiac)
        start = datetime(rok, miesiac_int, 1)
        if miesiac_int == 12:
            koniec = datetime(rok + 1, 1, 1)
        else:
            koniec = datetime(rok, miesiac_int + 1, 1)
        return start, koniec

    return datetime(rok, 1, 1), datetime(rok + 1, 1, 1)


@dataclass(frozen=True)
class FiltryMeczow:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    id_hala: int | None = None
    szukaj_druzyny: str | None = None
    data_od: datetime | None = None
    data_do: datetime | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "data"
    runda: str | None = None
    kolejka: str | None = None
    tylko_rozegrane: bool = False
    tylko_zakonczone: bool = False

    def __post_init__(self) -> None:
        if self.strona < 1:
            raise ValueError("strona musi byc >= 1")
        if not 1 <= self.rozmiar_strony <= 100:
            raise ValueError("rozmiar_strony musi byc w zakresie 1-100")
        if self.sortowanie not in SORTOWANIA_DOZWOLONE:
            raise ValueError(f"niedozwolone sortowanie: {self.sortowanie}")


@dataclass(frozen=True)
class PozycjaListyMeczow:
    id_mecz: int
    termin: datetime | None
    sezon: str | None
    rozgrywki: str | None
    gospodarz: str | None
    gosc: str | None
    mecz: DaneMeczu
    hala: str | None
    runda: str | None = None
    kolejka: str | None = None


@dataclass(frozen=True)
class StronaMeczow:
    pozycje: list[PozycjaListyMeczow]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class OpcjeFiltrowMeczow:
    sezony: list[OpcjaWyboru] = field(default_factory=list)
    rozgrywki: list[str] = field(default_factory=list)
    hale: list[OpcjaWyboru] = field(default_factory=list)
    rundy: list[str] = field(default_factory=list)
    kolejki: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DaneMeczu:
    id: int
    lp: int | None = None
    alias_gosp: int | None = None
    alias_gosc: int | None = None
    wynik_gosp_pol: int | None = None
    wynik_gosp_full: int | None = None
    wynik_gosc_pol: int | None = None
    wynik_gosc_full: int | None = None
    wynik_temp_gosp_pol: int | None = None
    wynik_temp_gosp_full: int | None = None
    wynik_temp_gosc_pol: int | None = None
    wynik_temp_gosc_full: int | None = None
    wynik_koncowy_gosp: int | None = None
    wynik_koncowy_gosc: int | None = None
    wynik_bramki_gosp: int | None = None
    wynik_bramki_gosc: int | None = None
    dogrywka_1_pol_gosp: int | None = None
    dogrywka_1_pol_gosc: int | None = None
    dogrywka_1_full_gosp: int | None = None
    dogrywka_1_full_gosc: int | None = None
    dogrywka_2_pol_gosp: int | None = None
    dogrywka_2_pol_gosc: int | None = None
    dogrywka_2_full_gosp: int | None = None
    dogrywka_2_full_gosc: int | None = None
    dogrywka_karne_gosp: int | None = None
    dogrywka_karne_gosc: int | None = None
    karne_bramki_gosp: int | None = None
    karne_bramki_gosc: int | None = None
    karne_ile_gosp: int | None = None
    karne_ile_gosc: int | None = None
    kary_gosp: int | None = None
    kary_gosc: int | None = None
    czy_remis: bool | None = None
    zwyciezca: int | None = None
    timeout1_gosp: str | None = None
    timeout2_gosp: str | None = None
    timeout3_gosp: str | None = None
    timeout1_gosc: str | None = None
    timeout2_gosc: str | None = None
    timeout3_gosc: str | None = None
    data_propozycji: datetime | None = None
    data_faktyczna: datetime | None = None
    data_ostatniej_zmiany: datetime | None = None
    zamiana: bool | None = None
    wycofany: bool | None = None
    wycofany_typ: str | None = None
    id_zespol_walkower: int | None = None
    protokol: str | None = None
    protokol_zatwierdzony: bool | None = None
    protokol_zalacznik_typ: str | None = None
    protokol_zalacznik_nazwa: str | None = None
    komentarz: str | None = None
    widzowie: int | None = None
    transmisja: str | None = None
    transmisja_godzina: str | None = None
    bilety_url: str | None = None
    po_para_id: int | None = None
    po_para_id_gosp: int | None = None
    po_para_id_gosc: int | None = None
    rozgrywki_code: str | None = None
    id_zespol_gosp: int | None = None
    id_zespol_gosc: int | None = None


@dataclass(frozen=True)
class ZawodnikMeczu:
    nr_koszulki: int | None = None
    zawodnik: str | None = None
    pozycja: str | None = None
    bramki: int | None = None
    dwie_minuty: int | None = None
    upomnienie: bool | None = None
    dyskwalifikacja: bool | None = None
    kd: int | None = None
    wyjscie: bool | None = None
    karne_bramki: int | None = None
    karne_liczba: int | None = None
    karne_bramki_seria: int | None = None
    karne_liczba_seria: int | None = None
    id_zawodnik: int | None = None


@dataclass(frozen=True)
class SzczegolyMeczu:
    mecz: DaneMeczu
    nazwa_sezon: str | None = None
    nazwa_rozgrywki: str | None = None
    nazwa_gospodarz: str | None = None
    nazwa_gosc: str | None = None
    nazwa_hala: str | None = None
    miasto_hala: str | None = None
    nazwa_runda: str | None = None
    nazwa_kolejka: str | None = None
    nr_kolejka: int | None = None
    nazwa_zespol_wycofany: str | None = None
    nazwa_zespol_walkower: str | None = None
    sklad_gospodarz: list[ZawodnikMeczu] = field(default_factory=list)
    sklad_gosc: list[ZawodnikMeczu] = field(default_factory=list)
    sklad_inne: list[ZawodnikMeczu] = field(default_factory=list)
