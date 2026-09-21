const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');
const kod = readFileSync('src/handball/interface/static/js/venue_details.js', 'utf8');

class ElementFixture {
  constructor(dataset = {}) {
    this.dataset = dataset;
    this.zdarzenia = {};
  }
  addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; }
  setAttribute(nazwa, wartosc) { this[nazwa] = wartosc; }
  focus() { this.fokus = true; }
}

test('karta hali otwiera wskazana zakladke i obsluguje klawiature', () => {
  const klucze = ['dane', 'mecze', 'zawodnicy', 'statystyki'];
  const przyciski = klucze.map(klucz => new ElementFixture({venueTab: klucz}));
  const panele = klucze.map(klucz => new ElementFixture({venuePanel: klucz}));
  const pasek = {hidden: true, querySelectorAll: () => przyciski};
  const korzen = {
    dataset: {activeTab: 'statystyki'},
    querySelector: () => pasek,
    querySelectorAll: () => panele,
  };
  runInNewContext(kod, {
    document: {querySelector: () => korzen},
  });
  assert.equal(pasek.hidden, false);
  assert.deepEqual(panele.map(panel => panel.hidden), [true, true, true, false]);
  przyciski[3].zdarzenia.keydown({key: 'Home', preventDefault() {}});
  assert.deepEqual(panele.map(panel => panel.hidden), [false, true, true, true]);
  assert.equal(przyciski[0].fokus, true);
});
