from wtforms import BooleanField

from handball.interface.admin.forms.schedule_filters import TerminarzFilterForm


class PobieranieMeczowFilterForm(TerminarzFilterForm):
    wynik_bez_danych = BooleanField()
    kolejki_zakonczone = BooleanField()
