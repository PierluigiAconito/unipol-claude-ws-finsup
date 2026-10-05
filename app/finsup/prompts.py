"""Caricamento dei system prompt usati dall'app a runtime.

I prompt non stanno nel codice ma in `agents/prompts/<nome>.md`: sono parte
della struttura agentica consegnata (versionati e revisionabili come le
skill), brevi e mirati per tenere basso il consumo di token.
"""
from __future__ import annotations

from functools import cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "agents" / "prompts"


@cache
def load_prompt(name: str) -> str:
    """Ritorna il testo di `agents/prompts/<name>.md`, senza spazi ai bordi."""
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8").strip()
