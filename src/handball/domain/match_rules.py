from enum import StrEnum

from handball.domain.matches import DaneMeczu, ZawodnikMeczu


class StatusMeczu(StrEnum):
    WYCOFANY = "wycofany"
    WALKOWER = "walkower"
    ROZEGRANY = "rozegrany"
    ZAPLANOWANY = "zaplanowany"


class MeczPolicy:
    def para[T](self, mecz: DaneMeczu, gospodarz: T, gosc: T) -> tuple[T, T]:
        return (gosc, gospodarz) if mecz.zamiana else (gospodarz, gosc)

    def status(self, mecz: DaneMeczu) -> StatusMeczu:
        if mecz.wycofany:
            return StatusMeczu.WYCOFANY
        if mecz.id_zespol_walkower is not None:
            return StatusMeczu.WALKOWER
        if mecz.wynik_gosp_full is not None and mecz.wynik_gosc_full is not None:
            return StatusMeczu.ROZEGRANY
        return StatusMeczu.ZAPLANOWANY

    def ma_serie_karnych(self, mecz: DaneMeczu) -> bool:
        return mecz.dogrywka_karne_gosp is not None or mecz.dogrywka_karne_gosc is not None

    def ma_dogrywke(self, mecz: DaneMeczu) -> bool:
        return mecz.dogrywka_1_full_gosp is not None or mecz.dogrywka_1_full_gosc is not None

    def najwiecej_bramek(self, sklad: list[ZawodnikMeczu]) -> int | None:
        znane = [z.bramki for z in sklad if z.bramki is not None]
        return max(znane) if znane else None
