from datetime import date

from handball.domain.match_preview import CzlonekKadry
from handball.interface.presenters.match_protocol_live_presenter import (
    NazwaPlikuProtokoluPolicy,
    NumeryProtokoluLivePolicy,
)


def czlonek(id_zawodnik: int, numery: tuple[int, ...]) -> CzlonekKadry:
    return CzlonekKadry(id_zawodnik, "Jan", f"GRACZ{id_zawodnik}", numery, None, None)


def test_nazwa_pliku_to_data_i_druzyny_bez_polskich_znakow() -> None:
    nazwa = NazwaPlikuProtokoluPolicy().nazwa(
        date(2024, 10, 10), "Orlen Wisła Płock", "Łomża Industria Kielce"
    )
    assert nazwa == "2024-10-10_Orlen-Wisla-Plock_Lomza-Industria-Kielce"
    assert NazwaPlikuProtokoluPolicy().czesc("  ") == "druzyna"


def test_brakujace_i_powtorzone_numery_dostaja_wolne_od_100() -> None:
    czlonkowie = [
        czlonek(1, (7,)),
        czlonek(2, ()),
        czlonek(3, (7, 12)),
        czlonek(4, (100,)),
        czlonek(5, (12, 3)),
    ]
    assert NumeryProtokoluLivePolicy().numery(czlonkowie) == [7, 101, 102, 100, 3]
