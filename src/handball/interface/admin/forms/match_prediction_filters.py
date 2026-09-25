from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    validators,
)
from wtforms.form import Form

from handball.domain.match_predictions import (
    FiltryPrognoz,
    KlasaTrafnosci,
    KlasaWyniku,
    Plec,
    PoziomRozgrywek,
    Typ1X2,
    ZakresBacktestu,
)

ROZMIARY_STRONY = (50, 100, 250, 500)
LICZBY_SEZONOW_RAPORTU = (3, 5, 10, 15)
WSZYSTKIE_SEZONY = "wszystkie"


class ZakresRaportuForm(Form):
    sezony_raportu = SelectField(
        choices=[(str(n), str(n)) for n in LICZBY_SEZONOW_RAPORTU]
        + [(WSZYSTKIE_SEZONY, "Wszystkie")],
        default=str(ZakresBacktestu().docelowa_liczba_sezonow_raportu),
        validators=[validators.Optional()],
    )

    def do_zakresu(self) -> ZakresBacktestu:
        wartosc = str(self.sezony_raportu.data or self.sezony_raportu.default)
        if wartosc == WSZYSTKIE_SEZONY:
            return ZakresBacktestu(None)
        return ZakresBacktestu(int(wartosc))


class PrognozyMeczowFilterForm(ZakresRaportuForm):
    model = SelectField(choices=[], validators=[validators.Optional()])
    poziom = SelectField(choices=[], validators=[validators.Optional()])
    plec = SelectField(choices=[], validators=[validators.Optional()])
    sezon = SelectField(choices=[], validate_choice=False, validators=[validators.Optional()])
    druzyna = StringField(validators=[validators.Optional(), validators.Length(max=200)])
    trafnosc = SelectField(
        choices=[("", "Wszystkie"), ("trafione", "TAK"), ("nietrafione", "NIE")],
        validators=[validators.Optional()],
    )
    typ_prognozy = SelectMultipleField(
        choices=[("poprawny", "Poprawny"), ("nieprzewidziany", "Nieprzewidziany")],
        validators=[validators.Optional()],
    )
    wynik_1x2 = SelectMultipleField(
        choices=[(typ.value, typ.value) for typ in Typ1X2], validators=[validators.Optional()]
    )
    dokladny_wynik = BooleanField()
    poprawna_roznica = BooleanField()
    ocena = SelectMultipleField(choices=[], validators=[validators.Optional()])
    ocena_wyniku = SelectMultipleField(choices=[], validators=[validators.Optional()])
    strona = IntegerField(
        default=1, validators=[validators.Optional(), validators.NumberRange(min=1)]
    )
    rozmiar = SelectField(
        choices=[(str(r), str(r)) for r in ROZMIARY_STRONY],
        default="100",
        validators=[validators.Optional()],
    )

    def do_filtrow(self, domyslny_model: str) -> FiltryPrognoz:
        return FiltryPrognoz(
            wersja_modelu=self.model.data or domyslny_model,
            poziom=PoziomRozgrywek(self.poziom.data) if self.poziom.data else None,
            plec=Plec(self.plec.data) if self.plec.data else None,
            id_sezon=self._identyfikator_sezonu(),
            druzyna=(self.druzyna.data or "").strip() or None,
            trafiony={"trafione": True, "nietrafione": False}.get(self.trafnosc.data or ""),
            klasy=frozenset(KlasaTrafnosci(wartosc) for wartosc in self.ocena.data or ()),
            klasy_wyniku=frozenset(
                KlasaWyniku(wartosc) for wartosc in self.ocena_wyniku.data or ()
            ),
            tylko_dokladny_wynik=bool(self.dokladny_wynik.data),
            tylko_poprawna_roznica=bool(self.poprawna_roznica.data),
            poprawny_typ_prognozy=self._poprawny_typ_prognozy(),
            typy_wyniku=frozenset(Typ1X2(wartosc) for wartosc in self.wynik_1x2.data or ()),
            strona=self.strona.data or 1,
            rozmiar_strony=int(self.rozmiar.data or 100),
            zakres=self.do_zakresu(),
        )

    def _poprawny_typ_prognozy(self) -> bool | None:
        wybrane = set(self.typ_prognozy.data or ())
        if len(wybrane) != 1:
            return None
        return wybrane == {"poprawny"}

    def _identyfikator_sezonu(self) -> int | None:
        if not self.sezon.data:
            return None
        if not str(self.sezon.data).isdigit():
            raise ValueError("Niepoprawny sezon.")
        return int(self.sezon.data)
