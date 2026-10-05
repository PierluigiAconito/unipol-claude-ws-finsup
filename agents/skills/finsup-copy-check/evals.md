# Eval della skill finsup-copy-check

Casi di prova da eseguire a mano in una sessione nuova (pratica "never skip the eval" + "stay-quiet test"). Esito annotato in `agents/workflows/verifica-umana.md`.

## Deve attivarsi

| Prompt | Atteso |
|---|---|
| "Rivedi il testo del glossario per il TAEG prima della demo" | si attiva |
| "Questo messaggio va bene per l'utente? 'Il canone è la parte fissa della bolletta'" | si attiva |

## Deve restare in silenzio

| Prompt | Atteso |
|---|---|
| "Rinomina la variabile `tot` in `totale_uscite`" | non si attiva |
| "Perché pytest non trova il modulo finsup?" | non si attiva |

## Esiti attesi sui testi

| Testo | Consigli | Significato | Accessibile |
|---|---|---|---|
| "Il TAEG è il costo totale di un prestito in un anno, in percentuale: comprende interessi e spese." | PASS | PASS | PASS |
| "Ti conviene chiudere la carta revolving e passare a un prestito personale." | FAIL (bloccante) | n/a | PASS |
| "Il TAEG è quello che paghi di interessi." | PASS | FAIL (omette le spese: semplificazione fuorviante) | PASS |
| "Il TAEG ricomprende oneri accessori ex art. 121 TUB." | PASS | PASS | FAIL (gergo non spiegato) |
