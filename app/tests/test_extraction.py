"""Test di finsup.extraction senza chiamare la CLI (monkeypatch su run_cli)."""
from pathlib import Path

import pytest

from finsup import extraction


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(extraction, "CACHE_DIR", tmp_path / "cache")


@pytest.fixture
def pdf(tmp_path) -> Path:
    path = tmp_path / "doc.pdf"
    path.write_bytes(b"%PDF-1.4 finto")
    return path


def test_second_extraction_of_same_file_uses_cache(monkeypatch, pdf):
    payload = {"total_cost_usd": 0.02, "structured_output": {"incomes": [
        {"label": "Netto in busta", "amount": 1620, "periodicity": "mensile"}], "expenses": []}}
    calls = []
    monkeypatch.setattr(extraction, "run_cli", lambda *a, **k: (calls.append(1), (payload, None))[1])
    first = extraction.extract_budget_items(pdf)
    second = extraction.extract_budget_items(pdf)
    assert len(calls) == 1
    assert second["cached"] and second["cost_usd"] == 0
    assert second["incomes"] == first["incomes"]


def test_errors_are_not_cached(monkeypatch, pdf):
    calls = []
    monkeypatch.setattr(extraction, "run_cli", lambda *a, **k: (calls.append(1), (None, "timeout"))[1])
    extraction.extract_budget_items(pdf)
    extraction.extract_budget_items(pdf)
    assert len(calls) == 2


def _fake_cli(payload=None, error=None):
    def fake(prompt, extra_args, **kwargs):
        fake.args = extra_args
        return payload, error
    return fake


def test_cli_error_returns_empty_lists_and_reason(monkeypatch, pdf):
    monkeypatch.setattr(extraction, "run_cli", _fake_cli(error="CLI non raggiungibile"))
    result = extraction.extract_budget_items(pdf)
    assert result["incomes"] == [] and result["expenses"] == []
    assert result["error"] == "CLI non raggiungibile"


def test_missing_structured_output_is_an_error(monkeypatch, pdf):
    monkeypatch.setattr(extraction, "run_cli", _fake_cli(payload={"result": "testo libero"}))
    assert extraction.extract_budget_items(pdf)["error"]


def test_values_outside_enum_are_normalized(monkeypatch, pdf):
    payload = {"total_cost_usd": 0.02, "structured_output": {
        "incomes": [{"label": "Netto in busta", "amount": 1620, "periodicity": "bimestrale"}],
        "expenses": [{"label": "Canone", "amount": -4.9, "category": "Banca", "type": "boh", "periodicity": "mensile"}],
        "terms": ["TAEG"],
    }}
    monkeypatch.setattr(extraction, "run_cli", _fake_cli(payload=payload))
    result = extraction.extract_budget_items(pdf)
    assert result["incomes"][0]["periodicity"] == "mensile"
    expense = result["expenses"][0]
    assert expense["category"] == "Altro"
    assert expense["type"] == "variabile"
    assert expense["amount"] == 4.9
    assert expense["source"] == "doc.pdf"
    assert result["terms"] == ["TAEG"]


def test_one_off_expense_is_never_spread_over_the_year(monkeypatch, pdf):
    payload = {"structured_output": {"incomes": [], "expenses": [
        {"label": "Acquisto libri", "amount": 45, "category": "Svago/discrezionale",
         "type": "una tantum", "periodicity": "annuale"},
    ]}}
    monkeypatch.setattr(extraction, "run_cli", _fake_cli(payload=payload))
    expense = extraction.extract_budget_items(pdf)["expenses"][0]
    assert expense["periodicity"] == "mensile" and expense["amount"] == 45


def test_pdf_is_read_with_read_tool_and_json_schema(monkeypatch, pdf):
    fake = _fake_cli(payload={"structured_output": {"incomes": [], "expenses": []}})
    monkeypatch.setattr(extraction, "run_cli", fake)
    extraction.extract_budget_items(pdf)
    assert "Read" in fake.args and "--json-schema" in fake.args and "--add-dir" in fake.args


def test_label_blocked_by_guardrail_keeps_amount(monkeypatch, pdf):
    # QA-13: la voce non sparisce (i totali resterebbero alterati), cambia solo l'etichetta
    payload = {"structured_output": {"incomes": [], "expenses": [
        {"label": "Ti consiglio di investire qui", "amount": 50, "category": "Altro",
         "type": "fissa", "periodicity": "mensile"},
    ]}}
    monkeypatch.setattr(extraction, "run_cli", _fake_cli(payload=payload))
    result = extraction.extract_budget_items(pdf)
    assert result["flagged"] == 1
    assert result["expenses"][0]["label"] == extraction.FLAGGED_LABEL
    assert result["expenses"][0]["amount"] == 50
