"""BudgetFacile: capire il proprio budget (Hagenthon, Tema 02: Inclusione Finanziaria).

Flusso in tre passi, come da requisiti (app/docs/requisiti-funzionali.md):
1. inserimento: form guidato (RF-01a) e/o documenti letti da Claude (RF-01b)
2. conferma obbligatoria voce per voce (RF-09): nessun calcolo prima
3. risultati: riepilogo e grafici (RF-03), benchmark 50/30/20 (RF-05),
   risparmio negativo (RF-06), proiezione obiettivo (RF-07), glossario (RF-04)

I numeri vengono sempre da finsup.budget (deterministico): l'AI serve solo a
leggere i documenti e a spiegare le parole tecniche, e ogni suo testo passa
dal guardrail anti-consigli prima di essere mostrato.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import altair as alt
import pandas as pd
import streamlit as st

from finsup import extraction, glossary
from finsup.budget import (
    BENCHMARK_503020,
    CATEGORIES,
    DEFAULT_TYPE,
    EXPENSE_TYPES,
    PERIODICITIES,
    benchmark_503020,
    compute_budget,
    eur,
    to_monthly,
    months_to_goal,
    remove_duplicates,
    top_categories,
)

# Nome e promessa come nella copertina della presentazione.
APP_NAME = "BudgetFacile"
TAGLINE = "Dall'ammasso di documenti a un budget chiaro in pochi minuti."

st.set_page_config(page_title=APP_NAME, page_icon="💶", layout="wide")

DISCLAIMER = (
    f"**Strumento educativo, non consulenza finanziaria.** {APP_NAME} ti aiuta a capire com'è fatto "
    "il tuo budget: non dice cosa fare con i tuoi soldi, le decisioni restano tue."
)
DUPLICATE_FILL = "#FFF4C2"  # giallo: voci doppie tolte in automatico

# Colori allineati alla presentazione (variabili :root del deck). Palette
# categoriale: apre con verde (--acc-m) e ambra (--amber) del deck, validata
# con validate_palette.js della skill dataviz sullo sfondo #F4F2ED (CVD minimo
# 11,6). Un colore fisso per categoria, che segue la categoria e non il suo
# peso. Alcuni slot sono sotto 3:1 di contrasto: per questo c'e' la tabella
# sotto il grafico. "Altro" e' nel grigio del deck, come ogni categoria residua.
CATEGORY_COLORS = dict(zip(CATEGORIES, [
    "#00A880", "#D07010", "#4a3aa7", "#eda100", "#2a78d6", "#e87ba4", "#c2410c", "#B0AFBA",
]))
ACCENT = "#006B54"          # --acc del deck: serie singola ed evidenza
REFERENCE_GRAY = "#B0AFBA"  # --hint: serie di riferimento, de-enfatizzata
LABEL_INK = "#6A6A7E"       # --muted: etichette dei valori
SURFACE = "#F4F2ED"         # --bg: separatore tra le fette della ciambella
# Assi in formato italiano: 1.200 invece di 1,200 (QA-32).
IT_AXIS = alt.Axis(labelExpr="replace(format(datum.value, ',.0f'), regexp(',', 'g'), '.')")
SERIES = ["Il tuo budget", "Riferimento 50/30/20"]

STEPS = {"input": "Inserisci le voci", "conferma": "Conferma i dati", "risultati": "Capisci il budget"}

INCOME_COLUMNS = ["label", "amount", "periodicity", "source"]
EXPENSE_COLUMNS = ["label", "amount", "category", "type", "periodicity", "source"]
INCOME_CONFIG = {
    "label": st.column_config.TextColumn("Voce", width="large", required=True),
    "amount": st.column_config.NumberColumn(
        # "euro"/"localized" seguono la lingua del browser (in inglese: €1,620.00); il
        # formato fisso resta uguale ovunque
        "Importo (€)", min_value=0.0, step=0.01, format="%.2f €", width="small",
        help="L'importo come compare nel documento, anche se non è mensile",
    ),
    "periodicity": st.column_config.SelectboxColumn(
        "Ogni quanto", options=PERIODICITIES, required=True, default="mensile", width="small",
        help="Quanto spesso ricevi o paghi questo importo. L'app lo riporta al mese "
             "(annuale ÷ 12, trimestrale ÷ 3)",
    ),
    "source": st.column_config.TextColumn(
        "Da dove arriva", disabled=True, width="small",
        help="Il documento da cui è stata letta la voce (vuoto se l'hai scritta tu)",
    ),
}
EXPENSE_CONFIG = {
    **INCOME_CONFIG,
    # larghezze in px: tutte le colonne, compresa "Elimina", entrano a 1280 px (QA-38)
    "label": st.column_config.TextColumn("Voce", width=320, required=True),
    "amount": st.column_config.NumberColumn(
        "Importo (€)", min_value=0.0, step=0.01, format="%.2f €", width=100,
        help=INCOME_CONFIG["amount"]["help"],
    ),
    "category": st.column_config.SelectboxColumn(
        "Categoria", options=CATEGORIES, required=True, default="Altro", width=150,
    ),
    "periodicity": st.column_config.SelectboxColumn(
        "Ogni quanto", options=PERIODICITIES, required=True, default="mensile", width=105,
        help=INCOME_CONFIG["periodicity"]["help"],
    ),
    "source": st.column_config.TextColumn(
        "Da dove arriva", disabled=True, width=90, help=INCOME_CONFIG["source"]["help"],
    ),
    "type": st.column_config.SelectboxColumn(
        "Tipo", options=EXPENSE_TYPES, required=True, default="variabile", width=95,
        help="Fissa: stessa cifra ogni volta (es. affitto). Semi-fissa: cambia poco (es. carburante). "
             "Variabile: cambia molto (es. spesa, svago). Una tantum: capita una volta sola "
             "(es. una riparazione, un regalo)",
    ),
}

DEFAULT_INCOMES = [{"label": "Stipendio netto", "amount": 0.0, "periodicity": "mensile"}]
DEFAULT_EXPENSES = [
    {"label": label, "amount": 0.0, "category": cat, "type": DEFAULT_TYPE[cat], "periodicity": per}
    for label, cat, per in [
        ("Affitto o mutuo", "Abitazione", "mensile"),
        ("Utenze (luce, gas, acqua, internet)", "Abitazione", "mensile"),
        ("Rate di prestiti", "Debiti/finanziamenti", "mensile"),
        ("Assicurazioni (auto, casa, salute)", "Assicurazioni", "annuale"),
        ("Carburante e mezzi pubblici", "Trasporti", "mensile"),
        ("Farmaci, visite, palestra", "Salute e benessere", "mensile"),
        ("Spesa alimentare", "Alimentari", "mensile"),
        ("Abbonamenti, uscite, shopping", "Svago/discrezionale", "mensile"),
    ]
]


# --------------------------------------------------------------------- stato

def _init_state() -> None:
    ss = st.session_state
    ss.setdefault("step", "input")
    ss.setdefault("incomes", DEFAULT_INCOMES)
    ss.setdefault("expenses", DEFAULT_EXPENSES)
    ss.setdefault("doc_terms", [])
    ss.setdefault("extraction_log", [])
    ss.setdefault("glossary", None)
    ss.setdefault("duplicates", [])  # voci doppie tolte in automatico dopo l'estrazione
    ss.setdefault("v", 0)  # versione delle tabelle: cambia quando i dati arrivano da fuori


def _go(step: str) -> None:
    st.session_state.step = step
    st.session_state.v += 1
    st.rerun()


def _records(df: pd.DataFrame) -> list[dict]:
    """Righe della tabella editabile come dict, scartando le righe vuote."""
    df = df.astype(object).where(df.notna(), None)
    return [r for r in df.to_dict("records") if r.get("label") or r.get("amount")]


def _merge(current: list[dict], extracted: list[dict]) -> list[dict]:
    """Le voci lette dai documenti sostituiscono le righe-modello ancora a zero."""
    if not extracted:
        return current
    return [r for r in current if (r.get("amount") or 0) > 0] + extracted


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".", ",")


# --------------------------------------------------------------- componenti

def _table_height(rows: int) -> int:
    """Altezza che mostra tutte le righe + la riga "+": niente scroll interno (QA-38)."""
    return 35 * (rows + 2) + 3


DELETE_COLUMN = {"remove": st.column_config.CheckboxColumn(
    "Elimina", default=False, width=70, help="Spunta per togliere la voce dal calcolo",
)}


def _edit_tables(prefix: str, deletable: bool = False) -> tuple[list[dict], list[dict]]:
    """Tabelle editabili di entrate e uscite; con `deletable` c'e' la colonna "Elimina"."""
    v = st.session_state.v
    tables = []
    for title, items, columns, config, key in (
        ("Entrate", st.session_state.incomes, INCOME_COLUMNS, INCOME_CONFIG, "inc"),
        ("Uscite", st.session_state.expenses, EXPENSE_COLUMNS, EXPENSE_CONFIG, "exp"),
    ):
        st.markdown(f"**{title}**")
        df = pd.DataFrame(items, columns=columns)
        if deletable:
            df.insert(0, "remove", False)
            config = {**DELETE_COLUMN, **config}
        edited = st.data_editor(
            df, key=f"{prefix}_{key}_{v}", num_rows="dynamic", hide_index=True, width="stretch",
            height=_table_height(len(items)), column_config=config,
        )
        tables.append([{k: val for k, val in r.items() if k != "remove"}
                       for r in _records(edited) if not r.get("remove")])
    return tables[0], tables[1]


def _add_item_form(incomes: list[dict], expenses: list[dict], *, step: str, expanded: bool = False) -> None:
    """Aggiunta guidata di una voce personalizzata, oltre alla riga "+" delle tabelle.

    Con questo e le tabelle l'intero budget si inserisce a mano: l'app funziona
    anche senza leggere documenti, quindi senza AI.
    """
    with st.expander("➕ Aggiungi una voce", expanded=expanded):
        kind = st.radio("Che cosa vuoi aggiungere?", ["Uscita", "Entrata"], horizontal=True, key="add_kind")
        label_col, amount_col, period_col = st.columns([3, 1, 1])
        label = label_col.text_input("Descrizione", placeholder="Es. regalo di compleanno, ripetizioni", key="add_label")
        amount = amount_col.number_input("Importo (€)", min_value=0.0, step=1.0, key="add_amount")
        periodicity = period_col.selectbox("Ogni quanto", PERIODICITIES, key="add_period")
        if kind == "Uscita":
            cat_col, type_col = st.columns(2)
            category = cat_col.selectbox("Categoria", CATEGORIES, index=len(CATEGORIES) - 1, key="add_cat")
            expense_type = type_col.selectbox("Tipo", EXPENSE_TYPES, index=EXPENSE_TYPES.index(DEFAULT_TYPE[category]),
                                              key="add_type")
        if st.button("Aggiungi", disabled=not label or amount <= 0):
            item = {"label": label, "amount": amount, "periodicity": periodicity, "source": None}
            # le modifiche gia' fatte nelle tabelle restano: si parte dai valori correnti
            st.session_state.incomes, st.session_state.expenses = incomes, expenses
            if kind == "Uscita":
                st.session_state.expenses = expenses + [{**item, "category": category, "type": expense_type}]
            else:
                st.session_state.incomes = incomes + [item]
            for key in ("add_label", "add_amount"):
                st.session_state.pop(key, None)
            _go(step)


def _run_extraction(files) -> tuple[list[dict], list[dict]]:
    paths = [extraction.save_upload(f.name, f.getvalue()) for f in files]
    with ThreadPoolExecutor(max_workers=len(paths)) as pool:
        results = list(pool.map(extraction.extract_budget_items, paths))

    # Messaggi in parole semplici per l'utente: niente costi o errori tecnici (QA-38).
    log, incomes, expenses = [], [], []
    for path, result in zip(paths, results):
        if result["error"]:
            log.append(("warning", f"**{path.name}**: non sono riuscito a leggere questo documento. "
                                   "Puoi inserire le voci a mano qui sotto."))
            continue
        incomes += result["incomes"]
        expenses += result["expenses"]
        st.session_state.doc_terms += result["terms"]
        log.append(("success", f"**{path.name}**: trovate {len(result['incomes'])} entrate e "
                               f"{len(result['expenses'])} uscite."))
        if result["flagged"]:
            log.append(("warning", f"**{path.name}**: {result['flagged']} voci hanno una descrizione da "
                                   f"verificare («{extraction.FLAGGED_LABEL}»): l'importo è quello del documento."))
    st.session_state.extraction_log = log
    return incomes, expenses


def _duplicates_table() -> None:
    """Voci doppie tolte in automatico, evidenziate in giallo: niente sparisce in silenzio."""
    dropped = st.session_state.duplicates
    if not dropped:
        return
    st.markdown("**Voci doppie, contate una volta sola**")
    st.caption(
        "Queste voci comparivano in due documenti (es. lo stipendio nella busta paga e il suo accredito "
        "sul conto): le ho tolte dal calcolo per non contarle due volte."
    )
    df = pd.DataFrame([{
        "Voce tolta": d.get("label"), "Importo": eur(float(d.get("amount") or 0)),
        "Da dove arriva": d.get("source"), "Già contata come": d.get("duplicate_of"),
    } for d in dropped])
    styled = df.style.set_properties(**{"background-color": DUPLICATE_FILL, "color": "#1A1A28"})
    st.dataframe(styled, hide_index=True, width="stretch")


# Titolo e passi con lo stile della copertina e della slide "Come funziona"
# del deck: "Budget" nel colore del testo e "Facile" nel verde --acc, cerchi
# numerati come .step-n.
HEADER_CSS = """<style>
[data-testid='stMetricValue'] { font-size: 1.85rem; }
.bf-title { font-size: 2.7rem !important; font-weight: 800; letter-spacing: -1.5px; line-height: 1.15;
            color: #1A1A28; margin: 0; }
.bf-title span { color: #006B54; }
.bf-lead { color: #6A6A7E; font-size: 1.05rem !important; margin: .2rem 0 .6rem 0; }
.bf-flow { display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; margin: .3rem 0 .2rem 0; }
.bf-step { display: flex; align-items: center; gap: .5rem; color: #6A6A7E; font-weight: 600; }
.bf-step .n { width: 32px; height: 32px; border-radius: 50%; border: 2px solid #B0AFBA; display: flex;
              align-items: center; justify-content: center; font-weight: 800; }
.bf-step.done .n { background: #E5F2EE; border-color: #006B54; color: #006B54; }
.bf-step.active { color: #1A1A28; }
.bf-step.active .n { background: #006B54; border-color: #006B54; color: #FFFFFF; }
.bf-sep { color: #B0AFBA; font-weight: 700; }
</style>"""


def _header() -> None:
    """Titolo come nel deck e flusso dei 3 passi in alto (al posto della sidebar)."""
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"<div class='bf-title'>Budget<span>Facile</span></div><div class='bf-lead'>{TAGLINE}</div>",
                unsafe_allow_html=True)
    keys = list(STEPS)
    current = keys.index(st.session_state.step)
    steps = []
    for i, key in enumerate(keys):
        state = "active" if i == current else "done" if i < current else ""
        steps.append(f"<div class='bf-step {state}'><div class='n'>{i + 1}</div>{STEPS[key]}</div>")
    flow_col, restart_col = st.columns([5, 1], vertical_alignment="center")
    flow_col.markdown(f"<div class='bf-flow'>{'<span class=bf-sep>→</span>'.join(steps)}</div>",
                      unsafe_allow_html=True)
    if restart_col.button("Ricomincia da capo", width="stretch"):
        st.session_state.clear()
        st.rerun()


# -------------------------------------------------------------- passo 1

def step_input() -> None:
    st.header("1 · Le tue entrate e uscite")
    box = st.container(border=True)
    with box:
        st.subheader("📄 Hai dei documenti? Caricali così come sono")
        st.write(
            "Busta paga, estratto conto, bolletta o il tuo foglio spese (PDF o Excel). Li leggo io e "
            "precompilo le tabelle qui sotto: prima del calcolo potrai controllare e correggere ogni voce."
        )
        files = st.file_uploader(
            "Documenti", type=["pdf", "xlsx", "xls"], accept_multiple_files=True,
            key=f"upload_{st.session_state.v}", label_visibility="collapsed",
        )
        read_docs = st.button("Carica i documenti", type="primary", disabled=not files)
        for level, message in st.session_state.extraction_log:
            getattr(st, level)(message)

    st.subheader("✍️ Oppure inserisci tutto a mano")
    st.caption(
        "Non servono documenti: puoi scrivere qui ogni entrata e uscita, oppure completare quelle lette. "
        "Scrivi gli importi come li paghi o li ricevi: le voci annuali o trimestrali (es. assicurazione, "
        "bollo) vengono riportate al mese in automatico. Per una voce nuova usa il riquadro sotto le "
        "tabelle o la riga + in fondo a ogni tabella."
    )
    incomes, expenses = _edit_tables("input")
    _add_item_form(incomes, expenses, step="input")

    if read_docs:
        with box, st.spinner("Sto leggendo i documenti: può volerci fino a un minuto…"):
            new_incomes, new_expenses = _run_extraction(files)
        # La stessa voce in due documenti (es. stipendio in busta paga e accredito sul conto) e'
        # normale: si tiene una copia sola, senza chiedere nulla all'utente, e le copie tolte
        # restano visibili in giallo nella conferma.
        st.session_state.incomes, dropped_incomes = remove_duplicates(_merge(incomes, new_incomes))
        st.session_state.expenses, dropped_expenses = remove_duplicates(_merge(expenses, new_expenses))
        dropped = dropped_incomes + dropped_expenses
        st.session_state.duplicates += dropped
        if dropped:
            st.session_state.extraction_log.append(("info", f"{len(dropped)} voci comparivano in due documenti: le "
                                                            "ho contate una volta sola (le trovi in giallo nella conferma)."))
        _go("input")
    if st.button("Vai alla conferma →", type="primary"):
        st.session_state.incomes, st.session_state.expenses = incomes, expenses
        _go("conferma")


# -------------------------------------------------------------- passo 2

def step_confirm() -> None:
    st.header("2 · Controlla i dati prima del calcolo")
    st.write(
        "Qui trovi **tutte** le voci, inserite a mano o lette dai documenti. Controlla per ciascuna "
        "importo, categoria e ogni quanto si ripete: puoi correggere, aggiungere o cancellare righe. "
        "**Il calcolo parte solo quando confermi.**"
    )
    if any(r.get("source") for r in st.session_state.incomes + st.session_state.expenses):
        st.warning(
            "Alcune voci sono state lette automaticamente (colonna «Da dove arriva»): confrontale con i "
            "documenti originali, la lettura automatica può sbagliare.",
            icon="🔎",
        )
    st.caption("Spunta «Elimina» per togliere una voce dal calcolo; per aggiungerne una usa il riquadro sotto le tabelle.")
    incomes, expenses = _edit_tables("conferma", deletable=True)
    _add_item_form(incomes, expenses, step="conferma")
    _duplicates_table()
    preview = compute_budget(incomes, expenses)
    st.caption(
        f"Anteprima riportata al mese: entrate {eur(preview.total_income)} · uscite {eur(preview.total_expenses)}"
    )

    back_col, confirm_col = st.columns([1, 2])
    if back_col.button("← Torna all'inserimento", width="stretch"):
        st.session_state.incomes, st.session_state.expenses = incomes, expenses
        _go("input")
    if confirm_col.button("✅ Confermo i dati: calcola il budget", type="primary", width="stretch"):
        st.session_state.incomes, st.session_state.expenses = incomes, expenses
        st.session_state.confirmed = {"incomes": incomes, "expenses": expenses}
        st.session_state.glossary = None
        _go("risultati")


# -------------------------------------------------------------- passo 3

def step_results() -> None:
    data = st.session_state.get("confirmed")
    if not data:  # RF-09: senza conferma esplicita non si calcola
        _go("conferma")
    s = compute_budget(data["incomes"], data["expenses"])

    st.header("3 · Il tuo budget del mese, spiegato")
    cols = st.columns(4)
    cols[0].metric("Entrate al mese", eur(s.total_income), border=True)
    cols[1].metric("Uscite al mese", eur(s.total_expenses), border=True)
    cols[2].metric("Risparmio al mese", eur(s.savings), border=True, help="Entrate al mese − uscite al mese")
    cols[3].metric("Tasso di risparmio", _pct(s.savings_rate), border=True,
                   help="La parte delle entrate che resta dopo le uscite")
    st.caption(
        "Sul totale delle entrate: spese fisse " + _pct(s.type_share_of_income("fissa"))
        + " · semi-fisse " + _pct(s.type_share_of_income("semi-fissa"))
        + " · variabili " + _pct(s.type_share_of_income("variabile"))
        + (" · una tantum " + _pct(s.type_share_of_income("una tantum")) if s.by_type.get("una tantum") else "")
    )

    if s.savings <= 0:
        _negative_savings(s)

    # Schede invece di una pagina lunga piu' di 3.000 px (QA-38).
    summary, benchmark, words, goal, details = st.tabs([
        "📊 Riepilogo", "⚖️ Regola 50/30/20", "📖 Glossario", "🎯 Obiettivo di risparmio",
        "🧮 Come è stato calcolato",
    ])
    with summary:
        left, right = st.columns([3, 2], gap="large")
        with left:
            _category_chart(s)
        with right:
            _income_vs_expenses_chart(s)
    with benchmark:
        _benchmark_section(s)
    with words:
        _glossary_section(data)
    with goal:
        _goal_section(s)
    with details:
        _calculation_details(data, s)

    if st.button("← Modifica i dati"):
        _go("conferma")


def _negative_savings(s) -> None:
    """RF-06: evidenzia e mostra le categorie piu' pesanti, senza prescrizioni."""
    verb = "superano" if s.savings < 0 else "sono pari a"
    lines = "\n".join(
        f"- **{category}**: {_pct(share)} delle uscite ({eur(s.by_category[category])} al mese)"
        for category, share in top_categories(s)
    )
    st.error(
        f"**Questo mese le uscite {verb} le entrate**: il saldo del mese è {eur(s.savings)}.\n\n"
        f"Le categorie che pesano di più sul totale delle uscite sono:\n{lines}",
        icon="⚠️",
    )
    st.caption("È una fotografia dei tuoi dati, non un giudizio: cosa farne resta una tua decisione.")


def _category_chart(s) -> None:
    st.subheader("Dove vanno le uscite")
    rows = [
        {"Categoria": c, "Importo": v, "Al mese": eur(v), "Quota": s.category_share(c), "ordine": i}
        for i, (c, v) in enumerate(s.by_category.items()) if v > 0
    ]
    if not rows:
        st.caption("Nessuna uscita inserita.")
        return
    df = pd.DataFrame(rows)
    present = list(df["Categoria"])
    donut = alt.Chart(df).mark_arc(innerRadius=62, outerRadius=110, stroke=SURFACE, strokeWidth=2).encode(
        theta=alt.Theta("Importo:Q", stack=True),
        order=alt.Order("ordine:Q"),
        color=alt.Color(
            "Categoria:N",
            scale=alt.Scale(domain=present, range=[CATEGORY_COLORS[c] for c in present]),
            # legenda a destra: con la colonna 3/5 entra a 1280 px senza sovrapporsi (QA-33)
            legend=alt.Legend(title=None, orient="right", labelLimit=170),
        ),
        tooltip=[
            alt.Tooltip("Categoria:N"),
            alt.Tooltip("Al mese:N"),
            alt.Tooltip("Quota:Q", format=".1%", title="Sul totale uscite"),
        ],
    )
    st.altair_chart(donut.properties(height=290), width="stretch")
    # Vista tabellare: identita' mai affidata al solo colore (relief rule).
    table = df.assign(Quota=df["Quota"].map(_pct))[["Categoria", "Al mese", "Quota"]]
    st.dataframe(table, hide_index=True, width="stretch")


def _income_vs_expenses_chart(s) -> None:
    st.subheader("Entrate e uscite al mese")
    df = pd.DataFrame([
        {"Voce": "Entrate", "Euro": s.total_income},
        {"Voce": "Uscite", "Euro": s.total_expenses},
    ])
    df["Etichetta"] = df["Euro"].map(eur)
    bars = alt.Chart(df).mark_bar(cornerRadiusEnd=4, color=ACCENT).encode(
        y=alt.Y("Voce:N", title=None, sort=None, scale=alt.Scale(paddingInner=0.4)),
        # margine a destra per l'etichetta con l'importo
        x=alt.X("Euro:Q", title="€ al mese", axis=IT_AXIS,
                scale=alt.Scale(domain=[0, max(df["Euro"].max(), 1) * 1.25])),
        tooltip=[alt.Tooltip("Voce:N"), alt.Tooltip("Etichetta:N", title="Al mese")],
    )
    labels = bars.mark_text(align="left", dx=6, color=LABEL_INK, fontSize=13).encode(text="Etichetta:N")
    st.altair_chart((bars + labels).properties(height=140), width="stretch")


def _benchmark_section(s) -> None:
    """RF-05: confronto informativo con la regola 50/30/20 (grafico + testo fisso)."""
    rows = benchmark_503020(s)
    df = pd.DataFrame(
        [{"Voce": r["bucket"], "Serie": SERIES[0], "Euro": r["actual"], "Quota": r["actual_pct"]} for r in rows]
        + [{"Voce": r["bucket"], "Serie": SERIES[1], "Euro": r["reference"], "Quota": r["reference_pct"]} for r in rows]
    )
    df["Etichetta"] = df["Euro"].map(eur)
    df["Percentuale"] = df["Quota"].map(lambda q: f"{q * 100:.0f}%")
    x = alt.X("Voce:N", title=None, sort=list(BENCHMARK_503020), axis=alt.Axis(labelAngle=0, labelFontSize=13))
    x_offset = alt.XOffset("Serie:N", sort=SERIES, scale=alt.Scale(paddingInner=0.08))
    bars = alt.Chart(df).mark_bar(cornerRadiusEnd=4).encode(
        x=x, xOffset=x_offset,
        y=alt.Y("Euro:Q", title="€ al mese", axis=IT_AXIS),
        color=alt.Color(
            "Serie:N", scale=alt.Scale(domain=SERIES, range=[ACCENT, REFERENCE_GRAY]),
            legend=alt.Legend(title=None, orient="top"),
        ),
        tooltip=[
            alt.Tooltip("Voce:N"), alt.Tooltip("Serie:N"), alt.Tooltip("Etichetta:N", title="Al mese"),
            alt.Tooltip("Quota:Q", format=".1%", title="Sulle entrate"),
        ],
    )
    # etichetta con la % sulle entrate sopra ogni barra (QA-42)
    labels = alt.Chart(df).mark_text(dy=-8, color=LABEL_INK, fontSize=12).encode(
        x=x, xOffset=x_offset, y="Euro:Q", text="Percentuale:N",
    )
    chart_col, text_col = st.columns([3, 2], gap="large")
    chart_col.altair_chart((bars + labels).properties(height=320), width="stretch")

    by_bucket = {r["bucket"]: r["actual_pct"] for r in rows}
    with text_col:
        st.markdown(
            "La **regola 50/30/20** è un riferimento educativo molto diffuso: divide le entrate del mese "
            "in tre parti. Nel tuo budget:\n\n"
            f"- **Necessità: {_pct(by_bucket['Necessità'])}** delle entrate (riferimento 50%)\n"
            f"- **Desideri: {_pct(by_bucket['Desideri'])}** (riferimento 30%)\n"
            f"- **Risparmio: {_pct(by_bucket['Risparmio'])}** (riferimento 20%)"
        )
        _benchmark_note()


def _benchmark_note() -> None:
    st.caption(
        "È solo un termine di paragone per leggere i tuoi numeri, non un obiettivo da raggiungere: ogni "
        "situazione personale è diversa. Per il confronto l'app conta come desideri solo la categoria "
        "svago; tutte le altre (compresa «altro», che di solito raccoglie commissioni e imposte) "
        "sono contate come necessità."
    )


def _glossary_section(data: dict) -> None:
    """RF-04: glossario contestuale; per i termini nuovi, Claude solo su richiesta."""
    labels = [r.get("label") or "" for r in data["incomes"] + data["expenses"]]
    terms = glossary.detect_terms(labels, st.session_state.doc_terms)
    if not terms:
        st.caption("Nessun termine tecnico riconosciuto nelle voci confermate.")
        return

    context = dict(terms)
    for item in glossary.known_definitions(terms):
        # dove compare il termine: nelle voci confermate o solo nel testo dei documenti (QA-40)
        where = context[item["term"]]
        where = "nei documenti caricati" if where == "documento caricato" else f"nella voce «{where}»"
        st.markdown(f"**{item['term']}**: {item['text']}  \n<small>Compare {where}.</small>", unsafe_allow_html=True)
    st.caption("Definizioni riviste a mano dal team: spiegano il significato, non cosa fare.")

    others = glossary.unknown_terms(terms)
    if not others:
        return
    result = st.session_state.glossary
    if result is None:
        st.write("Altri termini trovati nei documenti: " + ", ".join(f"**{t}**" for t, _ in others))
        if st.button("Chiedimi di spiegarli in parole semplici", type="primary"):
            with st.spinner("Sto preparando le spiegazioni…"):
                st.session_state.glossary = glossary.explain_with_ai(others)
            st.rerun()
        st.caption(
            "Una sola richiesta per tutti i termini, solo se la chiedi. Ogni spiegazione passa da un "
            "filtro che blocca qualsiasi consiglio prima di essere mostrata."
        )
        return

    if result["error"]:
        st.caption("Le spiegazioni non sono disponibili in questo momento.")
    for item in result["items"]:
        st.markdown(f"**{item['term']}**: {item['text']}")
    if result["blocked"]:
        st.caption(f"Non mostrate perché non rispettavano il vincolo educativo: {', '.join(result['blocked'])}.")
    if result["items"]:
        st.caption("Spiegazioni generate automaticamente e controllate dal filtro anti-consigli prima di essere mostrate.")


def _goal_section(s) -> None:
    """RF-07: proiezione puramente matematica dell'obiettivo di risparmio."""
    goal = st.number_input("Cifra che vorresti mettere da parte (€)", min_value=0.0, value=1000.0, step=100.0)
    months = months_to_goal(goal, s.savings)
    if months is None:
        st.info(
            f"Con un risparmio mensile di {eur(s.savings)}, mantenendo il ritmo attuale la cifra di "
            f"{eur(goal)} non viene raggiunta."
        )
    else:
        years = ""
        if months >= 12:
            y, m = divmod(months, 12)
            years = f" (circa {y} {'anno' if y == 1 else 'anni'}" + (f" e {m} {'mese' if m == 1 else 'mesi'})" if m else ")")
        st.info(
            f"Se il risparmio restasse quello attuale ({eur(s.savings)} al mese), la cifra di {eur(goal)} "
            f"verrebbe raggiunta in circa **{months} mesi**{years}."
        )
    st.caption(
        "È una semplice proiezione matematica (obiettivo ÷ risparmio al mese) per vedere l'effetto nel tempo "
        "del budget attuale: non è una previsione né un consiglio su come o dove tenere i soldi. Non tiene "
        "conto di interessi, inflazione o spese impreviste."
    )


def _calculation_details(data: dict, s) -> None:
    """RF-03: come e' stato ottenuto il risultato, voce per voce."""
    st.markdown(
        "Ogni importo viene riportato al mese: un importo **annuale** si divide per 12, uno "
        "**trimestrale** per 3. Poi: **risparmio = entrate al mese − uscite al mese** "
        f"= {eur(s.total_income)} − {eur(s.total_expenses)} = **{eur(s.savings)}**."
    )
    rows = [
        {"Tipo": "Entrata", "Voce": r.get("label"), "Importo": eur(float(r.get("amount") or 0)),
         "Ogni quanto": r.get("periodicity"), "Al mese": eur(to_monthly(r.get("amount"), r.get("periodicity"))),
         "Categoria": ""}
        for r in data["incomes"]
    ] + [
        {"Tipo": "Uscita", "Voce": r.get("label"), "Importo": eur(float(r.get("amount") or 0)),
         "Ogni quanto": r.get("periodicity"), "Al mese": eur(to_monthly(r.get("amount"), r.get("periodicity"))),
         "Categoria": r.get("category")}
        for r in data["expenses"]
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=_table_height(len(rows)))
    _duplicates_table()


# --------------------------------------------------------------------- main

_init_state()
_header()
st.info(DISCLAIMER, icon="ℹ️")
{"input": step_input, "conferma": step_confirm, "risultati": step_results}[st.session_state.step]()
