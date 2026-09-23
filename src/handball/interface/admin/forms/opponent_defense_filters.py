from wtforms import BooleanField, IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.opponent_defense import FiltryDefensywyRywala


class DefensywaRywalaFilterForm(Form):
    id_sezon = SelectField(choices=[], validators=[validators.Optional()])
    rozgrywki = SelectField(choices=[], validators=[validators.Optional()])
    miejsce = SelectField(
        choices=[("", "Wszystkie"), ("dom", "U siebie"), ("wyjazd", "Na wyjeździe")],
        validators=[validators.Optional()],
    )
    liczba_ostatnich_sezonow = IntegerField(
        validators=[validators.Optional(), validators.NumberRange(min=1)]
    )
    przeciwnik = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    wszystkie_mecze = BooleanField()
    id_mecz_przykladu = IntegerField(validators=[validators.Optional()])

    def do_filtrow(self) -> FiltryDefensywyRywala:
        return FiltryDefensywyRywala(
            id_sezon=int(self.id_sezon.data) if self.id_sezon.data else None,
            rozgrywki=self.rozgrywki.data or None,
            liczba_ostatnich_sezonow=self.liczba_ostatnich_sezonow.data,
            miejsce=self.miejsce.data or None,
            tylko_pelne_dane=not self.wszystkie_mecze.data,
            przeciwnik=(self.przeciwnik.data or "").strip() or None,
        )
