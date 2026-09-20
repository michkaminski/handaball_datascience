from handball.domain.players import StronaZawodnikow
from handball.interface.view_models.players import (
    PozycjaListyZawodnikowViewModel,
    StronaZawodnikowViewModel,
)


class ZawodnikPresenter:
    def przygotuj_liste(self, strona: StronaZawodnikow) -> StronaZawodnikowViewModel:
        return StronaZawodnikowViewModel(
            pozycje=[
                PozycjaListyZawodnikowViewModel(
                    id_zawodnik=p.id_zawodnik,
                    imie=p.imie or "—",
                    nazwisko=p.nazwisko or "—",
                    rocznik=str(p.rocznik) if p.rocznik is not None else "—",
                    pozycje=", ".join(p.pozycje) or "—",
                    druzyny=", ".join(p.druzyny) or "—",
                    wzrost=f"{p.wzrost} cm" if p.wzrost is not None else "—",
                    waga=f"{p.waga} kg" if p.waga is not None else "—",
                )
                for p in strona.pozycje
            ],
            liczba_wszystkich=strona.liczba_wszystkich,
            strona=strona.strona,
            rozmiar_strony=strona.rozmiar_strony,
        )
