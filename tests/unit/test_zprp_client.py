from unittest.mock import Mock, patch

from handball.domain.imports import ZadaniePobrania
from handball.infrastructure.zprp_client import ZprpClient


def test_kolejne_zadania_maja_odstep_trzech_sekund() -> None:
    klient = ZprpClient()
    klient._pobierz = Mock(return_value=("url", b"{}"))
    zadanie = ZadaniePobrania("test.php", {}, "test")
    with (
        patch("handball.infrastructure.zprp_client.monotonic", side_effect=[0, 1, 3, 8, 8]),
        patch("handball.infrastructure.zprp_client.sleep") as czekaj,
    ):
        klient.pobierz(zadanie)
        klient.pobierz(zadanie)
        klient.pobierz(zadanie)
    assert [wywolanie.args[0] for wywolanie in czekaj.call_args_list] == [2.0, 0.0]
    assert klient._pobierz.call_count == 3
