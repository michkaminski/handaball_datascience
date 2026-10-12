const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = readFileSync('src/handball/interface/static/js/import_pobieranie.js', 'utf8');

const przygotujWybor = () => {
  const zdarzenia = {};
  const pola = [
    {name: 'mecze', checked: false},
    {name: 'mecze', checked: false},
    {name: 'mecze', checked: false},
  ];
  const stany = [{textContent: ''}, {textContent: ''}];
  const przyciski = {
    widoczne: {dataset: {zaznacz: 'widoczne'}, zdarzenia: {}},
    zadne: {dataset: {zaznacz: 'zadne'}, zdarzenia: {}},
    kolejka: {dataset: {}, zdarzenia: {}, closest: () => ({querySelectorAll: () => pola.slice(0, 2)})},
  };
  const formularz = {
    dataset: {limit: '2'},
    addEventListener(nazwa, akcja) { zdarzenia[nazwa] = akcja; },
    querySelectorAll(selektor) {
      if (selektor === 'input[name="mecze"]') return pola;
      if (selektor === '[data-stan-zaznaczenia]') return stany;
      if (selektor === '[data-zaznacz]') return [przyciski.widoczne, przyciski.zadne];
      if (selektor === '[data-zaznacz-kolejke]') return [przyciski.kolejka];
      return [];
    },
  };
  [przyciski.widoczne, przyciski.zadne, przyciski.kolejka].forEach(przycisk => {
    przycisk.addEventListener = (nazwa, akcja) => { przycisk.zdarzenia[nazwa] = akcja; };
  });
  const dokument = {
    querySelector: selektor => (selektor === '[data-import-z-terminarza]' ? formularz : null),
  };
  runInNewContext(kod, {document: dokument});
  return {zdarzenia, pola, stany, przyciski};
};

test('zaznaczenie meczow liczy wybor i blokuje pusta oraz zbyt dluga liste', () => {
  const {zdarzenia, pola, stany, przyciski} = przygotujWybor();
  assert.equal(stany[0].textContent, 'Zaznaczono: 0');
  przyciski.kolejka.zdarzenia.click();
  assert.equal(pola[0].checked && pola[1].checked, true);
  assert.equal(pola[2].checked, false);
  assert.equal(stany[1].textContent, 'Zaznaczono: 2');
  let zablokowane = false;
  zdarzenia.submit({preventDefault: () => { zablokowane = true; }});
  assert.equal(zablokowane, false);
  przyciski.widoczne.zdarzenia.click();
  zdarzenia.submit({preventDefault: () => { zablokowane = true; }});
  assert.equal(zablokowane, true);
  assert.match(stany[0].textContent, /najwyżej 2/);
  przyciski.zadne.zdarzenia.click();
  zablokowane = false;
  zdarzenia.submit({preventDefault: () => { zablokowane = true; }});
  assert.equal(zablokowane, true);
  assert.equal(stany[0].textContent, 'Zaznacz przynajmniej jeden mecz.');
});
