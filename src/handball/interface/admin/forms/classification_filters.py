from wtforms import IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.classifications import FiltryKlasyfikacji
from handball.interface.admin.forms.catalog_filters import opcjonalny_int


class KlasyfikacjaFilterForm(Form):
    szukaj = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    id_sezon = SelectField(coerce=opcjonalny_int, validators=[validators.Optional()])
    id_rozgrywki = SelectField(coerce=opcjonalny_int, validators=[validators.Optional()])
    strona = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    rozmiar_strony = IntegerField(default=20, validators=[validators.NumberRange(min=1, max=100)])
    sortowanie = SelectField()

    def do_filtrow(self) -> FiltryKlasyfikacji:
        return FiltryKlasyfikacji(
            szukaj=(self.szukaj.data or "").strip() or None,
            id_sezon=self.id_sezon.data,
            id_rozgrywki=self.id_rozgrywki.data,
            strona=self.strona.data or 1,
            rozmiar_strony=self.rozmiar_strony.data or 20,
            sortowanie=self.sortowanie.data,
        )
