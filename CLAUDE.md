# Regole operative del progetto

Prototipo Hagenthon, Tema 02: Inclusione Finanziaria. Dettagli completi in [PROJECT.md](PROJECT.md) — qui solo le regole, non il contesto (per restare leggero ad ogni sessione).

## Vincolo di dominio (non negoziabile)

Questa applicazione **non deve mai dare consigli finanziari**: niente raccomandazioni di investimento, consulenza personalizzata, indicazioni su cosa comprare/vendere/scegliere. Solo spiegazione e comprensione. Ogni testo generato dall'AI e destinato all'utente finale passa dal guardrail in `app/content_guard.py` prima di essere mostrato o committato.

## Stack

- Python 3.13, Streamlit per la UI, nessun backend separato
- GenAI: CLI locale `claude -p` (vedi `app/ai_client.py`), non l'SDK Anthropic con API key — riusa l'autenticazione Claude Code già presente sulla macchina
- Se la CLI locale non è autenticata o non risponde, `ai_client.ask()` ritorna una risposta mock (`mocked: True`): l'app deve restare utilizzabile anche offline

## Uso consapevole dell'AI (token ridotti)

- Modello di default: Haiku (il più economico adeguato al task), non Sonnet/Opus salvo necessità reale
- `--max-budget-usd` sempre impostato sulle chiamate CLI
- System prompt brevi e mirati, mai l'intero PROJECT.md incollato in un prompt
- Preferire skill/pattern mirati a chiamate monolitiche quando si estende la soluzione

## Verifica umana

- Ogni nuova funzionalità che genera testo rivolto all'utente finale va rivista a mano prima di essere considerata demo-ready, non solo testata automaticamente
- Annotare le review in `docs/04-verifica-umana.md` (cosa è stato controllato, esito)

## Pattern attivi in questo repo (evidenza per la valutazione)

- **Rules**: questo file
- **Hook**: `.claude/hooks/check_financial_advice.py`, eseguito su Write/Edit per bloccare contenuti che violano il vincolo di dominio prima ancora del commit
- **Skill**: `.claude/skills/finsup-copy-check/` per revisionare un testo educativo rispetto a "niente consigli" + "semplificare senza tradire"
