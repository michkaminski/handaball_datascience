from handball.domain.opponent_defense import (
    AnalizaDefensywyRywala,
    FiltryDefensywyRywala,
    MeczZDefensywaRywala,
    StatystykiKlasyDefensywy,
)
from handball.interface.presenters.match_presenter import MeczFormat
from handball.interface.view_models.opponent_defense import (
    DefensywaRywalaKartaViewModel,
    DefensywaRywalaSzczegolyViewModel,
    KlasaKartaViewModel,
    KlasaSzczegolyViewModel,
    KrokPrzykladuViewModel,
    PrzykladMeczuViewModel,
)


class DefensywaRywalaPresenter:
    def __init__(self, formatowanie: MeczFormat) -> None:
        self._format = formatowanie

    def przygotuj_karte(self, analiza: AnalizaDefensywyRywala) -> DefensywaRywalaKartaViewModel:
        klasy = [
            KlasaKartaViewModel(klasa=k.klasa, srednia=self._liczba(k.srednia), n=str(k.n))
            for k in analiza.klasy
        ]
        return DefensywaRywalaKartaViewModel(
            id_zawodnik=analiza.id_zawodnik,
            liczba_meczow=str(analiza.liczba_meczow_z_defense_factor),
            klasy=klasy,
            wykres=[
                {"klasa": k.klasa, "srednia": k.srednia, "n": k.n}
                for k in analiza.klasy
                if k.srednia is not None
            ],
            ma_wystarczajaco_danych=analiza.liczba_meczow_z_defense_factor > 0,
        )

    def przygotuj_szczegoly(
        self,
        analiza: AnalizaDefensywyRywala,
        nazwa_zawodnika: str,
        filtry: FiltryDefensywyRywala,
        id_mecz_przykladu: int | None,
    ) -> DefensywaRywalaSzczegolyViewModel:
        cfg = analiza.konfiguracja
        sezony_w_kolejnosci: list[str] = []
        rozgrywki_w_kolejnosci: list[str] = []
        for m in analiza.mecze:
            if m.sezon not in sezony_w_kolejnosci:
                sezony_w_kolejnosci.append(m.sezon)
            if m.rozgrywki not in rozgrywki_w_kolejnosci:
                rozgrywki_w_kolejnosci.append(m.rozgrywki)
        zakres_sezonow = (
            "brak meczów w wybranym zakresie"
            if not sezony_w_kolejnosci
            else sezony_w_kolejnosci[0]
            if len(sezony_w_kolejnosci) == 1
            else f"{sezony_w_kolejnosci[0]}–{sezony_w_kolejnosci[-1]}"
        )
        zakres_rozgrywek = ", ".join(rozgrywki_w_kolejnosci) or "—"
        pary = [
            m
            for m in analiza.mecze
            if m.defense_factor is not None and m.bramki_zawodnika is not None
        ]
        return DefensywaRywalaSzczegolyViewModel(
            id_zawodnik=analiza.id_zawodnik,
            nazwa_zawodnika=nazwa_zawodnika,
            liczba_meczow=str(analiza.liczba_wystapien),
            liczba_ze_znanymi_bramkami=str(analiza.liczba_meczow_ze_znanymi_bramkami),
            liczba_z_defense_factor=str(analiza.liczba_meczow_z_defense_factor),
            zakres_sezonow=zakres_sezonow,
            zakres_rozgrywek=zakres_rozgrywek,
            opis_filtrow=self._opis_filtrow(filtry),
            mala_proba_ostrzezenie=analiza.liczba_meczow_z_defense_factor < cfg.prog_malej_proby,
            klasy=[self._klasa_szczegoly(k, cfg.prog_malej_proby) for k in analiza.klasy],
            wykres_klas=[{"klasa": k.klasa, "srednia": k.srednia, "n": k.n} for k in analiza.klasy],
            wykres_prawdopodobienstw=[
                {
                    "klasa": k.klasa,
                    "progi": [{"prog": p, "udzial": u} for p, u in k.udzialy_progowe],
                }
                for k in analiza.klasy
            ],
            mecze=[self._wiersz_meczu(m) for m in analiza.mecze],
            punkty_scatter=[self._punkt_scatter(m) for m in pary],
            boxplot_klas=[self._boxplot_klasy(k) for k in analiza.klasy if k.n > 0],
            r_pearson=self._liczba(analiza.korelacja.r_pearson),
            interpretacja_pearson=self._interpretacja_korelacji(analiza.korelacja.r_pearson),
            rho_spearman=self._liczba(analiza.korelacja.rho_spearman),
            roznica_pearson_spearman=self._roznica_korelacji(
                analiza.korelacja.r_pearson, analiza.korelacja.rho_spearman
            ),
            wyraz_wolny=self._liczba(analiza.regresja.wyraz_wolny),
            wspolczynnik_kierunkowy=self._liczba(analiza.regresja.wspolczynnik_kierunkowy),
            r_kwadrat=self._liczba(analiza.regresja.r_kwadrat),
            przedzial_ufnosci=self._przedzial(analiza.regresja.przedzial_ufnosci_beta1),
            delta_10=self._delta_10(analiza.regresja.wspolczynnik_kierunkowy),
            konfiguracja={
                "k_shrinkage": self._liczba(cfg.k_shrinkage),
                "w_poprzedni_sezon": self._liczba(cfg.w_poprzedni_sezon),
                "granica_bardzo_mocna": self._liczba(cfg.granica_bardzo_mocna),
                "granica_mocna": self._liczba(cfg.granica_mocna),
                "granica_slaba": self._liczba(cfg.granica_slaba),
                "granica_bardzo_slaba": self._liczba(cfg.granica_bardzo_slaba),
                "prog_malej_proby": str(cfg.prog_malej_proby),
                "progi": ", ".join(f"{p}+" for p in cfg.progi_prawdopodobienstwa),
            },
            poprzedni_sezon_uzyty=cfg.uzyj_poprzedniego_sezonu
            and any(m.ga_previous is not None for m in analiza.mecze),
            przyklad=self._przyklad(analiza.mecze, id_mecz_przykladu),
            opcje_przykladu=[
                {
                    "id_mecz": str(m.id_mecz),
                    "etykieta": f"{self._format.data(m.termin)} – {m.przeciwnik or '—'}",
                }
                for m in pary
            ],
            interpretacja_koncowa=self._interpretacja_koncowa(analiza),
            komentarz_automatyczny=self._komentarz_automatyczny(analiza.klasy),
        )

    @staticmethod
    def _opis_filtrow(filtry: FiltryDefensywyRywala) -> str:
        czesci = []
        if filtry.id_sezon is not None:
            czesci.append("wybrany sezon")
        if filtry.liczba_ostatnich_sezonow is not None:
            czesci.append(f"ostatnie {filtry.liczba_ostatnich_sezonow} sezony")
        if filtry.rozgrywki:
            czesci.append(f"rozgrywki: {filtry.rozgrywki}")
        if filtry.przeciwnik:
            czesci.append(f"przeciwnik: {filtry.przeciwnik}")
        if filtry.miejsce == "dom":
            czesci.append("tylko mecze u siebie")
        elif filtry.miejsce == "wyjazd":
            czesci.append("tylko mecze na wyjeździe")
        if not filtry.tylko_pelne_dane:
            czesci.append("łącznie z meczami bez pełnych danych")
        return "; ".join(czesci) if czesci else "cała kariera, wszystkie sezony i rozgrywki"

    def _klasa_szczegoly(
        self, k: StatystykiKlasyDefensywy, prog_malej_proby: int
    ) -> KlasaSzczegolyViewModel:
        return KlasaSzczegolyViewModel(
            klasa=k.klasa,
            n=str(k.n),
            suma_bramek=str(k.suma_bramek),
            srednia=self._liczba(k.srednia),
            mediana=self._liczba(k.mediana),
            minimum=self._liczba(k.minimum),
            maksimum=self._liczba(k.maksimum),
            kwartyl_pierwszy=self._liczba(k.kwartyl_pierwszy),
            kwartyl_trzeci=self._liczba(k.kwartyl_trzeci),
            wariancja=self._liczba(k.wariancja),
            odchylenie_standardowe=self._liczba(k.odchylenie_standardowe),
            mala_proba=k.n < prog_malej_proby,
            udzialy_progowe=[
                {"prog": f"{prog}+", "udzial": f"{100 * udzial:.1f}%"}
                for prog, udzial in k.udzialy_progowe
            ],
        )

    def _wiersz_meczu(self, m: MeczZDefensywaRywala) -> dict[str, str | int | float | None]:
        return {
            "id_mecz": m.id_mecz,
            "data": self._format.data(m.termin),
            "sezon": m.sezon,
            "rozgrywki": m.rozgrywki,
            "druzyna_zawodnika": m.druzyna_zawodnika or "—",
            "przeciwnik": m.przeciwnik or "—",
            "wynik": (
                f"{m.wynik_druzyny_zawodnika}:{m.wynik_przeciwnika}"
                if m.wynik_druzyny_zawodnika is not None and m.wynik_przeciwnika is not None
                else "—"
            ),
            "bramki_zawodnika": m.bramki_zawodnika if m.bramki_zawodnika is not None else None,
            "ga_team": self._liczba(m.ga_team),
            "ga_smoothed": self._liczba(m.ga_smoothed),
            "ga_league": self._liczba(m.ga_league),
            "defense_factor": self._liczba(m.defense_factor),
            "defense_factor_wartosc": m.defense_factor,
            "klasa": m.klasa_defensywy or "—",
            "n_rywala": m.n_meczy_rywala,
        }

    @staticmethod
    def _punkt_scatter(m: MeczZDefensywaRywala) -> dict[str, str | int | float | None]:
        return {
            "x": m.defense_factor,
            "y": m.bramki_zawodnika,
            "id_mecz": m.id_mecz,
            "etykieta": m.przeciwnik or "—",
            "sezon": m.sezon,
            "klasa": m.klasa_defensywy or "—",
        }

    @staticmethod
    def _boxplot_klasy(k: StatystykiKlasyDefensywy) -> dict[str, object]:
        return {
            "klasa": k.klasa,
            "n": k.n,
            "minimum": k.minimum_wewnetrzne,
            "kwartyl_pierwszy": k.kwartyl_pierwszy,
            "mediana": k.mediana,
            "kwartyl_trzeci": k.kwartyl_trzeci,
            "maksimum": k.maksimum_wewnetrzne,
            "odstajace": list(k.wartosci_odstajace),
        }

    @staticmethod
    def _interpretacja_korelacji(r: float | None) -> str:
        if r is None:
            return "brak danych do oceny"
        sila = abs(r)
        if sila < 0.10:
            opis = "praktycznie brak liniowej zależności"
        elif sila < 0.30:
            opis = "słaba zależność"
        elif sila < 0.50:
            opis = "umiarkowana zależność"
        elif sila < 0.70:
            opis = "wyraźna zależność"
        else:
            opis = "silna zależność"
        kierunek = "dodatnia" if r >= 0 else "ujemna"
        return f"{opis} ({kierunek})"

    @staticmethod
    def _roznica_korelacji(r: float | None, rho: float | None) -> str:
        if r is None or rho is None:
            return ""
        if abs(r - rho) > 0.15:
            return (
                "Wyniki Pearsona i Spearmana różnią się zauważalnie — "
                "zależność może nie być liniowa."
            )
        return "Wyniki Pearsona i Spearmana są zbliżone."

    @staticmethod
    def _przedzial(przedzial: tuple[float, float] | None) -> str:
        if przedzial is None:
            return "—"
        dolny, gorny = przedzial
        return f"{dolny:.2f} – {gorny:.2f}"

    @staticmethod
    def _delta_10(beta1: float | None) -> str:
        if beta1 is None:
            return "—"
        return f"{beta1 * 0.10:+.2f}"

    def _przyklad(
        self, mecze: tuple[MeczZDefensywaRywala, ...], id_mecz_przykladu: int | None
    ) -> PrzykladMeczuViewModel | None:
        kandydaci = [m for m in mecze if m.defense_factor is not None]
        if not kandydaci:
            return None
        wybrany = None
        if id_mecz_przykladu is not None:
            wybrany = next((m for m in kandydaci if m.id_mecz == id_mecz_przykladu), None)
        if wybrany is None:
            wybrany = kandydaci[-1]
        return PrzykladMeczuViewModel(
            id_mecz=wybrany.id_mecz,
            etykieta=f"{self._format.data(wybrany.termin)} — "
            f"{wybrany.druzyna_zawodnika or '—'} vs {wybrany.przeciwnik or '—'}",
            kroki=self._kroki_przykladu(wybrany),
        )

    def _kroki_przykladu(self, m: MeczZDefensywaRywala) -> list[KrokPrzykladuViewModel]:
        kroki = [
            KrokPrzykladuViewModel(
                "Rywal rozegrał wcześniej w tych rozgrywkach", f"{m.n_meczy_rywala} meczów"
            )
        ]
        if m.n_meczy_rywala > 0 and m.ga_team is not None:
            suma = m.ga_team * m.n_meczy_rywala
            kroki.append(
                KrokPrzykladuViewModel("Stracił łącznie", f"{suma:.0f} bramek w tych meczach")
            )
            kroki.append(
                KrokPrzykladuViewModel(
                    "GA_team = bramki stracone / mecze",
                    f"{suma:.0f} / {m.n_meczy_rywala} = {m.ga_team:.2f}",
                )
            )
        else:
            kroki.append(
                KrokPrzykladuViewModel("GA_team", "brak wcześniejszych meczów w tych rozgrywkach")
            )
        kroki.append(
            KrokPrzykladuViewModel(
                "GA_league (średnia ligowa przed meczem)", self._liczba(m.ga_league)
            )
        )
        if m.ga_previous is not None:
            kroki.append(
                KrokPrzykladuViewModel("GA_previous (poprzedni sezon)", self._liczba(m.ga_previous))
            )
        if m.ga_smoothed is not None and m.ga_league is not None:
            kroki.append(
                KrokPrzykladuViewModel(
                    "GA_smoothed (wygładzone)",
                    f"{m.ga_smoothed:.2f}",
                )
            )
            kroki.append(
                KrokPrzykladuViewModel(
                    "DefenseFactor = GA_smoothed / GA_league",
                    f"{m.ga_smoothed:.2f} / {m.ga_league:.2f} = {m.defense_factor:.2f}"
                    if m.defense_factor is not None
                    else "—",
                )
            )
        kroki.append(KrokPrzykladuViewModel("Klasa defensywy", m.klasa_defensywy or "—"))
        kroki.append(
            KrokPrzykladuViewModel(
                "Zawodnik zdobył w tym meczu",
                f"{m.bramki_zawodnika} bramek" if m.bramki_zawodnika is not None else "—",
            )
        )
        return kroki

    def _interpretacja_koncowa(self, analiza: AnalizaDefensywyRywala) -> str:
        niepuste = [k for k in analiza.klasy if k.n > 0]
        if len(niepuste) < 2 or analiza.korelacja.r_pearson is None:
            return (
                "Zbyt mało meczów z wyznaczonym Defense Factor, aby sensownie porównać klasy "
                "defensywy. Zwiększ zakres filtrów albo poczekaj na więcej danych."
            )
        pierwsza, ostatnia = niepuste[0], niepuste[-1]
        roznica = (ostatnia.srednia or 0) - (pierwsza.srednia or 0)
        r = analiza.korelacja.r_pearson
        rho = analiza.korelacja.rho_spearman
        beta1 = analiza.regresja.wspolczynnik_kierunkowy
        r2 = analiza.regresja.r_kwadrat
        zdania = [
            f"W analizowanej próbie {analiza.liczba_meczow_z_defense_factor} spotkań "
            "z wyznaczonym Defense Factor średnia liczba bramek zawodnika zmienia się "
            "wraz z jakością defensywy rywala.",
            f"Przeciw klasie „{pierwsza.klasa}” zawodnik zdobywał średnio "
            f"{self._liczba(pierwsza.srednia)} bramki, a przeciw „{ostatnia.klasa}” "
            f"{self._liczba(ostatnia.srednia)}.",
            f"Różnica wynosi {roznica:+.1f} bramki na mecz.",
            f"Pearson r = {self._liczba(r)} wskazuje na {self._interpretacja_korelacji(r)}.",
        ]
        if rho is not None:
            zdania.append(
                f"Spearman rho = {self._liczba(rho)} pokazuje podobną zależność monotoniczną."
            )
        if beta1 is not None:
            zdania.append(
                f"Regresja liniowa daje β1 = {self._liczba(beta1)}. Wzrost Defense Factor o 0,10 "
                f"odpowiada w modelu zmianie {self._delta_10(beta1)} bramki."
            )
        if r2 is not None:
            zdania.append(
                f"R² = {self._liczba(r2)} oznacza, że jednoczynnikowy model liniowy opisuje "
                f"około {r2 * 100:.0f}% zmienności liczby bramek w analizowanej próbie."
            )
        zdania.append(
            "Nie oznacza to, że jakość defensywy jest jedyną przyczyną wyniku — na liczbę bramek "
            "wpływają także inne czynniki."
        )
        return " ".join(zdania)

    @staticmethod
    def _komentarz_automatyczny(klasy: tuple[StatystykiKlasyDefensywy, ...]) -> str:
        niepuste = [k for k in klasy if k.n > 0 and k.srednia is not None]
        if len(niepuste) < 2:
            return "Za mało danych w kilku klasach defensywy, aby ocenić zależność."
        roznica = niepuste[-1].srednia - niepuste[0].srednia  # type: ignore[operator]
        if roznica > 1.0:
            return (
                f"Zawodnik zdobywa średnio więcej bramek przeciw słabszym defensywom. "
                f"Średnia rośnie z {niepuste[0].srednia:.1f} przeciw „{niepuste[0].klasa}” "
                f"do {niepuste[-1].srednia:.1f} przeciw „{niepuste[-1].klasa}”."
            )
        return (
            "Różnice pomiędzy klasami defensywy są niewielkie. "
            "Dane nie wskazują na wyraźną zależność."
        )

    @staticmethod
    def _liczba(wartosc: int | float | None) -> str:
        if wartosc is None:
            return "—"
        if isinstance(wartosc, float):
            return f"{wartosc:.2f}"
        return str(wartosc)
