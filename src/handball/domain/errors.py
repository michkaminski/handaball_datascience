from __future__ import annotations


class NieZnalezionoMeczu(Exception):
    pass


class BladOdczytuDanych(Exception):
    pass


class NieZnalezionoZawodnika(Exception):
    pass


class NieZnalezionoHali(Exception):
    pass


class NieZnalezionoSedziego(Exception):
    pass


class NieZnalezionoDruzyny(Exception):
    pass


class NieZnalezionoPrognozy(Exception):
    pass


class NieznanyModelPrognoz(ValueError):
    pass
