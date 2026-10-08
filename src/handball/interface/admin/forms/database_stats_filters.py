from wtforms import IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.database_stats import DOMYSLNE_SORTOWANIE, FiltryStatystykBazy


def opcjonalny_int(wartosc: object) -> int | None:
    return int(str(wartosc)) if wartosc not in {None, ""} else None


class StatystykiBazyFilterForm(Form):
    szukaj = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    schemat = SelectField(validators=[validators.Optional()])
    zapelnienie = SelectField(
        choices=[
            ("", "Wszystkie"),
            ("niepuste", "Tylko z danymi"),
            ("puste", "Tylko puste"),
        ],
        default="",
    )
    min_rekordow = IntegerField(validators=[validators.Optional(), validators.NumberRange(min=0)])
    sortowanie = SelectField()

    def do_filtrow(self) -> FiltryStatystykBazy:
        return FiltryStatystykBazy(
            szukaj=(self.szukaj.data or "").strip() or None,
            schemat=(self.schemat.data or "").strip() or None,
            zapelnienie=(self.zapelnienie.data or "").strip() or None,
            min_rekordow=opcjonalny_int(self.min_rekordow.data),
            sortowanie=self.sortowanie.data or DOMYSLNE_SORTOWANIE,
        )
