# Verifica Umana

Log delle review manuali sul testo/funzionalità generate con l'AI, prima di considerarle demo-ready. Richiesto come evidenza dal criterio di valutazione "verifica umana" (vedi [00-regole-e-valutazione.md](00-regole-e-valutazione.md)).

| Data | Cosa è stato rivisto | Chi | Esito |
|---|---|---|---|
| 2026-10-05 | Bootstrap: guardrail `content_guard.py` (pattern anti-consigli-finanziari) | team | PASS — testato con `pytest`, vedi `tests/test_content_guard.py` |
