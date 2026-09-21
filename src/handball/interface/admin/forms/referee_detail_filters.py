from datetime import datetime

from wtforms import DateField, IntegerField, SelectField, StringField, validators
from wtforms.form import Form

from handball.domain.referee_details import FiltryMeczowSedziego


class MeczeSedziegoFilterForm(Form):
    sezon = SelectField(choices=[], validators=[validators.Optional()])
    rozgrywki = SelectField(choices=[], validators=[validators.Optional()])
    druzyna = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    strona_meczu = SelectField(
        choices=[("", "Wszystkie"), ("gospodarz", "Gospodarz"), ("gosc", "Gość")],
        validators=[validators.Optional()],
    )
    data_od = DateField(validators=[validators.Optional()])
    data_do = DateField(validators=[validators.Optional()])
    strona = IntegerField(default=1, validators=[validators.NumberRange(min=1)])
    rozmiar = IntegerField(default=20, validators=[validators.NumberRange(min=1, max=100)])
    sortowanie = SelectField(choices=[("data", "data"), ("-data", "-data")], default="-data")

    def do_filtrow(self) -> FiltryMeczowSedziego:
        return FiltryMeczowSedziego(
            id_sezon=int(self.sezon.data) if self.sezon.data else None,
            rozgrywki=self.rozgrywki.data or None,
            druzyna=(self.druzyna.data or "").strip() or None,
            strona_meczu=self.strona_meczu.data or None,
            data_od=datetime.combine(self.data_od.data, datetime.min.time())
            if self.data_od.data
            else None,
            data_do=datetime.combine(self.data_do.data, datetime.max.time())
            if self.data_do.data
            else None,
            strona=self.strona.data or 1,
            rozmiar_strony=self.rozmiar.data or 20,
            sortowanie=self.sortowanie.data,
        )
