from wtforms import IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.player_details import FiltryMeczowZawodnika


class MeczeZawodnikaFilterForm(Form):
    id_sezon = SelectField(choices=[], validators=[validators.Optional()])
    rozgrywki = SelectField(choices=[], validators=[validators.Optional()])
    przeciwnik = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    strona = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    rozmiar_strony = IntegerField(default=20, validators=[validators.NumberRange(min=1, max=100)])
    sortowanie = SelectField(choices=[("data", "data"), ("-data", "-data")], default="-data")
    zakladka = SelectField(
        choices=[
            ("profil", "Profil"),
            ("sezony", "Sezony i drużyny"),
            ("mecze", "Mecze"),
            ("podsumowanie", "Podsumowanie"),
            ("forma", "Forma i regularność"),
        ],
        default="profil",
    )

    def do_filtrow(self) -> FiltryMeczowZawodnika:
        return FiltryMeczowZawodnika(
            id_sezon=int(self.id_sezon.data) if self.id_sezon.data else None,
            rozgrywki=self.rozgrywki.data or None,
            przeciwnik=(self.przeciwnik.data or "").strip() or None,
            strona=self.strona.data if self.strona.data is not None else 1,
            rozmiar_strony=self.rozmiar_strony.data if self.rozmiar_strony.data is not None else 20,
            sortowanie=self.sortowanie.data,
        )
