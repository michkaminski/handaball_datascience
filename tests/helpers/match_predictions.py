from datetime import datetime

from handball.domain.match_predictions import MeczLigowy, WzorceNazwLig

SEZONY = {
    1: ("2021/2022", 2021),
    2: ("2022/2023", 2022),
    3: ("2023/2024", 2023),
    4: ("2024/2025", 2024),
    5: ("2025/2026", 2025),
}

NAZWY = {10: "Wisła Płock", 20: "Industria Kielce", 30: "Górnik Zabrze", 40: "Zagłębie Lubin"}


def mecz_ligowy(
    id_mecz: int,
    data: datetime | None,
    gosp: int | None,
    gosc: int | None,
    wynik_gosp: int | None,
    wynik_gosc: int | None,
    *,
    id_sezon: int = 5,
    plec: str | None = "M",
    nazwa_rozgrywek: str | None = "ORLEN Superliga",
    zamiana: bool | None = False,
    wycofany: bool | None = False,
    walkower: bool = False,
    kolejka: int | None = 1,
) -> MeczLigowy:
    sezon, rok = SEZONY[id_sezon]
    return MeczLigowy(
        id_mecz=id_mecz,
        plec=plec,
        nazwa_rozgrywek=nazwa_rozgrywek,
        id_sezon=id_sezon,
        sezon=sezon,
        rok_sezonu=rok,
        kolejka=kolejka,
        data=data,
        id_zespol_gosp=gosp,
        id_zespol_gosc=gosc,
        nazwa_gosp=NAZWY.get(gosp or 0),
        nazwa_gosc=NAZWY.get(gosc or 0),
        wynik_gosp=wynik_gosp,
        wynik_gosc=wynik_gosc,
        zamiana=zamiana,
        wycofany=wycofany,
        walkower=walkower,
    )


def mecze_dwoch_sezonow() -> list[MeczLigowy]:
    return [
        mecz_ligowy(101, datetime(2024, 9, 1, 18), 10, 20, 30, 28, id_sezon=4),
        mecz_ligowy(102, datetime(2024, 9, 8, 18), 20, 10, 33, 25, id_sezon=4),
        mecz_ligowy(103, datetime(2024, 9, 15, 18), 30, 40, 27, 27, id_sezon=4),
        mecz_ligowy(201, datetime(2025, 9, 1, 18), 10, 30, 31, 26, id_sezon=5),
        mecz_ligowy(202, datetime(2025, 9, 8, 18), 40, 20, 24, 35, id_sezon=5, zamiana=True),
        mecz_ligowy(203, datetime(2025, 9, 15, 18), 20, 10, 29, 29, id_sezon=5),
    ]


class MeczeLigoweInMemoryRepository:
    def __init__(self, mecze: list[MeczLigowy] | None = None) -> None:
        self._mecze = mecze if mecze is not None else mecze_dwoch_sezonow()
        self.wzorce: WzorceNazwLig | None = None
        self.liczba_odczytow = 0

    def pobierz_mecze(self, wzorce: WzorceNazwLig) -> list[MeczLigowy]:
        self.wzorce = wzorce
        self.liczba_odczytow += 1
        return list(self._mecze)
