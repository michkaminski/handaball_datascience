import pytest

from handball.domain.match_rules import MeczPolicy, StatusMeczu
from handball.domain.matches import DaneMeczu, ZawodnikMeczu


@pytest.mark.parametrize(
    ("mecz", "status"),
    [
        (DaneMeczu(id=1, wycofany=True, id_zespol_walkower=2), StatusMeczu.WYCOFANY),
        (DaneMeczu(id=1, id_zespol_walkower=2), StatusMeczu.WALKOWER),
        (DaneMeczu(id=1, wynik_gosp_full=0, wynik_gosc_full=0), StatusMeczu.ROZEGRANY),
        (DaneMeczu(id=1, wynik_gosp_full=32), StatusMeczu.ZAPLANOWANY),
    ],
)
def test_status_zachowuje_pierwszenstwo_i_rozroznia_zero_od_braku(
    mecz: DaneMeczu, status: StatusMeczu
) -> None:
    assert MeczPolicy().status(mecz) == status


def test_maksimum_nie_zamienia_braku_danych_w_zero() -> None:
    reguly = MeczPolicy()
    assert reguly.najwiecej_bramek([]) is None
    assert reguly.najwiecej_bramek([ZawodnikMeczu()]) is None
    assert reguly.najwiecej_bramek([ZawodnikMeczu(bramki=0)]) == 0
    assert reguly.najwiecej_bramek([ZawodnikMeczu(bramki=7), ZawodnikMeczu()]) == 7
