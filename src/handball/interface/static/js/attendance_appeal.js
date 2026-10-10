(() => {
  const korzen = document.querySelector('[data-maf]');
  if (!korzen) return;
  const panel = korzen.closest('[data-attendance-panel]') || korzen;
  const adresy = korzen.dataset;
  const ruchOgraniczony = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const KOLORY = {glowny: '#2b6ea4', drugi: '#3a7c67', akcent: '#9f6a15', ujemny: '#b04646', neutralny: '#64748b', siatka: '#e5eaf0', ciemny: '#10283f'};
  const PALETA = ['#2b6ea4', '#3a7c67', '#9f6a15', '#7a4f9a', '#b04646', '#1f8a9c'];
  const LIMIT_WIERSZY = 50;

  const stan = {
    model: null,
    dane: null,
    wykresy: new Map(),
    sortowanie: {pole: 'iaf', kierunek: -1},
    limit: LIMIT_WIERSZY,
    zaznaczone: new Set(),
    trendy: [],
    uruchomiono: false,
  };

  const element = selektor => korzen.querySelector(selektor);
  const html = tekst => String(tekst ?? '').replace(/[&<>"']/g, znak => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[znak]));
  const liczba = (wartosc, miejsca = 0) => {
    if (wartosc === null || wartosc === undefined || Number.isNaN(Number(wartosc))) return '—';
    return Number(wartosc).toLocaleString('pl-PL', {minimumFractionDigits: miejsca, maximumFractionDigits: miejsca}).replace(/ /g, ' ');
  };
  const procent = (wartosc, miejsca = 1) => (wartosc === null || wartosc === undefined ? '—' : `${liczba(100 * wartosc, miejsca)}%`);
  const zeZnakiem = (wartosc, miejsca = 1) => (wartosc === null || wartosc === undefined ? '—' : `${wartosc > 0 ? '+' : ''}${liczba(wartosc, miejsca)}`);
  const adres = (szablon, identyfikator) => szablon.replace(/\/0(?=\/?$|\?)/, `/${identyfikator}`);
  const zParametrami = (bazowy, parametry) => `${bazowy}?${new URLSearchParams(parametry).toString()}`;
  const wypelnienie = () => stan.dane?.model?.measure === 'fill';
  const data = tekst => (tekst ? new Date(tekst).toLocaleDateString('pl-PL') : '—');

  const pobierz = async url => {
    const odpowiedz = await fetch(url, {headers: {Accept: 'application/json'}});
    const tresc = await odpowiedz.json().catch(() => ({}));
    if (!odpowiedz.ok) throw new Error(tresc.blad || `Błąd ${odpowiedz.status}`);
    return tresc;
  };

  let ladowanieECharts = null;
  const echarts = () => {
    if (window.echarts) return Promise.resolve(window.echarts);
    if (!ladowanieECharts) {
      const url = korzen.closest('[data-echarts-url]')?.dataset.echartsUrl;
      ladowanieECharts = new Promise((rozwiaz, odrzuc) => {
        const skrypt = document.createElement('script');
        skrypt.src = url;
        skrypt.onload = () => rozwiaz(window.echarts);
        skrypt.onerror = odrzuc;
        document.head.append(skrypt);
      });
    }
    return ladowanieECharts;
  };

  const rysuj = async (nazwa, opcje) => {
    const host = korzen.querySelector(`[data-maf-chart="${nazwa}"]`);
    if (!host) return;
    const biblioteka = await echarts();
    let wykres = stan.wykresy.get(nazwa);
    if (!wykres) {
      wykres = biblioteka.init(host, null, {renderer: 'svg'});
      stan.wykresy.set(nazwa, wykres);
    }
    wykres.setOption({animation: !ruchOgraniczony, animationDuration: 300, ...opcje}, true);
  };
  window.addEventListener('resize', () => stan.wykresy.forEach(wykres => wykres.resize()));

  const katex = (wzor, wyswietlany = true) => {
    if (window.katex) {
      try { return window.katex.renderToString(wzor, {displayMode: wyswietlany, throwOnError: false}); } catch (blad) { return html(wzor); }
    }
    return `<code>${html(wzor)}</code>`;
  };

  const popover = korzen.parentElement.querySelector('[data-maf-popover]');
  const linkPojecia = klucz => {
    const metryka = stan.dane?.links?.metryki?.[klucz];
    if (!metryka) return null;
    return {...stan.dane.links.pojecia[metryka.pojecie], url: metryka.url};
  };
  const ikonaInfo = klucz => `<button type="button" class="maf-info" data-maf-info-button="${html(klucz)}" aria-label="Definicja matematyczna">i</button>`;
  const ustawIkony = (zakres = korzen) => {
    zakres.querySelectorAll('span[data-maf-info]').forEach(miejsce => {
      if (linkPojecia(miejsce.dataset.mafInfo)) miejsce.outerHTML = ikonaInfo(miejsce.dataset.mafInfo);
    });
  };
  const pokazPopover = (przycisk, przypnij) => {
    const pojecie = linkPojecia(przycisk.dataset.mafInfoButton);
    if (!pojecie || !popover) return;
    const kotwice = pojecie.kotwice || {};
    popover.innerHTML = `<b>${html(pojecie.nazwa)}</b><p>${html(pojecie.opis)}</p><nav>
      <a href="${html(kotwice.definicja || pojecie.url)}">Definicja</a>
      <a href="${html(kotwice.wzor || pojecie.url)}">Wzór</a>
      <a href="${html(kotwice.wyprowadzenie || pojecie.url)}">Wyprowadzenie</a>
      <a href="${html(kotwice.przyklad || pojecie.url)}">Przykład</a>
      <a href="${html(stan.dane.links.model)}">Pełna dokumentacja modelu</a></nav>`;
    popover.hidden = false;
    popover.dataset.przypiety = przypnij ? '1' : '';
    const prostokat = przycisk.getBoundingClientRect();
    const rodzic = popover.offsetParent?.getBoundingClientRect() || {left: 0, top: 0};
    popover.style.left = `${Math.max(8, prostokat.left - rodzic.left - 10)}px`;
    popover.style.top = `${prostokat.bottom - rodzic.top + 6}px`;
  };
  panel.addEventListener('mouseover', zdarzenie => {
    const przycisk = zdarzenie.target.closest('[data-maf-info-button]');
    if (przycisk && popover?.dataset.przypiety !== '1') pokazPopover(przycisk, false);
  });
  panel.addEventListener('mouseout', zdarzenie => {
    if (zdarzenie.target.closest('[data-maf-info-button]') && popover?.dataset.przypiety !== '1') popover.hidden = true;
  });
  panel.addEventListener('click', zdarzenie => {
    const przycisk = zdarzenie.target.closest('[data-maf-info-button]');
    if (przycisk) {
      zdarzenie.preventDefault();
      pokazPopover(przycisk, true);
      return;
    }
    if (popover && !zdarzenie.target.closest('[data-maf-popover]')) {
      popover.hidden = true;
      popover.dataset.przypiety = '';
    }
  });

  const status = () => {
    const model = stan.dane.model;
    const diagnostyka = stan.dane.diagnostics;
    const opis = {
      ok: 'Model przeszedł diagnostykę zbieżności (R-hat < 1,01, ESS ≥ 400, brak dywergencji).',
      ostrzezenie: 'Diagnostyka zgłasza ostrzeżenia — wyniki traktuj ostrożnie, zwłaszcza dla pojedynczych klubów.',
      niewiarygodny: 'Model NIE przeszedł podstawowej diagnostyki. Wyniki nie powinny być interpretowane jako wiarygodne.',
    }[model.status];
    element('[data-maf-status]').innerHTML = `<div class="maf-status ${html(model.status)}">
      <b>${html(model.label)}</b><span>${html(opis)}</span>
      <span class="maf-meta">Wersja ${html(model.version)} · trening ${data(model.trained_at)} · ${liczba(model.matches_used)} meczów · ${html(model.period.from || '')} – ${html(model.period.to || '')} · max R-hat ${liczba(diagnostyka.max_rhat, 3)} ${ikonaInfo('rhat')} · min ESS ${liczba(diagnostyka.min_ess_bulk)} ${ikonaInfo('ess')}</span></div>`;
  };

  const kpi = () => {
    const k = stan.dane.kpi;
    const najlepszyEfekt = k.best_effect;
    const pozycje = [
      ['Łączna frekwencja', liczba(k.total), 'Suma widzów w meczach użytych przez model', 'suma'],
      ['Średnia frekwencja', liczba(k.mean), `Średnia arytmetyczna; odchylenie standardowe ${liczba(k.sd)}`, 'srednia'],
      ['Mediana frekwencji', liczba(k.median), 'Połowa meczów miała mniej widzów', 'mediana'],
      ['Średnie wypełnienie hal', wypelnienie() ? procent(k.fill_mean) : 'n/d', wypelnienie() ? 'Średnia z A/C, tylko znana pojemność' : 'Model liczby widzów — bez fikcyjnego wypełnienia', 'wypelnienie'],
      ['Liczba spotkań', liczba(k.matches), `W tym ${liczba(k.reliable_clubs)} klubów z wiarygodnym IAF`, 'mecze'],
      ['Najwyższa frekwencja', liczba(k.top_match?.actual), k.top_match ? `${html(k.top_match.host)} – ${html(k.top_match.opponent)}, ${data(k.top_match.kickoff)}` : '', 'rekord'],
      ['Największy dodatni efekt rywala', najlepszyEfekt ? `${zeZnakiem(najlepszyEfekt.value, wypelnienie() ? 1 : 0)} ${html(najlepszyEfekt.unit)}` : '—', najlepszyEfekt ? html(najlepszyEfekt.name) : 'brak wiarygodnych oszacowań', 'efekt_pp'],
      ['Najwyższy indeks IAF', k.best_iaf ? liczba(k.best_iaf.value, 1) : '—', k.best_iaf ? `${html(k.best_iaf.name)} (mediana posterior)` : 'brak wiarygodnych oszacowań', 'iaf'],
    ];
    element('[data-maf-kpis]').innerHTML = pozycje.map(([etykieta, wartosc, opis, klucz]) => `<div class="maf-kpi">
      <div class="maf-kpi-label">${html(etykieta)} ${ikonaInfo(klucz)}</div>
      <div class="maf-kpi-value">${wartosc}</div><div class="maf-kpi-desc">${opis}</div></div>`).join('');
  };

  const klubyRywale = () => (stan.dane?.clubs || []).filter(klub => klub.away);
  const pobierzPole = (klub, pole) => {
    const w = klub.away;
    return {
      nazwa: klub.name.toLowerCase(), mecze: w.matches, srednia: w.mean, mediana: w.median,
      wypelnienie: w.fill_mean ?? -1, iaf: w.iaf.median, efekt: wypelnienie() ? (w.pp?.median ?? 0) : w.extra.median,
      p: w.p_gt_100, szerokosc: w.iaf.q975 - w.iaf.q025,
    }[pole];
  };

  const przefiltrowane = () => {
    const fraza = element('[data-maf-search]').value.trim().toLowerCase();
    const tylkoWiarygodne = element('[data-maf-reliable]').checked;
    const minimum = Number(element('[data-maf-min]').value);
    const {pole, kierunek} = stan.sortowanie;
    return klubyRywale()
      .filter(klub => !fraza || klub.name.toLowerCase().includes(fraza) || (klub.names_history || []).some(nazwa => nazwa.toLowerCase().includes(fraza)))
      .filter(klub => !tylkoWiarygodne || klub.away.reliable)
      .filter(klub => klub.away.matches >= minimum)
      .sort((a, b) => {
        const x = pobierzPole(a, pole);
        const y = pobierzPole(b, pole);
        return (x < y ? -1 : x > y ? 1 : 0) * kierunek;
      });
  };

  const pasekPrzedzialu = iaf => {
    const min = 50;
    const max = 170;
    const pozycja = wartosc => `${Math.max(0, Math.min(100, (wartosc - min) / (max - min) * 100))}%`;
    return `<span class="maf-ci" title="95%: ${liczba(iaf.q025, 1)} – ${liczba(iaf.q975, 1)}"><em style="left:${pozycja(100)}"></em><span style="left:${pozycja(iaf.q025)};width:calc(${pozycja(iaf.q975)} - ${pozycja(iaf.q025)})"></span><i style="left:${pozycja(iaf.median)}"></i></span>`;
  };

  const ranking = () => {
    const tabela = element('[data-maf-ranking]');
    const wiersze = przefiltrowane();
    const naglowki = [
      ['#', null], ['', null], ['Klub', 'nazwa'], ['Mecze (wyjazd)', 'mecze'], ['Średnia', 'srednia'], ['Mediana', 'mediana'],
      ['Wypełnienie', 'wypelnienie'], ['IAF', 'iaf'], [wypelnienie() ? 'Efekt p.p.' : 'Dodatkowi widzowie', 'efekt'],
      ['P(IAF > 100)', 'p'], ['Przedział 95%', 'szerokosc'], ['', null],
    ];
    const ikonyNaglowkow = {IAF: 'iaf', 'Efekt p.p.': 'efekt_pp', 'Dodatkowi widzowie': 'efekt_rywala', 'P(IAF > 100)': 'p_iaf', 'Przedział 95%': 'przedzial', 'Średnia': 'srednia', 'Mediana': 'mediana'};
    const glowa = naglowki.map(([tekst, pole]) => {
      const sort = pole ? ` data-sort="${pole}" aria-sort="${stan.sortowanie.pole === pole ? (stan.sortowanie.kierunek > 0 ? 'ascending' : 'descending') : 'none'}"` : '';
      const ikona = ikonyNaglowkow[tekst] ? ` ${ikonaInfo(ikonyNaglowkow[tekst])}` : '';
      return `<th scope="col" class="${pole && pole !== 'nazwa' ? 'num' : ''}"${sort}>${html(tekst)}${ikona}</th>`;
    }).join('');
    const tresc = wiersze.slice(0, stan.limit).map((klub, indeks) => {
      const w = klub.away;
      const efekt = wypelnienie() ? `${zeZnakiem(w.pp?.median, 1)}` : zeZnakiem(w.extra.median, 0);
      const ocena = w.reliable ? '' : ` <span class="maf-badge warn" title="${html(w.notes.join('; '))}">niepewne</span>`;
      return `<tr class="maf-row" data-klub="${klub.id}">
        <td class="num">${indeks + 1}</td>
        <td><input type="checkbox" aria-label="Zaznacz do porównania" data-maf-select="${klub.id}"${stan.zaznaczone.has(klub.id) ? ' checked' : ''}></td>
        <td><a href="${adres(adresy.urlDruzyna, klub.id)}">${html(klub.name)}</a>${ocena}</td>
        <td class="num">${liczba(w.matches)}</td><td class="num">${liczba(w.mean)}</td><td class="num">${liczba(w.median)}</td>
        <td class="num">${w.fill_mean === null || w.fill_mean === undefined ? 'n/d' : procent(w.fill_mean)}</td>
        <td class="num"><b>${liczba(w.iaf.median, 1)}</b></td>
        <td class="num ${(wypelnienie() ? w.pp?.median : w.extra.median) > 0 ? 'maf-up' : 'maf-down'}">${efekt}</td>
        <td class="num">${procent(w.p_gt_100, 1)}</td>
        <td class="num">${pasekPrzedzialu(w.iaf)}${liczba(w.iaf.q025, 1)} – ${liczba(w.iaf.q975, 1)}</td>
        <td><button type="button" class="btn secondary small" data-maf-trace="${klub.id}">Jak obliczono?</button></td></tr>`;
    }).join('');
    tabela.innerHTML = `<caption class="sr-only">Ranking klubów według IAF</caption><thead><tr>${glowa}</tr></thead><tbody>${tresc || '<tr><td colspan="12" class="note">Brak klubów dla filtrów.</td></tr>'}</tbody>`;
    element('[data-maf-more]').hidden = wiersze.length <= stan.limit;
    element('[data-maf-export]').href = zParametrami(adresy.urlEksport, {model: stan.model});
  };

  const szczegolyWiersza = wiersz => {
    const nastepny = wiersz.nextElementSibling;
    if (nastepny?.classList.contains('maf-detail')) { nastepny.remove(); return; }
    const klub = stan.dane.clubs.find(item => item.id === Number(wiersz.dataset.klub));
    const w = klub.away;
    const dom = klub.home;
    const sezony = (w.by_season || []).map(sezon => `<tr><td>${html(sezon.season)}</td><td class="num">${liczba(sezon.matches)}</td><td class="num">${liczba(sezon.median, 1)}</td><td class="num">${liczba(sezon.q025, 1)} – ${liczba(sezon.q975, 1)}</td></tr>`).join('');
    const szczegol = document.createElement('tr');
    szczegol.className = 'maf-detail';
    szczegol.innerHTML = `<td colspan="12"><div class="maf-two">
      <div><h5>Jako rywal (wyjazd)</h5><dl class="maf-kv">
        <dt>Mecze / różni gospodarze</dt><dd>${liczba(w.matches)} / ${liczba(w.hosts)}</dd>
        <dt>Sezony</dt><dd>${html((w.seasons || []).join(', '))}</dd>
        <dt>Efekt R<sub>j</sub> (skala ${wypelnienie() ? 'logit' : 'log'})</dt><dd>${liczba(w.effect.median, 3)} [${liczba(w.effect.q025, 3)}; ${liczba(w.effect.q975, 3)}]</dd>
        <dt>Dodatkowi widzowie (hala referencyjna)</dt><dd>${zeZnakiem(w.extra.median, 0)} [${zeZnakiem(w.extra.q025, 0)}; ${zeZnakiem(w.extra.q975, 0)}]</dd>
        <dt>R-hat / ESS</dt><dd>${liczba(w.rhat, 3)} / ${liczba(w.ess_bulk)}</dd>
        <dt>Uwagi</dt><dd>${w.notes.length ? html(w.notes.join('; ')) : 'oszacowanie wiarygodne'}</dd>
        ${klub.names_history?.length > 1 ? `<dt>Nazwy historyczne</dt><dd>${html(klub.names_history.join(' · '))}</dd>` : ''}
      </dl></div>
      <div><h5>Jako gospodarz (własna publiczność)</h5>${dom ? `<dl class="maf-kv">
        <dt>Mecze u siebie</dt><dd>${liczba(dom.matches)}</dd><dt>Średnia / mediana</dt><dd>${liczba(dom.mean)} / ${liczba(dom.median)}</dd>
        ${dom.fill_mean !== null && dom.fill_mean !== undefined ? `<dt>Średnie wypełnienie</dt><dd>${procent(dom.fill_mean)}</dd>` : ''}
        <dt>Indeks siły gospodarza</dt><dd>${liczba(dom.index.median, 1)} [${liczba(dom.index.q025, 1)}; ${liczba(dom.index.q975, 1)}]</dd>
      </dl>` : '<p class="note">Brak meczów u siebie w modelu.</p>'}
      ${sezony ? `<h5>IAF w sezonach</h5><table class="att-table"><thead><tr><th>Sezon</th><th class="num">Mecze</th><th class="num">IAF</th><th class="num">95%</th></tr></thead><tbody>${sezony}</tbody></table>` : ''}</div></div></td>`;
    wiersz.after(szczegol);
  };

  const porownaj = async () => {
    const [a, b] = [...stan.zaznaczone];
    const miejsce = element('[data-maf-compare-result]');
    try {
      const wynik = await pobierz(zParametrami(adresy.urlPorownanie, {model: stan.model, a, b}));
      const nazwa = id => stan.dane.clubs.find(klub => klub.id === id)?.name || id;
      miejsce.innerHTML = `<div class="maf-note-box">P(IAF<sub>${html(nazwa(a))}</sub> &gt; IAF<sub>${html(nazwa(b))}</sub> | dane) = <b>${procent(wynik.p_first_greater, 1)}</b> (± ${procent(wynik.mcse, 1)} błąd Monte Carlo) ${ikonaInfo('p_iaf')}.
        Różnica median ${zeZnakiem(wynik.difference.median, 1)} pkt, 95% przedział różnicy ${liczba(wynik.difference.q025, 1)} – ${liczba(wynik.difference.q975, 1)}.</div>`;
    } catch (blad) {
      miejsce.innerHTML = `<p class="att-warning">${html(blad.message)}</p>`;
    }
  };

  const odswiezPrzyciskPorownania = () => {
    const przycisk = element('[data-maf-compare]');
    przycisk.disabled = stan.zaznaczone.size !== 2;
    przycisk.textContent = `Porównaj zaznaczone (${stan.zaznaczone.size}/2)`;
  };

  const forest = () => {
    const sort = element('[data-maf-forest-sort]').value;
    const limit = Number(element('[data-maf-forest-limit]').value);
    const tylkoWiarygodne = element('[data-maf-forest-reliable]').checked;
    const porzadek = {
      iaf: (a, b) => b.away.iaf.median - a.away.iaf.median,
      waski: (a, b) => (a.away.iaf.q975 - a.away.iaf.q025) - (b.away.iaf.q975 - b.away.iaf.q025),
      szeroki: (a, b) => (b.away.iaf.q975 - b.away.iaf.q025) - (a.away.iaf.q975 - a.away.iaf.q025),
      mecze: (a, b) => b.away.matches - a.away.matches,
    }[sort];
    const wiarygodne = klubyRywale().filter(klub => klub.away.reliable);
    const zrodlo = tylkoWiarygodne && wiarygodne.length ? wiarygodne : klubyRywale();
    element('[data-maf-forest-note]').textContent = tylkoWiarygodne && !wiarygodne.length
      ? 'Brak oszacowań spełniających kryteria wiarygodności — pokazano wszystkie kluby.'
      : '';
    const kluby = zrodlo.sort(porzadek).slice(0, limit).reverse();
    const nazwy = kluby.map(klub => klub.name);
    rysuj('forest', {
      grid: {left: 210, right: 30, top: 20, bottom: 40},
      tooltip: {trigger: 'item', formatter: p => {
        const klub = kluby[p.dataIndex];
        if (!klub) return '';
        const w = klub.away;
        return `<b>${html(klub.name)}</b><br>IAF (mediana): ${liczba(w.iaf.median, 1)}<br>95%: ${liczba(w.iaf.q025, 1)} – ${liczba(w.iaf.q975, 1)}<br>P(IAF > 100): ${procent(w.p_gt_100)}<br>Mecze: ${w.matches}`;
      }},
      xAxis: {type: 'value', name: 'IAF', nameLocation: 'middle', nameGap: 26, scale: true, splitLine: {lineStyle: {color: KOLORY.siatka}}},
      yAxis: {type: 'category', data: nazwy, axisLabel: {fontSize: 11, width: 200, overflow: 'truncate'}},
      series: [
        {type: 'custom', name: '95% przedział', renderItem: (parametry, api) => {
          const y = api.coord([0, api.value(0)])[1];
          const od = api.coord([api.value(1), api.value(0)])[0];
          const doo = api.coord([api.value(2), api.value(0)])[0];
          return {type: 'group', children: [
            {type: 'line', shape: {x1: od, y1: y, x2: doo, y2: y}, style: {stroke: KOLORY.glowny, lineWidth: 2}},
            {type: 'line', shape: {x1: od, y1: y - 4, x2: od, y2: y + 4}, style: {stroke: KOLORY.glowny, lineWidth: 1.5}},
            {type: 'line', shape: {x1: doo, y1: y - 4, x2: doo, y2: y + 4}, style: {stroke: KOLORY.glowny, lineWidth: 1.5}},
          ]};
        }, encode: {x: [1, 2], y: 0}, data: kluby.map((klub, i) => [i, klub.away.iaf.q025, klub.away.iaf.q975]), z: 1},
        {type: 'scatter', name: 'mediana', symbolSize: 9, itemStyle: {color: KOLORY.ciemny}, data: kluby.map((klub, i) => [klub.away.iaf.median, i]), encode: {x: 0, y: 1},
          markLine: {silent: true, symbol: 'none', lineStyle: {color: KOLORY.ujemny, type: 'dashed'}, label: {formatter: 'IAF = 100'}, data: [{xAxis: 100}]}},
      ],
    });
  };

  const opcjeKlubow = (lista, wybrany) => lista.map(klub => `<option value="${klub.id}"${klub.id === wybrany ? ' selected' : ''}>${html(klub.name)}</option>`).join('');

  const trendy = () => {
    const kluby = stan.trendy.map(id => stan.dane.clubs.find(klub => klub.id === id)).filter(Boolean);
    element('[data-maf-trend-chips]').innerHTML = `<span class="maf-chips">${kluby.map(klub => `<span class="maf-chip">${html(klub.name)} <button type="button" data-maf-trend-remove="${klub.id}" aria-label="Usuń">×</button></span>`).join('')}</span>`;
    const sezony = stan.dane.model.seasons;
    const serie = [];
    kluby.forEach((klub, indeks) => {
      const kolor = PALETA[indeks % PALETA.length];
      const mapa = new Map((klub.away.by_season || []).map(sezon => [sezon.season, sezon]));
      const dolne = sezony.map(s => mapa.get(s)?.q10 ?? null);
      const gorne = sezony.map(s => (mapa.has(s) ? mapa.get(s).q90 - mapa.get(s).q10 : null));
      serie.push({type: 'line', stack: `pasmo${indeks}`, data: dolne, lineStyle: {opacity: 0}, symbol: 'none', silent: true, tooltip: {show: false}});
      serie.push({type: 'line', stack: `pasmo${indeks}`, data: gorne, lineStyle: {opacity: 0}, symbol: 'none', areaStyle: {color: kolor, opacity: 0.14}, silent: true, tooltip: {show: false}});
      serie.push({type: 'line', name: klub.name, data: sezony.map(s => mapa.get(s)?.median ?? null), connectNulls: false, itemStyle: {color: kolor}, lineStyle: {width: 2, color: kolor}, symbol: ['circle', 'rect', 'triangle', 'diamond'][indeks % 4], symbolSize: 7});
    });
    rysuj('trend', {
      grid: {left: 50, right: 20, top: 30, bottom: 50},
      legend: {top: 0, data: kluby.map(klub => klub.name)},
      tooltip: {trigger: 'axis', valueFormatter: v => liczba(v, 1)},
      xAxis: {type: 'category', data: sezony, axisLabel: {rotate: sezony.length > 10 ? 35 : 0}},
      yAxis: {type: 'value', name: 'IAF', scale: true, splitLine: {lineStyle: {color: KOLORY.siatka}}},
      series: serie.length ? [...serie, {type: 'line', data: [], markLine: {silent: true, symbol: 'none', lineStyle: {color: KOLORY.ujemny, type: 'dashed'}, data: [{yAxis: 100}]}}] : [],
    });
    element('[data-maf-trend-table]').innerHTML = kluby.length ? `<thead><tr><th>Klub</th>${sezony.map(s => `<th class="num">${html(s)}</th>`).join('')}</tr></thead><tbody>${kluby.map(klub => {
      const mapa = new Map((klub.away.by_season || []).map(sezon => [sezon.season, sezon]));
      return `<tr><th scope="row">${html(klub.name)}</th>${sezony.map(s => `<td class="num">${mapa.has(s) ? `${liczba(mapa.get(s).median, 1)}<br><small>${liczba(mapa.get(s).q025, 0)}–${liczba(mapa.get(s).q975, 0)}</small>` : '—'}</td>`).join('')}</tr>`;
    }).join('')}</tbody>` : '';
  };

  const posterior = async () => {
    const id = Number(element('[data-maf-posterior-select]').value);
    if (!id) return;
    try {
      const wynik = await pobierz(zParametrami(adres(adresy.urlKlub, id), {model: stan.model}));
      const w = wynik.club.away;
      const krawedzie = w.histogram.edges;
      const srodki = w.histogram.counts.map((_, i) => (krawedzie[i] + krawedzie[i + 1]) / 2);
      const suma = w.histogram.counts.reduce((a, b) => a + b, 0) || 1;
      element('[data-maf-posterior-summary]').innerHTML = `mediana ${liczba(w.iaf.median, 1)}, 95% ${liczba(w.iaf.q025, 1)} – ${liczba(w.iaf.q975, 1)}, <b>P(IAF &gt; 100) = ${procent(w.p_gt_100, 1)}</b>`;
      rysuj('posterior', {
        grid: {left: 50, right: 20, top: 20, bottom: 40},
        tooltip: {trigger: 'axis', formatter: p => `IAF ≈ ${liczba(srodki[p[0].dataIndex], 1)}<br>udział próbek: ${procent(w.histogram.counts[p[0].dataIndex] / suma, 1)}`},
        xAxis: {type: 'category', data: srodki.map(v => liczba(v, 1)), name: 'IAF', nameLocation: 'middle', nameGap: 26},
        yAxis: {type: 'value', name: 'gęstość (udział próbek)', splitLine: {lineStyle: {color: KOLORY.siatka}}},
        series: [{type: 'bar', barCategoryGap: '4%', data: w.histogram.counts.map((liczbaPrb, i) => ({value: liczbaPrb / suma, itemStyle: {color: srodki[i] > 100 ? KOLORY.drugi : '#b7c6d4'}}))}],
      });
    } catch (blad) {
      element('[data-maf-posterior-summary]').textContent = blad.message;
    }
  };

  const gospodarz = async () => {
    const id = Number(element('[data-maf-host-select]').value);
    const miejsce = element('[data-maf-host]');
    if (!id) return;
    miejsce.innerHTML = '<p class="note">Obliczanie…</p>';
    try {
      const wynik = await pobierz(zParametrami(adres(adresy.urlGospodarz, id), {model: stan.model}));
      const tabela = (wiersze, tytul) => `<div><h4>${tytul}</h4><table class="att-table"><thead><tr><th>Rywal</th><th class="num">Wizyty</th><th class="num">Indeks u gospodarza</th><th class="num">95%</th><th class="num">P(&gt; 100)</th><th class="num">Δ widzów</th></tr></thead><tbody>${wiersze.map(w => `<tr><td>${html(w.name)}</td><td class="num">${w.visits}</td><td class="num"><b>${liczba(w.index.median, 1)}</b></td><td class="num">${liczba(w.index.q025, 1)} – ${liczba(w.index.q975, 1)}</td><td class="num">${procent(w.p_gt_100)}</td><td class="num">${zeZnakiem(w.extra.median, 0)}</td></tr>`).join('') || '<tr><td colspan="6" class="note">Brak danych</td></tr>'}</tbody></table></div>`;
      miejsce.innerHTML = `<p class="note">Oczekiwana frekwencja u ${html(wynik.host)} z typowym rywalem: <b>${liczba(wynik.reference_expected.median)}</b> widzów (95%: ${liczba(wynik.reference_expected.q025)} – ${liczba(wynik.reference_expected.q975)})${wynik.capacity ? `, hala ~${liczba(wynik.capacity)} miejsc` : ''}. Średnia własna u siebie (dane): ${liczba(wynik.home_mean)}. Analiza obejmuje ${wynik.opponents_total} rywali, którzy grali u tego gospodarza.</p>
        ${wynik.uniform_ratio ? '<p class="maf-note-box">W modelu liczby widzów (łącze log) efekt rywala jest multiplikatywny i taki sam względem każdego gospodarza — różni się jedynie liczba widzów (Δ).</p>' : '<p class="note">W modelu wypełnienia (łącze logit) ten sam rywal zwiększa wypełnienie różnie u różnych gospodarzy — efekt słabnie, gdy hala jest bliska kompletu.</p>'}
        <div class="maf-two">${tabela(wynik.top, 'Najbardziej zwiększają zainteresowanie')}${tabela(wynik.bottom, 'Najsłabiej przyciągają')}</div>`;
    } catch (blad) {
      miejsce.innerHTML = `<p class="att-warning">${html(blad.message)}</p>`;
    }
  };

  const symulatorPrzygotuj = () => {
    const kluby = [...stan.dane.clubs].sort((a, b) => a.name.localeCompare(b.name, 'pl'));
    const gospodarze = kluby.filter(klub => klub.home);
    const rywale = kluby.filter(klub => klub.away);
    element('[data-maf-sim-host]').innerHTML = opcjeKlubow(gospodarze);
    element('[data-maf-sim-opponent]').innerHTML = opcjeKlubow(rywale);
    element('[data-maf-sim-competition]').innerHTML = `<option value="">nowe / nieznane</option>${stan.dane.competitions.map(r => `<option value="${html(r.key)}">${html(r.name)} (${r.matches})</option>`).join('')}`;
    const sezony = stan.dane.model.seasons;
    element('[data-maf-sim-season]').innerHTML = `<option value="">kolejny sezon (nowy)</option>${[...sezony].reverse().map((s, i) => `<option value="${html(s)}"${i === 0 ? ' selected' : ''}>${html(s)}</option>`).join('')}`;
    element('[data-maf-sim-venue]').innerHTML = `<option value="">— wpisz pojemność —</option>${stan.dane.venues.filter(h => h.capacity).map(h => `<option value="${h.id}" data-capacity="${h.capacity}" data-host="${h.main_host}">${html(h.name)} (${liczba(h.capacity)})</option>`).join('')}`;
    const ustawHale = () => {
      const id = Number(element('[data-maf-sim-host]').value);
      const hala = [...element('[data-maf-sim-venue]').options].find(opcja => Number(opcja.dataset.host) === id);
      if (hala) {
        element('[data-maf-sim-venue]').value = hala.value;
        element('[data-maf-sim-capacity]').value = hala.dataset.capacity;
      } else {
        const host = stan.dane.hosts.find(h => h.id === id);
        element('[data-maf-sim-capacity]').value = host?.capacity ? Math.round(host.capacity) : '';
      }
      const rozgrywki = stan.dane.competitions[0];
      if (rozgrywki && !element('[data-maf-sim-competition]').value) element('[data-maf-sim-competition]').value = rozgrywki.key;
    };
    element('[data-maf-sim-host]').onchange = ustawHale;
    element('[data-maf-sim-venue]').onchange = () => {
      const opcja = element('[data-maf-sim-venue]').selectedOptions[0];
      if (opcja?.dataset.capacity) element('[data-maf-sim-capacity]').value = opcja.dataset.capacity;
    };
    const rywal = element('[data-maf-sim-opponent]');
    if (rywal.value === element('[data-maf-sim-host]').value && rywal.options.length > 1) {
      rywal.selectedIndex = rywal.selectedIndex === 0 ? 1 : 0;
    }
    ustawHale();
    element('[data-maf-sim-capacity]').required = wypelnienie();
  };

  const symuluj = async formularz => {
    const parametry = Object.fromEntries(new FormData(formularz).entries());
    parametry.model = stan.model;
    Object.keys(parametry).forEach(klucz => { if (parametry[klucz] === '') delete parametry[klucz]; });
    const miejsce = element('[data-maf-sim-result]');
    miejsce.innerHTML = '<p class="note">Symulacja Monte Carlo…</p>';
    try {
      const w = await pobierz(zParametrami(adresy.urlPrognoza, parametry));
      const przedzialy = Object.entries(w.intervals).map(([poziom, [od, doo]]) => `<tr><td>${poziom}%</td><td class="num">${liczba(od)} – ${liczba(doo)}</td>${w.capacity ? `<td class="num">${procent(Math.min(od / w.capacity, 1), 0)} – ${procent(Math.min(doo / w.capacity, 1), 0)}</td>` : ''}</tr>`).join('');
      const progi = w.fill_probabilities ? Object.entries(w.fill_probabilities).map(([poziom, p]) => `<tr><td>wypełnienie ≥ ${poziom}%</td><td class="num"><b>${procent(p, 1)}</b></td></tr>`).join('') : '';
      miejsce.innerHTML = `<div class="maf-sim-grid"><div>
        <dl class="maf-kv">
          <dt>Oczekiwana liczba widzów ${ikonaInfo('wartosc_oczekiwana_prognozy')}</dt><dd>${liczba(w.expected)}</dd>
          <dt>Mediana prognozy</dt><dd>${liczba(w.median)}</dd>
          ${w.fill_expected !== undefined ? `<dt>Prognozowane wypełnienie</dt><dd>${procent(w.fill_expected, 1)} (hala ${liczba(w.capacity)} miejsc)</dd>` : ''}
          <dt>Przedział wiarygodności <i>średniej</i> (tylko niepewność parametrów) ${ikonaInfo('przedzial')}</dt><dd>${liczba(w.mean_parameter.q025)} – ${liczba(w.mean_parameter.q975)}</dd>
          ${w.p_threshold !== undefined ? `<dt>P(widzów ≥ ${liczba(w.threshold)})</dt><dd>${procent(w.p_threshold, 1)}</dd>` : ''}
        </dl>
        <h4>Przedziały predykcyjne ${ikonaInfo('przedzial_predykcyjny')}</h4>
        <table class="att-table"><thead><tr><th>Poziom</th><th class="num">Widzowie</th>${w.capacity ? '<th class="num">Wypełnienie</th>' : ''}</tr></thead><tbody>${przedzialy}</tbody></table>
        ${progi ? `<h4>Prawdopodobieństwo zapełnienia hali</h4><table class="att-table"><tbody>${progi}</tbody></table>` : ''}
        <p class="note">${w.draws} próbek posterior × ${w.samples / w.draws} losowań meczu = ${liczba(w.samples)} symulacji. ${w.notes.map(html).join(' · ')}</p>
      </div><div class="att-chart" data-maf-chart="symulacja" role="img" aria-label="Rozkład predykcyjny liczby widzów; zaznaczone przedziały i pojemność hali."></div></div>`;
      const krawedzie = w.histogram.edges;
      const srodki = w.histogram.probabilities.map((_, i) => (krawedzie[i] + krawedzie[i + 1]) / 2);
      const [od95, do95] = w.intervals['95'];
      stan.wykresy.get('symulacja')?.dispose();
      stan.wykresy.delete('symulacja');
      rysuj('symulacja', {
        grid: {left: 54, right: 20, top: 24, bottom: 44},
        tooltip: {trigger: 'axis', formatter: p => `${liczba(krawedzie[p[0].dataIndex])} – ${liczba(krawedzie[p[0].dataIndex + 1])} widzów<br>prawdopodobieństwo: ${procent(w.histogram.probabilities[p[0].dataIndex], 1)}`},
        xAxis: {type: 'category', data: srodki.map(v => liczba(v)), name: 'Widzowie', nameLocation: 'middle', nameGap: 28},
        yAxis: {type: 'value', name: 'P', axisLabel: {formatter: v => procent(v, 0)}, splitLine: {lineStyle: {color: KOLORY.siatka}}},
        series: [{type: 'bar', barCategoryGap: '3%', data: w.histogram.probabilities.map((p, i) => ({value: p, itemStyle: {color: srodki[i] >= od95 && srodki[i] <= do95 ? KOLORY.glowny : '#c3d0dc'}}))}],
      });
      ustawIkony(miejsce);
    } catch (blad) {
      miejsce.innerHTML = `<p class="att-warning">${html(blad.message)}</p>`;
    }
  };

  const tabelaMeczow = (wiersze, rekordy = false) => `<thead><tr><th>Data</th>${rekordy ? '<th>Sezon</th>' : ''}<th>Mecz</th><th class="num">Widzowie</th><th class="num">Oczekiwane</th><th class="num">Różnica</th><th class="num">%</th>${wypelnienie() ? '<th class="num">p.p.</th>' : ''}<th class="num">z</th><th class="num">p</th></tr></thead><tbody>${wiersze.map(m => `<tr>
    <td><a href="${adres(adresy.urlMecz, m.match_id)}">${data(m.kickoff)}</a></td>${rekordy ? `<td>${html(m.season)}</td>` : ''}
    <td>${html(m.host)} – ${html(m.opponent)}<br><small class="note">${html(m.competition)}</small></td>
    <td class="num"><b>${liczba(m.actual)}</b></td><td class="num">${liczba(m.expected)}<br><small class="note">90%: ${liczba(m.interval90[0])}–${liczba(m.interval90[1])}</small></td>
    <td class="num ${m.difference > 0 ? 'maf-up' : 'maf-down'}">${zeZnakiem(m.difference, 0)}</td><td class="num">${zeZnakiem(m.difference_pct, 0)}</td>
    ${wypelnienie() ? `<td class="num">${zeZnakiem(m.difference_pp, 1)}</td>` : ''}<td class="num">${liczba(m.z, 2)}</td><td class="num">${m.p_value < 0.001 ? '&lt;0,001' : liczba(m.p_value, 3)}</td></tr>`).join('')}</tbody>`;

  const odchylenia = () => {
    const niespodzianki = stan.dane.surprises;
    element('[data-maf-surprises="positive"]').innerHTML = tabelaMeczow(niespodzianki.positive.slice(0, 20));
    element('[data-maf-surprises="negative"]').innerHTML = tabelaMeczow(niespodzianki.negative.slice(0, 20));
    const rekordy = stan.dane.records;
    element('[data-maf-records="season"]').innerHTML = tabelaMeczow(rekordy.season, true);
    element('[data-maf-records="club"]').innerHTML = tabelaMeczow(rekordy.club.slice(0, 20), true);
    element('[data-maf-records="venue"]').innerHTML = tabelaMeczow(rekordy.venue.slice(0, 20), true);
    const mapa = stan.dane.heatmap;
    rysuj('heatmap', {
      grid: {left: 200, right: 30, top: 10, bottom: 110},
      tooltip: {formatter: p => `${html(mapa.hosts[p.value[1]])}, ${html(mapa.seasons[p.value[0]])}<br>średnie z = ${liczba(p.value[2], 2)} (${p.value[3]} meczów)`},
      xAxis: {type: 'category', data: mapa.seasons, axisLabel: {rotate: 35}},
      yAxis: {type: 'category', data: mapa.hosts, axisLabel: {fontSize: 11, width: 190, overflow: 'truncate'}},
      visualMap: {dimension: 2, min: -2, max: 2, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, inRange: {color: ['#b04646', '#f4f6f8', '#2b6ea4']}, text: ['powyżej oczekiwań', 'poniżej']},
      series: [{type: 'heatmap', data: mapa.values, label: {show: false}}],
    });
  };

  const diagnostyka = () => {
    const d = stan.dane.diagnostics;
    const b = stan.dane.backtest;
    const m = stan.dane.model;
    const wspolczynniki = stan.dane.coefficients.map(c => `<tr><td>${html(c.label)}</td><td class="num">${liczba(c.coefficient.median, 3)}</td><td class="num">${liczba(c.coefficient.q025, 3)} – ${liczba(c.coefficient.q975, 3)}</td><td class="num">${procent(c.p_positive, 0)}</td><td class="num">${zeZnakiem(c.effect.median, 2)} ${html(c.effect_unit)}</td><td class="num">${liczba(c.rhat, 3)}</td><td class="num">${liczba(c.ess_bulk)}</td></tr>`).join('');
    const grupy = m.groups.map(g => `<tr><td>${html(g.label)}</td><td class="num">${liczba(g.levels)}</td><td>${{fixed: 'efekt stały, N(0, 1)', centered: 'losowy, parametryzacja centrowana', noncentered: 'losowy, niecentrowana'}[g.mode]}</td><td class="num">${g.sigma ? `${liczba(g.sigma.median, 3)} [${liczba(g.sigma.q025, 3)}; ${liczba(g.sigma.q975, 3)}]` : '—'}</td></tr>`).join('');
    const nazwaParametru = nazwa => {
      const indeks = /^beta\[(\d+)\]$/.exec(nazwa);
      return indeks ? `β: ${m.features.labels[Number(indeks[1])] || nazwa}` : nazwa;
    };
    const kluczowe = d.key_parameters.map(p => `<tr><td><code>${html(nazwaParametru(p.name))}</code></td><td class="num">${liczba(p.mean, 3)}</td><td class="num">${liczba(p.sd, 3)}</td><td class="num">${liczba(p.rhat, 3)}</td><td class="num">${liczba(p.ess_bulk)}</td><td class="num">${liczba(p.ess_tail)}</td></tr>`).join('');
    const pokrycie = b.available ? Object.values(b.coverage).map(c => `<tr><td>${procent(c.nominal, 0)}</td><td class="num"><b>${procent(c.observed, 1)}</b></td><td class="num">${liczba(c.mean_width)}</td></tr>`).join('') : '';
    const ppc = stan.dane.ppc.checks.map(c => `<tr><td>${html(c.statistic)}</td><td class="num">${liczba(c.observed, 3)}</td><td class="num">${liczba(c.replicated_q05, 3)} – ${liczba(c.replicated_q95, 3)}</td><td class="num">${liczba(c.p_value, 2)}</td></tr>`).join('');
    element('[data-maf-diagnostics]').innerHTML = `<div class="maf-two"><div>
      <h4>Zbieżność MCMC (NUTS) ${ikonaInfo('mcmc')}</h4><dl class="maf-kv">
        <dt>Status</dt><dd>${html(d.status)}</dd><dt>Łańcuchy × próbki</dt><dd>${d.chains} × ${d.draws_per_chain} (rozgrzewka ${m.sampler.warmup})</dd>
        <dt>Maks. R-hat ${ikonaInfo('rhat')}</dt><dd>${liczba(d.max_rhat, 4)} (próg ${liczba(d.thresholds.rhat, 2)}; ${procent(d.share_rhat_ok, 1)} parametrów &lt; 1,01)</dd>
        <dt>Min. ESS bulk / tail ${ikonaInfo('ess')}</dt><dd>${liczba(d.min_ess_bulk)} / ${liczba(d.min_ess_tail)} (próg ${liczba(d.thresholds.ess)})</dd>
        <dt>Dywergencje</dt><dd>${d.divergences}</dd><dt>E-BFMI</dt><dd>${d.ebfmi.map(v => liczba(v, 2)).join(' · ')}</dd>
        <dt>Rozmiar kroku</dt><dd>${d.step_sizes.map(v => liczba(v, 3)).join(' · ')}</dd><dt>Ziarno losowe</dt><dd>${m.sampler.seed}</dd>
        <dt>Odcisk danych (SHA-256)</dt><dd><code>${html(m.data_fingerprint.slice(0, 16))}…</code></dd>
      </dl></div><div>
      <h4>Walidacja chronologiczna ${ikonaInfo('backtest')}</h4>${b.available ? `<dl class="maf-kv">
        <dt>Trening → test</dt><dd>${html(b.train_seasons[0])}–${html(b.train_seasons[b.train_seasons.length - 1])} → ${html(b.test_seasons.join(', '))}</dd>
        <dt>Mecze trening / test</dt><dd>${liczba(b.train_matches)} / ${liczba(b.test_matches)}</dd>
        <dt>MAE ${ikonaInfo('mae')}</dt><dd>${liczba(b.mae)} widzów (punkt odniesienia: ${liczba(b.baseline_mae)})</dd>
        <dt>RMSE ${ikonaInfo('rmse')}</dt><dd>${liczba(b.rmse)} (punkt odniesienia: ${liczba(b.baseline_rmse)})</dd>
        ${b.mae_fill_pp !== undefined ? `<dt>MAE wypełnienia</dt><dd>${liczba(b.mae_fill_pp, 1)} p.p.</dd>` : ''}
        <dt>CRPS</dt><dd>${liczba(b.crps, 1)}</dd><dt>Diagnostyka modelu treningowego</dt><dd>${html(b.diagnostics_status)}</dd>
      </dl><p class="note">Punkt odniesienia: ${html(b.baseline_label)}.</p>
      <h5>Pokrycie przedziałów predykcyjnych ${ikonaInfo('pokrycie')}</h5><table class="att-table"><thead><tr><th>Nominalne</th><th class="num">Obserwowane</th><th class="num">Śr. szerokość</th></tr></thead><tbody>${pokrycie}</tbody></table>` : `<p class="note">${html(b.reason || 'brak')}</p>`}</div></div>
      <h4>Współczynniki warunków meczu ${ikonaInfo('wspolczynniki')}</h4>
      <p class="note">Kowariaty ciągłe są standaryzowane ${ikonaInfo('standaryzacja')} (współczynnik = zmiana o 1 odchylenie standardowe). Efekt pokazany na skali wyniku dla populacji referencyjnej. Forma = średnia punktów z 5 poprzednich meczów ${ikonaInfo('forma')}. Korelacja nie oznacza przyczynowości.</p>
      <div class="table-wrap att-table-wrap"><table class="att-table"><thead><tr><th>Czynnik</th><th class="num">β (mediana)</th><th class="num">95%</th><th class="num">P(β &gt; 0)</th><th class="num">Efekt</th><th class="num">R-hat</th><th class="num">ESS</th></tr></thead><tbody>${wspolczynniki}</tbody></table></div>
      <div class="maf-two"><div><h4>Struktura hierarchiczna ${ikonaInfo('hierarchia')}</h4><table class="att-table"><thead><tr><th>Efekt</th><th class="num">Poziomy</th><th>Typ ${ikonaInfo('efekty_losowe')}</th><th class="num">σ ${ikonaInfo('hiperprior')}</th></tr></thead><tbody>${grupy}</tbody></table>
      <p class="note">Efekty mają ograniczenie sumy zerowej ${ikonaInfo('identyfikowalnosc')} (globalnie dla H, R, S, L; w obrębie klubu dla HS i RS), dlatego IAF = 100 to przeciętny rywal w populacji.</p></div>
      <div><h4>Parametry globalne</h4><table class="att-table"><thead><tr><th>Parametr</th><th class="num">Średnia</th><th class="num">SD</th><th class="num">R-hat</th><th class="num">ESS bulk</th><th class="num">ESS tail</th></tr></thead><tbody>${kluczowe}</tbody></table>
      <h5>Statystyki PPC</h5><table class="att-table"><thead><tr><th>Statystyka</th><th class="num">Obserwowana</th><th class="num">Replikacje 90%</th><th class="num">p</th></tr></thead><tbody>${ppc}</tbody></table></div></div>`;
    const p = stan.dane.ppc;
    const srodki = p.observed.map((_, i) => (p.edges[i] + p.edges[i + 1]) / 2);
    const etykieta = v => (p.scale === 'wypełnienie hali' ? procent(v, 0) : liczba(10 ** v));
    rysuj('ppc', {
      grid: {left: 50, right: 16, top: 44, bottom: 44}, legend: {top: 0, data: ['90% danych replikowanych', 'obserwowane']},
      tooltip: {trigger: 'axis'},
      xAxis: {type: 'category', data: srodki.map(etykieta), name: p.scale, nameLocation: 'middle', nameGap: 28},
      yAxis: {type: 'value', name: 'mecze', splitLine: {lineStyle: {color: KOLORY.siatka}}},
      series: [
        {name: 'dolna granica', type: 'line', stack: 'pasmo', silent: true, tooltip: {show: false}, data: p.replicated_q05, lineStyle: {opacity: 0}, symbol: 'none'},
        {name: '90% danych replikowanych', type: 'line', stack: 'pasmo', data: p.replicated_q95.map((v, i) => v - p.replicated_q05[i]), lineStyle: {opacity: 0}, symbol: 'none', areaStyle: {color: KOLORY.glowny, opacity: 0.18}},
        {name: 'obserwowane', type: 'bar', data: p.observed, itemStyle: {color: 'rgba(16,40,63,0.55)'}, barCategoryGap: '20%'},
      ],
    });
    if (b.available) {
      const oczekiwane = b.pit_histogram.reduce((a, c) => a + c, 0) / b.pit_histogram.length;
      rysuj('pit', {
        grid: {left: 50, right: 16, top: 20, bottom: 40},
        tooltip: {trigger: 'axis'},
        xAxis: {type: 'category', data: b.pit_histogram.map((_, i) => `${i / 10}–${(i + 1) / 10}`), name: 'PIT', nameLocation: 'middle', nameGap: 26},
        yAxis: {type: 'value', name: 'mecze', splitLine: {lineStyle: {color: KOLORY.siatka}}},
        series: [{type: 'bar', data: b.pit_histogram, itemStyle: {color: KOLORY.drugi}, markLine: {silent: true, symbol: 'none', lineStyle: {type: 'dashed', color: KOLORY.ciemny}, label: {formatter: 'idealna kalibracja', position: 'insideEndTop'}, data: [{yAxis: oczekiwane}]}}],
      });
    }
  };

  const jakosc = () => {
    const q = stan.dane.quality;
    const pozycje = [
      ['Rekordy wejściowe', q.total_records], ['Usunięte duplikaty', q.duplicates_removed], ['Brak frekwencji (NULL ≠ 0)', q.attendance_unknown],
      ['Zero widzów (bez publiczności)', q.attendance_zero], ['Teren neutralny', q.neutral_matches], ['Nieznana pojemność', q.capacity_unknown],
      ['Widzów więcej niż miejsc', q.capacity_exceeded], ['Wartości podejrzane', q.suspicious_values], ['Wartości odstające (oznaczone, w modelu)', q.outliers_flagged],
      ['Mecze w modelu liczby widzów', q.usable_count], ['Mecze w modelu wypełnienia', q.usable_fill],
    ];
    const etykiety = q.issue_labels;
    const przyklady = q.issues.slice(0, 40).map(i => `<tr><td><a href="${adres(adresy.urlMecz, i.match_id)}">${i.match_id}</a></td><td>${html(etykiety[i.code] || i.code)}</td></tr>`).join('');
    element('[data-maf-quality]').innerHTML = `<div class="maf-two"><dl class="maf-kv">${pozycje.map(([e, v]) => `<dt>${html(e)}</dt><dd>${liczba(v)}</dd>`).join('')}</dl>
      <div><p class="note">Pojemność hali w bazie jest nominalna i stała w czasie; dostępną pojemność meczu można nadpisać plikiem korekt (CapacityOverride). Mecze z pojemnością niespójną z frekwencją nie trafiają do modelu wypełnienia, ale pozostają w modelu liczby widzów. Wypełnienia nie wylicza się, gdy pojemność jest nieznana.</p>
      <h5>Przykładowe zgłoszenia</h5><table class="att-table"><thead><tr><th>Mecz</th><th>Problem</th></tr></thead><tbody>${przyklady || '<tr><td colspan="2">brak</td></tr>'}</tbody></table></div></div>`;
  };

  const slad = async id => {
    const dialog = korzen.parentElement.querySelector('[data-maf-dialog]');
    const cialo = dialog.querySelector('[data-maf-dialog-body]');
    cialo.innerHTML = '<p class="note">Wczytywanie…</p>';
    dialog.showModal();
    try {
      const wynik = await pobierz(zParametrami(adres(adresy.urlKlub, id), {model: stan.model}));
      const k = wynik.club;
      const w = k.away;
      const m = wynik.model;
      const ref = m.reference;
      const sigmaR = m.groups.find(g => g.name === 'opponent')?.sigma;
      const probki = m.sampler.chains * Math.floor(m.sampler.draws / m.sampler.thin_store);
      const wzor = m.measure === 'fill'
        ? String.raw`\mathrm{IAF}_j = 100\cdot\frac{\frac{1}{|X_{ref}|}\sum_{i\in X_{ref}} \operatorname{logit}^{-1}\!\big(\eta_i^{(0)} + R_j\big)}{\frac{1}{|X_{ref}|}\sum_{i\in X_{ref}} \operatorname{logit}^{-1}\!\big(\eta_i^{(0)}\big)}`
        : String.raw`\mathrm{IAF}_j = 100\cdot\frac{\frac{1}{|X_{ref}|}\sum_{i} e^{\eta_i^{(0)} + R_j}}{\frac{1}{|X_{ref}|}\sum_{i} e^{\eta_i^{(0)}}} = 100\cdot e^{R_j}`;
      const skala = v => (m.measure === 'fill' ? procent(v, 2) : liczba(v));
      dialog.querySelector('[data-maf-dialog-title]').textContent = `Jak obliczono IAF — ${k.name}`;
      cialo.innerHTML = `<dl class="maf-kv">
        <dt>Klub</dt><dd>${html(k.name)}${k.names_history.length > 1 ? ` <small class="note">(${html(k.names_history.join(', '))})</small>` : ''}</dd>
        <dt>Model / wersja</dt><dd>${html(m.label)} · ${html(m.version)}</dd><dt>Data treningu</dt><dd>${new Date(m.trained_at).toLocaleString('pl-PL')}</dd>
        <dt>Mecze w estymacji modelu</dt><dd>${liczba(m.matches_used)} (${html(m.period.from)} – ${html(m.period.to)})</dd>
        <dt>Mecze klubu jako rywala</dt><dd>${liczba(w.matches)} u ${liczba(w.hosts)} gospodarzy</dd>
        <dt>Populacja referencyjna X<sub>ref</sub></dt><dd>mecze z sezonów ${html(ref.seasons.join(', '))}: ${liczba(ref.matches_sampled)} wylosowanych z ${liczba(ref.matches_available)} (stałe ziarno); każdy z własnym gospodarzem, sezonem, rozgrywkami i warunkami, ale z efektem rywala zastąpionym przez R<sub>j</sub></dd>
        <dt>Oczekiwane ${m.measure === 'fill' ? 'wypełnienie' : 'liczba widzów'} — typowy rywal</dt><dd>${skala(ref.expected.median)} [95%: ${skala(ref.expected.q025)} – ${skala(ref.expected.q975)}]</dd>
        <dt>Oczekiwane ${m.measure === 'fill' ? 'wypełnienie' : 'liczba widzów'} — ${html(k.name)}</dt><dd>${skala(w.club_mean.median)} [95%: ${skala(w.club_mean.q025)} – ${skala(w.club_mean.q975)}]</dd>
      </dl>
      <h4>Wzór IAF ${ikonaInfo('iaf')}</h4><div class="maf-formula">${katex(wzor)}</div>
      <p class="note">η<sub>i</sub><sup>(0)</sup> = α + H<sub>h(i)</sub> + HS + S + L + x<sub>i</sub><sup>⊤</sup>β — predyktor meczu i bez efektu rywala. Referencyjny rywal ma R = 0 (średnia efektów wszystkich rywali, ograniczenie sumy zerowej).</p>
      <h4>1. Ilustracja na wartościach centralnych (nie jest metodą obliczenia)</h4>
      <ol class="maf-steps"><li>Mediany posterior: R<sub>j</sub> = ${liczba(w.effect.median, 4)}, η<sup>(0)</sup> uśrednione po X<sub>ref</sub>.</li>
      <li>Licznik: ${skala(w.central.club)}; mianownik: ${skala(w.central.reference)}.</li>
      <li>100 × ${skala(w.central.club)} / ${skala(w.central.reference)} = <b>${liczba(w.central.iaf, 1)}</b></li></ol>
      <h4>2. Faktyczna metoda — rozkład posterior ${ikonaInfo('iaf_posterior')}</h4>
      <ol class="maf-steps"><li>Dla każdej z S = ${liczba(probki)} zapisanych próbek posterior θ<sup>(s)</sup> (NUTS, ${m.sampler.chains} łańcuchy) liczymy IAF<sub>j</sub><sup>(s)</sup> powyższym wzorem — z pełnym η<sup>(0,s)</sup> dla każdego meczu referencyjnego. ${ikonaInfo('monte_carlo')}</li>
      <li>Mediana posterior: <b>${liczba(w.iaf.median, 1)}</b>; średnia: ${liczba(w.iaf.mean, 1)}. Mediana z próbek ≠ wzór na medianach (nieliniowość funkcji logistycznej — nierówność Jensena).</li>
      <li>95% przedział wiarygodności = kwantyle 2,5% i 97,5% próbek: <b>${liczba(w.iaf.q025, 1)} – ${liczba(w.iaf.q975, 1)}</b> ${ikonaInfo('przedzial')}</li>
      <li>P(IAF &gt; 100 | dane) = (1/S) Σ<sub>s</sub> 1[IAF<sup>(s)</sup> &gt; 100] = <b>${procent(w.p_gt_100, 1)}</b> ${ikonaInfo('p_iaf')}</li>
      ${w.pp ? `<li>Efekt w punktach procentowych: ${zeZnakiem(w.pp.median, 2)} p.p. [${zeZnakiem(w.pp.q025, 2)}; ${zeZnakiem(w.pp.q975, 2)}] ${ikonaInfo('efekt_pp')}</li>` : ''}
      <li>Dodatkowi widzowie (hala referencyjna${ref.capacity_median ? ` ${liczba(ref.capacity_median)} miejsc` : ''}): ${zeZnakiem(w.extra.median, 0)} [${zeZnakiem(w.extra.q025, 0)}; ${zeZnakiem(w.extra.q975, 0)}]</li></ol>
      <h4>Współczynniki wpływające na wynik</h4>
      <table class="att-table"><thead><tr><th>Składnik</th><th class="num">Mediana</th><th class="num">95%</th><th>Rola</th></tr></thead><tbody>
      <tr><td>R<sub>j</sub> — efekt klubu jako rywala</td><td class="num">${liczba(w.effect.median, 4)}</td><td class="num">${liczba(w.effect.q025, 3)} – ${liczba(w.effect.q975, 3)}</td><td>jedyny parametr różniący licznik od mianownika</td></tr>
      <tr><td>σ<sub>R</sub> — rozrzut efektów rywali ${ikonaInfo('hiperprior')}</td><td class="num">${sigmaR ? liczba(sigmaR.median, 3) : '—'}</td><td class="num">${sigmaR ? `${liczba(sigmaR.q025, 3)} – ${liczba(sigmaR.q975, 3)}` : '—'}</td><td>siła ściągania (partial pooling) ${ikonaInfo('pooling')}</td></tr>
      <tr><td>α, H, HS, S, L, β</td><td class="num" colspan="2">przez η<sup>(0)</sup> meczów referencyjnych</td><td>wspólne dla wszystkich klubów — standaryzacja porównania</td></tr>
      </tbody></table>
      <dl class="maf-kv"><dt>Diagnostyka IAF klubu</dt><dd>R-hat ${liczba(w.rhat, 3)} ${ikonaInfo('rhat')} · ESS ${liczba(w.ess_bulk)} ${ikonaInfo('ess')}</dd>
      <dt>Ocena wiarygodności</dt><dd>${w.reliable ? 'wiarygodne' : html(w.notes.join('; '))}</dd></dl>
      <p class="note">Wynik to statystyczny efekt związany z obecnością rywala przy kontroli gospodarza, sezonu i warunków meczu — nie dowód, że dana liczba widzów przyszła wyłącznie z jego powodu.</p>`;
      ustawIkony(cialo);
    } catch (blad) {
      cialo.innerHTML = `<p class="att-warning">${html(blad.message)}</p>`;
    }
  };

  const wczytaj = async () => {
    stan.model = element('[data-maf-model]')?.value;
    if (!stan.model || !element('[data-maf-kpis]')) return;
    element('[data-maf-kpis]').innerHTML = '<p class="note">Wczytywanie modelu…</p>';
    try {
      stan.dane = await pobierz(zParametrami(adresy.urlDane, {model: stan.model}));
    } catch (blad) {
      element('[data-maf-kpis]').innerHTML = `<p class="att-warning">${html(blad.message)}</p>`;
      return;
    }
    stan.zaznaczone.clear();
    stan.limit = LIMIT_WIERSZY;
    const rywale = klubyRywale().sort((a, b) => b.away.matches - a.away.matches);
    const wiarygodniRywale = rywale.filter(klub => klub.away.reliable);
    stan.trendy = (wiarygodniRywale.length ? wiarygodniRywale : rywale).slice(0, 3).map(klub => klub.id);
    const alfabetycznie = [...rywale].sort((a, b) => a.name.localeCompare(b.name, 'pl'));
    element('[data-maf-trend-select]').innerHTML = opcjeKlubow(alfabetycznie);
    element('[data-maf-posterior-select]').innerHTML = opcjeKlubow(alfabetycznie, rywale[0]?.id);
    const gospodarze = stan.dane.clubs.filter(klub => klub.home).sort((a, b) => b.home.matches - a.home.matches);
    element('[data-maf-host-select]').innerHTML = opcjeKlubow(gospodarze, gospodarze[0]?.id);
    status();
    kpi();
    ranking();
    odswiezPrzyciskPorownania();
    forest();
    trendy();
    posterior();
    gospodarz();
    symulatorPrzygotuj();
    odchylenia();
    diagnostyka();
    jakosc();
    ustawIkony();
  };

  const podlacz = () => {
    element('[data-maf-model]')?.addEventListener('change', wczytaj);
    ['[data-maf-search]', '[data-maf-reliable]', '[data-maf-min]'].forEach(s => element(s)?.addEventListener('input', () => { stan.limit = LIMIT_WIERSZY; ranking(); }));
    element('[data-maf-more]')?.addEventListener('click', () => { stan.limit += LIMIT_WIERSZY; ranking(); });
    element('[data-maf-ranking]')?.addEventListener('click', zdarzenie => {
      const naglowek = zdarzenie.target.closest('th[data-sort]');
      if (naglowek && !zdarzenie.target.closest('[data-maf-info-button]')) {
        const pole = naglowek.dataset.sort;
        stan.sortowanie = {pole, kierunek: stan.sortowanie.pole === pole ? -stan.sortowanie.kierunek : (pole === 'nazwa' ? 1 : -1)};
        ranking();
        return;
      }
      const wybor = zdarzenie.target.closest('[data-maf-select]');
      if (wybor) {
        const id = Number(wybor.dataset.mafSelect);
        if (wybor.checked) {
          if (stan.zaznaczone.size >= 2) { wybor.checked = false; return; }
          stan.zaznaczone.add(id);
        } else stan.zaznaczone.delete(id);
        odswiezPrzyciskPorownania();
        return;
      }
      const sladPrzycisk = zdarzenie.target.closest('[data-maf-trace]');
      if (sladPrzycisk) { slad(Number(sladPrzycisk.dataset.mafTrace)); return; }
      if (zdarzenie.target.closest('a, button, input')) return;
      const wiersz = zdarzenie.target.closest('tr.maf-row');
      if (wiersz) szczegolyWiersza(wiersz);
    });
    element('[data-maf-compare]')?.addEventListener('click', porownaj);
    ['[data-maf-forest-sort]', '[data-maf-forest-limit]', '[data-maf-forest-reliable]'].forEach(s => element(s)?.addEventListener('change', forest));
    element('[data-maf-trend-add]')?.addEventListener('click', () => {
      const id = Number(element('[data-maf-trend-select]').value);
      if (id && !stan.trendy.includes(id) && stan.trendy.length < 6) { stan.trendy.push(id); trendy(); }
    });
    element('[data-maf-trend-chips]')?.addEventListener('click', zdarzenie => {
      const usun = zdarzenie.target.closest('[data-maf-trend-remove]');
      if (usun) { stan.trendy = stan.trendy.filter(id => id !== Number(usun.dataset.mafTrendRemove)); trendy(); }
    });
    element('[data-maf-posterior-select]')?.addEventListener('change', posterior);
    element('[data-maf-host-select]')?.addEventListener('change', gospodarz);
    element('[data-maf-sim]')?.addEventListener('submit', zdarzenie => { zdarzenie.preventDefault(); symuluj(zdarzenie.target); });
    korzen.parentElement.querySelector('[data-maf-dialog-close]')?.addEventListener('click', () => korzen.parentElement.querySelector('[data-maf-dialog]').close());
  };

  const uruchom = () => {
    if (stan.uruchomiono) return;
    stan.uruchomiono = true;
    podlacz();
    wczytaj();
  };
  const widoczny = () => !panel.hidden && panel.offsetParent !== null;
  if (widoczny()) uruchom();
  new MutationObserver(() => {
    if (widoczny()) {
      uruchom();
      stan.wykresy.forEach(wykres => wykres.resize());
    }
  }).observe(panel, {attributes: true, attributeFilter: ['hidden', 'class', 'style']});
})();
