const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = readFileSync('src/handball/interface/static/js/goal_charts.js', 'utf8')
  + readFileSync('src/handball/interface/static/js/team_details.js', 'utf8');

class ElementFixture {
  constructor(dataset = {}, dzieci = []) {
    this.zdarzenia = {};
    this.dataset = dataset;
    this.dzieci = dzieci;
  }
  addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; }
  setAttribute(nazwa, wartosc) { this[nazwa] = wartosc; }
  focus() { this.fokus = true; }
  querySelectorAll() { return this.dzieci; }
}

const zrodlo = dane => {
  const element = new ElementFixture();
  element.textContent = JSON.stringify(dane);
  return element;
};

const przelacznik = (klucz, wartosci) => {
  const przyciski = wartosci.map(wartosc => new ElementFixture({[klucz]: wartosc}));
  const grupa = new ElementFixture({}, przyciski);
  grupa.hidden = true;
  return {grupa, przyciski};
};

const przygotujKarte = (aktywna, elementy = {}) => {
  const klucze = ['dane', 'sezony', 'mecze', 'zawodnicy', 'podsumowanie', 'forma'];
  const przyciski = klucze.map(klucz => new ElementFixture({teamTab: klucz}));
  const panele = klucze.map(klucz => new ElementFixture({teamPanel: klucz}));
  const pasek = {hidden: true, querySelectorAll: () => przyciski};
  const korzen = {
    dataset: {activeTab: aktywna, echartsUrl: '/echarts.js', teamMatchUrl: '/mecze/0'},
    querySelector: selektor => ({'[data-team-tabs]': pasek, ...elementy})[selektor] ?? null,
    querySelectorAll: selektor => ({'a[data-team-scroll]': [], '[data-team-panel]': panele})[selektor] ?? [],
  };
  const opcje = [];
  const echarts = {
    init: (element, motyw, ustawienia) => ({
      setOption: (opcja, ustawieniaAktualizacji) => opcje.push({element, opcja, ustawienia, ustawieniaAktualizacji}),
      on(nazwa, akcja) { element.zdarzeniaWykresu = {...element.zdarzeniaWykresu, [nazwa]: akcja}; },
      resize() {},
    }),
  };
  runInNewContext(kod, {
    window: {echarts, matchMedia: () => ({matches: false}), open: (...argumenty) => { korzen.otwarte = argumenty; }},
    document: {querySelector: selektor => (selektor === '[data-team-detail]' ? korzen : null)},
  });
  return {korzen, opcje, przyciski, panele, pasek};
};

const wykres = (opcje, element) => opcje.filter(wpis => wpis.element === element).map(wpis => wpis.opcja);
const poczekaj = () => new Promise(resolve => setImmediate(resolve));

const grupa = (znane, suma, srednia, mediana, dominanty) => ({mecze: znane, znane, suma, srednia, mediana, dominanty, q1: mediana - 1, q3: mediana + 1, minimum: mediana - 3, maksimum: mediana + 3});

const SEZONY = [
  {
    sezon: '2025/<i>2026</i>',
    zdobyte: grupa(6, 180, 30, 30, [30]),
    stracone: grupa(6, 150, 25, 24, [24, 26]),
    rozgrywki: [
      {rozgrywki: 'Liga', zdobyte: grupa(5, 150, 30, 30, [30]), stracone: grupa(5, 120, 24, 24, [24])},
      {rozgrywki: 'Puchar <b>', zdobyte: grupa(1, 30, 30, 30, [30]), stracone: grupa(1, 30, 30, 30, [30])},
    ],
  },
  {
    sezon: '2026/2027',
    zdobyte: grupa(2, 56, 28, 28, [28]),
    stracone: grupa(2, 60, 30, 30, [30]),
    rozgrywki: [{rozgrywki: 'Liga', zdobyte: grupa(2, 56, 28, 28, [28]), stracone: grupa(2, 60, 30, 30, [30])}],
  },
];

test('zakladki druzyny wybieraja panel z adresu i obsluguja klawiature', () => {
  const {pasek, panele, przyciski} = przygotujKarte('zawodnicy');
  assert.equal(pasek.hidden, false);
  assert.deepEqual(panele.map(panel => panel.hidden), [true, true, true, false, true, true]);
  przyciski[3].zdarzenia.keydown({key: 'End', preventDefault() {}});
  assert.equal(panele[5].hidden, false);
  assert.equal(przyciski[5].fokus, true);
  assert.equal(przyciski[5]['aria-selected'], 'true');
});

test('podsumowanie pokazuje miary sezonow dla zdobytych i straconych na jednym wykresie', async () => {
  const miary = new ElementFixture();
  const {grupa: przelacznikMiar, przyciski} = przelacznik('teamMeansView', ['linie', 'slupki']);
  const {opcje} = przygotujKarte('podsumowanie', {
    '[data-team-season-means]': miary,
    '[data-team-seasons-data]': zrodlo(SEZONY),
    '[data-team-means-toggle]': przelacznikMiar,
  });
  await poczekaj();
  const opcja = wykres(opcje, miary)[0];
  assert.equal(przelacznikMiar.hidden, false);
  assert.equal(opcja.aria.show, true);
  assert.deepEqual(Array.from(opcja.series, seria => seria.name), [
    'Średnia zdobytych', 'Mediana zdobytych', 'Dominanta zdobytych',
    'Średnia straconych', 'Mediana straconych', 'Dominanta straconych',
  ]);
  assert.equal(opcja.series[0].data[0], 30);
  assert.equal(opcja.series[3].data[1].itemStyle.color, '#ffffff');
  assert.deepEqual(Array.from(opcja.series[5].data, punkt => Array.from(punkt)), [[0, 24], [0, 26], [1, 30]]);
  const tooltip = opcja.tooltip.formatter([{seriesType: 'line', dataIndex: 0}]);
  assert.match(tooltip, /2025\/&lt;i&gt;2026&lt;\/i&gt;/);
  assert.match(tooltip, /różnica średnich: <b>\+5,0<\/b>/);
  assert.match(tooltip, /Puchar &lt;b&gt;/);
  assert.match(tooltip, /24, 26/);
  przyciski[1].zdarzenia.click();
  const slupki = wykres(opcje, miary)[1];
  assert.deepEqual(Array.from(slupki.series, seria => seria.type), ['bar', 'bar', 'bar', 'bar']);
  assert.ok(slupki.series[2].itemStyle.decal);
  assert.equal(przyciski[1]['aria-pressed'], 'true');
});

test('suma sezonu ma dwa stosy rozgrywek, etykiety Z i S oraz przelicza sumy po ukryciu rozgrywek', async () => {
  const sumy = new ElementFixture();
  const {opcje} = przygotujKarte('podsumowanie', {
    '[data-team-season-sums]': sumy,
    '[data-team-seasons-data]': zrodlo(SEZONY),
  });
  await poczekaj();
  const opcja = wykres(opcje, sumy)[0];
  const segmenty = opcja.series.filter(seria => !seria.id.startsWith('suma-'));
  assert.deepEqual(Array.from(segmenty, seria => seria.id), ['zdobyte-Liga', 'stracone-Liga', 'zdobyte-Puchar <b>', 'stracone-Puchar <b>']);
  assert.deepEqual(Array.from(segmenty[1].data), [120, 60]);
  assert.equal(segmenty[0].itemStyle.color, segmenty[1].itemStyle.color);
  assert.ok(segmenty[1].itemStyle.decal);
  assert.equal(segmenty[0].itemStyle.decal, undefined);
  const etykietaZ = opcja.series.find(seria => seria.id === 'suma-zdobyte');
  assert.equal(etykietaZ.label.formatter({dataIndex: 0}), 'Z 180');
  assert.match(opcja.tooltip.formatter([{dataIndex: 0}]), /Bramki w sezonie: <b>180:150<\/b>/);
  sumy.zdarzeniaWykresu.legendselectchanged({selected: {Liga: true, 'Puchar <b>': false}});
  const poUkryciu = wykres(opcje, sumy)[1].series;
  assert.equal(poUkryciu.find(seria => seria.id === 'suma-stracone').label.formatter({dataIndex: 0}), 'S 120');
  assert.match(opcja.tooltip.formatter([{dataIndex: 0}]), /150:120/);
});

test('rozklad pokazuje zdobyte i stracone i przelacza miejsce', async () => {
  const rozklad = new ElementFixture();
  const {grupa: miejsce, przyciski} = przelacznik('teamPlaceView', ['wszystkie', 'dom', 'wyjazd']);
  const {opcje} = przygotujKarte('podsumowanie', {
    '[data-team-distribution]': rozklad,
    '[data-team-distribution-data]': zrodlo([
      {bramki: 25, zdobyte: {wszystkie: 1, dom: 0, wyjazd: 1}, stracone: {wszystkie: 3, dom: 2, wyjazd: 1}},
      {bramki: 30, zdobyte: {wszystkie: 4, dom: 3, wyjazd: 1}, stracone: {wszystkie: 0, dom: 0, wyjazd: 0}},
    ]),
    '[data-team-place-toggle="distribution"]': miejsce,
  });
  await poczekaj();
  const opcja = wykres(opcje, rozklad)[0];
  assert.deepEqual(Array.from(opcja.series[1].data), [3, 0]);
  assert.ok(opcja.series[1].itemStyle.decal);
  przyciski[1].zdarzenia.click();
  const dom = wykres(opcje, rozklad)[1];
  assert.deepEqual(Array.from(dom.series[0].data), [0, 3]);
  assert.match(dom.aria.description, /mecze u siebie/);
});

const MECZE = (() => {
  const punkt = (id, sezon, zdobyte, stracone) => ({
    id_mecz: id, etykieta: `0${id}.09.2026`, sezon, rozgrywki: 'Liga', przeciwnik: 'Rywal', miejsce_etykieta: 'U siebie',
    wynik: `${zdobyte}:${stracone}`, rezultat: zdobyte > stracone ? 'Zwycięstwo' : 'Porażka',
    zdobyte, stracone, roznica: zdobyte - stracone,
    zdobyte_srednia_5: null, zdobyte_mediana_10: null, stracone_srednia_5: null, stracone_mediana_10: null, roznica_srednia_5: id === 2 ? -0.5 : null,
  });
  const wszystkie = [punkt(1, '2025/2026', 30, 25), punkt(2, '2026/2027', 24, 30)];
  return {
    wszystkie: {punkty: wszystkie, mediana_zdobytych: 27, mediana_straconych: 27.5, liczba: 2, trend_5: false, trend_10: false},
    dom: {punkty: [wszystkie[0]], mediana_zdobytych: 30, mediana_straconych: 25, liczba: 1, trend_5: false, trend_10: false},
    wyjazd: {punkty: [], mediana_zdobytych: null, mediana_straconych: null, liczba: 0, trend_5: false, trend_10: false},
  };
})();

test('forma rysuje mecze, bilans, forme kroczaca i rozstep dla obu serii', async () => {
  const mecze = new ElementFixture();
  const bilans = new ElementFixture();
  const kroczaca = new ElementFixture();
  const boxplot = new ElementFixture();
  const {grupa: miejsce, przyciski} = przelacznik('teamPlaceView', ['wszystkie', 'dom', 'wyjazd']);
  const {opcje, korzen} = przygotujKarte('forma', {
    '[data-team-matches]': mecze,
    '[data-team-balance]': bilans,
    '[data-team-rolling]': kroczaca,
    '[data-team-boxplot]': boxplot,
    '[data-team-matches-data]': zrodlo(MECZE),
    '[data-team-place-toggle="matches"]': miejsce,
    '[data-team-spread-data]': zrodlo([
      {sezon: '2025/2026', zdobyte: {n: 1, mala_proba: true, mediana: 30, q1: 30, q3: 30, minimum: 30, maksimum: 30, odstajace: []}, stracone: {n: 1, mala_proba: true, mediana: 25, q1: 25, q3: 25, minimum: 25, maksimum: 25, odstajace: [40]}},
    ]),
  });
  await poczekaj();
  const opcjaMeczow = wykres(opcje, mecze)[0];
  assert.deepEqual(Array.from(opcjaMeczow.series, seria => seria.name), ['Bramki zdobyte', 'Bramki stracone']);
  assert.equal(opcjaMeczow.series[1].lineStyle.type, 'dashed');
  assert.equal(opcjaMeczow.series[1].markLine.data[0].yAxis, 27.5);
  assert.match(opcjaMeczow.tooltip.formatter([{dataIndex: 1}]), /Wynik: 24:30 \(Porażka\)\nZdobyte: 24 · Stracone: 30/);
  mecze.zdarzeniaWykresu.click({data: {idMecz: 2}});
  assert.equal(korzen.otwarte[0], '/mecze/2');
  przyciski[2].zdarzenia.click();
  const wyjazd = opcje.filter(wpis => wpis.element === mecze)[1];
  assert.equal(wyjazd.ustawieniaAktualizacji.notMerge, true);
  assert.match(wyjazd.opcja.title.text, /mecze na wyjeździe/);
  const opcjaBilansu = wykres(opcje, bilans)[0];
  assert.deepEqual(Array.from(opcjaBilansu.series[0].data, punkt => punkt.value), [5, -6]);
  assert.ok(opcjaBilansu.series[0].data[1].itemStyle.decal);
  assert.equal(opcjaBilansu.series[1].data[1], -0.5);
  const opcjaKroczacej = wykres(opcje, kroczaca)[0];
  assert.deepEqual(Array.from(opcjaKroczacej.series, seria => seria.id), ['tlo-zdobyte', 'tlo-stracone', 'zdobyte-5', 'stracone-5']);
  assert.equal(opcjaKroczacej.series[2].markLine.data[0].xAxis, 1);
  const opcjaRozstepu = wykres(opcje, boxplot)[0];
  assert.deepEqual(Array.from(opcjaRozstepu.series, seria => seria.type), ['boxplot', 'boxplot', 'scatter', 'scatter']);
  assert.deepEqual(Array.from(opcjaRozstepu.series[3].data, punkt => Array.from(punkt)), [[0, 40]]);
  assert.equal(opcjaRozstepu.xAxis.data[0], '2025/2026 *');
});
