# QA findings: deliverable Hagenthon (Tema 02)

Findings della sessione QA sullo stato della working copy, incluso il codice non ancora pushato. Il QA segnala, il team corregge: quando un finding è risolto, aggiornare lo stato con chi l'ha chiuso e come.

**Metro di giudizio**: regole di consegna (slide "Repository finale"), criteri di valutazione in [regole-e-valutazione.md](../context/regole-e-valutazione.md), vincoli del Tema 02 ([temi-della-sfida.md](../context/temi-della-sfida.md)), specifica in [requisiti-funzionali.md](../../app/docs/requisiti-funzionali.md). Il valutatore automatico legge il repo pubblicato: conta ciò che è scritto, verificabile e **pushato**.

**Severità**: **Bloccante** = viola una regola di consegna o rompe la demo dal vivo · **Alta** = un valutatore lo nota e costa punti · **Media** = indebolisce un criterio · **Bassa** = rifinitura.

**Giri**: giro 1 (QA-01..16), revisione manuale. Giro 2 (QA-17..43), QA multiprofilo con [`/qa-review`](../commands/qa-review.md) più l'estrazione reale dei documenti demo forniti dal team. Giro 3 (QA-44..53), QA finale prima della consegna, sul repo committato. Tutti del 2026-10-05.

---

## Giro 3: QA finale prima della consegna

Eseguito sul repo committato (HEAD `c9fab2d`, poi i fix fino al push finale), con i 5 profili in parallelo e verifiche deterministiche fatte dalla sessione QA.

| Profilo / verifica | Modello | Token | Esito in una riga |
|---|---|---|---|
| `qa-faculty` | Sonnet | ~77k | Soluzione e pattern in crescita (pattern 3 → 4); la presentazione resta il punto debole (2/5) |
| `qa-check-agent` | Sonnet | ~87k | Root conforme, **nessun link rotto**, RF-01..09 tutti implementati e testati; criteri: tecnica alto, gli altri medio per deck e firme mancanti |
| `qa-graphic-designer` | Opus | ~166k | App molto migliorata, 9 difetti da demo (GFX-29..37); deck fuori brand e tagliato |
| `qa-utente-target` | Sonnet (via general-purpose: profilo non registrato nella sessione) | ~90k | Comprensione migliorata su 5 domande su 5, **nessun numero inventato**; 3 testi da chiarire |
| `finsup-copy-reviewer` | Haiku | n.d. | Interrotto da un errore API, ma ha consegnato i findings: "consiglia ≥ 20%" e "oneri di sistema = rete" nel deck (QA-27) |
| Clone pulito + `pip install -r app/requirements.txt` + `pytest app` | n.a. | n.a. | Tutti verdi |
| Estrazione reale end-to-end dei due scenari, dalla cache | Haiku | $0.09 (2 documenti riletti), poi $0 | Ha trovato la regressione QA-46; dopo il fix Marco −81,56 € e Alessandra 1.132,24 €, identici agli attesi |

**Scorecard faculty** (prima del rifacimento del deck): problema 4 · valore 3 · Tema 02 3 · tecnica 4 · uso AI 3 · verifica umana 3 · pattern 4 · presentazione 2. Il deck è stato poi rifatto (QA-17, 18, 26..30, 37), quindi la colonna presentazione va rivalutata.

**Chiuso nel giro**, dalle due sessioni coordinate per messaggio:
- **sviluppo**: QA-44, 45, 46, 47, 49, 50, 51;
- **sessione QA**: QA-03 (verificato), 07, 15, 25, 43, 48 e tutta la presentazione.

**Restano**:
- firme umane in `verifica-umana.md` (QA-09, 4 righe): può metterle solo una persona;
- QA-06 (hook visto bloccare dal vivo);
- QA-14 (numero del team) e nomi del team nel deck (QA-41);
- QA-36 (CF e date 2025 nei documenti demo);
- QA-52 (palette dell'app rispetto al deck), che è una decisione dell'utente.

**Nota sul brand**: la regola di consegna dice solo "brand guidelines Accenture". Palette, font e simbolo `>` vengono dalla skill [`accenture-html-deck`](../skills/accenture-html-deck/SKILL.md), scritta dal team in base al brand pubblico di Accenture: la faculty non ha fornito guidelines. Se arrivano quelle ufficiali, prevalgono.

---

## Giro 2: sintesi del QA multiprofilo

| Profilo (subagent) | Modello | Token del giro | Esito in una riga |
|---|---|---|---|
| `qa-faculty` | Sonnet | ~145k | Soluzione solida, presentazione debole (2/5): mancano struttura agentica e Risk & Clarity nei 5 minuti |
| `qa-check-agent` | Sonnet | ~167k | **Su `origin/main` oggi tutti i criteri valgono "basso"**: il lavoro non è pushato |
| `qa-graphic-designer` | Opus | ~136k | Deck fuori brand e con testo tagliato; app ok ma fragile a 1280×720 e in dark mode |
| `qa-utente-target` | Haiku | ~74k | Comprensione migliorata su 5 domande su 5 (vedi la nota sui limiti) |
| `finsup-copy-reviewer` | Haiku | ~44k | Nessun consiglio nei testi; non ha visto 2 problemi del deck (QA-27) |

In più: estrazione reale dei 4 documenti demo con il codice dell'app, **$0.17** in totale (Haiku).

### Scorecard faculty (simulata)
| Problema e persona | Valore per l'utente | Aderenza Tema 02 | Qualità tecnica | Uso consapevole AI | Verifica umana | Pattern Claude Code | Presentazione |
|---|---|---|---|---|---|---|---|
| 4 | 3 | 3 | 4 | 3 | 3 | 3 | **2** |

### Stima del punteggio oggettivo (check agent)
- **`origin/main` oggi**: basso su qualità tecnica, uso dell'AI, verifica umana e strategia AI; basso/medio sui pattern. Il repo pubblicato è ancora lo scheletro pre-ristrutturazione, con l'hook in `PostToolUse`.
- **Se si pusha la working copy attuale**: sensibilmente più alto su qualità tecnica, token e verifica umana, ma resta bloccato da `presentation/` assente.

### Test di comprensione (utente target)
| Domanda | Prima | Dopo l'app |
|---|---|---|
| Quanto entra al mese? | "circa, confuso" | preciso |
| Quanto esce e per cosa? | "non lo so" | totale + categorie principali dal grafico |
| Quanto mi resta? | "non riesco" | risparmio e tasso |
| Cosa vuol dire TAEG? | "non lo so" | spiegazione corretta dal glossario |
| In quanto tempo 1.000 €? | "impossibile" | mesi dalla proiezione RF-07 |

Va usato come evidenza del "miglioramento tangibile" chiesto dal Tema 02 **solo dopo** una prova umana: il profilo ha inventato alcuni numeri (vedi in fondo, "Limiti emersi").

### ⚠️ Decisione richiesta al team: uno scenario demo unico (QA-21)
Oggi esistono **tre storie diverse**:
1. Before/After del deck: netto 1.509 €, risparmio 159 €, "Giu 2025".
2. App: dati di esempio, `app/demo_assets/`, `app/docs/deliverable-tema02.md` ("Laura", 1.720 €, risparmio 37,46 €).
3. I 4 documenti forniti dal team: persona 1 Marco "basso risparmio", persona 2 Alessandra "alto risparmio", Settembre 2025.

Va scelta **una** storia, e deck, dati di esempio (fallback), deliverable e copione della demo devono usare gli stessi numeri.

### I 5 fix con il miglior rapporto punti/tempo
1. **README riscritto, poi push di tutto** (QA-03 → QA-02). Oggi il valutatore vede lo scheletro.
2. **Presentazione in `presentation/`**:
   - 2 slide nuove: struttura agentica; AI/token/verifica umana (QA-01, QA-18)
   - Risk & Clarity nel flusso principale (QA-26)
   - slide demo sistemata (QA-19)
3. **Restyle brand Accenture del deck** (QA-17): niente CDN (QA-30), testo ≥ 18-20px (QA-29), Before/After non tagliato (QA-28).
4. **Scenario demo coerente** (QA-21): xlsx risalvato (QA-20), persona 1 con le spese (QA-22), stipendio non doppio (QA-23), estrazione caricata prima del pitch (QA-24).
5. **Quick win app**: configurazione Streamlit con tema chiaro, viola e toolbar minima (QA-31), formato italiano (QA-32), ciambella (QA-33). Poche righe, molto visibili in demo.

### Domande probabili in Q&A (dal profilo faculty)
1. "Perché la slide dice BudgetFacile e l'app FinSup?" Va risolto prima (QA-25).
2. "Dove vediamo hook, skill e subagent?" Mostrare `agents/README.md` e la tabella pattern → file, `agents/hooks/` + `.claude/settings.json`.
3. "Come garantite che l'AI non dia consigli?" Mostrare `content_guard.py` usato da hook e app, e `test_glossary.py::test_ai_text_violating_guardrail_is_never_shown`.
4. "Quanto costa e perché Haiku?" Mostrare `uso-token.md`, dopo il fix QA-07 (l'estrazione usa un tetto di $0.30 e costa $0.02-0.07 a documento).
5. "E se il risparmio è negativo?" Ramo RF-06 nel copione demo (QA-16).

---

## Riepilogo

| ID | Sev. | Area | Finding | Fonti | Owner suggerito | Stato |
|---|---|---|---|---|---|---|
| QA-01 | Bloccante | Consegna | `presentation/` non esiste nel repo (il deck è solo in Downloads) | QA · FAC · CHK | collega | chiuso (sessione QA): deck in `presentation/index.html`, rifatto nel giro 3 |
| QA-02 | Bloccante | Consegna | Nulla pushato dopo la ristrutturazione: `origin/main` = scheletro con hook PostToolUse | QA · CHK-07 | team | chiuso: push intermedio `c9fab2d` e push finale a fine giro 3 (sessione QA, su indicazione dell'utente) |
| QA-03 | Bloccante | Consegna | README di root obsoleto; i suoi link a `docs/` si rompono al push | QA · CHK-09 | team | chiuso (sviluppo, 5228100); verificato da CHK al giro 3: nessun link rotto in README, agents/README, CLAUDE.md, workflows e docs |
| QA-17 | Bloccante | Presentazione | Fuori brand Accenture: verde/beige, Segoe UI, nessun `>` | GFX-01/02/03 · FAC-04 | collega | chiuso (sessione QA, giro 3): nero, bianco e viola `#A100FF` (`#BE82FF` per il testo piccolo), Graphik con ripiego Arial, simbolo `>`, secondo la skill `accenture-html-deck` (vedi la nota sul brand in testa) |
| QA-18 | Bloccante | Presentazione | Nessuna slide su struttura agentica, uso AI/token e verifica umana | FAC-03 · CHK-02 · GFX-06 | collega | chiuso (sessione QA, giro 3): 3 slide sul modello agentico (app a runtime; componenti in `agents/`; processo con sessioni parallele, SDD e QA) più 1 su uso dell'AI e verifica umana |
| QA-19 | Bloccante | Presentazione | Slide demo con segnaposto visibile e URL `localhost:3000` (l'app è su 8501) | GFX-05 · FAC-05 · CHK-03 | collega | chiuso (collega): `APP_URL` e etichetta su `localhost:8501`, segnaposto sostituito; verificato da QA |
| QA-20 | Bloccante | Demo | L'estratto conto `.xlsx` della persona 2 non si apre nell'app | QA (estrazione reale) | team | lato app chiuso (sviluppo): lettura fogli con `calamine`, che ignora gli stili; provato sul file della persona 2 (43 righe lette). **Verificato da QA** sui documenti finali: entrambi gli xlsx letti ed estratti correttamente |
| QA-06 | Alta | Pattern | Hook PreToolUse mai visto bloccare in una sessione reale | QA · FAC | team | aperto |
| QA-07 | Alta | Token | I documenti sui token non corrispondono al codice dell'estrazione | QA · FAC · CHK | sessione QA | chiuso (sessione QA, 4d57e55): `uso-token.md` e `uso-ai.md` riportano tool minimi, tetti 0.05/0.30, cache e costi misurati |
| QA-21 | Alta | Demo | Tre scenari demo diversi tra deck, app e documenti: serve una decisione | GFX-10 · FAC · QA | team | **deciso (team)**: 2 scenari, **Marco = basso risparmio** (busta paga + bolletta + estratto conto da creare, QA-22) e **Alessandra = alto risparmio** (busta paga + estratto conto). Laura esce dalla demo. **fatto (sessione QA, su incarico dell'utente)**: 5 documenti finali in `app/demo_assets/`, asset e generatore di Laura rimossi, `demo_data.SCENARIOS` con valori attesi e test, `deliverable-tema02.md` e copione aggiornati, prewarm eseguito. Punto 4 superato: il pulsante dei dati di esempio è stato tolto dall'app (decisione dell'utente) **Punto 6 chiuso** (giro 3): il Before/After del deck usa Marco |
| QA-22 | Alta | Demo | Persona 1 "basso risparmio" esce al **90,7%** di risparmio | QA (estrazione reale) | team / sviluppo | chiuso (team): estratto conto di Marco fornito; verificato da QA: risparmio −81,56 € (−5,8%), ramo RF-06 visibile |
| QA-23 | Alta | Demo / app | Persona 2: stipendio contato due volte, entrate 5.872,68 invece di 3.296,34 | QA (estrazione reale) | team + sviluppo | lato app chiuso (sviluppo): avviso "possibile doppione" in conferma RF-09 (stesso importo da file diversi), calcolato sui valori modificati in diretta; `possible_duplicates` + test. **Verificato da QA** sui documenti finali: segnalati lo stipendio di entrambi e la bolletta di Marco; vedi però il falso positivo QA-45 |
| QA-24 | Alta | Demo | Estrazione da 41 a 97 s per documento: troppo per un pitch di 5 minuti | QA (estrazione reale) | team + sviluppo | lato app chiuso (sviluppo): cache su disco per hash di file + prompt + schema, più `app/scripts/prewarm_extraction.py` da lanciare prima del pitch; test sulla cache. **Verificato da QA**: prewarm sui 5 documenti finali, 4 già in cache e 1 letto ($0.025) |
| QA-25 | Alta | Coerenza | Nome del prodotto: "BudgetFacile" nel deck, "FinSup" in app e repo | FAC-02 · GFX-11 · CHK-01 | team | chiuso (sviluppo + sessione QA): BudgetFacile in app, README e deck; CLAUDE.md e agents/README dichiarano che FinSup è il nome interno del progetto e del package |
| QA-26 | Alta | Tema 02 | Risk & Clarity Note solo in appendice, fuori dai 5 minuti | FAC-01 · GFX-06 | collega | chiuso (sessione QA, giro 3): Risk & Clarity Note nel flusso principale (slide 10), con il link al repo |
| QA-27 | Alta | Tema 02 | Testi del deck: "50/30/20 consiglia ≥ 20%", "oneri di sistema = rete", "qualsiasi formato" | GFX-12 · QA | collega | chiuso (sessione QA, giro 3): testi riscritti ("termine di paragone", definizione di oneri di sistema dal glossario rivisto, "PDF o Excel"); i testi del deck passati da `content_guard`, 0 violazioni |
| QA-28 | Alta | Presentazione | Before/After: i box ad altezza fissa tagliano totale bolletta e glossario | GFX-07 | collega | chiuso (sessione QA, giro 3): Before/After con estratti reali dei documenti di Marco e i numeri prodotti dall'app; box ad altezza libera, verificati a 1280×720 |
| QA-29 | Alta | Presentazione | Testo troppo piccolo per il proiettore (12-13px) e deck che non scala a 1920 | GFX-08/09 | collega | chiuso (sessione QA, giro 3): palco fisso 1600×900 scalato sullo schermo, stesso layout a 1280 e a 1920; testo minimo circa 13,6px a 1280 e 20px a 1920, corpo 18-24px |
| QA-30 | Alta | Presentazione | Icone da CDN: offline spariscono | GFX-04 · FAC-04 · CHK-04 | collega | chiuso (sessione QA, giro 3): nessuna risorsa remota, icone sostituite dal simbolo `>` |
| QA-31 | Alta | App UI | Tema non fissato (dark mode illeggibile), pulsanti rossi, toolbar di sviluppo visibile | GFX-17/21/23 | sviluppo | chiuso (sviluppo): `app/.streamlit/config.toml`, letto accanto allo script anche avviando dalla root (Streamlit 1.65); tema chiaro con i colori, il font e gli angoli della presentazione (su indicazione dell'utente, non il viola Accenture), toolbar minima; palette dei grafici allineata al deck e rivalidata. `.gitignore` ora ignora solo `secrets.toml` |
| QA-32 | Alta | App UI | Importi non in formato italiano in tabelle e assi | GFX-18 | sviluppo | parziale (sviluppo): assi in formato italiano (1.800). Nelle tabelle editabili resta "1620.00 €", perché i formati localizzati di Streamlit seguono la lingua del browser (in inglese: "€1,620.00") |
| QA-33 | Alta | App UI | Ciambella tagliata e legenda sovrapposta a 1280×720 | GFX-19 | sviluppo | chiuso (sviluppo): raggio 110, legenda sotto su 2 colonne, colonna più larga (3:2); verificato a 1280×720 |
| QA-09 | Media | Verifica umana | Definizioni del glossario "riviste a mano" senza firma nel log | QA · FAC | team | aperto, ambito esteso (FAC-09 · CHK-13): 4 righe di pre-filtro in `verifica-umana.md` senza firma umana (glossario, testi fissi, estrazione reale). Può firmarle solo una persona |
| QA-34 | Media | App / prompt | Bolletta estratta in 13 righe (IVA e accise come spese separate) | QA (estrazione reale) | sviluppo | chiuso (sviluppo): regola bollette in `agents/prompts/estrazione.md` (una voce per servizio, IVA inclusa, più bollo e mora). **Verificato da QA**: bolletta di Marco in 5 righe, totale 130,95 € invariato |
| QA-35 | Media | Glossario | Offline mancano le definizioni dei termini dei documenti demo reali | QA (estrazione reale) | sviluppo | chiuso (sviluppo): 10 definizioni nuove e RID riconosciuto; firma umana da fare (riga in `verifica-umana.md`) |
| QA-36 | Media | Dati demo | Dati in formato reale nel repo pubblico (P.IVA valida, CF, targa); date 2025 | QA | team | in parte chiuso (sessione QA): P.IVA valida di Innovatech sostituita con una non valida nella copia in `app/demo_assets/` (il resto del PDF è invariato); le altre P.IVA e l'IBAN di Marco hanno checksum non validi. **Resta** (decisione del team): CF in formato reale, date settembre 2025 |
| QA-37 | Media | Presentazione | Contrasti sotto AA, gerarchia incoerente, 4 passi nel deck contro 3 nell'app | GFX-13/14/15 | collega | chiuso (sessione QA, giro 3): testo secondario `#B3B3B3` e viola chiaro `#BE82FF` su nero (sopra AA); 3 passi come nell'app |
| QA-38 | Media | App UI | Tabelle con doppio scroll, risultati lunghi 4,4 schermate, messaggi tecnici all'utente | GFX-20/24/25 | sviluppo | chiuso (sviluppo): tabelle alte quanto le righe e con larghezze in px (niente scroll a 1280); risultati in 5 schede; costi ed errori della CLI in "Dettagli tecnici" |
| QA-39 | Media | App UI | Disclaimer duplicato in due box | GFX-22 | sviluppo | chiuso (sviluppo): una volta sola, sotto il titolo di ogni passo (la sidebar si può chiudere) |
| QA-40 | Media | Comprensione | Colonne Tipo/Periodicità non spiegate, 50/30/20 denso, glossario con termini assenti | UT-01/02/04/05 · copy | sviluppo | chiuso (sviluppo): `help` sulle colonne, 50/30/20 in 3 numeri in grassetto, ogni termine indica dove compare. I termini presenti solo nel testo dei documenti restano, perché RF-04 li include ("termini incontrati nei documenti caricati") |
| QA-14 | Bassa | Coerenza | Team di 3 o di 2 persone? | QA · FAC | team | aperto |
| QA-15 | Bassa | Pattern | Skill `accenture-html-deck` diversa dal deck consegnato | QA · FAC · CHK | collega + sessione QA | chiuso (sessione QA, giro 3): il deck segue la skill (brand, scaletta, nessuna risorsa remota, nessun segnaposto) |
| QA-41 | Bassa | Presentazione | "Hagenthon 2025", nomi del team mancanti, nessun link al repo, navigazione dispersa | FAC-06 · CHK-05/06 · GFX-16 | collega | in parte (sessione QA, giro 3): anno 2026, link al repo in copertina e in chiusura, navigazione unica; **mancano i nomi del team** (da inserire dal team) |
| QA-42 | Bassa | App UI | Uploader in inglese, colori delle categorie, barre senza etichette, palette diversa dal deck | GFX-26/27/28 | sviluppo | parziale (sviluppo): "Altro" in grigio, % sulle barre 50/30/20, primario viola come il brand. I testi dell'uploader non sono traducibili da Streamlit |
| QA-43 | Bassa | Pulizia | Prompt orfano `agents/prompts/spiega_concetto.md` | CHK-08 | sessione QA | chiuso (sessione QA): file rimosso, nessun riferimento nel codice |
| QA-44 | Media | App / prompt | L'estrazione mette il mutuo in Debiti/finanziamenti e il ristorante in Svago; la spec §4.2 li vuole in Abitazione e Alimentari | QA (estrazione reale) | sviluppo | chiuso (sviluppo); **verificato da QA** al giro 3 sull'estrazione reale: mutuo in Abitazione, ristorante in Alimentari |
| QA-45 | Media | App | Falso doppione: in Marco "Imposta di bollo 2,00 € (bolletta)" e "Commissione di gestione 2,00 € (estratto conto)" segnalati come possibile doppione solo per l'importo uguale | QA (estrazione reale) | sviluppo | chiuso (sviluppo); **verificato da QA** al giro 3: bollo e commissione da 2 € restano entrambi |
| QA-46 | Alta | Demo / app | Regressione: con il nuovo tipo "una tantum" l'estrazione segnava "Acquisto libri 45 €" anche come annuale, e Alessandra usciva a 1.173,49 € invece di 1.132,24 € | QA (end-to-end giro 3) | sviluppo | chiuso (sviluppo, 97b88ad): una voce una tantum conta per intero nel mese; **verificato da QA** sull'estrazione reale |
| QA-47 | Media | App | Al secondo caricamento i doppioni venivano ricalcolati sulla lista già ripulita: rischio di togliere il bollo da 2 € o la commissione da 2 € | QA (end-to-end giro 3) | sviluppo | chiuso (sviluppo, bce621b): si considerano solo le coppie con una voce del nuovo caricamento; **verificato da QA**: 0 voci tolte al secondo passaggio |
| QA-48 | Media | Coerenza | Percentuali per categoria di Marco nel deliverable diverse da quelle live (bar in Alimentari, mora in Altro) | QA (end-to-end giro 3) | sessione QA | chiuso (sessione QA, b7a29d9): `demo_data` e deliverable allineati ai numeri live; totali invariati |
| QA-49 | Media | Comprensione | Testi dei risultati: "risparmio di −81,56 € mantenendo il ritmo", tipi di spesa non spiegati sotto le metriche, necessità oltre il 100% | UT-01/02/03 | sviluppo | chiuso (sviluppo, bce621b); verificato da QA nei testi di `main.py` |
| QA-50 | Alta | App | "Aggiungi una voce": il Tipo restava "variabile" anche con Abitazione (percentuali fisse e variabili falsate); i campi non si azzeravano | GFX-33 | sviluppo | chiuso (sviluppo, c935325): chiave del Tipo legata alla categoria, campi azzerati; 2 test |
| QA-51 | Media | App UI | Righe modello a 0 €, "None" nella colonna di origine, reset senza conferma, risultati sotto la piega, box blu fuori palette, etichette 50/30/20 arrotondate | GFX-30/31/32/34/36/37 | sviluppo | chiuso (sviluppo, c935325) |
| QA-52 | Media | Coerenza | Il deck ora è sul brand Accenture (viola), l'app resta verde e beige | GFX-29 | utente | aperto: **decisione dell'utente**. Token pronti nel report GFX (primario `#A100FF`, sfondo bianco, testo nero, Arial), circa 15 minuti di sviluppo |
| QA-53 | Bassa | Demo | Con soli dati inseriti a mano il glossario dice "nessun termine riconosciuto" | GFX-35 | team | accettato: la demo si fa con i documenti dopo il prewarm, dove il glossario si riempie |
| QA-04 | Alta | Qualità tecnica | `app/requirements.txt` incompleto | QA | sviluppo | chiuso (sviluppo), verificato da QA |
| QA-05 | Alta | Requisiti | `app/main.py` era lo scheletro | QA | sviluppo | chiuso (sviluppo), verificato da QA e CHK (matrice RF) |
| QA-08 | Media | Tema 02 | 50/30/20: "Altro" tra i desideri | QA | sviluppo | chiuso (sviluppo), verificato da QA |
| QA-10 | Media | Token | Glossario: fino a 12 chiamate CLI | QA | sviluppo | chiuso (sviluppo), verificato da QA |
| QA-11 | Media | Qualità tecnica | Nessun test per estrazione e glossario | QA | sviluppo | chiuso (sviluppo), verificato da QA |
| QA-12 | Media | Coerenza | Riferimento errato in `ai_client.py` | QA | sviluppo | chiuso (sviluppo), verificato da QA |
| QA-13 | Bassa | Tema 02 | Voci bloccate scartate in silenzio | QA | sviluppo | chiuso (sviluppo), verificato da QA |
| QA-16 | Bassa | Demo | Ramo RF-06 non visibile con i dati demo | QA | sviluppo | chiuso (sviluppo): chiuso: con lo scenario di Marco il ramo RF-06 si vede senza ritocchi (−81,56 €); test `test_low_savings_scenario_shows_negative_savings` |

---

## Dettaglio dei findings aperti

### QA-01: `presentation/` non esiste nel repo
- **Regola**: repo in `app/`, `agents/`, `presentation/`; presentazione **HTML** con **brand Accenture**, sulla soluzione **e** sulla struttura agentica; pushata entro il freeze.
- **Stato**: il deck esiste (`BudgetFacile`, 6 slide più 4 di appendice) ma solo in `Downloads/presentation.html`.
- **Fix**: salvarlo come `presentation/index.html`, con gli screenshot in `presentation/assets/`, dopo i fix QA-17..19 e QA-25..30.

### QA-02: Nulla pushato
- **Stato**: ultimo push = `b7f358b`. In locale ci sono `0a5b50a` (ristrutturazione) e `838eb1e` (sviluppo). Non committati: le modifiche della sessione QA (`CLAUDE.md`, `agents/instructions|subagents|commands|workflows`, `agents/README.md`, rimandi in `.claude/`) e i file condivisi `verifica-umana.md`, `qa-findings.md`, `.claude/launch.json`.
- **Aggravante (CHK-07)**: su `origin/main` l'hook è ancora `PostToolUse` con percorso relativo, quindi la "evidenza pattern" pubblicata non corrisponde a ciò che i documenti promettono.
- **Fix**: README prima (QA-03), poi commit dei path espliciti di ogni sessione, poi push da parte di una persona.

### QA-03: README di root obsoleto
- **File**: `README.md`. Dice "in costruzione", linka `docs/`, che sparisce col push (CHK-09), e non cita `app/`, `agents/`, `presentation/`.
- **Fix** (va fatto **prima** del push):
  1. Pitch in 2 righe e vincolo "educazione, non consulenza".
  2. Avvio e test.
  3. Struttura a 3 cartelle, e perché ci sono `CLAUDE.md` e `.claude/`.
  4. Tabella **criterio → file che lo dimostra**.
  5. Link a `app/docs/deliverable-tema02.md` e a `presentation/`.

### QA-17: Deck fuori brand Accenture (GFX-01/02/03, FAC-04)
- **Dove**: `:root` (righe 9-24), `body` (27), `.mono`, `.quote-mark`, bullet e frecce di tutte le slide.
- **Fix**:
  - Colori: `--bg:#000000; --text:#FFFFFF; --muted:#B3B3B3; --acc:#A100FF`. Testo piccolo viola in `#BE82FF` (7,8:1 sul nero). Card `#0D0D0D` con bordo `#262626`. Pannelli in `#460073`.
  - Font: `Graphik, Arial, Helvetica, sans-serif`; per il codice `ui-monospace, Consolas, monospace`.
  - `>` in `#A100FF` come bullet, freccia di flusso ed eyebrow. Eliminare verde, beige e Segoe UI.

### QA-18: Nessuna slide sulla struttura agentica (FAC-03, CHK-02, GFX-06)
- **Regola**: `presentation/` deve presentare "la soluzione **e** la struttura agentica". Uso consapevole dell'AI, verifica umana e pattern sono criteri di valutazione.
- **Fix**: due slide.
  1. **Struttura agentica**: mappa di `agents/` (rules, hook, skill, subagent, comandi, prompt) e la "doppia rete" sul vincolo, da `agents/README.md`.
  2. **AI · Python · persona**: dove l'AI e dove no (`strategia-ai.md`), numeri misurati (`uso-token.md`, dopo QA-07), punti di verifica umana (RF-09, log firmato, QA multiprofilo).

### QA-19: Slide demo con segnaposto e porta sbagliata (GFX-05, FAC-05, CHK-03)
- **Dove**: `.demo-body-f` (343-349), `#demo-url-lbl` (341), `APP_URL` (462).
- **Problema**: in proiezione si legge "L'app verrà mostrata qui. Aggiorna APP_URL…"; "Apri app" punta a `localhost:3000`, quindi apre una pagina vuota.
- **Fix**: `APP_URL='http://localhost:8501'` e testo segnaposto rimosso; nel riquadro, uno screenshot reale dei risultati come fallback.

### QA-20: L'estratto conto `.xlsx` della persona 2 non si apre nell'app
- **Prova** (estrazione reale con `finsup.extraction`): `file non leggibile (CellStyle.__init__() got an unexpected keyword argument 'applyNumFmt')`. Il file ha attributi di stile non standard (`applyNumFmt`) e nessuno stile di default; openpyxl, usato da `pd.read_excel`, lo rifiuta.
- **Verificato**: con lo stile corretto l'estrazione funziona (20 voci giuste, periodicità trimestrale e annuale riconosciute).
- **Fix**: aprire e risalvare il file in Excel o LibreOffice (o rigenerarlo con openpyxl) e riprovarlo nell'app. Opzionale per lo sviluppo: in `extraction.py`, se openpyxl fallisce, rileggere solo i valori ignorando gli stili.

### QA-21: Tre scenari demo diversi (decisione del team)
- **Dove**: deck (slide 5), `app/finsup/demo_data.py` + `app/demo_assets/` + `app/docs/deliverable-tema02.md`, documenti in `Downloads/persona*`.
- **Rischio**: la giuria confronta slide e demo e vede persone, cifre, categorie e date diverse (GFX-10: anche "Casa & utenze" contro "Abitazione").
- **Fix**: scegliere uno scenario. Documenti in `app/demo_assets/`, "dati di esempio" che riproducono gli stessi numeri (fallback se l'estrazione non va), Before/After = **screenshot reale** dell'app, `deliverable-tema02.md` e copione allineati.
- **Decisione del team**: due scenari, **Marco (basso risparmio)** e **Alessandra (alto risparmio)**. Laura esce dalla demo.
- **Criteri di accettazione** (li verifica il giro QA finale):
  1. **Documenti** in `app/demo_assets/`: Marco = busta paga + bolletta + **estratto conto nuovo** (QA-22); Alessandra = busta paga + estratto conto. Nessun altro set di persone nel repo: gli asset di Laura vanno rimossi, insieme ai test e ai dati che li citano, per non lasciare una terza storia.
  2. **Estratto conto di Marco**: stesso mese della busta paga; addebiti realistici (affitto, spesa, una rata con TAEG, abbonamenti, commissioni); risparmio finale **basso** (pochi punti percentuali) oppure **negativo**, così da mostrare RF-06 senza ritocchi. Se contiene l'accredito dello stipendio e l'addebito della bolletta, l'avviso "possibile doppione" deve segnalarli entrambi.
  3. **Numeri attesi** di entrambi gli scenari (entrate, uscite, risparmio, tasso, dopo aver tolto i doppioni) scritti in `app/docs/deliverable-tema02.md` e verificati da un test.
  4. **"Dati di esempio"**: un fallback per **ciascuno** dei due scenari, con gli stessi numeri attesi, se l'estrazione non va durante il pitch.
  5. **Dati fittizi** (QA-36): P.IVA, CF, IBAN e targhe mascherati o non validi; date coerenti tra i documenti (meglio settembre 2026).
  6. **Deck**: la slide demo nomina i due scenari; il Before/After usa screenshot reali di uno dei due (QA-28).
  7. **Prima del pitch**: `app/scripts/prewarm_extraction.py` lanciato su tutti i documenti dei due scenari (QA-24).

### QA-22: Persona 1 "basso risparmio" esce al 90,7%
- **Prova**: busta paga → +1.408,73; bolletta → −130,95 (le uniche uscite). Risparmio 1.277,78 €, tasso **90,7%**.
- **Causa**: nessun documento porta affitto, spesa o rate. Inoltre, dopo l'upload, `_merge` scarta le righe-modello a zero del form.
- **Fix**: aggiungere un documento di spese per la persona 1 (estratto conto o foglio spese), oppure prevedere nel copione l'inserimento manuale di 3-4 voci nella conferma (mostra anche RF-01a + RF-09).

### QA-23: Persona 2, stipendio contato due volte
- **Prova**: la busta paga dà +2.576,34 e l'estratto conto dà di nuovo +2.576,34 ("Accredito stipendio"). Entrate **5.872,68** invece di 3.296,34; risparmio 63% invece di circa 34%.
- **Fix app** (sviluppo): nella conferma RF-09, segnalare le voci con lo stesso importo provenienti da file diversi ("possibile doppione: tienine una").
- **Fix copione**: caricare solo l'estratto conto, oppure togliere il doppione in conferma come dimostrazione di RF-09.

### QA-24: Estrazione troppo lenta per un pitch di 5 minuti
- **Misure**: busta paga 41-57 s, bolletta 94 s, estratto conto 97 s. Due file in parallelo richiedono circa 100 s.
- **Fix**:
  - Caricare i documenti **prima** del pitch e presentare dalla sessione già pronta.
  - Oppure cache su disco per hash del file (sviluppo).
  - Tenere i "dati di esempio" come piano B.

### QA-25: Nome del prodotto (FAC-02, GFX-11, CHK-01)
- "BudgetFacile" in `<title>`, nella copertina e in A.2; "FinSup" in app, `CLAUDE.md` e `agents/`. **Fix**: un solo nome ovunque.

### QA-26: Risk & Clarity solo in appendice (FAC-01, GFX-06)
- È uno dei tre deliverable del Tema 02 e oggi si raggiunge solo con "Annex →". **Fix**: versione condensata in una slide principale; il dettaglio resta in appendice per il Q&A.

### QA-27: Testi del deck da correggere
- Slide 5, riga 323, "Benchmark 50/30/20 **consiglia** ≥ 20%": formulazione prescrittiva, mentre l'app dice "non un obiettivo". Proposta: "Riferimento 50/30/20: 20% delle entrate al risparmio".
- Slide 5, glossario, "Oneri di sistema = spese per rete e incentivi": inesatto. La rete è un'altra voce (nella bolletta demo: "canone di distribuzione, quota rete"); gli oneri di sistema finanziano costi generali del sistema elettrico, come gli incentivi alle rinnovabili.
- Slide 4, passo 1, "PDF o XLS… **qualsiasi formato**": contraddittorio, i formati accettati sono solo PDF e XLS/XLSX.
- Il pre-filtro `finsup-copy-reviewer` li aveva promossi: serve la lettura di una persona, da firmare in `verifica-umana.md`.

### QA-28: Before/After tagliato (GFX-07)
- `.ba-box { height:280px; overflow:hidden }`: nel box "Prima" mancano 72px ("IVA 22%", "Totale bolletta"); nel box "Dopo" il glossario si riduce a una linea.
- **Fix**: `min-height` con `overflow:visible`, oppure meno righe con mono a 16px. Meglio ancora screenshot reali (QA-21).

### QA-29: Leggibilità da proiettore e scala (GFX-08/09)
- Corpo 12-13px, mono 10,5px, etichette 10-11px; a 1920×1080 il contenuto resta largo 1280 e occupa una fascia di circa 400px.
- **Fix**: card ≥ 20px, didascalie ≥ 18px, eyebrow 14px; stage fisso 1280×720 scalato via JS al resize.

### QA-30: Icone da CDN (GFX-04, CHK-04)
- `<link>` a `cdn.jsdelivr.net`: con il CDN disattivato le icone spariscono e lasciano vuoti nelle card. **Fix**: SVG inline, oppure solo il `>`.

### QA-31: App, tema e controlli di sviluppo (GFX-17/21/23)
- **Problemi**:
  - Il tema segue il sistema operativo: in scuro le etichette dei valori (`LABEL_INK #52514e`) sono a 2,4:1 e il disclaimer a circa 3,8:1.
  - I pulsanti primari sono rossi `#FF4B4B`.
  - In demo si vedono "Deploy" e "Rerun".
- **Fix**: configurazione Streamlit con `[theme] base="light"`, `primaryColor="#A100FF"`, `textColor="#000000"`, `[client] toolbarMode="minimal"`, `[server] runOnSave=false`.
- **Attenzione**: `.streamlit/` è in `.gitignore`, e una `.streamlit/` in root aggiunge una cartella alla struttura. Due strade:
  - `app/.streamlit/config.toml`, avviando da `app/` (`cd app && streamlit run main.py`), con `.gitignore` che ignora solo `secrets.toml`;
  - oppure le stesse opzioni come flag di `streamlit run`.

### QA-32: Formato numerico (GFX-18)
- Nelle tabelle editabili si legge "1620.00 €", accanto all'anteprima "1.720,00 €"; sugli assi "1,200". **Fix**: formato localizzato nelle `NumberColumn`; sugli assi `labelExpr` che usa il punto come separatore delle migliaia.

### QA-33: Ciambella a 1280×720 (GFX-19)
- `outerRadius 130` e la legenda a destra non entrano nella colonna da 373px. **Fix**: legenda in basso su 2 colonne, `outerRadius=110`, oppure grafico a tutta larghezza.

### QA-06: Hook mai visto bloccare in una sessione reale
- Lo script è corretto (test in `app/tests/test_hook.py`). Nella sessione QA però gli hook di progetto non risultano attivi, e su `origin/main` c'è ancora la vecchia configurazione (QA-02).
- **Fix**: dopo il push, aprire una sessione Claude Code nuova, chiedere di scrivere in `app/` una frase con un consiglio d'investimento, verificare il blocco e firmare l'esito in `verifica-umana.md`.

### QA-07: Documenti sui token da allineare al codice
- **File**: `agents/workflows/uso-token.md`, `agents/instructions/uso-ai.md` (sessione QA, non committati). Dicono "$0.05 e nessun tool su ogni chiamata".
- **Dati misurati**:
  - Estrazione: tetto $0.30 e timeout 180 s per documento, tool Read solo sulla cartella degli upload (`--add-dir`), `--json-schema`. Senza almeno un tool, lo structured output viene ignorato.
  - Costo reale: $0.014-0.023 sui documenti di `app/demo_assets/` (48 s in parallelo); $0.019-0.066 sui documenti persona (41-97 s).
  - Glossario: 16 termini noti a 0 token, gli altri in una sola chiamata.
  - Accorgimento per Windows: `claude.CMD` tronca gli argomenti al primo a-capo, quindi il prompt passa via stdin.

### QA-09: Firma umana sulle definizioni del glossario
- Pre-filtro pronto nella sezione "Pre-filtri preparati dagli agenti" di `verifica-umana.md`. Manca solo la firma di una persona.

### QA-34: Bolletta estratta in 13 righe
- **Prova**: il totale torna (130,95), ma la conferma RF-09 mostra 13 righe: quota energia, potenza, rete, accise, IVA 10%, gas, IVA 22%… Per il target è il contrario di "semplificare".
- **Fix**: regola in `agents/prompts/estrazione.md` per le bollette: una voce per servizio (luce, gas, internet, IVA inclusa) più gli oneri accessori (bollo, mora).

### QA-35: Glossario offline incompleto per i documenti reali
- **Termini rilevati dall'estrazione e senza definizione di riserva**: oneri di sistema, accise, quota rete, RID, POD/PDR, detrazione, base imponibile, CCNL, scatto di anzianità. Inoltre "RID" non è riconosciuto dal pattern dell'SDD.
- **Rischio**: senza CLI questi termini spariscono dal glossario.
- **Fix**: definizioni riviste per i termini dello scenario scelto (QA-21), firmate in `verifica-umana.md`.

### QA-36: Dati demo in formato reale nel repo pubblico
- **Problemi**:
  - P.IVA `11342780019` (Innovatech): checksum **valido**, potrebbe appartenere a una società reale.
  - Codici fiscali in formato valido, derivati da nome, data e luogo: un omonimo reale avrebbe lo stesso codice.
  - Targa in formato valido; IBAN della persona 1 con checksum non valido (ok); IBAN della persona 2 = IBAN d'esempio noto (ok).
- **Fix**: mascherare, per esempio "P.IVA 00000000000 (fittizia)" e "CF XXXXXX00X00X000X".
- **Rifiniture**:
  - Date "Settembre 2025", ma la demo è nel 2026.
  - Interessi di mora: 0,75 € per 12 giorni al 2,5% implicano una fattura da circa 900 €, non da 130 €.
  - Nel foglio Excel "Saldo finale (30/09)" ha il valore vuoto.

### QA-37: Coerenza stilistica del deck (GFX-13/14/15)
- **Problemi**:
  - Contrasti misurati 1,8-2,7:1 (nota "Valori fittizi", etichette annex, freccia verde).
  - h2 a 38px contro 30px.
  - Le garanzie in A.3 sono in rosso, colore che segnala un errore.
  - 4 passi nel deck contro 3 nell'app; connettori quasi invisibili.
- **Fix**: dentro il restyle QA-17, con 3 passi etichettati come nell'app.

### QA-38: App, usabilità (GFX-20/24/25)
- **Problemi**:
  - Tabella "Uscite" con doppio scroll a 1280: "Ogni quanto" e "Da dove arriva" tagliate, riga "+" nascosta.
  - Pagina dei risultati lunga 3.176px.
  - Costi in "$", percorsi ed errori grezzi della CLI mostrati all'utente.
- **Fix**:
  - Altezza della tabella proporzionale alle righe e colonne strette.
  - `st.tabs` (Riepilogo · 50/30/20 · Parole tecniche · Obiettivo).
  - Dettagli tecnici in un expander; errori come `st.warning` in parole semplici.

### QA-39: Disclaimer duplicato (GFX-22)
- Compare in sidebar e sotto il titolo, in due box da 4-5 righe. **Fix**: una volta sola, ma **sempre visibile** (vincolo di dominio): sidebar oppure `st.caption` sotto il titolo.

### QA-40: Comprensione per l'utente target (UT-01/02/04/05, copy reviewer)
- **Problemi**: colonne "Tipo" e "Ogni quanto" senza spiegazione; testo 50/30/20 denso; "come è stato calcolato" nascosto nell'expander; glossario con termini assenti dai dati confermati (es. TAN, TARI).
- **Fix**: `help` sulle colonne; 50/30/20 in tre numeri in grassetto; anteprima della formula; glossario filtrato sulle voci confermate.

### QA-14, QA-15, QA-41, QA-42, QA-43 (bassa)
- **QA-14**: `regole-e-valutazione.md` dice team da 3, `progetto.md` dice 2.
- **QA-15**: ora che il deck esiste, la skill descrive un'altra presentazione. Il brand è una regola di consegna (QA-17): adattare il deck al brand e la scaletta della skill al deck, oppure rimuovere la skill.
- **QA-41**: anno 2025 in copertina, "Accenture Team" senza nomi, nessuna chiusura con il link al repo, navigazione dispersa, contatore "A0 / 3".
- **QA-42**: testi dell'uploader in inglese; due verdi tra le categorie e "Altro" in rosso (sembra un allarme); barre 50/30/20 senza etichette di valore; nessun colore in comune tra app e deck.
- **QA-43**: `agents/prompts/spiega_concetto.md` non è più usato da nessun modulo.

---

## Limiti emersi negli strumenti di QA (giro 3)
- **Profilo non registrato**: `qa-utente-target` non risultava tra i subagent della sessione. È stato lanciato come agente generico con la stessa definizione, su Sonnet.
- **Utente target su Sonnet, con i numeri verificati in mano**: nessun importo inventato, a differenza del giro 2 su Haiku. La definizione ora lo prescrive.
- **`finsup-copy-reviewer`**: interrotto da un errore API dopo aver prodotto la tabella dei findings, che è stata comunque usata.
- **Il QA statico non vede le regressioni dei dati**: QA-46, QA-47 e QA-48 sono emersi solo dall'estrazione reale end-to-end, che va rifatta a ogni cambio di prompt o schema.

## Limiti emersi negli strumenti di QA (giro 2)
- **Registrazione dei subagent**: i profili nuovi in `.claude/agents/` sono stati riconosciuti solo a giro avviato. Il giro 2 è stato quindi eseguito con agenti generici, con la **stessa definizione** e lo **stesso modello** di ciascun profilo. Dal prossimo giro `/qa-review` li usa direttamente.
- **`finsup-copy-reviewer` (Haiku)**: ha promosso i testi di QA-27. Il pre-filtro non sostituisce la persona. Valutare in `content_guard` un pattern per i verbi prescrittivi in terza persona ("consiglia", "raccomanda", "suggerisce di").
- **`qa-utente-target` (Haiku, solo sorgente)**: ha inventato alcuni numeri, per esempio un'anteprima di 1.683,24 € contro 1.682,54 € (stessa funzione `compute_budget` nel codice) e una rata di 145 € contro i 185 € dei dati. Il test di comprensione regge nella sostanza, ma i numeri vanno presi da una prova reale. Prossimo giro: farlo lavorare sull'app avviata, o su Sonnet.
- **Costo del giro 2**: circa 566k token di subagent, ciascuno nel proprio contesto; al thread principale sono tornati solo i report. Estrazione reale: $0.17.

## Da ricontrollare al freeze (passaggio QA finale)
- [x] Tutti i Bloccanti e gli Alta chiusi o motivati (giro 3: resta QA-06, Alta, motivato: hook testato, non ancora visto bloccare dal vivo)
- [x] `pytest app` verde da un clone pulito con `pip install -r app/requirements.txt`
- [x] Root: solo `app/`, `agents/`, `presentation/`, `README.md`, più i file richiesti da Claude Code (`CLAUDE.md`, `.claude/`, `.gitignore`)
- [x] Link relativi di `README.md` e `agents/README.md` tutti funzionanti
- [x] Ogni affermazione di README e presentazione (numeri, componenti, "blocca", "rivisto a mano") ha un file o una riga di log che la prova
- [x] Demo provata end-to-end con i documenti dello scenario scelto, con la CLI **e** senza (fallback)
- [ ] `git status` pulito e `git log origin/main` contiene tutto
