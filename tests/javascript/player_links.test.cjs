const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = readFileSync('src/handball/interface/static/js/goal_charts.js', 'utf8')
  + readFileSync('src/handball/interface/static/js/player_details.js', 'utf8')
  + readFileSync('src/handball/interface/static/js/matches.js', 'utf8');

class ElementFixture {
  constructor() {
    this.zdarzenia = {};
  }
  addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; }
}

const przygotuj = ({bezOkna = false} = {}) => {
  const link = new ElementFixture();
  link.href = '/administracja/zawodnicy/7';
  const okno = {
    showModal() { this.open = true; },
    querySelector: () => ({setAttribute() {}, removeAttribute() {}, replaceChildren() {}, addEventListener() {}}),
    querySelectorAll: () => [],
    addEventListener() {},
  };
  const otwarcia = [];
  const karty = [];
  const zegary = new Map();
  let licznik = 0;
  const korzen = {
    querySelector: selektor => (selektor === '[data-player-modal-dialog]' && !bezOkna ? okno : null),
    querySelectorAll: selektor => (selektor === 'a[data-player-modal-link]' ? [link] : []),
  };
  runInNewContext(kod, {
    URL, AbortController,
    setTimeout: (akcja, czas) => { licznik += 1; zegary.set(licznik, {akcja, czas}); return licznik; },
    clearTimeout: numer => zegary.delete(numer),
    window: {open: (...argumenty) => karty.push(argumenty), fetch: adres => { otwarcia.push({adres}); return new Promise(() => {}); }, location: {href: 'http://localhost/'}},
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
  return {link, okno, otwarcia, karty, zegary, klik, uplyw};
};

test('pojedyncze klikniecie zawodnika otwiera okno ze szczegolami po krotkim opoznieniu', () => {
  const {okno, otwarcia, karty, zegary, klik, uplyw} = przygotuj();
  const zdarzenie = klik();
  assert.equal(zdarzenie.zatrzymane, true);
  assert.equal(otwarcia.length, 0);
  assert.equal([...zegary.values()][0].czas, 250);
  uplyw();
  assert.deepEqual(otwarcia, [{adres: '/administracja/zawodnicy/7'}]);
  assert.equal(okno.open, true);
  assert.equal(karty.length, 0);
});

test('dwuklik otwiera karte zawodnika w nowej karcie bez okna modalnego', () => {
  const {link, otwarcia, karty, zegary, klik, uplyw} = przygotuj();
  klik();
  klik({detail: 2});
  link.zdarzenia.dblclick({preventDefault() {}});
  assert.equal(zegary.size, 0);
  uplyw();
  assert.equal(otwarcia.length, 0);
  assert.deepEqual(karty.map(argumenty => Array.from(argumenty)), [['/administracja/zawodnicy/7', '_blank', 'noopener']]);
});

test('Enter na linku otwiera okno od razu, a Ctrl+klik zostaje przegladarce', () => {
  const {otwarcia, klik} = przygotuj();
  klik({detail: 0});
  assert.equal(otwarcia.length, 1);
  const zCtrl = klik({ctrlKey: true});
  assert.equal(zCtrl.zatrzymane, undefined);
  assert.equal(otwarcia.length, 1);
});

test('bez okna modalnego link dziala jak zwykly odnosnik', () => {
  const {link} = przygotuj({bezOkna: true});
  assert.equal(link.zdarzenia.click, undefined);
});
