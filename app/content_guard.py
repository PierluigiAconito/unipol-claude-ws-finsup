"""Guardrail sul vincolo del Tema 02: niente consigli finanziari.

Il brief vieta esplicitamente "raccomandazioni di investimento, consulenza
finanziaria personalizzata o indicazioni su cosa comprare, vendere o
scegliere". Questo modulo cerca pattern linguistici tipici di un consiglio
d'azione finanziaria personalizzato in un testo (generato dall'AI o scritto
a mano). Usato sia a runtime nell'app (`app.py`) sia dall'hook di
Claude Code (`.claude/hooks/check_financial_advice.py`).

Nota: i pattern intercettano il *consiglio d'azione*, non la menzione di
termini finanziari (che e' necessaria per un tool educativo).
"""
from __future__ import annotations

import re

FORBIDDEN_PATTERNS = [
    r"\bti consiglio di (investire|comprare|vendere|scegliere)\b",
    r"\bdovresti (investire|comprare|vendere|scegliere)\b",
    r"\b(investi|compra|vendi) (in|su|il|la|questo|questa)\b",
    r"\bla scelta migliore per te è\b",
    r"\bti consigliamo (questo|questa|il|la) (fondo|titolo|prodotto|polizza)\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in FORBIDDEN_PATTERNS]


def find_violations(text: str) -> list[str]:
    """Ritorna le frasi del testo che violano il vincolo "niente consigli"."""
    return [m.group(0) for pattern in _COMPILED for m in pattern.finditer(text)]


def is_compliant(text: str) -> bool:
    return not find_violations(text)
