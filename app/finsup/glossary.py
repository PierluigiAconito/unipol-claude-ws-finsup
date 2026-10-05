"""RF-04: glossario contestuale dei termini tecnici.

1. `detect_terms` riconosce i termini nelle voci confermate e tra quelli
   segnalati dall'estrazione (deterministico, nessun token speso).
2. I termini gia' in `KNOWN_TERMS` usano una definizione preparata con
   Claude e rivista a mano (0 token a runtime, gia' verificata).
3. Per gli altri `explain_with_ai` fa UNA sola chiamata a Claude con
   output JSON, solo su richiesta dell'utente. Ogni spiegazione passa da
   `content_guard` PRIMA di essere mostrata: se viola il vincolo "niente
   consigli" non viene mostrata.
"""
from __future__ import annotations

import json
import re

from finsup.ai_client import run_cli
from finsup.content_guard import find_violations
from finsup.prompts import load_prompt

MAX_TERMS = 25
MAX_AI_TERMS = 10

# termine -> (pattern di riconoscimento, definizione rivista a mano).
# L'ordine conta: i termini piu' specifici prima (es. addizionale prima di IRPEF).
KNOWN_TERMS: dict[str, tuple[str, str]] = {
    "TAEG": (
        r"\btaeg\b",
        "Tasso Annuo Effettivo Globale: indica in percentuale quanto costa davvero un prestito in un "
        "anno, contando sia gli interessi sia le altre spese obbligatorie (ad esempio le commissioni).",
    ),
    "TAN": (
        r"\btan\b",
        "Tasso Annuo Nominale: è la percentuale dei soli interessi che si pagano in un anno su un "
        "prestito, senza le altre spese. Per questo di solito è più basso del TAEG.",
    ),
    "Interessi di mora": (
        r"\bmora\b",
        "Sono interessi in più che si pagano quando una rata o una bolletta viene pagata dopo la "
        "scadenza: una specie di penale per il ritardo.",
    ),
    "Commissione di gestione": (
        r"commission[ei] di gestione",
        "Su un conto corrente è il costo che la banca addebita a intervalli regolari per tenerlo "
        "aperto e gestirlo (spesso si chiama anche canone). Per altri prodotti, come i fondi, lo "
        "stesso nome indica il costo per la loro gestione.",
    ),
    "Imposta di bollo": (
        r"imposta di bollo",
        "È una tassa dello Stato che la banca trattiene dal conto e versa allo Stato: non è un "
        "guadagno della banca.",
    ),
    "Addebito diretto (SDD/RID)": (
        r"\bsdd\b|\brid\b|addebito (diretto|automatico)",
        "È un pagamento che parte in automatico dal conto alla scadenza, dopo che lo hai "
        "autorizzato una volta. Oggi si chiama SDD (dall'inglese SEPA Direct Debit, il sistema "
        "europeo dei pagamenti); RID è il nome che si usava prima.",
    ),
    "Contributi INPS": (
        r"\binps\b|contributi previdenziali",
        "Sono la parte dello stipendio lordo che viene trattenuta e versata all'INPS: servono a "
        "finanziare la pensione e altre tutele, come malattia e disoccupazione.",
    ),
    "Addizionale regionale e comunale": (
        r"addizional[ei]",
        "Sono piccole tasse sul reddito che si aggiungono all'IRPEF e vanno alla Regione e al Comune "
        "in cui vivi; in busta paga vengono trattenute a rate.",
    ),
    "Imponibile": (
        r"imponibile",
        "È l'importo su cui si calcola una tassa. In busta paga l'imponibile IRPEF è lo stipendio "
        "lordo meno i contributi previdenziali.",
    ),
    "Detrazioni": (
        r"detrazion[ei]",
        "Sono sconti sulle tasse: riducono l'IRPEF da pagare. Quelle per lavoro dipendente "
        "dipendono dal reddito e vengono applicate direttamente in busta paga.",
    ),
    "IRPEF": (
        r"\birpef\b",
        "Imposta sul Reddito delle Persone Fisiche: è la principale tassa sui redditi. Il datore di "
        "lavoro la trattiene dallo stipendio lordo e la versa allo Stato.",
    ),
    "Trattenute": (
        r"trattenut[ae]",
        "Sono le somme tolte dallo stipendio lordo (tasse e contributi) prima del pagamento: per "
        "questo il netto in busta è più basso del lordo.",
    ),
    "TFR": (
        r"\btfr\b|trattamento di fine rapporto",
        "Trattamento di Fine Rapporto: una somma che il datore di lavoro mette da parte ogni mese. "
        "Non fa parte dello stipendio del mese: di solito si riceve quando il rapporto di lavoro "
        "finisce, oppure va a un fondo pensione se il lavoratore lo ha scelto.",
    ),
    "Ritenuta d'acconto": (
        r"ritenut[ae] d['’]acconto",
        "È una parte del compenso che chi ti paga trattiene e versa allo Stato come anticipo delle "
        "tasse dovute su quel reddito (per le collaborazioni occasionali di solito è il 20%).",
    ),
    "Franchigia": (
        r"franchigia",
        "Nelle assicurazioni è la parte del danno che resta a carico dell'assicurato: con una "
        "franchigia di 500 €, i primi 500 € di ogni danno sono a tuo carico.",
    ),
    "RC auto": (
        r"\brc\b|responsabilit[aà] civile",
        "Responsabilità Civile auto: è l'assicurazione obbligatoria che copre i danni che il veicolo "
        "causa ad altre persone o a cose di altri.",
    ),
    "Bollo auto": (
        r"\bbollo auto\b|^bollo$",
        "È la tassa che si paga ogni anno alla Regione per il fatto di possedere un'auto o una moto, "
        "anche se non la si usa.",
    ),
    "TARI": (
        r"\btari\b",
        "È la tassa sui rifiuti: si paga al Comune per il servizio di raccolta e smaltimento dei rifiuti.",
    ),
    "CCNL": (
        r"\bccnl\b|contratto collettivo",
        "Contratto Collettivo Nazionale di Lavoro: l'accordo tra sindacati e datori di lavoro che "
        "fissa per un settore le regole comuni, come livelli, paga minima, ferie e orari.",
    ),
    "Scatto di anzianità": (
        r"scatt[oi] di anzianit",
        "È un aumento dello stipendio che il contratto di lavoro prevede dopo un certo numero di "
        "anni passati nella stessa azienda.",
    ),
    "Oneri di sistema": (
        r"oneri di sistema",
        "Sono una parte della bolletta che non paga l'energia consumata ma costi generali del "
        "sistema elettrico e del gas fissati per legge, come gli incentivi alle fonti rinnovabili. "
        "Li pagano tutti i clienti.",
    ),
    "Accise": (
        r"\baccis[ae]\b",
        "Sono imposte dello Stato sul consumo di energia elettrica e gas: di solito crescono con la "
        "quantità consumata e sono già comprese nel totale della bolletta.",
    ),
    "Quota rete (distribuzione)": (
        r"quota rete|distribuzione",
        "È la parte della bolletta che paga il trasporto dell'energia o del gas fino a casa e la "
        "gestione del contatore. Una parte è fissa: si paga anche se si consuma poco.",
    ),
    "Quota potenza": (
        r"quota potenza|potenza impegnata",
        "È la parte fissa della bolletta della luce che dipende dalla potenza del contatore (ad "
        "esempio 3 kW), cioè da quanti apparecchi si possono usare insieme. Non dipende dai consumi.",
    ),
    "POD e PDR": (
        r"\bpod\b|\bpdr\b",
        "Sono i codici che identificano il punto in cui arriva la fornitura: il POD per la luce, il "
        "PDR per il gas. Servono a riconoscere la tua fornitura nelle comunicazioni con il fornitore.",
    ),
    "IVA": (
        r"\biva\b",
        "Imposta sul Valore Aggiunto: una tassa compresa nel prezzo di beni e servizi, che il "
        "venditore versa allo Stato. La percentuale cambia a seconda del servizio (ad esempio 10% o 22%).",
    ),
}

AI_SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
        "term": {"type": "string"},
        "explanation": {"type": "string"},
    }, "required": ["term", "explanation"]}}},
    "required": ["items"],
}

_COMPILED = {term: re.compile(pattern, re.IGNORECASE) for term, (pattern, _) in KNOWN_TERMS.items()}


def detect_terms(labels: list[str], doc_terms: list[str] | None = None) -> list[tuple[str, str]]:
    """Ritorna (termine, contesto) per i termini tecnici trovati, senza duplicati."""
    found: dict[str, str] = {}
    for label in labels:
        for term, pattern in _COMPILED.items():
            if term not in found and pattern.search(label or ""):
                found[term] = label
    for raw in doc_terms or []:
        term = _canonical(raw)
        if term:
            found.setdefault(term, "documento caricato")
    return list(found.items())[:MAX_TERMS]


def known_definitions(terms: list[tuple[str, str]]) -> list[dict]:
    """Definizioni riviste a mano per i termini noti: nessuna chiamata AI."""
    return [{"term": t, "text": KNOWN_TERMS[t][1]} for t, _ in terms if t in KNOWN_TERMS]


def unknown_terms(terms: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [(t, c) for t, c in terms if t not in KNOWN_TERMS][:MAX_AI_TERMS]


def explain_with_ai(terms: list[tuple[str, str]]) -> dict:
    """Una sola chiamata a Claude per tutti i termini non noti.

    Ritorna {"items": [{"term", "text"}], "blocked": [termini], "error", "cost_usd"}.
    Le spiegazioni bloccate dal guardrail non finiscono mai in `items`.
    """
    if not terms:
        return {"items": [], "blocked": [], "error": None, "cost_usd": 0.0}
    prompt = "Spiega questi termini, ciascuno nel suo contesto:\n" + "\n".join(
        f'- {term} (compare in: "{context}")' for term, context in terms
    )
    payload, error = run_cli(
        prompt,
        # un tool attivo serve allo structured output (con --tools "" viene ignorato)
        ["--tools", "Read", "--json-schema", json.dumps(AI_SCHEMA)],
        system_prompt=load_prompt("glossario"),
    )
    if error or not isinstance(payload.get("structured_output"), dict):
        return {"items": [], "blocked": [], "error": error or "risposta senza dati strutturati", "cost_usd": 0.0}

    items, blocked = [], []
    for item in payload["structured_output"].get("items", []):
        term, text = str(item.get("term", "")).strip(), str(item.get("explanation", "")).strip()
        if not term or not text:
            continue
        if find_violations(text):  # guardrail PRIMA di mostrare
            blocked.append(term)
        else:
            items.append({"term": term, "text": text})
    return {"items": items, "blocked": blocked, "error": None, "cost_usd": payload.get("total_cost_usd", 0.0)}


def _canonical(raw: str) -> str:
    raw = (raw or "").strip()
    for term, pattern in _COMPILED.items():
        if pattern.search(raw):
            return term
    return raw
