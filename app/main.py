"""FinSup — capire il proprio budget (Hagenthon, Tema 02: Inclusione Finanziaria).

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

from finsup import demo_data, extraction, glossary
from finsup.ai_client import DEFAULT_MODEL
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
    top_categories,
)

st.set_page_config(page_title="FinSup — Capire il proprio budget", page_icon="💶", layout="wide")

DISCLAIMER = (
    "**Strumento educativo, non consulenza finanziaria.** FinSup ti aiuta a capire com'è fatto "
    "il tuo budget: non dice cosa fare con i tuoi soldi, le decisioni restano tue."
)

# Palette categoriale di riferimento della skill dataviz, validata con
# validate_palette.js: un colore fisso per categoria (segue la categoria,
# non il suo peso). Tre slot sono sotto 3:1 di contrasto -> tabella sotto il grafico.
CATEGORY_COLORS = dict(zip(CATEGORIES, [
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948",
]))
ACCENT, REFERENCE_GRAY, LABEL_INK = "#2a78d6", "#898781", "#52514e"
SERIES = ["Il tuo budget", "Riferimento 50/30/20"]

STEPS = {"input": "1 · Inserisci le voci", "conferma": "2 · Conferma i dati", "risultati": "3 · Capisci il budget"}

INCOME_COLUMNS = ["label", "amount", "periodicity", "source"]
EXPENSE_COLUMNS = ["label", "amount", "category", "type", "periodicity", "source"]
INCOME_CONFIG = {
    "label": st.column_config.TextColumn("Voce", width="large", required=True),
    "amount": st.column_config.NumberColumn("Importo (€)", min_value=0.0, step=0.01, format="%.2f €"),
    "periodicity": st.column_config.SelectboxColumn("Ogni quanto", options=PERIODICITIES, required=True, default="mensile"),
    "source": st.column_config.TextColumn("Da dove arriva", disabled=True),
}
EXPENSE_CONFIG = {
    **INCOME_CONFIG,
    "category": st.column_config.SelectboxColumn("Categoria", options=CATEGORIES, required=True, default="Altro"),
    "type": st.column_config.SelectboxColumn("Tipo", options=EXPENSE_TYPES, required=True, default="variabile"),
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

def _edit_tables(prefix: str) -> tuple[list[dict], list[dict]]:
    v = st.session_state.v
    st.markdown("**Entrate**")
    incomes = st.data_editor(
        pd.DataFrame(st.session_state.incomes, columns=INCOME_COLUMNS),
        key=f"{prefix}_inc_{v}", num_rows="dynamic", hide_index=True, width="stretch",
        column_config=INCOME_CONFIG,
    )
    st.markdown("**Uscite**")
    expenses = st.data_editor(
        pd.DataFrame(st.session_state.expenses, columns=EXPENSE_COLUMNS),
        key=f"{prefix}_exp_{v}", num_rows="dynamic", hide_index=True, width="stretch",
        column_config=EXPENSE_CONFIG,
    )
    return _records(incomes), _records(expenses)


def _run_extraction(files) -> tuple[list[dict], list[dict]]:
    paths = [extraction.save_upload(f.name, f.getvalue()) for f in files]
    with ThreadPoolExecutor(max_workers=len(paths)) as pool:
        results = list(pool.map(extraction.extract_budget_items, paths))

    log, incomes, expenses = [], [], []
    for path, result in zip(paths, results):
        if result["error"]:
            log.append(("warning", f"**{path.name}**: lettura non riuscita ({result['error']}). "
                                   "Puoi inserire le voci a mano o usare i dati di esempio."))
            continue
        incomes += result["incomes"]
        expenses += result["expenses"]
        st.session_state.doc_terms += result["terms"]
        log.append(("success", f"**{path.name}**: trovate {len(result['incomes'])} entrate e "
                               f"{len(result['expenses'])} uscite · costo ${result['cost_usd']:.3f}"))
        if result["flagged"]:
            log.append(("warning", f"**{path.name}**: {result['flagged']} voci hanno una descrizione da "
                                   f"verificare («{extraction.FLAGGED_LABEL}»): l'importo è quello del documento."))
    st.session_state.extraction_log = log
    return incomes, expenses


def _sidebar() -> None:
    with st.sidebar:
        st.title("💶 FinSup")
        st.caption("Capire il proprio budget, in parole semplici")
        for key, label in STEPS.items():
            st.markdown(f"**▶ {label}**" if key == st.session_state.step else label)
        st.divider()
        st.info(DISCLAIMER)
        if st.button("Ricomincia da capo", width="stretch"):
            st.session_state.clear()
            st.rerun()


# -------------------------------------------------------------- passo 1

def step_input() -> None:
    st.header("1 · Le tue entrate e uscite")
    box = st.container(border=True)
    with box:
        st.subheader("📄 Hai dei documenti? Caricali così come sono")
        st.write(
            "Busta paga, estratto conto, bolletta o il tuo foglio spese (PDF o Excel). Claude li legge "
            "e precompila le tabelle qui sotto: prima del calcolo potrai controllare e correggere ogni voce."
        )
        files = st.file_uploader(
            "Documenti", type=["pdf", "xlsx", "xls"], accept_multiple_files=True,
            key=f"upload_{st.session_state.v}", label_visibility="collapsed",
        )
        read_col, demo_col = st.columns(2)
        read_docs = read_col.button("Leggi i documenti con Claude", type="primary", disabled=not files, width="stretch")
        use_demo = demo_col.button("Usa i dati di esempio (persona fittizia)", width="stretch")
        for level, message in st.session_state.extraction_log:
            getattr(st, level)(message)

    st.subheader("✍️ Inserisci o completa le voci")
    st.caption(
        "Scrivi gli importi come li trovi nei documenti. Le voci annuali o trimestrali (es. assicurazione, "
        "bollo) vengono riportate al mese in automatico. Aggiungi righe con il + in fondo a ogni tabella."
    )
    incomes, expenses = _edit_tables("input")

    if read_docs:
        with box, st.spinner("Claude sta leggendo i documenti: può volerci fino a un minuto…"):
            new_incomes, new_expenses = _run_extraction(files)
        st.session_state.incomes = _merge(incomes, new_incomes)
        st.session_state.expenses = _merge(expenses, new_expenses)
        _go("input")
    if use_demo:
        st.session_state.incomes = [dict(i, source="esempio") for i in demo_data.INCOMES]
        st.session_state.expenses = [dict(e, source="esempio") for e in demo_data.EXPENSES]
        st.session_state.doc_terms = list(demo_data.TERMS)
        st.session_state.extraction_log = [("info", "Caricati i dati di esempio: gli stessi dei documenti demo "
                                                    "in app/demo_assets (persona e importi inventati).")]
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
    incomes, expenses = _edit_tables("conferma")
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
    )

    if s.savings <= 0:
        _negative_savings(s)

    left, right = st.columns(2, gap="large")
    with left:
        _category_chart(s)
    with right:
        _income_vs_expenses_chart(s)
        _benchmark_section(s)

    st.divider()
    _glossary_section(data)
    st.divider()
    _goal_section(s)
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
    donut = alt.Chart(df).mark_arc(innerRadius=70, outerRadius=130, stroke="#ffffff", strokeWidth=2).encode(
        theta=alt.Theta("Importo:Q", stack=True),
        order=alt.Order("ordine:Q"),
        color=alt.Color(
            "Categoria:N",
            scale=alt.Scale(domain=present, range=[CATEGORY_COLORS[c] for c in present]),
            legend=alt.Legend(title=None, orient="right", labelLimit=200),
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
        x=alt.X("Euro:Q", title="€ al mese", scale=alt.Scale(domain=[0, max(df["Euro"].max(), 1) * 1.25])),
        tooltip=[alt.Tooltip("Voce:N"), alt.Tooltip("Etichetta:N", title="Al mese")],
    )
    labels = bars.mark_text(align="left", dx=6, color=LABEL_INK, fontSize=13).encode(text="Etichetta:N")
    st.altair_chart((bars + labels).properties(height=140), width="stretch")


def _benchmark_section(s) -> None:
    """RF-05: confronto informativo con la regola 50/30/20 (grafico + testo fisso)."""
    st.subheader("Confronto con la regola 50/30/20")
    rows = benchmark_503020(s)
    df = pd.DataFrame(
        [{"Voce": r["bucket"], "Serie": SERIES[0], "Euro": r["actual"], "Quota": r["actual_pct"]} for r in rows]
        + [{"Voce": r["bucket"], "Serie": SERIES[1], "Euro": r["reference"], "Quota": r["reference_pct"]} for r in rows]
    )
    df["Etichetta"] = df["Euro"].map(eur)
    chart = alt.Chart(df).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("Voce:N", title=None, sort=list(BENCHMARK_503020), axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("Serie:N", sort=SERIES, scale=alt.Scale(paddingInner=0.08)),
        y=alt.Y("Euro:Q", title="€ al mese"),
        color=alt.Color(
            "Serie:N", scale=alt.Scale(domain=SERIES, range=[ACCENT, REFERENCE_GRAY]),
            legend=alt.Legend(title=None, orient="top"),
        ),
        tooltip=[
            alt.Tooltip("Voce:N"), alt.Tooltip("Serie:N"), alt.Tooltip("Etichetta:N", title="Al mese"),
            alt.Tooltip("Quota:Q", format=".1%", title="Sulle entrate"),
        ],
    )
    st.altair_chart(chart.properties(height=300), width="stretch")

    by_bucket = {r["bucket"]: r["actual_pct"] for r in rows}
    st.markdown(
        "La **regola 50/30/20** è un riferimento educativo molto diffuso: divide le entrate del mese in "
        "**50%** per le necessità, **30%** per i desideri e **20%** per il risparmio. "
        f"Nel tuo budget le necessità sono il **{_pct(by_bucket['Necessità'])}** delle entrate, i desideri "
        f"il **{_pct(by_bucket['Desideri'])}** e il risparmio il **{_pct(by_bucket['Risparmio'])}**."
    )
    st.caption(
        "È solo un termine di paragone per leggere i tuoi numeri, non un obiettivo da raggiungere: ogni "
        "situazione personale è diversa. Per il confronto FinSup conta come desideri solo la categoria "
        "svago; tutte le altre (compresa «altro», che di solito raccoglie commissioni e imposte) "
        "sono contate come necessità."
    )


def _glossary_section(data: dict) -> None:
    """RF-04: glossario contestuale, generato da Claude solo su richiesta."""
    st.subheader("📖 Le parole tecniche dei tuoi documenti")
    labels = [r.get("label") or "" for r in data["incomes"] + data["expenses"]]
    terms = glossary.detect_terms(labels, st.session_state.doc_terms)
    if not terms:
        st.caption("Nessun termine tecnico riconosciuto nelle voci confermate.")
        return

    for item in glossary.known_definitions(terms):
        st.markdown(f"**{item['term']}** — {item['text']}")
    st.caption("Definizioni preparate con Claude e riviste a mano dal team: spiegano il significato, non cosa fare.")

    others = glossary.unknown_terms(terms)
    if not others:
        return
    result = st.session_state.glossary
    if result is None:
        st.write("Altri termini trovati nei documenti: " + ", ".join(f"**{t}**" for t, _ in others))
        if st.button("Chiedi a Claude di spiegarli in parole semplici", type="primary"):
            with st.spinner("Claude sta preparando le spiegazioni…"):
                st.session_state.glossary = glossary.explain_with_ai(others)
            st.rerun()
        st.caption(
            "Una sola richiesta per tutti i termini, solo se la chiedi. Ogni spiegazione passa da un "
            "filtro che blocca qualsiasi consiglio prima di essere mostrata."
        )
        return

    if result["error"]:
        st.caption(f"Spiegazioni di Claude non disponibili in questo momento ({result['error']}).")
    for item in result["items"]:
        st.markdown(f"**{item['term']}** — {item['text']}")
    if result["blocked"]:
        st.caption(f"Non mostrate perché non rispettavano il vincolo educativo: {', '.join(result['blocked'])}.")
    if result["items"]:
        st.caption(
            f"Spiegazioni generate da Claude ({DEFAULT_MODEL}) e controllate dal filtro anti-consigli "
            f"· costo ${result['cost_usd']:.3f}."
        )


def _goal_section(s) -> None:
    """RF-07: proiezione puramente matematica dell'obiettivo di risparmio."""
    st.subheader("🎯 Simula un obiettivo di risparmio")
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
    with st.expander("Come è stato calcolato"):
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
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


# --------------------------------------------------------------------- main

_init_state()
_sidebar()
st.title("FinSup — capire il proprio budget")
st.info(DISCLAIMER, icon="ℹ️")
{"input": step_input, "conferma": step_confirm, "risultati": step_results}[st.session_state.step]()
