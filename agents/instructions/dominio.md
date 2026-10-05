# Vincolo di dominio (non negoziabile)

L'app **non dà mai consigli finanziari**: niente raccomandazioni di investimento, consulenza personalizzata, indicazioni su cosa comprare, vendere o scegliere, né prescrizioni su quali spese tagliare (RF-06, RF-07). Solo spiegazione e comprensione: la decisione resta all'utente.

- Ogni testo generato dall'AI per l'utente finale passa da `finsup.content_guard.find_violations` **prima** di essere mostrato. Se viola, non si mostra.
- Semplificare senza tradire: gli importi estratti dai documenti restano quelli originali, visibili e modificabili. Il calcolo parte solo dopo la conferma esplicita dell'utente (RF-09).
- Disclaimer "strumento educativo, non consulenza finanziaria" sempre visibile in UI.
- Doppia rete: guardrail a runtime nell'app + hook PreToolUse (`agents/hooks/check_financial_advice.py`) che blocca già in sviluppo la scrittura di file con linguaggio da consulente.
