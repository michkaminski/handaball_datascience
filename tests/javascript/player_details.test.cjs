const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');
const kod = readFileSync('src/handball/interface/static/js/player_details.js', 'utf8');

class ElementFixture {
  constructor() {
    this.zdarzenia = {};
    this.dataset = {playerHref: '/administracja/zawodnicy/7'};
    this.classList = {add: () => {}};
  }
  addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; }
  setAttribute() {}
  removeAttribute() {}
  replaceChildren(...dzieci) { this.dzieci = dzieci; }
  focus() { this.fokus = true; }
  showModal() { this.open = true; }
  close() { this.open = false; this.zdarzenia.close(); }
}

class ModalFixture {
  constructor(pobierz) {
    this.wiersz = new ElementFixture();
    this.okno = new ElementFixture();
    this.tresc = new ElementFixture();
    this.przycisk = new ElementFixture();
    this.link = new ElementFixture();
    this.fragment = {querySelector: selektor => selektor === '[data-player-navigation]' ? ({remove: () => { this.usunietoPowrot = true; }}) : null};
    this.okno.querySelector = selektor => selektor === '[data-player-content]' ? this.tresc : this.link;
    this.okno.querySelectorAll = () => [this.przycisk];
    const tabela = {querySelectorAll: () => [this.wiersz]};
    const fragment = this.fragment;
    runInNewContext(kod, {
      URLSearchParams, AbortController,
      DOMParser: class { parseFromString() { return {querySelector: () => fragment}; } },
      window: {fetch: pobierz, location: {href: 'http://localhost/administracja/zawodnicy'}},
      document: {
        querySelector: () => null,
        getElementById: id => ({
          'players-table': tabela,
          'player-detail-dialog': this.okno,
        })[id] ?? null,
      },
    });
  }

  async otworz() {
    this.wiersz.zdarzenia.dblclick({target: {closest: () => null}});
    await new Promise(resolve => setImmediate(resolve));
  }
}

test('dwuklik otwiera modal; zamkniecie przywraca fokus bez opuszczania listy', async () => {
  const modal = new ModalFixture(async () => ({ok: true, text: async () => '<div></div>'}));
  await modal.otworz();
  assert.equal(modal.okno.open, true);
  assert.equal(modal.link.href, '/administracja/zawodnicy/7');
  assert.equal(modal.tresc.dzieci[0], modal.fragment);
  assert.equal(modal.usunietoPowrot, true);
  modal.przycisk.zdarzenia.click();
  assert.equal(modal.okno.open, false);
  assert.equal(modal.wiersz.fokus, true);
});

test('dwuklik na linku nie otwiera dodatkowego modalu', () => {
  const modal = new ModalFixture(() => { throw new Error('Nie powinno pobierac'); });
  modal.wiersz.zdarzenia.dblclick({target: {closest: () => ({})}});
  assert.equal(modal.okno.open, undefined);
});

test('blad HTTP pokazuje komunikat i pozostawia link nowej karty', async () => {
  const modal = new ModalFixture(async () => ({ok: false}));
  await modal.otworz();
  assert.match(modal.tresc.textContent, /Nie udało się wczytać/);
  assert.equal(modal.link.href, '/administracja/zawodnicy/7');
});

test('zamkniecie podczas pobierania anuluje zadanie', async () => {
  let sygnal;
  const modal = new ModalFixture((adres, opcje) => {
    sygnal = opcje.signal;
    return new Promise(() => {});
  });
  await modal.otworz();
  modal.okno.close();
  assert.equal(sygnal.aborted, true);
});

test('Enter na wierszu otwiera podglad', async () => {
  const modal = new ModalFixture(async () => ({ok: true, text: async () => ''}));
  let zatrzymano = false;
  modal.wiersz.zdarzenia.keydown({
    key: 'Enter', target: modal.wiersz, preventDefault: () => { zatrzymano = true; },
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(zatrzymano, true);
  assert.equal(modal.okno.open, true);
});


test('zakladki zawodnika otwieraja mecze po paginacji i obsluguja klawiature', () => {
  const klucze = ['profil', 'sezony', 'mecze'];
  const przyciski = klucze.map(klucz => {
    const element = new ElementFixture();
    element.dataset = {playerTab: klucz};
    element.setAttribute = (nazwa, wartosc) => { element[nazwa] = wartosc; };
    return element;
  });
  const panele = klucze.map(klucz => {
    const element = new ElementFixture();
    element.dataset = {playerPanel: klucz};
    return element;
  });
  const pasek = {hidden: true, querySelectorAll: () => przyciski};
  const korzen = {
    dataset: {activeTab: 'mecze'},
    querySelector: selektor => selektor === '[data-player-tabs]' ? pasek : null,
    querySelectorAll: () => panele,
  };
  runInNewContext(kod, {
    document: {
      querySelector: selektor => selektor === '[data-player-detail]' ? korzen : null,
      getElementById: () => null,
    },
  });
  assert.equal(pasek.hidden, false);
  assert.deepEqual(panele.map(p => p.hidden), [true, true, false]);
  przyciski[2].zdarzenia.keydown({key: 'Home', preventDefault() {}});
  assert.deepEqual(panele.map(p => p.hidden), [false, true, true]);
  assert.equal(przyciski[0].fokus, true);
});

test('paginacja pobiera karte w tym samym modalu', async () => {
  const adresy = [];
  const modal = new ModalFixture(async adres => {
    adresy.push(adres);
    return {ok: true, text: async () => '<div></div>'};
  });
  await modal.otworz();
  let zatrzymano = false;
  modal.tresc.zdarzenia.click({
    target: {closest: () => ({href: '/administracja/zawodnicy/7?zakladka=mecze&strona=2'})},
    button: 0,
    preventDefault() { zatrzymano = true; },
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(zatrzymano, true);
  assert.equal(modal.okno.open, true);
  assert.equal(adresy[1], '/administracja/zawodnicy/7?zakladka=mecze&strona=2');
});

test('podsumowanie inicjalizuje wykresy formy u siebie/na wyjezdzie i rozklad', async () => {
  const klucze = ['profil', 'sezony', 'mecze', 'podsumowanie'];
  const przyciski = klucze.map(klucz => {
    const element = new ElementFixture();
    element.dataset = {playerTab: klucz};
    return element;
  });
  const panele = klucze.map(klucz => {
    const element = new ElementFixture();
    element.dataset = {playerPanel: klucz};
    return element;
  });
  const trendWszystkie = new ElementFixture();
  trendWszystkie.dataset = {};
  const trendDom = new ElementFixture();
  trendDom.dataset = {};
  const trendWyjazd = new ElementFixture();
  trendWyjazd.dataset = {};
  const rozklad = new ElementFixture();
  rozklad.dataset = {};
  const zrodlo = new ElementFixture();
  zrodlo.textContent = JSON.stringify({
    mediana: 3,
    mediana_dom: 4,
    mediana_wyjazd: 2,
    punkty: [
      {id_mecz: 9, etykieta: '01.09.2026', sezon: '2026/2027', rozgrywki: 'Liga', bramki: 4, miejsce: 'dom'},
      {id_mecz: 10, etykieta: '08.09.2026', sezon: '2026/2027', rozgrywki: 'Liga', bramki: 2, miejsce: 'wyjazd'},
    ],
    rozklad: [{bramki: 2, mecze: 1, dom: 0, wyjazd: 1}, {bramki: 4, mecze: 1, dom: 1, wyjazd: 0}],
  });
  const pasek = {hidden: true, querySelectorAll: () => przyciski};
  const korzen = {
    dataset: {activeTab: 'podsumowanie', echartsUrl: '/echarts.js', playerMatchUrl: '/mecze/0'},
    querySelector: selektor => ({
      '[data-player-tabs]': pasek,
      '[data-player-trend-wszystkie]': trendWszystkie,
      '[data-player-trend-dom]': trendDom,
      '[data-player-trend-wyjazd]': trendWyjazd,
      '[data-player-distribution]': rozklad,
      '[data-player-analytics-data]': zrodlo,
    })[selektor] ?? null,
    querySelectorAll: () => panele,
  };
  const opcje = [];
  const echarts = {
    init: (element, motyw, ustawienia) => ({
      setOption: opcja => opcje.push({opcja, ustawienia}),
      on() {},
      resize() {},
    }),
  };
  runInNewContext(kod, {
    window: {echarts, matchMedia: () => ({matches: false})},
    document: {
      querySelector: selektor => selektor === '[data-player-detail]' ? korzen : null,
      getElementById: () => null,
    },
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(opcje.length, 4);
  assert.deepEqual(opcje.map(wpis => wpis.ustawienia.renderer), ['svg', 'svg', 'svg', 'svg']);
  assert.equal(opcje[0].opcja.series[0].markLine.data[0].yAxis, 3);
  assert.equal(opcje[0].opcja.series[0].data.length, 2);
  assert.equal(opcje[1].opcja.series[0].markLine.data[0].yAxis, 4);
  assert.equal(opcje[1].opcja.series[0].data.length, 1);
  assert.equal(opcje[2].opcja.series[0].markLine.data[0].yAxis, 2);
  assert.equal(opcje[0].opcja.aria.show, true);
  assert.equal(opcje[3].opcja.series[0].name, 'Wszystkie');
  assert.equal(opcje[3].opcja.series[1].name, 'U siebie');
  assert.equal(opcje[3].opcja.series[2].name, 'Na wyjeździe');
  assert.equal(opcje[3].opcja.series[0].data[0], 1);
  assert.equal(opcje[3].opcja.series[0].data[1], 1);
  assert.equal(opcje[3].opcja.series[1].data[0], 0);
  assert.equal(opcje[3].opcja.series[1].data[1], 1);
  assert.equal(opcje[3].opcja.series[2].data[0], 1);
  assert.equal(opcje[3].opcja.series[2].data[1], 0);
});

test('forma inicjalizuje wykresy formy u siebie/na wyjezdzie i boxplot z granicami sezonow', async () => {
  const klucze = ['profil', 'sezony', 'mecze', 'podsumowanie', 'forma'];
  const przyciski = klucze.map(klucz => {
    const element = new ElementFixture();
    element.dataset = {playerTab: klucz};
    return element;
  });
  const panele = klucze.map(klucz => {
    const element = new ElementFixture();
    element.dataset = {playerPanel: klucz};
    return element;
  });
  const formaDom = new ElementFixture();
  formaDom.dataset = {};
  const formaWyjazd = new ElementFixture();
  formaWyjazd.dataset = {};
  const boxplot = new ElementFixture();
  boxplot.dataset = {};
  const zrodlo = new ElementFixture();
  zrodlo.textContent = JSON.stringify({
    dom: {
      punkty: [
        {id_mecz: 1, etykieta: '01.09.2025', sezon: '2024/2025', bramki: 1, mediana_5: null, srednia_5: null, mediana_10: null},
        {id_mecz: 2, etykieta: '02.09.2026', sezon: '2025/2026', bramki: 2, mediana_5: null, srednia_5: null, mediana_10: null},
      ],
    },
    wyjazd: {punkty: []},
    sezony: [
      {sezon: '2024/2025', n: 1, mala_proba: true, mediana: 1, q1: 1, q3: 1, minimum: 1, maksimum: 1, odstajace: []},
      {sezon: '2025/2026', n: 1, mala_proba: true, mediana: 2, q1: 2, q3: 2, minimum: 2, maksimum: 2, odstajace: [5]},
    ],
  });
  const pasek = {hidden: true, querySelectorAll: () => przyciski};
  const korzen = {
    dataset: {activeTab: 'forma', echartsUrl: '/echarts.js', playerMatchUrl: '/mecze/0'},
    querySelector: selektor => ({
      '[data-player-tabs]': pasek,
      '[data-player-form-dom]': formaDom,
      '[data-player-form-wyjazd]': formaWyjazd,
      '[data-player-boxplot]': boxplot,
      '[data-player-forma-data]': zrodlo,
    })[selektor] ?? null,
    querySelectorAll: () => panele,
  };
  const opcje = [];
  const echarts = {
    init: (element, motyw, ustawienia) => ({
      setOption: opcja => opcje.push({opcja, ustawienia}),
      on() {},
      resize() {},
    }),
  };
  runInNewContext(kod, {
    window: {echarts, matchMedia: () => ({matches: false})},
    document: {
      querySelector: selektor => selektor === '[data-player-detail]' ? korzen : null,
      getElementById: () => null,
    },
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(opcje.length, 2);
  assert.deepEqual(opcje.map(wpis => wpis.ustawienia.renderer), ['svg', 'svg']);
  assert.equal(opcje[0].opcja.series[0].markLine.data[0].xAxis, 1);
  assert.equal(opcje[0].opcja.aria.show, true);
  assert.match(formaWyjazd.textContent, /Brak meczów na wyjeździe/);
  assert.equal(opcje[1].opcja.series[0].type, 'boxplot');
  const odstajace = opcje[1].opcja.series[1].data;
  assert.equal(odstajace.length, 1);
  assert.equal(odstajace[0][0], 1);
  assert.equal(odstajace[0][1], 5);
});
