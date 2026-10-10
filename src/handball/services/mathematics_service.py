from __future__ import annotations

from dataclasses import dataclass

from mathlib.registry import Category, Concept, MathRegistry
from mathlib.render import ArticleRenderer, RenderedArticle


@dataclass(frozen=True)
class DzialMatematyki:
    dzial: Category
    artykuly: tuple[Concept, ...]


@dataclass(frozen=True)
class StronaArtykulu:
    artykul: RenderedArticle
    dzial: Category
    poprzedni: Concept | None
    nastepny: Concept | None
    powiazane: tuple[Concept, ...]
    uzywane_przez: tuple[str, ...]


class BibliotekaMatematycznaService:
    def __init__(self, rejestr: MathRegistry) -> None:
        self._rejestr = rejestr
        self._renderer = ArticleRenderer(rejestr)

    @property
    def rejestr(self) -> MathRegistry:
        return self._rejestr

    def dzialy(self) -> tuple[DzialMatematyki, ...]:
        return tuple(
            DzialMatematyki(dzial, tuple(self._rejestr.articles(dzial.id)))
            for dzial in self._rejestr.categories
        )

    def dzial(self, identyfikator: str) -> DzialMatematyki | None:
        dzial = self._rejestr.category(identyfikator)
        if dzial is None:
            return None
        return DzialMatematyki(dzial, tuple(self._rejestr.articles(dzial.id)))

    def artykul(self, identyfikator_dzialu: str, slug: str) -> StronaArtykulu | None:
        pojecie = self._rejestr.concepts.get(slug)
        if pojecie is None or pojecie.is_alias or pojecie.category != identyfikator_dzialu:
            return None
        dzial = self._rejestr.category(identyfikator_dzialu)
        if dzial is None or not self._rejestr.article_path(pojecie).exists():
            return None
        lista = self._rejestr.articles(identyfikator_dzialu)
        pozycja = lista.index(pojecie)
        return StronaArtykulu(
            artykul=self._renderer.render(pojecie),
            dzial=dzial,
            poprzedni=lista[pozycja - 1] if pozycja > 0 else None,
            nastepny=lista[pozycja + 1] if pozycja + 1 < len(lista) else None,
            powiazane=tuple(
                self._rejestr.concepts[item]
                for item in pojecie.related
                if item in self._rejestr.concepts
            ),
            uzywane_przez=pojecie.models,
        )

    def odnosniki(self, identyfikatory: tuple[str, ...]) -> dict[str, dict[str, object]]:
        wynik: dict[str, dict[str, object]] = {}
        for identyfikator in identyfikatory:
            pojecie = self._rejestr.concepts[identyfikator]
            wynik[identyfikator] = {
                "nazwa": pojecie.name,
                "opis": pojecie.summary,
                "url": self._rejestr.url(identyfikator),
                "kotwice": {
                    "definicja": self._rejestr.url(identyfikator, "definicja"),
                    "wzor": self._rejestr.url(identyfikator, "wzor"),
                    "wyprowadzenie": self._rejestr.url(identyfikator, "wyprowadzenie"),
                    "przyklad": self._rejestr.url(identyfikator, "przyklad"),
                },
            }
        return wynik
