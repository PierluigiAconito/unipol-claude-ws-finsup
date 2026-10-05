"""Wrapper token-conscious sulla CLI locale di Claude Code.

Invoca `claude -p` come sottoprocesso invece dell'SDK Anthropic con API key:
cosi' l'app riusa l'autenticazione di Claude Code gia' presente sulla
macchina (nessuna chiave separata da gestire per la demo). Se la CLI non
e' disponibile o non autenticata, ritorna una risposta mock cosi' l'app
resta utilizzabile anche offline/senza token valido.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile

DEFAULT_MODEL = "claude-haiku-4-5-20251001"  # modello piu' economico adeguato al task
TIMEOUT_S = 60
MAX_BUDGET_USD = "0.05"  # tetto per chiamata, uso consapevole dei token/costo

# Lanciare `claude -p` dalla cwd del repo fa auto-caricare CLAUDE.md, hook e
# memoria di progetto anche per un prompt banale (~23k token extra, misurato
# a $0.03/chiamata contro $0.008 circa fuori repo). Per queste chiamate
# "esplicative" una-tantum non serve ne' il contesto di progetto ne' l'uso
# di tool: le isoliamo in una cwd neutra e disabilitiamo i tool per tenere
# il costo per chiamata basso (vedi docs/04-verifica-umana.md per la misura).
_NEUTRAL_CWD = tempfile.gettempdir()


def _claude_binary() -> str | None:
    return shutil.which("claude")


def _subprocess_env() -> dict:
    """Ambiente per il sottoprocesso `claude`, con fallback Windows.

    Caso reale incontrato in bootstrap: token impostato con `setx` ma il
    processo che lancia l'app (terminale/IDE) era gia' avviato prima e non
    lo vede ancora nel proprio ambiente. Se manca, proviamo a leggerlo dal
    registro utente invece di costringere l'utente a riavviare tutto.
    """
    env = os.environ.copy()
    if env.get("CLAUDE_CODE_OAUTH_TOKEN"):
        return env
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, "CLAUDE_CODE_OAUTH_TOKEN")
            if value:
                env["CLAUDE_CODE_OAUTH_TOKEN"] = value
    except (ImportError, OSError, FileNotFoundError):
        pass
    return env


def ask(prompt: str, *, system_prompt: str | None = None, model: str = DEFAULT_MODEL) -> dict:
    """Esegue un singolo prompt non interattivo sulla CLI locale di Claude.

    Ritorna sempre un dict con almeno {"text", "mocked", "cost_usd", "tokens"}.
    Non solleva eccezioni: in caso di qualsiasi problema ritorna una risposta mock.
    """
    binary = _claude_binary()
    if binary is None:
        return _mock(reason="claude CLI non trovata nel PATH")

    cmd = [
        binary, "-p", prompt,
        "--model", model,
        "--output-format", "json",
        "--no-session-persistence",
        "--max-budget-usd", MAX_BUDGET_USD,
        "--tools", "",  # nessun bisogno di tool per una spiegazione una-tantum
    ]
    if system_prompt:
        cmd += ["--system-prompt", system_prompt]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",  # la CLI emette UTF-8; su Windows il default e' cp1252
            timeout=TIMEOUT_S,
            cwd=_NEUTRAL_CWD,
            env=_subprocess_env(),
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return _mock(reason=f"CLI non raggiungibile ({exc})")

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return _mock(reason="output della CLI non interpretabile come JSON")

    if payload.get("is_error"):
        return _mock(reason=payload.get("result", "errore CLI sconosciuto"))

    return {
        "text": payload.get("result", ""),
        "mocked": False,
        "cost_usd": payload.get("total_cost_usd", 0.0),
        "tokens": payload.get("usage", {}),
    }


def _mock(*, reason: str) -> dict:
    return {
        "text": (
            f"[MOCK] Claude locale non disponibile ({reason}). "
            "Risposta segnaposto per permettere la demo anche offline."
        ),
        "mocked": True,
        "cost_usd": 0.0,
        "tokens": {},
    }
