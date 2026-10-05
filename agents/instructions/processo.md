# Processo e verifica umana

- **Spec-driven**: la specifica è `app/docs/requisiti-funzionali.md`. Ogni funzionalità cita il suo RF. Se il codice deve divergere, si aggiorna prima la specifica.
- Nessun testo rivolto all'utente è demo-ready senza tre passaggi: guardrail verde, review con la skill `finsup-copy-check` (o il subagent `finsup-copy-reviewer`), **review di una persona** annotata in `agents/workflows/verifica-umana.md`. Claude non scrive esiti di review al posto delle persone.
- Prima del freeze: comando `/demo-ready`.
- Più sessioni Claude lavorano in parallelo sulla stessa working copy: ognuna dichiara i file che possiede, committa solo path espliciti (mai `git add -A`), push solo dopo l'ok di una persona del team.
- Niente dati personali reali: solo documenti demo inventati o anonimizzati, in `app/demo_assets/`.
- Escalation: chiedere prima di cambiare la struttura del repo (vincolo di consegna), il vincolo di dominio, o di fare push.
