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


def test_entered_data_goes_through_mandatory_confirmation():
    at = _app()
    at.session_state.incomes, at.session_state.expenses = demo_data.INCOMES, demo_data.EXPENSES
    at.run()
    at = _click(at, "Vai alla conferma")
    assert at.session_state.step == "conferma"
    assert not at.metric  # RF-09: nessun calcolo prima della conferma
    at = _click(at, "Confermo i dati")
    assert at.session_state.step == "risultati"
    values = {m.label: m.value for m in at.metric}
    assert values["Risparmio al mese"] == "-81,56 €"  # scenario di default: Marco, basso risparmio
    assert at.error  # risparmio negativo: avviso RF-06
    assert any("non consulenza finanziaria" in i.value for i in at.info)


def test_duplicates_removed_automatically_are_shown_in_confirmation():
    at = _app()
    at.session_state.duplicates = [{"label": "Accredito stipendio", "amount": 1408.73, "source": "estratto.xlsx",
                                    "duplicate_of": "«Netto a pagare» (busta_paga.pdf)"}]
    at.session_state.step = "conferma"
    at.run()
    assert not at.exception
    assert any("Voci doppie" in m.value for m in at.markdown)
    assert not at.warning or all("doppione" not in w.value for w in at.warning)  # niente avvisi da gestire


def test_custom_expense_can_be_added_in_confirmation():
    at = _app()
    at.session_state.incomes, at.session_state.expenses = demo_data.INCOMES, demo_data.EXPENSES
    at.session_state.step = "conferma"
    at.run()
    at.text_input(key="add_label").input("Ripetizioni di inglese")
    at.number_input(key="add_amount").set_value(80.0)
    at.run()  # come nel browser: il pulsante si abilita dopo aver compilato i campi
    at = _click(at, "Aggiungi")
    assert at.session_state.step == "conferma"
    added = [e for e in at.session_state.expenses if e["label"] == "Ripetizioni di inglese"]
    assert added and added[0]["amount"] == 80.0 and added[0]["category"] == "Altro"
    assert len(at.session_state.expenses) == len(demo_data.EXPENSES) + 1


def test_results_without_confirmation_redirect_to_confirmation():
    at = _app()
    at.session_state.step = "risultati"
    at.run()
    assert at.session_state.step == "conferma"
    assert not at.metric


def test_negative_savings_highlighted_without_prescriptions():
    at = _app()
    at.session_state.confirmed = {"incomes": demo_data.MARCO["incomes"], "expenses": demo_data.MARCO["expenses"]}
    at.session_state.step = "risultati"
    at.run()
    assert at.error, "RF-06: il risparmio negativo va evidenziato"
    message = at.error[0].value
    assert "superano" in message and "Abitazione" in message
    from finsup.content_guard import find_violations
    assert not find_violations(message)
