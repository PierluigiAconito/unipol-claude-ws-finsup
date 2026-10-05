# Deliverable Tema 02: evidenze dal prototipo BudgetFacile

I tre deliverable richiesti dalla challenge, con i numeri reali prodotti dall'app (estrazione dai documenti, verificata il 2026-10-05) sui due scenari demo in [`app/demo_assets/`](../demo_assets/). I documenti sono fittizi (persone, aziende e banche inesistenti); i valori attesi sono in [`demo_data.py`](../finsup/demo_data.py) e verificati da `test_demo_scenarios_match_expected_values`.

| Scenario | Persona | Documenti |
|---|---|---|
| **Basso risparmio** | Marco Ferretti, commesso, Milano | `marco_bustapaga.pdf` · `marco_bolletta.pdf` · `marco_estrattoconto.xlsx` |
| **Alto risparmio** | Alessandra Moretti, quadro, Torino | `alessandra_bustapaga.pdf` · `alessandra_estrattoconto.xlsx` |

## 1. User Difficulty Statement

Vedi [requisiti-funzionali.md §2](requisiti-funzionali.md#2-persona-e-difficoltà-user-difficulty-statement): una persona con bassa alfabetizzazione finanziaria riceve busta paga, bollette ed estratto conto pieni di gergo, e ogni mese non riesce a rispondere a "quanto spendo, per cosa, e quanto mi resta davvero?".

## 2. Before / After Simplicity Evidence

### Before: documenti sparsi, nessun quadro d'insieme (Marco)

| Documento | Cosa vede l'utente |
|---|---|
| Busta paga | Lordo 1.750,00 €, poi contributi INPS 9,19%, base imponibile IRPEF, IRPEF lorda al 23%, detrazione art. 13 TUIR, IRPEF netta, addizionali regionale e comunale, quota TFR, contributo INPS azienda, costo aziendale. Il netto (1.408,73 €) è una riga tra le altre |
| Bolletta multiservizi | 13 righe su 3 servizi: quota energia, quota potenza impegnata, canone di distribuzione (quota rete), accise e oneri di sistema, IVA 10% e 22%, POD/PDR, imposta di bollo, interessi di mora "D.Lgs. 231/2002". Totale 130,95 € |
| Estratto conto | 15 movimenti con sigle: prestito personale "TAEG 8,99%", "Addebito RID", imposta di bollo trimestrale, canone, commissione di gestione. Lo stipendio compare di nuovo come accredito e la bolletta di nuovo come addebito |

Per sapere quanto resta a fine mese bisogna capire quale riga della busta paga conta, non contare due volte stipendio e bolletta, sommare gli addebiti, riportare al mese il bollo trimestrale e capire cosa sono TAEG, oneri di sistema, mora e RID.

### After: un budget unico, spiegato

Caricati i documenti e confermato il calcolo nella conferma RF-09 (i doppioni tra documenti li toglie l'app e li mostra in giallo):

| | Marco (basso risparmio) | Alessandra (alto risparmio) |
|---|---|---|
| Entrate al mese | **1.408,73 €** | **3.296,34 €** (stipendio 2.576,34 € + affitto percepito 720 €) |
| Uscite al mese | **1.490,29 €** | **2.164,10 €** |
| Risparmio al mese | **−81,56 €** (−5,8%): avviso RF-06 con le categorie che pesano di più, senza indicazioni su cosa fare | **1.132,24 €** (34,3%) |
| Dove vanno le uscite | Abitazione 52,2% · Debiti/finanziamenti 19,1% · Alimentari 16,0% · Assicurazioni 5,0% · Altro 3,8% · Trasporti 2,3% · Svago 1,5% | Abitazione 49,9% · Alimentari 21,6% · Altro 10,0% · Assicurazioni 5,3% · Svago 5,2% · Salute 4,2% · Trasporti 3,7% |
| Regola 50/30/20 (riferimento) | necessità 104,2% · desideri 1,6% · risparmio −5,8% | necessità 62,2% · desideri 3,4% · risparmio 34,3% |
| Obiettivo di risparmio | 1.000 €: "mantenendo il ritmo attuale la cifra non viene raggiunta" | 10.000 €: "raggiunta in circa 9 mesi", come proiezione matematica |

Perché l'app non dà lo stesso saldo del riepilogo della banca (Marco −87,26 €, Alessandra +1.085,29 €): riporta al mese le voci non mensili (RF-02). Il bollo trimestrale di 8,55 € vale 2,85 € al mese, le spese annuali del fido di 45 € valgono 3,75 € al mese.

Esempi di singola voce, prima e dopo:

| Prima (documento) | Dopo (BudgetFacile) |
|---|---|
| `26/09/2025  Imposta di bollo trimestrale conto corrente (luglio-settembre 2025)  8,55` | Categoria Altro, **2,85 € al mese** (8,55 € ÷ 3). Glossario: è una tassa dello Stato che la banca trattiene e versa allo Stato |
| `Accise e oneri di sistema energia  120 kWh × 0,0227 €/kWh  2,72` | Dentro la voce "Energia elettrica" (58,05 €, IVA inclusa). Glossario per "Accise" e "Oneri di sistema" |
| `Rata mensile prestito personale nr. 14/48 - BancaAmici (TAEG 8,99%)  285,00` | Categoria Debiti/finanziamenti, 19,1% delle uscite di Marco. Glossario: il TAEG è il costo totale del prestito in un anno, interessi e spese compresi |

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
- Stesso denaro in due documenti (stipendio in busta paga e accredito in estratto conto; bolletta e suo addebito RID): l'app lo conta una volta sola, tiene il dettaglio (netto in busta, voci della bolletta) e toglie l'accredito o l'addebito dell'estratto conto. Le voci tolte restano visibili, in giallo, nella conferma RF-09: niente sparisce in silenzio.

**Come è stata evitata l'ambiguità**
- Disclaimer "strumento educativo, non consulenza finanziaria" in cima a ogni schermata.
- **Conferma obbligatoria (RF-09)**: nessun calcolo senza passare dalla tabella editabile voce per voce; i risultati senza conferma rimandano alla conferma (test `test_results_without_confirmation_redirect_to_confirmation`).
- Nessuna prescrizione: il 50/30/20 è "un termine di paragone, non un obiettivo da raggiungere"; con risparmio negativo l'app mostra solo quali categorie pesano di più (RF-06); la proiezione dichiara di non essere una previsione e di non considerare interessi, inflazione e imprevisti (RF-07).
- Ogni testo AI passa da [`content_guard.py`](../finsup/content_guard.py) **prima** di essere mostrato; se viola il vincolo non viene mostrato e l'utente vede che una spiegazione è stata omessa.
- Fonte sempre dichiarata: definizione rivista a mano dal team oppure spiegazione generata automaticamente e passata dal filtro anti-consigli.

**Limiti noti**: la categoria è proposta dall'estrazione, che segue le regole della specifica §4.2 scritte nel prompt (mutuo e affitto in Abitazione, ristorazione in Alimentari); se sbaglia, si corregge nella conferma RF-09 e i totali non cambiano. Il riconoscimento dei doppioni si basa sugli importi: due spese diverse con lo stesso importo in file diversi vanno controllate nella tabella gialla. Il prototipo copre l'happy path (§8 della specifica).

## Scaletta della demo (circa 2 minuti)

0. **Prima del pitch**: `.venv/Scripts/python app/scripts/prewarm_extraction.py app/demo_assets/*` legge i 5 documenti una volta e salva il risultato in cache (l'estrazione reale richiede 40-100 s per documento). In demo gli stessi file vengono riletti all'istante, a costo zero.
1. **Marco, basso risparmio. Before**: aprire la bolletta (13 righe di gergo) e la busta paga.
2. Caricare i 3 file di Marco e premere "Carica i documenti": grazie al passo 0 la lettura è istantanea e non richiede rete.
3. **Conferma RF-09**: accredito dello stipendio (= busta paga) e addebito RID della bolletta (= totale delle sue voci) sono già tolti e mostrati in giallo; far vedere che gli importi sono quelli dei documenti, poi confermare.
4. **After**: risparmio −81,56 € con l'avviso RF-06 (Abitazione e Debiti pesano di più), regola 50/30/20 come riferimento, glossario su "Oneri di sistema" e "TAEG".
5. **Alessandra, alto risparmio**: "Ricomincia da capo", caricare i 2 file e confermare (stipendio contato una volta, mutuo già in Abitazione). Risparmio 1.132,24 € (34,3%); obiettivo di 10.000 € in circa 9 mesi.
