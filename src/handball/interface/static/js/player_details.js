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

  const formatujLiczbe = (wartosc, miejsca = 1) => (wartosc === null || wartosc === undefined ? '—' : Number(wartosc).toFixed(miejsca).replace('.', ','));

  class AnalitykaZawodnikaController {
    constructor(korzen) {
      this.korzen = korzen;
    }

    async uruchom() {
      await Promise.all([this.uruchomSezony(), this.uruchomRozklad()]);
    }

    async uruchomSezony() {
      const element = this.korzen.querySelector('[data-player-season-stats]');
      const zrodlo = this.korzen.querySelector('[data-player-season-stats-data]');
      if (!element || !zrodlo || element.dataset.chartReady) return;
      element.dataset.chartReady = 'true';
      try {
        const echarts = await zaladujECharts(this.korzen.dataset.echartsUrl);
        this.rysujSezony(echarts, element, JSON.parse(zrodlo.textContent));
      } catch {
        element.textContent = 'Nie udało się narysować wykresu. Dane tabelaryczne pozostają dostępne poniżej.';
      }
    }

    opisGrupy(grupa) {
      const wiersze = [
        ['Mecze ze znaną liczbą bramek', grupa.znane === grupa.mecze ? String(grupa.mecze) : `${grupa.znane} z ${grupa.mecze}`],
        ['Suma bramek', grupa.suma ?? '—'],
        ['Średnia', formatujLiczbe(grupa.srednia, 2)],
        ['Mediana', formatujLiczbe(grupa.mediana)],
        ['Dominanta', grupa.dominanty.length ? grupa.dominanty.join(', ') : '—'],
        ['Q1–Q3', grupa.q1 === null ? '—' : `${formatujLiczbe(grupa.q1)}–${formatujLiczbe(grupa.q3)}`],
        ['Min–maks', grupa.minimum === null ? '—' : `${grupa.minimum}–${grupa.maksimum}`],
      ];
      const malaProba = grupa.znane < PROG_MALEJ_PROBY ? '<span class="player-tooltip-flag">mała próba</span>' : '';
      return `<div class="player-tooltip"><div class="player-tooltip-title">${escapujHtml(grupa.sezon)}${malaProba}</div>`
        + `<div class="player-tooltip-sub">${escapujHtml(grupa.rozgrywki)}</div><table>`
        + wiersze.map(([etykieta, wartosc]) => `<tr><th>${escapujHtml(etykieta)}</th><td>${escapujHtml(wartosc)}</td></tr>`).join('')
        + '</table></div>';
    }

    rysujSezony(echarts, element, grupy) {
      const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      const wykres = echarts.init(element, null, {renderer: 'svg'});
      const skrot = tekst => (tekst.length > 22 ? `${tekst.slice(0, 21)}…` : tekst);
      wykres.setOption({
        animation: !ograniczonyRuch,
        animationDuration: 450,
        animationEasing: 'cubicOut',
        aria: {show: true, description: 'Wykres średniej, mediany i dominanty bramek zawodnika na mecz w kolejnych sezonach i rozgrywkach.'},
        color: ['#2b6ea4', '#3a7c67', '#9f6a15'],
        legend: {top: 0},
        grid: {left: 42, right: 18, top: 36, bottom: 78},
        tooltip: {
          trigger: 'axis',
          axisPointer: {type: 'line', lineStyle: {color: '#9aa5b1', type: 'dashed'}},
          confine: true,
          backgroundColor: '#ffffff',
          borderColor: '#c8d4dd',
          borderWidth: 1,
          padding: 0,
          extraCssText: 'box-shadow:0 6px 18px rgba(16,40,63,.16);border-radius:8px;',
          formatter: parametry => {
            const lista = Array.isArray(parametry) ? parametry : [parametry];
            const linia = lista.find(parametr => parametr.seriesType === 'line');
            const grupa = grupy[linia ? linia.dataIndex : lista[0]?.value?.[0]];
            return grupa ? this.opisGrupy(grupa) : '';
          },
        },
        xAxis: {
          type: 'category',
          data: grupy.map(grupa => `${grupa.sezon}\n${skrot(grupa.rozgrywki)}`),
          axisLabel: {rotate: 30, hideOverlap: true, fontSize: 10, lineHeight: 12},
        },
        yAxis: {type: 'value', minInterval: 1, name: 'Bramki na mecz'},
        dataZoom: grupy.length > 20 ? [{type: 'inside'}, {type: 'slider', height: 14, bottom: 2}] : undefined,
        series: [
          {
            name: 'Średnia',
            type: 'line',
            symbol: 'circle',
            symbolSize: 9,
            smooth: 0.15,
            connectNulls: false,
            lineStyle: {width: 2.5},
            emphasis: {focus: 'series', scale: 1.5},
            data: grupy.map(grupa => this.punktSezonu(grupa, grupa.srednia, '#2b6ea4')),
          },
          {
            name: 'Mediana',
            type: 'line',
            symbol: 'rect',
            symbolSize: 8,
            connectNulls: false,
            lineStyle: {width: 2, type: 'dashed'},
            emphasis: {focus: 'series', scale: 1.5},
            data: grupy.map(grupa => this.punktSezonu(grupa, grupa.mediana, '#3a7c67')),
          },
          {
            name: 'Dominanta',
            type: 'scatter',
            symbol: 'diamond',
            symbolSize: 12,
            emphasis: {focus: 'series', scale: 1.4},
            data: grupy.flatMap((grupa, indeks) => grupa.dominanty.map(wartosc => [indeks, wartosc])),
          },
        ],
      });
      this.obserwujRozmiar(wykres, element);
    }

    punktSezonu(grupa, wartosc, kolor) {
      if (grupa.znane >= PROG_MALEJ_PROBY) return wartosc;
      return {value: wartosc, itemStyle: {color: '#ffffff', borderColor: kolor, borderWidth: 2}};
    }

    async uruchomRozklad() {
      const rozklad = this.korzen.querySelector('[data-player-distribution]');
      const zrodlo = this.korzen.querySelector('[data-player-distribution-data]');
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
        aria: {show: true, description: 'Histogram liczby meczów według liczby zdobytych bramek: wszystkie, u siebie i na wyjeździe.'},
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

  class FormaZawodnikaController {
    constructor(korzen) {
      this.korzen = korzen;
    }

    async uruchom() {
      await Promise.all([this.uruchomTrendy(), this.uruchomForme()]);
    }

    async uruchomTrendy() {
      const trendWszystkie = this.korzen.querySelector('[data-player-trend-wszystkie]');
      const trendDom = this.korzen.querySelector('[data-player-trend-dom]');
      const trendWyjazd = this.korzen.querySelector('[data-player-trend-wyjazd]');
      const zrodlo = this.korzen.querySelector('[data-player-trend-data]');
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
      const formaWszystkie = this.korzen.querySelector('[data-player-form-wszystkie]');
      const formaDom = this.korzen.querySelector('[data-player-form-dom]');
      const formaWyjazd = this.korzen.querySelector('[data-player-form-wyjazd]');
      const boxplot = this.korzen.querySelector('[data-player-boxplot]');
      const zrodlo = this.korzen.querySelector('[data-player-forma-data]');
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
        aria: {show: true, description: 'Wykres bramek zawodnika w kolejnych meczach. Linia przerywana oznacza medianę.'},
        color: ['#2b6ea4'],
        grid: {left: 42, right: 18, top: 28, bottom: 54},
        tooltip: {
          trigger: 'item',
          renderMode: 'richText',
          formatter: parametry => {
            const punkt = punkty[parametry.dataIndex];
            return `${punkt.etykieta}\n${punkt.sezon} · ${punkt.rozgrywki}\nBramki: ${punkt.bramki ?? 'brak danych'}`;
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
          name: 'Bramki',
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
        if (id) window.open(this.korzen.dataset.playerMatchUrl.replace(/0$/, String(id)), '_blank', 'noopener');
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
        aria: {show: true, description: 'Wykres bramek zawodnika w kolejnych meczach z medianą i średnią kroczącą z 5 oraz mediną kroczącą z 10 meczów. Kolor punktu oznacza sezon.'},
        legend: {top: 0},
        grid: {left: 42, right: 18, top: 34, bottom: 54},
        tooltip: {
          trigger: 'item',
          renderMode: 'richText',
          formatter: parametry => {
            const punkt = punkty[parametry.dataIndex];
            return `${punkt.etykieta}\n${punkt.sezon}\nBramki: ${punkt.bramki ?? 'brak danych'}\nMediana 5: ${punkt.mediana_5?.toFixed(1) ?? '—'}\nŚrednia 5: ${punkt.srednia_5?.toFixed(1) ?? '—'}`;
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
            name: 'Bramki',
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
        if (id) window.open(this.korzen.dataset.playerMatchUrl.replace(/0$/, String(id)), '_blank', 'noopener');
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

  class DefensywaSkrotZawodnikaController {
    constructor(korzen) {
      this.korzen = korzen;
    }

    async uruchom() {
      const wykres = this.korzen.querySelector('[data-defense-summary]');
      const zrodlo = this.korzen.querySelector('[data-defense-summary-data]');
      if (!wykres || !zrodlo || wykres.dataset.chartReady) return;
      wykres.dataset.chartReady = 'true';
      try {
        const echarts = await zaladujECharts(this.korzen.dataset.echartsUrl);
        const klasy = JSON.parse(zrodlo.textContent);
        const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
        const instancja = echarts.init(wykres, null, {renderer: 'svg'});
        instancja.setOption({
          animation: !ograniczonyRuch,
          animationDuration: 400,
          aria: {show: true, description: 'Średnia liczba bramek zawodnika według pięciu klas jakości defensywy rywala, z liczbą meczów n przy każdej klasie.'},
          color: ['#2b6ea4'],
          grid: {left: 42, right: 18, top: 20, bottom: 60},
          tooltip: {
            trigger: 'item',
            formatter: parametry => `${parametry.name}\nŚrednia: ${parametry.value}\nn=${klasy[parametry.dataIndex].n}`,
          },
          xAxis: {
            type: 'category',
            data: klasy.map(k => k.klasa),
            axisLabel: {rotate: 20, hideOverlap: true},
          },
          yAxis: {type: 'value', name: 'Średnia bramek'},
          series: [{
            type: 'bar',
            barMaxWidth: 40,
            data: klasy.map(k => k.srednia),
            label: {show: true, position: 'top', formatter: parametry => `n=${klasy[parametry.dataIndex].n}`},
            emphasis: {focus: 'series'},
          }],
        });
        if (typeof ResizeObserver === 'function') new ResizeObserver(() => instancja.resize()).observe(wykres);
      } catch {
        wykres.textContent = 'Nie udało się narysować wykresu.';
      }
    }
  }

  class ZakladkiZawodnikaController {
    constructor(korzen, poWyborze = () => {}) {
      this.korzen = korzen;
      this.poWyborze = poWyborze;
    }

    uruchom() {
      const zdjecie = this.korzen.querySelector('[data-player-photo]');
      if (zdjecie) {
        const brak = () => {
          zdjecie.hidden = true;
          this.korzen.querySelector('[data-player-photo-fallback]').hidden = false;
        };
        zdjecie.addEventListener('error', brak);
        if (zdjecie.complete && !zdjecie.naturalWidth) brak();
      }
      this.podlaczSpisTresci();
      const pasek = this.korzen.querySelector('[data-player-tabs]');
      if (!pasek) return;
      this.przyciski = Array.from(pasek.querySelectorAll('[role="tab"]'));
      this.panele = Array.from(this.korzen.querySelectorAll('[data-player-panel]'));
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
      const indeks = this.przyciski.findIndex(p => p.dataset.playerTab === this.korzen.dataset.activeTab);
      this.wybierz(Math.max(0, indeks));
    }

    podlaczSpisTresci() {
      const spis = this.korzen.querySelector('[data-player-toc]');
      if (!spis) return;
      this.korzen.querySelectorAll('a[data-player-scroll]').forEach(link => {
        link.addEventListener('click', zdarzenie => {
          const cel = this.korzen.querySelector(link.getAttribute('href'));
          if (!cel) return;
          zdarzenie.preventDefault();
          const ograniczonyRuch = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
          cel.scrollIntoView({behavior: ograniczonyRuch ? 'auto' : 'smooth', block: 'start'});
          cel.focus({preventScroll: true});
        });
      });
    }

    wybierz(indeks) {
      this.przyciski.forEach((przycisk, numer) => {
        przycisk.setAttribute('aria-selected', String(numer === indeks));
        przycisk.tabIndex = numer === indeks ? 0 : -1;
      });
      const klucz = this.przyciski[indeks].dataset.playerTab;
      this.panele.forEach(panel => { panel.hidden = panel.dataset.playerPanel !== klucz; });
      if (klucz === 'podsumowanie') new AnalitykaZawodnikaController(this.korzen).uruchom();
      if (klucz === 'forma') {
        new FormaZawodnikaController(this.korzen).uruchom();
        new DefensywaSkrotZawodnikaController(this.korzen).uruchom();
      }
      this.poWyborze(klucz);
    }
  }

  class SzczegolyZawodnikaController {
    constructor(tabela, okno, pobierz) {
      this.tabela = tabela;
      this.okno = okno;
      this.pobierz = pobierz;
      this.tresc = okno.querySelector('[data-player-content]');
      this.link = okno.querySelector('[data-player-open-tab]');
      this.zadanie = null;
      this.wiersz = null;
    }

    uruchom() {
      this.okno.querySelectorAll('[data-player-close]').forEach(przycisk => {
        przycisk.addEventListener('click', () => this.okno.close());
      });
      this.okno.addEventListener('close', () => {
        this.zadanie?.abort();
        this.tresc.replaceChildren();
        this.wiersz?.focus();
      });
      this.tabela.querySelectorAll('tbody tr[data-player-href]').forEach(wiersz => {
        wiersz.classList.add('row-clickable');
        wiersz.tabIndex = 0;
        wiersz.addEventListener('dblclick', zdarzenie => {
          if (!zdarzenie.target.closest('a, button, input, select')) this.otworz(wiersz);
        });
        wiersz.addEventListener('keydown', zdarzenie => {
          if (zdarzenie.key === 'Enter' && zdarzenie.target === wiersz) {
            zdarzenie.preventDefault();
            this.otworz(wiersz);
          }
        });
      });
      this.tresc.addEventListener('submit', zdarzenie => {
        const formularz = zdarzenie.target.closest('[data-player-match-filters]');
        if (!formularz) return;
        zdarzenie.preventDefault();
        const adres = new URL(formularz.action, window.location.href);
        adres.search = new URLSearchParams(new FormData(formularz)).toString();
        this.wczytaj(adres.href);
      });
      this.tresc.addEventListener('click', zdarzenie => {
        const link = zdarzenie.target.closest('[data-player-page], .paginacja a');
        if (!link || zdarzenie.ctrlKey || zdarzenie.metaKey || zdarzenie.shiftKey || zdarzenie.altKey || zdarzenie.button > 0) return;
        zdarzenie.preventDefault();
        this.wczytaj(link.href);
      });
    }

    otworz(wiersz) {
      this.wiersz = wiersz;
      if (!this.okno.open) this.okno.showModal();
      this.wczytaj(wiersz.dataset.playerHref);
    }

    async wczytaj(adres) {
      this.zadanie?.abort();
      const zadanie = new AbortController();
      this.zadanie = zadanie;
      this.link.href = adres;
      this.tresc.textContent = 'Ładowanie szczegółów zawodnika…';
      this.tresc.setAttribute('aria-busy', 'true');
      try {
        const odpowiedz = await this.pobierz(adres, {signal: zadanie.signal});
        if (!odpowiedz.ok) throw new Error('Błąd odczytu');
        const dokument = new DOMParser().parseFromString(await odpowiedz.text(), 'text/html');
        const szczegoly = dokument.querySelector('[data-player-detail]');
        if (!szczegoly) throw new Error('Brak karty');
        szczegoly.querySelector('[data-player-navigation]')?.remove();
        if (!zadanie.signal.aborted) {
          this.tresc.replaceChildren(szczegoly);
          new ZakladkiZawodnikaController(szczegoly, klucz => {
            const url = new URL(this.link.href, window.location.href);
            url.searchParams.set('zakladka', klucz);
            this.link.href = url.href;
          }).uruchom();
          const panel = szczegoly.querySelector('[data-player-panel]:not([hidden])');
          panel?.focus({preventScroll: true});
          this.tresc.scrollTop = 0;
        }
      } catch {
        if (!zadanie.signal.aborted) {
          this.tresc.textContent = 'Nie udało się wczytać szczegółów zawodnika. Otwórz kartę w nowej karcie, aby sprawdzić odpowiedź, lub zamknij okno i spróbuj ponownie.';
        }
      } finally {
        if (this.zadanie === zadanie) this.tresc.removeAttribute('aria-busy');
      }
    }
  }

  const szczegoly = document.querySelector('[data-player-detail]');
  if (szczegoly) new ZakladkiZawodnikaController(szczegoly).uruchom();
  const tabela = document.getElementById('players-table');
  const okno = document.getElementById('player-detail-dialog');
  if (tabela && okno && typeof okno.showModal === 'function') {
    new SzczegolyZawodnikaController(tabela, okno, window.fetch.bind(window)).uruchom();
  }
})();
