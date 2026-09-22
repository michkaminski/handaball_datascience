(() => {
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

  const tabela = document.querySelector('[data-detail-table]');
  const okno = document.querySelector('[data-detail-dialog]');
  if (tabela && okno && typeof okno.showModal === 'function') {
    new SzczegolyKlasyfikacjiController(tabela, okno, window.fetch.bind(window)).uruchom();
  }
})();
