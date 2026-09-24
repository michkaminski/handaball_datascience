(() => {
  let ladowanieECharts = null;

  const zaladujECharts = adres => {
    if (window.echarts) return Promise.resolve(window.echarts);
    if (ladowanieECharts) return ladowanieECharts;
    ladowanieECharts = new Promise((resolve, reject) => {
      const skrypt = document.createElement('script');
      skrypt.src = adres;
      skrypt.onload = () => resolve(window.echarts);
      skrypt.onerror = () => reject(new Error('Nie udało się załadować ECharts'));
      document.head.append(skrypt);
    });
    return ladowanieECharts;
  };

  const escapujHtml = tekst => String(tekst ?? '').replace(/[&<>"']/g, znak => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[znak]);

  const PROG_MALEJ_PROBY = 5;

  const PALETA_ROZGRYWEK = ['#3a7c67', '#9f6a15', '#7c3aed', '#b04646', '#0e7490', '#64748b'];

  const WZOR_KOLOR = 'rgba(255,255,255,0.5)';
  const WZORY_ROZGRYWEK = [
    {symbol: 'rect', symbolSize: 1, dashArrayX: [1, 0], dashArrayY: [2, 5], rotation: Math.PI / 4, color: WZOR_KOLOR},
    {symbol: 'circle', symbolSize: 0.7, dashArrayX: [[1, 4]], dashArrayY: [4], color: WZOR_KOLOR},
    {symbol: 'rect', symbolSize: 1, dashArrayX: [1, 0], dashArrayY: [2, 5], rotation: -Math.PI / 4, color: WZOR_KOLOR},
    {symbol: 'triangle', symbolSize: 0.8, dashArrayX: [[1, 4]], dashArrayY: [5], color: WZOR_KOLOR},
    {symbol: 'rect', symbolSize: 1, dashArrayX: [1, 0], dashArrayY: [2, 4], rotation: 0, color: WZOR_KOLOR},
    {symbol: 'diamond', symbolSize: 0.8, dashArrayX: [[1, 4]], dashArrayY: [5], color: WZOR_KOLOR},
  ];

  const formatujLiczbe = (wartosc, miejsca = 1) => (wartosc === null || wartosc === undefined ? '—' : Number(wartosc).toFixed(miejsca).replace('.', ','));

  class AnalitykaBramekController {
    constructor(korzen, {prefiks, podmiot, etykieta = 'Bramki'}) {
      this.korzen = korzen;
      this.prefiks = prefiks;
      this.podmiot = podmiot;
      this.etykieta = etykieta;
    }

    adresMeczu(id) {
      return this.korzen.dataset[`${this.prefiks}MatchUrl`].replace(/0$/, String(id));
    }

    async uruchom() {
      await Promise.all([this.uruchomSezony(), this.uruchomRozklad()]);
    }

    async uruchomSezony() {
      const element = this.korzen.querySelector(`[data-${this.prefiks}-season-stats]`);
      const zrodlo = this.korzen.querySelector(`[data-${this.prefiks}-season-stats-data]`);
      if (!element || !zrodlo || element.dataset.chartReady) return;
      element.dataset.chartReady = 'true';
      const bramki = this.korzen.querySelector(`[data-${this.prefiks}-season-goals]`);
      try {
        const echarts = await zaladujECharts(this.korzen.dataset.echartsUrl);
        const sezony = JSON.parse(zrodlo.textContent);
        this.rysujSezony(echarts, element, sezony);
        if (bramki) this.rysujBramkiSezonow(echarts, bramki, sezony);
      } catch {
        element.textContent = 'Nie udało się narysować wykresu. Dane tabelaryczne pozostają dostępne poniżej.';
        if (bramki) bramki.hidden = true;
      }
    }

    opisSezonu(sezon) {
      const mecze = grupa => (grupa.znane === grupa.mecze ? String(grupa.mecze) : `${grupa.znane} z ${grupa.mecze}`);
      const dominanta = grupa => (grupa.dominanty.length ? grupa.dominanty.join(', ') : '—');
      const wiersze = [
        ['Suma bramek', sezon.suma ?? '—'],
        ['Średnia', formatujLiczbe(sezon.srednia, 2)],
        ['Mediana', formatujLiczbe(sezon.mediana)],
        ['Dominanta', dominanta(sezon)],
        ['Q1–Q3', sezon.q1 === null ? '—' : `${formatujLiczbe(sezon.q1)}–${formatujLiczbe(sezon.q3)}`],
        ['Min–maks', sezon.minimum === null ? '—' : `${sezon.minimum}–${sezon.maksimum}`],
      ];
      const malaProba = sezon.znane < PROG_MALEJ_PROBY ? '<span class="player-tooltip-flag">mała próba</span>' : '';
      const rozgrywki = sezon.rozgrywki.map(grupa => '<tr>'
        + `<th>${escapujHtml(grupa.rozgrywki)}</th>`
        + `<td>${escapujHtml(mecze(grupa))}</td>`
        + `<td>${escapujHtml(formatujLiczbe(grupa.srednia, 2))}</td>`
        + `<td>${escapujHtml(formatujLiczbe(grupa.mediana))}</td>`
        + `<td>${escapujHtml(dominanta(grupa))}</td></tr>`).join('');
      return `<div class="player-tooltip"><div class="player-tooltip-title">${escapujHtml(sezon.sezon)}${malaProba}</div>`
        + `<div class="player-tooltip-sub">Wszystkie rozgrywki · mecze: ${escapujHtml(mecze(sezon))}</div><table>`
        + wiersze.map(([etykieta, wartosc]) => `<tr><th>${escapujHtml(etykieta)}</th><td>${escapujHtml(wartosc)}</td></tr>`).join('')
        + '</table><div class="player-tooltip-section">Podział na rozgrywki</div>'
        + '<table class="player-tooltip-breakdown"><thead><tr><th>Rozgrywki</th><td>Mecze</td><td>Śr.</td><td>Med.</td><td>Dom.</td></tr></thead>'
        + `<tbody>${rozgrywki}</tbody></table></div>`;
    }

    rysujSezony(echarts, element, sezony) {
      const wykres = echarts.init(element, null, {renderer: 'svg'});
      wykres.setOption(this.opcjeSezonow(sezony, 'linie'));
      const przelacznik = this.korzen.querySelector(`[data-${this.prefiks}-season-toggle]`);
      if (przelacznik) {
        const przyciski = Array.from(przelacznik.querySelectorAll(`[data-${this.prefiks}-season-view]`));
        przelacznik.hidden = false;
        przyciski.forEach(przycisk => {
          przycisk.addEventListener('click', () => {
            const tryb = przycisk.dataset[`${this.prefiks}SeasonView`];
            przyciski.forEach(inny => inny.setAttribute('aria-pressed', String(inny === przycisk)));
            wykres.setOption(this.opcjeSezonow(sezony, tryb), {replaceMerge: ['series']});
          });
        });
      }
      this.obserwujRozmiar(wykres, element);
      return wykres;
    }

    tooltipSezonow(sezony, opis) {
      return {
        trigger: 'axis',
        axisPointer: {type: 'shadow'},
        confine: true,
        backgroundColor: '#ffffff',
        borderColor: '#c8d4dd',
        borderWidth: 1,
        padding: 0,
        extraCssText: 'box-shadow:0 6px 18px rgba(16,40,63,.16);border-radius:8px;',
        formatter: parametry => {
          const lista = Array.isArray(parametry) ? parametry : [parametry];
          const kategoria = lista.find(parametr => parametr.seriesType !== 'scatter');
          const sezon = sezony[kategoria ? kategoria.dataIndex : lista[0]?.value?.[0]];
          return sezon ? opis(sezon) : '';
        },
      };
    }

    osSezonow(sezony) {
      return {
        type: 'category',
        data: sezony.map(sezon => sezon.sezon),
        axisLabel: {rotate: sezony.length > 6 ? 30 : 0, hideOverlap: true},
      };
    }

    opcjeSezonow(sezony, tryb) {
      const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      const przejscie = {enabled: !ograniczonyRuch};
      const wspolne = {
        animation: !ograniczonyRuch,
        animationDuration: 450,
        animationDurationUpdate: 500,
        animationEasing: 'cubicOut',
        color: ['#2b6ea4', '#3a7c67', '#9f6a15'],
        legend: {top: 0},
        grid: {left: 42, right: 18, top: 36, bottom: 48},
        tooltip: this.tooltipSezonow(sezony, sezon => this.opisSezonu(sezon)),
        xAxis: this.osSezonow(sezony),
        yAxis: {type: 'value', minInterval: 1, name: 'Bramki na mecz'},
        dataZoom: sezony.length > 20 ? [{type: 'inside'}, {type: 'slider', height: 14, bottom: 2}] : undefined,
      };
      if (tryb === 'slupki') {
        return {
          ...wspolne,
          aria: {show: true, description: `Wykres słupkowy średniej, mediany i dominanty bramek ${this.podmiot} na mecz w kolejnych sezonach; przy kilku dominantach słupek pokazuje najmniejszą, a etykieta wszystkie.`},
          series: [
            {id: 'srednia', name: 'Średnia', type: 'bar', barMaxWidth: 18, universalTransition: przejscie, emphasis: {focus: 'series'}, data: sezony.map(sezon => this.slupekSezonu(sezon, sezon.srednia, '#2b6ea4'))},
            {id: 'mediana', name: 'Mediana', type: 'bar', barMaxWidth: 18, universalTransition: przejscie, emphasis: {focus: 'series'}, data: sezony.map(sezon => this.slupekSezonu(sezon, sezon.mediana, '#3a7c67'))},
            {
              id: 'dominanta',
              name: 'Dominanta',
              type: 'bar',
              barMaxWidth: 18,
              universalTransition: przejscie,
              emphasis: {focus: 'series'},
              data: sezony.map(sezon => {
                if (!sezon.dominanty.length) return null;
                const slupek = this.slupekSezonu(sezon, Math.min(...sezon.dominanty), '#9f6a15');
                const punkt = typeof slupek === 'object' ? slupek : {value: slupek};
                return sezon.dominanty.length > 1
                  ? {...punkt, label: {show: true, position: 'top', fontSize: 10, color: '#6b4a10', formatter: sezon.dominanty.join('/')}}
                  : punkt;
              }),
            },
          ],
        };
      }
      return {
        ...wspolne,
        aria: {show: true, description: `Wykres średniej, mediany i dominanty bramek ${this.podmiot} na mecz w kolejnych sezonach; szczegóły z podziałem na rozgrywki w okienku po najechaniu.`},
        series: [
          {
            id: 'srednia',
            name: 'Średnia',
            type: 'line',
            symbol: 'circle',
            symbolSize: 9,
            smooth: 0.15,
            connectNulls: false,
            lineStyle: {width: 2.5},
            universalTransition: przejscie,
            emphasis: {focus: 'series', scale: 1.5},
            data: sezony.map(sezon => this.punktSezonu(sezon, sezon.srednia, '#2b6ea4')),
          },
          {
            id: 'mediana',
            name: 'Mediana',
            type: 'line',
            symbol: 'rect',
            symbolSize: 8,
            connectNulls: false,
            lineStyle: {width: 2, type: 'dashed'},
            universalTransition: przejscie,
            emphasis: {focus: 'series', scale: 1.5},
            data: sezony.map(sezon => this.punktSezonu(sezon, sezon.mediana, '#3a7c67')),
          },
          {
            id: 'dominanta',
            name: 'Dominanta',
            type: 'scatter',
            symbol: 'diamond',
            symbolSize: 12,
            universalTransition: przejscie,
            emphasis: {focus: 'series', scale: 1.4},
            data: sezony.flatMap((sezon, indeks) => sezon.dominanty.map(wartosc => [indeks, wartosc])),
          },
        ],
      };
    }

    slupekSezonu(grupa, wartosc, kolor) {
      if (wartosc === null || grupa.znane >= PROG_MALEJ_PROBY) return wartosc;
      return {value: wartosc, itemStyle: {color: `${kolor}40`, borderColor: kolor, borderWidth: 1.5, borderType: 'dashed'}};
    }

    opisBramekSezonu(sezon) {
      const wiersze = sezon.rozgrywki.map(grupa => '<tr>'
        + `<th>${escapujHtml(grupa.rozgrywki)}</th>`
        + `<td>${escapujHtml(grupa.znane === grupa.mecze ? grupa.mecze : `${grupa.znane} z ${grupa.mecze}`)}</td>`
        + `<td>${escapujHtml(grupa.suma ?? '—')}</td></tr>`).join('');
      return `<div class="player-tooltip"><div class="player-tooltip-title">${escapujHtml(sezon.sezon)}</div>`
        + `<div class="player-tooltip-sub">Suma bramek w sezonie: <b>${escapujHtml(sezon.suma ?? '—')}</b></div>`
        + '<div class="player-tooltip-section">Podział na rozgrywki</div>'
        + '<table class="player-tooltip-breakdown"><thead><tr><th>Rozgrywki</th><td>Mecze</td><td>Bramki</td></tr></thead>'
        + `<tbody>${wiersze}</tbody></table></div>`;
    }

    slotyRozgrywek(sezony, styl, ukryte) {
      const widoczne = sezony.map(sezon => sezon.rozgrywki.filter(grupa => !ukryte.has(grupa.rozgrywki)));
      const liczbaSlotow = Math.max(0, ...widoczne.map(grupy => grupy.length));
      return Array.from({length: liczbaSlotow}, (_, slot) => ({
        id: `rozgrywki-${slot}`,
        name: `rozgrywki-${slot}`,
        type: 'bar',
        barMaxWidth: 30,
        emphasis: {focus: 'self'},
        data: widoczne.map(grupy => {
          const grupa = grupy[slot];
          return grupa ? {value: grupa.suma, nazwa: grupa.rozgrywki, itemStyle: styl.get(grupa.rozgrywki)} : null;
        }),
      }));
    }

    rysujBramkiSezonow(echarts, element, sezony) {
      const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      const nazwy = [...new Set(sezony.flatMap(sezon => sezon.rozgrywki.map(grupa => grupa.rozgrywki)))];
      const styl = new Map(nazwy.map((nazwa, indeks) => [nazwa, {
        color: PALETA_ROZGRYWEK[indeks % PALETA_ROZGRYWEK.length],
        decal: WZORY_ROZGRYWEK[indeks % WZORY_ROZGRYWEK.length],
      }]));
      const suma = {
        id: 'suma',
        name: 'Suma w sezonie',
        type: 'bar',
        barMaxWidth: 30,
        barGap: '10%',
        barCategoryGap: '18%',
        itemStyle: {color: '#173e65'},
        emphasis: {focus: 'self'},
        label: {show: sezony.length <= 12, position: 'top', fontSize: 10, color: '#173e65'},
        data: sezony.map(sezon => sezon.suma),
      };
      const legenda = nazwy.map(nazwa => ({
        id: `legenda-${nazwa}`,
        name: nazwa,
        type: 'line',
        data: [],
        symbol: 'roundRect',
        itemStyle: styl.get(nazwa),
        lineStyle: {opacity: 0},
      }));
      const serie = ukryte => [suma, ...this.slotyRozgrywek(sezony, styl, ukryte), ...legenda];
      const wykres = echarts.init(element, null, {renderer: 'svg'});
      wykres.setOption({
        animation: !ograniczonyRuch,
        animationDuration: 450,
        animationDurationUpdate: 350,
        animationEasing: 'cubicOut',
        aria: {show: true, description: `Wykres słupkowy liczby bramek ${this.podmiot} w kolejnych sezonach: pierwszy słupek to suma sezonu, kolejne to bramki w poszczególnych rozgrywkach, rozróżnione kolorem i wzorem.`},
        legend: {
          top: 0,
          left: 'center',
          width: '88%',
          type: 'scroll',
          icon: 'roundRect',
          data: ['Suma w sezonie', ...nazwy],
          formatter: nazwa => (nazwa.length > 26 ? `${nazwa.slice(0, 25)}…` : nazwa),
        },
        grid: {left: 42, right: 18, top: 60, bottom: 48},
        tooltip: this.tooltipSezonow(sezony, sezon => this.opisBramekSezonu(sezon)),
        xAxis: this.osSezonow(sezony),
        yAxis: {type: 'value', minInterval: 1, name: 'Bramki'},
        dataZoom: sezony.length > 20 ? [{type: 'inside'}, {type: 'slider', height: 14, bottom: 2}] : undefined,
        series: serie(new Set()),
      });
      wykres.on('legendselectchanged', zdarzenie => {
        const ukryte = new Set(nazwy.filter(nazwa => zdarzenie.selected[nazwa] === false));
        wykres.setOption({legend: {selected: zdarzenie.selected}, series: serie(ukryte)}, {replaceMerge: ['series']});
      });
      this.obserwujRozmiar(wykres, element);
      return wykres;
    }

    punktSezonu(grupa, wartosc, kolor) {
      if (grupa.znane >= PROG_MALEJ_PROBY) return wartosc;
      return {value: wartosc, itemStyle: {color: '#ffffff', borderColor: kolor, borderWidth: 2}};
    }

    async uruchomRozklad() {
      const rozklad = this.korzen.querySelector(`[data-${this.prefiks}-distribution]`);
      const zrodlo = this.korzen.querySelector(`[data-${this.prefiks}-distribution-data]`);
      if (!rozklad || !zrodlo || rozklad.dataset.chartReady) return;
      rozklad.dataset.chartReady = 'true';
      try {
        const echarts = await zaladujECharts(this.korzen.dataset.echartsUrl);
        this.rysujRozklad(echarts, rozklad, JSON.parse(zrodlo.textContent));
      } catch {
        rozklad.textContent = 'Nie udało się narysować wykresu. Dane tabelaryczne pozostają dostępne poniżej.';
      }
    }

    rysujRozklad(echarts, element, rozklad) {
      const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      const wykres = echarts.init(element, null, {renderer: 'svg'});
      wykres.setOption({
        animation: !ograniczonyRuch,
        animationDuration: 400,
        aria: {show: true, description: `Histogram liczby meczów według liczby bramek ${this.podmiot}: wszystkie, u siebie i na wyjeździe.`},
        color: ['#3a7c67', '#2b6ea4', '#9f6a15'],
        legend: {top: 0},
        grid: {left: 42, right: 18, top: 34, bottom: 38},
        tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
        xAxis: {type: 'category', name: 'Bramki', data: rozklad.map(punkt => punkt.bramki)},
        yAxis: {type: 'value', minInterval: 1, name: 'Mecze'},
        series: [
          {
            name: 'Wszystkie',
            type: 'bar',
            barMaxWidth: 20,
            emphasis: {focus: 'series'},
            data: rozklad.map(punkt => punkt.mecze),
          },
          {
            name: 'U siebie',
            type: 'bar',
            barMaxWidth: 20,
            emphasis: {focus: 'series'},
            data: rozklad.map(punkt => punkt.dom),
          },
          {
            name: 'Na wyjeździe',
            type: 'bar',
            barMaxWidth: 20,
            emphasis: {focus: 'series'},
            data: rozklad.map(punkt => punkt.wyjazd),
          },
        ],
      });
      this.obserwujRozmiar(wykres, element);
    }

    obserwujRozmiar(wykres, element) {
      if (typeof ResizeObserver === 'function') new ResizeObserver(() => wykres.resize()).observe(element);
    }
  }

  const PALETA_SEZONOW = ['#2b6ea4', '#3a7c67', '#9f6a15', '#7c3aed', '#b04646', '#0e7490'];

  class FormaBramekController {
    constructor(korzen, {prefiks, podmiot, etykieta = 'Bramki'}) {
      this.korzen = korzen;
      this.prefiks = prefiks;
      this.podmiot = podmiot;
      this.etykieta = etykieta;
    }

    adresMeczu(id) {
      return this.korzen.dataset[`${this.prefiks}MatchUrl`].replace(/0$/, String(id));
    }

    async uruchom() {
      await Promise.all([this.uruchomTrendy(), this.uruchomForme()]);
    }

    async uruchomTrendy() {
      const trendWszystkie = this.korzen.querySelector(`[data-${this.prefiks}-trend-wszystkie]`);
      const trendDom = this.korzen.querySelector(`[data-${this.prefiks}-trend-dom]`);
      const trendWyjazd = this.korzen.querySelector(`[data-${this.prefiks}-trend-wyjazd]`);
      const zrodlo = this.korzen.querySelector(`[data-${this.prefiks}-trend-data]`);
      if (!trendWszystkie || !trendDom || !trendWyjazd || !zrodlo || trendWszystkie.dataset.chartReady) return;
      trendWszystkie.dataset.chartReady = 'true';
      try {
        const echarts = await zaladujECharts(this.korzen.dataset.echartsUrl);
        const dane = JSON.parse(zrodlo.textContent);
        const punktyDom = dane.punkty.filter(punkt => punkt.miejsce === 'dom');
        const punktyWyjazd = dane.punkty.filter(punkt => punkt.miejsce === 'wyjazd');
        this.rysujTrend(echarts, trendWszystkie, dane.punkty, dane.mediana, 'Brak meczów w wybranym zakresie.');
        this.rysujTrend(echarts, trendDom, punktyDom, dane.mediana_dom, 'Brak meczów u siebie w wybranym zakresie.');
        this.rysujTrend(echarts, trendWyjazd, punktyWyjazd, dane.mediana_wyjazd, 'Brak meczów na wyjeździe w wybranym zakresie.');
      } catch {
        trendWszystkie.textContent = 'Nie udało się narysować wykresów. Dane tabelaryczne pozostają dostępne poniżej.';
        trendDom.hidden = true;
        trendWyjazd.hidden = true;
      }
    }

    async uruchomForme() {
      const formaWszystkie = this.korzen.querySelector(`[data-${this.prefiks}-form-wszystkie]`);
      const formaDom = this.korzen.querySelector(`[data-${this.prefiks}-form-dom]`);
      const formaWyjazd = this.korzen.querySelector(`[data-${this.prefiks}-form-wyjazd]`);
      const boxplot = this.korzen.querySelector(`[data-${this.prefiks}-boxplot]`);
      const zrodlo = this.korzen.querySelector(`[data-${this.prefiks}-forma-data]`);
      if (!formaWszystkie || !formaDom || !formaWyjazd || !boxplot || !zrodlo || formaWszystkie.dataset.chartReady) return;
      formaWszystkie.dataset.chartReady = 'true';
      try {
        const echarts = await zaladujECharts(this.korzen.dataset.echartsUrl);
        const dane = JSON.parse(zrodlo.textContent);
        this.rysujForme(echarts, formaWszystkie, dane.wszystkie.punkty, 'Brak meczów w wybranym zakresie.');
        this.rysujForme(echarts, formaDom, dane.dom.punkty, 'Brak meczów u siebie w wybranym zakresie.');
        this.rysujForme(echarts, formaWyjazd, dane.wyjazd.punkty, 'Brak meczów na wyjeździe w wybranym zakresie.');
        this.rysujBoxplot(echarts, boxplot, dane);
      } catch {
        formaWszystkie.textContent = 'Nie udało się narysować wykresów. Dane tabelaryczne pozostają dostępne poniżej.';
        formaDom.hidden = true;
        formaWyjazd.hidden = true;
        boxplot.hidden = true;
      }
    }

    rysujTrend(echarts, element, punkty, mediana, komunikatBraku) {
      if (!punkty.length) {
        element.textContent = komunikatBraku;
        return;
      }
      const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      const maksimum = Math.max(...punkty.map(punkt => punkt.bramki ?? -1));
      const wykres = echarts.init(element, null, {renderer: 'svg'});
      wykres.setOption({
        animation: !ograniczonyRuch,
        animationDuration: 450,
        animationEasing: 'cubicOut',
        aria: {show: true, description: `Wykres bramek ${this.podmiot} w kolejnych meczach. Linia przerywana oznacza medianę.`},
        color: ['#2b6ea4'],
        grid: {left: 42, right: 18, top: 28, bottom: 54},
        tooltip: {
          trigger: 'item',
          renderMode: 'richText',
          formatter: parametry => {
            const punkt = punkty[parametry.dataIndex];
            const przeciwnik = punkt.przeciwnik ? `\n${punkt.przeciwnik}` : '';
            return `${punkt.etykieta}\n${punkt.sezon} · ${punkt.rozgrywki}${przeciwnik}\n${this.etykieta}: ${punkt.bramki ?? 'brak danych'}`;
          },
        },
        xAxis: {
          type: 'category',
          data: punkty.map(punkt => punkt.etykieta),
          axisLabel: {rotate: 35, hideOverlap: true},
        },
        yAxis: {type: 'value', minInterval: 1, name: 'Bramki'},
        dataZoom: [{type: 'inside'}, {type: 'slider', height: 16, bottom: 4}],
        series: [{
          name: this.etykieta,
          type: 'line',
          smooth: 0.18,
          showSymbol: true,
          symbol: 'circle',
          symbolSize: 7,
          emphasis: {focus: 'series', scale: 1.7},
          lineStyle: {width: 2},
          areaStyle: {opacity: 0.08},
          data: punkty.map(punkt => ({
            value: punkt.bramki,
            idMecz: punkt.id_mecz,
            symbolSize: punkt.bramki === maksimum ? 12 : 7,
            itemStyle: punkt.bramki === maksimum ? {color: '#b04646', borderColor: '#fff', borderWidth: 2} : undefined,
          })),
          markLine: mediana === null ? undefined : {
            silent: true,
            symbol: 'none',
            lineStyle: {type: 'dashed', color: '#2f7e6c'},
            label: {formatter: `Mediana ${mediana}`},
            data: [{yAxis: mediana}],
          },
        }],
      });
      wykres.on('click', parametry => {
        const id = parametry.data?.idMecz;
        if (id) window.open(this.adresMeczu(id), '_blank', 'noopener');
      });
      this.obserwujRozmiar(wykres, element);
    }

    kolorSezonu(sezon, kolejnosc) {
      if (!kolejnosc.has(sezon)) kolejnosc.set(sezon, kolejnosc.size);
      return PALETA_SEZONOW[kolejnosc.get(sezon) % PALETA_SEZONOW.length];
    }

    rysujForme(echarts, element, punkty, komunikatBraku) {
      if (!punkty.length) {
        element.textContent = komunikatBraku;
        return;
      }
      const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      const kolejnosc = new Map();
      const graniceSezonow = [];
      punkty.forEach((punkt, indeks) => {
        if (indeks > 0 && punkt.sezon !== punkty[indeks - 1].sezon) graniceSezonow.push(indeks);
      });
      const maMediane10 = punkty.some(punkt => punkt.mediana_10 !== null);
      const wykres = echarts.init(element, null, {renderer: 'svg'});
      wykres.setOption({
        animation: !ograniczonyRuch,
        animationDuration: 450,
        animationEasing: 'cubicOut',
        aria: {show: true, description: `Wykres bramek ${this.podmiot} w kolejnych meczach z medianą i średnią kroczącą z 5 oraz mediną kroczącą z 10 meczów. Kolor punktu oznacza sezon.`},
        legend: {top: 0},
        grid: {left: 42, right: 18, top: 34, bottom: 54},
        tooltip: {
          trigger: 'item',
          renderMode: 'richText',
          formatter: parametry => {
            const punkt = punkty[parametry.dataIndex];
            return `${punkt.etykieta}\n${punkt.sezon}\n${this.etykieta}: ${punkt.bramki ?? 'brak danych'}\nMediana 5: ${punkt.mediana_5?.toFixed(1) ?? '—'}\nŚrednia 5: ${punkt.srednia_5?.toFixed(1) ?? '—'}`;
          },
        },
        xAxis: {
          type: 'category',
          data: punkty.map(punkt => punkt.etykieta),
          axisLabel: {rotate: 35, hideOverlap: true},
        },
        yAxis: {type: 'value', minInterval: 1, name: 'Bramki'},
        dataZoom: [{type: 'inside'}, {type: 'slider', height: 16, bottom: 4}],
        series: [
          {
            name: this.etykieta,
            type: 'scatter',
            symbolSize: 7,
            emphasis: {focus: 'series', scale: 1.7},
            data: punkty.map(punkt => ({
              value: punkt.bramki,
              idMecz: punkt.id_mecz,
              itemStyle: {color: this.kolorSezonu(punkt.sezon, kolejnosc)},
            })),
            markLine: {
              silent: true,
              symbol: 'none',
              lineStyle: {type: 'dashed', color: '#9aa5b1'},
              label: {formatter: parametry => punkty[parametry.value]?.sezon ?? ''},
              data: graniceSezonow.map(indeks => ({xAxis: indeks})),
            },
          },
          {
            name: 'Mediana krocząca (5)',
            type: 'line',
            showSymbol: false,
            connectNulls: false,
            lineStyle: {width: 2, color: '#173e65'},
            data: punkty.map(punkt => punkt.mediana_5),
          },
          {
            name: 'Średnia krocząca (5)',
            type: 'line',
            showSymbol: false,
            connectNulls: false,
            lineStyle: {width: 2, type: 'dotted', color: '#3a7c67'},
            data: punkty.map(punkt => punkt.srednia_5),
          },
          ...(maMediane10 ? [{
            name: 'Mediana krocząca (10)',
            type: 'line',
            showSymbol: false,
            connectNulls: false,
            lineStyle: {width: 2, type: 'dashed', color: '#9f6a15'},
            data: punkty.map(punkt => punkt.mediana_10),
          }] : []),
        ],
      });
      wykres.on('click', parametry => {
        const id = parametry.data?.idMecz;
        if (id) window.open(this.adresMeczu(id), '_blank', 'noopener');
      });
      this.obserwujRozmiar(wykres, element);
    }

    rysujBoxplot(echarts, element, dane) {
      const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      const wykres = echarts.init(element, null, {renderer: 'svg'});
      wykres.setOption({
        animation: !ograniczonyRuch,
        animationDuration: 400,
        aria: {show: true, description: 'Boxplot rozstępu ćwiartkowego bramek na mecz według sezonu, z zaznaczonymi wartościami odstającymi.'},
        grid: {left: 42, right: 18, top: 20, bottom: 60},
        tooltip: {trigger: 'item'},
        xAxis: {
          type: 'category',
          data: dane.sezony.map(sezon => `${sezon.sezon} (n=${sezon.n})`),
          axisLabel: {rotate: 30, hideOverlap: true},
        },
        yAxis: {type: 'value', minInterval: 1, name: 'Bramki'},
        series: [
          {
            name: 'Rozstęp',
            type: 'boxplot',
            data: dane.sezony.map(sezon => [sezon.minimum, sezon.q1, sezon.mediana, sezon.q3, sezon.maksimum]),
            itemStyle: {color: '#eef4fa', borderColor: '#2b6ea4'},
          },
          {
            name: 'Odstające',
            type: 'scatter',
            symbolSize: 7,
            itemStyle: {color: '#b04646'},
            data: dane.sezony.flatMap((sezon, indeks) => sezon.odstajace.map(wartosc => [indeks, wartosc])),
          },
        ],
      });
      this.obserwujRozmiar(wykres, element);
    }

    obserwujRozmiar(wykres, element) {
      if (typeof ResizeObserver === 'function') new ResizeObserver(() => wykres.resize()).observe(element);
    }
  }

  globalThis.HandballWykresyBramek = {
    zaladujECharts,
    escapujHtml,
    formatujLiczbe,
    AnalitykaBramekController,
    FormaBramekController,
  };
})();
