(() => {
  const OPOZNIENIE_KLIKNIECIA = 250;
  const zmodyfikowane = zdarzenie => zdarzenie.ctrlKey || zdarzenie.metaKey || zdarzenie.shiftKey || zdarzenie.altKey || zdarzenie.button > 0;
  const pobierzZOkna = (adres, opcje) => window.fetch(adres, opcje);
  const otworzKarte = adres => window.open(adres, '_blank', 'noopener');

  class OknoDruzynyController {
    constructor(okno, pobierz, otworz) {
      this.okno = okno;
      this.pobierz = pobierz;
      this.otworzKarte = otworz;
      this.tresc = okno.querySelector('[data-team-content]');
      this.link = okno.querySelector('[data-team-open-tab]');
      this.zadanie = null;
      this.powrot = null;
    }

    uruchom() {
      this.okno.querySelectorAll('[data-team-close]').forEach(przycisk => {
        przycisk.addEventListener('click', () => this.okno.close());
      });
      this.okno.addEventListener('close', () => {
        this.zadanie?.abort();
        this.tresc.replaceChildren();
        this.powrot?.focus();
      });
      this.tresc.addEventListener('submit', zdarzenie => {
        const formularz = zdarzenie.target.closest('form');
        if (!formularz || formularz.method.toLowerCase() !== 'get' || !this.wewnetrzny(formularz.action)) return;
        zdarzenie.preventDefault();
        const adres = new URL(formularz.action, window.location.href);
        adres.search = new URLSearchParams(new FormData(formularz)).toString();
        this.wczytaj(adres.href);
      });
      this.tresc.addEventListener('click', zdarzenie => {
        const link = zdarzenie.target.closest('a[href]');
        if (!link || link.target || link.hasAttribute('data-team-scroll') || link.hasAttribute('data-player-modal-link')) return;
        if (zmodyfikowane(zdarzenie) || !this.wewnetrzny(link.href)) return;
        zdarzenie.preventDefault();
        this.wczytaj(link.href);
      });
    }

    wewnetrzny(adres) {
      if (!this.link.href) return false;
      return new URL(adres, window.location.href).pathname === new URL(this.link.href, window.location.href).pathname;
    }

    otworz(adres, powrot) {
      this.powrot = powrot;
      if (!this.okno.open) this.okno.showModal();
      this.wczytaj(adres);
    }

    async wczytaj(adres) {
      this.zadanie?.abort();
      const zadanie = new AbortController();
      this.zadanie = zadanie;
      this.link.href = adres;
      this.tresc.textContent = 'Ładowanie karty drużyny…';
      this.tresc.setAttribute('aria-busy', 'true');
      try {
        const odpowiedz = await this.pobierz(adres, {signal: zadanie.signal});
        if (!odpowiedz.ok) throw new Error('Błąd odczytu');
        const dokument = new DOMParser().parseFromString(await odpowiedz.text(), 'text/html');
        const szczegoly = dokument.querySelector('[data-team-detail]');
        if (!szczegoly) throw new Error('Brak karty');
        szczegoly.querySelector('[data-team-navigation]')?.remove();
        if (!zadanie.signal.aborted) {
          this.tresc.replaceChildren(szczegoly);
          this.tresc.scrollTop = 0;
          const Zakladki = globalThis.HandballDruzyna?.ZakladkiDruzynyController;
          if (Zakladki) new Zakladki(szczegoly).uruchom();
          const Linki = globalThis.HandballZawodnik?.LinkiZawodnikowController;
          if (Linki) new Linki(szczegoly, this.pobierz, this.otworzKarte).uruchom();
        }
      } catch {
        if (!zadanie.signal.aborted) {
          this.tresc.textContent = 'Nie udało się wczytać karty drużyny. Otwórz ją w nowej karcie albo spróbuj ponownie.';
        }
      } finally {
        if (this.zadanie === zadanie) this.tresc.removeAttribute('aria-busy');
      }
    }
  }

  class LinkiDruzynController {
    constructor(korzen, pobierz, otworz, zegar = globalThis) {
      this.korzen = korzen;
      this.pobierz = pobierz;
      this.otworzKarte = otworz;
      this.zegar = zegar;
      this.odlozone = null;
    }

    uruchom() {
      const okno = this.korzen.querySelector('[data-team-modal-dialog]');
      if (!okno || typeof okno.showModal !== 'function') return;
      this.okienko = new OknoDruzynyController(okno, this.pobierz, this.otworzKarte);
      this.okienko.uruchom();
      this.korzen.querySelectorAll('a[data-team-modal-link]').forEach(link => {
        link.addEventListener('click', zdarzenie => {
          if (zmodyfikowane(zdarzenie)) return;
          zdarzenie.preventDefault();
          this.anuluj();
          if (zdarzenie.detail === 0) {
            this.okienko.otworz(link.href, link);
            return;
          }
          this.odlozone = this.zegar.setTimeout(() => {
            this.odlozone = null;
            this.okienko.otworz(link.href, link);
          }, OPOZNIENIE_KLIKNIECIA);
        });
        link.addEventListener('dblclick', zdarzenie => {
          zdarzenie.preventDefault();
          this.anuluj();
          this.otworzKarte(link.href);
        });
      });
    }

    anuluj() {
      if (this.odlozone !== null) this.zegar.clearTimeout(this.odlozone);
      this.odlozone = null;
    }
  }

  class SzczegolyKlasyfikacjiController {
    constructor(tabela, okno, pobierz) {
      this.tabela = tabela;
      this.okno = okno;
      this.pobierz = pobierz;
      this.tresc = okno.querySelector('[data-detail-content]');
      this.link = okno.querySelector('[data-detail-open-tab]');
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
      this.tabela.querySelectorAll('tbody tr[data-detail-href]').forEach(wiersz => {
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

    otworz(wiersz) {
      this.wiersz = wiersz;
      if (!this.okno.open) this.okno.showModal();
      this.wczytaj(wiersz.dataset.detailHref);
    }

    async wczytaj(adres) {
      this.zadanie?.abort();
      const zadanie = new AbortController();
      this.zadanie = zadanie;
      this.link.href = adres;
      this.tresc.textContent = 'Ładowanie szczegółów…';
      this.tresc.setAttribute('aria-busy', 'true');
      try {
        const odpowiedz = await this.pobierz(adres, {signal: zadanie.signal});
        if (!odpowiedz.ok) throw new Error('Błąd odczytu');
        const dokument = new DOMParser().parseFromString(await odpowiedz.text(), 'text/html');
        const szczegoly = dokument.querySelector('[data-classification-detail]');
        if (!szczegoly) throw new Error('Brak szczegółów');
        szczegoly.querySelector('[data-detail-navigation]')?.remove();
        if (!zadanie.signal.aborted) {
          this.tresc.replaceChildren(szczegoly);
          this.tresc.scrollTop = 0;
          new LinkiDruzynController(szczegoly, this.pobierz, otworzKarte).uruchom();
        }
      } catch {
        if (!zadanie.signal.aborted) {
          this.tresc.textContent = 'Nie udało się wczytać szczegółów. Otwórz je w nowej karcie albo spróbuj ponownie.';
        }
      } finally {
        if (this.zadanie === zadanie) this.tresc.removeAttribute('aria-busy');
      }
    }
  }

  globalThis.HandballKlasyfikacja = {OknoDruzynyController, LinkiDruzynController};

  const tabela = document.querySelector('[data-detail-table]');
  const okno = document.querySelector('[data-detail-dialog]');
  if (tabela && okno && typeof okno.showModal === 'function') {
    new SzczegolyKlasyfikacjiController(tabela, okno, pobierzZOkna).uruchom();
  }
  const szczegoly = document.querySelector('[data-classification-detail]');
  if (szczegoly) new LinkiDruzynController(szczegoly, pobierzZOkna, otworzKarte).uruchom();
})();
