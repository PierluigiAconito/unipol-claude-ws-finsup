# Deliverable Tema 02: evidenze dal prototipo FinSup

I tre deliverable richiesti dalla challenge, con i numeri reali prodotti dall'app sui documenti demo in [`app/demo_assets/`](../demo_assets/) (persona e importi inventati, generati da [`generate_demo_assets.py`](../scripts/generate_demo_assets.py)).

## 1. User Difficulty Statement

Vedi [requisiti-funzionali.md §2](requisiti-funzionali.md#2-persona-e-difficoltà-user-difficulty-statement): una persona con bassa alfabetizzazione finanziaria riceve busta paga, estratto conto e altri documenti pieni di gergo, e ogni mese non riesce a rispondere a "quanto spendo, per cosa, e quanto mi resta davvero?".

## 2. Before / After Simplicity Evidence

### Before: tre documenti, nessun quadro d'insieme

| Documento | Cosa vede l'utente |
|---|---|
| `busta_paga_demo.pdf` | 9 righe tra competenze e trattenute: lordo 2.180,00 €, contributi INPS 9,19%, imponibile IRPEF, IRPEF lorda, detrazioni art. 13 TUIR, addizionali "rata 9/11", TFR "accantonato, non corrisposto". Il netto (1.620,00 €) è una riga tra le altre |
| `estratto_conto_demo.pdf` | 15 addebiti in ordine di data, con sigle e note legali: "TAN 7,90% - TAEG 8,45%", "addebito diretto SDD", "interessi di mora", "commissione di gestione", "imposta di bollo (addebito trimestrale)" |
| `foglio_spese_demo.xlsx` | voci annuali (assicurazione RC con franchigia 500 €, bollo auto, TARI) e un'entrata annuale "netto ritenuta d'acconto", da riportare al mese a mano |

Per sapere quanto resta a fine mese bisogna: capire quale riga della busta paga conta, sommare 15 addebiti, dividere per 12 le voci annuali e per 3 il bollo trimestrale, e capire cosa sono TAEG, mora, SDD.

### After: un budget unico, spiegato

Caricati i tre file, controllate le voci nella schermata di conferma e confermato il calcolo, l'app mostra:

| | Valore |
|---|---|
| Entrate al mese | **1.720,00 €** (stipendio netto 1.620 € + collaborazioni 1.200 €/anno = 100 €/mese) |
| Uscite al mese | **1.682,54 €** |
| Risparmio al mese | **37,46 €**, tasso di risparmio **2,2%** |
| Dove vanno le uscite | Abitazione 46,9% · Alimentari 22,6% · Debiti/finanziamenti 11,7% · Trasporti 8,2% · Svago 4,0% · Salute 3,4% · Assicurazioni 2,7% · Altro 0,5% (torta + tabella) |
| Regola 50/30/20 | necessità 93,9% · desideri 4,0% · risparmio 2,2% delle entrate, accanto al riferimento 50/30/20 (grafico a barre) |
| Obiettivo 1.000 € | "verrebbe raggiunta in circa 27 mesi (circa 2 anni e 3 mesi)", come proiezione matematica |

Esempio di singola voce, prima e dopo:

| Prima (estratto conto) | Dopo (FinSup) |
|---|---|
| `14/09/2026  Imposta di bollo (addebito trimestrale)  8,55 €` | Categoria Altro, **2,85 € al mese** (8,55 € ÷ 3). Glossario: *"È una tassa dello Stato che la banca trattiene dal conto e versa allo Stato: non è un guadagno della banca."* |
| `10/09/2026  Interessi di mora rata di agosto  12,40 €` | Categoria Debiti/finanziamenti. Glossario: *"Sono interessi in più che si pagano quando una rata o una bolletta viene pagata dopo la scadenza: una specie di penale per il ritardo."* |
| `Assicurazione auto RC (franchigia 500 €)  540  annuale` | **45,00 € al mese**. Glossario per "RC auto" e "Franchigia" |

## 3. Risk & Clarity Note

**Cosa è stato semplificato**
- Gergo dei documenti → definizioni di massimo 2 frasi. Per i 26 termini più comuni (busta paga, estratto conto, bolletta) la definizione è preparata con Claude e rivista a mano; gli altri termini trovati nei documenti li spiega Claude su richiesta, con una sola chiamata.
- Bollette → una voce per servizio (luce, gas, internet) con IVA, accise e oneri inclusi, più i costi accessori (bollo, mora): stesso totale, molte meno righe.
- Decine di righe sparse → 8 categorie di spesa della specifica, con incidenza in percentuale.
- Importi annuali e trimestrali → quota mensile, sempre affiancata all'importo originale nella tabella "Come è stato calcolato".
- Regola 50/30/20: solo la categoria Svago conta come "desideri", tutte le altre come "necessità". La semplificazione è scritta sotto il grafico.

**Cosa NON è stato alterato**
- Gli importi: l'estrazione riporta l'importo esatto del documento e la colonna "Da dove arriva" indica il file di origine. I calcoli sono deterministici ([`budget.py`](../finsup/budget.py), coperti da test), non generati dall'AI.
- Nessuna voce sparisce in silenzio: se un'etichetta estratta fa scattare il guardrail, la voce resta con il suo importo e un'etichetta neutra, segnalata all'utente.
- Busta paga: conta solo il netto in busta. Lordo e trattenute non diventano uscite, quindi niente doppio conteggio.
- Stesso importo in due documenti (es. stipendio in busta paga e accredito sull'estratto conto): l'app non unisce nulla da sola, segnala il "possibile doppione" nella conferma e lascia decidere all'utente.

**Come è stata evitata l'ambiguità**
- Disclaimer "strumento educativo, non consulenza finanziaria" in cima a ogni schermata e nella barra laterale.
- **Conferma obbligatoria (RF-09)**: nessun calcolo senza passare dalla tabella editabile voce per voce; i risultati senza conferma rimandano alla conferma (test `test_results_without_confirmation_redirect_to_confirmation`).
- Nessuna prescrizione: il 50/30/20 è "un termine di paragone, non un obiettivo da raggiungere"; con risparmio negativo l'app mostra solo quali categorie pesano di più (RF-06); la proiezione dichiara di non essere una previsione e di non considerare interessi, inflazione e imprevisti (RF-07).
- Ogni testo AI passa da [`content_guard.py`](../finsup/content_guard.py) **prima** di essere mostrato; se viola il vincolo non viene mostrato e l'utente vede che una spiegazione è stata omessa.
- Fonte sempre dichiarata: definizione rivista dal team oppure spiegazione generata da Claude, con il costo della chiamata.

**Limiti noti**: la categoria proposta dall'estrazione può essere discutibile (es. "Ristoranti e bar" in Svago invece che in Alimentari); per questo esiste la conferma RF-09. Il prototipo copre l'happy path (§8 della specifica).

## Scaletta della demo (circa 2 minuti)

0. **Prima del pitch**: `.venv/Scripts/python app/scripts/prewarm_extraction.py app/demo_assets/*` legge i documenti una volta e salva il risultato in cache (l'estrazione reale richiede 40-100 s per documento). In demo lo stesso file viene riletto all'istante, a costo zero.
1. **Before**: aprire `estratto_conto_demo.pdf` e `busta_paga_demo.pdf`.
2. Caricare i 3 file e premere "Leggi i documenti con Claude". Fallback offline: "Usa i dati di esempio", con gli stessi dati dei documenti.
3. **Conferma RF-09**: mostrare la colonna "Da dove arriva", correggere una categoria (Ristoranti → Alimentari), poi confermare.
4. **After**: metriche, poi le schede Riepilogo (torta + barre), Regola 50/30/20, Parole tecniche, Obiettivo di risparmio (1.000 €).
5. **RF-06**: "Modifica i dati", cancellare la riga "Collaborazioni occasionali" e confermare. Il saldo diventa −62,54 €, con evidenza delle categorie più pesanti e nessuna indicazione su cosa fare.
