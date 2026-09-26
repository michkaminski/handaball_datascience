const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = readFileSync('src/handball/interface/static/js/match_preview.js', 'utf8');

const przygotuj = () => {
  const formularz = {action: '', wyslane: 0, submit() { this.wyslane += 1; }};
  const pole = (sekcja) => ({
    zdarzenia: {},
    addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; },
    closest: selektor => (selektor === 'section[id]' && sekcja ? {id: sekcja} : null),
  });
  const kadra = pole('kadra');
  const okres = pole('bezposrednie');
  const przyciski = [{hidden: false}, {hidden: false}];
  const dokument = {
    querySelector: selektor => (selektor === '[data-preview-options]' ? formularz : null),
    querySelectorAll: selektor => ({
      '[data-preview-apply]': przyciski,
      '[data-preview-auto]': [kadra, okres],
    })[selektor] || [],
  };
  runInNewContext(kod, {document: dokument});
  return {formularz, kadra, okres, przyciski};
};

test('zmiana opcji wysyla formularz i wraca do sekcji', () => {
  const {formularz, kadra, okres, przyciski} = przygotuj();
  assert.deepEqual(przyciski.map(p => p.hidden), [true, true]);
  kadra.zdarzenia.change();
  assert.equal(formularz.action, '#kadra');
  okres.zdarzenia.change();
  assert.equal(formularz.action, '#bezposrednie');
  assert.equal(formularz.wyslane, 2);
});

test('checkbox ukrywa i pokazuje uwagi o innym klubie i lidze', () => {
  const klasy = new Set();
  const siatka = {classList: {toggle: (nazwa, wlacz) => (wlacz ? klasy.add(nazwa) : klasy.delete(nazwa))}};
  const pole = {
    checked: true,
    dataset: {previewNotesToggle: '#kadra-druk'},
    zdarzenia: {},
    addEventListener(nazwa, akcja) { this.zdarzenia[nazwa] = akcja; },
  };
  const dokument = {
    querySelector: selektor => (selektor === '#kadra-druk' ? siatka : null),
    querySelectorAll: selektor => (selektor === '[data-preview-notes-toggle]' ? [pole] : []),
  };
  runInNewContext(kod, {document: dokument});
  assert.equal(klasy.has('preview-hide-notes'), true);
  pole.checked = false;
  pole.zdarzenia.change();
  assert.equal(klasy.has('preview-hide-notes'), false);
});
