from wtforms import SelectField, validators
from wtforms.form import Form

from handball.domain.goal_distribution import DOZWOLONE_PLCI, FiltryRozkladuBramek


class RozkladBramekFilterForm(Form):
    id_sezon = SelectField(
        choices=[("", "Wszystkie")],
        default="",
        validators=[validators.Optional()],
    )
    rozgrywki = SelectField(
        choices=[("", "Wszystkie")],
        default="",
        validators=[validators.Optional()],
    )
    plec = SelectField(
        choices=[
            ("", "Wszystkie"),
            ("M", "Mężczyźni"),
            ("K", "Kobiety"),
        ],
        validators=[validators.Optional()],
    )

    def do_filtrow(self) -> FiltryRozkladuBramek:
        plec = (self.plec.data or "").strip() or None
        if plec is not None and plec not in DOZWOLONE_PLCI:
            raise ValueError("nieobsługiwana płeć")
        return FiltryRozkladuBramek(
            id_sezon=int(self.id_sezon.data) if self.id_sezon.data else None,
            rozgrywki=(self.rozgrywki.data or "").strip() or None,
            plec=plec,
        )
