# Uso consapevole dell'AI (token ridotti)

- **Dove l'AI, dove no**: AI solo dove serve linguaggio (estrazione delle voci da PDF/XLS, glossario dei termini). Calcoli, normalizzazioni, benchmark e proiezioni sono Python deterministico e testato: mai chiedere numeri al modello.
- Runtime: CLI locale `claude -p` tramite `finsup.ai_client.ask()`, che riusa l'autenticazione di Claude Code (niente API key). Se la CLI non risponde, risposta mock (`mocked: True`): l'app resta usabile offline.
- Modello di default Haiku, il più economico adeguato al task. `--max-budget-usd` sempre impostato. Cwd neutra per non caricare il contesto di progetto a ogni chiamata; `--tools ""` per le chiamate solo testo, solo `Read` dove serve lo structured output (estrazione, glossario). Estrazione in cache per hash del contenuto: mai rileggere lo stesso documento.
- System prompt brevi in `agents/prompts/<nome>.md`, caricati con `finsup.prompts.load_prompt`. Mai prompt inline nel codice, mai documenti interi o `progetto.md` dentro un prompt.
- In sviluppo: ricerche ampie e review delegate a subagent (contesto isolato, torna solo la sintesi). Le revisioni dei testi passano dal subagent `finsup-copy-reviewer`, fissato su Haiku.
- Misure e scelte documentate in `agents/workflows/uso-token.md`.
