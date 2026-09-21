from decimal import Decimal

from handball.domain.venue_details import (
    RankingZawodnikaHali,
    StatystykiHali,
    StronaZawodnikowHali,
    SzczegolyHali,
)
from handball.interface.presenters.match_presenter import MeczFormat
from handball.interface.view_models.venue_details import (
    FrekwencjaHaliViewModel,
    KomorkaKalendarzaHaliViewModel,
    PasekHaliViewModel,
    PorownanieHaliViewModel,
    ProfilWynikowHaliViewModel,
    RankingDruzynyHaliViewModel,
    RankingRozgrywekHaliViewModel,
    RankingZawodnikaHaliViewModel,
    RekordMeczuHaliViewModel,
    StatystykiHaliViewModel,
    StronaZawodnikowHaliViewModel,
    SzczegolyHaliViewModel,
    ZawodnikHaliViewModel,
)


class SzczegolyHaliPresenter:
    def __init__(self, formatowanie: MeczFormat) -> None:
        self._format = formatowanie

    def przygotuj_szczegoly(self, dane: SzczegolyHali) -> SzczegolyHaliViewModel:
        adres = " ".join(w for w in (dane.ulica, dane.numer) if w) or "—"
        return SzczegolyHaliViewModel(
            id_hala=dane.id_hala,
            nazwa=dane.nazwa or "Hala bez nazwy",
            miasto=self._format.tekst(dane.miasto),
            adres=adres,
            pojemnosc=self._format.tekst(dane.pojemnosc),
            pierwszy_mecz=self._format.data(dane.pierwszy_mecz),
            ostatni_mecz=self._format.data(dane.ostatni_mecz),
            liczba_meczow=dane.liczba_meczow,
            liczba_rozegranych=dane.liczba_rozegranych,
            liczba_rozgrywek=dane.liczba_rozgrywek,
            liczba_sezonow=dane.liczba_sezonow,
            liczba_druzyn=dane.liczba_druzyn,
            liczba_zawodnikow=dane.liczba_zawodnikow,
        )

    def przygotuj_zawodnikow(self, dane: StronaZawodnikowHali) -> StronaZawodnikowHaliViewModel:
        return StronaZawodnikowHaliViewModel(
            [
                ZawodnikHaliViewModel(
                    id_zawodnik=z.id_zawodnik,
                    zawodnik=" ".join(n for n in (z.imie, z.nazwisko) if n) or "Brak danych",
                    pierwszy_wystep=self._format.data(z.pierwszy_wystep),
                    ostatni_wystep=self._format.data(z.ostatni_wystep),
                    wystepy=z.wystepy,
                    bramki=self._format.tekst(z.bramki),
                    srednia_bramek=self._srednia(z.srednia_bramek),
                    druzyny=", ".join(z.druzyny) or "—",
                )
                for z in dane.pozycje
            ],
            dane.liczba_wszystkich,
            dane.strona,
            dane.rozmiar_strony,
        )

    def przygotuj_statystyki(self, dane: StatystykiHali) -> StatystykiHaliViewModel:
        wszystkie_mecze = sum(trend.mecze for trend in dane.trendy)
        maks_kalendarza = max((komorka.mecze for komorka in dane.kalendarz), default=0)
        return StatystykiHaliViewModel(
            druzyny=[
                RankingDruzynyHaliViewModel(
                    druzyna=d.druzyna or f"Zespół #{d.id_zespol}",
                    mecze=d.mecze,
                    zwyciestwa=d.zwyciestwa,
                    remisy=d.remisy,
                    porazki=d.porazki,
                    bramki_zdobyte=d.bramki_zdobyte,
                    bramki_stracone=d.bramki_stracone,
                    bilans=f"{d.bramki_zdobyte - d.bramki_stracone:+d}",
                )
                for d in dane.druzyny
            ],
            rozgrywki=[
                RankingRozgrywekHaliViewModel(
                    r.rozgrywki,
                    r.mecze,
                    r.sezony,
                    self._format.tekst(r.pierwszy_sezon),
                    self._format.tekst(r.ostatni_sezon),
                )
                for r in dane.rozgrywki
            ],
            zawodnicy=[self._ranking_zawodnika(z) for z in dane.zawodnicy],
            skuteczni_zawodnicy=[self._ranking_zawodnika(z) for z in dane.skuteczni_zawodnicy],
            liczba_druzyn=dane.liczba_druzyn,
            liczba_rozgrywek=dane.liczba_rozgrywek,
            liczba_zawodnikow=dane.liczba_zawodnikow,
            trendy_mecze=self._paski(
                [(trend.sezon, trend.mecze, str(trend.mecze), "") for trend in dane.trendy]
            ),
            trendy_bramki=self._paski(
                [
                    (
                        trend.sezon,
                        float(trend.srednia_bramek),
                        f"{trend.srednia_bramek:.1f}",
                        f"{trend.mecze} meczów",
                    )
                    for trend in dane.trendy
                ]
            ),
            dni_tygodnia=self._paski(
                [
                    (
                        dzien.etykieta,
                        dzien.mecze,
                        str(dzien.mecze),
                        self._udzial(dzien.mecze, wszystkie_mecze),
                    )
                    for dzien in dane.dni_tygodnia
                ]
            ),
            histogram_bramek=self._paski(
                [
                    (
                        przedzial.etykieta,
                        przedzial.mecze,
                        str(przedzial.mecze),
                        self._udzial(przedzial.mecze, wszystkie_mecze),
                    )
                    for przedzial in dane.histogram_bramek
                ]
            ),
            sezony_kalendarza=sorted({komorka.sezon for komorka in dane.kalendarz}),
            kalendarz=self._kalendarz(dane, maks_kalendarza),
            profil_wynikow=ProfilWynikowHaliViewModel(
                self._liczba(dane.profil_wynikow.srednia_bramek),
                self._liczba(dane.profil_wynikow.mediana_bramek),
                self._liczba(dane.profil_wynikow.odchylenie_bramek),
                self._zakres(
                    dane.profil_wynikow.minimum_bramek, dane.profil_wynikow.maksimum_bramek
                ),
                self._zakres(
                    dane.profil_wynikow.kwartyl_pierwszy, dane.profil_wynikow.kwartyl_trzeci
                ),
                self._liczba(dane.profil_wynikow.srednia_roznica),
                self._licznik_z_udzialem(dane.profil_wynikow.mecze_jedna_bramka, wszystkie_mecze),
                self._licznik_z_udzialem(dane.profil_wynikow.mecze_trzy_bramki, wszystkie_mecze),
                self._licznik_z_udzialem(dane.profil_wynikow.mecze_piec_bramek, wszystkie_mecze),
            ),
            frekwencja=FrekwencjaHaliViewModel(
                dane.frekwencja.mecze_z_danymi == dane.frekwencja.wszystkie_mecze,
                self._licznik_z_udzialem(
                    dane.frekwencja.mecze_z_danymi, dane.frekwencja.wszystkie_mecze
                ),
                self._liczba(dane.frekwencja.srednia, 0),
                self._liczba(dane.frekwencja.mediana, 0),
                self._format.tekst(dane.frekwencja.maksimum),
                f"{dane.frekwencja.wypelnienie:.1f}%"
                if dane.frekwencja.wypelnienie is not None
                else "—",
            ),
            porownanie=[
                PorownanieHaliViewModel(
                    p.metryka, self._liczba(p.hala), self._liczba(p.wszystkie_hale)
                )
                for p in dane.porownanie
            ],
            rekordy=[
                RekordMeczuHaliViewModel(
                    r.rodzaj,
                    r.id_mecz,
                    self._format.data(r.data),
                    "{} – {}".format(r.gospodarz or "—", r.gosc or "—"),
                    f"{r.wynik_gosp}:{r.wynik_gosc}",
                    self._wartosc_rekordu(r.rodzaj, r.wartosc),
                )
                for r in dane.rekordy
            ],
        )

    def _ranking_zawodnika(self, dane: RankingZawodnikaHali) -> RankingZawodnikaHaliViewModel:
        return RankingZawodnikaHaliViewModel(
            dane.id_zawodnik,
            dane.zawodnik,
            dane.wystepy,
            dane.bramki,
            self._srednia(dane.srednia_bramek),
            ", ".join(dane.druzyny) or "—",
        )

    def _srednia(self, wartosc: Decimal | None) -> str:
        return f"{wartosc:.2f}" if wartosc is not None else "—"

    def _paski(self, dane: list[tuple[str, int | float, str, str]]) -> list[PasekHaliViewModel]:
        maksimum = max((pozycja[1] for pozycja in dane), default=0)
        return [
            PasekHaliViewModel(
                etykieta,
                wartosc,
                round(liczba * 100 / maksimum) if maksimum else 0,
                max(3, round(liczba * 100 / maksimum)) if maksimum else 0,
                opis,
            )
            for etykieta, liczba, wartosc, opis in dane
        ]

    def _liczba(self, wartosc: Decimal | None, miejsca: int = 1) -> str:
        return f"{wartosc:.{miejsca}f}" if wartosc is not None else "—"

    def _zakres(self, minimum: object, maksimum: object) -> str:
        return f"{minimum}–{maksimum}" if minimum is not None and maksimum is not None else "—"

    def _udzial(self, liczba: int, wszystkie: int) -> str:
        return f"{liczba * 100 / wszystkie:.1f}%" if wszystkie else "—"

    def _licznik_z_udzialem(self, liczba: int, wszystkie: int) -> str:
        return f"{liczba} ({self._udzial(liczba, wszystkie)})"

    def _wartosc_rekordu(self, rodzaj: str, wartosc: int) -> str:
        if rodzaj == "Najwyższa frekwencja":
            return f"{wartosc} widzów"
        if rodzaj in {"Pierwszy mecz", "Ostatni mecz"}:
            return ""
        return f"{wartosc} bramek"

    def _kalendarz(
        self, dane: StatystykiHali, maksimum: int
    ) -> list[KomorkaKalendarzaHaliViewModel]:
        wartosci = {(komorka.sezon, komorka.miesiac): komorka.mecze for komorka in dane.kalendarz}
        return [
            KomorkaKalendarzaHaliViewModel(
                sezon,
                miesiac,
                wartosci.get((sezon, miesiac), 0),
                round(wartosci.get((sezon, miesiac), 0) * 4 / maksimum) if maksimum else 0,
            )
            for sezon in sorted({komorka.sezon for komorka in dane.kalendarz})
            for miesiac in range(1, 13)
        ]
