const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = readFileSync('src/handball/interface/static/js/classification_details.js', 'utf8');

class ElementFixture {
  constructor() {
    this.zdarzenia = {};
  }
  addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; }
}

const przygotuj = () => {
  const link = new ElementFixture();
  link.href = '/administracja/druzyny/77';
  const tresc = Object.assign(new ElementFixture(), {setAttribute() {}, removeAttribute() {}, replaceChildren() {}});
  const linkKarty = {};
  const okno = Object.assign(new ElementFixture(), {
    showModal() { this.open = true; },
    querySelector: selektor => (selektor === '[data-team-content]' ? tresc : linkKarty),
    querySelectorAll: () => [],
  });
  const pobrane = [];
  const karty = [];
  const zegary = new Map();
  let licznik = 0;
  const korzen = {
    querySelector: selektor => (selektor === '[data-team-modal-dialog]' ? okno : null),
    querySelectorAll: selektor => (selektor === 'a[data-team-modal-link]' ? [link] : []),
  };
  runInNewContext(kod, {
    URL, URLSearchParams, AbortController,
    setTimeout: (akcja, czas) => { licznik += 1; zegary.set(licznik, {akcja, czas}); return licznik; },
    clearTimeout: numer => zegary.delete(numer),
    window: {
      open: (...argumenty) => karty.push(argumenty),
      fetch: adres => { pobrane.push(adres); return new Promise(() => {}); },
      location: {href: 'http://localhost/administracja/tabele/40'},
    },
    document: {querySelector: selektor => (selektor === '[data-classification-detail]' ? korzen : null)},
  });
  const klik = (dodatkowe = {}) => {
    const zdarzenie = {detail: 1, button: 0, preventDefault() { this.zatrzymane = true; }, ...dodatkowe};
    link.zdarzenia.click(zdarzenie);
    return zdarzenie;
  };
  const uplyw = () => [...zegary.entries()].forEach(([numer, {akcja}]) => { zegary.delete(numer); akcja(); });
  return {link, okno, linkKarty, pobrane, karty, zegary, klik, uplyw};
};

test('pojedyncze klikniecie druzyny otwiera okno modalne po krotkim opoznieniu', () => {
  const {okno, linkKarty, pobrane, karty, zegary, klik, uplyw} = przygotuj();
  const zdarzenie = klik();
  assert.equal(zdarzenie.zatrzymane, true);
  assert.equal(pobrane.length, 0);
  assert.equal([...zegary.values()][0].czas, 250);
  uplyw();
  assert.equal(okno.open, true);
  assert.deepEqual(pobrane, ['/administracja/druzyny/77']);
  assert.equal(linkKarty.href, '/administracja/druzyny/77');
  assert.equal(karty.length, 0);
});

test('dwuklik druzyny otwiera nowa karte bez okna modalnego', () => {
  const {link, okno, pobrane, karty, zegary, klik} = przygotuj();
  klik();
  klik({detail: 2});
  link.zdarzenia.dblclick({preventDefault() {}});
  assert.equal(zegary.size, 0);
  assert.equal(okno.open, undefined);
  assert.equal(pobrane.length, 0);
  assert.deepEqual(karty, [['/administracja/druzyny/77', '_blank', 'noopener']]);
});

test('klikniecie z klawiatura otwiera okno od razu, a z modyfikatorem zostawia przegladarke', () => {
  const {okno, pobrane, klik} = przygotuj();
  const zModyfikatorem = klik({ctrlKey: true});
  assert.equal(zModyfikatorem.zatrzymane, undefined);
  klik({detail: 0});
  assert.equal(okno.open, true);
  assert.deepEqual(pobrane, ['/administracja/druzyny/77']);
});
