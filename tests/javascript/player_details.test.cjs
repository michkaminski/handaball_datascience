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
