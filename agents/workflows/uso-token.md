# Uso consapevole dei token

Ogni scelta qui sotto è applicata nel repo. Le misure sono state rilevate durante lo sviluppo.

## Runtime (chiamate dell'app a Claude)

| Scelta | Dove | Effetto |
|---|---|---|
| CLI lanciata da una cwd neutra, con `--tools ""` | `app/finsup/ai_client.py` | Lanciata dalla cartella del repo, `claude -p` caricava CLAUDE.md, hook e memoria anche per un prompt banale: circa **23k token in più**, **~$0.03 a chiamata contro ~$0.008** (misurato in bootstrap) |
| Haiku come modello di default | `DEFAULT_MODEL` in `ai_client.py` | Il modello più economico adeguato a estrazione e spiegazioni brevi |
| `--max-budget-usd 0.05` su ogni chiamata | `ai_client.py` | Tetto di costo garantito per chiamata |
| `--no-session-persistence` | `ai_client.py` | Ogni chiamata è one-shot: nessuna cronologia che cresce e viene riletta |
| System prompt brevi e dedicati per compito | `agents/prompts/` | Nessun documento di progetto incollato nei prompt |
| Calcoli in Python, non nel modello | `app/finsup/` | Zero token per tutti i numeri |

## Sviluppo (Claude Code)

| Scelta | Dove | Effetto |
|---|---|---|
| `CLAUDE.md` snello + regole modulari importate | `CLAUDE.md`, `agents/instructions/` | Caricati sempre solo regole e mappa; il contesto lungo (`agents/context/progetto.md`) si legge solo quando serve |
| Skill, subagent e comandi come "rimandi" in `.claude/` | `.claude/skills|agents|commands/` | Disclosure progressiva: all'avvio solo nome e descrizione, istruzioni complete lette solo se il componente viene attivato |
| Ricerche delegate a subagent | es. verifica della documentazione Claude Code sugli hook | Il subagent ha consumato **~69k token nel proprio contesto**; al thread principale è tornata solo una sintesi di una pagina |
| Review dei testi con un subagent fissato su Haiku | `agents/subagents/finsup-copy-reviewer.md` | Compito di classificazione su un modello economico, contesto isolato |
| Sessioni separate per filone di lavoro | sviluppo app / verifica deliverable | Ogni sessione resta piccola e focalizzata (meno context rot) |
