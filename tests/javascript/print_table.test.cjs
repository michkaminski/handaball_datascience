const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = readFileSync('src/handball/interface/static/js/print_table.js', 'utf8');

const komorka = (tagName, textContent, colSpan = 1) => ({tagName, textContent, colSpan});

const tabela = {
  rows: [
    {cells: [komorka('TH', 'Data'), komorka('TH', 'Gospodarz'), komorka('TH', 'Wynik')]},
    {cells: [komorka('TH', '  LOTTO Superliga · Seria 4 ', 3)]},
    {cells: [komorka('TD', '26.09.2026'), komorka('TD', '\n  <b>Kielce</b> & Co  '), komorka('TD', '30:30')]},
  ],
};

const przygotuj = ({blokada = false} = {}) => {
  const zdarzenia = {};
  const przycisk = {
    dataset: {printTable: '#tips-table', printTitle: 'Typowania meczów', printSubtitle: 'Okres: sob. 26.09.2026'},
    addEventListener: (nazwa, akcja) => { zdarzenia[nazwa] = akcja; },
  };
  const zapisane = [];
  const karta = {document: {open() { zapisane.push('open'); }, write(html) { zapisane.push(html); }, close() { zapisane.push('close'); }}};
  const otwarcia = [];
  const okno = {open: (...argumenty) => { otwarcia.push(argumenty); return blokada ? null : karta; }};
  const dokument = {
    querySelector: selektor => (selektor === '#tips-table' ? tabela : null),
    querySelectorAll: selektor => (selektor === '[data-print-table]' ? [przycisk] : []),
  };
  runInNewContext(kod, {document: dokument, window: okno});
  return {zdarzenia, zapisane, otwarcia};
};

test('przycisk otwiera nowa karte z czysta tabela tekstowa', () => {
  const {zdarzenia, zapisane, otwarcia} = przygotuj();
  zdarzenia.click();
  assert.deepEqual(otwarcia, [['', '_blank']]);
  assert.equal(zapisane[0], 'open');
  assert.equal(zapisane[2], 'close');
  const html = zapisane[1];
  assert.match(html, /<title>Typowania meczów<\/title>/);
  assert.match(html, /<p>Okres: sob\. 26\.09\.2026<\/p>/);
  assert.match(html, /<tr><th>Data<\/th><th>Gospodarz<\/th><th>Wynik<\/th><\/tr>/);
  assert.match(html, /<tr><th colspan="3">LOTTO Superliga · Seria 4<\/th><\/tr>/);
  assert.match(html, /<td>&lt;b&gt;Kielce&lt;\/b&gt; &amp; Co<\/td>/);
  assert.doesNotMatch(html, /<a |<img|<script|class=/);
});

test('zablokowane okno nie powoduje bledu', () => {
  const {zdarzenia, zapisane} = przygotuj({blokada: true});
  zdarzenia.click();
  assert.deepEqual(zapisane, []);
});

const przygotujSekcje = () => {
  const zdarzenia = {};
  const przycisk = {
    dataset: {
      printSection: '#kadra-druk',
      printStyles: '/statyczne/css/admin.css',
      printTitle: 'Kadry w sezonie 2025/2026: A — B',
      printSubtitle: 'Superliga · sob. 26.09.2026',
    },
    addEventListener: (nazwa, akcja) => { zdarzenia[nazwa] = akcja; },
  };
  const usuniete = [];
  const zamienione = [];
  const kopia = {
    outerHTML: '<div class="preview-grid"><table class="preview-squad"><td class="num top-scorer">13</td></table></div>',
    querySelectorAll: selektor => {
      if (selektor === '[data-print-exclude]') return [{remove: () => usuniete.push('x')}];
      if (selektor === 'a') {
        return [{
          textContent: 'Jan Kowalski',
          ownerDocument: {createElement: () => ({textContent: ''})},
          replaceWith: wezel => zamienione.push(wezel.textContent),
        }];
      }
      return [];
    },
  };
  const sekcja = {cloneNode: gleboko => (gleboko ? kopia : null)};
  const zapisane = [];
  const karta = {document: {open() {}, write(html) { zapisane.push(html); }, close() {}}};
  const dokument = {
    baseURI: 'http://localhost:5057/administracja/terminarz/204',
    querySelector: selektor => (selektor === '#kadra-druk' ? sekcja : null),
    querySelectorAll: selektor => (selektor === '[data-print-section]' ? [przycisk] : []),
  };
  runInNewContext(kod, {document: dokument, window: {open: () => karta}, URL});
  return {zdarzenia, zapisane, usuniete, zamienione};
};

test('druk skladow zachowuje style strony i rozciaga tabele', () => {
  const {zdarzenia, zapisane, usuniete, zamienione} = przygotujSekcje();
  zdarzenia.click();
  const html = zapisane[0];
  assert.match(html, /<link rel="stylesheet" href="http:\/\/localhost:5057\/statyczne\/css\/admin\.css">/);
  assert.match(html, /print-color-adjust:exact/);
  assert.match(html, /\.preview-grid\{display:block\}/);
  assert.match(html, /table\{width:100%\}/);
  assert.match(html, /th,td\{white-space:nowrap\}/);
  assert.match(html, /\.preview-prev small,\.preview-prev small\.muted\{display:inline\}/);
  assert.doesNotMatch(html, /font-size:(8|10\.5)px/);
  assert.match(html, /<h1>Kadry w sezonie 2025\/2026: A — B<\/h1>/);
  assert.match(html, /<td class="num top-scorer">13<\/td>/);
  assert.deepEqual(usuniete, ['x']);
  assert.deepEqual(zamienione, ['Jan Kowalski']);
});

test('dopasowanie zmniejsza skale az tresc zmiesci sie na jednej stronie A4', () => {
  const kontekst = {document: {querySelectorAll: () => []}, window: {}};
  runInNewContext(`${kod}\nglobalThis.D = DopasowanieDoStrony;`, kontekst);
  const strona = {style: {}, querySelector: () => null, querySelectorAll: () => [], getBoundingClientRect() { return {height: 2000 * Number(this.style.zoom)}; }};
  const dokument = {querySelector: selektor => (selektor === '[data-print-page]' ? strona : null)};
  const skala = new kontekst.D().dopasuj(dokument);
  assert.equal(skala, 0.51);
  assert.equal(strona.style.zoom, '0.51');
  assert.equal(strona.style.width, `${718 / 0.51}px`);
  const mala = {style: {}, querySelector: () => null, querySelectorAll: () => [], getBoundingClientRect: () => ({height: 500})};
  assert.equal(new kontekst.D().dopasuj({querySelector: () => mala}), 1);
  assert.equal(new kontekst.D().dopasuj({querySelector: () => null}), 1);
});

test('karta druku skladow ma skrypt dopasowania do strony A4', () => {
  const {zdarzenia, zapisane} = przygotujSekcje();
  zdarzenia.click();
  assert.match(zapisane[0], /<div data-print-page>/);
  assert.match(zapisane[0], /new DopasowanieDoStrony\(\)\.dopasuj\(document\)/);
  assert.match(zapisane[0], /@page\{size:A4 portrait;margin:10mm\}/);
});

test('druk bez uwag usuwa uwagi i ustawia tabele obok siebie', () => {
  const kontekst = {document: {querySelectorAll: () => []}, window: {}};
  runInNewContext(`${kod}\nglobalThis.B = WydrukSekcjiBuilder;`, kontekst);
  const usuniete = [];
  const kopia = {
    outerHTML: '<div class="preview-grid preview-hide-notes"></div>',
    classList: {contains: nazwa => nazwa === 'preview-hide-notes'},
    querySelectorAll: selektor => (selektor === '.preview-prev-note' ? [{remove: () => usuniete.push(1)}, {remove: () => usuniete.push(2)}] : []),
  };
  const budowniczy = new kontekst.B();
  budowniczy.tresc({cloneNode: () => kopia});
  assert.deepEqual(usuniete, [1, 2]);
  const html = budowniczy.htmlSekcji('', 'T', '', '');
  assert.match(html, /\.preview-grid\.preview-hide-notes\{display:grid;grid-template-columns:repeat\(2,minmax\(0,1fr\)\)/);
});

test('dopasowanie zmniejsza skale takze gdy tabela nie miesci sie w szerokosci kolumny', () => {
  const kontekst = {document: {querySelectorAll: () => []}, window: {}};
  runInNewContext(`${kod}
globalThis.D = DopasowanieDoStrony;`, kontekst);
  const strona = {style: {}, querySelector: () => null, getBoundingClientRect: () => ({height: 400})};
  const kolumna = {getBoundingClientRect: () => ({width: 359})};
  const tabela = {parentElement: kolumna, getBoundingClientRect: () => ({width: 500 * Number(strona.style.zoom)})};
  strona.querySelectorAll = selektor => (selektor === 'table' ? [tabela] : []);
  assert.equal(new kontekst.D().dopasuj({querySelector: () => strona}), 0.72);
});

test('uklad bez uwag drukuje sie poziomo na jednej kartce', () => {
  const kontekst = {document: {querySelectorAll: () => []}, window: {}};
  runInNewContext(`${kod}
globalThis.D = DopasowanieDoStrony;`, kontekst);
  const klasy = new Set();
  const strona = {
    style: {},
    classList: {add: nazwa => klasy.add(nazwa)},
    querySelector: selektor => (selektor === '.preview-hide-notes' ? {} : null),
    querySelectorAll: () => [],
    getBoundingClientRect() { return {height: 1000 * Number(this.style.zoom)}; },
  };
  const skala = new kontekst.D().dopasuj({querySelector: () => strona});
  assert.equal(klasy.has('print-landscape'), true);
  assert.equal(skala, 0.7);
  assert.equal(strona.style.width, `${1047 / 0.7}px`);
});
