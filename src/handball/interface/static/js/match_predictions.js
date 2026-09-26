class WierszePrognozController {
  constructor(tabela, okno) {
    this.tabela = tabela;
    this.okno = okno;
  }

  uruchom() {
    this.tabela.querySelectorAll('tbody tr[data-href]').forEach(wiersz => {
      wiersz.classList.add('row-clickable');
      wiersz.tabIndex = 0;
      wiersz.addEventListener('click', zdarzenie => this.klik(wiersz, zdarzenie));
      wiersz.addEventListener('auxclick', zdarzenie => {
        if (zdarzenie.button === 1 && !this.elementInteraktywny(zdarzenie)) this.okno.open(wiersz.dataset.href, '_blank');
      });
      wiersz.addEventListener('keydown', zdarzenie => {
        if (zdarzenie.key === 'Enter' && zdarzenie.target === wiersz) {
          zdarzenie.preventDefault();
          this.przejdz(wiersz.dataset.href);
        }
      });
    });
  }

  klik(wiersz, zdarzenie) {
    if (this.elementInteraktywny(zdarzenie)) return;
    if (zdarzenie.ctrlKey || zdarzenie.metaKey) {
      this.okno.open(wiersz.dataset.href, '_blank');
      return;
    }
    this.przejdz(wiersz.dataset.href);
  }

  elementInteraktywny(zdarzenie) {
    return Boolean(zdarzenie.target.closest && zdarzenie.target.closest('a, button, input, select'));
  }

  przejdz(adres) {
    this.okno.location.href = adres;
  }
}

const tabelaPrognoz = document.querySelector('[data-prediction-report] #predictions-table');
if (tabelaPrognoz) new WierszePrognozController(tabelaPrognoz, window).uruchom();
const tabelaTypowan = document.querySelector('[data-tips-report] #tips-table');
if (tabelaTypowan) new WierszePrognozController(tabelaTypowan, window).uruchom();
