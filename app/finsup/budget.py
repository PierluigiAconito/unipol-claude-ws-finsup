"""Logica di calcolo del budget (RF-02, RF-03, RF-05, RF-06, RF-07).

Puro Python, deterministico, nessuna chiamata AI: i numeri mostrati
all'utente non dipendono mai da un LLM. Le voci sono dict con chiavi
`label`, `amount`, `periodicity` (+ `category`, `type` per le uscite),
cosi' arrivano direttamente dalle tabelle della UI o dall'estrazione.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

PERIODICITY_MONTHS = {"mensile": 1, "trimestrale": 3, "annuale": 12}
PERIODICITIES = list(PERIODICITY_MONTHS)

# Categorie di spesa della spec (§4.2), nell'ordine in cui vanno mostrate:
# l'ordine fissa anche il colore di ciascuna categoria nei grafici.
CATEGORIES = [
    "Abitazione",
    "Debiti/finanziamenti",
    "Assicurazioni",
    "Trasporti",
    "Salute e benessere",
    "Alimentari",
    "Svago/discrezionale",
    "Altro",
]
# "una tantum": spesa che capita una volta sola (es. una riparazione). Conta nel
# mese in cui si paga, come le altre; il tipo serve a leggere la composizione.
EXPENSE_TYPES = ["fissa", "semi-fissa", "variabile", "una tantum"]
DEFAULT_TYPE = {
    "Abitazione": "fissa",
    "Debiti/finanziamenti": "fissa",
    "Assicurazioni": "fissa",
    "Trasporti": "semi-fissa",
    "Salute e benessere": "semi-fissa",
    "Alimentari": "variabile",
    "Svago/discrezionale": "variabile",
    "Altro": "variabile",
}

# Regola 50/30/20 (RF-05): semplificazione dichiarata di FinSup. Solo lo
# svago conta come "desideri"; "Altro" resta tra le necessita' perche' nei
# documenti reali raccoglie soprattutto costi obbligatori (commissioni
# bancarie, imposte), che non sarebbe corretto presentare come desideri.
WANTS_CATEGORIES = {"Svago/discrezionale"}
NEEDS_CATEGORIES = set(CATEGORIES) - WANTS_CATEGORIES
BENCHMARK_503020 = {"Necessità": 0.50, "Desideri": 0.30, "Risparmio": 0.20}


def to_monthly(amount, periodicity: str | None) -> float:
    """RF-02: riporta un importo alla sua quota mensile (annuale / 12, ...)."""
    months = PERIODICITY_MONTHS.get((periodicity or "mensile").strip().lower(), 1)
    return _number(amount) / months


@dataclass
class BudgetSummary:
    total_income: float
    total_expenses: float
    savings: float
    savings_rate: float  # risparmio / entrate, 0..1 (negativo se in perdita)
    by_category: dict[str, float] = field(default_factory=dict)  # quota mensile
    by_type: dict[str, float] = field(default_factory=dict)

    def category_share(self, category: str) -> float:
        """Incidenza della categoria sul totale uscite (0..1)."""
        return self.by_category.get(category, 0.0) / self.total_expenses if self.total_expenses else 0.0

    def type_share_of_income(self, expense_type: str) -> float:
        """Peso di spese fisse/semi-fisse/variabili sul totale entrate (0..1)."""
        return self.by_type.get(expense_type, 0.0) / self.total_income if self.total_income else 0.0


def compute_budget(incomes: list[dict], expenses: list[dict]) -> BudgetSummary:
    """RF-03: entrate e uscite mensili, risparmio e indicatori derivati (§5)."""
    total_income = sum(to_monthly(i.get("amount"), i.get("periodicity")) for i in incomes)

    by_category = {c: 0.0 for c in CATEGORIES}
    by_type = {t: 0.0 for t in EXPENSE_TYPES}
    for e in expenses:
        monthly = to_monthly(e.get("amount"), e.get("periodicity"))
        category = e.get("category") if e.get("category") in by_category else "Altro"
        expense_type = e.get("type") if e.get("type") in by_type else DEFAULT_TYPE[category]
        by_category[category] += monthly
        by_type[expense_type] += monthly

    total_expenses = sum(by_category.values())
    savings = total_income - total_expenses
    return BudgetSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        savings=savings,
        savings_rate=savings / total_income if total_income else 0.0,
        by_category=by_category,
        by_type=by_type,
    )


def top_categories(summary: BudgetSummary, n: int = 3) -> list[tuple[str, float]]:
    """RF-06: categorie che pesano di piu' sul totale uscite, con la quota (0..1)."""
    ranked = sorted(summary.by_category.items(), key=lambda kv: kv[1], reverse=True)
    return [(c, summary.category_share(c)) for c, v in ranked[:n] if v > 0]


def benchmark_503020(summary: BudgetSummary) -> list[dict]:
    """RF-05: confronto informativo con la regola 50/30/20, in EUR e in %."""
    needs = sum(v for c, v in summary.by_category.items() if c in NEEDS_CATEGORIES)
    actual = {
        "Necessità": needs,
        "Desideri": summary.total_expenses - needs,
        "Risparmio": summary.savings,
    }
    income = summary.total_income
    return [
        {
            "bucket": bucket,
            "actual": actual[bucket],
            "actual_pct": actual[bucket] / income if income else 0.0,
            "reference": income * pct,
            "reference_pct": pct,
        }
        for bucket, pct in BENCHMARK_503020.items()
    ]


def months_to_goal(goal: float, monthly_savings: float) -> int | None:
    """RF-07: mesi per raggiungere l'obiettivo al ritmo attuale; None se irraggiungibile."""
    if monthly_savings <= 0:
        return None
    if goal <= 0:
        return 0
    return math.ceil(goal / monthly_savings)


def possible_duplicates(items: list[dict]) -> list[tuple[dict, dict]]:
    """RF-09: coppie di voci con lo stesso importo lette da file diversi.

    Due casi tipici:
    - lo stipendio nella busta paga e il suo accredito nell'estratto conto;
    - l'addebito di una bolletta nell'estratto conto e la bolletta stessa,
      che l'estrazione divide per servizio: si confronta con il totale delle
      voci di quel file (la seconda voce della coppia ha `is_total=True`).
    Se un file e' gia' abbinato come totale a una voce di un altro file, le
    sue singole voci non vengono confrontate con quel file: una bolletta
    pagata dal conto non e' anche "bollo 2,00 = commissione 2,00" (QA-45).
    """
    by_source: dict[str, list[dict]] = {}
    for item in items:
        if item.get("source"):
            by_source.setdefault(item["source"], []).append(item)

    total_pairs, linked = [], set()  # linked: coppie di file gia' spiegate da un totale
    for a in items:
        for source, group in by_source.items():
            if len(group) < 2 or source == a.get("source") or not a.get("source"):
                continue
            total = {"label": f"totale delle voci di {source}", "source": source, "is_total": True,
                     "amount": round(sum(_number(g.get("amount")) for g in group), 2)}
            if _same_amount(a, total):
                total_pairs.append((a, total))
                linked.add(frozenset((source, a["source"])))

    pairs = []
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if (_same_amount(a, b) and _different_files(a, b)
                    and frozenset((a["source"], b["source"])) not in linked):
                pairs.append((a, b))
    return pairs + total_pairs


def remove_duplicates(items: list[dict], new_sources: set[str] | None = None) -> tuple[list[dict], list[dict]]:
    """Toglie le voci doppie tra file diversi: ogni importo conta una volta sola.

    Avere la stessa voce in due documenti e' normale (busta paga + estratto
    conto), quindi non si chiede all'utente di cancellarla. Quale copia resta:
    - addebito uguale al totale di un altro file: restano le voci dettagliate
      (es. la bolletta per servizio), si toglie l'addebito;
    - stesso importo in due file: si toglie la copia del file con piu' voci
      (l'estratto conto, che riporta solo il movimento) e resta quella del
      documento d'origine (es. la busta paga).
    Ritorna (voci tenute, voci tolte); ogni voce tolta ha `duplicate_of` con
    la voce che la sostituisce, cosi' la UI la mostra e niente sparisce in silenzio.

    `new_sources`: i file dell'ultimo caricamento. Se indicato, si toglie solo
    dove almeno una voce della coppia e' nuova: le voci gia' controllate non
    vengono rimesse in discussione (altrimenti, tolto l'addebito della
    bolletta, bollo 2,00 e commissione 2,00 tornerebbero "doppioni").
    """
    per_source: dict[str, int] = {}
    for item in items:
        if item.get("source"):
            per_source[item["source"]] = per_source.get(item["source"], 0) + 1

    removed: dict[int, str] = {}
    for a, b in possible_duplicates(items):
        if new_sources is not None and a.get("source") not in new_sources and b.get("source") not in new_sources:
            continue
        if b.get("is_total"):
            victim, kept_label = a, f"{b['label']} ({eur(b['amount'])})"
        else:
            victim, keeper = (a, b) if per_source[a["source"]] > per_source[b["source"]] else (b, a)
            if id(keeper) in removed:
                continue
            kept_label = f"«{keeper['label']}» ({keeper['source']})"
        removed.setdefault(id(victim), kept_label)

    kept = [i for i in items if id(i) not in removed]
    dropped = [dict(i, duplicate_of=removed[id(i)]) for i in items if id(i) in removed]
    return kept, dropped


def _same_amount(a: dict, b: dict) -> bool:
    return _number(a.get("amount")) > 0 and abs(_number(a.get("amount")) - _number(b.get("amount"))) < 0.005


def _different_files(a: dict, b: dict) -> bool:
    return bool(a.get("source") and b.get("source") and a.get("source") != b.get("source"))


def eur(value: float) -> str:
    """Formato italiano: 1.234,56 € (RF-08, solo EUR)."""
    text = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} €"


def _number(value) -> float:
    """Importo numerico robusto alle celle vuote/NaN delle tabelle editabili."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if math.isnan(number) else number
