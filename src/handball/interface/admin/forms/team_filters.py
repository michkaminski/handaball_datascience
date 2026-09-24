from typing import Any

from wtforms import IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.team_details import (
    FiltryDruzyny,
    FiltryZawodnikowDruzyny,
    FiltryZestawieniaDruzyny,
)

ZAKLADKI_DRUZYNY = (
    ("dane", "Dane podstawowe"),
    ("sezony", "Sezony"),
    ("mecze", "Mecze"),
    ("zawodnicy", "Zawodnicy"),
    ("zestawienie", "Zestawienie sezonu"),
    ("podsumowanie", "Podsumowanie"),
    ("forma", "Forma i regularność"),
)

SORTOWANIA_ZAWODNIKOW = (
    ("-bramki", "Bramki malejąco"),
    ("bramki", "Bramki rosnąco"),
    ("-mecze", "Mecze malejąco"),
    ("mecze", "Mecze rosnąco"),
    ("-srednia", "Średnia malejąco"),
    ("srednia", "Średnia rosnąco"),
    ("nazwisko", "Nazwisko A–Z"),
    ("-nazwisko", "Nazwisko Z–A"),
    ("-ostatni_mecz", "Ostatni mecz: najnowsze"),
    ("ostatni_mecz", "Ostatni mecz: najstarsze"),
)


class DruzynaFilterForm(Form):
    id_sezon = SelectField(choices=[], validators=[validators.Optional()])
    rozgrywki = SelectField(choices=[], validators=[validators.Optional()])
    przeciwnik = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    zawodnik = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    strona = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    rozmiar_strony = IntegerField(default=20, validators=[validators.NumberRange(min=1, max=100)])
    sortowanie = SelectField(choices=[("data", "data"), ("-data", "-data")], default="-data")
    strona_zawodnikow = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    sortowanie_zawodnikow = SelectField(choices=list(SORTOWANIA_ZAWODNIKOW), default="-bramki")
    zakladka = SelectField(choices=list(ZAKLADKI_DRUZYNY), default="dane")
    sezon_zestawienia = SelectField(choices=[], validators=[validators.Optional()])
    rozgrywki_zestawienia = SelectField(choices=[], validators=[validators.Optional()])
    przeciwnik_zestawienia = StringField(
        validators=[validators.Optional(), validators.Length(max=200)]
    )

    def __init__(self, formdata: Any = None, **kwargs: Any) -> None:
        super().__init__(formdata, **kwargs)
        wartosci = formdata.getlist("zakonczone") if formdata is not None else []
        self.tylko_zakonczone = not wartosci or "1" in wartosci

    def do_filtrow(self) -> FiltryDruzyny:
        return FiltryDruzyny(
            id_sezon=int(self.id_sezon.data) if self.id_sezon.data else None,
            rozgrywki=self.rozgrywki.data or None,
            przeciwnik=(self.przeciwnik.data or "").strip() or None,
            strona=self.strona.data if self.strona.data is not None else 1,
            rozmiar_strony=self.rozmiar_strony.data if self.rozmiar_strony.data is not None else 20,
            sortowanie=self.sortowanie.data,
            tylko_zakonczone=self.tylko_zakonczone,
        )

    def do_filtrow_zestawienia(self, domyslny_sezon: int | None) -> FiltryZestawieniaDruzyny | None:
        wybrany = (
            int(self.sezon_zestawienia.data) if self.sezon_zestawienia.data else domyslny_sezon
        )
        if wybrany is None:
            return None
        return FiltryZestawieniaDruzyny(
            id_sezon=wybrany,
            rozgrywki=self.rozgrywki_zestawienia.data or None,
            przeciwnik=(self.przeciwnik_zestawienia.data or "").strip() or None,
        )

    def do_filtrow_zawodnikow(self) -> FiltryZawodnikowDruzyny:
        return FiltryZawodnikowDruzyny(
            id_sezon=int(self.id_sezon.data) if self.id_sezon.data else None,
            rozgrywki=self.rozgrywki.data or None,
            zawodnik=(self.zawodnik.data or "").strip() or None,
            strona=self.strona_zawodnikow.data if self.strona_zawodnikow.data is not None else 1,
            rozmiar_strony=self.rozmiar_strony.data if self.rozmiar_strony.data is not None else 20,
            sortowanie=self.sortowanie_zawodnikow.data,
        )
