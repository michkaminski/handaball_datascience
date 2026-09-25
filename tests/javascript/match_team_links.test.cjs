const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = ['goal_charts', 'player_details', 'team_details', 'classification_details', 'matches']
  .map(nazwa => readFileSync(`src/handball/interface/static/js/${nazwa}.js`, 'utf8'))
  .join('\n');

class ElementFixture {
  constructor() {
    this.zdarzenia = {};
  }
  addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; }
}

const przygotuj = () => {
  const link = new ElementFixture();
  link.href = '/administracja/druzyny/22';
  const okno = {
    showModal() { this.open = true; },
    querySelector: () => ({setAttribute() {}, removeAttribute() {}, replaceChildren() {}, addEventListener() {}}),
    querySelectorAll: () => [],
    addEventListener() {},
  };
  const pobrania = [];
  const karty = [];
  const zegary = new Map();
  let licznik = 0;
  const korzen = {
    querySelector: selektor => (selektor === '[data-team-modal-dialog]' ? okno : null),
    querySelectorAll: selektor => (selektor === 'a[data-team-modal-link]' ? [link] : []),
  };
  runInNewContext(kod, {
    URL, AbortController,
    setTimeout: (akcja, czas) => { licznik += 1; zegary.set(licznik, {akcja, czas}); return licznik; },
    clearTimeout: numer => zegary.delete(numer),
    window: {open: (...argumenty) => karty.push(argumenty), fetch: adres => { pobrania.push(adres); return new Promise(() => {}); }, location: {href: 'http://localhost/'}},
    document: {
      querySelector: selektor => (selektor === '[data-match-detail]' ? korzen : null),
      getElementById: () => null,
    },
  });
  const klik = (dodatkowe = {}) => {
    const zdarzenie = {detail: 1, button: 0, preventDefault() { this.zatrzymane = true; }, ...dodatkowe};
    link.zdarzenia.click(zdarzenie);
    return zdarzenie;
  };
  const uplyw = () => [...zegary.entries()].forEach(([numer, {akcja}]) => { zegary.delete(numer); akcja(); });
  return {link, okno, pobrania, karty, zegary, klik, uplyw};
};

test('klikniecie druzyny w szczegolach meczu otwiera karte druzyny w oknie', () => {
  const {okno, pobrania, karty, klik, uplyw} = przygotuj();
  assert.equal(klik().zatrzymane, true);
  assert.equal(pobrania.length, 0);
  uplyw();
  assert.deepEqual(pobrania, ['/administracja/druzyny/22']);
  assert.equal(okno.open, true);
  assert.equal(karty.length, 0);
});

test('dwuklik druzyny w szczegolach meczu otwiera karte w nowej karcie', () => {
  const {link, okno, pobrania, karty, zegary, klik, uplyw} = przygotuj();
  klik();
  klik({detail: 2});
  link.zdarzenia.dblclick({preventDefault() {}});
  assert.equal(zegary.size, 0);
  uplyw();
  assert.equal(pobrania.length, 0);
  assert.equal(okno.open, undefined);
  assert.deepEqual(karty.map(argumenty => Array.from(argumenty)), [['/administracja/druzyny/22', '_blank', 'noopener']]);
});
