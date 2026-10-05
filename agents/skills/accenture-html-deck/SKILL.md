---
name: accenture-html-deck
description: Crea o modifica la presentazione finale HTML in presentation/ seguendo le brand guidelines Accenture e la scaletta di 5 minuti richiesta dalla consegna. Usare per qualsiasi modifica a presentation/index.html.
---

# Presentazione HTML, brand Accenture

## Vincoli di consegna
- Un solo file `presentation/index.html`, autosufficiente e offline: niente CDN, font o immagini remote. Eventuali screenshot in `presentation/assets/`.
- Deve presentare **la soluzione e la struttura agentica** in **5 minuti**, demo inclusa: al massimo 8 slide, un messaggio per slide.

## Brand (palette di base Accenture)
- Sfondo nero `#000000`, testo bianco `#FFFFFF`, testo secondario `#B3B3B3`.
- Viola core **`#A100FF`** per accenti grafici, numeri chiave e il simbolo `>`. Su sfondo nero, per testo piccolo usa il viola chiaro `#BE82FF` (contrasto leggibile). Viola scuri `#7500C0` e `#460073` per superfici e riempimenti.
- Il simbolo **`>`** è l'elemento ricorrente: elenchi puntati e frecce di flusso.
- Font: `Graphik` (font del brand) con ripiego `Arial, Helvetica, sans-serif`; `ui-monospace` per codice e alberi di cartelle.
- Etichetta di sezione sopra ogni titolo: maiuscolo, spaziato, viola chiaro (es. `REPOSITORY FINALE`).
- Card su `#0D0D0D` con bordo `#262626`, angoli arrotondati. Niente gradienti arcobaleno, niente stock photo.

## Scaletta (allineata ai criteri di valutazione)
1. Copertina: nome, promessa in una riga, team.
2. User Difficulty Statement (Tema 02).
3. Soluzione: flusso documenti, estrazione AI, conferma utente, calcolo, comprensione.
4. Before / After Simplicity Evidence, con screenshot reali dell'app.
5. Demo live.
6. Struttura agentica: rules, hook, skill, subagent, comando, prompt, con la doppia rete sul vincolo.
7. Uso consapevole dell'AI + verifica umana: dove l'AI, dove no, numeri sui token, punti di controllo umani.
8. Risk & Clarity Note + chiusura con il link al repo.

## Regole
- I contenuti marcati con classe `todo` sono segnaposto: prima del freeze non ne deve restare nessuno (`grep -c 'class="todo' presentation/index.html` deve dare 0).
- Ogni testo sulla soluzione rispetta il vincolo di dominio: si descrive cosa l'app fa capire, mai cosa l'utente dovrebbe fare con i soldi.
- Numeri e affermazioni devono corrispondere al repo (`agents/workflows/uso-token.md`, `app/docs/requisiti-funzionali.md`).
