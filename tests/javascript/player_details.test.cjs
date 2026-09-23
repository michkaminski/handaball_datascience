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

const przygotujKarte = (aktywna, elementy) => {
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
  const pasek = {hidden: true, querySelectorAll: () => przyciski};
  const korzen = {
    dataset: {activeTab: aktywna, echartsUrl: '/echarts.js', playerMatchUrl: '/mecze/0'},
    querySelector: selektor => ({'[data-player-tabs]': pasek, ...elementy})[selektor] ?? null,
    querySelectorAll: selektor => selektor === 'a[data-player-scroll]' ? (elementy.linki ?? []) : panele,
  };
  const opcje = [];
  const echarts = {
    init: (element, motyw, ustawienia) => ({
      setOption: opcja => opcje.push({element, opcja, ustawienia}),
      on() {},
      resize() {},
    }),
  };
  return {korzen, opcje, echarts, przyciski, panele};
};

const uruchomKarte = (korzen, echarts, window = {}) => {
  runInNewContext(kod, {
    window: {echarts, matchMedia: () => ({matches: false}), ...window},
    document: {
      querySelector: selektor => selektor === '[data-player-detail]' ? korzen : null,
      getElementById: () => null,
    },
  });
};

const pustyElement = () => {
  const element = new ElementFixture();
  element.dataset = {};
  return element;
};

const zrodloDanych = dane => {
  const element = pustyElement();
  element.textContent = JSON.stringify(dane);
  return element;
};

test('podsumowanie inicjalizuje tylko wykres rozkladu bramek', async () => {
  const rozklad = pustyElement();
  const trend = pustyElement();
  const {korzen, opcje, echarts} = przygotujKarte('podsumowanie', {
    '[data-player-distribution]': rozklad,
    '[data-player-distribution-data]': zrodloDanych([
      {bramki: 2, mecze: 1, dom: 0, wyjazd: 1},
      {bramki: 4, mecze: 1, dom: 1, wyjazd: 0},
    ]),
    '[data-player-trend-wszystkie]': trend,
  });
  uruchomKarte(korzen, echarts);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(opcje.length, 1);
  assert.equal(opcje[0].element, rozklad);
  assert.equal(opcje[0].ustawienia.renderer, 'svg');
  assert.equal(opcje[0].opcja.aria.show, true);
  assert.deepEqual(Array.from(opcje[0].opcja.series, seria => seria.name), ['Wszystkie', 'U siebie', 'Na wyjeździe']);
  assert.deepEqual(Array.from(opcje[0].opcja.series[0].data), [1, 1]);
  assert.deepEqual(Array.from(opcje[0].opcja.series[1].data), [0, 1]);
  assert.deepEqual(Array.from(opcje[0].opcja.series[2].data), [1, 0]);
  assert.equal(trend.dataset.chartReady, undefined);
});

test('podsumowanie rysuje srednia, mediane i dominanty wedlug sezonu i rozgrywek z tooltipem', async () => {
  const sezony = pustyElement();
  const {korzen, opcje, echarts} = przygotujKarte('podsumowanie', {
    '[data-player-season-stats]': sezony,
    '[data-player-season-stats-data]': zrodloDanych([
      {sezon: '2024/2025', rozgrywki: 'Liga <b>A</b>', mecze: 4, znane: 3, suma: 10, srednia: 3.3333, mediana: 4, dominanty: [4], q1: 3, q3: 4, minimum: 2, maksimum: 4},
      {sezon: '2025/2026', rozgrywki: 'Puchar', mecze: 2, znane: 2, suma: 4, srednia: 2, mediana: 2, dominanty: [1, 3], q1: 1.5, q3: 2.5, minimum: 1, maksimum: 3},
    ]),
  });
  uruchomKarte(korzen, echarts);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(opcje.length, 1);
  const opcja = opcje[0].opcja;
  assert.equal(opcje[0].ustawienia.renderer, 'svg');
  assert.equal(opcja.aria.show, true);
  assert.deepEqual(Array.from(opcja.series, seria => seria.name), ['Średnia', 'Mediana', 'Dominanta']);
  assert.equal(opcja.series[0].data[0].value, 3.3333);
  assert.equal(opcja.series[0].data[0].itemStyle.color, '#ffffff');
  assert.equal(opcja.series[1].data[1].value, 2);
  assert.equal(opcja.dataZoom, undefined);
  assert.deepEqual(Array.from(opcja.series[2].data, punkt => Array.from(punkt)), [[0, 4], [1, 1], [1, 3]]);
  assert.match(opcja.xAxis.data[0], /^2024\/2025\n/);
  const tooltip = opcja.tooltip.formatter([{seriesType: 'line', dataIndex: 0}]);
  assert.match(tooltip, /2024\/2025/);
  assert.match(tooltip, /Liga &lt;b&gt;A&lt;\/b&gt;/);
  assert.match(tooltip, /3,33/);
  assert.match(tooltip, /3 z 4/);
  assert.match(tooltip, /mała próba/);
  const tooltipDominanty = opcja.tooltip.formatter({seriesType: 'scatter', value: [1, 3]});
  assert.match(tooltipDominanty, /Puchar/);
  assert.match(tooltipDominanty, /1, 3/);
});

test('forma inicjalizuje trendy, forme krocząca, boxplot i defensywe rywali', async () => {
  const trendWszystkie = pustyElement();
  const trendDom = pustyElement();
  const trendWyjazd = pustyElement();
  const formaWszystkie = pustyElement();
  const formaDom = pustyElement();
  const formaWyjazd = pustyElement();
  const boxplot = pustyElement();
  const defensywa = pustyElement();
  const {korzen, opcje, echarts} = przygotujKarte('forma', {
    '[data-player-trend-wszystkie]': trendWszystkie,
    '[data-player-trend-dom]': trendDom,
    '[data-player-trend-wyjazd]': trendWyjazd,
    '[data-player-trend-data]': zrodloDanych({
      mediana: 3,
      mediana_dom: 4,
      mediana_wyjazd: 2,
      punkty: [
        {id_mecz: 9, etykieta: '01.09.2026', sezon: '2026/2027', rozgrywki: 'Liga', bramki: 4, miejsce: 'dom'},
        {id_mecz: 10, etykieta: '08.09.2026', sezon: '2026/2027', rozgrywki: 'Liga', bramki: 2, miejsce: 'wyjazd'},
      ],
    }),
    '[data-player-form-wszystkie]': formaWszystkie,
    '[data-player-form-dom]': formaDom,
    '[data-player-form-wyjazd]': formaWyjazd,
    '[data-player-boxplot]': boxplot,
    '[data-player-forma-data]': zrodloDanych({
      dom: {
        punkty: [
          {id_mecz: 1, etykieta: '01.09.2025', sezon: '2024/2025', bramki: 1, mediana_5: null, srednia_5: null, mediana_10: null},
          {id_mecz: 2, etykieta: '02.09.2026', sezon: '2025/2026', bramki: 2, mediana_5: null, srednia_5: null, mediana_10: null},
        ],
      },
      wszystkie: {
        punkty: [
          {id_mecz: 1, etykieta: '01.09.2025', sezon: '2024/2025', bramki: 1, mediana_5: null, srednia_5: null, mediana_10: null},
          {id_mecz: 3, etykieta: '01.09.2026', sezon: '2025/2026', bramki: 7, mediana_5: null, srednia_5: null, mediana_10: null},
          {id_mecz: 2, etykieta: '02.09.2026', sezon: '2025/2026', bramki: 2, mediana_5: null, srednia_5: null, mediana_10: null},
        ],
      },
      wyjazd: {punkty: []},
      sezony: [
        {sezon: '2024/2025', n: 1, mala_proba: true, mediana: 1, q1: 1, q3: 1, minimum: 1, maksimum: 1, odstajace: []},
        {sezon: '2025/2026', n: 1, mala_proba: true, mediana: 2, q1: 2, q3: 2, minimum: 2, maksimum: 2, odstajace: [5]},
      ],
    }),
    '[data-defense-summary]': defensywa,
    '[data-defense-summary-data]': zrodloDanych([
      {klasa: 'Bardzo mocna', srednia: 2.9, n: 22},
      {klasa: 'Bardzo słaba', srednia: 6.1, n: 19},
    ]),
  });
  uruchomKarte(korzen, echarts);
  await new Promise(resolve => setImmediate(resolve));
  const wykres = element => opcje.find(wpis => wpis.element === element).opcja;
  assert.equal(opcje.length, 7);
  assert.ok(opcje.every(wpis => wpis.ustawienia.renderer === 'svg'));
  assert.equal(wykres(trendWszystkie).series[0].markLine.data[0].yAxis, 3);
  assert.equal(wykres(trendWszystkie).series[0].data.length, 2);
  assert.equal(wykres(trendDom).series[0].markLine.data[0].yAxis, 4);
  assert.equal(wykres(trendDom).series[0].data.length, 1);
  assert.equal(wykres(trendWyjazd).series[0].markLine.data[0].yAxis, 2);
  assert.equal(wykres(formaWszystkie).series[0].data.length, 3);
  assert.equal(wykres(formaWszystkie).series[0].markLine.data[0].xAxis, 1);
  assert.equal(wykres(formaDom).series[0].markLine.data[0].xAxis, 1);
  assert.equal(wykres(formaDom).aria.show, true);
  assert.match(formaWyjazd.textContent, /Brak meczów na wyjeździe/);
  assert.equal(wykres(boxplot).series[0].type, 'boxplot');
  assert.deepEqual(Array.from(wykres(boxplot).series[1].data, punkt => Array.from(punkt)), [[1, 5]]);
  assert.deepEqual(Array.from(wykres(defensywa).series[0].data), [2.9, 6.1]);
  assert.equal(wykres(defensywa).xAxis.data[0], 'Bardzo mocna');
});

test('spis tresci i powrot do spisu przewijaja bez zmiany adresu', () => {
  const sekcja = pustyElement();
  let przewiniecie;
  sekcja.scrollIntoView = opcje => { przewiniecie = opcje; };
  const link = pustyElement();
  link.getAttribute = () => '#player-forma-sezony';
  const spis = pustyElement();
  spis.scrollIntoView = () => { spis.przewiniety = true; };
  const powrot = pustyElement();
  powrot.getAttribute = () => '#player-forma-spis';
  const {korzen, echarts} = przygotujKarte('profil', {
    '[data-player-toc]': spis,
    '#player-forma-sezony': sekcja,
    '#player-forma-spis': spis,
    linki: [link, powrot],
  });
  uruchomKarte(korzen, echarts, {matchMedia: () => ({matches: true})});
  let zatrzymano = false;
  link.zdarzenia.click({preventDefault: () => { zatrzymano = true; }});
  assert.equal(zatrzymano, true);
  assert.equal(przewiniecie.behavior, 'auto');
  assert.equal(przewiniecie.block, 'start');
  assert.equal(sekcja.fokus, true);
  powrot.zdarzenia.click({preventDefault() {}});
  assert.equal(spis.przewiniety, true);
  assert.equal(spis.fokus, true);
});
