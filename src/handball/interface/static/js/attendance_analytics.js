(() => {
  const KOLORY = {
    glowny: '#2b6ea4',
    wybrany: '#3a7c67',
    akcent: '#9f6a15',
    neutralny: '#64748b',
    dodatni: '#3a7c67',
    ujemny: '#b04646',
    siatka: '#e5eaf0',
  };

  const formatuj = wartosc => {
    if (wartosc === null || wartosc === undefined) return '—';
    return Math.round(Number(wartosc)).toLocaleString('pl-PL').replace(/\u00a0/g, ' ');
  };

  const formatujRoznice = wartosc => {
    if (wartosc === null || wartosc === undefined) return '—';
    const liczba = Math.round(Number(wartosc));
    return `${liczba > 0 ? '+' : ''}${formatuj(liczba)}`;
  };

  const formatujProcent = wartosc => {
    if (wartosc === null || wartosc === undefined) return '—';
    return `${Number(wartosc).toLocaleString('pl-PL', {maximumFractionDigits: 1})}%`;
  };

  const opcjeWykresu = sezony => {
    const etykiety = sezony.map(sezon => sezon.sezon);
    const srednie = sezony.map(sezon => sezon.srednia);
    const mediana = sezony.map(sezon => sezon.mediana);
    const kroczaca = sezony.map(sezon => sezon.srednia_kroczaca);
    return {
      animationDuration: 320,
      animationDurationUpdate: 220,
      grid: {left: 56, right: 18, top: 36, bottom: 48},
      tooltip: {
        trigger: 'axis',
        valueFormatter: formatuj,
        formatter: parametry => {
          const indeks = parametry[0]?.dataIndex ?? 0;
          const sezon = sezony[indeks];
          if (!sezon) return '';
          return [
            `<b>${sezon.sezon}</b>`,
            `Średnia: ${formatuj(sezon.srednia)}`,
            `Mediana: ${formatuj(sezon.mediana)}`,
            `Q1–Q3: ${formatuj(sezon.q1)} – ${formatuj(sezon.q3)}`,
            `Suma: ${formatuj(sezon.suma)}`,
            `Znane: ${formatuj(sezon.znane)} / ${formatuj(sezon.rozegrane)}`,
          ].join('<br>');
        },
      },
      legend: {top: 0, data: ['Średnia', 'Mediana', 'Śr. 3 sezony']},
      xAxis: {
        type: 'category',
        data: etykiety,
        axisLabel: {rotate: etykiety.length > 12 ? 35 : 0, fontSize: 11},
      },
      yAxis: {
        type: 'value',
        name: 'Widzowie',
        axisLabel: {formatter: formatuj},
        splitLine: {lineStyle: {color: KOLORY.siatka}},
      },
      series: [
        {
          name: 'Średnia',
          type: 'bar',
          data: srednie.map((wartosc, indeks) => ({
            value: wartosc,
            itemStyle: {color: sezony[indeks].wybrany ? KOLORY.wybrany : KOLORY.glowny},
          })),
          barMaxWidth: 42,
        },
        {
          name: 'Mediana',
          type: 'line',
          data: mediana,
          showSymbol: sezony.length <= 20,
          symbolSize: 6,
          lineStyle: {width: 2, color: KOLORY.akcent},
          itemStyle: {color: KOLORY.akcent},
        },
        {
          name: 'Śr. 3 sezony',
          type: 'line',
          data: kroczaca,
          showSymbol: false,
          lineStyle: {width: 2, type: 'dashed', color: KOLORY.neutralny},
          itemStyle: {color: KOLORY.neutralny},
        },
      ],
    };
  };

  const opcjePokrycia = pokrycie => {
    const etykiety = pokrycie.map(punkt => punkt.sezon);
    return {
      animationDuration: 320,
      grid: {left: 56, right: 56, top: 36, bottom: 48},
      tooltip: {
        trigger: 'axis',
        formatter: parametry => {
          const punkt = pokrycie[parametry[0]?.dataIndex ?? 0];
          if (!punkt) return '';
          return [
            `<b>${punkt.sezon}</b>`,
            `Znane: ${formatuj(punkt.znane)} / ${formatuj(punkt.rozegrane)}`,
            `Pokrycie: ${formatujProcent(punkt.pokrycie)}`,
          ].join('<br>');
        },
      },
      legend: {top: 0, data: ['Mecze ze znaną frekwencją', 'Pokrycie %']},
      xAxis: {
        type: 'category',
        data: etykiety,
        axisLabel: {rotate: etykiety.length > 12 ? 35 : 0, fontSize: 11},
      },
      yAxis: [
        {
          type: 'value',
          name: 'Mecze',
          axisLabel: {formatter: formatuj},
          splitLine: {lineStyle: {color: KOLORY.siatka}},
        },
        {
          type: 'value',
          name: '%',
          min: 0,
          max: 100,
          axisLabel: {formatter: '{value}%'},
          splitLine: {show: false},
        },
      ],
      series: [
        {
          name: 'Mecze ze znaną frekwencją',
          type: 'bar',
          data: pokrycie.map(punkt => punkt.znane),
          barMaxWidth: 36,
          itemStyle: {color: KOLORY.glowny},
        },
        {
          name: 'Pokrycie %',
          type: 'line',
          yAxisIndex: 1,
          data: pokrycie.map(punkt => punkt.pokrycie),
          showSymbol: pokrycie.length <= 20,
          symbolSize: 6,
          lineStyle: {width: 2, color: KOLORY.akcent},
          itemStyle: {color: KOLORY.akcent},
        },
      ],
    };
  };

  const opcjeSlupkowe = (pozycje, opisz, nazwaSerii = 'Średnia') => ({
    animationDuration: 320,
    grid: {left: 56, right: 18, top: 20, bottom: pozycje.length > 8 ? 56 : 40},
    tooltip: {
      trigger: 'axis',
      axisPointer: {type: 'shadow'},
      formatter: parametry => {
        const pozycja = pozycje[parametry[0]?.dataIndex ?? 0];
        return pozycja ? opisz(pozycja).join('<br>') : '';
      },
    },
    xAxis: {
      type: 'category',
      data: pozycje.map(pozycja => pozycja.etykieta),
      axisLabel: {rotate: pozycje.length > 8 ? 35 : 0, fontSize: 11},
    },
    yAxis: {
      type: 'value',
      name: 'Widzowie',
      axisLabel: {formatter: formatuj},
      splitLine: {lineStyle: {color: KOLORY.siatka}},
    },
    series: [{
      name: nazwaSerii,
      type: 'bar',
      data: pozycje.map(pozycja => pozycja.srednia),
      barMaxWidth: 40,
      itemStyle: {color: KOLORY.glowny},
    }],
  });

  const opcjeKalendarza = grupy => opcjeSlupkowe(grupy, grupa => [
    `<b>${grupa.etykieta}</b>`,
    `Średnia: ${formatuj(grupa.srednia)}`,
    `Znane: ${formatuj(grupa.znane)} / ${formatuj(grupa.rozegrane)}`,
  ]);

  const opcjeEfektuDnia = grupy => opcjeSlupkowe(grupy, grupa => [
    `<b>${grupa.etykieta}</b>`,
    `Średnia: ${formatuj(grupa.srednia)}`,
    `n: ${formatuj(grupa.n)}`,
  ]);

  const opcjePoziome = (pozycje, kolorPozycji, opisz, wartosc = pozycja => pozycja.srednia, nazwaSerii = 'Średnia') => ({
    animationDuration: 320,
    grid: {left: 150, right: 36, top: 12, bottom: 28},
    tooltip: {
      trigger: 'axis',
      axisPointer: {type: 'shadow'},
      formatter: parametry => {
        const pozycja = pozycje[parametry[0]?.dataIndex ?? 0];
        return pozycja ? opisz(pozycja).join('<br>') : '';
      },
    },
    xAxis: {
      type: 'value',
      axisLabel: {formatter: formatuj},
      splitLine: {lineStyle: {color: KOLORY.siatka}},
    },
    yAxis: {
      type: 'category',
      inverse: true,
      data: pozycje.map(pozycja => pozycja.nazwa),
      axisLabel: {width: 136, overflow: 'truncate', fontSize: 11},
    },
    series: [{
      name: nazwaSerii,
      type: 'bar',
      data: pozycje.map(pozycja => ({value: wartosc(pozycja), itemStyle: {color: kolorPozycji(pozycja)}})),
      barMaxWidth: 22,
      label: {show: pozycje.length <= 20, position: 'right', fontSize: 10, formatter: parametry => formatuj(parametry.value)},
    }],
  });

  const opcjeKlubow = kluby => opcjePoziome(kluby, () => KOLORY.glowny, klub => [
    `<b>${klub.nazwa}</b>`,
    `Średnia: ${formatuj(klub.srednia)}`,
    `Znane mecze: ${formatuj(klub.znane)}`,
  ]);

  const opcjeMiast = miasta => opcjePoziome(
    miasta,
    () => KOLORY.wybrany,
    miasto => [
      `<b>${miasto.nazwa}</b>`,
      `Suma: ${formatuj(miasto.suma)}`,
      `Średnia: ${formatuj(miasto.srednia)}`,
      `Mediana: ${formatuj(miasto.mediana)}`,
      `Dominanta: ${formatuj(miasto.dominanta)}`,
      `Znane mecze: ${formatuj(miasto.znane)}`,
      `Kluby: ${formatuj(miasto.kluby)}`,
    ],
    miasto => miasto.suma,
    'Suma',
  );

  const opisPozycjiMiasta = pozycja => [
    `<b>${pozycja.nazwa}</b>`,
    `Suma: ${formatuj(pozycja.suma)}`,
    `Średnia: ${formatuj(pozycja.srednia)}`,
    `Mediana: ${formatuj(pozycja.mediana)}`,
    `Znane mecze: ${formatuj(pozycja.znane)}`,
  ];

  const opcjeSezonowMiasta = sezony => ({
    animationDuration: 320,
    grid: {left: 56, right: 18, top: 36, bottom: sezony.length > 8 ? 56 : 40},
    legend: {top: 0, data: ['Średnia', 'Mediana']},
    tooltip: {
      trigger: 'axis',
      formatter: parametry => {
        const sezon = sezony[parametry[0]?.dataIndex ?? 0];
        if (!sezon) return '';
        return [
          `<b>${sezon.sezon}</b>`,
          `Średnia: ${formatuj(sezon.srednia)}`,
          `Mediana: ${formatuj(sezon.mediana)}`,
          `Suma: ${formatuj(sezon.suma)}`,
          `Znane: ${formatuj(sezon.znane)} / ${formatuj(sezon.rozegrane)}`,
        ].join('<br>');
      },
    },
    xAxis: {
      type: 'category',
      data: sezony.map(sezon => sezon.sezon),
      axisLabel: {rotate: sezony.length > 8 ? 35 : 0, fontSize: 11},
    },
    yAxis: {
      type: 'value',
      name: 'Widzowie',
      axisLabel: {formatter: formatuj},
      splitLine: {lineStyle: {color: KOLORY.siatka}},
    },
    series: [
      {
        name: 'Średnia',
        type: 'bar',
        data: sezony.map(sezon => sezon.srednia),
        barMaxWidth: 36,
        itemStyle: {color: KOLORY.wybrany},
      },
      {
        name: 'Mediana',
        type: 'line',
        data: sezony.map(sezon => sezon.mediana),
        showSymbol: sezony.length <= 20,
        symbolSize: 6,
        lineStyle: {width: 2, color: KOLORY.akcent},
        itemStyle: {color: KOLORY.akcent},
      },
    ],
  });

  const opcjeRozgrywekMiasta = rozgrywki => opcjePoziome(
    rozgrywki,
    () => KOLORY.akcent,
    opisPozycjiMiasta,
    pozycja => pozycja.suma,
    'Suma',
  );

  const opcjeHalMiasta = hale => opcjePoziome(
    hale,
    () => KOLORY.glowny,
    opisPozycjiMiasta,
    pozycja => pozycja.suma,
    'Suma',
  );

  const wybraneMiasto = (dane, stan) => {
    const lista = Array.isArray(dane.miastaSzczegoly) ? dane.miastaSzczegoly : [];
    return lista.find(miasto => miasto.klucz === stan.miasto) ?? lista[0] ?? null;
  };

  const opcjePrzeciwnikow = przeciwnicy => opcjePoziome(
    przeciwnicy,
    przeciwnik => ((przeciwnik.roznica ?? 0) < 0 ? KOLORY.ujemny : KOLORY.dodatni),
    przeciwnik => [
      `<b>${przeciwnik.nazwa}</b>`,
      `Średnia: ${formatuj(przeciwnik.srednia)}`,
      `Różnica vs średnia gospodarza: ${formatujRoznice(przeciwnik.roznica)}`,
    ],
  );

  const opcjeHeatmapy = heatmapa => {
    const {dni, godziny, komorki} = heatmapa;
    const minimum = heatmapa.minimum ?? 0;
    const maksimum = Math.max(heatmapa.maksimum ?? 1, minimum + 1);
    return {
      animationDuration: 320,
      grid: {left: 96, right: 24, top: 16, bottom: 72},
      tooltip: {
        position: 'top',
        formatter: parametry => {
          const [x, y, srednia, znane] = parametry.value;
          return [
            `<b>${dni[y]}, ${godziny[x]}</b>`,
            `Średnia: ${formatuj(srednia)}`,
            `Mecze ze znaną frekwencją: ${formatuj(znane)}`,
          ].join('<br>');
        },
      },
      xAxis: {type: 'category', data: godziny, splitArea: {show: true}, axisLabel: {fontSize: 11}},
      yAxis: {type: 'category', data: dni, inverse: true, splitArea: {show: true}},
      visualMap: {
        min: minimum,
        max: maksimum,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        formatter: formatuj,
        inRange: {color: ['#eaf3f8', KOLORY.glowny, '#173e65']},
      },
      series: [{
        name: 'Średnia frekwencja',
        type: 'heatmap',
        data: komorki.map(komorka => [komorka.x, komorka.y, komorka.srednia, komorka.znane]),
        label: {show: godziny.length <= 12, formatter: parametry => formatuj(parametry.value[2]), fontSize: 10},
        emphasis: {itemStyle: {borderColor: KOLORY.akcent, borderWidth: 2}},
      }],
    };
  };

  const opcjeHistogramu = histogram => ({
    animationDuration: 320,
    grid: {left: 56, right: 18, top: 24, bottom: 64},
    tooltip: {
      trigger: 'axis',
      axisPointer: {type: 'shadow'},
      formatter: parametry => {
        const przedzial = histogram.przedzialy[parametry[0]?.dataIndex ?? 0];
        if (!przedzial) return '';
        return `<b>${przedzial.etykieta} widzów</b><br>Mecze: ${formatuj(przedzial.liczba)}`;
      },
    },
    xAxis: {
      type: 'category',
      data: histogram.przedzialy.map(przedzial => przedzial.etykieta),
      name: 'Widzowie',
      nameLocation: 'middle',
      nameGap: 44,
      axisLabel: {rotate: histogram.przedzialy.length > 8 ? 35 : 0, fontSize: 11},
    },
    yAxis: {type: 'value', name: 'Mecze', splitLine: {lineStyle: {color: KOLORY.siatka}}},
    series: [{
      name: 'Mecze',
      type: 'bar',
      data: histogram.przedzialy.map(przedzial => przedzial.liczba),
      barCategoryGap: '8%',
      itemStyle: {color: KOLORY.glowny},
    }],
  });

  const maPozycje = lista => Array.isArray(lista) && lista.length > 0;
  const maSrednie = lista => maPozycje(lista) && lista.some(pozycja => pozycja.srednia !== null && pozycja.srednia !== undefined);

  const WYKRESY = {
    trend: {
      ma: dane => maSrednie(dane.sezony),
      pusty: 'Brak znanej frekwencji do narysowania wykresu.',
      opcje: dane => opcjeWykresu(dane.sezony),
    },
    coverage: {
      ma: dane => maPozycje(dane.pokrycie),
      pusty: 'Brak sezonów do narysowania pokrycia.',
      opcje: dane => opcjePokrycia(dane.pokrycie),
    },
    clubs: {
      ma: dane => maSrednie(dane.kluby),
      pusty: 'Brak klubów ze znaną frekwencją.',
      opcje: dane => opcjeKlubow(dane.kluby),
    },
    cities: {
      ma: dane => maPozycje(dane.miasta),
      pusty: 'Brak miast klubów ze znaną frekwencją.',
      opcje: dane => opcjeMiast(dane.miasta),
    },
    citySeasons: {
      ma: (dane, stan) => maPozycje(wybraneMiasto(dane, stan)?.sezony),
      pusty: 'Brak sezonów ze znaną frekwencją dla wybranego miasta.',
      opcje: (dane, stan) => opcjeSezonowMiasta(wybraneMiasto(dane, stan).sezony),
    },
    cityCompetitions: {
      ma: (dane, stan) => maPozycje(wybraneMiasto(dane, stan)?.rozgrywki),
      pusty: 'Brak rozgrywek ze znaną frekwencją dla wybranego miasta.',
      opcje: (dane, stan) => opcjeRozgrywekMiasta(wybraneMiasto(dane, stan).rozgrywki),
    },
    cityHalls: {
      ma: (dane, stan) => maPozycje(wybraneMiasto(dane, stan)?.hale),
      pusty: 'Brak hal z meczami ze znaną frekwencją dla wybranego miasta.',
      opcje: (dane, stan) => opcjeHalMiasta(wybraneMiasto(dane, stan).hale),
    },
    heatmap: {
      ma: dane => maPozycje(dane.heatmapa?.komorki),
      pusty: 'Brak meczów ze znaną godziną do narysowania mapy cieplnej.',
      opcje: dane => opcjeHeatmapy(dane.heatmapa),
    },
    months: {
      ma: dane => maSrednie(dane.miesiace),
      pusty: 'Brak meczów z terminem do narysowania wykresu miesięcy.',
      opcje: dane => opcjeKalendarza(dane.miesiace),
    },
    weekdays: {
      ma: dane => maSrednie(dane.dni),
      pusty: 'Brak meczów z terminem do narysowania wykresu dni tygodnia.',
      opcje: dane => opcjeKalendarza(dane.dni),
    },
    hours: {
      ma: dane => maSrednie(dane.godziny),
      pusty: 'Brak meczów ze znaną godziną do narysowania wykresu godzin.',
      opcje: dane => opcjeKalendarza(dane.godziny),
    },
    opponents: {
      ma: dane => maSrednie(dane.przeciwnicy),
      pusty: 'Brak przeciwników ze znaną frekwencją.',
      opcje: dane => opcjePrzeciwnikow(dane.przeciwnicy),
    },
    histogram: {
      ma: dane => maPozycje(dane.histogram?.przedzialy),
      pusty: 'Brak znanej frekwencji do narysowania histogramu.',
      opcje: dane => opcjeHistogramu(dane.histogram),
    },
    weekdayEffect: {
      ma: dane => maSrednie(dane.efektDnia),
      pusty: 'Brak meczów z terminem do narysowania efektu dnia tygodnia.',
      opcje: dane => opcjeEfektuDnia(dane.efektDnia),
    },
  };

  const odczytajDane = () => {
    const dane = document.getElementById('attendance-chart-data');
    if (!dane) return null;
    try {
      return JSON.parse(dane.textContent);
    } catch (_blad) {
      return null;
    }
  };

  const komunikat = (miejsce, tekst) => {
    miejsce.textContent = tekst;
    miejsce.classList.add('note');
  };

  const bezAnimacji = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  class MenedzerWykresow {
    constructor(korzen, dane, definicje) {
      this.korzen = korzen;
      this.dane = dane;
      this.definicje = definicje;
      this.instancje = new Map();
      this.oczekujace = new Set();
      this.ladowanieBiblioteki = null;
      this.stan = {miasto: null};
    }

    podlaczOknoPrzegladarki() {
      window.addEventListener('resize', () => this.dopasuj(this.korzen));
    }

    async pokaz(zakres) {
      const miejsca = [...zakres.querySelectorAll('[data-chart]')];
      if (!miejsca.length) return;
      this.dopasuj(zakres);
      await this.rysuj(miejsca);
    }

    odswiez(klucze, zakres) {
      const miejsca = [...zakres.querySelectorAll('[data-chart]')]
        .filter(miejsce => klucze.includes(miejsce.dataset.chart));
      miejsca.forEach(miejsce => this.wyczysc(miejsce));
      return this.rysuj(miejsca);
    }

    wyczysc(miejsce) {
      const wykres = this.instancje.get(miejsce);
      if (wykres) {
        wykres.dispose();
        this.instancje.delete(miejsce);
      }
      miejsce.textContent = '';
      miejsce.classList.remove('note');
    }

    async rysuj(miejsca) {
      const nowe = miejsca.filter(miejsce => !this.instancje.has(miejsce) && !this.oczekujace.has(miejsce));
      if (!nowe.length) return;
      if (!this.dane) {
        nowe.forEach(miejsce => komunikat(miejsce, 'Nie udało się odczytać danych wykresu.'));
        return;
      }
      const doNarysowania = nowe.filter(miejsce => this.przygotuj(miejsce));
      if (!doNarysowania.length) return;
      doNarysowania.forEach(miejsce => this.oczekujace.add(miejsce));
      try {
        const echarts = await this.pobierzBiblioteke();
        doNarysowania.forEach(miejsce => this.narysuj(echarts, miejsce));
      } catch (_blad) {
        doNarysowania.forEach(miejsce => komunikat(miejsce, 'Nie udało się załadować wykresu. Dane tabelaryczne pozostają dostępne.'));
      } finally {
        doNarysowania.forEach(miejsce => this.oczekujace.delete(miejsce));
      }
    }

    przygotuj(miejsce) {
      const definicja = this.definicje[miejsce.dataset.chart];
      if (!definicja) return false;
      if (definicja.ma(this.dane, this.stan)) return true;
      komunikat(miejsce, definicja.pusty);
      return false;
    }

    pobierzBiblioteke() {
      if (!this.ladowanieBiblioteki) {
        this.ladowanieBiblioteki = globalThis.HandballWykresyBramek.zaladujECharts(this.korzen.dataset.echartsUrl);
      }
      return this.ladowanieBiblioteki;
    }

    narysuj(echarts, miejsce) {
      const wykres = echarts.init(miejsce, null, {renderer: 'svg'});
      wykres.setOption(this.definicje[miejsce.dataset.chart].opcje(this.dane, this.stan));
      if (bezAnimacji()) wykres.setOption({animation: false});
      this.instancje.set(miejsce, wykres);
    }

    dopasuj(zakres) {
      this.instancje.forEach((wykres, miejsce) => {
        if (zakres.contains(miejsce) && miejsce.offsetParent !== null) wykres.resize();
      });
    }
  }

  class ZakladkiFrekwencji {
    constructor(korzen, menedzer) {
      this.korzen = korzen;
      this.menedzer = menedzer;
      this.pasek = korzen.querySelector('[data-attendance-tabs]');
      this.przyciski = this.pasek ? [...this.pasek.querySelectorAll('[role="tab"]')] : [];
      this.panele = [...korzen.querySelectorAll('[data-attendance-panel]')];
    }

    uruchom() {
      if (!this.pasek || !this.przyciski.length) return false;
      this.panele.forEach(panel => {
        panel.setAttribute('role', 'tabpanel');
        panel.tabIndex = 0;
      });
      this.pasek.hidden = false;
      this.przyciski.forEach((przycisk, indeks) => {
        przycisk.addEventListener('click', () => this.wybierz(indeks, true));
        przycisk.addEventListener('keydown', zdarzenie => this.obsluzKlawisz(zdarzenie, indeks));
      });
      window.addEventListener('hashchange', () => this.otworzDlaKotwicy(false));
      const poczatkowa = this.indeksKlucza(this.korzen.dataset.activeTab);
      this.wybierz(Math.max(0, poczatkowa), false);
      this.otworzDlaKotwicy(false);
      return true;
    }

    indeksKlucza(klucz) {
      return this.przyciski.findIndex(przycisk => przycisk.dataset.tab === klucz);
    }

    obsluzKlawisz(zdarzenie, indeks) {
      const ostatni = this.przyciski.length - 1;
      const cele = {
        ArrowRight: indeks === ostatni ? 0 : indeks + 1,
        ArrowLeft: indeks === 0 ? ostatni : indeks - 1,
        Home: 0,
        End: ostatni,
      };
      if (!(zdarzenie.key in cele)) return;
      zdarzenie.preventDefault();
      this.wybierz(cele[zdarzenie.key], true);
      this.przyciski[cele[zdarzenie.key]].focus();
    }

    otworzDlaKotwicy(zapisz) {
      if (!window.location.hash) return;
      let cel = null;
      try {
        cel = this.korzen.querySelector(window.location.hash);
      } catch (_blad) {
        return;
      }
      const panel = cel?.closest('[data-attendance-panel]');
      if (!panel) return;
      const indeks = this.indeksKlucza(panel.dataset.attendancePanel);
      if (indeks >= 0) this.wybierz(indeks, zapisz);
    }

    wybierz(indeks, zapisz) {
      const klucz = this.przyciski[indeks].dataset.tab;
      this.przyciski.forEach((przycisk, numer) => {
        przycisk.setAttribute('aria-selected', String(numer === indeks));
        przycisk.tabIndex = numer === indeks ? 0 : -1;
      });
      this.panele.forEach(panel => { panel.hidden = panel.dataset.attendancePanel !== klucz; });
      this.zapamietaj(klucz, zapisz);
      const aktywny = this.panele.find(panel => panel.dataset.attendancePanel === klucz);
      if (aktywny) this.menedzer.pokaz(aktywny);
    }

    zapamietaj(klucz, zapisz) {
      const pole = document.querySelector('[data-attendance-tab-field]');
      if (pole) pole.value = klucz;
      if (!zapisz) return;
      const adres = new URL(window.location.href);
      adres.searchParams.delete('tab');
      adres.searchParams.set('zakladka', klucz);
      window.history.replaceState(null, '', adres);
    }
  }

  class FiltrTabeli {
    constructor(korzen) {
      this.pole = korzen.querySelector('[data-filter-input]');
      this.listy = [...korzen.querySelectorAll('[data-filter-select]')];
      this.tabela = korzen.querySelector('[data-filter-table]');
    }

    uruchom() {
      if (!this.tabela || !this.pole) return;
      const cialo = this.tabela.tBodies[0];
      this.wiersze = [...cialo.querySelectorAll('tr[data-filter-text]')];
      this.pusty = cialo.querySelector('.att-empty');
      this.pole.addEventListener('input', () => this.zastosuj());
      this.listy.forEach(lista => lista.addEventListener('change', () => this.zastosuj()));
    }

    pasuje(wiersz, zapytanie) {
      if (zapytanie && !wiersz.dataset.filterText.includes(zapytanie)) return false;
      return this.listy.every(lista => {
        const wartosc = lista.value;
        return !wartosc || wiersz.getAttribute(`data-filter-${lista.dataset.filterSelect}`) === wartosc;
      });
    }

    zastosuj() {
      const zapytanie = this.pole.value.trim().toLowerCase();
      let widoczne = 0;
      this.wiersze.forEach(wiersz => {
        const pasuje = this.pasuje(wiersz, zapytanie);
        wiersz.hidden = !pasuje;
        if (pasuje) widoczne += 1;
      });
      if (this.pusty) this.pusty.hidden = widoczne > 0;
    }
  }

  const WYKRESY_MIASTA = ['citySeasons', 'cityCompetitions', 'cityHalls'];

  class WyborMiasta {
    constructor(korzen, menedzer) {
      this.menedzer = menedzer;
      this.zakres = korzen.querySelector('[data-city-charts]');
      this.pole = this.zakres ? this.zakres.querySelector('[data-city-select]') : null;
    }

    uruchom() {
      if (!this.pole) return;
      this.menedzer.stan.miasto = this.pole.value || null;
      this.pole.addEventListener('change', () => {
        this.menedzer.stan.miasto = this.pole.value || null;
        this.menedzer.odswiez(WYKRESY_MIASTA, this.zakres);
      });
    }
  }

  const podlaczFiltry = () => {
    document.querySelectorAll('[data-attendance-filter]').forEach(korzen => new FiltrTabeli(korzen).uruchom());
  };

  const korzen = document.querySelector('[data-attendance]');
  if (korzen) {
    const menedzer = new MenedzerWykresow(korzen, odczytajDane(), WYKRESY);
    menedzer.podlaczOknoPrzegladarki();
    new WyborMiasta(korzen, menedzer).uruchom();
    const zakladki = new ZakladkiFrekwencji(korzen, menedzer);
    if (!zakladki.uruchom()) menedzer.pokaz(korzen);
  }
  podlaczFiltry();
})();
