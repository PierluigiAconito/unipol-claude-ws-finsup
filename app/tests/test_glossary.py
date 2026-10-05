"""Test di finsup.glossary senza chiamare la CLI (monkeypatch su run_cli)."""
from finsup import demo_data, glossary


def test_detects_terms_in_demo_labels():
    labels = [i["label"] for i in demo_data.INCOMES + demo_data.EXPENSES]
    terms = dict(glossary.detect_terms(labels))
    assert terms["TAEG"] == "Rata prestito auto (TAEG 8,45%)"
    for expected in ("Interessi di mora", "Commissione di gestione", "Imposta di bollo",
                     "Franchigia", "RC auto", "TARI", "Ritenuta d'acconto", "Bollo auto"):
        assert expected in terms


def test_doc_terms_are_mapped_to_known_terms_without_duplicates():
    terms = glossary.detect_terms(
        ["Rata (TAEG 8,45%)"],
        ["TAEG", "TFR (Trattamento di Fine Rapporto)", "Addizionale regionale IRPEF", "CCNL"],
    )
    names = [t for t, _ in terms]
    assert names == ["TAEG", "TFR", "Addizionale regionale e comunale", "CCNL"]
    assert glossary.unknown_terms(terms) == [("CCNL", "documento caricato")]


def test_known_terms_cost_no_ai_call(monkeypatch):
    monkeypatch.setattr(glossary, "run_cli", lambda *a, **k: (_ for _ in ()).throw(AssertionError("AI chiamata")))
    items = glossary.known_definitions([("TAEG", "x"), ("CCNL", "y")])
    assert [i["term"] for i in items] == ["TAEG"]


def test_unknown_terms_use_a_single_ai_call(monkeypatch):
    calls = []

    def fake(prompt, extra_args, **kwargs):
        calls.append(prompt)
        return {"total_cost_usd": 0.01, "structured_output": {"items": [
            {"term": "CCNL", "explanation": "Il contratto che fissa le regole del lavoro per un settore."},
            {"term": "Contingenza", "explanation": "Una parte storica dello stipendio."},
        ]}}, None

    monkeypatch.setattr(glossary, "run_cli", fake)
    result = glossary.explain_with_ai([("CCNL", "busta paga"), ("Contingenza", "busta paga")])
    assert len(calls) == 1
    assert [i["term"] for i in result["items"]] == ["CCNL", "Contingenza"]
    assert result["cost_usd"] == 0.01


def test_ai_text_violating_guardrail_is_never_shown(monkeypatch):
    def fake(prompt, extra_args, **kwargs):
        return {"structured_output": {"items": [
            {"term": "Fondo", "explanation": "Ti consiglio di investire in questo fondo."},
            {"term": "Rata", "explanation": "La somma che si paga a ogni scadenza di un prestito."},
        ]}}, None

    monkeypatch.setattr(glossary, "run_cli", fake)
    result = glossary.explain_with_ai([("Fondo", "x"), ("Rata", "y")])
    assert result["blocked"] == ["Fondo"]
    assert all("consiglio" not in i["text"] for i in result["items"])


def test_ai_unavailable_returns_error_and_no_items(monkeypatch):
    monkeypatch.setattr(glossary, "run_cli", lambda *a, **k: (None, "claude CLI non trovata nel PATH"))
    result = glossary.explain_with_ai([("CCNL", "x")])
    assert result["items"] == [] and result["error"]


def test_reviewed_definitions_pass_the_guardrail():
    from finsup.content_guard import find_violations

    for term, (_, definition) in glossary.KNOWN_TERMS.items():
        assert not find_violations(definition), term
