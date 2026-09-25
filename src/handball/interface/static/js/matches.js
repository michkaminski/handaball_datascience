(() => {
  class ZakladkiMeczuController {
    constructor(korzen) {
      this.korzen = korzen;
      this.pasek = korzen.querySelector('[data-match-tabs]');
    }

    uruchom() {
      if (!this.pasek) return;
      this.przyciski = Array.from(this.pasek.querySelectorAll('[role="tab"]'));
      this.panele = Array.from(this.korzen.querySelectorAll('[data-match-panel]'));
      this.panele.forEach(panel => {
        panel.setAttribute('role', 'tabpanel');
        panel.tabIndex = 0;
      });
      this.pasek.hidden = false;
      this.przyciski.forEach((przycisk, indeks) => {
        przycisk.addEventListener('click', () => this.wybierz(indeks));
        przycisk.addEventListener('keydown', zdarzenie => {
          const kierunki = {
            ArrowRight: (indeks + 1) % this.przyciski.length,
            ArrowLeft: (indeks + this.przyciski.length - 1) % this.przyciski.length,
            Home: 0,
            End: this.przyciski.length - 1,
          };
          if (!(zdarzenie.key in kierunki)) return;
          zdarzenie.preventDefault();
          const wybrany = kierunki[zdarzenie.key];
          this.wybierz(wybrany);
          this.przyciski[wybrany].focus();
        });
      });
      this.wybierz(0);
    }

    wybierz(indeks) {
      this.przyciski.forEach((przycisk, numer) => {
        przycisk.setAttribute('aria-selected', String(numer === indeks));
        przycisk.tabIndex = numer === indeks ? 0 : -1;
      });
      const identyfikator = this.przyciski[indeks].getAttribute('aria-controls');
      this.panele.forEach(panel => { panel.hidden = panel.id !== identyfikator; });
    }
  }

  const otworzKarte = adres => window.open(adres, '_blank', 'noopener');
  const uruchomSzczegolyMeczu = korzen => {
    new ZakladkiMeczuController(korzen).uruchom();
    const Linki = globalThis.HandballZawodnik?.LinkiZawodnikowController;
    if (Linki) new Linki(korzen, (adres, opcje) => window.fetch(adres, opcje), otworzKarte).uruchom();
    const LinkiDruzyn = globalThis.HandballKlasyfikacja?.LinkiDruzynController;
    if (LinkiDruzyn) new LinkiDruzyn(korzen, (adres, opcje) => window.fetch(adres, opcje), otworzKarte).uruchom();
  };

  const szczegolyStrony = document.querySelector('[data-match-detail]');
  if (szczegolyStrony) uruchomSzczegolyMeczu(szczegolyStrony);

  class FiltryMeczowController {
    constructor(formularz, lokalizacja, magazyn) {
      this.formularz = formularz;
      this.lokalizacja = lokalizacja;
      this.magazyn = magazyn;
      this.klucz = 'hds.mecze.filtry.v1';
      this.pola = ['id_sezon', 'rozgrywki', 'runda', 'kolejka', 'id_hala', 'druzyna', 'data_meczu', 'zakonczone'];
    }

    uruchom() {
      try {
        const magazyn = this.magazyn();
        if (this.lokalizacja.search) {
          const parametry = new URLSearchParams(this.lokalizacja.search);
          const zapis = {};
          this.pola.forEach(nazwa => {
            const wartosc = parametry.get(nazwa);
            if (wartosc) zapis[nazwa] = wartosc;
          });
          if (Object.keys(zapis).length) {
            magazyn.setItem(this.klucz, JSON.stringify(zapis));
          } else {
            magazyn.removeItem(this.klucz);
          }
          return;
        }
        const zapis = JSON.parse(magazyn.getItem(this.klucz));
        magazyn.removeItem(this.klucz);
        if (!zapis || typeof zapis !== 'object' || Array.isArray(zapis)) return;
        const parametry = new URLSearchParams();
        this.pola.forEach(nazwa => {
          const wartosc = zapis[nazwa];
          const pole = this.formularz.elements.namedItem(nazwa);
          if (typeof wartosc !== 'string' || !wartosc || !pole) return;
          if (pole.options && !Array.from(pole.options).some(opcja => opcja.value === wartosc)) return;
          parametry.set(nazwa, wartosc);
        });
        if (parametry.size) {
          this.lokalizacja.replace(`${this.lokalizacja.pathname}?${parametry}`);
        }
      } catch {
        return;
      }
    }
  }

  const formularzFiltrow = document.querySelector('[data-match-filters]');
  if (formularzFiltrow) {
    new FiltryMeczowController(formularzFiltrow, window.location, () => window.localStorage).uruchom();
  }

  class KolumnyMeczowController {
    constructor(tabela, okno, przycisk) {
      this.tabela = tabela;
      this.okno = okno;
      this.przycisk = przycisk;
      this.formularz = okno.querySelector('[data-columns-form]');
      this.kolumny = ['runda', 'kolejka'];
      this.klucz = 'hds.mecze.kolumny.v1';
      this.widocznosc = this.odczytaj();
    }

    odczytaj() {
      try {
        const zapis = JSON.parse(window.localStorage.getItem(this.klucz));
        return {runda: zapis?.runda === true, kolejka: zapis?.kolejka === true};
      } catch {
        return {runda: false, kolejka: false};
      }
    }

    uruchom() {
      this.zastosuj();
      this.przycisk.hidden = false;
      this.przycisk.addEventListener('click', () => {
        this.kolumny.forEach(kolumna => {
          this.formularz.elements.namedItem(kolumna).checked = this.widocznosc[kolumna];
        });
        this.okno.showModal();
      });
      this.okno.querySelectorAll('[data-columns-close]').forEach(przycisk => {
        przycisk.addEventListener('click', () => this.okno.close());
      });
      this.okno.addEventListener('close', () => this.przycisk.focus());
      this.formularz.addEventListener('submit', zdarzenie => {
        zdarzenie.preventDefault();
        this.kolumny.forEach(kolumna => {
          this.widocznosc[kolumna] = this.formularz.elements.namedItem(kolumna).checked;
        });
        this.zastosuj();
        try {
          window.localStorage.setItem(this.klucz, JSON.stringify(this.widocznosc));
        } catch {
          this.okno.close();
          return;
        }
        this.okno.close();
      });
    }

    zastosuj() {
      this.tabela.querySelectorAll('[data-match-column]').forEach(komorka => {
        komorka.hidden = !this.widocznosc[komorka.dataset.matchColumn];
      });
      const pusty = this.tabela.querySelector('[data-empty-matches]');
      if (pusty) {
        pusty.colSpan = this.tabela.querySelectorAll('thead th:not([hidden])').length;
      }
    }
  }

  const tabela = document.getElementById('matches-table');
  const okno = document.getElementById('match-columns-dialog');
  const przycisk = document.querySelector('[data-columns-open]');
  if (tabela && okno && przycisk && typeof okno.showModal === 'function') {
    new KolumnyMeczowController(tabela, okno, przycisk).uruchom();
  }

  class SzczegolyMeczuController {
    constructor(tabela, okno, pobierz) {
      this.tabela = tabela;
      this.okno = okno;
      this.pobierz = pobierz;
      this.tresc = okno.querySelector('[data-detail-content]');
      this.zadanie = null;
      this.wiersz = null;
    }

    uruchom() {
      this.okno.querySelectorAll('[data-detail-close]').forEach(przycisk => {
        przycisk.addEventListener('click', () => this.okno.close());
      });
      this.okno.addEventListener('close', () => {
        this.zadanie?.abort();
        this.tresc.replaceChildren();
        this.wiersz?.focus();
      });
      this.tabela.querySelectorAll('tbody tr[data-href]').forEach(wiersz => {
        wiersz.classList.add('row-clickable');
        wiersz.tabIndex = 0;
        wiersz.addEventListener('dblclick', zdarzenie => {
          if (!zdarzenie.target.closest('a, button, input, select')) this.otworz(wiersz);
        });
        wiersz.addEventListener('keydown', zdarzenie => {
          if (zdarzenie.key === 'Enter' && zdarzenie.target === wiersz) {
            zdarzenie.preventDefault();
            this.otworz(wiersz);
          }
        });
      });
    }

    async otworz(wiersz) {
      this.zadanie?.abort();
      const zadanie = new AbortController();
      this.zadanie = zadanie;
      this.wiersz = wiersz;
      this.tresc.textContent = 'Ładowanie szczegółów meczu…';
      this.tresc.setAttribute('aria-busy', 'true');
      this.okno.querySelector('[data-detail-tab]').href = wiersz.dataset.href;
      if (!this.okno.open) this.okno.showModal();
      try {
        const odpowiedz = await this.pobierz(wiersz.dataset.href, {signal: zadanie.signal});
        if (!odpowiedz.ok) throw new Error('Nie udało się pobrać meczu');
        const dokument = new DOMParser().parseFromString(await odpowiedz.text(), 'text/html');
        const szczegoly = dokument.querySelector('[data-match-detail]');
        if (!szczegoly) throw new Error('Brak szczegółów');
        szczegoly.querySelector('[data-detail-navigation]')?.remove();
        if (!zadanie.signal.aborted) {
          this.tresc.replaceChildren(szczegoly);
          uruchomSzczegolyMeczu(szczegoly);
        }
      } catch {
        if (!zadanie.signal.aborted) {
          this.tresc.textContent = 'Nie udało się wczytać szczegółów. Zamknij okno i spróbuj ponownie lub otwórz mecz w nowej karcie.';
        }
      } finally {
        if (this.zadanie === zadanie) this.tresc.removeAttribute('aria-busy');
      }
    }
  }

  const oknoSzczegolow = document.getElementById('match-detail-dialog');
  if (tabela && oknoSzczegolow && typeof oknoSzczegolow.showModal === 'function') {
    new SzczegolyMeczuController(tabela, oknoSzczegolow, window.fetch.bind(window)).uruchom();
  }
})();
