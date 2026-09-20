from wtforms import IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.players import FiltryZawodnikow


class ZawodnikFilterForm(Form):
    id_sezon = SelectField(choices=[], validators=[validators.Optional()])
    rozgrywki = SelectField(choices=[], validators=[validators.Optional()])
    druzyna = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    pozycja = SelectField(choices=[], validators=[validators.Optional()])
    rocznik = IntegerField(
        validators=[validators.Optional(), validators.NumberRange(min=1, max=9999)]
    )
    szukaj = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    strona = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    rozmiar_strony = IntegerField(default=20, validators=[validators.NumberRange(min=1, max=100)])
    sortowanie = SelectField(
        choices=[
            (kierunek + pole, kierunek + pole)
            for pole in (
                "id",
                "imie",
                "nazwisko",
                "rocznik",
                "wzrost",
                "waga",
                "mecze",
                "bramki",
            )
            for kierunek in ("", "-")
        ],
        default="nazwisko",
    )

    def do_filtrow(self) -> FiltryZawodnikow:
        return FiltryZawodnikow(
            id_sezon=int(self.id_sezon.data) if self.id_sezon.data else None,
            rozgrywki=self.rozgrywki.data or None,
            druzyna=(self.druzyna.data or "").strip() or None,
            pozycja=self.pozycja.data or None,
            rocznik=self.rocznik.data,
            szukaj=(self.szukaj.data or "").strip() or None,
            strona=self.strona.data if self.strona.data is not None else 1,
            rozmiar_strony=self.rozmiar_strony.data if self.rozmiar_strony.data is not None else 20,
            sortowanie=(
                "nazwisko"
                if self.sortowanie.data.lstrip("-") in {"mecze", "bramki"}
                else self.sortowanie.data
            ),
        )
