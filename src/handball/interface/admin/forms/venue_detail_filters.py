from wtforms import IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.venue_details import FiltryMeczowHali, FiltryZawodnikowHali


class MeczeHaliFilterForm(Form):
    m_sezon = SelectField(choices=[], validators=[validators.Optional()])
    m_rozgrywki = SelectField(choices=[], validators=[validators.Optional()])
    m_druzyna = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    m_strona = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    m_rozmiar = IntegerField(default=20, validators=[validators.NumberRange(min=1, max=100)])
    m_sortowanie = SelectField(
        choices=[("data", "data"), ("-data", "-data")],
        default="-data",
    )

    def do_filtrow(self) -> FiltryMeczowHali:
        return FiltryMeczowHali(
            id_sezon=int(self.m_sezon.data) if self.m_sezon.data else None,
            rozgrywki=self.m_rozgrywki.data or None,
            druzyna=(self.m_druzyna.data or "").strip() or None,
            strona=self.m_strona.data or 1,
            rozmiar_strony=self.m_rozmiar.data or 20,
            sortowanie=self.m_sortowanie.data,
        )


class ZawodnicyHaliFilterForm(Form):
    z_szukaj = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    z_strona = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    z_rozmiar = IntegerField(default=20, validators=[validators.NumberRange(min=1, max=100)])
    z_sortowanie = SelectField(
        choices=[
            (kierunek + pole, kierunek + pole)
            for pole in (
                "nazwisko",
                "pierwszy_wystep",
                "ostatni_wystep",
                "wystepy",
                "bramki",
                "srednia_bramek",
            )
            for kierunek in ("", "-")
        ],
        default="-wystepy",
    )

    def do_filtrow(self) -> FiltryZawodnikowHali:
        return FiltryZawodnikowHali(
            szukaj=(self.z_szukaj.data or "").strip() or None,
            strona=self.z_strona.data or 1,
            rozmiar_strony=self.z_rozmiar.data or 20,
            sortowanie=self.z_sortowanie.data,
        )
