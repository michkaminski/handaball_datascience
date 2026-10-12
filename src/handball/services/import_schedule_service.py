from __future__ import annotations

from handball.contracts.import_schedule_repository import PobieranieMeczowReadRepository
from handball.domain.competition_levels import DopasowanieGrupRozgrywek, GrupaRozgrywek
from handball.domain.match_rules import MeczPolicy, StatusMeczu
from handball.domain.schedule import (
    FiltryPobierania,
    FiltryTerminarza,
    KryteriaPobierania,
    PozycjaTerminarza,
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
        grupy: DopasowanieGrupRozgrywek | None = None,
    ) -> None:
        self._terminarz = terminarz
        self._mecze = mecze
        self._reguly = MeczPolicy()
        self._zakres = zakres or ZakresPobierania(self._reguly)
        self._grupy = grupy or DopasowanieGrupRozgrywek()

    def pobierz(self, kryteria: KryteriaPobierania) -> Terminarz | None:
        wybor = kryteria.wybor
        id_sezon = wybor.id_sezon
        if id_sezon is None or not self._ma_zakres(kryteria):
            return None
        wiersze = self._po_grupach(
            self._mecze.pobierz(
                FiltryPobierania(id_sezon, wybor.id_rozgrywki, wybor.id_runda, wybor.id_kolejka)
            ),
            kryteria.grupy,
        )
        if not kryteria.kolejki_zakonczone:
            return self._uloz(
                id_sezon,
                wybor,
                [pozycja for pozycja, brak in wiersze if self._zostaw(pozycja, brak, kryteria)],
            )
        terminarz = self._zakres.zakonczone_kolejki(
            self._uloz(id_sezon, wybor, [pozycja for pozycja, _brak in wiersze])
        )
        if not kryteria.bez_wynikow and not kryteria.wynik_bez_danych:
            return terminarz
        identyfikatory = {
            pozycja.id_mecz for pozycja, brak in wiersze if self._zostaw(pozycja, brak, kryteria)
        }
        return self._zakres.tylko_mecze(terminarz, identyfikatory)

    def _ma_zakres(self, kryteria: KryteriaPobierania) -> bool:
        wybor = kryteria.wybor
        return (
            wybor.id_rozgrywki is not None
            or kryteria.wynik_bez_danych
            or kryteria.kolejki_zakonczone
            or kryteria.bez_wynikow
            or bool(kryteria.grupy)
        )

    def _po_grupach(
        self,
        wiersze: list[tuple[PozycjaTerminarza, bool]],
        grupy: frozenset[GrupaRozgrywek],
    ) -> list[tuple[PozycjaTerminarza, bool]]:
        if not grupy:
            return wiersze
        return [
            (pozycja, brak)
            for pozycja, brak in wiersze
            if self._grupy.pasuje(pozycja.nazwa_rozgrywek, grupy)
        ]

    def _zostaw(self, pozycja: PozycjaTerminarza, brak: bool, kryteria: KryteriaPobierania) -> bool:
        if (
            kryteria.bez_wynikow
            and self._reguly.status(pozycja.mecz) is not StatusMeczu.ZAPLANOWANY
        ):
            return False
        return not kryteria.wynik_bez_danych or brak

    def _uloz(
        self, id_sezon: int, wybor: WyborTerminarza, pozycje: list[PozycjaTerminarza]
    ) -> Terminarz:
        return self._terminarz.uloz(
            FiltryTerminarza(id_sezon, wybor.id_rozgrywki or 0, wybor.id_runda, wybor.id_kolejka),
            pozycje,
        )
