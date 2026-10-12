from __future__ import annotations

from typing import Protocol

from handball.contracts.match_preview_repository import ZapowiedzMeczuReadRepository
from handball.domain.errors import NieZnalezionoMeczu
from handball.domain.match_predictions import PrognozaMeczu
from handball.domain.match_preview import (
    BezposrednieMecze,
    DruzynaZapowiedzi,
    MeczZapowiedzi,
    StatystykiZapowiedziCalculator,
    WystepZapowiedzi,
    ZawodnikKadry,
)
from handball.domain.match_report import (
    AnalizaModeluCalculator,
    AtakDruzynyCalculator,
    RaportMeczu,
    TloSezonuCalculator,
    TloSezonuDruzyny,
)
from handball.services.match_statistics_service import StatystykiMeczuService


class PrognozyModeluProvider(Protocol):
    def nazwa(self, wersja_modelu: str) -> str: ...

    def prognozy(self, wersja_modelu: str) -> tuple[PrognozaMeczu, ...]: ...


class RaportMeczuService:
    def __init__(
        self,
        statystyki: StatystykiMeczuService,
        zapowiedzi: ZapowiedzMeczuReadRepository,
        prognozy: PrognozyModeluProvider,
        model: AnalizaModeluCalculator,
        atak: AtakDruzynyCalculator,
        tlo: TloSezonuCalculator,
        historia: StatystykiZapowiedziCalculator,
    ) -> None:
        self._statystyki = statystyki
        self._zapowiedzi = zapowiedzi
        self._prognozy = prognozy
        self._model = model
        self._atak = atak
        self._tlo = tlo
        self._historia = historia

    def pobierz(self, id_mecz: int, wersja_modelu: str, z_modelem: bool = True) -> RaportMeczu:
        statystyki = self._statystyki.pobierz(id_mecz)
        if not statystyki.rozegrany:
            raise NieZnalezionoMeczu(f"Mecz {id_mecz} nie ma jeszcze wyniku.")
        mecz = self._zapowiedzi.pobierz_mecz(id_mecz)
        prognozy = self._prognozy.prognozy(wersja_modelu) if z_modelem else ()
        a, b = statystyki.gospodarz.bramki, statystyki.gosc.bramki
        szczegoly = statystyki.szczegoly
        wystepy_gospodarza = self._wystepy(mecz, mecz.gospodarz)
        wystepy_goscia = self._wystepy(mecz, mecz.gosc)
        return RaportMeczu(
            statystyki=statystyki,
            mecz=mecz,
            model=self._model.analizuj(prognozy, id_mecz),
            nazwa_modelu=self._prognozy.nazwa(wersja_modelu) if z_modelem else "",
            liga=self._model.tlo_ligi(prognozy, id_mecz),
            atak_gospodarza=self._atak.oblicz(
                szczegoly.sklad_gospodarz, self._kadra(mecz, mecz.gospodarz), a
            ),
            atak_goscia=self._atak.oblicz(szczegoly.sklad_gosc, self._kadra(mecz, mecz.gosc), b),
            tlo_gospodarza=self._tlo_druzyny(wystepy_gospodarza, mecz, a, b),
            tlo_goscia=self._tlo_druzyny(wystepy_goscia, mecz, b, a),
            widzowie=szczegoly.mecz.widzowie,
            bezposrednie=self._bezposrednie(wystepy_gospodarza, mecz),
        )

    def _wystepy(
        self, mecz: MeczZapowiedzi, druzyna: DruzynaZapowiedzi
    ) -> tuple[WystepZapowiedzi, ...] | None:
        if druzyna.id_zespol is None or mecz.data_faktyczna is None:
            return None
        return tuple(self._zapowiedzi.pobierz_wystepy(druzyna.id_zespol, mecz.data_faktyczna))

    def _kadra(self, mecz: MeczZapowiedzi, druzyna: DruzynaZapowiedzi) -> list[ZawodnikKadry]:
        if druzyna.id_zespol is None or mecz.data_faktyczna is None:
            return []
        return self._zapowiedzi.pobierz_kadre(druzyna.id_zespol, mecz.id_sezon, mecz.data_faktyczna)

    def _tlo_druzyny(
        self,
        wystepy: tuple[WystepZapowiedzi, ...] | None,
        mecz: MeczZapowiedzi,
        zdobyte: int | None,
        stracone: int | None,
    ) -> TloSezonuDruzyny | None:
        if wystepy is None:
            return None
        tlo = self._tlo.oblicz(wystepy, mecz, zdobyte, stracone)
        return tlo if tlo.mecze else None

    def _bezposrednie(
        self, wystepy: tuple[WystepZapowiedzi, ...] | None, mecz: MeczZapowiedzi
    ) -> BezposrednieMecze | None:
        if wystepy is None or mecz.gosc.id_zespol is None:
            return None
        historia = self._historia.bezposrednie(wystepy, mecz.gosc.id_zespol)
        return historia if historia.mecze else None
