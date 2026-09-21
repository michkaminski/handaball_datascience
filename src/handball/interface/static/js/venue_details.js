(() => {
  class ZakladkiHaliController {
    constructor(korzen) {
      this.korzen = korzen;
    }

    uruchom() {
      const pasek = this.korzen.querySelector('[data-venue-tabs]');
      if (!pasek) return;
      this.przyciski = Array.from(pasek.querySelectorAll('[role="tab"]'));
      this.panele = Array.from(this.korzen.querySelectorAll('[data-venue-panel]'));
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
      const indeks = this.przyciski.findIndex(
        przycisk => przycisk.dataset.venueTab === this.korzen.dataset.activeTab
      );
      this.wybierz(Math.max(0, indeks));
    }

    wybierz(indeks) {
      this.przyciski.forEach((przycisk, numer) => {
        przycisk.setAttribute('aria-selected', String(numer === indeks));
        przycisk.tabIndex = numer === indeks ? 0 : -1;
      });
      const klucz = this.przyciski[indeks].dataset.venueTab;
      this.panele.forEach(panel => {
        panel.hidden = panel.dataset.venuePanel !== klucz;
      });
    }
  }

  const szczegoly = document.querySelector('[data-venue-detail]');
  if (szczegoly) new ZakladkiHaliController(szczegoly).uruchom();
})();
