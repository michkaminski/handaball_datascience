from handball.domain.catalogs import (
    FiltryKatalogu,
    PozycjaDruzyny,
    PozycjaRozgrywek,
    PozycjaSezonu,
    StronaKatalogu,
)
from handball.domain.options import OpcjaWyboru


class KatalogPodstawowyInMemoryRepository:
    def __init__(self) -> None:
        self.filtry: FiltryKatalogu | None = None

    def pobierz_sezony(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaSezonu]:
        self.filtry = filtry
        return StronaKatalogu([PozycjaSezonu(195, "2025/2026", 2025, 12, "aktywny", 240)], 1, 1, 20)

    def pobierz_rozgrywki(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaRozgrywek]:
        self.filtry = filtry
        return StronaKatalogu(
            [PozycjaRozgrywek(8, 195, "2025/2026", "Superliga", "M", 14, 182)], 1, 1, 20
        )

    def pobierz_druzyny(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaDruzyny]:
        self.filtry = filtry
        return StronaKatalogu(
            [PozycjaDruzyny(77, 5, 195, "2025/2026", "Drużyna Testowa", "M", "Kielce", False, 26)],
            1,
            1,
            20,
        )

    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]:
        return [OpcjaWyboru(195, "2025/2026")]
