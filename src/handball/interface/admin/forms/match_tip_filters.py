from typing import cast

from wtforms import DateField, IntegerField, SelectMultipleField, StringField, validators
from wtforms.form import Form

from handball.domain.match_tips import WyborTypowan
from handball.domain.schedule import FiltryTerminarza


class TypowaniaFilterForm(Form):
    data_od = DateField(validators=[validators.Optional()])
    data_do = DateField(validators=[validators.Optional()])
    rozgrywki = SelectMultipleField(
        choices=[], validate_choice=False, validators=[validators.Optional()]
    )
    model = StringField(validators=[validators.Optional(), validators.Length(max=100)])

    def do_wyboru(self) -> WyborTypowan:
        return WyborTypowan(
            data_od=self.data_od.data,
            data_do=self.data_do.data,
            rozgrywki=frozenset(
                nazwa.strip() for nazwa in self.rozgrywki.data or () if nazwa.strip()
            ),
            wersja_modelu=(self.model.data or "").strip() or None,
        )


class TypowaniaKolejkiForm(Form):
    id_sezon = IntegerField(validators=[validators.InputRequired()])
    id_rozgrywki = IntegerField(validators=[validators.InputRequired()])
    id_kolejka = IntegerField(validators=[validators.InputRequired()])
    model = StringField(validators=[validators.Optional(), validators.Length(max=100)])

    def do_filtrow(self) -> FiltryTerminarza:
        return FiltryTerminarza(
            id_sezon=cast(int, self.id_sezon.data),
            id_rozgrywki=cast(int, self.id_rozgrywki.data),
            id_kolejka=self.id_kolejka.data,
        )
