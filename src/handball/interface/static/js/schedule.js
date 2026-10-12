class FiltryTerminarzaController {
  constructor(formularz) {
    this.formularz = formularz;
  }

  uruchom() {
    this.pola().forEach(pole => {
      pole.addEventListener('change', () => this.zmiana(pole));
    });
  }

  pola() {
    return Array.from(this.formularz.querySelectorAll('select[data-schedule-level]'));
  }

  zmiana(zmienione) {
    const poziom = Number(zmienione.dataset.scheduleLevel);
    this.pola()
      .filter(pole => Number(pole.dataset.scheduleLevel) > poziom)
      .forEach(pole => {
        pole.value = '';
        pole.disabled = true;
      });
    this.formularz.submit();
  }
}

class WierszeTerminarzaController {
  constructor(korzen, okno) {
    this.korzen = korzen;
    this.okno = okno;
  }

  uruchom() {
    this.korzen.querySelectorAll('.schedule-row[data-href]').forEach(wiersz => {
      wiersz.classList.add('row-clickable');
      wiersz.tabIndex = 0;
      wiersz.addEventListener('click', zdarzenie => {
        if (this.elementInteraktywny(zdarzenie)) return;
        if (zdarzenie.ctrlKey || zdarzenie.metaKey) {
          this.okno.open(wiersz.dataset.href, '_blank');
          return;
        }
        this.okno.location.href = wiersz.dataset.href;
      });
      wiersz.addEventListener('keydown', zdarzenie => {
        if (zdarzenie.key === 'Enter' && zdarzenie.target === wiersz) {
          zdarzenie.preventDefault();
          this.okno.location.href = wiersz.dataset.href;
        }
      });
    });
  }

  elementInteraktywny(zdarzenie) {
    return Boolean(zdarzenie.target.closest && zdarzenie.target.closest('a, button, input, select, label'));
  }
}

class OknoTypowanController {
  constructor(korzen, okno, pobierz, parser) {
    this.korzen = korzen;
    this.okno = okno;
    this.pobierz = pobierz;
    this.parser = parser;
    this.tresc = okno.querySelector('[data-tips-content]');
    this.tytul = okno.querySelector('[data-tips-dialog-title]');
    this.link = okno.querySelector('[data-tips-open-tab]');
    this.zadanie = null;
    this.zrodlo = null;
  }

  uruchom() {
    this.okno.querySelectorAll('[data-tips-close]').forEach(przycisk => {
      przycisk.addEventListener('click', () => this.okno.close());
    });
    this.okno.addEventListener('close', () => {
      if (this.zadanie) this.zadanie.abort();
      this.tresc.replaceChildren();
      if (this.zrodlo) this.zrodlo.focus();
    });
    this.korzen.querySelectorAll('a[data-tips-link]').forEach(link => {
      link.addEventListener('click', zdarzenie => {
        if (zdarzenie.ctrlKey || zdarzenie.metaKey || zdarzenie.shiftKey || zdarzenie.button > 0) return;
        zdarzenie.preventDefault();
        this.otworz(link);
      });
    });
  }

  otworz(link) {
    this.zrodlo = link;
    this.tytul.textContent = `Typowania — ${link.textContent.trim()}`;
    if (!this.okno.open) this.okno.showModal();
    return this.wczytaj(link.getAttribute('href'));
  }

  async wczytaj(adres) {
    if (this.zadanie) this.zadanie.abort();
    const zadanie = new AbortController();
    this.zadanie = zadanie;
    this.link.href = adres;
    this.tresc.textContent = 'Ładowanie typowań…';
    this.tresc.setAttribute('aria-busy', 'true');
    try {
      const odpowiedz = await this.pobierz(adres, {signal: zadanie.signal});
      if (!odpowiedz.ok) throw new Error('Błąd odczytu');
      const dokument = this.parser.parseFromString(await odpowiedz.text(), 'text/html');
      const typowania = dokument.querySelector('[data-schedule-tips]');
      if (!typowania) throw new Error('Brak typowań');
      if (!zadanie.signal.aborted) {
        this.tresc.replaceChildren(typowania);
        this.tresc.scrollTop = 0;
      }
    } catch {
      if (!zadanie.signal.aborted) {
        this.tresc.textContent = 'Nie udało się wczytać typowań. Otwórz je w nowej karcie albo spróbuj ponownie.';
      }
    } finally {
      if (this.zadanie === zadanie) this.tresc.removeAttribute('aria-busy');
    }
  }
}

const formularzTerminarza = document.querySelector('[data-schedule-filters]');
if (formularzTerminarza) new FiltryTerminarzaController(formularzTerminarza).uruchom();
new WierszeTerminarzaController(document, window).uruchom();
const oknoTypowan = document.querySelector('[data-tips-dialog]');
if (oknoTypowan && typeof oknoTypowan.showModal === 'function') {
  new OknoTypowanController(document, oknoTypowan, (adres, opcje) => window.fetch(adres, opcje), new DOMParser()).uruchom();
}
