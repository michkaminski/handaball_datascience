class ZakladkiSedziegoController {
  constructor(kontener) {
    this.kontener = kontener;
    this.przyciski = [...kontener.querySelectorAll('[data-referee-tab]')];
    this.panele = [...kontener.querySelectorAll('[data-referee-panel]')];
  }

  uruchom() {
    const pasek = this.kontener.querySelector('[data-referee-tabs]');
    if (!pasek || !this.przyciski.length) return;
    pasek.hidden = false;
    this.przyciski.forEach((przycisk, indeks) => {
      przycisk.addEventListener('click', () => this.wybierz(przycisk.dataset.refereeTab));
      przycisk.addEventListener('keydown', (zdarzenie) => this.klawiatura(zdarzenie, indeks));
    });
    this.wybierz(this.kontener.dataset.activeTab || 'dane');
  }

  wybierz(klucz) {
    this.przyciski.forEach((przycisk) => {
      const aktywny = przycisk.dataset.refereeTab === klucz;
      przycisk.setAttribute('aria-selected', String(aktywny));
      przycisk.tabIndex = aktywny ? 0 : -1;
    });
    this.panele.forEach((panel) => { panel.hidden = panel.dataset.refereePanel !== klucz; });
  }

  klawiatura(zdarzenie, indeks) {
    const klawisze = ['ArrowLeft', 'ArrowRight', 'Home', 'End'];
    if (!klawisze.includes(zdarzenie.key)) return;
    zdarzenie.preventDefault();
    let cel = indeks;
    if (zdarzenie.key === 'ArrowLeft') cel = (indeks - 1 + this.przyciski.length) % this.przyciski.length;
    if (zdarzenie.key === 'ArrowRight') cel = (indeks + 1) % this.przyciski.length;
    if (zdarzenie.key === 'Home') cel = 0;
    if (zdarzenie.key === 'End') cel = this.przyciski.length - 1;
    const przycisk = this.przyciski[cel];
    this.wybierz(przycisk.dataset.refereeTab);
    przycisk.focus();
  }
}

const szczegolySedziego = document.querySelector('[data-referee-detail]');
if (szczegolySedziego) new ZakladkiSedziegoController(szczegolySedziego).uruchom();