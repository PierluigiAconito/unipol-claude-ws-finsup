# Comando: /demo-ready

Checklist pre-freeze. Esegui i passi in ordine e alla fine riporta un riepilogo PASS/FAIL per ciascuno. Non correggere nulla in automatico: segnala e basta. Ambito opzionale: $ARGUMENTS.

1. **Test**: `pytest app -q`. Riporta il numero di test passati o falliti.
2. **Struttura di consegna**: in root devono esistere `app/`, `agents/`, `presentation/` e `README.md`, senza altre cartelle di progetto visibili (le dotfile dell'harness sono ammesse). `presentation/` deve contenere un file `.html`.
3. **Guardrail sui prompt**: per ogni file in `agents/prompts/` esegui `finsup.content_guard.find_violations` (da `app/`) e riporta le violazioni.
4. **Review dei testi**: delega al subagent `finsup-copy-reviewer` i file in `agents/prompts/` e `app/main.py`. Riporta la sua tabella così com'è.
5. **Riferimenti**: controlla che i link relativi in `README.md` e `agents/README.md` puntino a file esistenti.
6. **Verifica umana**: elenca le funzionalità con testo rivolto all'utente che non hanno ancora una riga in `agents/workflows/verifica-umana.md`. **Non aggiungere righe tu**: chiedi a una persona del team di fare la review e di annotarla.
