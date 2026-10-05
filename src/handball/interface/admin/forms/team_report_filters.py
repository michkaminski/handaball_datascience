from wtforms import IntegerField, validators
from wtforms.form import Form

from handball.domain.team_report import DOMYSLNA_LICZBA_MECZOW

NAJMNIEJ_MECZOW = 5
NAJWIECEJ_MECZOW = 30


class RaportDruzynyForm(Form):
    id_sezon = IntegerField(validators=[validators.InputRequired(), validators.NumberRange(min=1)])
    mecze = IntegerField(
        default=DOMYSLNA_LICZBA_MECZOW,
        validators=[
            validators.Optional(),
            validators.NumberRange(min=NAJMNIEJ_MECZOW, max=NAJWIECEJ_MECZOW),
        ],
    )

    def do_sezonu(self) -> int:
        return int(self.id_sezon.data or 0)

    def do_liczby_meczow(self) -> int:
        return int(self.mecze.data or DOMYSLNA_LICZBA_MECZOW)
