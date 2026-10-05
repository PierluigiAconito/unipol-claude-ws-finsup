# Verifica Umana

Log delle review manuali sul testo/funzionalità generate con l'AI, prima di considerarle demo-ready. Richiesto come evidenza dal criterio di valutazione "verifica umana" (vedi [regole-e-valutazione.md](../context/regole-e-valutazione.md)).

## Dove interviene una persona

| Punto | Chi verifica | Come |
|---|---|---|
| Dati estratti dai documenti (RF-01b) | **l'utente finale**, a runtime | schermata di conferma obbligatoria, editabile voce per voce, prima di ogni calcolo (RF-09) |
| Testi AI rivolti all'utente (glossario, spiegazioni) | team | guardrail + skill/subagent come pre-filtro, poi lettura umana: riga in tabella sotto |
| Codice generato con Claude Code | team | review del diff prima del commit + `pytest app` verde |
| Presentazione e numeri mostrati in demo | team | prova completa della demo con i documenti in `app/demo_assets/` |

Regola: le righe di esito le scrive una persona dopo aver controllato davvero. Gli agenti possono preparare il controllo, non firmarlo.

## Log

| Data | Cosa è stato rivisto | Chi | Esito |
|---|---|---|---|
| 2026-10-05 | Bootstrap: guardrail `content_guard.py` (pattern anti-consigli-finanziari) | team | PASS — testato con `pytest`, vedi `app/tests/test_content_guard.py` |

## Pre-filtri preparati dagli agenti (da firmare)

Controlli già eseguiti da una sessione Claude Code: servono a preparare la review umana, non la sostituiscono. Chi verifica legge il testo indicato, compila "Firma umana" e sposta la riga nel Log sopra.

| Data | Cosa | Pre-filtro (agente) | Cosa guardare | Firma umana |
|---|---|---|---|---|
| 2026-10-05 | 16 definizioni riviste del glossario, `KNOWN_TERMS` in `app/finsup/glossary.py` | skill `finsup-copy-check`: consigli PASS, accessibilità PASS. Significato: 2 correzioni già applicate ("Commissione di gestione" vale solo per il conto corrente, ora detto esplicitamente; sigla SEPA spiegata). TFR (può andare a un fondo pensione) e ritenuta d'acconto (20% solo per le collaborazioni occasionali) già precisati. Test: `test_reviewed_definitions_pass_the_guardrail` | correttezza tecnica di franchigia, addizionali, imposta di bollo | |
| 2026-10-05 | 10 definizioni nuove per i documenti reali (QA-35): oneri di sistema, accise, quota rete, quota potenza, POD e PDR, IVA, imponibile, detrazioni, CCNL, scatto di anzianità; "Addebito diretto" ora riconosce anche RID | pre-filtro dell'agente: consigli PASS (hook e test guardrail verdi). Significato: oneri di sistema distinti dalla quota rete, come segnalato in QA-27; accise "di solito" proporzionali ai consumi | aliquote IVA (10%/22%) e definizione di imponibile IRPEF | |
| 2026-10-05 | Testi fissi di `app/main.py`: disclaimer, avviso RF-09, testo e nota 50/30/20 (RF-05), avviso RF-06, proiezione RF-07 | skill `finsup-copy-check`: PASS su tutti e 3 i punti. Nessun imperativo su soldi o spese; 50/30/20 presentato come "termine di paragone, non obiettivo"; RF-06 senza indicazioni su cosa tagliare (verificato anche da `test_negative_savings_highlighted_without_prescriptions`) | leggere le 5 schermate in demo | |
| 2026-10-05 | Estrazione reale dei 5 documenti finali dei due scenari (`app/demo_assets/`, Marco e Alessandra) con Claude Haiku | sessione QA: importi, periodicità e netto in busta corrispondenti ai documenti; doppioni segnalati (stipendio di entrambi, bolletta di Marco), più un falso doppione da ignorare (bollo 2,00 / commissione 2,00, QA-45). Dopo la conferma: Marco −81,56 € (−5,8%), Alessandra +1.132,24 € (34,3%), uguali ai valori attesi in `demo_data.py`. Costo $0.17, 41-97 s a documento (in demo: cache con prewarm) | confrontare in conferma le voci estratte con i documenti; categorie del mutuo e del ristorante (QA-44) | |
