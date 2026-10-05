from wtforms import BooleanField, IntegerField, SelectField, validators
from wtforms.form import Form

from handball.domain.match_preview import OpcjeZapowiedzi
from handball.domain.match_protocol import KolejnoscProtokolu
from handball.domain.schedule import WyborTerminarza

LATA_BEZPOSREDNICH = (5, 10, 15, 20)
WSZYSTKIE_LATA = "wszystkie"


class TerminarzFilterForm(Form):
    id_sezon = IntegerField(validators=[validators.Optional()])
    id_rozgrywki = IntegerField(validators=[validators.Optional()])
    id_runda = IntegerField(validators=[validators.Optional()])
    id_kolejka = IntegerField(validators=[validators.Optional()])

    def do_wyboru(self) -> WyborTerminarza:
        return WyborTerminarza(
            id_sezon=self.id_sezon.data,
            id_rozgrywki=self.id_rozgrywki.data,
            id_runda=self.id_runda.data,
            id_kolejka=self.id_kolejka.data,
        )


class ZapowiedzOpcjeForm(Form):
    kadra_poprzedni = BooleanField()
    bez_uwag = BooleanField()
    lata = SelectField(
        choices=[(str(n), f"{n} lat") for n in LATA_BEZPOSREDNICH]
        + [(WSZYSTKIE_LATA, "Wszystkie")],
        default="10",
        validators=[validators.Optional()],
    )
    kolejnosc_protokolu = SelectField(
        choices=[
            (KolejnoscProtokolu.POZYCJE.value, "pozycja, numer"),
            (KolejnoscProtokolu.NUMERY.value, "według numerów"),
        ],
        default=KolejnoscProtokolu.POZYCJE.value,
        validators=[validators.Optional()],
    )

    def do_opcji(self) -> OpcjeZapowiedzi:
        lata = self.lata.data or self.lata.default
        return OpcjeZapowiedzi(
            kadra_z_poprzedniego_sezonu=bool(self.kadra_poprzedni.data),
            lata_bezposrednich=None if lata == WSZYSTKIE_LATA else int(str(lata)),
        )

    def do_kolejnosci_protokolu(self) -> KolejnoscProtokolu:
        return KolejnoscProtokolu(
            str(self.kolejnosc_protokolu.data or self.kolejnosc_protokolu.default)
        )
