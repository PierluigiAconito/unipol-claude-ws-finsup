---
name: finsup-copy-check
description: Revisiona un testo educativo-finanziario destinato all'utente finale rispetto ai vincoli del Tema 02 (niente consigli, non tradire il significato, linguaggio accessibile). Usare prima di considerare "demo-ready" una schermata o un messaggio con testo generato dall'AI.
---

# FinSup Copy Check

Quando ti viene chiesto di rivedere del testo per il prototipo FinSup (Tema 02 — Inclusione Finanziaria), controlla esplicitamente questi tre punti e riporta un verdetto per ciascuno:

1. **Niente consigli finanziari**: il testo non deve mai dire all'utente cosa fare con i propri soldi (investire, comprare, vendere, scegliere un prodotto). Va bene spiegare *cosa significa* un concetto o una voce di bolletta/estratto conto, non *cosa scegliere*.
2. **Non tradire il significato**: se il testo semplifica un'informazione originale (bolletta, estratto conto, concetto), il senso non deve cambiare. Segnala se una semplificazione rischia di essere fuorviante.
3. **Linguaggio accessibile**: frasi brevi, lessico comune, niente gergo tecnico non spiegato — il target ha bassa alfabetizzazione finanziaria.

Se il testo fallisce il punto 1, trattalo come bloccante (coerente con il guardrail automatico in `app/content_guard.py` e l'hook `.claude/hooks/check_financial_advice.py`): riformula prima di procedere, non limitarti a segnalarlo.

Riporta l'esito in forma breve: per ogni punto, PASS/FAIL + una riga di motivazione.
