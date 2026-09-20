(() => {
  class FiltryZawodnikowController {
    constructor(formularz, lokalizacja, magazyn) {
      this.formularz = formularz;
      this.lokalizacja = lokalizacja;
      this.magazyn = magazyn;
      this.klucz = 'hds.zawodnicy.filtry.v1';
      this.pola = ['id_sezon', 'rozgrywki', 'druzyna', 'pozycja', 'rocznik', 'szukaj'];
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
          if (pole.type === 'number' && (!/^\d+$/.test(wartosc)
            || (pole.min && Number(wartosc) < Number(pole.min))
            || (pole.max && Number(wartosc) > Number(pole.max)))) return;
          if (pole.maxLength > 0 && wartosc.length > pole.maxLength) return;
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

  const formularz = document.querySelector('[data-player-filters]');
  if (formularz) {
    new FiltryZawodnikowController(formularz, window.location, () => window.localStorage).uruchom();
  }
})();
