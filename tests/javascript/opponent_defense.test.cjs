const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');
const kod = readFileSync('src/handball/interface/static/js/opponent_defense.js', 'utf8');

class ElementFixture {
  constructor() {
    this.zdarzenia = {};
    this.dataset = {};
  }
  addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; }
  querySelectorAll() { return []; }
}

function uruchom(dane) {
  const klasy = new ElementFixture();
  const boxplot = new ElementFixture();
  const prawdopodobienstwa = new ElementFixture();
  const scatter = new ElementFixture();
  const zrodla = {
    '[data-defense-klasy]': klasy,
    '[data-defense-klasy-data]': {textContent: JSON.stringify(dane.klasy)},
    '[data-defense-boxplot]': boxplot,
    '[data-defense-boxplot-data]': {textContent: JSON.stringify(dane.boxplot)},
    '[data-defense-prawdopodobienstwa]': prawdopodobienstwa,
    '[data-defense-prawdopodobienstwa-data]': {textContent: JSON.stringify(dane.prawdopodobienstwa)},
    '[data-defense-scatter]': scatter,
    '[data-defense-scatter-data]': {textContent: JSON.stringify(dane.scatter)},
  };
  const korzen = {
    dataset: {echartsUrl: '/echarts.js', playerMatchUrl: '/mecze/0'},
    querySelector: selektor => zrodla[selektor] ?? null,
  };
  const opcje = [];
  const echarts = {
    init: (element, motyw, ustawienia) => ({
      setOption: opcja => opcje.push({element, opcja, ustawienia}),
      on() {},
      resize() {},
    }),
  };
  runInNewContext(kod, {
    window: {echarts, matchMedia: () => ({matches: false})},
    document: {querySelector: selektor => selektor === '[data-defense-report]' ? korzen : null},
  });
  return opcje;
}

test('cztery wykresy analizy defensywy inicjalizuja sie z danych JSON', async () => {
  const opcje = uruchom({
    klasy: [{klasa: 'Mocna', srednia: 3.6, n: 41}],
    boxplot: [{klasa: 'Mocna', n: 41, minimum: 1, kwartyl_pierwszy: 2, mediana: 3, kwartyl_trzeci: 5, maksimum: 8, odstajace: [10]}],
    prawdopodobienstwa: [{klasa: 'Mocna', progi: [{prog: 3, udzial: 0.5}, {prog: 5, udzial: 0.2}]}],
    scatter: [{x: 0.95, y: 4, id_mecz: 55, etykieta: 'Rywal', sezon: '2026/2027', klasa: 'Mocna'}],
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(opcje.length, 4);
  assert.deepEqual(opcje.map(o => o.ustawienia.renderer), ['svg', 'svg', 'svg', 'svg']);
  assert.equal(opcje[0].opcja.series[0].data[0], 3.6);
  assert.equal(opcje[1].opcja.series[0].type, 'boxplot');
  assert.equal(opcje[1].opcja.series[0].data[0][0], 1);
  assert.equal(opcje[1].opcja.series[0].data[0][4], 8);
  assert.equal(opcje[1].opcja.series[1].data[0][1], 10);
  assert.equal(opcje[2].opcja.series[0].name, 'P(3+)');
  assert.equal(opcje[2].opcja.series[1].name, 'P(5+)');
  assert.equal(opcje[2].opcja.series[0].data[0], 50);
  assert.equal(opcje[3].opcja.series[0].type, 'scatter');
  assert.equal(opcje[3].opcja.series[0].data[0].value[0], 0.95);
  assert.equal(opcje[3].opcja.series[0].data[0].value[1], 4);
  assert.equal(opcje[3].opcja.series[0].data[0].idMecz, 55);
});
