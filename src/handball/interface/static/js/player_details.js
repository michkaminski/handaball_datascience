(() => {
  const {zaladujECharts, AnalitykaBramekController, FormaBramekController} = globalThis.HandballWykresyBramek;
  const OPCJE_WYKRESOW = {prefiks: 'player', podmiot: 'zawodnika'};

  class DefensywaSkrotZawodnikaController {
    constructor(korzen) {
      this.korzen = korzen;
    }

    async uruchom() {
      const wykres = this.korzen.querySelector('[data-defense-summary]');
      const zrodlo = this.korzen.querySelector('[data-defense-summary-data]');
      if (!wykres || !zrodlo || wykres.dataset.chartReady) return;
      wykres.dataset.chartReady = 'true';
      try {
        const echarts = await zaladujECharts(this.korzen.dataset.echartsUrl);
        const klasy = JSON.parse(zrodlo.textContent);
        const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
        const instancja = echarts.init(wykres, null, {renderer: 'svg'});
        instancja.setOption({
          animation: !ograniczonyRuch,
          animationDuration: 400,
          aria: {show: true, description: 'Średnia liczba bramek zawodnika według pięciu klas jakości defensywy rywala, z liczbą meczów n przy każdej klasie.'},
          color: ['#2b6ea4'],
          grid: {left: 42, right: 18, top: 20, bottom: 60},
          tooltip: {
            trigger: 'item',
            formatter: parametry => `${parametry.name}\nŚrednia: ${parametry.value}\nn=${klasy[parametry.dataIndex].n}`,
          },
          xAxis: {
            type: 'category',
            data: klasy.map(k => k.klasa),
            axisLabel: {rotate: 20, hideOverlap: true},
          },
          yAxis: {type: 'value', name: 'Średnia bramek'},
          series: [{
            type: 'bar',
            barMaxWidth: 40,
            data: klasy.map(k => k.srednia),
            label: {show: true, position: 'top', formatter: parametry => `n=${klasy[parametry.dataIndex].n}`},
            emphasis: {focus: 'series'},
          }],
        });
        if (typeof ResizeObserver === 'function') new ResizeObserver(() => instancja.resize()).observe(wykres);
      } catch {
        wykres.textContent = 'Nie udało się narysować wykresu.';
      }
    }
  }

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
      this.podlaczSpisTresci();
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

    podlaczSpisTresci() {
      const spis = this.korzen.querySelector('[data-player-toc]');
      if (!spis) return;
      this.korzen.querySelectorAll('a[data-player-scroll]').forEach(link => {
        link.addEventListener('click', zdarzenie => {
          const cel = this.korzen.querySelector(link.getAttribute('href'));
          if (!cel) return;
          zdarzenie.preventDefault();
          const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
          cel.scrollIntoView({behavior: ograniczonyRuch ? 'auto' : 'smooth', block: 'start'});
          cel.focus({preventScroll: true});
        });
      });
    }

    wybierz(indeks) {
      this.przyciski.forEach((przycisk, numer) => {
        przycisk.setAttribute('aria-selected', String(numer === indeks));
        przycisk.tabIndex = numer === indeks ? 0 : -1;
      });
      const klucz = this.przyciski[indeks].dataset.playerTab;
      this.panele.forEach(panel => { panel.hidden = panel.dataset.playerPanel !== klucz; });
      if (klucz === 'podsumowanie') new AnalitykaBramekController(this.korzen, OPCJE_WYKRESOW).uruchom();
      if (klucz === 'forma') {
        new FormaBramekController(this.korzen, OPCJE_WYKRESOW).uruchom();
        new DefensywaSkrotZawodnikaController(this.korzen).uruchom();
      }
      this.poWyborze(klucz);
    }
  }

  class OknoZawodnikaController {
    constructor(okno, pobierz) {
      this.okno = okno;
      this.pobierz = pobierz;
      this.tresc = okno.querySelector('[data-player-content]');
      this.link = okno.querySelector('[data-player-open-tab]');
      this.zadanie = null;
      this.powrot = null;
    }

    uruchom() {
      this.okno.querySelectorAll('[data-player-close]').forEach(przycisk => {
        przycisk.addEventListener('click', () => this.okno.close());
      });
      this.okno.addEventListener('close', () => {
        this.zadanie?.abort();
        this.tresc.replaceChildren();
        this.powrot?.focus();
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

  class SzczegolyZawodnikaController {
    constructor(tabela, okno, pobierz) {
      this.tabela = tabela;
      this.okienko = new OknoZawodnikaController(okno, pobierz);
    }

    uruchom() {
      this.okienko.uruchom();
      this.tabela.querySelectorAll('tbody tr[data-player-href]').forEach(wiersz => {
        wiersz.classList.add('row-clickable');
        wiersz.tabIndex = 0;
        wiersz.addEventListener('dblclick', zdarzenie => {
          if (!zdarzenie.target.closest('a, button, input, select')) this.okienko.otworz(wiersz.dataset.playerHref, wiersz);
        });
        wiersz.addEventListener('keydown', zdarzenie => {
          if (zdarzenie.key === 'Enter' && zdarzenie.target === wiersz) {
            zdarzenie.preventDefault();
            this.okienko.otworz(wiersz.dataset.playerHref, wiersz);
          }
        });
      });
    }
  }

  const OPOZNIENIE_KLIKNIECIA = 250;

  class LinkiZawodnikowController {
    constructor(korzen, pobierz, otworzKarte, zegar = globalThis) {
      this.korzen = korzen;
      this.pobierz = pobierz;
      this.otworzKarte = otworzKarte;
      this.zegar = zegar;
      this.odlozone = null;
    }

    uruchom() {
      const okno = this.korzen.querySelector('[data-player-modal-dialog]');
      if (!okno || typeof okno.showModal !== 'function') return;
      this.okienko = new OknoZawodnikaController(okno, this.pobierz);
      this.okienko.uruchom();
      this.korzen.querySelectorAll('a[data-player-modal-link]').forEach(link => {
        link.addEventListener('click', zdarzenie => {
          if (zdarzenie.ctrlKey || zdarzenie.metaKey || zdarzenie.shiftKey || zdarzenie.altKey || zdarzenie.button > 0) return;
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

  globalThis.HandballZawodnik = {OknoZawodnikaController, LinkiZawodnikowController};

  const szczegoly = document.querySelector('[data-player-detail]');
  if (szczegoly) new ZakladkiZawodnikaController(szczegoly).uruchom();
  const tabela = document.getElementById('players-table');
  const okno = document.getElementById('player-detail-dialog');
  if (tabela && okno && typeof okno.showModal === 'function') {
    new SzczegolyZawodnikaController(tabela, okno, window.fetch.bind(window)).uruchom();
  }
})();
