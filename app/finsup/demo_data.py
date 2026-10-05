"""Dati demo completamente inventati (persona fittizia, nessun dato reale).

Unica fonte di verita' sia per i documenti demo generati da
`scripts/generate_demo_assets.py` (busta paga, estratto conto, foglio
spese) sia per il pulsante "Carica dati di esempio" dell'app, che fa da
fallback se l'estrazione da file non e' disponibile durante la demo.
"""

PERSON = "Laura Esempio"  # nome fittizio

PAYSLIP = {
    "employer": "Officine Demo S.r.l. (azienda fittizia)",
    "month": "Settembre 2026",
    "gross": 2180.00,
    "inps": 200.34,          # contributi previdenziali 9,19%
    "irpef_gross": 485.00,
    "irpef_deductions": 163.94,
    "regional_surcharge": 28.40,
    "municipal_surcharge": 10.20,
    "net": 1620.00,
    "tfr_month": 161.48,     # accantonato, non pagato in busta
}

INCOMES = [
    {"label": "Stipendio netto (busta paga)", "amount": 1620.00, "periodicity": "mensile"},
    {"label": "Collaborazioni occasionali (netto ritenuta d'acconto)", "amount": 1200.00, "periodicity": "annuale"},
]

# Addebiti dell'estratto conto di settembre (mensili, tranne l'imposta di bollo).
BANK_EXPENSES = [
    {"label": "Affitto", "amount": 650.00, "category": "Abitazione", "type": "fissa", "periodicity": "mensile"},
    {"label": "Bolletta luce e gas (addebito SDD)", "amount": 95.00, "category": "Abitazione", "type": "fissa", "periodicity": "mensile"},
    {"label": "Internet fibra", "amount": 29.90, "category": "Abitazione", "type": "fissa", "periodicity": "mensile"},
    {"label": "Rata prestito auto (TAEG 8,45%)", "amount": 185.00, "category": "Debiti/finanziamenti", "type": "fissa", "periodicity": "mensile"},
    {"label": "Interessi di mora rata di agosto", "amount": 12.40, "category": "Debiti/finanziamenti", "type": "variabile", "periodicity": "mensile"},
    {"label": "Commissione di gestione conto", "amount": 4.90, "category": "Altro", "type": "fissa", "periodicity": "mensile"},
    {"label": "Imposta di bollo", "amount": 8.55, "category": "Altro", "type": "fissa", "periodicity": "trimestrale"},
    {"label": "Supermercato", "amount": 310.00, "category": "Alimentari", "type": "variabile", "periodicity": "mensile"},
    {"label": "Ristoranti e bar", "amount": 70.00, "category": "Alimentari", "type": "variabile", "periodicity": "mensile"},
    {"label": "Carburante", "amount": 85.00, "category": "Trasporti", "type": "semi-fissa", "periodicity": "mensile"},
    {"label": "Abbonamento mezzi pubblici", "amount": 35.00, "category": "Trasporti", "type": "semi-fissa", "periodicity": "mensile"},
    {"label": "Palestra", "amount": 39.00, "category": "Salute e benessere", "type": "semi-fissa", "periodicity": "mensile"},
    {"label": "Farmacia", "amount": 18.00, "category": "Salute e benessere", "type": "semi-fissa", "periodicity": "mensile"},
    {"label": "Abbonamento streaming", "amount": 12.99, "category": "Svago/discrezionale", "type": "variabile", "periodicity": "mensile"},
    {"label": "Shopping online", "amount": 55.00, "category": "Svago/discrezionale", "type": "variabile", "periodicity": "mensile"},
]

# Foglio spese personale (XLSX): voci annuali, da normalizzare su base mensile.
SHEET_EXPENSES = [
    {"label": "Assicurazione auto RC (franchigia 500 €)", "amount": 540.00, "category": "Assicurazioni", "type": "fissa", "periodicity": "annuale"},
    {"label": "Bollo auto", "amount": 210.00, "category": "Trasporti", "type": "semi-fissa", "periodicity": "annuale"},
    {"label": "TARI (tassa rifiuti)", "amount": 180.00, "category": "Abitazione", "type": "fissa", "periodicity": "annuale"},
]

EXPENSES = BANK_EXPENSES + SHEET_EXPENSES

# Termini tecnici presenti nei documenti demo (per il glossario RF-04).
TERMS = [
    "TAEG", "TAN", "Interessi di mora", "Commissione di gestione", "Imposta di bollo",
    "Contributi INPS", "IRPEF", "Addizionale regionale", "TFR", "Ritenuta d'acconto", "Franchigia",
]
