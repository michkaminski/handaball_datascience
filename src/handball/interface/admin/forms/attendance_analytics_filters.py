from wtforms import BooleanField, SelectField, validators
from wtforms.form import Form

from handball.domain.attendance_analytics import FiltryFrekwencji, OpcjeFiltrowFrekwencji
from handball.domain.goal_distribution import DOZWOLONE_PLCI, OpcjaFiltrow

WSZYSTKIE = ("", "Wszystkie")


def _wybory(opcje: tuple[OpcjaFiltrow, ...]) -> list[tuple[str, str]]:
    return [WSZYSTKIE] + [(opcja.wartosc, opcja.etykieta) for opcja in opcje]


class FrekwencjaFilterForm(Form):
    id_sezon = SelectField(choices=[WSZYSTKIE], default="", validators=[validators.Optional()])
    rozgrywki = SelectField(choices=[WSZYSTKIE], default="", validators=[validators.Optional()])
    plec = SelectField(
        choices=[WSZYSTKIE, ("M", "Mężczyźni"), ("K", "Kobiety")],
        default="",
        validators=[validators.Optional()],
    )
    id_zespol = SelectField(choices=[WSZYSTKIE], default="", validators=[validators.Optional()])
    id_hala = SelectField(choices=[WSZYSTKIE], default="", validators=[validators.Optional()])
    bez_zer = BooleanField(default=False)

    def zastosuj_opcje(self, opcje: OpcjeFiltrowFrekwencji) -> None:
        self.id_sezon.choices = _wybory(opcje.sezony)
        self.rozgrywki.choices = _wybory(opcje.rozgrywki)
        self.id_zespol.choices = _wybory(opcje.kluby)
        self.id_hala.choices = _wybory(opcje.hale)

    def do_filtrow(self) -> FiltryFrekwencji:
        plec = (self.plec.data or "").strip() or None
        if plec is not None and plec not in DOZWOLONE_PLCI:
            raise ValueError("nieobsługiwana płeć")
        return FiltryFrekwencji(
            id_sezon=_liczba(self.id_sezon.data),
            rozgrywki=(self.rozgrywki.data or "").strip() or None,
            plec=plec,
            id_zespol=_liczba(self.id_zespol.data),
            id_hala=_liczba(self.id_hala.data),
            bez_zer=bool(self.bez_zer.data),
        )


def _liczba(tekst: str | None) -> int | None:
    return int(tekst) if tekst else None
