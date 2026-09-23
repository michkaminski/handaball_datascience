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

  const ograniczonyRuch = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

  const wczytajJson = (korzen, selektor) => {
    const element = korzen.querySelector(selektor);
    return element ? JSON.parse(element.textContent) : null;
  };

  const obserwujRozmiar = (wykres, element) => {
    if (typeof ResizeObserver === 'function') new ResizeObserver(() => wykres.resize()).observe(element);
  };

  function rysujKlasy(echarts, korzen) {
    const element = korzen.querySelector('[data-defense-klasy]');
    const dane = wczytajJson(korzen, '[data-defense-klasy-data]');
    if (!element || !dane) return;
    const wykres = echarts.init(element, null, {renderer: 'svg'});
    wykres.setOption({
      animation: !ograniczonyRuch(),
      animationDuration: 400,
      aria: {show: true, description: 'Średnia liczba bramek zawodnika według pięciu klas jakości defensywy rywala, z liczbą meczów n przy każdej klasie.'},
      color: ['#2b6ea4'],
      grid: {left: 46, right: 18, top: 20, bottom: 60},
      tooltip: {
        trigger: 'item',
        formatter: parametry => `${parametry.name}\nŚrednia: ${parametry.value}\nn=${dane[parametry.dataIndex].n}`,
      },
      xAxis: {type: 'category', data: dane.map(k => k.klasa), axisLabel: {rotate: 20, hideOverlap: true}},
      yAxis: {type: 'value', name: 'Średnia bramek'},
      series: [{
        type: 'bar',
        barMaxWidth: 50,
        data: dane.map(k => k.srednia),
        label: {show: true, position: 'top', formatter: parametry => `n=${dane[parametry.dataIndex].n}`},
        emphasis: {focus: 'series'},
      }],
    });
    obserwujRozmiar(wykres, element);
  }

  function rysujBoxplot(echarts, korzen) {
    const element = korzen.querySelector('[data-defense-boxplot]');
    const dane = wczytajJson(korzen, '[data-defense-boxplot-data]');
    if (!element || !dane) return;
    const wykres = echarts.init(element, null, {renderer: 'svg'});
    wykres.setOption({
      animation: !ograniczonyRuch(),
      animationDuration: 400,
      aria: {show: true, description: 'Boxplot rozkładu bramek zawodnika według klasy defensywy rywala, z zaznaczonymi wartościami odstającymi.'},
      grid: {left: 46, right: 18, top: 20, bottom: 60},
      tooltip: {trigger: 'item'},
      xAxis: {type: 'category', data: dane.map(k => `${k.klasa} (n=${k.n})`), axisLabel: {rotate: 20, hideOverlap: true}},
      yAxis: {type: 'value', minInterval: 1, name: 'Bramki'},
      series: [
        {
          name: 'Rozstęp',
          type: 'boxplot',
          data: dane.map(k => [k.minimum, k.kwartyl_pierwszy, k.mediana, k.kwartyl_trzeci, k.maksimum]),
          itemStyle: {color: '#eef4fa', borderColor: '#2b6ea4'},
        },
        {
          name: 'Odstające',
          type: 'scatter',
          symbolSize: 7,
          itemStyle: {color: '#b04646'},
          data: dane.flatMap((k, indeks) => k.odstajace.map(wartosc => [indeks, wartosc])),
        },
      ],
    });
    obserwujRozmiar(wykres, element);
  }

  function rysujPrawdopodobienstwa(echarts, korzen) {
    const element = korzen.querySelector('[data-defense-prawdopodobienstwa]');
    const dane = wczytajJson(korzen, '[data-defense-prawdopodobienstwa-data]');
    if (!element || !dane || !dane.length) return;
    const progi = dane[0].progi.map(p => p.prog);
    const wykres = echarts.init(element, null, {renderer: 'svg'});
    wykres.setOption({
      animation: !ograniczonyRuch(),
      animationDuration: 400,
      aria: {show: true, description: 'Prawdopodobieństwo zdobycia co najmniej progowej liczby bramek w zależności od klasy defensywy rywala.'},
      legend: {top: 0},
      grid: {left: 46, right: 18, top: 34, bottom: 60},
      tooltip: {trigger: 'axis'},
      xAxis: {type: 'category', data: dane.map(k => k.klasa), axisLabel: {rotate: 20, hideOverlap: true}},
      yAxis: {type: 'value', name: 'Prawdopodobieństwo', axisLabel: {formatter: '{value}%'}},
      series: progi.map(prog => ({
        name: `P(${prog}+)`,
        type: 'line',
        data: dane.map(k => {
          const wpis = k.progi.find(p => p.prog === prog);
          return wpis ? Math.round(wpis.udzial * 1000) / 10 : null;
        }),
      })),
    });
    obserwujRozmiar(wykres, element);
  }

  function rysujScatter(echarts, korzen) {
    const element = korzen.querySelector('[data-defense-scatter]');
    const dane = wczytajJson(korzen, '[data-defense-scatter-data]');
    if (!element || !dane) return;
    const wykres = echarts.init(element, null, {renderer: 'svg'});
    wykres.setOption({
      animation: !ograniczonyRuch(),
      animationDuration: 400,
      aria: {show: true, description: 'Wykres punktowy: liczba bramek zawodnika w meczu względem Defense Factor rywala. Każdy punkt to jeden mecz.'},
      color: ['#2b6ea4'],
      grid: {left: 46, right: 18, top: 20, bottom: 46},
      tooltip: {
        trigger: 'item',
        formatter: parametry => {
          const p = dane[parametry.dataIndex];
          return `${p.etykieta}\n${p.sezon} · ${p.klasa}\nDefense Factor: ${p.x?.toFixed(2)}\nBramki: ${p.y}`;
        },
      },
      xAxis: {type: 'value', name: 'Defense Factor'},
      yAxis: {type: 'value', minInterval: 1, name: 'Bramki'},
      series: [{
        type: 'scatter',
        symbolSize: 9,
        emphasis: {focus: 'series', scale: 1.4},
        data: dane.map(p => ({value: [p.x, p.y], idMecz: p.id_mecz})),
      }],
    });
    wykres.on('click', parametry => {
      const id = parametry.data?.idMecz;
      if (id) window.open(korzen.dataset.playerMatchUrl.replace(/0$/, String(id)), '_blank', 'noopener');
    });
    obserwujRozmiar(wykres, element);
  }

  function podepnijSortowanieTabeli(korzen) {
    const tabela = korzen.querySelector('[data-defense-sortable]');
    if (!tabela) return;
    const naglowki = Array.from(tabela.querySelectorAll('th[data-sort]'));
    let biezacaKolumna = null;
    let rosnaco = true;
    naglowki.forEach((naglowek, indeks) => {
      naglowek.addEventListener('click', () => {
        rosnaco = biezacaKolumna === indeks ? !rosnaco : true;
        biezacaKolumna = indeks;
        naglowki.forEach(n => n.classList.remove('sorted-asc', 'sorted-desc'));
        naglowek.classList.add(rosnaco ? 'sorted-asc' : 'sorted-desc');
        const numeryczna = naglowek.hasAttribute('data-sort-num');
        const cialo = tabela.querySelector('tbody');
        const wiersze = Array.from(cialo.querySelectorAll('tr'));
        wiersze.sort((a, b) => {
          const tekstA = a.children[indeks]?.textContent.trim() ?? '';
          const tekstB = b.children[indeks]?.textContent.trim() ?? '';
          if (numeryczna) {
            const liczbaA = parseFloat(tekstA.replace(',', '.')) || -Infinity;
            const liczbaB = parseFloat(tekstB.replace(',', '.')) || -Infinity;
            return rosnaco ? liczbaA - liczbaB : liczbaB - liczbaA;
          }
          return rosnaco ? tekstA.localeCompare(tekstB, 'pl') : tekstB.localeCompare(tekstA, 'pl');
        });
        wiersze.forEach(wiersz => cialo.append(wiersz));
      });
    });
  }

  const korzen = document.querySelector('[data-defense-report]');
  if (!korzen) return;
  podepnijSortowanieTabeli(korzen);
  zaladujECharts(korzen.dataset.echartsUrl)
    .then(echarts => {
      rysujKlasy(echarts, korzen);
      rysujBoxplot(echarts, korzen);
      rysujPrawdopodobienstwa(echarts, korzen);
      rysujScatter(echarts, korzen);
    })
    .catch(() => {
      korzen.querySelectorAll('.player-chart').forEach(element => {
        element.textContent = 'Nie udało się narysować wykresu. Dane tabelaryczne pozostają dostępne powyżej.';
      });
    });
})();
