import pytest

from finsup import demo_data
from finsup.budget import (
    benchmark_503020,
    compute_budget,
    months_to_goal,
    to_monthly,
    top_categories,
)


@pytest.mark.parametrize(
    "amount, periodicity, expected",
    [(120, "mensile", 120), (120, "trimestrale", 40), (1200, "annuale", 100), (90, None, 90)],
)
def test_to_monthly_normalizes_periodicity(amount, periodicity, expected):
    assert to_monthly(amount, periodicity) == pytest.approx(expected)


@pytest.mark.parametrize("empty", [None, "", float("nan")])
def test_to_monthly_treats_empty_cells_as_zero(empty):
    assert to_monthly(empty, "mensile") == 0


def test_compute_budget_matches_spec_formula():
    incomes = [
        {"label": "Stipendio", "amount": 1500, "periodicity": "mensile"},
        {"label": "Bonus", "amount": 1200, "periodicity": "annuale"},
    ]
    expenses = [
        {"label": "Affitto", "amount": 600, "category": "Abitazione", "type": "fissa", "periodicity": "mensile"},
        {"label": "Assicurazione", "amount": 360, "category": "Assicurazioni", "type": "fissa", "periodicity": "annuale"},
        {"label": "Spesa", "amount": 300, "category": "Alimentari", "type": "variabile", "periodicity": "mensile"},
    ]
    s = compute_budget(incomes, expenses)
    assert s.total_income == pytest.approx(1600)
    assert s.total_expenses == pytest.approx(930)
    assert s.savings == pytest.approx(670)
    assert s.savings_rate == pytest.approx(670 / 1600)
    assert s.by_category["Assicurazioni"] == pytest.approx(30)
    assert s.category_share("Abitazione") == pytest.approx(600 / 930)
    assert s.type_share_of_income("fissa") == pytest.approx(630 / 1600)


def test_unknown_category_falls_back_to_altro():
    s = compute_budget([], [{"amount": 10, "category": "Boh", "periodicity": "mensile"}])
    assert s.by_category["Altro"] == 10
    assert s.by_type["variabile"] == 10


def test_demo_data_gives_small_positive_savings():
    s = compute_budget(demo_data.INCOMES, demo_data.EXPENSES)
    assert s.total_income == pytest.approx(1720)
    assert s.total_expenses == pytest.approx(1682.54)
    assert s.savings == pytest.approx(37.46)


def test_negative_savings_and_top_categories():
    s = compute_budget(
        [{"amount": 1000, "periodicity": "mensile"}],
        [
            {"amount": 800, "category": "Abitazione", "periodicity": "mensile"},
            {"amount": 300, "category": "Alimentari", "periodicity": "mensile"},
            {"amount": 0, "category": "Svago/discrezionale", "periodicity": "mensile"},
        ],
    )
    assert s.savings == pytest.approx(-100)
    top = top_categories(s)
    assert [c for c, _ in top] == ["Abitazione", "Alimentari"]  # categorie a zero escluse
    assert top[0][1] == pytest.approx(800 / 1100)


def test_benchmark_503020_splits_needs_wants_savings():
    s = compute_budget(
        [{"amount": 2000, "periodicity": "mensile"}],
        [
            {"amount": 900, "category": "Abitazione", "periodicity": "mensile"},
            {"amount": 500, "category": "Svago/discrezionale", "periodicity": "mensile"},
        ],
    )
    rows = {r["bucket"]: r for r in benchmark_503020(s)}
    assert rows["Necessità"]["actual"] == pytest.approx(900)
    assert rows["Desideri"]["actual"] == pytest.approx(500)
    assert rows["Risparmio"]["actual"] == pytest.approx(600)
    assert rows["Risparmio"]["actual_pct"] == pytest.approx(0.30)
    assert rows["Necessità"]["reference"] == pytest.approx(1000)


def test_benchmark_counts_bank_fees_in_altro_as_needs():
    # QA-08: commissioni e imposta di bollo (categoria "Altro") non sono "desideri"
    s = compute_budget(
        [{"amount": 1000, "periodicity": "mensile"}],
        [
            {"amount": 4.90, "category": "Altro", "periodicity": "mensile"},
            {"amount": 50, "category": "Svago/discrezionale", "periodicity": "mensile"},
        ],
    )
    rows = {r["bucket"]: r for r in benchmark_503020(s)}
    assert rows["Necessità"]["actual"] == pytest.approx(4.90)
    assert rows["Desideri"]["actual"] == pytest.approx(50)


def test_demo_without_side_income_shows_negative_savings():
    # QA-16: in demo basta cancellare la riga delle collaborazioni nella
    # schermata di conferma (RF-09) per mostrare il ramo RF-06.
    incomes = [i for i in demo_data.INCOMES if i["periodicity"] == "mensile"]
    s = compute_budget(incomes, demo_data.EXPENSES)
    assert s.savings == pytest.approx(-62.54)
    assert top_categories(s)[0][0] == "Abitazione"


@pytest.mark.parametrize(
    "goal, savings, expected",
    [(1000, 100, 10), (1000, 37.46, 27), (0, 50, 0), (1000, 0, None), (1000, -20, None)],
)
def test_months_to_goal(goal, savings, expected):
    assert months_to_goal(goal, savings) == expected
