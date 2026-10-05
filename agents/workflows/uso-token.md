# Uso consapevole dei token

Ogni scelta qui sotto è applicata nel repo. Le misure sono state rilevate durante lo sviluppo.

## Runtime (chiamate dell'app a Claude)

L'AI entra in due punti soltanto: l'estrazione delle voci dai documenti e la spiegazione dei termini che il glossario rivisto non copre. Tutto il resto è Python.

| Scelta | Dove | Effetto |
|---|---|---|
| CLI lanciata sempre da una cwd neutra | `app/finsup/ai_client.py` | Lanciata dalla cartella del repo, `claude -p` caricava CLAUDE.md, hook e memoria anche per un prompt banale: circa **23k token in più**, **~$0.03 a chiamata contro ~$0.008** (misurato in bootstrap) |
| Strumenti al minimo | `ai_client.py`, `extraction.py`, `glossary.py` | `--tools ""` per le chiamate solo testo. Estrazione e glossario usano soltanto `Read`, perché lo structured output (`--json-schema`) senza almeno un tool viene ignorato; nell'estrazione `Read` vede solo la cartella degli upload (`--add-dir`) |
| Haiku come modello di default | `DEFAULT_MODEL` in `ai_client.py` | Il modello più economico adeguato a estrazione e spiegazioni brevi |
| Tetto di costo su ogni chiamata | `MAX_BUDGET_USD` in `ai_client.py`, `EXTRACTION_BUDGET_USD` in `extraction.py` | `--max-budget-usd 0.05` per glossario e chiamate brevi; `0.30` (timeout 180 s) per l'estrazione, una sola chiamata per documento |
| Cache su disco dell'estrazione | `extraction.py` | Chiave = hash di contenuto del file + prompt + schema: lo stesso documento non viene mai riletto, a costo zero. `app/scripts/prewarm_extraction.py` la prepara prima della demo |
| Glossario rivisto prima, AI dopo | `KNOWN_TERMS` in `glossary.py` | 26 definizioni scritte e riviste dal team, mostrate a 0 token; i termini nuovi vanno in **una sola** chiamata e solo se l'utente la chiede |
| `--no-session-persistence` | `ai_client.py` | Ogni chiamata è one-shot: nessuna cronologia che cresce e viene riletta |
| System prompt brevi e dedicati per compito | `agents/prompts/` | Nessun documento di progetto incollato nei prompt |
| Calcoli e doppioni in Python, non nel modello | `app/finsup/budget.py` | Zero token per tutti i numeri, deduplica compresa |

**Costi misurati** (Haiku, documenti demo in `app/demo_assets/`): da $0.014 a $0.07 a documento, in 40-100 s; i 5 documenti dei due scenari costano circa $0.22 in tutto e, dopo il prewarm, $0 a ogni rilettura in demo.

## Sviluppo (Claude Code)

| Scelta | Dove | Effetto |
|---|---|---|
| `CLAUDE.md` snello + regole modulari importate | `CLAUDE.md`, `agents/instructions/` | Caricati sempre solo regole e mappa; il contesto lungo (`agents/context/progetto.md`) si legge solo quando serve |
| Skill, subagent e comandi come "rimandi" in `.claude/` | `.claude/skills|agents|commands/` | Disclosure progressiva: all'avvio solo nome e descrizione, istruzioni complete lette solo se il componente viene attivato |
| Ricerche delegate a subagent | es. verifica della documentazione Claude Code sugli hook | Il subagent ha consumato **~69k token nel proprio contesto**; al thread principale è tornata solo una sintesi di una pagina |
| Review dei testi con un subagent fissato su Haiku | `agents/subagents/finsup-copy-reviewer.md` | Compito di classificazione su un modello economico, contesto isolato |
| Sessioni separate per filone di lavoro | sviluppo app / verifica deliverable | Ogni sessione resta piccola e focalizzata (meno context rot) |
