(() => {
  const {zaladujECharts, escapujHtml, formatujLiczbe} = globalThis.HandballWykresyBramek;

  const PROG_MALEJ_PROBY = 5;
  const KOLOR_ZDOBYTE = '#2b6ea4';
  const KOLOR_STRACONE = '#b04646';
  const WZOR_KOLOR = 'rgba(255,255,255,0.55)';
  const WZOR_KRESKI = {symbol: 'rect', symbolSize: 1, dashArrayX: [1, 0], dashArrayY: [2, 5], rotation: Math.PI / 4, color: WZOR_KOLOR};
  const WZOR_KROPKI = {symbol: 'circle', symbolSize: 0.7, dashArrayX: [[1, 4]], dashArrayY: [4], color: WZOR_KOLOR};
  const PALETA_ROZGRYWEK = ['#3a7c67', '#9f6a15', '#7c3aed', '#0e7490', '#64748b', '#c2410c'];
  const SERIE_BILANSU = [
    {klucz: 'wygrane', nazwa: 'Zwycięstwa', kolor: '#2f7e6c', wzor: null},
    {klucz: 'remisy', nazwa: 'Remisy', kolor: '#9f6a15', wzor: WZOR_KROPKI},
    {klucz: 'porazki', nazwa: 'Porażki', kolor: KOLOR_STRACONE, wzor: WZOR_KRESKI},
  ];
  const MIEJSCA = {wszystkie: 'wszystkie mecze', dom: 'mecze u siebie', wyjazd: 'mecze na wyjeździe'};

  const ograniczonyRuch = () => Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
  const bilans = wartosc => `${wartosc > 0 ? '+' : ''}${wartosc}`;
  const zeZnakiem = wartosc => (wartosc === null || wartosc === undefined ? '—' : `${wartosc > 0 ? '+' : ''}${formatujLiczbe(wartosc)}`);

  const tooltipHtml = formatter => ({
    trigger: 'axis',
    axisPointer: {type: 'shadow'},
    confine: true,
    backgroundColor: '#ffffff',
    borderColor: '#c8d4dd',
    borderWidth: 1,
    padding: 0,
    extraCssText: 'box-shadow:0 6px 18px rgba(16,40,63,.16);border-radius:8px;',
    formatter,
  });

  const osSezonow = sezony => ({
    type: 'category',
    data: sezony.map(sezon => sezon.sezon),
    axisLabel: {rotate: sezony.length > 6 ? 30 : 0, hideOverlap: true},
  });

  const osMeczow = punkty => ({
    type: 'category',
    data: punkty.map(punkt => punkt.etykieta),
    axisLabel: {rotate: 35, hideOverlap: true},
  });

  const animacja = () => ({
    animation: !ograniczonyRuch(),
    animationDuration: 450,
    animationDurationUpdate: 400,
    animationEasing: 'cubicOut',
  });

  const graniceSezonow = punkty => punkty.flatMap((punkt, indeks) => (indeks > 0 && punkt.sezon !== punkty[indeks - 1].sezon ? [{xAxis: indeks}] : []));

  class WykresyBramekDruzynyController {
    constructor(korzen) {
      this.korzen = korzen;
    }

    async narysuj(selektor, zrodloSelektor, rysuj) {
      const element = this.korzen.querySelector(selektor);
      const zrodlo = this.korzen.querySelector(zrodloSelektor);
      if (!element || !zrodlo || element.dataset.chartReady) return;
      element.dataset.chartReady = 'true';
      try {
        const echarts = await zaladujECharts(this.korzen.dataset.echartsUrl);
        const wykres = echarts.init(element, null, {renderer: 'svg'});
        rysuj(wykres, JSON.parse(zrodlo.textContent), element);
        if (typeof ResizeObserver === 'function') new ResizeObserver(() => wykres.resize()).observe(element);
      } catch {
        element.textContent = 'Nie udało się narysować wykresu. Dane tabelaryczne pozostają dostępne poniżej.';
      }
    }

    przelacznik(selektor, klucz, przyZmianie) {
      const grupa = this.korzen.querySelector(selektor);
      if (!grupa) return;
      const przyciski = Array.from(grupa.querySelectorAll('button'));
      grupa.hidden = false;
      przyciski.forEach(przycisk => {
        przycisk.addEventListener('click', () => {
          przyciski.forEach(inny => inny.setAttribute('aria-pressed', String(inny === przycisk)));
          przyZmianie(przycisk.dataset[klucz]);
        });
      });
    }

    miejsce(nazwa, przyZmianie) {
      this.przelacznik(`[data-team-place-toggle="${nazwa}"]`, 'teamPlaceView', przyZmianie);
    }

    otworzMeczPoKliknieciu(wykres) {
      wykres.on('click', parametry => {
        const id = parametry.data?.idMecz;
        if (id) window.open(this.korzen.dataset.teamMatchUrl.replace(/0$/, String(id)), '_blank', 'noopener');
      });
    }
  }

  class PodsumowanieDruzynyController extends WykresyBramekDruzynyController {
    uruchom() {
      return Promise.all([
        this.narysuj('[data-team-results]', '[data-team-results-data]', (wykres, sezony) => this.rysujBilans(wykres, sezony)),
        this.narysuj('[data-team-season-means]', '[data-team-seasons-data]', (wykres, sezony) => this.rysujMiary(wykres, sezony)),
        this.narysuj('[data-team-season-sums]', '[data-team-seasons-data]', (wykres, sezony) => this.rysujSumy(wykres, sezony)),
        this.narysuj('[data-team-distribution]', '[data-team-distribution-data]', (wykres, rozklad) => this.rysujRozklad(wykres, rozklad)),
      ]);
    }

    opisBilansu(sezon) {
      const procent = sezon.rozegrane ? `${formatujLiczbe(100 * sezon.wygrane / sezon.rozegrane)}%` : '—';
      return `<div class="player-tooltip"><div class="player-tooltip-title">${escapujHtml(sezon.sezon)}</div>`
        + `<div class="player-tooltip-sub">Mecze rozegrane: <b>${escapujHtml(sezon.rozegrane)}</b> · zwycięstwa: ${escapujHtml(procent)}</div><table>`
        + SERIE_BILANSU.map(seria => `<tr><th>${escapujHtml(seria.nazwa)}</th><td>${escapujHtml(sezon[seria.klucz])}</td></tr>`).join('')
        + `<tr><th>Bramki</th><td>${escapujHtml(`${sezon.zdobyte}:${sezon.stracone}`)}</td></tr></table></div>`;
    }

    rysujBilans(wykres, sezony) {
      wykres.setOption({
        ...animacja(),
        aria: {show: true, description: 'Wykres słupkowy skumulowany: liczba zwycięstw, remisów i porażek drużyny w kolejnych sezonach, rozróżnionych kolorem i wzorem.'},
        legend: {top: 0},
        grid: {left: 42, right: 18, top: 36, bottom: 48},
        tooltip: tooltipHtml(parametry => {
          const sezon = sezony[(Array.isArray(parametry) ? parametry[0] : parametry)?.dataIndex];
          return sezon ? this.opisBilansu(sezon) : '';
        }),
        xAxis: osSezonow(sezony),
        yAxis: {type: 'value', minInterval: 1, name: 'Mecze'},
        series: SERIE_BILANSU.map(seria => ({
          id: seria.klucz,
          name: seria.nazwa,
          type: 'bar',
          stack: 'bilans',
          barMaxWidth: 34,
          emphasis: {focus: 'series'},
          itemStyle: {color: seria.kolor, decal: seria.wzor ?? undefined},
          data: sezony.map(sezon => sezon[seria.klucz]),
        })),
      });
      return wykres;
    }

    opisMiar(sezon) {
      const z = sezon.zdobyte;
      const s = sezon.stracone;
      const dominanta = grupa => (grupa.dominanty.length ? grupa.dominanty.join(', ') : '—');
      const wiersze = [
        ['Średnia', formatujLiczbe(z.srednia, 2), formatujLiczbe(s.srednia, 2)],
        ['Mediana', formatujLiczbe(z.mediana), formatujLiczbe(s.mediana)],
        ['Dominanta', dominanta(z), dominanta(s)],
        ['Q1–Q3', z.q1 === null ? '—' : `${formatujLiczbe(z.q1)}–${formatujLiczbe(z.q3)}`, s.q1 === null ? '—' : `${formatujLiczbe(s.q1)}–${formatujLiczbe(s.q3)}`],
        ['Suma', z.suma ?? '—', s.suma ?? '—'],
      ];
      const roznica = z.srednia === null || s.srednia === null ? null : z.srednia - s.srednia;
      const malaProba = z.znane < PROG_MALEJ_PROBY ? '<span class="player-tooltip-flag">mała próba</span>' : '';
      const rozgrywki = sezon.rozgrywki.map(grupa => '<tr>'
        + `<th>${escapujHtml(grupa.rozgrywki)}</th>`
        + `<td>${escapujHtml(grupa.zdobyte.znane)}</td>`
        + `<td>${escapujHtml(formatujLiczbe(grupa.zdobyte.srednia))}</td>`
        + `<td>${escapujHtml(formatujLiczbe(grupa.stracone.srednia))}</td></tr>`).join('');
      return `<div class="player-tooltip"><div class="player-tooltip-title">${escapujHtml(sezon.sezon)}${malaProba}</div>`
        + `<div class="player-tooltip-sub">Mecze: ${escapujHtml(z.znane)} · różnica średnich: <b>${escapujHtml(zeZnakiem(roznica))}</b></div>`
        + '<table class="player-tooltip-breakdown"><thead><tr><th>Miara</th><td>Zdobyte</td><td>Stracone</td></tr></thead><tbody>'
        + wiersze.map(([etykieta, zdobyte, stracone]) => `<tr><th>${escapujHtml(etykieta)}</th><td>${escapujHtml(zdobyte)}</td><td>${escapujHtml(stracone)}</td></tr>`).join('')
        + '</tbody></table><div class="player-tooltip-section">Podział na rozgrywki (średnie)</div>'
        + '<table class="player-tooltip-breakdown"><thead><tr><th>Rozgrywki</th><td>Mecze</td><td>Zdob.</td><td>Strac.</td></tr></thead>'
        + `<tbody>${rozgrywki}</tbody></table></div>`;
    }

    punktMiary(sezon, wartosc, kolor) {
      if (wartosc === null || sezon.zdobyte.znane >= PROG_MALEJ_PROBY) return wartosc;
      return {value: wartosc, itemStyle: {color: '#ffffff', borderColor: kolor, borderWidth: 2}};
    }

    opcjeMiar(sezony, tryb) {
      const przejscie = {enabled: !ograniczonyRuch()};
      const wspolne = {
        ...animacja(),
        legend: {top: 0, type: 'scroll'},
        grid: {left: 42, right: 18, top: 44, bottom: 48},
        tooltip: tooltipHtml(parametry => {
          const lista = Array.isArray(parametry) ? parametry : [parametry];
          const kategoria = lista.find(parametr => parametr.seriesType !== 'scatter');
          const sezon = sezony[kategoria ? kategoria.dataIndex : lista[0]?.value?.[0]];
          return sezon ? this.opisMiar(sezon) : '';
        }),
        xAxis: osSezonow(sezony),
        yAxis: {type: 'value', name: 'Bramki na mecz', scale: true},
        dataZoom: sezony.length > 20 ? [{type: 'inside'}, {type: 'slider', height: 14, bottom: 2}] : undefined,
      };
      const rodzaje = [['zdobyte', 'zdobytych', KOLOR_ZDOBYTE], ['stracone', 'straconych', KOLOR_STRACONE]];
      if (tryb === 'slupki') {
        return {
          ...wspolne,
          aria: {show: true, description: 'Wykres słupkowy średniej i mediany bramek zdobytych i straconych przez drużynę na mecz w kolejnych sezonach; słupki straconych mają ukośny wzór.'},
          series: rodzaje.flatMap(([rodzaj, przymiotnik, kolor]) => [
            {id: `srednia-${rodzaj}`, name: `Średnia ${przymiotnik}`, type: 'bar', barMaxWidth: 14, universalTransition: przejscie, emphasis: {focus: 'series'}, itemStyle: {color: kolor, decal: rodzaj === 'stracone' ? WZOR_KRESKI : undefined}, data: sezony.map(sezon => sezon[rodzaj].srednia)},
            {id: `mediana-${rodzaj}`, name: `Mediana ${przymiotnik}`, type: 'bar', barMaxWidth: 14, universalTransition: przejscie, emphasis: {focus: 'series'}, itemStyle: {color: `${kolor}99`, decal: rodzaj === 'stracone' ? WZOR_KRESKI : WZOR_KROPKI}, data: sezony.map(sezon => sezon[rodzaj].mediana)},
          ]),
        };
      }
      return {
        ...wspolne,
        aria: {show: true, description: 'Wykres liniowy średniej i mediany oraz dominanty bramek zdobytych (niebieskie) i straconych (czerwone) przez drużynę na mecz w kolejnych sezonach.'},
        series: rodzaje.flatMap(([rodzaj, przymiotnik, kolor]) => [
          {id: `srednia-${rodzaj}`, name: `Średnia ${przymiotnik}`, type: 'line', symbol: 'circle', symbolSize: 8, smooth: 0.15, lineStyle: {width: 2.5, color: kolor}, itemStyle: {color: kolor}, universalTransition: przejscie, emphasis: {focus: 'series', scale: 1.5}, data: sezony.map(sezon => this.punktMiary(sezon, sezon[rodzaj].srednia, kolor))},
          {id: `mediana-${rodzaj}`, name: `Mediana ${przymiotnik}`, type: 'line', symbol: 'rect', symbolSize: 7, lineStyle: {width: 2, type: 'dashed', color: kolor}, itemStyle: {color: kolor}, universalTransition: przejscie, emphasis: {focus: 'series', scale: 1.5}, data: sezony.map(sezon => this.punktMiary(sezon, sezon[rodzaj].mediana, kolor))},
          {id: `dominanta-${rodzaj}`, name: `Dominanta ${przymiotnik}`, type: 'scatter', symbol: rodzaj === 'zdobyte' ? 'diamond' : 'triangle', symbolSize: 11, itemStyle: {color: kolor, opacity: 0.75}, universalTransition: przejscie, emphasis: {focus: 'series', scale: 1.4}, data: sezony.flatMap((sezon, indeks) => sezon[rodzaj].dominanty.map(wartosc => [indeks, wartosc]))},
        ]),
      };
    }

    rysujMiary(wykres, sezony) {
      wykres.setOption(this.opcjeMiar(sezony, 'linie'));
      this.przelacznik('[data-team-means-toggle]', 'teamMeansView', tryb => wykres.setOption(this.opcjeMiar(sezony, tryb), {replaceMerge: ['series']}));
      return wykres;
    }

    opisSum(sezon, ukryte) {
      const widoczne = sezon.rozgrywki.filter(grupa => !ukryte.has(grupa.rozgrywki));
      const suma = rodzaj => widoczne.reduce((wynik, grupa) => wynik + (grupa[rodzaj].suma ?? 0), 0);
      const wiersze = widoczne.map(grupa => '<tr>'
        + `<th>${escapujHtml(grupa.rozgrywki)}</th>`
        + `<td>${escapujHtml(grupa.zdobyte.znane)}</td>`
        + `<td>${escapujHtml(grupa.zdobyte.suma ?? '—')}</td>`
        + `<td>${escapujHtml(grupa.stracone.suma ?? '—')}</td>`
        + `<td>${escapujHtml(bilans((grupa.zdobyte.suma ?? 0) - (grupa.stracone.suma ?? 0)))}</td></tr>`).join('');
      return `<div class="player-tooltip"><div class="player-tooltip-title">${escapujHtml(sezon.sezon)}</div>`
        + `<div class="player-tooltip-sub">Bramki w sezonie: <b>${escapujHtml(`${suma('zdobyte')}:${suma('stracone')}`)}</b></div>`
        + '<div class="player-tooltip-section">Podział na rozgrywki</div>'
        + '<table class="player-tooltip-breakdown"><thead><tr><th>Rozgrywki</th><td>Mecze</td><td>Zdob.</td><td>Strac.</td><td>Bilans</td></tr></thead>'
        + `<tbody>${wiersze}</tbody></table></div>`;
    }

    serieSum(sezony, nazwy, kolory, ukryte) {
      const sumy = rodzaj => sezony.map(sezon => sezon.rozgrywki
        .filter(grupa => !ukryte.has(grupa.rozgrywki))
        .reduce((wynik, grupa) => wynik + (grupa[rodzaj].suma ?? 0), 0));
      const etykiety = [['zdobyte', 'Z'], ['stracone', 'S']].map(([rodzaj, skrot]) => {
        const wartosci = sumy(rodzaj);
        return {
          id: `suma-${rodzaj}`,
          name: `suma-${rodzaj}`,
          type: 'bar',
          stack: rodzaj,
          barMaxWidth: 28,
          silent: true,
          itemStyle: {color: 'transparent'},
          tooltip: {show: false},
          label: {show: sezony.length <= 14, position: 'top', fontSize: 10, color: rodzaj === 'zdobyte' ? KOLOR_ZDOBYTE : KOLOR_STRACONE, formatter: parametry => `${skrot} ${wartosci[parametry.dataIndex]}`},
          data: sezony.map(() => 0),
        };
      });
      const segmenty = nazwy.flatMap(nazwa => ['zdobyte', 'stracone'].map(rodzaj => ({
        id: `${rodzaj}-${nazwa}`,
        name: nazwa,
        type: 'bar',
        stack: rodzaj,
        barMaxWidth: 28,
        barGap: '12%',
        emphasis: {focus: 'series'},
        itemStyle: {color: kolory.get(nazwa), decal: rodzaj === 'stracone' ? WZOR_KRESKI : undefined, borderColor: '#ffffff', borderWidth: 0.5},
        data: sezony.map(sezon => sezon.rozgrywki.find(grupa => grupa.rozgrywki === nazwa)?.[rodzaj].suma ?? null),
      })));
      return [...segmenty, ...etykiety];
    }

    rysujSumy(wykres, sezony) {
      const nazwy = [...new Set(sezony.flatMap(sezon => sezon.rozgrywki.map(grupa => grupa.rozgrywki)))];
      const kolory = new Map(nazwy.map((nazwa, indeks) => [nazwa, PALETA_ROZGRYWEK[indeks % PALETA_ROZGRYWEK.length]]));
      let ukryte = new Set();
      wykres.setOption({
        ...animacja(),
        aria: {show: true, description: 'Wykres słupkowy: przy każdym sezonie lewy słupek to bramki zdobyte, prawy — stracone z ukośnym wzorem; segmenty to rozgrywki, a etykiety Z i S podają sumy sezonu.'},
        legend: {top: 0, left: 'center', width: '88%', type: 'scroll', data: nazwy, formatter: nazwa => (nazwa.length > 26 ? `${nazwa.slice(0, 25)}…` : nazwa)},
        grid: {left: 48, right: 18, top: 56, bottom: 48},
        tooltip: tooltipHtml(parametry => {
          const sezon = sezony[(Array.isArray(parametry) ? parametry[0] : parametry)?.dataIndex];
          return sezon ? this.opisSum(sezon, ukryte) : '';
        }),
        xAxis: osSezonow(sezony),
        yAxis: {type: 'value', minInterval: 1, name: 'Bramki'},
        dataZoom: sezony.length > 20 ? [{type: 'inside'}, {type: 'slider', height: 14, bottom: 2}] : undefined,
        series: this.serieSum(sezony, nazwy, kolory, ukryte),
      });
      wykres.on('legendselectchanged', zdarzenie => {
        ukryte = new Set(nazwy.filter(nazwa => zdarzenie.selected[nazwa] === false));
        wykres.setOption({series: this.serieSum(sezony, nazwy, kolory, ukryte).filter(seria => seria.id.startsWith('suma-'))});
      });
      return wykres;
    }

    opcjeRozkladu(rozklad, miejsce) {
      return {
        ...animacja(),
        aria: {show: true, description: `Histogram liczby meczów według liczby bramek zdobytych (niebieskie) i straconych (czerwone, z wzorem) przez drużynę: ${MIEJSCA[miejsce]}.`},
        legend: {top: 0},
        grid: {left: 42, right: 18, top: 34, bottom: 38},
        tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
        xAxis: {type: 'category', name: 'Bramki', data: rozklad.map(punkt => punkt.bramki)},
        yAxis: {type: 'value', minInterval: 1, name: 'Mecze'},
        series: [
          {id: 'zdobyte', name: 'Mecze z tyloma zdobytymi', type: 'bar', barMaxWidth: 16, emphasis: {focus: 'series'}, itemStyle: {color: KOLOR_ZDOBYTE}, data: rozklad.map(punkt => punkt.zdobyte[miejsce])},
          {id: 'stracone', name: 'Mecze z tyloma straconymi', type: 'bar', barMaxWidth: 16, emphasis: {focus: 'series'}, itemStyle: {color: KOLOR_STRACONE, decal: WZOR_KRESKI}, data: rozklad.map(punkt => punkt.stracone[miejsce])},
        ],
      };
    }

    rysujRozklad(wykres, rozklad) {
      wykres.setOption(this.opcjeRozkladu(rozklad, 'wszystkie'));
      this.miejsce('distribution', miejsce => wykres.setOption(this.opcjeRozkladu(rozklad, miejsce)));
      return wykres;
    }
  }

  class FormaDruzynyController extends WykresyBramekDruzynyController {
    uruchom() {
      return Promise.all([
        this.narysuj('[data-team-matches]', '[data-team-matches-data]', (wykres, dane) => this.zMiejscem(wykres, dane, 'matches', (d, m) => this.opcjeMeczow(d, m))),
        this.narysuj('[data-team-balance]', '[data-team-matches-data]', (wykres, dane) => this.zMiejscem(wykres, dane, 'balance', (d, m) => this.opcjeBilansu(d, m))),
        this.narysuj('[data-team-rolling]', '[data-team-matches-data]', (wykres, dane) => this.zMiejscem(wykres, dane, 'rolling', (d, m) => this.opcjeKroczacej(d, m))),
        this.narysuj('[data-team-boxplot]', '[data-team-spread-data]', (wykres, dane) => this.rysujRozstep(wykres, dane)),
      ]);
    }

    zMiejscem(wykres, dane, nazwa, opcje) {
      wykres.setOption(opcje(dane.wszystkie, 'wszystkie'));
      this.miejsce(nazwa, miejsce => wykres.setOption(opcje(dane[miejsce], miejsce), {notMerge: true}));
      this.otworzMeczPoKliknieciu(wykres);
      return wykres;
    }

    tooltipMeczu(punkty, dodatkowe) {
      return {
        trigger: 'axis',
        renderMode: 'richText',
        confine: true,
        formatter: parametry => {
          const punkt = punkty[(Array.isArray(parametry) ? parametry[0] : parametry)?.dataIndex];
          if (!punkt) return '';
          return `${punkt.etykieta} · ${punkt.miejsce_etykieta}\n${punkt.przeciwnik ?? '—'}\n${punkt.sezon} · ${punkt.rozgrywki}\nWynik: ${punkt.wynik} (${punkt.rezultat})${dodatkowe(punkt)}`;
        },
      };
    }

    brak(miejsce) {
      return {
        title: {text: `Brak rozegranych meczów: ${MIEJSCA[miejsce]}.`, left: 'center', top: 'middle', textStyle: {fontSize: 13, fontWeight: 'normal', color: '#68798a'}},
        xAxis: {show: false},
        yAxis: {show: false},
        series: [],
      };
    }

    opcjeMeczow(dane, miejsce) {
      const punkty = dane.punkty;
      if (!punkty.length) return this.brak(miejsce);
      const mediana = (wartosc, kolor, etykieta) => (wartosc === null ? undefined : {silent: true, symbol: 'none', lineStyle: {type: 'dashed', color: kolor}, label: {position: 'insideEndTop', formatter: `${etykieta} ${formatujLiczbe(wartosc)}`, color: kolor, fontSize: 10}, data: [{yAxis: wartosc}]});
      return {
        ...animacja(),
        aria: {show: true, description: `Wykres liniowy bramek zdobytych (niebieska linia z kółkami) i straconych (czerwona przerywana z kwadratami) przez drużynę w kolejnych meczach, z medianami: ${MIEJSCA[miejsce]}.`},
        legend: {top: 0},
        grid: {left: 42, right: 18, top: 36, bottom: 58},
        tooltip: this.tooltipMeczu(punkty, punkt => `\nZdobyte: ${punkt.zdobyte} · Stracone: ${punkt.stracone}`),
        xAxis: osMeczow(punkty),
        yAxis: {type: 'value', minInterval: 1, name: 'Bramki', scale: true},
        dataZoom: [{type: 'inside'}, {type: 'slider', height: 16, bottom: 4}],
        series: [
          {id: 'zdobyte', name: 'Bramki zdobyte', type: 'line', symbol: 'circle', symbolSize: 6, lineStyle: {width: 1.8, color: KOLOR_ZDOBYTE}, itemStyle: {color: KOLOR_ZDOBYTE}, emphasis: {focus: 'series', scale: 1.6}, markLine: mediana(dane.mediana_zdobytych, KOLOR_ZDOBYTE, 'Med. zdob.'), data: punkty.map(punkt => ({value: punkt.zdobyte, idMecz: punkt.id_mecz}))},
          {id: 'stracone', name: 'Bramki stracone', type: 'line', symbol: 'rect', symbolSize: 6, lineStyle: {width: 1.8, type: 'dashed', color: KOLOR_STRACONE}, itemStyle: {color: KOLOR_STRACONE}, emphasis: {focus: 'series', scale: 1.6}, markLine: mediana(dane.mediana_straconych, KOLOR_STRACONE, 'Med. strac.'), data: punkty.map(punkt => ({value: punkt.stracone, idMecz: punkt.id_mecz}))},
        ],
      };
    }

    opcjeBilansu(dane, miejsce) {
      const punkty = dane.punkty;
      if (!punkty.length) return this.brak(miejsce);
      return {
        ...animacja(),
        aria: {show: true, description: `Wykres słupkowy różnicy bramek drużyny w kolejnych meczach (dodatnia zielona, ujemna czerwona z wzorem) ze średnią kroczącą z 5 meczów: ${MIEJSCA[miejsce]}.`},
        legend: {top: 0, data: ['Różnica bramek', 'Średnia krocząca różnicy (5)']},
        grid: {left: 42, right: 18, top: 36, bottom: 58},
        tooltip: this.tooltipMeczu(punkty, punkt => `\nRóżnica: ${bilans(punkt.roznica)}\nŚrednia krocząca (5): ${zeZnakiem(punkt.roznica_srednia_5)}`),
        xAxis: osMeczow(punkty),
        yAxis: {type: 'value', minInterval: 1, name: 'Różnica bramek'},
        dataZoom: [{type: 'inside'}, {type: 'slider', height: 16, bottom: 4}],
        series: [
          {
            id: 'roznica',
            name: 'Różnica bramek',
            type: 'bar',
            barMaxWidth: 10,
            itemStyle: {color: '#2f7e6c'},
            emphasis: {focus: 'series'},
            markLine: {silent: true, symbol: 'none', lineStyle: {color: '#9aa5b1'}, label: {show: false}, data: [{yAxis: 0}]},
            data: punkty.map(punkt => ({
              value: punkt.roznica,
              idMecz: punkt.id_mecz,
              itemStyle: punkt.roznica < 0 ? {color: KOLOR_STRACONE, decal: WZOR_KRESKI} : punkt.roznica === 0 ? {color: '#9f6a15'} : undefined,
            })),
          },
          {id: 'kroczaca', name: 'Średnia krocząca różnicy (5)', type: 'line', showSymbol: false, connectNulls: false, lineStyle: {width: 2.5, color: '#173e65'}, itemStyle: {color: '#173e65'}, data: punkty.map(punkt => punkt.roznica_srednia_5)},
        ],
      };
    }

    opcjeKroczacej(dane, miejsce) {
      const punkty = dane.punkty;
      if (!punkty.length) return this.brak(miejsce);
      const linia = (id, nazwa, pole, kolor, typ) => ({id, name: nazwa, type: 'line', showSymbol: false, connectNulls: false, lineStyle: {width: typ === 'solid' ? 2.5 : 2, type: typ, color: kolor}, itemStyle: {color: kolor}, emphasis: {focus: 'series'}, data: punkty.map(punkt => punkt[pole])});
      const tlo = (id, nazwa, pole, kolor, symbol) => ({id, name: nazwa, type: 'scatter', symbol, symbolSize: 5, itemStyle: {color: kolor, opacity: 0.22}, emphasis: {focus: 'series'}, data: punkty.map(punkt => ({value: punkt[pole], idMecz: punkt.id_mecz}))});
      const serie = [
        tlo('tlo-zdobyte', 'Mecze: zdobyte', 'zdobyte', KOLOR_ZDOBYTE, 'circle'),
        tlo('tlo-stracone', 'Mecze: stracone', 'stracone', KOLOR_STRACONE, 'rect'),
        {...linia('zdobyte-5', 'Średnia krocząca zdobytych (5)', 'zdobyte_srednia_5', KOLOR_ZDOBYTE, 'solid'), markLine: {silent: true, symbol: 'none', lineStyle: {type: 'dashed', color: '#c8d4dd'}, label: {position: 'insideEndTop', formatter: parametry => punkty[parametry.value]?.sezon ?? '', fontSize: 9, color: '#68798a'}, data: graniceSezonow(punkty)}},
        linia('stracone-5', 'Średnia krocząca straconych (5)', 'stracone_srednia_5', KOLOR_STRACONE, 'solid'),
      ];
      if (dane.trend_10) {
        serie.push(linia('zdobyte-10', 'Mediana krocząca zdobytych (10)', 'zdobyte_mediana_10', KOLOR_ZDOBYTE, 'dotted'));
        serie.push(linia('stracone-10', 'Mediana krocząca straconych (10)', 'stracone_mediana_10', KOLOR_STRACONE, 'dotted'));
      }
      return {
        ...animacja(),
        aria: {show: true, description: `Wykres formy kroczącej: średnia z 5 i mediana z 10 ostatnich meczów dla bramek zdobytych (niebieskie) i straconych (czerwone) przez drużynę, na tle wyników poszczególnych meczów; ${MIEJSCA[miejsce]}. Linie pionowe oznaczają początek sezonu.`},
        legend: {top: 0, type: 'scroll'},
        grid: {left: 42, right: 18, top: 64, bottom: 58},
        tooltip: this.tooltipMeczu(punkty, punkt => `\nZdobyte: ${punkt.zdobyte} · Stracone: ${punkt.stracone}\nŚr. 5: ${formatujLiczbe(punkt.zdobyte_srednia_5)} / ${formatujLiczbe(punkt.stracone_srednia_5)}\nMed. 10: ${formatujLiczbe(punkt.zdobyte_mediana_10)} / ${formatujLiczbe(punkt.stracone_mediana_10)}`),
        xAxis: osMeczow(punkty),
        yAxis: {type: 'value', name: 'Bramki', scale: true},
        dataZoom: [{type: 'inside'}, {type: 'slider', height: 16, bottom: 4}],
        series: serie,
      };
    }

    rysujRozstep(wykres, sezony) {
      const pudelko = rodzaj => sezony.map(sezon => {
        const r = sezon[rodzaj];
        return r ? [r.minimum, r.q1, r.mediana, r.q3, r.maksimum] : [];
      });
      const odstajace = rodzaj => sezony.flatMap((sezon, indeks) => (sezon[rodzaj]?.odstajace ?? []).map(wartosc => [indeks, wartosc]));
      wykres.setOption({
        ...animacja(),
        aria: {show: true, description: 'Boxplot bramek zdobytych (niebieskie pudełka) i straconych (czerwone, przerywane) przez drużynę na mecz w kolejnych sezonach, z wartościami odstającymi jako punktami.'},
        legend: {top: 0},
        grid: {left: 42, right: 18, top: 36, bottom: 60},
        tooltip: {
          trigger: 'item',
          renderMode: 'richText',
          formatter: parametry => {
            const sezon = sezony[parametry.dataIndex ?? parametry.value?.[0]];
            if (!sezon) return '';
            if (parametry.seriesType === 'scatter') return `${sezon.sezon}\n${parametry.seriesName}: ${parametry.value[1]}`;
            const r = sezon[parametry.seriesId];
            if (!r) return `${sezon.sezon}\nBrak danych`;
            return `${sezon.sezon} (n=${r.n}${r.mala_proba ? ', mała próba' : ''})\n${parametry.seriesName}\nMediana: ${formatujLiczbe(r.mediana)}\nQ1–Q3: ${formatujLiczbe(r.q1)}–${formatujLiczbe(r.q3)}\nWąsy: ${r.minimum}–${r.maksimum}`;
          },
        },
        xAxis: {type: 'category', data: sezony.map(sezon => `${sezon.sezon}${sezon.zdobyte?.mala_proba ? ' *' : ''}`), axisLabel: {rotate: 30, hideOverlap: true}},
        yAxis: {type: 'value', minInterval: 1, name: 'Bramki', scale: true},
        series: [
          {id: 'zdobyte', name: 'Bramki zdobyte', type: 'boxplot', boxWidth: [6, 18], itemStyle: {color: '#eaf2fb', borderColor: KOLOR_ZDOBYTE, borderWidth: 1.5}, data: pudelko('zdobyte')},
          {id: 'stracone', name: 'Bramki stracone', type: 'boxplot', boxWidth: [6, 18], itemStyle: {color: '#fbecec', borderColor: KOLOR_STRACONE, borderWidth: 1.5, borderType: 'dashed'}, data: pudelko('stracone')},
          {id: 'odstajace-zdobyte', name: 'Odstające zdobyte', type: 'scatter', symbol: 'circle', symbolSize: 6, itemStyle: {color: KOLOR_ZDOBYTE}, data: odstajace('zdobyte')},
          {id: 'odstajace-stracone', name: 'Odstające stracone', type: 'scatter', symbol: 'rect', symbolSize: 6, itemStyle: {color: KOLOR_STRACONE}, data: odstajace('stracone')},
        ],
      });
      return wykres;
    }
  }

  class ZakladkiDruzynyController {
    constructor(korzen) {
      this.korzen = korzen;
    }

    uruchom() {
      this.podlaczSpisTresci();
      const pasek = this.korzen.querySelector('[data-team-tabs]');
      if (!pasek) return;
      this.przyciski = Array.from(pasek.querySelectorAll('[role="tab"]'));
      this.panele = Array.from(this.korzen.querySelectorAll('[data-team-panel]'));
      this.panele.forEach(panel => {
        panel.setAttribute('role', 'tabpanel');
        panel.tabIndex = 0;
      });
      pasek.hidden = false;
      this.przyciski.forEach((przycisk, indeks) => {
        przycisk.addEventListener('click', () => this.wybierz(indeks));
        przycisk.addEventListener('keydown', zdarzenie => {
          const kierunki = {
            ArrowRight: (indeks + 1) % this.przyciski.length,
            ArrowLeft: (indeks + this.przyciski.length - 1) % this.przyciski.length,
            Home: 0,
            End: this.przyciski.length - 1,
          };
          if (!(zdarzenie.key in kierunki)) return;
          zdarzenie.preventDefault();
          this.wybierz(kierunki[zdarzenie.key]);
          this.przyciski[kierunki[zdarzenie.key]].focus();
        });
      });
      const indeks = this.przyciski.findIndex(p => p.dataset.teamTab === this.korzen.dataset.activeTab);
      this.wybierz(Math.max(0, indeks));
    }

    podlaczSpisTresci() {
      this.korzen.querySelectorAll('a[data-team-scroll]').forEach(link => {
        link.addEventListener('click', zdarzenie => {
          const cel = this.korzen.querySelector(link.getAttribute('href'));
          if (!cel) return;
          zdarzenie.preventDefault();
          cel.scrollIntoView({behavior: ograniczonyRuch() ? 'auto' : 'smooth', block: 'start'});
          cel.focus({preventScroll: true});
        });
      });
    }

    wybierz(indeks) {
      this.przyciski.forEach((przycisk, numer) => {
        przycisk.setAttribute('aria-selected', String(numer === indeks));
        przycisk.tabIndex = numer === indeks ? 0 : -1;
      });
      const klucz = this.przyciski[indeks].dataset.teamTab;
      this.panele.forEach(panel => { panel.hidden = panel.dataset.teamPanel !== klucz; });
      if (klucz === 'podsumowanie') new PodsumowanieDruzynyController(this.korzen).uruchom();
      if (klucz === 'forma') new FormaDruzynyController(this.korzen).uruchom();
    }
  }

  globalThis.HandballDruzyna = {ZakladkiDruzynyController};

  const szczegoly = document.querySelector('[data-team-detail]');
  if (szczegoly) {
    new ZakladkiDruzynyController(szczegoly).uruchom();
    const Linki = globalThis.HandballZawodnik?.LinkiZawodnikowController;
    if (Linki) new Linki(szczegoly, (adres, opcje) => window.fetch(adres, opcje), adres => window.open(adres, '_blank', 'noopener')).uruchom();
  }
})();
