const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = readFileSync('src/handball/interface/static/js/match_predictions.js', 'utf8');

class WierszFixture {
  constructor(adres) {
    this.dataset = {href: adres};
    this.zdarzenia = {};
    this.klasy = new Set();
    this.classList = {add: nazwa => this.klasy.add(nazwa)};
  }
  addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; }
}

const przygotuj = () => {
  const wiersz = new WierszFixture('/administracja/raporty/prognozy-meczow/203');
  const tabela = {querySelectorAll: selektor => (selektor === 'tbody tr[data-href]' ? [wiersz] : [])};
  const otwarte = [];
  const okno = {location: {href: '/administracja/raporty/prognozy-meczow'}, open: (...argumenty) => otwarte.push(argumenty)};
  const raport = {querySelector: () => null};
  runInNewContext(kod, {
    window: okno,
    document: {querySelector: selektor => (selektor === '[data-prediction-report] #predictions-table' ? tabela : raport.querySelector(selektor))},
  });
  const cel = interaktywny => ({closest: () => (interaktywny ? {} : null)});
  return {wiersz, okno, otwarte, cel};
};

test('wiersz jest klikalny i dostepny z klawiatury', () => {
  const {wiersz} = przygotuj();
  assert.equal(wiersz.klasy.has('row-clickable'), true);
  assert.equal(wiersz.tabIndex, 0);
});

test('klikniecie wiersza przechodzi do szczegolow prognozy', () => {
  const {wiersz, okno, cel} = przygotuj();
  wiersz.zdarzenia.click({target: cel(false)});
  assert.equal(okno.location.href, '/administracja/raporty/prognozy-meczow/203');
});

test('klikniecie linku w wierszu zostawia obsluge przegladarce', () => {
  const {wiersz, okno, otwarte, cel} = przygotuj();
  wiersz.zdarzenia.click({target: cel(true)});
  assert.equal(okno.location.href, '/administracja/raporty/prognozy-meczow');
  assert.equal(otwarte.length, 0);
});

test('ctrl klikniecie i srodkowy przycisk otwieraja nowa karte', () => {
  const {wiersz, okno, otwarte, cel} = przygotuj();
  wiersz.zdarzenia.click({target: cel(false), ctrlKey: true});
  wiersz.zdarzenia.auxclick({target: cel(false), button: 1});
  assert.deepEqual(otwarte, [['/administracja/raporty/prognozy-meczow/203', '_blank'], ['/administracja/raporty/prognozy-meczow/203', '_blank']]);
  assert.equal(okno.location.href, '/administracja/raporty/prognozy-meczow');
});

test('Enter na wierszu przechodzi do szczegolow', () => {
  const {wiersz, okno} = przygotuj();
  let zatrzymane = false;
  wiersz.zdarzenia.keydown({key: 'Enter', target: wiersz, preventDefault: () => { zatrzymane = true; }});
  assert.equal(zatrzymane, true);
  assert.equal(okno.location.href, '/administracja/raporty/prognozy-meczow/203');
});
