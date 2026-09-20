import pytest

from handball.domain.players import FiltryZawodnikow


@pytest.mark.parametrize(
    "parametry",
    [
        {"strona": 0},
        {"rozmiar_strony": 0},
        {"rozmiar_strony": 101},
        {"rocznik": 0},
        {"rocznik": 10000},
        {"id_sezon": 0},
        {"sortowanie": "--imie"},
        {"sortowanie": "sql"},
    ],
)
def test_filtry_odrzucaja_bledne_wartosci(parametry: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        FiltryZawodnikow(**parametry)


def test_domyslne_filtry_obejmuja_wszystkie_sezony() -> None:
    filtry = FiltryZawodnikow()
    assert filtry.id_sezon is None
    assert filtry.sortowanie == "nazwisko"
