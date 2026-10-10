(() => {
  const korzen = document.querySelector('[data-mathlib]');
  if (!korzen) return;

  const KOLORY = {glowny: '#2b6ea4', drugi: '#3a7c67', akcent: '#9f6a15', siatka: '#e5eaf0'};
  const ruchOgraniczony = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const renderujWzory = element => {
    if (typeof window.renderMathInElement !== 'function') return;
    window.renderMathInElement(element, {
      delimiters: [
        {left: '\\[', right: '\\]', display: true},
        {left: '\\(', right: '\\)', display: false},
      ],
      throwOnError: false,
      strict: 'ignore',
    });
  };

  const numerujWzory = artykul => {
    const numery = new Map();
    artykul.querySelectorAll('.ml-eq[id]').forEach((wzor, indeks) => {
      const numer = indeks + 1;
      numery.set(wzor.id, numer);
      const etykieta = document.createElement('span');
      etykieta.className = 'ml-eqnum';
      etykieta.innerHTML = `<a href="#${wzor.id}" title="Bezpośredni odnośnik do wzoru">(${numer})</a>`;
      wzor.append(etykieta);
    });
    artykul.querySelectorAll('a.ml-eqref').forEach(odnosnik => {
      const cel = (odnosnik.getAttribute('href') || '').slice(1);
      if (numery.has(cel)) odnosnik.textContent = `(${numery.get(cel)})`;
    });
  };

  const lgamma = x => {
    const g = 7;
    const c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
      -176.61503916999185, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6,
      1.5056327351493116e-7];
    if (x < 0.5) return Math.log(Math.PI / Math.abs(Math.sin(Math.PI * x))) - lgamma(1 - x);
    x -= 1;
    let a = c[0];
    const t = x + g + 0.5;
    for (let i = 1; i < g + 2; i += 1) a += c[i] / (x + i);
    return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
  };
  const lbeta = (a, b) => lgamma(a) + lgamma(b) - lgamma(a + b);
  const lchoose = (n, k) => lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1);
  const zakres = (od, doo, kroki) => Array.from({length: kroki + 1}, (_, i) => od + (doo - od) * i / kroki);
  const gestoscBeta = (x, a, b) => (x <= 0 || x >= 1) ? 0 : Math.exp((a - 1) * Math.log(x) + (b - 1) * Math.log(1 - x) - lbeta(a, b));

  const SUWAKI = {
    mu: [-5, 5, 0.1], sigma: [0.1, 5, 0.1], a: [0.2, 30, 0.1], b: [0.2, 30, 0.1],
    phi: [0.5, 100, 0.5], n: [1, 200, 1], p: [0.01, 0.99, 0.01], kappa: [0.2, 50, 0.1],
    alpha: [-5, 5, 0.1], beta: [-4, 4, 0.1], k: [0, 200, 1], tau: [0.05, 2, 0.05],
  };
  const SUWAKI_SREDNIEJ = {mu: [0.01, 0.99, 0.01]};

  const TYPY = {
    normal: {
      tytul: p => `N(μ = ${p.mu}, σ = ${p.sigma})`,
      dane: p => {
        const xs = zakres(p.mu - 4 * p.sigma, p.mu + 4 * p.sigma, 200);
        return {ciagly: true, serie: [{nazwa: 'gęstość', punkty: xs.map(x => [x, Math.exp(-0.5 * ((x - p.mu) / p.sigma) ** 2) / (p.sigma * Math.sqrt(2 * Math.PI))])}]};
      },
    },
    beta: {
      tytul: p => `Beta(a = ${p.a}, b = ${p.b}), średnia = ${(p.a / (p.a + p.b)).toFixed(3)}`,
      dane: p => ({ciagly: true, serie: [{nazwa: 'gęstość', punkty: zakres(0.001, 0.999, 200).map(x => [x, gestoscBeta(x, p.a, p.b)])}]}),
    },
    'beta-mean': {
      suwaki: SUWAKI_SREDNIEJ,
      tytul: p => `Beta(μ = ${p.mu}, φ = ${p.phi}): a = ${(p.mu * p.phi).toFixed(2)}, b = ${((1 - p.mu) * p.phi).toFixed(2)}`,
      dane: p => ({ciagly: true, serie: [{nazwa: 'gęstość', punkty: zakres(0.001, 0.999, 200).map(x => [x, gestoscBeta(x, p.mu * p.phi, (1 - p.mu) * p.phi)])}]}),
    },
    binomial: {
      tytul: p => `Bin(n = ${p.n}, p = ${p.p})`,
      dane: p => ({ciagly: false, serie: [{nazwa: 'P(X = k)', punkty: zakres(0, p.n, p.n).map(k => [k, Math.exp(lchoose(p.n, k) + k * Math.log(p.p) + (p.n - k) * Math.log(1 - p.p))])}]}),
    },
    betabinomial: {
      tytul: p => `BetaBin(n = ${p.n}, a = ${p.a}, b = ${p.b})`,
      dane: p => ({ciagly: false, serie: [{nazwa: 'P(X = k)', punkty: zakres(0, p.n, p.n).map(k => [k, Math.exp(lchoose(p.n, k) + lbeta(k + p.a, p.n - k + p.b) - lbeta(p.a, p.b))])}]}),
    },
    negbinomial: {
      suwaki: {mu: [1, 3000, 1]},
      tytul: p => `NB(μ = ${p.mu}, κ = ${p.kappa}), wariancja = ${Math.round(p.mu + p.mu * p.mu / p.kappa)}`,
      dane: p => {
        const gora = Math.ceil(p.mu + 4 * Math.sqrt(p.mu + p.mu * p.mu / p.kappa));
        const krok = Math.max(1, Math.floor(gora / 300));
        const punkty = [];
        for (let y = 0; y <= gora; y += krok) {
          punkty.push([y, Math.exp(lgamma(y + p.kappa) - lgamma(p.kappa) - lgamma(y + 1) + p.kappa * Math.log(p.kappa / (p.kappa + p.mu)) + y * Math.log(p.mu / (p.kappa + p.mu)))]);
        }
        return {ciagly: krok > 1, serie: [{nazwa: 'P(Y = y)', punkty}]};
      },
    },
    logistic: {
      tytul: p => `p(x) = logit⁻¹(${p.alpha} + ${p.beta}·x)`,
      dane: p => ({ciagly: true, serie: [{nazwa: 'p(x)', punkty: zakres(-6, 6, 200).map(x => [x, 1 / (1 + Math.exp(-(p.alpha + p.beta * x)))])}]}),
    },
    'beta-update': {
      tytul: p => `Prior Beta(${p.a}, ${p.b}) → posterior Beta(${p.a + p.k}, ${p.b + Math.max(p.n - p.k, 0)})`,
      dane: p => {
        const k = Math.min(p.k, p.n);
        const xs = zakres(0.001, 0.999, 200);
        return {ciagly: true, serie: [
          {nazwa: 'prior', punkty: xs.map(x => [x, gestoscBeta(x, p.a, p.b)]), przerywana: true},
          {nazwa: 'posterior', punkty: xs.map(x => [x, gestoscBeta(x, p.a + k, p.b + p.n - k)])},
        ]};
      },
    },
    shrinkage: {
      tytul: p => `Współczynnik ściągania B(n) = (σ²/n) / (σ²/n + τ²), τ = ${p.tau}, σ = ${p.sigma}`,
      dane: p => ({ciagly: true, osX: 'liczba meczów n', osY: 'waga średniej populacji', serie: [{nazwa: 'B(n)', punkty: zakres(1, 60, 59).map(n => [n, (p.sigma ** 2 / n) / (p.sigma ** 2 / n + p.tau ** 2)])}]}),
    },
  };

  let ladowanie = null;
  const zaladujECharts = () => {
    if (window.echarts) return Promise.resolve(window.echarts);
    if (!ladowanie) {
      ladowanie = new Promise((rozwiaz, odrzuc) => {
        const skrypt = document.createElement('script');
        skrypt.src = korzen.dataset.echartsUrl;
        skrypt.onload = () => rozwiaz(window.echarts);
        skrypt.onerror = odrzuc;
        document.head.append(skrypt);
      });
    }
    return ladowanie;
  };

  const opcje = (typ, parametry) => {
    const dane = typ.dane(parametry);
    return {
      animation: !ruchOgraniczony,
      animationDuration: 250,
      title: {text: typ.tytul(parametry), left: 'center', textStyle: {fontSize: 13, fontWeight: 600, color: '#173752'}},
      grid: {left: 54, right: 18, top: 40, bottom: 40},
      tooltip: {trigger: 'axis', valueFormatter: v => Number(v).toPrecision(4)},
      legend: dane.serie.length > 1 ? {bottom: 0} : undefined,
      xAxis: {type: 'value', name: dane.osX || '', nameLocation: 'middle', nameGap: 26, scale: true, splitLine: {lineStyle: {color: KOLORY.siatka}}},
      yAxis: {type: 'value', name: dane.osY || '', splitLine: {lineStyle: {color: KOLORY.siatka}}},
      series: dane.serie.map((seria, indeks) => dane.ciagly ? {
        name: seria.nazwa, type: 'line', showSymbol: false, data: seria.punkty, smooth: false,
        lineStyle: {width: 2, type: seria.przerywana ? 'dashed' : 'solid', color: indeks ? KOLORY.drugi : KOLORY.glowny},
        areaStyle: seria.przerywana ? undefined : {opacity: 0.12, color: indeks ? KOLORY.drugi : KOLORY.glowny},
      } : {name: seria.nazwa, type: 'bar', data: seria.punkty, barMaxWidth: 14, itemStyle: {color: KOLORY.glowny}}),
    };
  };

  const zbudujWykres = async host => {
    const typ = TYPY[host.dataset.plot];
    if (!typ) return;
    let parametry = {};
    try { parametry = JSON.parse(host.dataset.params || '{}'); } catch (blad) { parametry = {}; }
    const pudelko = document.createElement('div');
    pudelko.className = 'ml-plot-box';
    const plotno = document.createElement('div');
    plotno.className = 'ml-plot-canvas';
    plotno.setAttribute('role', 'img');
    const sterowanie = document.createElement('div');
    sterowanie.className = 'ml-plot-controls';
    pudelko.append(plotno, sterowanie);
    host.replaceChildren(pudelko);
    const echarts = await zaladujECharts();
    const wykres = echarts.init(plotno, null, {renderer: 'svg'});
    const odswiez = () => {
      plotno.setAttribute('aria-label', `Wykres: ${typ.tytul(parametry)}`);
      wykres.setOption(opcje(typ, parametry), true);
    };
    Object.keys(parametry).forEach(nazwa => {
      const [min, max, krok] = (typ.suwaki && typ.suwaki[nazwa]) || SUWAKI[nazwa] || [0, 10, 0.1];
      const etykieta = document.createElement('label');
      const pole = document.createElement('input');
      Object.assign(pole, {type: 'range', min, max, step: krok, value: parametry[nazwa]});
      const wynik = document.createElement('output');
      wynik.value = parametry[nazwa];
      pole.addEventListener('input', () => {
        parametry[nazwa] = Number(pole.value);
        wynik.value = pole.value;
        odswiez();
      });
      etykieta.append(document.createTextNode(nazwa), pole, wynik);
      sterowanie.append(etykieta);
    });
    odswiez();
    window.addEventListener('resize', () => wykres.resize());
  };

  const spisTresci = () => {
    const linki = [...document.querySelectorAll('[data-ml-toc]')];
    if (!linki.length || !('IntersectionObserver' in window)) return;
    const mapa = new Map(linki.map(link => [link.dataset.mlToc, link]));
    const obserwator = new IntersectionObserver(wpisy => {
      wpisy.filter(wpis => wpis.isIntersecting).forEach(wpis => {
        linki.forEach(link => link.classList.remove('active'));
        mapa.get(wpis.target.id)?.classList.add('active');
      });
    }, {rootMargin: '0px 0px -70% 0px'});
    mapa.forEach((_, id) => {
      const cel = document.getElementById(id);
      if (cel) obserwator.observe(cel);
    });
  };

  const wyszukiwarka = () => {
    const pole = document.querySelector('[data-ml-search]');
    if (!pole) return;
    pole.addEventListener('input', () => {
      const fraza = pole.value.trim().toLowerCase();
      document.querySelectorAll('[data-ml-item]').forEach(element => {
        element.hidden = Boolean(fraza) && !element.dataset.mlItem.includes(fraza);
      });
      document.querySelectorAll('[data-ml-category]').forEach(dzial => {
        const widoczne = dzial.querySelectorAll('[data-ml-item]:not([hidden])').length;
        dzial.hidden = Boolean(fraza) && widoczne === 0;
      });
    });
  };

  const artykul = document.querySelector('[data-ml-article]');
  if (artykul) {
    numerujWzory(artykul);
    renderujWzory(artykul);
    artykul.querySelectorAll('.ml-plot[data-plot]').forEach(host => { zbudujWykres(host); });
    spisTresci();
    if (window.location.hash) document.getElementById(window.location.hash.slice(1))?.scrollIntoView();
  }
  renderujWzory(document.querySelector('.ml-main') || korzen);
  wyszukiwarka();
})();
