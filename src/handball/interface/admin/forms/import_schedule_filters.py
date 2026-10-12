from wtforms import BooleanField, SelectMultipleField, validators

from handball.domain.competition_levels import GrupaRozgrywek
from handball.domain.schedule import KryteriaPobierania
from handball.interface.admin.forms.schedule_filters import TerminarzFilterForm

GRUPY_POZIOMU = (
    (GrupaRozgrywek.SUPERLIGA, "Superligi"),
    (GrupaRozgrywek.LIGA_CENTRALNA, "Ligi centralne"),
    (GrupaRozgrywek.I_LIGA, "I ligi"),
    (GrupaRozgrywek.II_LIGA, "II ligi"),
    (GrupaRozgrywek.PUCHAR_POLSKI, "Puchary Polski"),
)


class PobieranieMeczowFilterForm(TerminarzFilterForm):
    wynik_bez_danych = BooleanField()
    kolejki_zakonczone = BooleanField()
    bez_wynikow = BooleanField()
    grupa = SelectMultipleField(
        choices=[(grupa.value, etykieta) for grupa, etykieta in GRUPY_POZIOMU],
        validators=[validators.Optional()],
    )

    def grupy(self) -> frozenset[GrupaRozgrywek]:
        return frozenset(GrupaRozgrywek(wartosc) for wartosc in self.grupa.data or ())

    def do_kryteriow(self) -> KryteriaPobierania:
        return KryteriaPobierania(
            self.do_wyboru(),
            wynik_bez_danych=bool(self.wynik_bez_danych.data),
            kolejki_zakonczone=bool(self.kolejki_zakonczone.data),
            bez_wynikow=bool(self.bez_wynikow.data),
            grupy=self.grupy(),
        )
