from handball.domain.classifications import PozycjaSkladu, SzczegolySkladu
from handball.interface.view_models.classifications import (
    PozycjaSkladuViewModel,
    SzczegolySkladuViewModel,
)


class SkladPresenter:
    def przygotuj(self, szczegoly: SzczegolySkladu) -> SzczegolySkladuViewModel:
        pozycje = sorted(
            {(zawodnik.pozycja or "").strip().casefold() for zawodnik in szczegoly.zawodnicy}
            - {"", "—", "-"}
        )
        kolory = {pozycja: indeks * 137 % 360 for indeks, pozycja in enumerate(pozycje)}
        zawodnicy = [
            PozycjaSkladuViewModel(
                id_zawodnik=zawodnik.id_zawodnik,
                zawodnik=zawodnik.zawodnik,
                nr_koszulki=zawodnik.nr_koszulki,
                pozycja=zawodnik.pozycja,
                wzrost=zawodnik.wzrost,
                waga=zawodnik.waga,
                kolor_pozycji=kolory.get((zawodnik.pozycja or "").strip().casefold()),
            )
            for zawodnik in sorted(szczegoly.zawodnicy, key=self._kolejnosc)
        ]
        return SzczegolySkladuViewModel(szczegoly.sklad, zawodnicy)

    def _kolejnosc(self, zawodnik: PozycjaSkladu) -> tuple[bool, str, bool, int, str]:
        pozycja = (zawodnik.pozycja or "").strip().casefold()
        return (
            pozycja in {"", "—", "-"},
            pozycja,
            zawodnik.nr_koszulki is None,
            zawodnik.nr_koszulki or 0,
            zawodnik.zawodnik.casefold(),
        )
