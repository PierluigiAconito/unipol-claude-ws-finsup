# Strategia di applicazione dell'AI

Principio: **AI dove serve linguaggio, codice deterministico dove servono numeri, una persona dove serve giudizio.** Un'app educativa sul budget non può permettersi un totale sbagliato o un consiglio travestito da spiegazione.

## Nella soluzione (runtime)

| Funzionalità | Chi la fa | Perché |
|---|---|---|
| Estrazione delle voci da busta paga, bollette, estratto conto (RF-01b) | **AI** (Claude, prompt `agents/prompts/estrazione.md`) | I documenti reali non hanno un formato fisso: un parser a template non regge. L'AI restituisce JSON strutturato |
| Conferma dei dati estratti (RF-09) | **Utente** | Un errore di estrazione deve essere visibile e correggibile prima di ogni calcolo. È anche la garanzia di "non alterare il significato" |
| Normalizzazione mensile, totali, risparmio, indicatori, 50/30/20, proiezione obiettivo (RF-02, 03, 05, 06, 07) | **Python deterministico** (`app/finsup/`) | I numeri devono essere esatti, ripetibili e testabili. Zero token |
| Glossario dei termini tecnici incontrati (RF-04) | **AI** (prompt `agents/prompts/glossario.md`) | Spiegare il gergo in parole semplici è un compito linguistico |
| Controllo "niente consigli" sui testi AI | **Regole deterministiche** (`app/finsup/content_guard.py`) | Prevedibile, testato, costo zero. Non usiamo un'AI per giudicare un'altra AI su un vincolo bloccante |
| Fallback senza CLI o senza rete | **Mock** (`ai_client._mock`) | La demo non deve dipendere dalla rete |

Cosa l'AI **non** fa, per scelta: niente chatbot aperto, nessun calcolo, nessuna decisione al posto dell'utente, nessun suggerimento su cosa tagliare o dove mettere i soldi.

## Nello sviluppo (Claude Code)

| Attività | AI | Persona |
|---|---|---|
| Specifica funzionale | supporto alla stesura | scritta e validata dal team (`app/docs/requisiti-funzionali.md`) |
| Codice e test | generati con Claude Code, guidati da `CLAUDE.md` + `agents/instructions/` | review del diff, `pytest app` verde |
| Vincolo di dominio | hook PreToolUse che blocca la scrittura, skill e subagent come pre-filtro | review finale dei testi, annotata in `verifica-umana.md` |
| Lavoro in parallelo | più sessioni Claude Code sulla stessa working copy, con file assegnati a ciascuna | decide cosa si committa e quando si pusha |

Dettaglio del flusso: [sdd-workflow.md](sdd-workflow.md). Scelte sui token: [uso-token.md](uso-token.md).
