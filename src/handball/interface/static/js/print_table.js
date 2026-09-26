class WydrukTabeliBuilder {
  html(tabela, tytul, opis) {
    const wiersze = Array.from(tabela.rows).map(wiersz => this.wiersz(wiersz)).join('\n');
    return [
      '<!doctype html>',
      '<html lang="pl">',
      '<head>',
      '<meta charset="utf-8">',
      `<title>${this.tekst(tytul)}</title>`,
      '<style>body{font-family:Arial,sans-serif;font-size:11px;color:#000;background:#fff;margin:12px}h1{font-size:15px;margin:0 0 4px}p{margin:0 0 8px}table{border-collapse:collapse}th,td{border:1px solid #000;padding:2px 4px;text-align:left;vertical-align:top}thead th{font-weight:bold}@media print{body{margin:0}}</style>',
      '</head>',
      '<body>',
      `<h1>${this.tekst(tytul)}</h1>`,
      opis ? `<p>${this.tekst(opis)}</p>` : '',
      '<table>',
      wiersze,
      '</table>',
      '</body>',
      '</html>',
    ].join('\n');
  }

  wiersz(wiersz) {
    const komorki = Array.from(wiersz.cells).map(komorka => {
      const znacznik = komorka.tagName.toLowerCase() === 'th' ? 'th' : 'td';
      const scalenie = komorka.colSpan > 1 ? ` colspan="${komorka.colSpan}"` : '';
      return `<${znacznik}${scalenie}>${this.tekst(komorka.textContent)}</${znacznik}>`;
    });
    return `<tr>${komorki.join('')}</tr>`;
  }

  tekst(wartosc) {
    return String(wartosc || '')
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}

class DrukTabeliController {
  constructor(przycisk, dokument, okno, budowniczy) {
    this.przycisk = przycisk;
    this.dokument = dokument;
    this.okno = okno;
    this.budowniczy = budowniczy;
  }

  uruchom() {
    this.przycisk.addEventListener('click', () => this.drukuj());
  }

  drukuj() {
    const tabela = this.dokument.querySelector(this.przycisk.dataset.printTable);
    if (!tabela) return;
    const karta = this.okno.open('', '_blank');
    if (!karta) return;
    karta.document.open();
    karta.document.write(
      this.budowniczy.html(tabela, this.przycisk.dataset.printTitle, this.przycisk.dataset.printSubtitle),
    );
    karta.document.close();
  }
}

class DopasowanieDoStrony {
  constructor(szerokosc = 718, wysokosc = 1030, krok = 0.01, minimum = 0.3) {
    this.szerokosc = szerokosc;
    this.wysokosc = wysokosc;
    this.krok = krok;
    this.minimum = minimum;
    this.wysokoscKartki = 1047;
  }

  dopasuj(dokument) {
    const strona = dokument.querySelector('[data-print-page]');
    if (!strona) return 1;
    const poziomo = Boolean(strona.querySelector('.preview-hide-notes'));
    if (poziomo) strona.classList.add('print-landscape');
    const szerokosc = poziomo ? this.wysokoscKartki : this.szerokosc;
    const wysokosc = poziomo ? this.szerokosc - 18 : this.wysokosc;
    let skala = 1;
    while (true) {
      strona.style.width = `${szerokosc / skala}px`;
      strona.style.zoom = String(skala);
      if (this.miesci(strona, wysokosc) || skala - this.krok < this.minimum) {
        return skala;
      }
      skala = Math.round((skala - this.krok) * 100) / 100;
    }
  }

  miesci(strona, wysokosc) {
    if (strona.getBoundingClientRect().height > wysokosc) return false;
    return Array.from(strona.querySelectorAll('table')).every(
      tabela => tabela.getBoundingClientRect().width <= tabela.parentElement.getBoundingClientRect().width + 1,
    );
  }
}

class WydrukSekcjiBuilder extends WydrukTabeliBuilder {
  htmlSekcji(tresc, tytul, opis, arkusz) {
    return [
      '<!doctype html>',
      '<html lang="pl">',
      '<head>',
      '<meta charset="utf-8">',
      `<title>${this.tekst(tytul)}</title>`,
      arkusz ? `<link rel="stylesheet" href="${this.tekst(arkusz)}">` : '',
      '<style>*{-webkit-print-color-adjust:exact;print-color-adjust:exact}body{display:block;background:#fff;margin:12px;min-height:0}h1{font-size:16px;margin:0 0 4px}.print-subtitle{margin:0 0 10px;font-size:12px;color:#43566b}.preview-grid{display:block}.preview-grid>div{margin:0 0 18px;break-inside:avoid}.table-wrap{overflow:visible;max-height:none}table{width:100%}thead{display:table-header-group}th,td{white-space:nowrap}.preview-squad td.preview-prev{white-space:normal;max-width:none}.preview-prev small,.preview-prev small.muted{display:inline}.preview-prev-note::before{content:" · ";color:#8a97a3;font-weight:400}tr{break-inside:avoid}.preview-grid.preview-hide-notes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;align-items:start}.preview-grid.preview-hide-notes>div{min-width:0;margin:0}.preview-grid.preview-hide-notes .preview-legend{grid-column:1/-1}[data-print-page]{transform-origin:top left}[data-print-page].print-landscape{page:poziomo}@page{size:A4 portrait;margin:10mm}@page poziomo{size:A4 landscape;margin:10mm}@media print{body{margin:0}}</style>',
      '</head>',
      '<body>',
      '<div data-print-page>',
      `<h1>${this.tekst(tytul)}</h1>`,
      opis ? `<p class="print-subtitle">${this.tekst(opis)}</p>` : '',
      tresc,
      '</div>',
      `<script>${DopasowanieDoStrony.toString()};window.addEventListener('load', () => new DopasowanieDoStrony().dopasuj(document));</script>`,
      '</body>',
      '</html>',
    ].join('\n');
  }

  tresc(element) {
    const kopia = element.cloneNode(true);
    kopia.querySelectorAll('[data-print-exclude]').forEach(wezel => wezel.remove());
    if (kopia.classList && kopia.classList.contains('preview-hide-notes')) {
      kopia.querySelectorAll('.preview-prev-note').forEach(wezel => wezel.remove());
    }
    kopia.querySelectorAll('a').forEach(link => {
      const tekst = link.ownerDocument.createElement('span');
      tekst.textContent = link.textContent;
      link.replaceWith(tekst);
    });
    return kopia.outerHTML;
  }
}

class DrukSekcjiController {
  constructor(przycisk, dokument, okno, budowniczy) {
    this.przycisk = przycisk;
    this.dokument = dokument;
    this.okno = okno;
    this.budowniczy = budowniczy;
  }

  uruchom() {
    this.przycisk.addEventListener('click', () => this.drukuj());
  }

  drukuj() {
    const sekcja = this.dokument.querySelector(this.przycisk.dataset.printSection);
    if (!sekcja) return;
    const karta = this.okno.open('', '_blank');
    if (!karta) return;
    const arkusz = this.przycisk.dataset.printStyles
      ? new URL(this.przycisk.dataset.printStyles, this.dokument.baseURI).href
      : '';
    karta.document.open();
    karta.document.write(
      this.budowniczy.htmlSekcji(
        this.budowniczy.tresc(sekcja),
        this.przycisk.dataset.printTitle,
        this.przycisk.dataset.printSubtitle,
        arkusz,
      ),
    );
    karta.document.close();
  }
}

document.querySelectorAll('[data-print-section]').forEach(przycisk => {
  new DrukSekcjiController(przycisk, document, window, new WydrukSekcjiBuilder()).uruchom();
});

document.querySelectorAll('[data-print-table]').forEach(przycisk => {
  new DrukTabeliController(przycisk, document, window, new WydrukTabeliBuilder()).uruchom();
});
