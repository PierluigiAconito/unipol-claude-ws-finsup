import pytest

from finsup.content_guard import find_violations, is_compliant


@pytest.mark.parametrize(
    "text",
    [
        "Il TAEG rappresenta il costo totale del prestito in percentuale annua.",
        "Questa voce in bolletta è il canone fisso, indipendente dai consumi.",
        "La regola 50/30/20 è un riferimento: il 20% delle entrate va al risparmio.",
        "Le spese per abbonamenti pesano il 12% sulle tue uscite totali.",
        "Con questo ritmo di risparmio l'obiettivo si raggiunge in 8 mesi.",
    ],
)
def test_allows_educational_text(text):
    assert is_compliant(text), find_violations(text)


@pytest.mark.parametrize(
    "text",
    [
        "Ti consiglio di investire in questo fondo pensione.",
        "Dovresti comprare questo prodotto finanziario subito.",
        "Ti suggerisco di aprire un conto deposito.",
        "Dovresti ridurre le spese per lo svago.",
        "Ti conviene chiudere la carta revolving.",
        "Taglia gli abbonamenti streaming per risparmiare.",
        "La scelta migliore per te è il mutuo a tasso fisso.",
    ],
)
def test_blocks_advice_and_prescriptions(text):
    assert not is_compliant(text)
    assert find_violations(text)
