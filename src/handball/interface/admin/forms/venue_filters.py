from wtforms import IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.catalogs import FiltryKatalogu


class HalaFilterForm(Form):
    szukaj = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    miasto = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    pojemnosc_min = IntegerField(validators=[validators.Optional(), validators.NumberRange(min=0)])
    strona = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    rozmiar_strony = IntegerField(default=20, validators=[validators.NumberRange(min=1, max=100)])
    sortowanie = SelectField(
        choices=[
            (kierunek + pole, kierunek + pole)
            for pole in ("id", "nazwa", "miasto", "adres", "pojemnosc", "liczba_meczow")
            for kierunek in ("", "-")
        ],
        default="nazwa",
    )

    def do_filtrow(self) -> FiltryKatalogu:
        return FiltryKatalogu(
            szukaj=(self.szukaj.data or "").strip() or None,
            miasto=(self.miasto.data or "").strip() or None,
            pojemnosc_min=self.pojemnosc_min.data,
            strona=self.strona.data if self.strona.data is not None else 1,
            rozmiar_strony=(
                self.rozmiar_strony.data if self.rozmiar_strony.data is not None else 20
            ),
            sortowanie=self.sortowanie.data,
        )
