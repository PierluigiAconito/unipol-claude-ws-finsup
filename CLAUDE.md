# FinSup: regole operative per Claude Code

Prototipo Hagenthon, Tema 02 (Inclusione Finanziaria): app Streamlit che aiuta una persona con bassa alfabetizzazione finanziaria a **capire** il proprio budget mensile, partendo dai documenti che ha già (busta paga, bollette, estratto conto). Contesto completo in [agents/context/progetto.md](agents/context/progetto.md): qui solo regole, per restare leggero a ogni sessione. Non incollarlo nei prompt.

## Run · Test

```bash
pip install -r app/requirements.txt
streamlit run app/main.py      # http://localhost:8501
pytest app                     # guardrail, hook, logica di calcolo
```

## Mappa del repo (struttura di consegna obbligatoria)

- `app/`: la soluzione. `main.py` (UI Streamlit), `finsup/` (logica), `tests/`, `docs/requisiti-funzionali.md` (la specifica, fonte di verità)
- `agents/`: la struttura agentica. `instructions/` (queste regole), `skills/`, `subagents/`, `commands/`, `hooks/`, `prompts/` (system prompt usati dall'app a runtime), `workflows/`, `context/`
- `presentation/`: presentazione HTML (brand Accenture)
- `.claude/`: solo collegamenti. Claude Code scopre skill, subagent e comandi solo lì, ma la fonte unica è `agents/`: mai logica duplicata in `.claude/`

## Regole (modulari, caricate sempre)

@agents/instructions/dominio.md
@agents/instructions/uso-ai.md
@agents/instructions/processo.md
