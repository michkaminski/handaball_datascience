from __future__ import annotations

from handball.contracts.import_schedule_repository import PobieranieMeczowReadRepository
from handball.domain.match_rules import MeczPolicy
from handball.domain.schedule import (
    FiltryPobierania,
    FiltryTerminarza,
    Terminarz,
    WyborTerminarza,
    ZakresPobierania,
)
from handball.services.schedule_service import TerminarzService


class PobieranieMeczowService:
    def __init__(
        self,
        terminarz: TerminarzService,
        mecze: PobieranieMeczowReadRepository,
        zakres: ZakresPobierania | None = None,
    ) -> None:
        self._terminarz = terminarz
        self._mecze = mecze
        self._zakres = zakres or ZakresPobierania(MeczPolicy())

    def pobierz(
        self,
        wybor: WyborTerminarza,
        wynik_bez_danych: bool,
        kolejki_zakonczone: bool,
    ) -> Terminarz | None:
        if wybor.id_sezon is None:
            return None
        if wybor.id_rozgrywki is None and not wynik_bez_danych and not kolejki_zakonczone:
            return None
        wiersze = self._mecze.pobierz(
            FiltryPobierania(wybor.id_sezon, wybor.id_rozgrywki, wybor.id_runda, wybor.id_kolejka)
        )
        wybrane = [pozycja for pozycja, _brak in wiersze]
        if wynik_bez_danych and not kolejki_zakonczone:
            wybrane = [pozycja for pozycja, brak in wiersze if brak]
        terminarz = self._terminarz.uloz(
            FiltryTerminarza(
                wybor.id_sezon, wybor.id_rozgrywki or 0, wybor.id_runda, wybor.id_kolejka
            ),
            wybrane,
        )
        if not kolejki_zakonczone:
            return terminarz
        zakonczone = self._zakres.zakonczone_kolejki(terminarz)
        if not wynik_bez_danych:
            return zakonczone
        brakujace = {pozycja.id_mecz for pozycja, brak in wiersze if brak}
        return self._zakres.tylko_mecze(zakonczone, brakujace)
