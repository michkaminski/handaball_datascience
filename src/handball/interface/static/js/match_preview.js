class OpcjeZapowiedziController {
  constructor(dokument, formularz) {
    this.dokument = dokument;
    this.formularz = formularz;
  }

  uruchom() {
    this.dokument.querySelectorAll('[data-preview-apply]').forEach(przycisk => {
      przycisk.hidden = true;
    });
    this.dokument.querySelectorAll('[data-preview-auto]').forEach(pole => {
      pole.addEventListener('change', () => this.zatwierdz(pole));
    });
  }

  zatwierdz(pole) {
    const sekcja = pole.closest('section[id]');
    this.formularz.action = sekcja ? `#${sekcja.id}` : '';
    this.formularz.submit();
  }
}

class UwagiKadryController {
  constructor(pole, siatka) {
    this.pole = pole;
    this.siatka = siatka;
  }

  uruchom() {
    this.pole.addEventListener('change', () => this.pokaz());
    this.pokaz();
  }

  pokaz() {
    this.siatka.classList.toggle('preview-hide-notes', this.pole.checked);
  }
}

const formularzOpcjiZapowiedzi = document.querySelector('[data-preview-options]');
if (formularzOpcjiZapowiedzi) new OpcjeZapowiedziController(document, formularzOpcjiZapowiedzi).uruchom();
document.querySelectorAll('[data-preview-notes-toggle]').forEach(pole => {
  const siatka = document.querySelector(pole.dataset.previewNotesToggle);
  if (siatka) new UwagiKadryController(pole, siatka).uruchom();
});
