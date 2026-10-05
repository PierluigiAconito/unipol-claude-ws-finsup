# Comando: /qa-review

QA multiprofilo dei deliverable. Ogni profilo è un subagent separato, con contesto isolato e un modello scelto per il compito: punti di vista indipendenti, nessuno influenzato dagli altri, e il thread principale riceve solo i report. Ambito opzionale (es. "solo presentazione", oppure il percorso di una presentazione non ancora nel repo): $ARGUMENTS.

## Profili

| Subagent | Simula | Modello | Prefisso |
|---|---|---|---|
| `qa-faculty` | giudizio soggettivo della giuria | Sonnet | FAC |
| `qa-check-agent` | agente valutatore del portale: requisiti, consegna, pulizia del repo | Sonnet | CHK |
| `qa-graphic-designer` | grafica di presentazione (brand Accenture) e app | Opus | GFX |
| `qa-utente-target` | la persona del Tema 02 che usa l'app; test di comprensione prima e dopo | Sonnet | UT |
| `finsup-copy-reviewer` | conformità dei testi al Tema 02 (niente consigli, significato, accessibilità) | Haiku | (tabella propria) |

## Passi
1. Lancia **in parallelo**, in un unico messaggio, i subagent della tabella. Passa a ciascuno l'ambito ($ARGUMENTS) e, se la presentazione non è ancora in `presentation/`, il suo percorso.
2. Raccogli i report. **Non correggere nulla**: il QA segnala, il team corregge.
3. Unisci i findings in `agents/workflows/qa-findings.md`:
   - **deduplica**: se più profili segnalano la stessa cosa, una sola riga con tutti gli ID (es. `FAC-02 · GFX-01`). La convergenza tra profili alza la priorità
   - ordina per severità; tieni lo stato dei findings già presenti (non riaprire quelli chiusi senza una nuova prova)
   - aggiungi in testa la scorecard faculty e la stima del punteggio del check agent, con la data del giro
4. Rispondi con: i bloccanti, i 5 fix con il miglior rapporto punti/tempo e le domande probabili in Q&A.
