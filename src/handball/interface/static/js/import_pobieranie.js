class WyborMeczowDoPobrania {
  constructor(formularz) {
    this.formularz = formularz;
  }

  uruchom() {
    this.formularz.addEventListener('change', () => this.odswiez());
    this.formularz.addEventListener('submit', zdarzenie => this.wyslij(zdarzenie));
    this.formularz.querySelectorAll('[data-zaznacz]').forEach(przycisk => {
      przycisk.addEventListener('click', () => this.zaznacz(przycisk.dataset.zaznacz === 'widoczne'));
    });
    this.formularz.querySelectorAll('[data-zaznacz-kolejke]').forEach(przycisk => {
      przycisk.addEventListener('click', () => this.zaznaczKolejke(przycisk));
    });
    this.odswiez();
  }

  pola() {
    return Array.from(this.formularz.querySelectorAll('input[name="mecze"]'));
  }

  stany() {
    return Array.from(this.formularz.querySelectorAll('[data-stan-zaznaczenia]'));
  }

  zaznacz(zaznaczone) {
    this.pola().forEach(pole => {
      pole.checked = zaznaczone;
    });
    this.odswiez();
  }

  zaznaczKolejke(przycisk) {
    const kolejka = przycisk.closest('.schedule-matchday');
    if (!kolejka) return;
    kolejka.querySelectorAll('input[name="mecze"]').forEach(pole => {
      pole.checked = true;
    });
    this.odswiez();
  }

  odswiez(tekst) {
    const liczba = this.pola().filter(pole => pole.checked).length;
    const komunikat = tekst || `Zaznaczono: ${liczba}`;
    this.stany().forEach(stan => {
      stan.textContent = komunikat;
    });
  }

  wyslij(zdarzenie) {
    const liczba = this.pola().filter(pole => pole.checked).length;
    const limit = Number(this.formularz.dataset.limit);
    if (liczba === 0) {
      zdarzenie.preventDefault();
      this.odswiez('Zaznacz przynajmniej jeden mecz.');
      return;
    }
    if (liczba > limit) {
      zdarzenie.preventDefault();
      this.odswiez(`Można pobrać najwyżej ${limit} meczów naraz. Zawęź rundę albo kolejkę.`);
    }
  }
}

const formularzPobierania = document.querySelector('[data-import-z-terminarza]');
if (formularzPobierania) new WyborMeczowDoPobrania(formularzPobierania).uruchom();
