from app.content_guard import find_violations, is_compliant


def test_allows_educational_explanation():
    text = "Il TAEG rappresenta il costo totale del prestito in percentuale annua."
    assert is_compliant(text)


def test_allows_bill_breakdown():
    text = "Questa voce in bolletta è il canone fisso, indipendente dai consumi."
    assert is_compliant(text)


def test_blocks_investment_advice():
    text = "Ti consiglio di investire in questo fondo pensione."
    assert not is_compliant(text)
    assert find_violations(text)


def test_blocks_buy_recommendation():
    text = "Dovresti comprare questo prodotto finanziario subito."
    assert not is_compliant(text)
