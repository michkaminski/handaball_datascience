const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {test} = require('node:test');

const kod = readFileSync('src/handball/interface/static/js/matches.js', 'utf8');
const klucz = 'hds.mecze.filtry.v1';

class ListaMeczowFixture {
  constructor(zapis, search = '') {
    this.dane = new Map(zapis === undefined ? [] : [[klucz, zapis]]);
    this.adres = null;
    this.lokalizacja = {
      pathname: '/administracja/mecze',
      search,
      replace: adres => { this.adres = adres; },
    };
    this.magazyn = {
      getItem: nazwa => this.dane.get(nazwa) ?? null,
      setItem: (nazwa, wartosc) => this.dane.set(nazwa, wartosc),
      removeItem: nazwa => this.dane.delete(nazwa),
    };
  }

  uruchom() {
    const formularz = {
      elements: {
        namedItem: nazwa => nazwa === 'id_sezon'
          ? {options: [{value: ''}, {value: '195'}]}
          : {},
      },
    };
    runInNewContext(kod, {
      URLSearchParams,
      window: {location: this.lokalizacja, localStorage: this.magazyn},
      document: {
        querySelector: selektor => selektor === '[data-match-filters]' ? formularz : null,
        getElementById: () => null,
      },
    });
  }
}

test('przywraca filtry i pomija strone oraz obce parametry', () => {
  const lista = new ListaMeczowFixture(JSON.stringify({
    id_sezon: '195', druzyna: 'Wisła Płock', strona: '8', obcy: 'wartosc',
  }));
  lista.uruchom();
  const parametry = new URLSearchParams(lista.adres.split('?')[1]);
  assert.equal(parametry.get('id_sezon'), '195');
  assert.equal(parametry.get('druzyna'), 'Wisła Płock');
  assert.equal(parametry.size, 2);
});

test('jawny link ma pierwszenstwo i zapisuje tylko filtry', () => {
  const lista = new ListaMeczowFixture('{"druzyna":"Kielce"}', '?druzyna=Lubin&strona=3');
  lista.uruchom();
  assert.equal(lista.adres, null);
  assert.deepEqual(JSON.parse(lista.dane.get(klucz)), {druzyna: 'Lubin'});
});

test('wyczyszczenie usuwa pamiec i kolejny powrot jej nie przywraca', () => {
  const lista = new ListaMeczowFixture('{"id_sezon":"195"}', '?id_sezon=');
  lista.uruchom();
  assert.equal(lista.dane.has(klucz), false);
  lista.lokalizacja.search = '';
  lista.uruchom();
  assert.equal(lista.adres, null);
});

test('pomija nieaktualny sezon oraz uszkodzony zapis', () => {
  for (const zapis of ['{"id_sezon":"999"}', '{', 'null', '[]', '{"druzyna":123}']) {
    const lista = new ListaMeczowFixture(zapis);
    lista.uruchom();
    assert.equal(lista.adres, null);
  }
});

test('niedostepny magazyn nie przerywa dzialania strony', () => {
  const lista = new ListaMeczowFixture();
  lista.magazyn.getItem = () => { throw new Error('Storage blocked'); };
  assert.doesNotThrow(() => lista.uruchom());
  assert.equal(lista.adres, null);
});