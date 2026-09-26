from collections.abc import Sequence
from datetime import date, datetime

from handball.domain.errors import NieZnalezionoMeczu
from handball.domain.match_preview import (
    DruzynaZapowiedzi,
    MeczZapowiedzi,
    SezonKadry,
    WystepSezonuZawodnika,
    WystepZapowiedzi,
    ZawodnikKadry,
)
from handball.domain.matches import DaneMeczu
from handball.domain.options import OpcjaWyboru
from handball.domain.schedule import FiltryTerminarza, PozycjaTerminarza

ROZGRYWKI = {5: [OpcjaWyboru(501, "ORLEN Superliga"), OpcjaWyboru(502, "II Liga Mężczyzn")]}
RUNDY = {501: [OpcjaWyboru(11, "I runda"), OpcjaWyboru(12, "II runda")]}
KOLEJKI = {
    11: [OpcjaWyboru(111, "Seria 1"), OpcjaWyboru(112, "Seria 2")],
    12: [OpcjaWyboru(121, "Seria 3")],
}


def pozycja(
    id_mecz: int,
    termin: datetime | None,
    gospodarz: str,
    gosc: str,
    wynik: tuple[int, int] | None,
    *,
    id_runda: int = 11,
    id_kolejka: int = 111,
    zamiana: bool = False,
    godzina_znana: bool = True,
) -> PozycjaTerminarza:
    runda = {11: "I runda", 12: "II runda"}[id_runda]
    kolejka = {111: ("Seria 1", 1), 112: ("Seria 2", 2), 121: ("Seria 3", 3)}[id_kolejka]
    return PozycjaTerminarza(
        id_mecz=id_mecz,
        mecz=DaneMeczu(
            id=id_mecz,
            wynik_gosp_full=wynik[0] if wynik else None,
            wynik_gosc_full=wynik[1] if wynik else None,
            data_faktyczna=termin if godzina_znana else None,
            data_propozycji=termin,
            zamiana=zamiana,
        ),
        gospodarz=gospodarz,
        gosc=gosc,
        hala="Orlen Arena",
        id_runda=id_runda,
        runda=runda,
        id_kolejka=id_kolejka,
        kolejka=kolejka[0],
        nr_kolejki=kolejka[1],
    )


def pozycje_terminarza() -> list[PozycjaTerminarza]:
    return [
        pozycja(201, datetime(2025, 9, 1, 18), "Wisła Płock", "Górnik Zabrze", (31, 26)),
        pozycja(
            202,
            datetime(2025, 9, 1, 20, 15),
            "Industria Kielce",
            "Zagłębie Lubin",
            (35, 24),
            zamiana=True,
        ),
        pozycja(203, datetime(2025, 9, 2, 18), "Industria Kielce", "Wisła Płock", (29, 29)),
        pozycja(
            204, datetime(2025, 9, 8, 18), "Górnik Zabrze", "Wisła Płock", None, id_kolejka=112
        ),
        pozycja(
            301,
            datetime(2026, 2, 7),
            "Zagłębie Lubin",
            "Industria Kielce",
            None,
            id_runda=12,
            id_kolejka=121,
            godzina_znana=False,
        ),
    ]


class TerminarzInMemoryRepository:
    def __init__(self, pozycje: list[PozycjaTerminarza] | None = None) -> None:
        self._pozycje = pozycje if pozycje is not None else pozycje_terminarza()
        self.filtry: list[FiltryTerminarza] = []

    def pobierz_rozgrywki(self, id_sezon: int) -> list[OpcjaWyboru]:
        return list(ROZGRYWKI.get(id_sezon, []))

    def pobierz_rundy(self, id_rozgrywki: int) -> list[OpcjaWyboru]:
        return list(RUNDY.get(id_rozgrywki, []))

    def pobierz_kolejki(self, id_rozgrywki: int, id_runda: int | None) -> list[OpcjaWyboru]:
        if id_rozgrywki not in RUNDY:
            return []
        if id_runda is not None:
            return list(KOLEJKI.get(id_runda, []))
        return [k for runda in RUNDY[id_rozgrywki] for k in KOLEJKI.get(runda.wartosc, [])]

    def pobierz_mecze(self, filtry: FiltryTerminarza) -> list[PozycjaTerminarza]:
        self.filtry.append(filtry)
        if filtry.id_rozgrywki != 501:
            return []
        return [
            p
            for p in self._pozycje
            if (filtry.id_runda is None or p.id_runda == filtry.id_runda)
            and (filtry.id_kolejka is None or p.id_kolejka == filtry.id_kolejka)
        ]


def mecz_zapowiedzi(
    id_mecz: int = 204,
    *,
    wynik: tuple[int, int] | None = None,
    data: datetime | None = datetime(2025, 9, 22, 18),
    zamiana: bool = False,
    gosp: tuple[int, str] = (30, "Górnik Zabrze"),
    gosc: tuple[int, str] = (10, "Wisła Płock"),
) -> MeczZapowiedzi:
    return MeczZapowiedzi(
        id_mecz=id_mecz,
        id_sezon=5,
        sezon="2025/2026",
        id_rozgrywki=501,
        rozgrywki="ORLEN Superliga",
        runda="I runda",
        kolejka="Seria 2",
        nr_kolejki=2,
        data_faktyczna=data,
        data_propozycji=data,
        kolumna_gosp=DruzynaZapowiedzi(*gosp),
        kolumna_gosc=DruzynaZapowiedzi(*gosc),
        wynik_gosp=wynik[0] if wynik else None,
        wynik_gosc=wynik[1] if wynik else None,
        hala="Hala Pogoń",
        miasto="Zabrze",
        zamiana=zamiana,
        wycofany=False,
        walkower=False,
    )


def wystep(
    id_mecz: int,
    data: datetime,
    id_zespol: int,
    id_rywal: int,
    rywal: str,
    zdobyte: int,
    stracone: int,
    *,
    u_siebie: bool = True,
    id_rozgrywki: int = 501,
) -> WystepZapowiedzi:
    return WystepZapowiedzi(
        id_mecz=id_mecz,
        data=data,
        id_sezon=5,
        id_rozgrywki=id_rozgrywki,
        rozgrywki="ORLEN Superliga" if id_rozgrywki == 501 else "Puchar Polski",
        id_zespol=id_zespol,
        id_rywal=id_rywal,
        rywal=rywal,
        u_siebie=u_siebie,
        bramki_zdobyte=zdobyte,
        bramki_stracone=stracone,
    )


WYSTEPY: dict[int, list[WystepZapowiedzi]] = {
    30: [
        wystep(201, datetime(2025, 9, 1, 18), 30, 10, "Wisła Płock", 26, 31, u_siebie=False),
        wystep(103, datetime(2024, 9, 15, 18), 30, 40, "Zagłębie Lubin", 27, 27),
        wystep(
            90,
            datetime(2025, 8, 20, 18),
            30,
            20,
            "Industria Kielce",
            30,
            28,
            id_rozgrywki=900,
        ),
    ],
    10: [
        wystep(201, datetime(2025, 9, 1, 18), 10, 30, "Górnik Zabrze", 31, 26),
        wystep(203, datetime(2025, 9, 15, 18), 10, 20, "Industria Kielce", 29, 29, u_siebie=False),
        wystep(
            88,
            datetime(2024, 3, 1, 18),
            10,
            30,
            "Górnik Zabrze",
            22,
            25,
            u_siebie=False,
            id_rozgrywki=900,
        ),
    ],
}


KADRY: dict[tuple[int, int], list[ZawodnikKadry]] = {
    (10, 5): [
        ZawodnikKadry(
            7, "Jan", "Kowalski", (7,), "Rozgrywający", 2, 13, data_urodzenia=date(1998, 1, 2)
        ),
        ZawodnikKadry(1, "Adam", "Nowak", (1, 12), "Bramkarz", 2, 0),
        ZawodnikKadry(9, "Piotr", "Lis", (9,), "Skrzydłowy", 1, 4),
        ZawodnikKadry(5, "Ewa", "Bez", (), None, 1, 0),
    ],
    (10, 4): [
        ZawodnikKadry(7, "Jan", "Kowalski", (17,), "Rozgrywający", 3, 20),
        ZawodnikKadry(3, "Olaf", "Stary", (3,), "Obrotowy", 4, 6),
        ZawodnikKadry(4, "Karol", "Rezerwa", (44,), "Bramkarz", 2, 0, zagrane=0),
    ],
}


WYSTEPY_ZAWODNIKOW: dict[int, list[WystepSezonuZawodnika]] = {
    4: [
        WystepSezonuZawodnika(7, 10, "Wisła Płock", "ORLEN Superliga", 3, 20),
        WystepSezonuZawodnika(1, 20, "Industria Kielce", "ORLEN Superliga", 4, 1),
        WystepSezonuZawodnika(9, 88, "KPR Legionowo", "I Liga Mężczyzn Grupa A", 5, 30),
        WystepSezonuZawodnika(9, 88, "KPR Legionowo", "Puchar Polski", 1, 6),
        WystepSezonuZawodnika(3, 10, "Wisła Płock", "ORLEN Superliga", 4, 6),
        WystepSezonuZawodnika(3, 30, "Górnik Zabrze", "ORLEN Superliga", 2, 5),
    ]
}


class ZapowiedzMeczuInMemoryRepository:
    def __init__(self, mecze: list[MeczZapowiedzi] | None = None) -> None:
        self._mecze = {m.id_mecz: m for m in (mecze or [mecz_zapowiedzi()])}
        self.odczyty: list[tuple[int, datetime]] = []
        self.kadry: list[tuple[int, int, datetime]] = []
        self.wystepy_zawodnikow: list[tuple[tuple[int, ...], int]] = []

    def pobierz_mecz(self, id_mecz: int) -> MeczZapowiedzi:
        try:
            return self._mecze[id_mecz]
        except KeyError as wyjatek:
            raise NieZnalezionoMeczu(f"Nie znaleziono meczu o id {id_mecz}") from wyjatek

    def pobierz_wystepy(self, id_zespol: int, przed: datetime) -> list[WystepZapowiedzi]:
        self.odczyty.append((id_zespol, przed))
        return [w for w in WYSTEPY.get(id_zespol, []) if w.data < przed]

    def pobierz_kadre(self, id_zespol: int, id_sezon: int, przed: datetime) -> list[ZawodnikKadry]:
        self.kadry.append((id_zespol, id_sezon, przed))
        return list(KADRY.get((id_zespol, id_sezon), []))

    def pobierz_wystepy_zawodnikow(
        self, id_zawodnikow: Sequence[int], id_sezon: int, przed: datetime
    ) -> list[WystepSezonuZawodnika]:
        self.wystepy_zawodnikow.append((tuple(id_zawodnikow), id_sezon))
        return [w for w in WYSTEPY_ZAWODNIKOW.get(id_sezon, []) if w.id_zawodnik in id_zawodnikow]

    def pobierz_poprzedni_sezon(self, id_sezon: int) -> SezonKadry | None:
        return SezonKadry(4, "2024/2025") if id_sezon == 5 else None


class SezonyTerminarza:
    def pobierz_wszystkie(self) -> list[OpcjaWyboru]:
        return [OpcjaWyboru(5, "2025/2026"), OpcjaWyboru(4, "2024/2025")]


class ZegarTestowy:
    def teraz(self) -> datetime:
        return datetime(2025, 9, 20, 12)
