const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');
const kod = readFileSync('src/handball/interface/static/js/matches.js', 'utf8');

class ElementFixture {
  constructor() {
    this.zdarzenia = {};
    this.dataset = {href: '/administracja/mecze/12543'};
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
    this.fragment = {querySelector: selektor => selektor === '[data-detail-navigation]' ? ({remove: () => { this.usunietoPowrot = true; }}) : null};
    this.okno.querySelector = selektor => selektor === '[data-detail-content]' ? this.tresc : this.link;
    this.okno.querySelectorAll = () => [this.przycisk];
    const tabela = {querySelectorAll: () => [this.wiersz]};
    const fragment = this.fragment;
    runInNewContext(kod, {
      URLSearchParams, AbortController,
      DOMParser: class { parseFromString() { return {querySelector: () => fragment}; } },
      window: {fetch: pobierz},
      document: {
        querySelector: () => null,
        getElementById: id => ({
          'matches-table': tabela,
          'match-detail-dialog': this.okno,
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
  assert.equal(modal.link.href, '/administracja/mecze/12543');
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
  assert.equal(modal.link.href, '/administracja/mecze/12543');
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

test('zakladki pokazuja jeden panel i obsluguja klawiature', () => {
  const przyciski = ['basic', 'stats', 'rosters'].map(nazwa => {
    const przycisk = new ElementFixture();
    przycisk.getAttribute = () => nazwa;
    przycisk.setAttribute = (klucz, wartosc) => { przycisk[klucz] = wartosc; };
    return przycisk;
  });
  const panele = ['basic', 'stats', 'rosters'].map(id => Object.assign(new ElementFixture(), {id}));
  const pasek = {hidden: true, querySelectorAll: () => przyciski};
  const korzen = {
    querySelector: () => pasek,
    querySelectorAll: () => panele,
  };
  runInNewContext(kod, {
    document: {
      querySelector: selektor => selektor === '[data-match-detail]' ? korzen : null,
      getElementById: () => null,
    },
  });
  assert.equal(pasek.hidden, false);
  assert.deepEqual(panele.map(panel => panel.hidden), [false, true, true]);
  przyciski[2].zdarzenia.click();
  assert.deepEqual(panele.map(panel => panel.hidden), [true, true, false]);
  assert.equal(przyciski[2]['aria-selected'], 'true');
  przyciski[2].zdarzenia.keydown({key: 'ArrowRight', preventDefault() {}});
  assert.deepEqual(panele.map(panel => panel.hidden), [false, true, true]);
  assert.equal(przyciski[0].fokus, true);
});
