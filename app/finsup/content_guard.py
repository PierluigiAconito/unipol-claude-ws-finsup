"""Guardrail sul vincolo del Tema 02: niente consigli finanziari.

Il brief vieta esplicitamente "raccomandazioni di investimento, consulenza
finanziaria personalizzata o indicazioni su cosa comprare, vendere o
scegliere". Questo modulo cerca pattern linguistici tipici di un consiglio
d'azione finanziaria personalizzato in un testo (generato dall'AI o scritto
a mano). Usato sia a runtime nell'app (`app/main.py`) sia dall'hook di
Claude Code (`agents/hooks/check_financial_advice.py`).

Nota: i pattern intercettano il *consiglio d'azione*, non la menzione di
termini finanziari (che e' necessaria per un tool educativo). Coprono anche
la prescrizione di tagli di spesa, vietata da RF-06/RF-07
(app/docs/requisiti-funzionali.md).
"""
from __future__ import annotations

import re

_SPEND_VERBS = "investire|comprare|vendere|scegliere|tagliare|ridurre|eliminare|spendere"

FORBIDDEN_PATTERNS = [
    # consiglio esplicito in prima persona
    rf"\bti (consiglio|suggerisco|raccomando) di\b",
    r"\bti consigliamo (di|questo|questa|il|la)\b",
    # prescrizione in seconda persona
    rf"\bdovresti (\w+ )?({_SPEND_VERBS})\b",
    r"\bti conviene\b",
    # imperativi su prodotti o spese
    r"\b(investi|compra|vendi) (in|su|il|la|questo|questa)\b",
    r"\b(taglia|riduci|elimina)\b.{0,30}\b(spes[ae]|abbonament[oi]|uscit[ae])\b",
    # scelta al posto dell'utente
    r"\bla scelta migliore (per te )?(è|e')",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in FORBIDDEN_PATTERNS]


def find_violations(text: str) -> list[str]:
    """Ritorna le frasi del testo che violano il vincolo "niente consigli"."""
    return [m.group(0) for pattern in _COMPILED for m in pattern.finditer(text)]


def is_compliant(text: str) -> bool:
    return not find_violations(text)
