from __future__ import annotations

from datetime import datetime
from typing import Protocol
from zoneinfo import ZoneInfo

from handball.contracts.match_preview_repository import ZapowiedzMeczuReadRepository
from handball.domain.match_predictions import PrognozaZapowiedzi
from handball.domain.match_preview import (
    DruzynaZapowiedzi,
    KadraDruzyny,
    KadraZapowiedziCalculator,
    MeczZapowiedzi,
    OpcjeZapowiedzi,
    ProfilDruzynyZapowiedzi,
    SezonKadry,
    StatystykiZapowiedziCalculator,
    WystepZapowiedzi,
    ZapowiedzMeczu,
)


class Zegar(Protocol):
    def teraz(self) -> datetime: ...


class ZegarWarszawa:
    STREFA = ZoneInfo("Europe/Warsaw")

    def teraz(self) -> datetime:
        return datetime.now(self.STREFA).replace(tzinfo=None)


class PrognozaZapowiedziProvider(Protocol):
    def pobierz(self, wersja_modelu: str, id_mecz: int) -> PrognozaZapowiedzi: ...


class ZapowiedzMeczuService:
    def __init__(
        self,
        repozytorium: ZapowiedzMeczuReadRepository,
        statystyki: StatystykiZapowiedziCalculator,
        kadry: KadraZapowiedziCalculator,
        prognozy: PrognozaZapowiedziProvider,
        zegar: Zegar,
    ) -> None:
        self._repozytorium = repozytorium
        self._statystyki = statystyki
        self._kadry = kadry
        self._prognozy = prognozy
        self._zegar = zegar

    def pobierz(
        self, id_mecz: int, wersja_modelu: str, opcje: OpcjeZapowiedzi | None = None
    ) -> ZapowiedzMeczu:
        opcje = opcje or OpcjeZapowiedzi()
        mecz = self._repozytorium.pobierz_mecz(id_mecz)
        stan_na = mecz.data_faktyczna or self._zegar.teraz()
        sezon_poprzedni = self._repozytorium.pobierz_poprzedni_sezon(mecz.id_sezon)
        wystepy_gospodarza = self._wystepy(mecz.gospodarz, stan_na)
        return ZapowiedzMeczu(
            mecz=mecz,
            stan_na=stan_na,
            gospodarz=self._profil(
                mecz, mecz.gospodarz, wystepy_gospodarza, stan_na, True, sezon_poprzedni, opcje
            ),
            gosc=self._profil(
                mecz,
                mecz.gosc,
                self._wystepy(mecz.gosc, stan_na),
                stan_na,
                False,
                sezon_poprzedni,
                opcje,
            ),
            bezposrednie=self._statystyki.bezposrednie(
                wystepy_gospodarza,
                mecz.gosc.id_zespol,
                self._statystyki.poczatek_okresu(stan_na, opcje.lata_bezposrednich),
            ),
            prognoza=self._prognozy.pobierz(wersja_modelu, id_mecz),
            opcje=opcje,
            sezon_poprzedni=sezon_poprzedni,
        )

    def _wystepy(
        self, druzyna: DruzynaZapowiedzi, stan_na: datetime
    ) -> tuple[WystepZapowiedzi, ...]:
        if druzyna.id_zespol is None:
            return ()
        return tuple(self._repozytorium.pobierz_wystepy(druzyna.id_zespol, stan_na))

    def _profil(
        self,
        mecz: MeczZapowiedzi,
        druzyna: DruzynaZapowiedzi,
        wystepy: tuple[WystepZapowiedzi, ...],
        stan_na: datetime,
        u_siebie: bool,
        sezon_poprzedni: SezonKadry | None,
        opcje: OpcjeZapowiedzi,
    ) -> ProfilDruzynyZapowiedzi:
        return self._statystyki.profil(
            druzyna,
            wystepy,
            mecz.id_rozgrywki,
            u_siebie,
            self._kadra(mecz, druzyna, stan_na, sezon_poprzedni, opcje),
        )

    def _kadra(
        self,
        mecz: MeczZapowiedzi,
        druzyna: DruzynaZapowiedzi,
        stan_na: datetime,
        sezon_poprzedni: SezonKadry | None,
        opcje: OpcjeZapowiedzi,
    ) -> KadraDruzyny:
        if druzyna.id_zespol is None:
            return self._kadry.kadra(druzyna, ())
        sezon = self._repozytorium.pobierz_kadre(druzyna.id_zespol, mecz.id_sezon, stan_na)
        if sezon_poprzedni is None:
            return self._kadry.kadra(druzyna, sezon, rozgrywki=mecz.rozgrywki)
        dawni = (
            self._repozytorium.pobierz_kadre(druzyna.id_zespol, sezon_poprzedni.id_sezon, stan_na)
            if opcje.kadra_z_poprzedniego_sezonu
            else []
        )
        wystepy = self._repozytorium.pobierz_wystepy_zawodnikow(
            [z.id_zawodnik for z in (*sezon, *dawni)], sezon_poprzedni.id_sezon, stan_na
        )
        return self._kadry.kadra(druzyna, sezon, dawni, wystepy, mecz.rozgrywki)
