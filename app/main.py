"""Prototipo FinSup — Hagenthon Tema 02: Inclusione Finanziaria.

Scheletro applicativo: le funzionalita' core arrivano dai requisiti
funzionali (vedi docs/02-requisiti-funzionali.md). Questo file dimostra
che la pipeline e2e gira: input utente -> Claude locale -> guardrail
contenuti -> output, con trasparenza su costo/token per ogni chiamata.
"""
import streamlit as st

from finsup.ai_client import ask
from finsup.content_guard import find_violations

st.set_page_config(page_title="FinSup — Inclusione Finanziaria", page_icon="\U0001F4B6")

st.title("FinSup — Educazione Finanziaria")
st.caption("Hagenthon · Tema 02: Inclusione Finanziaria — prototipo in costruzione")

st.info(
    "Scheletro applicativo. Persona, scenario e funzionalita' core arrivano dai "
    "requisiti funzionali — vedi `docs/02-requisiti-funzionali.md`."
)

st.subheader("Prova rapida della pipeline")
domanda = st.text_input(
    "Chiedi la spiegazione di un concetto finanziario di base",
    placeholder="Es. Cos'è il TAEG?",
)

if st.button("Spiega", disabled=not domanda):
    with st.spinner("Chiedo a Claude (locale)..."):
        risposta = ask(
            domanda,
            system_prompt=(
                "Spiega concetti di finanza personale in italiano semplice, in "
                "massimo 3 frasi. Non dare mai consigli di investimento, "
                "raccomandazioni di prodotti o indicazioni su cosa fare con i "
                "propri soldi: spiega solo il significato."
            ),
        )

    if risposta["mocked"]:
        st.warning(f"Risposta mock (CLI locale non disponibile): {risposta['text']}")
    else:
        st.success(risposta["text"])
        violazioni = find_violations(risposta["text"])
        if violazioni:
            st.error(f"⚠️ Guardrail: rilevato linguaggio non ammesso → {violazioni}")
        st.caption(
            f"Costo stimato: ${risposta['cost_usd']:.4f} · token: {risposta['tokens']}"
        )
