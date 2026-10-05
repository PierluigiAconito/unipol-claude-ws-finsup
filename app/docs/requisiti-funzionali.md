# Requisiti Funzionali — App Educazione Finanziaria: Gestione Budget Personale

Versione: 0.3 (allineata a Hagenthon — Tema 02 "Inclusione Finanziaria")
Autore: C. Beltrame
Stato: Da validare

**Ambito**: applicazione web, demo funzionante per workshop, singolo utente,
valuta EUR, calcolo istantaneo (nessuno storico/persistenza multi-sessione
richiesto). I casi limite non critici per la demo possono restare non gestiti
(happy path prioritario).

**Scenario educativo scelto (vincolo challenge)**: *gestione del budget
personale*. L'app aiuta una persona a costruire e capire, in linguaggio
semplice, come sono composte le proprie entrate e uscite mensili e cosa
significa il risparmio che ne risulta — **non** fornisce consulenza
finanziaria, raccomandazioni di investimento né indicazioni su cosa fare con
i propri soldi (vietato esplicitamente dalla challenge).

## 1. Obiettivo del modulo

Dato il quadro economico mensile di una persona (entrate e uscite, anche
caricate da documenti reali), aiutarla a **capire** come è composto il proprio
budget: quanto entra, quanto esce e per cosa, quanto risparmio ne risulta, e
cosa significano in parole semplici le voci tecniche che incontra nei propri
documenti finanziari (bollette, estratti conto, busta paga). L'app non
raccomanda cosa fare con il risparmio: fornisce consapevolezza e comprensione,
non consulenza.

## 2. Persona e difficoltà (User Difficulty Statement)

- **Chi**: persona con bassa alfabetizzazione finanziaria, reddito da una o
  più fonti (stipendio + eventuali entrate accessorie), che riceve
  regolarmente documenti finanziari (bollette, estratto conto, busta paga)
  pieni di voci e gergo tecnico che non comprende a pieno (es. commissioni,
  interessi, TAEG, trattenute).
- **In quale processo**: ogni mese deve rispondere alla domanda "quanto sto
  spendendo, per cosa, e quanto mi resta davvero?" — oggi non riesce a
  costruire un quadro chiaro perché i dati sono sparsi su più documenti con
  linguaggio tecnico.
- **Dove si blocca**: non riesce ad aggregare entrate/uscite in un budget
  comprensibile, né a interpretare correttamente le singole voci dei propri
  documenti, e quindi non sa dire con sicurezza quanto può effettivamente
  risparmiare ogni mese.
- **Perché è rilevante**: senza un budget chiaro non può prendere decisioni
  quotidiane informate (è un prerequisito dell'educazione finanziaria di
  base, non un consiglio su investimenti).

## 3. Attori

- **Utente finale**: singola persona fisica descritta in §2. (Nessun
  multi-utente/nucleo familiare in questa versione.)

## 4. Dati in input

### 4.1 Entrate
| Campo | Tipo | Note |
|---|---|---|
| Stipendio netto mensile | numero | principale, obbligatorio |
| Altre entrate ricorrenti | numero + descrizione | es. affitto percepito, pensione, secondo lavoro |
| Entrate variabili/occasionali | numero + descrizione + periodicità | es. bonus annuale, tredicesima/quattordicesima, freelance — da normalizzare su base mensile (es. bonus annuo / 12) |

### 4.2 Uscite
| Categoria | Esempi | Tipo |
|---|---|---|
| Abitazione | mutuo/affitto, condominio, utenze (luce, gas, acqua, internet) | fissa |
| Debiti/finanziamenti | rate prestiti, carte revolving | fissa |
| Assicurazioni | auto, casa, vita, sanitaria | fissa |
| Trasporti | carburante, abbonamento mezzi, bollo/assicurazione auto | semi-fissa |
| Salute e benessere | palestra, farmaci, visite mediche | semi-fissa |
| Alimentari | spesa, ristorazione | variabile |
| Svago/discrezionale | abbonamenti streaming, shopping, viaggi, hobby | variabile |
| Altro | voce libera | variabile |

Ogni voce di spesa ha: **nome, importo, categoria, tipo (fissa/variabile),
periodicità** (mensile, trimestrale, annuale → normalizzata su base mensile).

## 5. Logica di calcolo

```
Entrate totali mensili = stipendio + altre entrate ricorrenti + (entrate variabili / periodicità in mesi)
Uscite totali mensili  = somma di tutte le spese normalizzate su base mensile
Risparmio mensile      = Entrate totali mensili − Uscite totali mensili
```

Indicatori derivati utili per la comprensione del budget (puramente
informativi, nessuna prescrizione):
- **Tasso di risparmio** = Risparmio mensile / Entrate totali mensili (%)
- **% spese fisse** vs **% spese variabili** sul totale entrate
- **Incidenza % di ogni categoria di spesa** sul totale uscite

## 6. Requisiti funzionali (RF)

- **RF-01**: L'utente inserisce entrate e uscite in due modalità alternative/
  complementari:
  - **a) Form guidato**: categorie predefinite + possibilità di aggiungere voci
    personalizzate, come descritto in §4.
  - **b) Caricamento file** (PDF o XLS/XLSX): l'utente carica **i documenti che
    ha a disposizione così come sono** (es. busta paga, estratto conto, foglio
    spese personale), senza vincoli di template. Il contenuto viene inviato a
    Claude, che lo analizza e ne estrae/propone automaticamente le voci di
    entrata e di uscita (importo, descrizione, categoria), precompilando il
    form di cui al punto (a). L'utente può correggere i valori estratti prima
    di lanciare il calcolo.
    *Implicazione architetturale: l'estrazione non è un parser deterministico
    su formato fisso, ma una chiamata a Claude (con supporto nativo a
    PDF/immagini e testo da file XLS) che restituisce i dati strutturati
    (JSON) da cui popolare il form.*
- **RF-02**: Il sistema normalizza automaticamente importi non mensili (annuali,
  trimestrali) su base mensile.
- **RF-03**: Il sistema calcola e mostra il risparmio mensile disponibile, con
  dettaglio di come è stato ottenuto (entrate − uscite, per categoria) in una
  visualizzazione chiara (prima: dati grezzi sparsi sui documenti originali;
  dopo: budget unico, aggregato e leggibile — vedi §9 Before/After).
- **RF-04**: Il sistema spiega in linguaggio semplice il significato dei
  termini tecnici incontrati nei documenti caricati o nelle voci di spesa
  (es. TAEG, interessi, commissioni, trattenute) tramite un breve glossario
  contestuale generato da Claude. Scopo: comprensione, non azione.
- **RF-05**: Il sistema mostra il tasso di risparmio calcolato e lo confronta,
  a solo scopo informativo/educativo, con un benchmark noto (es. regola
  50/30/20: 50% necessità, 30% desideri, 20% risparmio), spiegando cosa
  significa senza raccomandare di cambiare nulla.
- **RF-06**: Se il risparmio mensile è negativo o nullo, il sistema lo
  evidenzia chiaramente e mostra quali categorie di spesa incidono
  maggiormente sul totale, a scopo di consapevolezza — **senza indicare quali
  spese tagliare o quali azioni intraprendere** (nessuna prescrizione).
- **RF-07**: Il sistema consente di impostare un obiettivo di risparmio
  definito dall'utente (es. "mettere da parte 1.000€") e mostra, come
  semplice proiezione matematica, in quanti mesi sarebbe raggiungibile
  mantenendo il ritmo di risparmio attuale. È una simulazione illustrativa
  dell'effetto nel tempo delle proprie scelte di budget, non un consiglio su
  come/dove investire o allocare il denaro.
- **RF-08**: Tutti gli importi sono espressi in EUR (nessuna gestione
  multi-valuta).
- **RF-09**: Prima di eseguire il calcolo, il sistema mostra sempre una
  **schermata di conferma obbligatoria** con tutti i dati (inseriti a mano o
  estratti da file), editabile voce per voce. Il calcolo del budget parte solo
  dopo conferma esplicita dell'utente — mai in automatico subito dopo
  l'estrazione da file. Questo garantisce sia la robustezza della demo live
  (un eventuale errore di estrazione è visibile e correggibile) sia il
  vincolo "non alterare il significato originale" (§7).

> Nota: non è richiesto il salvataggio persistente del profilo o lo storico
> mensile — la demo copre un singolo calcolo "istantaneo" per sessione.

## 7. Cosa l'app NON fa (vincoli di conformità alla challenge)

- Non fornisce raccomandazioni di investimento (no ETF, fondi, azioni, ecc.).
- Non fornisce consulenza finanziaria personalizzata né indica cosa comprare,
  vendere o scegliere.
- Non prescrive tagli di spesa specifici: evidenzia i dati, la decisione resta
  interamente dell'utente.
- Non è un chatbot generico aperto: ogni interazione è legata a una capability
  applicativa concreta (calcolo budget, estrazione/spiegazione documenti,
  glossario, simulazione proiezione risparmio).
- Non altera il significato delle informazioni originali quando le
  semplifica: i dati estratti dai documenti caricati restano modificabili e
  verificabili dall'utente prima del calcolo (vedi RF-01b e RF-09).

## 8. Validazioni e casi limite

Per la demo si copre solo l'happy path. Gestita esplicitamente solo la
segnalazione di risparmio mensile negativo (RF-06), poiché è parte del
messaggio di valore della demo. Altri casi limite (importi non numerici, file
non riconosciuto, nessuna entrata inserita, periodicità irregolari, ecc.) sono
**fuori scope** e possono non essere gestiti.

## 9. Output atteso e deliverable della challenge

Output applicativo (demo) — tutti i punti seguenti sono componenti UI
**richiesti e funzionanti** nella demo, non mockup statici:
- Riepilogo mensile: entrate, uscite per categoria, risparmio netto.
- **Grafico** (a torta per ripartizione spese per categoria; a barre per
  confronto entrate vs uscite vs benchmark 50/30/20) — componente reale,
  collegato ai dati confermati dall'utente (RF-09).
- Glossario contestuale dei termini tecnici incontrati (RF-04).
- Confronto informativo con benchmark 50/30/20 (RF-05).

Deliverable richiesti esplicitamente dalla challenge, da preparare per la demo:
1. **User Difficulty Statement** → coperto da §2.
2. **Before/After Simplicity Evidence**: esempio concreto con un documento
   reale/realistico (es. busta paga + bolletta) che mostra (a) la situazione
   di partenza — voci sparse, linguaggio tecnico, nessun quadro d'insieme —
   e (b) il budget unico, chiaro e spiegato prodotto dall'app.
3. **Risk & Clarity Note**: cosa è stato semplificato (linguaggio tecnico →
   spiegazioni in parole semplici, aggregazione in categorie), cosa non è
   stato alterato (gli importi reali restano quelli originali e sono sempre
   visibili/modificabili dall'utente), e come si è evitata ambiguità
   (nessuna raccomandazione implicita, disclaimer esplicito "strumento
   educativo, non consulenza finanziaria" visibile in UI).

## 10. Decisioni confermate (ex punti aperti)

1. **Grafico**: componente UI reale e funzionante nella demo (non un
   placeholder) — vedi §9, tipo a torta/barre, collegato ai dati confermati.
2. **Conferma dati obbligatoria**: formalizzata come **RF-09** — nessun
   calcolo parte senza passaggio esplicito dell'utente attraverso la
   schermata di conferma/modifica.
3. **File di esempio**: saranno predisposti file fittizi/anonimizzati
   (es. busta paga, bolletta, estratto conto) da usare sia come fallback in
   demo sia come base per il deliverable "Before/After Simplicity Evidence"
   (§9 punto 2).

## 11. Asset da preparare per la demo

- Almeno 1 documento fittizio di busta paga (PDF).
- Almeno 1 documento fittizio tra bolletta o estratto conto (PDF o XLS), con
  alcune voci in gergo tecnico (es. "commissione di gestione", "interessi di
  mora", "TAEG") da far spiegare al glossario (RF-04) — utile anche a
  dimostrare visivamente il Before/After.
- Nessun dato reale/personale: tutti i file demo devono essere inventati o
  anonimizzati.
