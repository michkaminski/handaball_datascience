from handball.contracts.competition_repository import RozgrywkiReadRepository
from handball.contracts.season_repository import SezonReadRepository
from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
from handball.domain.options import OpcjaWyboru


class SlownikiZawodnikowService:
    def __init__(
        self,
        sezony: SezonReadRepository,
        rozgrywki: RozgrywkiReadRepository,
        kolejnosc: KolejnoscRozgrywekPolicy,
    ) -> None:
        self._sezony = sezony
        self._rozgrywki = rozgrywki
        self._kolejnosc = kolejnosc

    def pobierz_opcje(self) -> tuple[list[OpcjaWyboru], list[str]]:
        return (
            self._sezony.pobierz_wszystkie(),
            self._kolejnosc.uporzadkuj_nazwy(self._rozgrywki.pobierz_nazwy(None)),
        )
