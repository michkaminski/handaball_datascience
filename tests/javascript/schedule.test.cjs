const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = readFileSync('src/handball/interface/static/js/schedule.js', 'utf8');

class PoleFixture {
  constructor(poziom, wartosc) {
    this.dataset = {scheduleLevel: String(poziom)};
    this.value = wartosc;
    this.disabled = false;
    this.zdarzenia = {};
  }
  addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; }
}

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
  const pola = [new PoleFixture(0, '5'), new PoleFixture(1, '501'), new PoleFixture(2, '11'), new PoleFixture(3, '111')];
  const wiersz = new WierszFixture('/administracja/terminarz/204');
  let wyslane = 0;
  const formularz = {querySelectorAll: () => pola, submit: () => { wyslane += 1; }};
  const otwarte = [];
  const okno = {location: {href: '/administracja/terminarz'}, open: (...argumenty) => otwarte.push(argumenty)};
  const dokument = {
    querySelector: selektor => (selektor === '[data-schedule-filters]' ? formularz : null),
    querySelectorAll: selektor => (selektor === '.schedule-row[data-href]' ? [wiersz] : []),
  };
  runInNewContext(kod, {window: okno, document: dokument});
  const cel = interaktywny => ({closest: () => (interaktywny ? {} : null)});
  return {pola, wiersz, okno, otwarte, cel, wyslane: () => wyslane};
};

test('zmiana rozgrywek czysci runde i kolejke oraz wysyla formularz', () => {
  const {pola, wyslane} = przygotuj();
  pola[1].zdarzenia.change();
  assert.equal(pola[0].value, '5');
  assert.equal(pola[1].value, '501');
  assert.deepEqual([pola[2].value, pola[3].value], ['', '']);
  assert.equal(pola[2].disabled && pola[3].disabled, true);
  assert.equal(wyslane(), 1);
});

test('zmiana kolejki nie czysci wyzszych poziomow', () => {
  const {pola, wyslane} = przygotuj();
  pola[3].zdarzenia.change();
  assert.deepEqual(pola.map(pole => pole.value), ['5', '501', '11', '111']);
  assert.equal(wyslane(), 1);
});

test('klikniecie wiersza otwiera zapowiedz, a link zostaje przegladarce', () => {
  const {wiersz, okno, otwarte, cel} = przygotuj();
  assert.equal(wiersz.klasy.has('row-clickable'), true);
  wiersz.zdarzenia.click({target: cel(true)});
  assert.equal(okno.location.href, '/administracja/terminarz');
  wiersz.zdarzenia.click({target: cel(false), ctrlKey: true});
  assert.equal(otwarte.length, 1);
  wiersz.zdarzenia.click({target: cel(false)});
  assert.equal(okno.location.href, '/administracja/terminarz/204');
});

const przygotujOkno = ({ok = true, typowania = true} = {}) => {
  const zdarzenia = {};
  const zamkniecia = [];
  const przyciskiZamkniecia = [{addEventListener: (nazwa, akcja) => zamkniecia.push(akcja)}];
  const tresc = {
    textContent: '',
    dzieci: [],
    atrybuty: {},
    scrollTop: 5,
    replaceChildren(...dzieci) { this.dzieci = dzieci; this.textContent = ''; },
    setAttribute(nazwa, wartosc) { this.atrybuty[nazwa] = wartosc; },
    removeAttribute(nazwa) { delete this.atrybuty[nazwa]; },
  };
  const tytul = {textContent: ''};
  const nowaKarta = {href: ''};
  const okno = {
    open: false,
    otwarcia: 0,
    showModal() { this.open = true; this.otwarcia += 1; },
    close() { this.open = false; zdarzenia.close(); },
    addEventListener: (nazwa, akcja) => { zdarzenia[nazwa] = akcja; },
    querySelector: selektor => ({
      '[data-tips-content]': tresc,
      '[data-tips-dialog-title]': tytul,
      '[data-tips-open-tab]': nowaKarta,
    })[selektor],
    querySelectorAll: selektor => (selektor === '[data-tips-close]' ? przyciskiZamkniecia : []),
  };
  const link = {
    textContent: ' Seria 2 ',
    zdarzenia: {},
    fokus: 0,
    getAttribute: () => '/administracja/terminarz/typowania?id_kolejka=112',
    addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; },
    focus() { this.fokus += 1; },
  };
  const sekcja = {nazwa: 'typowania'};
  const pobrane = [];
  const dokument = {
    querySelector: selektor => (selektor === '[data-tips-dialog]' ? okno : null),
    querySelectorAll: selektor => (selektor === 'a[data-tips-link]' ? [link] : []),
  };
  class DOMParser {
    parseFromString(html) {
      return {querySelector: selektor => (selektor === '[data-schedule-tips]' && typowania ? sekcja : null), html};
    }
  }
  const window = {fetch: async (adres, opcje) => { pobrane.push([adres, opcje]); return {ok, text: async () => '<html></html>'}; }};
  runInNewContext(kod, {window, document: dokument, DOMParser, AbortController});
  return {okno, link, tresc, tytul, nowaKarta, pobrane, sekcja, zamkniecia};
};

test('klik kolejki otwiera okno i wstawia typowania', async () => {
  const {okno, link, tresc, tytul, nowaKarta, pobrane, sekcja} = przygotujOkno();
  let zablokowane = false;
  link.zdarzenia.click({button: 0, preventDefault: () => { zablokowane = true; }});
  assert.equal(zablokowane, true);
  assert.equal(okno.otwarcia, 1);
  assert.equal(tytul.textContent, 'Typowania — Seria 2');
  assert.equal(nowaKarta.href, '/administracja/terminarz/typowania?id_kolejka=112');
  await new Promise(setImmediate);
  assert.equal(pobrane[0][0], '/administracja/terminarz/typowania?id_kolejka=112');
  assert.deepEqual(tresc.dzieci, [sekcja]);
  assert.equal(tresc.atrybuty['aria-busy'], undefined);
});

test('klik z ctrl otwiera kolejke zwyklym linkiem', () => {
  const {okno, link} = przygotujOkno();
  let zablokowane = false;
  link.zdarzenia.click({button: 0, ctrlKey: true, preventDefault: () => { zablokowane = true; }});
  assert.equal(zablokowane, false);
  assert.equal(okno.otwarcia, 0);
});

test('blad odczytu pokazuje komunikat, a zamkniecie czysci okno i wraca do linku', async () => {
  const {okno, link, tresc, zamkniecia} = przygotujOkno({ok: false});
  link.zdarzenia.click({button: 0, preventDefault() {}});
  await new Promise(setImmediate);
  assert.match(tresc.textContent, /Nie udało się wczytać typowań/);
  zamkniecia[0]();
  assert.equal(okno.open, false);
  assert.deepEqual(tresc.dzieci, []);
  assert.equal(link.fokus, 1);
});
