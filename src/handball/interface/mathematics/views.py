from __future__ import annotations

from flask import abort, render_template
from flask.views import MethodView

from handball.request_dependencies import ZaleznosciZadaniaFactory

KONTEKST_MENU = {"sekcja_aktywna": "matematyka", "sekcja_glowna": "matematyka"}


class _MatematykaView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._biblioteka = fabryka_zaleznosci.utworz_biblioteke_matematyczna()


class MatematykaIndeksView(_MatematykaView):
    def get(self) -> str:
        rejestr = self._biblioteka.rejestr
        return render_template(
            "mathematics/index.html",
            dzialy=self._biblioteka.dzialy(),
            planowane=rejestr.planned_models,
            rejestr=rejestr,
            **KONTEKST_MENU,
        )


class MatematykaDzialView(_MatematykaView):
    def get(self, dzial: str) -> str:
        wynik = self._biblioteka.dzial(dzial)
        if wynik is None:
            abort(404)
        rejestr = self._biblioteka.rejestr
        return render_template(
            "mathematics/category.html",
            wynik=wynik,
            dzialy=self._biblioteka.dzialy(),
            planowane=[item for item in rejestr.planned_models if item["category"] == dzial],
            rejestr=rejestr,
            **KONTEKST_MENU,
        )


class MatematykaArtykulView(_MatematykaView):
    def get(self, dzial: str, slug: str) -> str:
        strona = self._biblioteka.artykul(dzial, slug)
        if strona is None:
            abort(404)
        return render_template(
            "mathematics/article.html",
            strona=strona,
            dzialy=self._biblioteka.dzialy(),
            rejestr=self._biblioteka.rejestr,
            **KONTEKST_MENU,
        )
