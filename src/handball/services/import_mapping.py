from __future__ import annotations

from datetime import datetime
from typing import Any

from handball.domain.imports import (
    SEZON_IMPORTU,
    BladImportu,
    PrzebiegImportu,
    RekordImportu,
    ZadaniePobrania,
)


class ZprpImportMapper:
    def __init__(self, przebieg: PrzebiegImportu, zrodlo: str) -> None:
        self._przebieg = przebieg
        self._zrodlo = zrodlo

    def wiersze(self, dane: Any) -> list[tuple[str, dict[str, Any]]]:
        if isinstance(dane, list):
            wynik = [(str(i), r) for i, r in enumerate(dane)]
        elif isinstance(dane, dict):
            wynik = list(dane.items())
        else:
            raise BladImportu("Nieprawidłowa struktura odpowiedzi API.")
        if any(not isinstance(r, dict) for _, r in wynik):
            raise BladImportu("Nieprawidłowy rekord w odpowiedzi API.")
        return wynik

    def liczba(self, wartosc: Any, wymagane: bool = False) -> int | None:
        if wartosc in (None, "", {}, []):
            if wymagane:
                raise BladImportu("API nie podało wymaganego identyfikatora.")
            return None
        try:
            wynik = int(str(wartosc))
        except ValueError as blad:
            raise BladImportu("Nieprawidłowa liczba w API; zapis został wstrzymany.") from blad
        if wymagane and wynik <= 0:
            raise BladImportu("Nieprawidłowy identyfikator w API.")
        return wynik

    def ident(self, wartosc: Any) -> int:
        wynik = self.liczba(wartosc, True)
        assert wynik is not None
        return wynik

    def pola(
        self,
        dane: dict[str, Any],
        teksty: dict[str, str] | None = None,
        liczby: dict[str, str] | None = None,
        flagi: dict[str, str] | None = None,
        daty: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        wynik: dict[str, Any] = {}
        for kolumna, pole in (teksty or {}).items():
            if pole in dane:
                wartosc = dane[pole]
                if wartosc in (None, "", {}, []):
                    wynik[kolumna] = None
                elif isinstance(wartosc, (str, int)):
                    wynik[kolumna] = str(wartosc)
                else:
                    raise BladImportu(f"Nieprawidłowy tekst w polu {pole}.")
        for kolumna, pole in (liczby or {}).items():
            if pole in dane:
                wynik[kolumna] = self.liczba(dane[pole])
        for kolumna, pole in (flagi or {}).items():
            if pole in dane:
                if dane[pole] in (None, "", {}, []):
                    wynik[kolumna] = None
                elif str(dane[pole]).lower() in ("0", "1", "true", "false"):
                    wynik[kolumna] = str(dane[pole]).lower() in ("1", "true")
                else:
                    raise BladImportu(f"Nieprawidłowa flaga {pole}.")
        for kolumna, pole in (daty or {}).items():
            if pole in dane:
                if dane[pole] in (None, "", {}, []):
                    wynik[kolumna] = None
                else:
                    try:
                        wynik[kolumna] = datetime.fromisoformat(str(dane[pole])).isoformat()
                    except ValueError:
                        wynik[kolumna] = None
        return wynik

    def dodaj(
        self, tabela: str, klucz: dict[str, Any], dane: dict[str, Any], uzupelnij: bool = False
    ) -> None:
        uzupelnij = uzupelnij or self._przebieg.tryb == "uzupelniajacy"
        for rekord in self._przebieg.rekordy:
            if rekord.tabela == tabela and rekord.klucz == klucz:
                rekord.dane.update(dane)
                if self._zrodlo not in rekord.zrodla:
                    rekord.zrodla.append(self._zrodlo)
                rekord.zrodlo = self._zrodlo
                return
        self._przebieg.rekordy.append(
            RekordImportu(tabela, klucz, {**klucz, **dane}, self._zrodlo, uzupelnij, [self._zrodlo])
        )

    def zlec(self, endpoint: str, rodzaj: str, parametry: dict[str, int], **kontekst: int) -> None:
        zadanie = ZadaniePobrania(endpoint, parametry, rodzaj, kontekst)
        if zadanie not in self._przebieg.kolejka:
            self._przebieg.kolejka.append(zadanie)

    def przetworz(self, zadanie: ZadaniePobrania, dokument: Any) -> None:
        if zadanie.rodzaj == "szczegoly":
            self.szczegoly(dokument, zadanie.kontekst)
            return
        if zadanie.rodzaj == "sklad":
            self.sklad(dokument, zadanie.kontekst)
            return
        if zadanie.rodzaj in ("tabele_spis", "tabela") and dokument in (None, [], {}):
            return
        if zadanie.rodzaj == "tabele_spis":
            self.tabele_spis(dokument, zadanie.kontekst["cid"])
            return
        if zadanie.rodzaj == "tabela":
            self.tabela(dokument, zadanie.kontekst)
            return
        wiersze = self.wiersze(dokument)
        if not wiersze:
            if zadanie.rodzaj == "mecze":
                return
            raise BladImportu(f"Pusta odpowiedź {zadanie.endpoint}; ponów pobranie później.")
        if zadanie.rodzaj == "sezony":
            sezon = next((r for _, r in wiersze if self.ident(r.get("ID_sezon")) == 195), None)
            if sezon is None or sezon.get("Nazwa") != "2026/2027":
                raise BladImportu("API nie potwierdza sezonu 2026/2027 (195).")
            self.dodaj(
                "sezony",
                {"id": 195},
                self.pola(
                    sezon,
                    {"nazwa": "Nazwa", "stan": "Stan"},
                    {"rok_rozpoczecia": "Rok_rozpoczecia", "ile_rozgrywek": "IleRozgrywek"},
                ),
            )
        elif zadanie.rodzaj == "rozgrywki":
            znalezione = set()
            for _, r in wiersze:
                cid = self.ident(r.get("Id_rozgrywki"))
                if cid not in self._przebieg.ligi:
                    continue
                if self.ident(r.get("ID_sezon")) != 195 or str(r.get("Kategoria")) != "1":
                    raise BladImportu("Rozgrywki spoza wybranego sezonu lub kategorii seniorów.")
                znalezione.add(cid)
                dane = self.pola(r, {"nazwa": "Nazwa", "plec": "Plec", "code": "code"})
                dane.update(id_sezon=195, kategoria=1)
                self.dodaj("rozgrywki", {"id": cid}, dane)
                self.zlec("pokaz_rundy.php", "rundy", {"Rozgrywki": cid}, cid=cid)
            if znalezione != set(self._przebieg.ligi):
                raise BladImportu("API nie zwróciło wszystkich wybranych lig.")
        elif zadanie.rodzaj == "rundy":
            cid = zadanie.kontekst["cid"]
            for _, r in wiersze:
                rid = self.ident(r.get("Id"))
                self.dodaj("rundy", {"id": rid}, {"id_rozgrywki": cid, "nazwa": r.get("Nazwa")})
                self.zlec("pokaz_kolejki.php", "kolejki", {"Runda": rid}, cid=cid, rid=rid)
        elif zadanie.rodzaj == "kolejki":
            cid, rid = zadanie.kontekst["cid"], zadanie.kontekst["rid"]
            for _, r in wiersze:
                did = self.ident(r.get("ID_kolejka"))
                dane = self.pola(
                    r,
                    {"nazwa": "Nazwa"},
                    {"nr": "Nr", "lp": "Lp"},
                    daty={"data_start": "DataStart", "data_koniec": "DataKoniec"},
                )
                self.dodaj("kolejki", {"id": did}, {**dane, "id_runda": rid, "id_rozgrywki": cid})
                self.zlec("pokaz_mecze.php", "mecze", {"Kolejka": did}, cid=cid, did=did)
        elif zadanie.rodzaj == "mecze":
            for _, r in wiersze:
                mid = self.mecz(r, zadanie.kontekst)
                self.zlec(
                    "pokaz_mecze_szczegoly.php",
                    "szczegoly",
                    {"Zawody": mid},
                    **zadanie.kontekst,
                    mid=mid,
                )

    def tabele_spis(self, dokument: Any, cid: int) -> None:
        for _, r in self.wiersze(dokument):
            tid = self.ident(r.get("tabela_id"))
            tabela = {"id_rozgrywki": cid, "tabela_id": tid}
            self.dodaj("tabele", tabela, self.pola(r, {"tabela_nazwa": "tabela_nazwa"}))
            grupy = self.wiersze(r["menu2"]) if r.get("menu2") else []
            for _, g in grupy or [("0", {})]:
                gid = self.liczba(g.get("tabela_Id2")) or 0
                self.dodaj(
                    "tabele_grupy",
                    {"id_tabela": {"tabela": "tabele", "klucz": tabela}, "grupa_id": gid},
                    self.pola(g, {"grupa_nazwa": "tabela_nazwa2"}),
                )
                self.zlec(
                    "pokaz_tabela.php",
                    "tabela",
                    {"Rozgrywki": cid, "Tabela": tid, "Tabela2": gid},
                    cid=cid,
                    tid=tid,
                    gid=gid,
                )

    def tabela(self, dokument: Any, kontekst: dict[str, int]) -> None:
        cid = kontekst["cid"]
        grupa = {
            "tabela": "tabele_grupy",
            "klucz": {
                "id_tabela": {
                    "tabela": "tabele",
                    "klucz": {"id_rozgrywki": cid, "tabela_id": kontekst["tid"]},
                },
                "grupa_id": kontekst["gid"],
            },
        }
        wiersze = self.wiersze(dokument)
        naglowek = next((r for _, r in wiersze if "ID_zespoly" not in r), {})
        druzyny = [r for _, r in wiersze if "ID_zespoly" in r]
        for miejsce, r in enumerate(druzyny, 1):
            tid = self.liczba(r.get("ID_zespoly"))
            if not tid or tid <= 0:
                continue
            self.druzyna(tid, cid, r.get("Nazwa"), uzupelnij_sezon=True)
            dane = self.pola(
                r,
                {
                    "kryteria": "Kryteria",
                    "zd_st": "Zd_St",
                    "grupa": "Grupa",
                    "grupa_kolor": "GrupaKolor",
                },
                {
                    "mecze": "Mecze",
                    "zwyciestwa": "Zwyciestwa",
                    "remisy": "Remisy",
                    "przegrane": "Przegrane",
                    "remis_wygrane": "RemisWygrane",
                    "remis_przegrane": "RemisPrzegrane",
                    "bramki_zdobyte": "BramkiZdobyte",
                    "bramki_stracone": "BramkiStracone",
                    "bramki_zdobyte_ex": "BramkiZdobyteEx",
                    "bramki_ex": "BramkiEx",
                    "bramki_zdobyte_wyjazd": "BramkiZdobyteWyjazd",
                    "punkty_zdobyte": "PunktyZdobyte",
                    "punkty_stracone": "PunktyStracone",
                    "punkty_ex": "PunktyEx",
                    "punkty_bonusowe": "PunktyBonusowe",
                },
            )
            if "kryteria" not in dane and "Kryteria" in naglowek:
                dane.update(self.pola(naglowek, {"kryteria": "Kryteria"}))
            dane.update(miejsce=miejsce, kolejnosc_zrodlowa=miejsce)
            self.dodaj("tabele_wiersze", {"id_tabela_grupa": grupa, "id_zespol": tid}, dane)

    def druzyna(
        self, tid: int | None, cid: int | None, nazwa: Any = None, uzupelnij_sezon: bool = False
    ) -> None:
        if not tid or tid <= 0:
            return
        sezon = self._przebieg.id_sezon
        self.dodaj("zespoly", {"id": tid}, {"kategoria": "Senior"}, True)
        dane = {"kategoria": "Senior"}
        if isinstance(nazwa, str) and nazwa:
            dane["nazwa"] = nazwa
        self.dodaj("zespoly_sezony", {"id_zespol": tid, "id_sezon": sezon}, dane, uzupelnij_sezon)
        if cid:
            self.dodaj(
                "zespoly_rozgrywki",
                {"id_zespol": tid, "id_rozgrywki": cid},
                {"id_sezon": sezon},
                uzupelnij_sezon,
            )
        if self._przebieg.tryb == "pelny":
            self.zlec("pokaz_sklad.php", "sklad", {"Sezon": 195, "Zespol": tid}, tid=tid)

    def mecz(self, r: dict[str, Any], kontekst: dict[str, int]) -> int:
        mid = self.ident(r.get("Id", r.get("IdZawody")))
        if "mid" in kontekst and mid != kontekst["mid"]:
            raise BladImportu("Szczegóły dotyczą innego meczu.")
        for pole, oczekiwane in (("ID_sezon", 195), ("Id_rozgrywki", kontekst["cid"])):
            if pole in r and self.ident(r[pole]) != oczekiwane:
                raise BladImportu("Niezgodność sezonu lub ligi w meczu.")
        if str(r.get("Kategoria", "1")) != "1":
            raise BladImportu("Mecz nie należy do kategorii seniorów.")
        liczby = """alias_gosp alias_gosc wynik_gosp_pol wynik_gosp_full wynik_gosc_pol
            wynik_gosc_full wynik_temp_gosp_pol wynik_temp_gosp_full wynik_temp_gosc_pol
            wynik_temp_gosc_full wynik_koncowy_gosp wynik_koncowy_gosc wynik_bramki_gosp
            wynik_bramki_gosc dogrywka_1_pol_gosp dogrywka_1_pol_gosc dogrywka_1_full_gosp
            dogrywka_1_full_gosc dogrywka_2_pol_gosp dogrywka_2_pol_gosc dogrywka_2_full_gosp
            dogrywka_2_full_gosc dogrywka_karne_gosp dogrywka_karne_gosc karne_bramki_gosp
            karne_bramki_gosc karne_ile_gosp karne_ile_gosc zwyciezca widzowie""".split()
        teksty = """timeout1_gosp timeout2_gosp timeout3_gosp timeout1_gosc timeout2_gosc
            timeout3_gosc wycofany_typ protokol komentarz transmisja transmisja_godzina
            bilety_url""".split()
        dane = self.pola(
            r,
            {**{p: p for p in teksty}, "rozgrywki_code": "RozgrywkiCode"},
            {
                **{p: p for p in liczby},
                "lp": "Lp",
                "kary_gosp": "KaryGosp",
                "kary_gosc": "KaryGosc",
            },
            {
                "zamiana": "zamiana",
                "wycofany": "wycofany",
                "czy_remis": "czy_remis",
                "protokol_zatwierdzony": "protokol_zatwierdz",
            },
            {
                "data_faktyczna": "data_fakt",
                "data_propozycji": "data_prop",
                "data_ostatniej_zmiany": "DataOstatnieZmiany",
            },
        )
        for strona in ("gosp", "gosc"):
            pole = "ID_zespoly_" + strona
            if pole in r:
                tid = self.liczba(r[pole])
                tid = tid if tid and tid > 0 else None
                self.druzyna(tid, kontekst["cid"], r.get(pole + "_ZespolNazwa"))
                dane["id_zespol_" + strona] = tid
        dane.update(
            self.pola(
                r,
                {
                    "data_propozycji_dzien": "data_prop_dzien",
                    "data_faktyczna_dzien": "data_fakt_dzien",
                    "protokol_zalacznik_plik": "protokol_zalcznik_plik",
                    "protokol_zalacznik_typ": "protokol_zalcznik_plik_typ",
                    "protokol_zalacznik_nazwa": "protokol_zalcznik_nazwa",
                },
                {
                    "po_para_id": "PO_para_ID",
                    "po_para_id_gosp": "PO_para_ID_gosp",
                    "po_para_id_gosc": "PO_para_ID_gosc",
                },
            )
        )
        for kolumna, pole in (
            ("id_zespol_walkower", "walkower_ID_zespoly"),
            ("id_zespol_wycofany", "wycofany_ID_zespoly"),
        ):
            if pole in r:
                tid = self.liczba(r[pole])
                tid = tid if tid and tid > 0 else None
                self.druzyna(tid, kontekst["cid"])
                dane[kolumna] = tid
        hala = self.pola(r, {p: "Hala_" + p for p in ("nazwa", "miasto", "ulica", "numer")})
        if hala.get("nazwa"):
            klucz_hali = {p: hala.get(p) for p in ("nazwa", "miasto", "ulica", "numer")}
            self.dodaj("hale", klucz_hali, self.pola(r, liczby={"pojemnosc": "Hala_pojemnosc"}))
            dane["id_hala"] = {"tabela": "hale", "klucz": klucz_hali}
        dane.update(id_sezon=195, id_rozgrywki=kontekst["cid"], id_kolejka=kontekst["did"])
        self.dodaj("mecze", {"id": mid}, dane)
        return mid

    def szczegoly(self, dokument: Any, kontekst: dict[str, int]) -> None:
        if dokument is None:
            return
        if isinstance(dokument, dict):
            naglowek: Any = dokument.get("0", {})
        elif isinstance(dokument, list):
            naglowek = dokument[0] if dokument else {}
        else:
            raise BladImportu(f"Nieprawidłowa struktura szczegółów meczu {kontekst['mid']}.")
        for _ in range(4):
            if isinstance(naglowek, dict) and "Id" in naglowek:
                break
            if isinstance(naglowek, dict):
                nastepny = next(iter(naglowek.values()), None)
            elif isinstance(naglowek, list):
                nastepny = naglowek[0] if naglowek else None
            else:
                nastepny = None
            if nastepny is None:
                return
            naglowek = nastepny
        if not isinstance(naglowek, dict) or "Id" not in naglowek:
            return
        mid = self.mecz(naglowek, kontekst)
        for strona in ("gosp", "gosc", "inne"):
            if strona not in dokument:
                continue
            for klucz, r in self.wiersze(dokument[strona]):
                pid = self.ident(klucz)
                osoba = self.pola(r, {"imie": "imie", "nazwisko": "nazwisko"})
                self.dodaj("zawodnicy", {"id": pid}, osoba, True)
                liczby = {
                    p: p
                    for p in (
                        "bramki",
                        "kd",
                        "karne_liczba",
                        "karne_bramki",
                        "karne_liczba_seria",
                        "karne_bramki_seria",
                    )
                }
                dane = self.pola(
                    r,
                    {"imie": "imie", "nazwisko": "nazwisko", "pozycja": "Pozycja"},
                    {**liczby, "nr_koszulki": "NrKoszulki", "dwie_minuty": "2minuty"},
                    {p: p for p in ("upomnienie", "dyskwalifikacja", "wyjscie")},
                )
                self.dodaj(
                    "mecze_zawodnicy", {"id_mecz": mid, "strona": strona, "id_zawodnik": pid}, dane
                )

    def sklad(self, dokument: Any, kontekst: dict[str, int]) -> None:
        wiersze = self.wiersze(dokument)
        naglowek = next((r for _, r in wiersze if "ID_zespol" in r), None)
        if naglowek is None:
            raise BladImportu("Brak nagłówka sezonowego składu drużyny.")
        if self.ident(naglowek["ID_zespol"]) != kontekst["tid"]:
            raise BladImportu("API zwróciło skład innej drużyny.")
        if naglowek.get("Sezon") != "2026/2027" or naglowek.get("Kategoria") != "Senior":
            raise BladImportu("Skład spoza sezonu 2026/2027 lub kategorii seniorów.")
        dane = self.pola(naglowek, {"nazwa": "Nazwa", "plec": "Plec"})
        self.dodaj(
            "zespoly_sezony", {"id_zespol": kontekst["tid"], "id_sezon": SEZON_IMPORTU}, dane
        )
        for _, r in wiersze:
            if "NrZawodnika" not in r:
                continue
            pid = self.ident(r["NrZawodnika"])
            self.dodaj(
                "zawodnicy",
                {"id": pid},
                self.pola(r, {"imie": "Imie", "nazwisko": "Nazwisko"}),
                True,
            )
