"""I due scenari della demo, trascritti dai documenti in `app/demo_assets/`.

Documenti fittizi forniti dal team (persone, aziende e banche inesistenti):
- Marco Ferretti, basso risparmio: busta paga + bolletta + estratto conto
- Alessandra Moretti, alto risparmio: busta paga + estratto conto

Le voci sono quelle che l'utente avrebbe dopo la conferma RF-09: lo
stipendio contato una volta sola (busta paga e accredito in estratto conto
sono lo stesso denaro) e, per Marco, la bolletta per servizio al posto del
suo addebito RID in estratto conto. Le categorie seguono la spec (§4.2):
mutuo e affitto in Abitazione, ristorazione in Alimentari.

Servono da valori attesi nei test: sono gli stessi numeri che l'app produce
estraendo i 5 documenti reali (Marco -81,56, Alessandra 1.132,24 al mese).
`INCOMES`, `EXPENSES` e `TERMS` restano come alias dello scenario di default.
"""


def _exp(label, amount, category, type_, periodicity="mensile"):
    return {"label": label, "amount": amount, "category": category, "type": type_, "periodicity": periodicity}


def _inc(label, amount, periodicity="mensile"):
    return {"label": label, "amount": amount, "periodicity": periodicity}


MARCO = {
    "person": "Marco Ferretti",
    "title": "Marco · basso risparmio",
    "files": [
        "marco_bustapaga.pdf",
        "marco_bolletta.pdf",
        "marco_estrattoconto.xlsx",
    ],
    "incomes": [
        _inc("Stipendio netto (busta paga GranSuper Distribuzione)", 1408.73),
    ],
    "expenses": [
        _exp("Affitto Via dei Navigli 8", 650.00, "Abitazione", "fissa"),
        _exp("Energia elettrica (bolletta NordEst)", 58.05, "Abitazione", "fissa"),
        _exp("Gas naturale (bolletta NordEst)", 39.77, "Abitazione", "fissa"),
        _exp("Internet fibra (bolletta NordEst)", 30.38, "Abitazione", "fissa"),
        _exp("Imposta di bollo sulla bolletta", 2.00, "Altro", "fissa"),
        _exp("Interessi di mora sulla bolletta di agosto", 0.75, "Debiti/finanziamenti", "variabile"),
        _exp("Rata prestito personale BancaAmici (TAEG 8,99%)", 285.00, "Debiti/finanziamenti", "fissa"),
        _exp("Assicurazione RC auto Generali", 75.00, "Assicurazioni", "fissa"),
        _exp("Supermercato Esselunga", 87.50, "Alimentari", "variabile"),
        _exp("Supermercato Lidl", 68.30, "Alimentari", "variabile"),
        _exp("Supermercato Pam", 64.20, "Alimentari", "variabile"),
        _exp("Abbonamento mezzi ATM", 35.00, "Trasporti", "semi-fissa"),
        _exp("Prelievo contanti", 40.00, "Altro", "variabile"),
        _exp("Netflix + Spotify", 22.99, "Svago/discrezionale", "variabile"),
        _exp("Canone conto corrente", 8.50, "Altro", "fissa"),
        _exp("Commissione di gestione conto", 2.00, "Altro", "fissa"),
        _exp("Imposta di bollo sul conto corrente", 8.55, "Altro", "fissa", "trimestrale"),
        _exp("Bar e spese quotidiane", 18.00, "Svago/discrezionale", "variabile"),
    ],
    "terms": [
        "TAEG", "Interessi di mora", "Imposta di bollo", "Commissione di gestione",
        "Oneri di sistema", "Accise", "Quota rete (distribuzione)", "Addebito diretto (SDD/RID)",
        "IRPEF", "Contributi INPS", "Addizionale regionale e comunale", "TFR",
    ],
    # Valori mensili attesi (bollo trimestrale 8,55 -> 2,85 al mese, RF-02).
    "expected": {"income": 1408.73, "expenses": 1490.29, "savings": -81.56},
}

ALESSANDRA = {
    "person": "Alessandra Moretti",
    "title": "Alessandra · alto risparmio",
    "files": [
        "alessandra_bustapaga.pdf",
        "alessandra_estrattoconto.xlsx",
    ],
    "incomes": [
        _inc("Stipendio netto (busta paga Innovatech Solutions)", 2576.34),
        _inc("Canone di locazione percepito", 720.00),
    ],
    "expenses": [
        _exp("Rata mutuo prima casa (TAEG 3,75%)", 900.00, "Abitazione", "fissa"),
        _exp("Bolletta luce, gas e internet (addebito RID)", 180.00, "Abitazione", "fissa"),
        _exp("Assicurazione RC auto Allianz", 95.00, "Assicurazioni", "fissa"),
        _exp("Polizza vita PosteVita", 20.00, "Assicurazioni", "fissa"),
        _exp("Supermercato Esselunga", 127.40, "Alimentari", "variabile"),
        _exp("Supermercato Conad", 98.60, "Alimentari", "variabile"),
        _exp("Supermercato Carrefour", 164.00, "Alimentari", "variabile"),
        _exp("Ristorante Il Glicine", 78.50, "Alimentari", "variabile"),
        _exp("Abbonamento trasporti GTT", 80.00, "Trasporti", "semi-fissa"),
        _exp("Palestra Virgin Active", 59.00, "Salute e benessere", "semi-fissa"),
        _exp("Farmacia", 32.00, "Salute e benessere", "semi-fissa"),
        _exp("Prelievo contanti", 200.00, "Altro", "variabile"),
        _exp("Libreria Feltrinelli", 45.00, "Svago/discrezionale", "variabile"),
        _exp("Amazon: Prime e acquisti vari", 67.50, "Svago/discrezionale", "variabile"),
        _exp("Canone conto corrente", 8.50, "Altro", "fissa"),
        _exp("Commissione di gestione conto", 2.00, "Altro", "fissa"),
        _exp("Imposta di bollo sul conto corrente", 8.55, "Altro", "fissa", "trimestrale"),
        _exp("Spese di istruttoria rinnovo fido (TAEG 8,75%)", 45.00, "Altro", "fissa", "annuale"),
    ],
    "terms": [
        "TAEG", "Imposta di bollo", "Commissione di gestione", "Addebito diretto (SDD/RID)",
        "RC auto", "IRPEF", "Contributi INPS", "Addizionale regionale e comunale",
        "TFR", "Detrazioni", "Imponibile", "Scatto di anzianità",
    ],
    # Valori mensili attesi (bollo 8,55/3 e istruttoria 45/12, RF-02).
    "expected": {"income": 3296.34, "expenses": 2164.10, "savings": 1132.24},
}

SCENARIOS = {"marco": MARCO, "alessandra": ALESSANDRA}
DEFAULT_SCENARIO = "marco"

INCOMES = SCENARIOS[DEFAULT_SCENARIO]["incomes"]
EXPENSES = SCENARIOS[DEFAULT_SCENARIO]["expenses"]
TERMS = SCENARIOS[DEFAULT_SCENARIO]["terms"]
