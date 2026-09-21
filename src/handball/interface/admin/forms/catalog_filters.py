from wtforms import IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.catalogs import FiltryKatalogu


def opcjonalny_int(wartosc: object) -> int | None:
    return int(str(wartosc)) if wartosc not in {None, ""} else None


class KatalogFilterForm(Form):
    szukaj = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    id_sezon = SelectField(coerce=opcjonalny_int, validators=[validators.Optional()])
    plec = SelectField(
        choices=[("", "Wszystkie"), ("K", "Kobiety"), ("M", "Mężczyźni")], default=""
    )
    stan = StringField(validators=[validators.Optional(), validators.Length(max=100)])
    miasto = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    wycofany = SelectField(
        choices=[("", "Wszystkie"), ("0", "Aktywne"), ("1", "Wycofane")], default=""
    )
    strona = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    rozmiar_strony = IntegerField(default=20, validators=[validators.NumberRange(min=1, max=100)])
    sortowanie = SelectField()

    def do_filtrow(self) -> FiltryKatalogu:
        return FiltryKatalogu(
            szukaj=(self.szukaj.data or "").strip() or None,
            id_sezon=self.id_sezon.data,
            plec=self.plec.data or None,
            stan=(self.stan.data or "").strip() or None,
            miasto=(self.miasto.data or "").strip() or None,
            wycofany=self._wycofany(),
            strona=self.strona.data or 1,
            rozmiar_strony=self.rozmiar_strony.data or 20,
            sortowanie=self.sortowanie.data,
        )

    def _wycofany(self) -> bool | None:
        if self.wycofany.data == "1":
            return True
        if self.wycofany.data == "0":
            return False
        return None
