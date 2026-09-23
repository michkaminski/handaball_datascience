(() => {
  class WyborLigController {
    constructor(pole) {
      this.pola = pole.querySelectorAll('input[name="ligi"]');
      this.przyciski = pole.querySelector('.import-selection');
    }

    uruchom() {
      this.przyciski.querySelectorAll('[data-wybor]').forEach(przycisk => {
        przycisk.addEventListener('click', () => this.zaznacz(przycisk.dataset.wybor));
      });
      this.przyciski.hidden = false;
    }

    zaznacz(wybor) {
      const wzorce = wybor.split('|');
      this.pola.forEach(pole => {
        const nazwa = pole.dataset.nazwa.toLocaleLowerCase('pl');
        pole.checked = wybor === 'wszystkie' || (
          wybor !== 'zadne' && wzorce.some(wzorzec => (
            wzorzec.startsWith('*') ? nazwa.includes(wzorzec.slice(1)) && !nazwa.includes('superpuchar') : nazwa.startsWith(wzorzec)
          ))
        );
      });
    }
  }

  document.querySelectorAll('[data-wybor-lig]').forEach(pole => {
    new WyborLigController(pole).uruchom();
  });

  document.querySelectorAll('[data-import-sezon]').forEach(formularz => {
    const lista = formularz.querySelector('select');
    formularz.querySelector('[data-import-sezon-przycisk]').hidden = true;
    lista.addEventListener('change', () => formularz.submit());
  });

  const form = document.getElementById('pobieranie');
  if (!form) return;
  let running = false;
  let bledyZRzedu = 0;
  const MAKS_OPOZNIENIE_MS = 5000;
  const button = form.querySelector('button');
  const status = document.getElementById('stan-pobierania');
  async function download() {
    if (running) return;
    running = true;
    button.disabled = true;
    status.textContent = 'Pobieranie…';
    try {
      while (running) {
        const response = await fetch(window.location.pathname, {
          method: 'POST', body: new FormData(form), headers: {'Accept': 'application/json'}
        });
        if (!response.ok) throw new Error('Pobieranie przerwane. Odśwież stronę i ponów krok.');
        const result = await response.json();
        document.getElementById('liczba-pobran').textContent = result.wykonane;
        document.getElementById('liczba-oczekujacych').textContent = result.oczekujace;
        if (result.status === 'BLAD') {
          bledyZRzedu += 1;
          const pominieteInfo = result.pominiete ? ` Pominięto dotąd: ${result.pominiete}.` : '';
          status.textContent =
            `Błąd kroku (${result.blad || ''}), ponawiam automatycznie (próba ${bledyZRzedu})…${pominieteInfo}`;
          await new Promise(resolve => setTimeout(resolve, Math.min(1000 * bledyZRzedu, MAKS_OPOZNIENIE_MS)));
          continue;
        }
        bledyZRzedu = 0;
        if (result.status !== 'POBIERANIE') { window.location.reload(); return; }
        await new Promise(resolve => setTimeout(resolve, 150));
      }
    } catch (error) {
      status.textContent = error.message;
      running = false;
      button.disabled = false;
    }
  }
  form.addEventListener('submit', event => { event.preventDefault(); download(); });
  if (form.dataset.auto === 'tak') download();
})();
