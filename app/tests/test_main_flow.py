"""Test del flusso UI con streamlit.testing (headless, nessuna chiamata AI)."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

from finsup import demo_data

MAIN = str(Path(__file__).resolve().parents[1] / "main.py")


def _app() -> AppTest:
    return AppTest.from_file(MAIN, default_timeout=30).run()


def _click(at: AppTest, text: str) -> AppTest:
    next(b for b in at.button if text in b.label).click()
    return at.run()


def test_disclaimer_always_visible_and_flow_starts_at_input():
    at = _app()
    assert not at.exception
    assert any("non consulenza finanziaria" in i.value for i in at.info)
    assert at.session_state.step == "input"


def test_demo_data_goes_through_mandatory_confirmation():
    at = _click(_app(), "dati di esempio")
    at = _click(at, "Vai alla conferma")
    assert at.session_state.step == "conferma"
    assert not at.metric  # RF-09: nessun calcolo prima della conferma
    at = _click(at, "Confermo i dati")
    assert at.session_state.step == "risultati"
    values = {m.label: m.value for m in at.metric}
    assert values["Risparmio al mese"] == "37,46 €"
    assert not at.error  # risparmio positivo: nessun avviso RF-06
    assert any("non consulenza finanziaria" in i.value for i in at.info)


def test_results_without_confirmation_redirect_to_confirmation():
    at = _app()
    at.session_state.step = "risultati"
    at.run()
    assert at.session_state.step == "conferma"
    assert not at.metric


def test_negative_savings_highlighted_without_prescriptions():
    at = _app()
    incomes = [i for i in demo_data.INCOMES if i["periodicity"] == "mensile"]
    at.session_state.confirmed = {"incomes": incomes, "expenses": demo_data.EXPENSES}
    at.session_state.step = "risultati"
    at.run()
    assert at.error, "RF-06: il risparmio negativo va evidenziato"
    message = at.error[0].value
    assert "superano" in message and "Abitazione" in message
    from finsup.content_guard import find_violations
    assert not find_violations(message)
