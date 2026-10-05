from __future__ import annotations

from typing import Protocol

from handball.domain.match_protocol import DaneProtokolu


class ProtokolMeczuReadRepository(Protocol):
    def pobierz_dane_protokolu(self, id_mecz: int) -> DaneProtokolu: ...
