(() => {
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

  if (tabela) {
    tabela.querySelectorAll('tbody tr[data-href]').forEach(wiersz => {
      wiersz.classList.add('row-clickable');
      wiersz.addEventListener('dblclick', () => {
        window.location.href = wiersz.dataset.href;
      });
    });
  }
})();
