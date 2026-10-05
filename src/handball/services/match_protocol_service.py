from __future__ import annotations

from handball.contracts.match_preview_repository import ZapowiedzMeczuReadRepository
from handball.contracts.match_protocol_repository import ProtokolMeczuReadRepository
from handball.domain.match_preview import OpcjeZapowiedzi
from handball.domain.match_protocol import KolejnoscProtokolu, ProtokolMeczu
from handball.services.match_preview_service import KadraMeczuBuilder, Zegar


class ProtokolMeczuService:
    def __init__(
        self,
        zapowiedzi: ZapowiedzMeczuReadRepository,
        protokoly: ProtokolMeczuReadRepository,
        kadry: KadraMeczuBuilder,
        zegar: Zegar,
    ) -> None:
        self._zapowiedzi = zapowiedzi
        self._protokoly = protokoly
        self._kadry = kadry
        self._zegar = zegar

    def pobierz(
        self,
        id_mecz: int,
        opcje: OpcjeZapowiedzi | None = None,
        kolejnosc: KolejnoscProtokolu = KolejnoscProtokolu.POZYCJE,
    ) -> ProtokolMeczu:
        opcje = opcje or OpcjeZapowiedzi()
        mecz = self._zapowiedzi.pobierz_mecz(id_mecz)
        stan_na = mecz.data_faktyczna or self._zegar.teraz()
        sezon_poprzedni = self._zapowiedzi.pobierz_poprzedni_sezon(mecz.id_sezon)
        return ProtokolMeczu(
            mecz=mecz,
            stan_na=stan_na,
            gospodarz=self._kadry.kadra(mecz, mecz.gospodarz, stan_na, sezon_poprzedni, opcje),
            gosc=self._kadry.kadra(mecz, mecz.gosc, stan_na, sezon_poprzedni, opcje),
            dane=self._protokoly.pobierz_dane_protokolu(id_mecz),
            opcje=opcje,
            kolejnosc=kolejnosc,
        )
