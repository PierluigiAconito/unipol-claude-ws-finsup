"""RF-01b: estrazione strutturata di entrate/uscite da file caricati.

Non e' un parser a template fisso: il file (PDF, o Excel convertito in
testo) va a Claude tramite la CLI locale, che restituisce JSON validato
contro `SCHEMA` (`--json-schema` -> campo `structured_output`).

Differenze rispetto a `ai_client.ask()`:
- tool `Read` abilitato: serve alla CLI per leggere il PDF da disco
  (supporto nativo PDF di Claude Code) ed e' richiesto anche dallo
  structured output, che con `--tools ""` viene ignorato (verificato);
- budget e timeout piu' alti: una sola chiamata per documento caricato.

Il risultato precompila il form e passa SEMPRE dalla conferma RF-09:
questo modulo non avvia mai il calcolo.

Cache su disco per hash (file + prompt + schema): un documento gia' letto
non viene riletto, quindi in demo si puo' "scaldare" la cache prima del
pitch (scripts/prewarm_extraction.py) e l'estrazione dal vivo e' immediata.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import pandas as pd

from finsup.ai_client import run_cli
from finsup.budget import CATEGORIES, DEFAULT_TYPE, EXPENSE_TYPES, PERIODICITIES
from finsup.content_guard import find_violations
from finsup.prompts import load_prompt

EXTRACTION_BUDGET_USD = "0.30"
EXTRACTION_TIMEOUT_S = 180
SPREADSHEET_SUFFIXES = {".xlsx", ".xls"}
FLAGGED_LABEL = "Voce dal documento (descrizione da verificare)"

# Cartella dedicata dentro la cwd neutra della CLI (vedi ai_client): i file
# di st.file_uploader vivono in memoria e vanno salvati su disco per Read.
UPLOAD_DIR = Path(tempfile.gettempdir()) / "finsup_uploads"
CACHE_DIR = Path(tempfile.gettempdir()) / "finsup_cache"

SCHEMA = {
    "type": "object",
    "properties": {
        "incomes": {"type": "array", "items": {"type": "object", "properties": {
            "label": {"type": "string"},
            "amount": {"type": "number"},
            "periodicity": {"type": "string", "enum": PERIODICITIES},
        }, "required": ["label", "amount", "periodicity"]}},
        "expenses": {"type": "array", "items": {"type": "object", "properties": {
            "label": {"type": "string"},
            "amount": {"type": "number"},
            "category": {"type": "string", "enum": CATEGORIES},
            "type": {"type": "string", "enum": EXPENSE_TYPES},
            "periodicity": {"type": "string", "enum": PERIODICITIES},
        }, "required": ["label", "amount", "category", "type", "periodicity"]}},
        "terms": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["incomes", "expenses"],
}


def save_upload(name: str, data: bytes) -> Path:
    UPLOAD_DIR.mkdir(exist_ok=True)
    path = UPLOAD_DIR / Path(name).name
    path.write_bytes(data)
    return path


def extract_budget_items(path: Path) -> dict:
    """Estrae le voci da un file. Non solleva eccezioni.

    Ritorna {"incomes", "expenses", "terms", "error", "cost_usd"}; in caso di
    errore le liste sono vuote e `error` spiega il motivo (l'utente puo'
    sempre inserire le voci a mano).
    """
    try:
        prompt = _user_prompt(path)
    except Exception as exc:  # file illeggibile: fuori scope gestirlo meglio (§8)
        return _empty(f"file non leggibile ({exc})")

    system_prompt = load_prompt("estrazione")
    cache_file = CACHE_DIR / f"{_cache_key(path, system_prompt)}.json"
    if cache_file.exists():
        data, cost, cached = json.loads(cache_file.read_text(encoding="utf-8")), 0.0, True
    else:
        payload, error = run_cli(
            prompt,
            [
                "--tools", "Read",
                "--allowedTools", "Read",
                "--add-dir", str(path.parent),
                "--json-schema", json.dumps(SCHEMA),
            ],
            system_prompt=system_prompt,
            max_budget_usd=EXTRACTION_BUDGET_USD,
            timeout_s=EXTRACTION_TIMEOUT_S,
        )
        if error:
            return _empty(error)
        data = payload.get("structured_output")
        if not isinstance(data, dict):
            return _empty("risposta senza dati strutturati")
        cost, cached = payload.get("total_cost_usd", 0.0), False
        CACHE_DIR.mkdir(exist_ok=True)
        cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    source = path.name
    incomes = [_clean_income(i, source) for i in data.get("incomes", [])]
    expenses = [_clean_expense(e, source) for e in data.get("expenses", [])]
    # Le etichette passano dal guardrail come ogni testo prodotto dall'AI. Una
    # voce bloccata NON viene scartata (cambierebbe i totali di nascosto):
    # resta con importo originale ed etichetta neutra, da verificare in RF-09.
    flagged = 0
    for item in incomes + expenses:
        if find_violations(item["label"]):
            item["label"] = FLAGGED_LABEL
            flagged += 1
    terms = [t for t in data.get("terms", []) if isinstance(t, str) and not find_violations(t)]
    return {
        "incomes": incomes,
        "expenses": expenses,
        "terms": terms[:12],
        "flagged": flagged,
        "cached": cached,
        "error": None,
        "cost_usd": cost,
    }


def _cache_key(path: Path, system_prompt: str) -> str:
    digest = hashlib.sha256(path.read_bytes())
    digest.update(system_prompt.encode("utf-8"))
    digest.update(json.dumps(SCHEMA, sort_keys=True).encode("utf-8"))
    return digest.hexdigest()


def _read_sheets(path: Path) -> dict[str, pd.DataFrame]:
    """Solo i valori delle celle. calamine ignora gli stili, che in alcuni
    file esportati da altri programmi fanno fallire openpyxl (QA-20)."""
    try:
        return pd.read_excel(path, sheet_name=None, engine="calamine")
    except Exception:
        return pd.read_excel(path, sheet_name=None)


def _user_prompt(path: Path) -> str:
    if path.suffix.lower() in SPREADSHEET_SUFFIXES:
        # Read non interpreta i fogli Excel: li passiamo come testo CSV.
        sheets = _read_sheets(path)
        text = "\n\n".join(f"## Foglio: {name}\n{df.to_csv(index=False)}" for name, df in sheets.items())
        return f"Contenuto del foglio di calcolo '{path.name}' in formato CSV:\n\n{text}\n\nEstrai le voci."
    return f'Leggi il file "{path}" con il tool Read ed estrai le voci.'


def _clean_income(item: dict, source: str) -> dict:
    return {
        "label": str(item.get("label", "")).strip(),
        "amount": abs(float(item.get("amount") or 0)),
        "periodicity": item.get("periodicity") if item.get("periodicity") in PERIODICITIES else "mensile",
        "source": source,
    }


def _clean_expense(item: dict, source: str) -> dict:
    category = item.get("category") if item.get("category") in CATEGORIES else "Altro"
    return {
        **_clean_income(item, source),
        "category": category,
        "type": item.get("type") if item.get("type") in EXPENSE_TYPES else DEFAULT_TYPE[category],
    }


def _empty(error: str) -> dict:
    return {"incomes": [], "expenses": [], "terms": [], "flagged": 0, "cached": False, "error": error, "cost_usd": 0.0}
