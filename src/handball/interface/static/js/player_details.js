(() => {
  class ZakladkiZawodnikaController {
    constructor(korzen, poWyborze = () => {}) {
      this.korzen = korzen;
      this.poWyborze = poWyborze;
    }

    uruchom() {
      const zdjecie = this.korzen.querySelector('[data-player-photo]');
      if (zdjecie) {
        const brak = () => {
          zdjecie.hidden = true;
          this.korzen.querySelector('[data-player-photo-fallback]').hidden = false;
        };
        zdjecie.addEventListener('error', brak);
        if (zdjecie.complete && !zdjecie.naturalWidth) brak();
      }
      const pasek = this.korzen.querySelector('[data-player-tabs]');
      if (!pasek) return;
      this.przyciski = Array.from(pasek.querySelectorAll('[role="tab"]'));
      this.panele = Array.from(this.korzen.querySelectorAll('[data-player-panel]'));
      this.panele.forEach(panel => {
        panel.setAttribute('role', 'tabpanel');
        panel.tabIndex = 0;
      });
      pasek.hidden = false;
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
          this.wybierz(kierunki[zdarzenie.key]);
          this.przyciski[kierunki[zdarzenie.key]].focus();
        });
      });
      const indeks = this.przyciski.findIndex(p => p.dataset.playerTab === this.korzen.dataset.activeTab);
      this.wybierz(Math.max(0, indeks));
    }

    wybierz(indeks) {
      this.przyciski.forEach((przycisk, numer) => {
        przycisk.setAttribute('aria-selected', String(numer === indeks));
        przycisk.tabIndex = numer === indeks ? 0 : -1;
      });
      const klucz = this.przyciski[indeks].dataset.playerTab;
      this.panele.forEach(panel => { panel.hidden = panel.dataset.playerPanel !== klucz; });
      this.poWyborze(klucz);
    }
  }

  class SzczegolyZawodnikaController {
    constructor(tabela, okno, pobierz) {
      this.tabela = tabela;
      this.okno = okno;
      this.pobierz = pobierz;
      this.tresc = okno.querySelector('[data-player-content]');
      this.link = okno.querySelector('[data-player-open-tab]');
      this.zadanie = null;
      this.wiersz = null;
    }

    uruchom() {
      this.okno.querySelectorAll('[data-player-close]').forEach(przycisk => {
        przycisk.addEventListener('click', () => this.okno.close());
      });
      this.okno.addEventListener('close', () => {
        this.zadanie?.abort();
        this.tresc.replaceChildren();
        this.wiersz?.focus();
      });
      this.tabela.querySelectorAll('tbody tr[data-player-href]').forEach(wiersz => {
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
      this.tresc.addEventListener('submit', zdarzenie => {
        const formularz = zdarzenie.target.closest('[data-player-match-filters]');
        if (!formularz) return;
        zdarzenie.preventDefault();
        const adres = new URL(formularz.action, window.location.href);
        adres.search = new URLSearchParams(new FormData(formularz)).toString();
        this.wczytaj(adres.href);
      });
      this.tresc.addEventListener('click', zdarzenie => {
        const link = zdarzenie.target.closest('[data-player-page], .paginacja a');
        if (!link || zdarzenie.ctrlKey || zdarzenie.metaKey || zdarzenie.shiftKey || zdarzenie.altKey || zdarzenie.button > 0) return;
        zdarzenie.preventDefault();
        this.wczytaj(link.href);
      });
    }

    otworz(wiersz) {
      this.wiersz = wiersz;
      if (!this.okno.open) this.okno.showModal();
      this.wczytaj(wiersz.dataset.playerHref);
    }

    async wczytaj(adres) {
      this.zadanie?.abort();
      const zadanie = new AbortController();
      this.zadanie = zadanie;
      this.link.href = adres;
      this.tresc.textContent = 'Ładowanie szczegółów zawodnika…';
      this.tresc.setAttribute('aria-busy', 'true');
      try {
        const odpowiedz = await this.pobierz(adres, {signal: zadanie.signal});
        if (!odpowiedz.ok) throw new Error('Błąd odczytu');
        const dokument = new DOMParser().parseFromString(await odpowiedz.text(), 'text/html');
        const szczegoly = dokument.querySelector('[data-player-detail]');
        if (!szczegoly) throw new Error('Brak karty');
        szczegoly.querySelector('[data-player-navigation]')?.remove();
        if (!zadanie.signal.aborted) {
          this.tresc.replaceChildren(szczegoly);
          new ZakladkiZawodnikaController(szczegoly, klucz => {
            const url = new URL(this.link.href, window.location.href);
            url.searchParams.set('zakladka', klucz);
            this.link.href = url.href;
          }).uruchom();
          const panel = szczegoly.querySelector('[data-player-panel]:not([hidden])');
          panel?.focus({preventScroll: true});
          this.tresc.scrollTop = 0;
        }
      } catch {
        if (!zadanie.signal.aborted) {
          this.tresc.textContent = 'Nie udało się wczytać szczegółów zawodnika. Otwórz kartę w nowej karcie, aby sprawdzić odpowiedź, lub zamknij okno i spróbuj ponownie.';
        }
      } finally {
        if (this.zadanie === zadanie) this.tresc.removeAttribute('aria-busy');
      }
    }
  }

  const szczegoly = document.querySelector('[data-player-detail]');
  if (szczegoly) new ZakladkiZawodnikaController(szczegoly).uruchom();
  const tabela = document.getElementById('players-table');
  const okno = document.getElementById('player-detail-dialog');
  if (tabela && okno && typeof okno.showModal === 'function') {
    new SzczegolyZawodnikaController(tabela, okno, window.fetch.bind(window)).uruchom();
  }
})();
