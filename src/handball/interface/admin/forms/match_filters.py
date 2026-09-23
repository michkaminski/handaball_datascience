from __future__ import annotations

from typing import Any

from wtforms import IntegerField, SelectField, StringField, ValidationError, validators
from wtforms.form import Form

from handball.domain.matches import FiltryMeczow, zakres_z_czesciowej_daty


def _waliduj_czesciowa_date(_formularz: Form, pole: StringField) -> None:
    if not pole.data:
        return
    try:
        zakres_z_czesciowej_daty(pole.data)
    except ValueError as wyjatek:
        raise ValidationError(
            "Podaj rok (2026), rok i miesiąc (2026-01) albo pełną datę (2026-01-15)."
        ) from wyjatek


class MeczFilterForm(Form):
    id_sezon = SelectField(choices=[], validators=[validators.Optional()])
    rozgrywki = SelectField(choices=[], validators=[validators.Optional()])
    runda = SelectField(choices=[], validators=[validators.Optional()])
    kolejka = SelectField(choices=[], validators=[validators.Optional()])
    id_hala = SelectField(choices=[], validators=[validators.Optional()])
    druzyna = StringField(validators=[validators.Optional()])
    data_meczu = StringField(validators=[validators.Optional(), _waliduj_czesciowa_date])
    strona = IntegerField(default=1, validators=[validators.Optional()])
    rozmiar_strony = IntegerField(default=20, validators=[validators.Optional()])
    sortowanie = SelectField(
        choices=[("data", "data"), ("-data", "-data")],
        default="data",
        validators=[validators.Optional()],
    )

    def __init__(self, formdata: Any = None, **kwargs: Any) -> None:
        super().__init__(formdata, **kwargs)
        wartosci = formdata.getlist("zakonczone") if formdata is not None else []
        self.tylko_zakonczone = not wartosci or "1" in wartosci

    def do_filtrow(self) -> FiltryMeczow:
        data_od = data_do = None
        if self.data_meczu.data:
            data_od, data_do = zakres_z_czesciowej_daty(self.data_meczu.data)

        return FiltryMeczow(
            id_sezon=int(self.id_sezon.data) if self.id_sezon.data else None,
            rozgrywki=self.rozgrywki.data or None,
            runda=self.runda.data or None,
            kolejka=self.kolejka.data or None,
            id_hala=int(self.id_hala.data) if self.id_hala.data else None,
            szukaj_druzyny=self.druzyna.data or None,
            data_od=data_od,
            data_do=data_do,
            strona=self.strona.data or 1,
            rozmiar_strony=self.rozmiar_strony.data or 20,
            sortowanie=self.sortowanie.data or "data",
            tylko_zakonczone=self.tylko_zakonczone,
        )
